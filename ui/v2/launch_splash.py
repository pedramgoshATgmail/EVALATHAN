"""Centered FUSS launching splash while the Evalathan desk starts.

Run as a standalone process from Evalathan.bat / launch.bat / launch.sh:
  pythonw ui/v2/launch_splash.py

Closes when ~/.evalathan/splash.stop appears, or after a safety timeout.
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
    stop = stop_path()
    if stop.is_file():
        try:
            stop.unlink()
        except OSError:
            pass
    pid_path().write_text(str(os.getpid()), encoding="utf-8")


def clear_markers() -> None:
    for path in (pid_path(), stop_path()):
        try:
            if path.is_file():
                path.unlink()
        except OSError:
            pass


def request_close() -> None:
    stop_path().write_text("1", encoding="utf-8")


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


def _logo_path() -> Path | None:
    assets = Path(__file__).resolve().parent / "assets"
    # Pre-sized splash art fills the circle exactly; fall back to the GUI logo.
    for name in ("fuss-splash.png", "fuss.png"):
        candidate = assets / name
        if candidate.is_file():
            return candidate
    return None


def _load_logo_fill(path: Path, target: int):
    """Return (photo_image, diameter). Logo fills the circular window."""
    import tkinter as tk

    raw = tk.PhotoImage(file=str(path))
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


def run_splash() -> int:
    if already_running():
        return 0

    try:
        import tkinter as tk
    except ImportError:
        return 0

    logo_path = _logo_path()
    if logo_path is None:
        return 0

    mark_running()
    started = time.monotonic()

    root = tk.Tk()
    root.title("EVALATHAN")
    root.overrideredirect(True)
    try:
        root.attributes("-topmost", True)
    except tk.TclError:
        pass

    # Transparent corners outside the circular region (Windows).
    key = "#010203"
    root.configure(bg=key)

    try:
        logo, size = _load_logo_fill(logo_path, TARGET_DIAMETER)
    except Exception:  # noqa: BLE001
        clear_markers()
        try:
            root.destroy()
        except tk.TclError:
            pass
        return 0
    root._logo = logo  # keep PhotoImage alive

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

    # Logo fills the circle; circular window clips the square image.
    canvas.create_image(size // 2, size // 2, image=logo, anchor="center")

    # Black "launching..." with animated dots, centered on the logo.
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
        font=("Segoe UI", 12, "bold"),
        anchor="e",
    )
    # Nudge the word+dots so the whole caption is centered as a group.
    bbox = canvas.bbox(label)
    word_w = (bbox[2] - bbox[0]) if bbox else 70
    dots_w = 28
    total_w = word_w + 4 + dots_w
    word_right = cx - total_w // 2 + word_w
    canvas.coords(label, word_right, cy)
    canvas.itemconfigure(label, anchor="e")
    dot_ids = []
    for i in range(3):
        dot_ids.append(
            canvas.create_text(
                word_right + 2 + i * 9,
                cy,
                text=".",
                fill=ink_dim,
                font=("Segoe UI", 16, "bold"),
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
            clear_markers()
            return
        root.after(POLL_MS, _poll)

    def _on_close() -> None:
        clear_markers()
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
        clear_markers()
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in {"--close", "close"}:
        request_close()
        return 0
    if argv and argv[0] in {"--check", "check"}:
        return 0 if already_running() else 1
    return run_splash()


if __name__ == "__main__":
    raise SystemExit(main())
