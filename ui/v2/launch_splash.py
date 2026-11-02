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
edge stays clean on light and dark backgrounds. Tk color-key alone is the
fallback (no SetWindowRgn - elliptic regions stair-step on every background).
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
DOT_MS = 420  # whole-caption fade pulse (launching...)


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


def _logo_art_only(im):
    """Keep cherries/FUSS (light art); drop key, orange disk, and dark fringe.

    The shipped fuss-splash.png is a Tk color-key asset: outside is (1,2,3) with
    near-black stair pixels at the circle rim. Pasting that rim into a layered
    window paints the black outline on every background. Rebuild the orange disk
    ourselves; only composite the light logo art.
    """
    px = im.load()
    w0, h0 = im.size
    for y in range(h0):
        for x in range(w0):
            r, g, b, a = px[x, y]
            if a < 8:
                px[x, y] = (0, 0, 0, 0)
                continue
            lum = (299 * r + 587 * g + 114 * b) // 1000
            # White / near-white logo strokes only.
            if lum >= 190 and min(r, g, b) >= 160:
                continue
            px[x, y] = (0, 0, 0, 0)
    return im


def _build_base_rgba(path: Path, size: int, supersample: int = 8):
    """Logo on a coverage-AA circular matte (clean on white and black).

    Hard circle at Nx, BOX-downscale for true coverage AA. Orange RGB is solid
    under a soft alpha matte so the rim never picks up the PNG color-key black.
    """
    from PIL import Image, ImageDraw

    ss = max(1, int(supersample))
    big = size * ss
    fill_rgb = (232, 135, 30)

    disk = Image.new("L", (big, big), 0)
    pad = max(1, ss)
    ImageDraw.Draw(disk).ellipse((pad, pad, big - pad - 1, big - pad - 1), fill=255)
    # BOX = area average = coverage antialias. LANCZOS sharpens and stair-steps.
    alpha = disk.resize((size, size), Image.Resampling.BOX)

    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pxo = out.load()
    for y in range(size):
        for x in range(size):
            a = alpha.getpixel((x, y))
            if a <= 0:
                continue
            pxo[x, y] = (fill_rgb[0], fill_rgb[1], fill_rgb[2], a)

    art = _logo_art_only(Image.open(path).convert("RGBA"))
    aw, ah = art.size
    art_scale = size / float(max(aw, ah, 1))
    art = art.resize(
        (max(1, int(round(aw * art_scale))), max(1, int(round(ah * art_scale)))),
        Image.Resampling.LANCZOS,
    )
    aw, ah = art.size
    out.paste(art, ((size - aw) // 2, (size - ah) // 2), art)
    return out


def _caption_fonts(supersample: int = 1):
    """TrueType fonts for 'launching' (Mac often lacks Segoe; default bitmap is tiny)."""
    from PIL import ImageFont

    ss = max(1, int(supersample))
    # +4 pt vs original 21/28 (was +3); prefer Bold so the caption reads thicker on Win+Mac.
    word_pt = 25 * ss
    dots_pt = 32 * ss
    candidates = (
        "segoeuib.ttf",  # Segoe UI Bold (Windows)
        "SegoeUI-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "Arial Bold.ttf",
        "arialbd.ttf",
        "segoeui.ttf",
        "SegoeUI.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "Arial.ttf",
        "Helvetica.ttc",
    )
    for name in candidates:
        try:
            return (
                ImageFont.truetype(name, word_pt),
                ImageFont.truetype(name, dots_pt),
            )
        except OSError:
            continue
    return ImageFont.load_default(), ImageFont.load_default()


def _caption_fade_rgba(phase: int) -> tuple[int, int, int, int]:
    """Dark green 'launching...' with whole-string fade pulse (3 baked frames)."""
    # Dark green base; alpha steps make the full word+ellipsis flash/fade together.
    r, g, b = 11, 92, 46  # #0B5C2E
    alphas = (255, 150, 72)
    return (r, g, b, alphas[phase % 3])


def _draw_caption(base, phase: int, supersample: int = 1):
    """Return a copy of base with centered dark-green fading 'launching...'."""
    from PIL import ImageDraw

    frame = base.copy()
    draw = ImageDraw.Draw(frame)
    size = frame.size[0]
    ss = max(1, int(supersample))
    font, _font_dots = _caption_fonts(ss)

    word = "launching..."
    try:
        wb = draw.textbbox((0, 0), word, font=font)
        word_w = wb[2] - wb[0]
        word_h = wb[3] - wb[1]
    except Exception:  # noqa: BLE001
        word_w, word_h = 150 * ss, 20 * ss
    x0 = (size - word_w) // 2
    y = size // 2 - word_h // 2 - 2 * ss
    draw.text((x0, y), word, fill=_caption_fade_rgba(phase), font=font)
    return frame

def _rgba_to_premultiplied_bgra(im) -> bytes:
    pixels = bytearray()
    for r, g, b, a in im.getdata():
        if a <= 0:
            pixels.extend((0, 0, 0, 0))
        else:
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
        base = _build_base_rgba(logo_path, size, supersample=8)
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
        from PIL import Image
    except ImportError:
        return path

    # Same art extract + orange disk as layered; only then flatten onto the key.
    rgba = _build_base_rgba(path, target, supersample=4)
    keyed = Image.new("RGBA", (target, target), (*key_rgb, 255))
    keyed.paste(rgba, (0, 0), rgba)
    out = state_dir() / "fuss-splash-keyed.png"
    keyed.convert("RGB").save(out, format="PNG")
    return out


def _rgba_splash_frame_pngs(logo_path: Path, size: int) -> list[Path] | None:
    """Write three real-alpha PNG frames (Mac Tk uses systemTransparent + PNG alpha)."""
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        base = _build_base_rgba(logo_path, size, supersample=8)
        out_dir = state_dir()
        paths: list[Path] = []
        for phase in range(3):
            frame = _draw_caption(base, phase)
            path = out_dir / f"fuss-splash-rgba-p{phase}.png"
            frame.save(path, format="PNG")
            paths.append(path)
        return paths
    except Exception:  # noqa: BLE001
        return None


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


def _run_splash_cocoa(logo_path: Path) -> bool:
    """True circular splash on macOS via AppKit (Tk still paints a square frame)."""
    try:
        from AppKit import (  # type: ignore[import-not-found]
            NSApplication,
            NSApplicationActivationPolicyAccessory,
            NSBackingStoreBuffered,
            NSBorderlessWindowMask,
            NSColor,
            NSFloatingWindowLevel,
            NSImage,
            NSImageView,
            NSWindow,
        )
        from AppKit import NSScreen  # type: ignore[import-not-found]
        from Foundation import NSMakeRect  # type: ignore[import-not-found]
    except Exception:  # noqa: BLE001
        return False

    frames = _rgba_splash_frame_pngs(logo_path, TARGET_DIAMETER)
    if not frames:
        return False

    size = float(TARGET_DIAMETER)
    images = []
    for path in frames:
        img = NSImage.alloc().initWithContentsOfFile_(str(path))
        if img is None:
            return False
        images.append(img)

    if stop_path().is_file():
        return False

    app = NSApplication.sharedApplication()
    try:
        app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    except Exception:  # noqa: BLE001
        pass

    # Screen center in Cocoa coords (origin bottom-left).
    screen = NSScreen.mainScreen()
    if screen is not None:
        frame = screen.frame()
        x = (frame.size.width - size) / 2.0
        y = (frame.size.height - size) / 2.0
    else:
        x, y = 200.0, 200.0

    window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
        NSMakeRect(x, y, size, size),
        NSBorderlessWindowMask,
        NSBackingStoreBuffered,
        False,
    )
    window.setOpaque_(False)
    window.setBackgroundColor_(NSColor.clearColor())
    window.setHasShadow_(False)
    window.setLevel_(NSFloatingWindowLevel)
    window.setIgnoresMouseEvents_(True)

    view = NSImageView.alloc().initWithFrame_(NSMakeRect(0, 0, size, size))
    view.setImage_(images[0])
    try:
        view.setImageScaling_(2)  # NSImageScaleNone
    except Exception:  # noqa: BLE001
        pass
    try:
        view.setWantsLayer_(True)
        view.layer().setBackgroundColor_(NSColor.clearColor().CGColor())
    except Exception:  # noqa: BLE001
        pass
    window.setContentView_(view)
    window.orderFrontRegardless()
    phase = {"i": 0}
    started = time.monotonic()
    last_dot = time.monotonic()

    # Pump Cocoa events until desk signals stop (same contract as Win32/Tk paths).
    try:
        from AppKit import NSDate, NSDefaultRunLoopMode  # type: ignore[import-not-found]

        while True:
            if stop_path().is_file() or (time.monotonic() - started) > MAX_SECONDS:
                break
            now = time.monotonic()
            if (now - last_dot) * 1000 >= DOT_MS:
                phase["i"] = (phase["i"] + 1) % len(images)
                view.setImage_(images[phase["i"]])
                last_dot = now
            event = app.nextEventMatchingMask_untilDate_inMode_dequeue_(
                0xFFFFFFFF,  # NSAnyEventMask
                NSDate.dateWithTimeIntervalSinceNow_(POLL_MS / 1000.0),
                NSDefaultRunLoopMode,
                True,
            )
            if event is not None:
                app.sendEvent_(event)
    finally:
        try:
            window.orderOut_(None)
            window.close()
        except Exception:  # noqa: BLE001
            pass
    return True


def _run_splash_tk_mac(logo_path: Path) -> bool:
    """Fallback Mac splash if Cocoa is unavailable."""
    try:
        import tkinter as tk
    except ImportError:
        return False

    frames = _rgba_splash_frame_pngs(logo_path, TARGET_DIAMETER)
    if not frames:
        return False

    size = TARGET_DIAMETER
    root = tk.Tk()
    root.title("EVALATHAN")
    root.overrideredirect(True)
    try:
        root.attributes("-topmost", True)
    except tk.TclError:
        pass
    try:
        root.attributes("-transparent", True)
        root.configure(bg="systemTransparent")
    except tk.TclError:
        try:
            root.destroy()
        except tk.TclError:
            pass
        return False

    photos = []
    try:
        from PIL import Image, ImageTk

        for path in frames:
            photos.append(ImageTk.PhotoImage(Image.open(path)))
    except Exception:  # noqa: BLE001
        try:
            root.destroy()
        except tk.TclError:
            pass
        return False
    root._photos = photos

    if stop_path().is_file():
        try:
            root.destroy()
        except tk.TclError:
            pass
        return False

    canvas = tk.Canvas(
        root,
        width=size,
        height=size,
        bg="systemTransparent",
        highlightthickness=0,
        bd=0,
    )
    canvas.pack(fill="both", expand=True)
    img_id = canvas.create_image(size // 2, size // 2, image=photos[0], anchor="center")

    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = max(0, (sw - size) // 2)
    y = max(0, (sh - size) // 2)
    root.geometry(f"{size}x{size}+{x}+{y}")

    phase = {"i": 0}
    started = time.monotonic()

    def _tick_dots() -> None:
        if not root.winfo_exists():
            return
        phase["i"] = (phase["i"] + 1) % len(photos)
        canvas.itemconfigure(img_id, image=photos[phase["i"]])
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
    return True

def _run_splash_tk(logo_path: Path) -> int:
    """Fallback splash (color-key). Used when layered / Mac transparent path is unavailable."""
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
    # Tk cannot do true alpha; pulse dark-green → mid → soft green for the whole string.
    fade_fills = ("#0B5C2E", "#3D8A5C", "#7AAD8E")
    cx = size // 2
    cy = size // 2
    label = canvas.create_text(
        cx,
        cy,
        text="launching...",
        fill=fade_fills[0],
        font=("Segoe UI", 20, "bold"),
        anchor="center",
    )

    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = max(0, (sw - size) // 2)
    y = max(0, (sh - size) // 2)
    root.geometry(f"{size}x{size}+{x}+{y}")
    # Do not SetWindowRgn - hard elliptic regions stair-step on every background.
    # Color-key alone is the Tk fallback; layered Win32 / Mac transparent is preferred.

    phase = {"i": 0}
    started = time.monotonic()

    def _tick_dots() -> None:
        if not root.winfo_exists():
            return
        canvas.itemconfigure(label, fill=fade_fills[phase["i"] % 3])
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
        elif sys.platform == "darwin":
            try:
                if _run_splash_cocoa(logo_path):
                    return 0
            except Exception:  # noqa: BLE001 - never block desk launch
                pass
            try:
                if _run_splash_tk_mac(logo_path):
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
