"""Centered FUSS launching splash while the Evalathan desk starts.

Run as a standalone process from Evalathan.bat / launch.bat / launch.sh:
  pythonw ui/v2/launch_splash.py

Closes when ~/.evalathan/splash.stop appears, when the recorded PID is killed,
or after a safety timeout.

Lifecycle (avoids a stuck splash after a second CMD/PowerShell install):
- Intentional start clears splash.stop, then launches this script.
- This process writes splash.pid only (it never clears splash.stop).
- If splash.stop already exists, exit immediately (desk is up / closing).
- On exit, clear splash.pid but leave splash.stop so a late sibling aborts.
- --close writes splash.stop and terminates the recorded PID.

On Windows the splash uses UpdateLayeredWindow (per-pixel alpha) so the circle
edge stays clean on light and dark backgrounds. Tk color-key + SetWindowRgn is
only a fallback (jagged / black fringe on white).
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# Target circle size; logo is scaled to fill it (Pillow) or the circle matches the logo.
TARGET_DIAMETER = 220
MAX_SECONDS = 180
POLL_MS = 120
DOT_MS = 380


def state_dir() -> Path:
    override = os.environ.get("EVALATHAN_STATE_DIR", "").strip()
    path = Path(override) if override else Path.home() / ".evalathan"
    path.mkdir(parents=True, exist_ok=True)
    return path


def pid_path() -> Path:
    return state_dir() / "splash.pid"


def stop_path() -> Path:
    return state_dir() / "splash.stop"


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if sys.platform == "win32":
        import ctypes

        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259
        handle = ctypes.windll.kernel32.OpenProcess(
            PROCESS_QUERY_LIMITED_INFORMATION, False, pid
        )
        if not handle:
            return False
        try:
            exit_code = ctypes.c_ulong()
            ok = ctypes.windll.kernel32.GetExitCodeProcess(
                handle, ctypes.byref(exit_code)
            )
            if ok == 0:
                return False
            return int(exit_code.value) == STILL_ACTIVE
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def already_running() -> bool:
    path = pid_path()
    if not path.is_file():
        return False
    try:
        pid = int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return False
    if pid == os.getpid():
        return False
    return _pid_alive(pid)


def mark_running() -> None:
    """Record this PID only. Never clear splash.stop (late starts must see it)."""
    pid_path().write_text(str(os.getpid()), encoding="utf-8")


def clear_pid() -> None:
    path = pid_path()
    try:
        if path.is_file():
            path.unlink()
    except OSError:
        pass


def clear_stop() -> None:
    path = stop_path()
    try:
        if path.is_file():
            path.unlink()
    except OSError:
        pass


def clear_markers() -> None:
    """Back-compat name: drop the PID marker only; leave stop for late siblings."""
    clear_pid()


def _kill_pid(pid: int) -> None:
    if pid <= 0 or pid == os.getpid():
        return
    if sys.platform == "win32":
        import ctypes

        PROCESS_TERMINATE = 0x0001
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
        if handle:
            try:
                ctypes.windll.kernel32.TerminateProcess(handle, 1)
            finally:
                ctypes.windll.kernel32.CloseHandle(handle)
        return
    try:
        os.kill(pid, 15)
    except OSError:
        try:
            os.kill(pid, 9)
        except OSError:
            pass


def request_close() -> None:
    """Signal stop and terminate any recorded splash PID (stuck overlay fix)."""
    stop_path().write_text("1", encoding="utf-8")
    path = pid_path()
    if not path.is_file():
        return
    try:
        pid = int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        clear_pid()
        return
    _kill_pid(pid)
    clear_pid()


def _assets_dir() -> Path:
    return Path(__file__).resolve().parent / "assets"


def _logo_path() -> Path | None:
    assets = _assets_dir()
    for name in ("fuss-splash.png", "fuss.png"):
        candidate = assets / name
        if candidate.is_file():
            return candidate
    return None


def _prebaked_bgra_frames(size: int) -> list[bytes] | None:
    """Ship premultiplied BGRA frames so ASAP splash needs no Pillow."""
    assets = _assets_dir()
    expected = size * size * 4
    frames: list[bytes] = []
    for phase in range(3):
        path = assets / f"fuss-splash-p{phase}.bgra"
        if not path.is_file():
            return None
        data = path.read_bytes()
        if len(data) != expected:
            return None
        frames.append(data)
    return frames


def _build_base_rgba(path: Path, size: int):
    """Logo on a soft-edged circular alpha matte (clean on white and black).

    Soft AA must sit on brand orange RGB. If the rim samples the old key-black
    fill (1,2,3), premultiplied alpha paints a dark halo on light desktops.
    """
    from PIL import Image, ImageDraw, ImageFilter

    key_rgb = {(0, 0, 0), (1, 2, 3)}
    im = Image.open(path).convert("RGBA")
    px = im.load()
    w0, h0 = im.size
    for y in range(h0):
        for x in range(w0):
            r, g, b, a = px[x, y]
            if (r, g, b) in key_rgb or a < 8:
                px[x, y] = (0, 0, 0, 0)
    w, h = im.size
    side = max(w, h, 1)
    if side != size:
        scale = size / float(side)
        im = im.resize(
            (max(1, int(round(w * scale))), max(1, int(round(h * scale)))),
            Image.Resampling.LANCZOS,
        )
        w, h = im.size
    # Opaque orange underlay so the blurred alpha rim never samples key-black.
    fill = (232, 135, 30, 255)
    solid = Image.new("RGBA", (size, size), fill)
    solid.paste(im, ((size - w) // 2, (size - h) // 2), im)
    disk = Image.new("L", (size, size), 0)
    ImageDraw.Draw(disk).ellipse((1, 1, size - 2, size - 2), fill=255)
    soft = disk.filter(ImageFilter.GaussianBlur(radius=1.6))
    r, g, b, _a = solid.split()
    return Image.merge("RGBA", (r, g, b, soft))


def _draw_caption(base, phase: int):
    """Return a copy of base with centered black 'launching' + animated dots."""
    from PIL import Image, ImageDraw, ImageFont

    frame = base.copy()
    draw = ImageDraw.Draw(frame)
    size = frame.size[0]
    try:
        font = ImageFont.truetype("segoeui.ttf", 21)
        font_dots = ImageFont.truetype("segoeui.ttf", 28)
    except OSError:
        font = ImageFont.load_default()
        font_dots = font

    word = "launching"
    # Measure word and three dots as a group, then center.
    try:
        wb = draw.textbbox((0, 0), word, font=font)
        word_w = wb[2] - wb[0]
        word_h = wb[3] - wb[1]
    except Exception:  # noqa: BLE001
        word_w, word_h = 90, 16
    dots_w = 40
    total = word_w + 6 + dots_w
    x0 = (size - total) // 2
    y = size // 2 - word_h // 2 - 2
    draw.text((x0, y), word, fill=(0, 0, 0, 255), font=font)
    active = phase % 3
    for i in range(3):
        if i == active:
            color = (0, 0, 0, 255)
        elif i == (active - 1) % 3:
            color = (58, 58, 58, 255)
        else:
            color = (106, 106, 106, 255)
        draw.text((x0 + word_w + 6 + i * 12, y - 4), ".", fill=color, font=font_dots)
    return frame


def _rgba_to_premultiplied_bgra(im) -> bytes:
    pixels = bytearray()
    for r, g, b, a in im.getdata():
        pixels.extend(
            (
                (b * a) // 255,
                (g * a) // 255,
                (r * a) // 255,
                a,
            )
        )
    return bytes(pixels)


def _load_layered_frames(logo_path: Path, size: int) -> list[bytes] | None:
    """Prefer prebaked BGRA; else build with Pillow when available."""
    prebaked = _prebaked_bgra_frames(size)
    if prebaked is not None:
        return prebaked
    try:
        base = _build_base_rgba(logo_path, size)
        return [
            _rgba_to_premultiplied_bgra(_draw_caption(base, phase)) for phase in range(3)
        ]
    except Exception:  # noqa: BLE001
        return None


def _run_splash_layered_win32(logo_path: Path) -> bool:
    """Per-pixel alpha splash. True if shown; False to fall back to Tk."""
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    kernel32 = ctypes.windll.kernel32

    # 64-bit Windows: LRESULT/WPARAM/LPARAM are pointer-sized. Using c_long
    # overflows in DefWindowProcW and silently kills the layered path.
    LRESULT = ctypes.c_ssize_t
    user32.DefWindowProcW.argtypes = [
        wintypes.HWND,
        ctypes.c_uint,
        wintypes.WPARAM,
        wintypes.LPARAM,
    ]
    user32.DefWindowProcW.restype = LRESULT
    user32.CreateWindowExW.restype = wintypes.HWND
    user32.UpdateLayeredWindow.restype = wintypes.BOOL

    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

    class SIZE(ctypes.Structure):
        _fields_ = [("cx", ctypes.c_long), ("cy", ctypes.c_long)]

    class BLENDFUNCTION(ctypes.Structure):
        _fields_ = [
            ("BlendOp", ctypes.c_byte),
            ("BlendFlags", ctypes.c_byte),
            ("SourceConstantAlpha", ctypes.c_byte),
            ("AlphaFormat", ctypes.c_byte),
        ]

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            ("biSize", wintypes.DWORD),
            ("biWidth", wintypes.LONG),
            ("biHeight", wintypes.LONG),
            ("biPlanes", wintypes.WORD),
            ("biBitCount", wintypes.WORD),
            ("biCompression", wintypes.DWORD),
            ("biSizeImage", wintypes.DWORD),
            ("biXPelsPerMeter", wintypes.LONG),
            ("biYPelsPerMeter", wintypes.LONG),
            ("biClrUsed", wintypes.DWORD),
            ("biClrImportant", wintypes.DWORD),
        ]

    class BITMAPINFO(ctypes.Structure):
        _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", wintypes.DWORD * 3)]

    WndProcType = ctypes.WINFUNCTYPE(
        LRESULT, wintypes.HWND, ctypes.c_uint, wintypes.WPARAM, wintypes.LPARAM
    )

    class WNDCLASS(ctypes.Structure):
        _fields_ = [
            ("style", ctypes.c_uint),
            ("lpfnWndProc", WndProcType),
            ("cbClsExtra", ctypes.c_int),
            ("cbWndExtra", ctypes.c_int),
            ("hInstance", wintypes.HINSTANCE),
            ("hIcon", wintypes.HICON),
            ("hCursor", wintypes.HANDLE),
            ("hbrBackground", wintypes.HBRUSH),
            ("lpszMenuName", wintypes.LPCWSTR),
            ("lpszClassName", wintypes.LPCWSTR),
        ]

    WS_POPUP = 0x80000000
    WS_EX_LAYERED = 0x00080000
    WS_EX_TOPMOST = 0x00000008
    WS_EX_TOOLWINDOW = 0x00000080
    WS_VISIBLE = 0x10000000
    HWND_TOPMOST = -1
    SWP_NOSIZE = 0x0001
    SWP_NOMOVE = 0x0002
    SWP_SHOWWINDOW = 0x0040
    SW_SHOW = 5
    AC_SRC_OVER = 0x00
    AC_SRC_ALPHA = 0x01
    ULW_ALPHA = 0x00000002
    DIB_RGB_COLORS = 0
    BI_RGB = 0
    WM_DESTROY = 0x0002
    WM_CLOSE = 0x0010
    PM_REMOVE = 0x0001

    size = TARGET_DIAMETER
    frames = _load_layered_frames(logo_path, size)
    if not frames:
        return False

    def _wnd_proc(hwnd, msg, wparam, lparam):
        if msg in (WM_DESTROY, WM_CLOSE):
            user32.PostQuitMessage(0)
            return 0
        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    wnd_proc = WndProcType(_wnd_proc)
    # Keep callable alive for the class lifetime.
    _run_splash_layered_win32._wnd_proc = wnd_proc  # type: ignore[attr-defined]

    hinstance = kernel32.GetModuleHandleW(None)
    class_name = "EvalathanFussSplash"
    wc = WNDCLASS()
    wc.style = 0
    wc.lpfnWndProc = wnd_proc
    wc.cbClsExtra = 0
    wc.cbWndExtra = 0
    wc.hInstance = hinstance
    wc.hIcon = None
    wc.hCursor = user32.LoadCursorW(None, 32512)
    wc.hbrBackground = None
    wc.lpszMenuName = None
    wc.lpszClassName = class_name
    atom = user32.RegisterClassW(ctypes.byref(wc))
    if not atom:
        # Already registered from a prior run in this process - ignore.
        err = kernel32.GetLastError()
        if err not in (0, 1410):  # ERROR_CLASS_ALREADY_EXISTS
            return False

    sw = user32.GetSystemMetrics(0)
    sh = user32.GetSystemMetrics(1)
    x = max(0, (sw - size) // 2)
    y = max(0, (sh - size) // 2)
    hwnd = user32.CreateWindowExW(
        WS_EX_LAYERED | WS_EX_TOPMOST | WS_EX_TOOLWINDOW,
        class_name,
        "EVALATHAN",
        WS_POPUP | WS_VISIBLE,
        x,
        y,
        size,
        size,
        None,
        None,
        hinstance,
        None,
    )
    if not hwnd:
        return False

    user32.SetWindowPos(
        hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
    )
    user32.ShowWindow(hwnd, SW_SHOW)

    hdc_screen = user32.GetDC(None)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = size
    bmi.bmiHeader.biHeight = -size  # top-down
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    bmi.bmiHeader.biCompression = BI_RGB
    bits = ctypes.c_void_p()
    hbmp = gdi32.CreateDIBSection(
        hdc_screen,
        ctypes.byref(bmi),
        DIB_RGB_COLORS,
        ctypes.byref(bits),
        None,
        0,
    )
    if not hbmp or not bits:
        user32.ReleaseDC(None, hdc_screen)
        gdi32.DeleteDC(hdc_mem)
        user32.DestroyWindow(hwnd)
        return False
    old = gdi32.SelectObject(hdc_mem, hbmp)

    blend = BLENDFUNCTION(AC_SRC_OVER, 0, 255, AC_SRC_ALPHA)
    pt_dst = POINT(x, y)
    pt_src = POINT(0, 0)
    sz = SIZE(size, size)
    started = time.monotonic()
    phase = 0
    last_dot = 0.0
    ok_paint = False

    def paint(data: bytes) -> bool:
        ctypes.memmove(bits, data, len(data))
        return bool(
            user32.UpdateLayeredWindow(
                hwnd,
                hdc_screen,
                ctypes.byref(pt_dst),
                ctypes.byref(sz),
                hdc_mem,
                ctypes.byref(pt_src),
                0,
                ctypes.byref(blend),
                ULW_ALPHA,
            )
        )

    try:
        ok_paint = paint(frames[phase % len(frames)])
        if not ok_paint:
            return False

        msg = wintypes.MSG()
        while True:
            if stop_path().is_file() or (time.monotonic() - started) > MAX_SECONDS:
                break
            while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, PM_REMOVE):
                if msg.message == 0x0012:  # WM_QUIT
                    break
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            now = time.monotonic()
            if (now - last_dot) * 1000 >= DOT_MS:
                phase += 1
                last_dot = now
                paint(frames[phase % len(frames)])
            time.sleep(POLL_MS / 1000.0)
    finally:
        gdi32.SelectObject(hdc_mem, old)
        gdi32.DeleteObject(hbmp)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(None, hdc_screen)
        if user32.IsWindow(hwnd):
            user32.DestroyWindow(hwnd)
    return True


def _apply_circle_region(root, size: int) -> None:
    """True circular window on Windows; other platforms keep a square frame."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        from ctypes import wintypes

        root.update_idletasks()
        hwnd = wintypes.HWND(int(root.winfo_id()))
        user32 = ctypes.windll.user32
        outer = user32.GetParent(hwnd) or hwnd
        hrgn = ctypes.windll.gdi32.CreateEllipticRgn(0, 0, size, size)
        if hrgn:
            user32.SetWindowRgn(outer, hrgn, True)
    except Exception:  # noqa: BLE001 - splash must never crash the launcher
        pass


def _keyed_splash_png(path: Path, target: int, key_rgb: tuple[int, int, int]) -> Path:
    """Flatten logo onto the transparent-key RGB so Tk never paints alpha as black."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return path

    im = Image.open(path).convert("RGBA")
    w, h = im.size
    side = max(w, h, 1)
    if side != target:
        scale = target / float(side)
        nw = max(1, int(round(w * scale)))
        nh = max(1, int(round(h * scale)))
        im = im.resize((nw, nh), Image.Resampling.LANCZOS)
        w, h = im.size
    canvas = Image.new("RGBA", (target, target), (*key_rgb, 255))
    ox = (target - w) // 2
    oy = (target - h) // 2
    canvas.paste(im, (ox, oy), im)
    mask = Image.new("L", (target, target), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, target - 1, target - 1), fill=255)
    keyed = Image.new("RGBA", (target, target), (*key_rgb, 255))
    keyed.paste(canvas, (0, 0), mask)
    out = state_dir() / "fuss-splash-keyed.png"
    keyed.convert("RGB").save(out, format="PNG")
    return out


def _load_logo_fill(path: Path, target: int, key_rgb: tuple[int, int, int] = (1, 2, 3)):
    """Return (photo_image, diameter). Logo fills the circular window."""
    import tkinter as tk

    load_path = path
    keyed = _keyed_splash_png(path, target, key_rgb)
    if keyed.is_file():
        load_path = keyed

    raw = tk.PhotoImage(file=str(load_path))
    w, h = int(raw.width()), int(raw.height())
    if w <= 0 or h <= 0:
        return raw, target
    side = max(w, h)
    if side == target:
        return raw, target
    if side < target:
        factor = max(1, target // side)
        if factor > 1:
            raw = raw.zoom(factor, factor)
    elif side > target:
        factor = max(1, int(round(side / float(target))))
        if factor > 1:
            raw = raw.subsample(factor, factor)
    diameter = max(int(raw.width()), int(raw.height()))
    return raw, diameter


def _run_splash_tk(logo_path: Path) -> int:
    """Fallback splash (color-key). Used when layered Win32 path is unavailable."""
    try:
        import tkinter as tk
    except ImportError:
        return 0

    key = "#010203"
    key_rgb = (1, 2, 3)
    root = tk.Tk()
    root.title("EVALATHAN")
    root.overrideredirect(True)
    try:
        root.attributes("-topmost", True)
    except tk.TclError:
        pass
    root.configure(bg=key)

    try:
        logo, size = _load_logo_fill(logo_path, TARGET_DIAMETER, key_rgb)
    except Exception:  # noqa: BLE001
        try:
            root.destroy()
        except tk.TclError:
            pass
        return 0
    root._logo = logo

    if stop_path().is_file():
        try:
            root.destroy()
        except tk.TclError:
            pass
        return 0

    canvas = tk.Canvas(
        root,
        width=size,
        height=size,
        bg=key,
        highlightthickness=0,
        bd=0,
    )
    canvas.pack(fill="both", expand=True)
    try:
        root.attributes("-transparentcolor", key)
    except tk.TclError:
        pass

    canvas.create_image(size // 2, size // 2, image=logo, anchor="center")
    ink = "#000000"
    ink_mid = "#3a3a3a"
    ink_dim = "#6a6a6a"
    cx = size // 2
    cy = size // 2
    label = canvas.create_text(
        cx,
        cy,
        text="launching",
        fill=ink,
        font=("Segoe UI", 16, "bold"),
        anchor="e",
    )
    bbox = canvas.bbox(label)
    word_w = (bbox[2] - bbox[0]) if bbox else 90
    dots_w = 36
    total_w = word_w + 4 + dots_w
    word_right = cx - total_w // 2 + word_w
    canvas.coords(label, word_right, cy)
    canvas.itemconfigure(label, anchor="e")
    dot_ids = []
    for i in range(3):
        dot_ids.append(
            canvas.create_text(
                word_right + 2 + i * 12,
                cy,
                text=".",
                fill=ink_dim,
                font=("Segoe UI", 21, "bold"),
                anchor="w",
            )
        )

    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = max(0, (sw - size) // 2)
    y = max(0, (sh - size) // 2)
    root.geometry(f"{size}x{size}+{x}+{y}")
    _apply_circle_region(root, size)

    phase = {"i": 0}
    started = time.monotonic()

    def _tick_dots() -> None:
        if not root.winfo_exists():
            return
        active = phase["i"] % 3
        for i, dot_id in enumerate(dot_ids):
            if i == active:
                color = ink
            elif i == (active - 1) % 3:
                color = ink_mid
            else:
                color = ink_dim
            canvas.itemconfigure(dot_id, fill=color)
        phase["i"] += 1
        root.after(DOT_MS, _tick_dots)

    def _poll() -> None:
        if not root.winfo_exists():
            return
        if stop_path().is_file() or (time.monotonic() - started) > MAX_SECONDS:
            try:
                root.destroy()
            except tk.TclError:
                pass
            return
        root.after(POLL_MS, _poll)

    def _on_close() -> None:
        try:
            root.destroy()
        except tk.TclError:
            pass

    root.protocol("WM_DELETE_WINDOW", _on_close)
    root.after(DOT_MS, _tick_dots)
    root.after(POLL_MS, _poll)
    try:
        root.mainloop()
    finally:
        pass
    return 0


def run_splash() -> int:
    # Desk already signaled ready, or a prior close left the stop flag - do not paint.
    if stop_path().is_file():
        return 0
    if already_running():
        return 0

    logo_path = _logo_path()
    if logo_path is None:
        return 0

    mark_running()
    if stop_path().is_file():
        clear_pid()
        return 0

    try:
        if sys.platform == "win32":
            try:
                if _run_splash_layered_win32(logo_path):
                    return 0
            except Exception:  # noqa: BLE001 - never block desk launch
                pass
        return _run_splash_tk(logo_path)
    finally:
        clear_pid()


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in {"--close", "close"}:
        request_close()
        return 0
    if argv and argv[0] in {"--check", "check"}:
        return 0 if already_running() else 1
    if argv and argv[0] in {"--clear-stop", "clear-stop"}:
        clear_stop()
        return 0
    return run_splash()


if __name__ == "__main__":
    raise SystemExit(main())
