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

DIAMETER = 220
LOGO_PX = 92
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


def _load_logo(path: Path, size: int):
    import tkinter as tk

    raw = tk.PhotoImage(file=str(path))
    w, h = int(raw.width()), int(raw.height())
    if w <= 0 or h <= 0:
        return raw
    if w > size or h > size:
        factor = max(1, int(round(max(w / size, h / size))))
        return raw.subsample(factor, factor)
    if w < size and h < size:
        factor = max(1, int(size // max(w, h)))
        if factor > 1:
            return raw.zoom(factor, factor)
    return raw


def run_splash() -> int:
    if already_running():
        return 0

    try:
        import tkinter as tk
    except ImportError:
        return 0

    logo_path = Path(__file__).resolve().parent / "assets" / "fuss.png"
    if not logo_path.is_file():
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

    bg = "#141414"
    fg = "#e8e8e8"
    muted = "#6e6e6e"
    root.configure(bg=bg)

    size = DIAMETER
    canvas = tk.Canvas(
        root,
        width=size,
        height=size,
        bg=bg,
        highlightthickness=0,
        bd=0,
    )
    canvas.pack(fill="both", expand=True)
    pad = 3
    canvas.create_oval(
        pad,
        pad,
        size - pad,
        size - pad,
        fill=bg,
        outline="#2c2c2c",
        width=2,
    )

    try:
        logo = _load_logo(logo_path, LOGO_PX)
    except Exception:  # noqa: BLE001
        clear_markers()
        try:
            root.destroy()
        except tk.TclError:
            pass
        return 0
    root._logo = logo  # keep PhotoImage alive
    canvas.create_image(size // 2, int(size * 0.38), image=logo, anchor="center")

    caption_y = int(size * 0.72)
    label = canvas.create_text(
        size // 2 - 18,
        caption_y,
        text="launching",
        fill=fg,
        font=("Segoe UI", 11),
        anchor="center",
    )
    bbox = canvas.bbox(label)
    word_right = bbox[2] if bbox else (size // 2 + 20)
    dot_ids = []
    for i in range(3):
        dot_ids.append(
            canvas.create_text(
                word_right + 2 + i * 9,
                caption_y,
                text=".",
                fill=muted,
                font=("Segoe UI", 14, "bold"),
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
            # Active dot bright; previous still soft; others muted - fade cycle.
            if i == active:
                color = fg
            elif i == (active - 1) % 3:
                color = "#a0a0a0"
            else:
                color = muted
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
