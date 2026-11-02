"""Spawn and dismiss the centered FUSS launching splash."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from evalathan.desk_store import state_dir


def splash_script() -> Path:
    """ui/v2/launch_splash.py next to the desk assets (standalone, no install needed)."""
    here = Path(__file__).resolve()
    candidate = here.parents[2] / "ui" / "v2" / "launch_splash.py"
    return candidate


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
    return _pid_alive(pid)


def _kill_pid(pid: int) -> None:
    if pid <= 0:
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


def clear_stop() -> None:
    path = stop_path()
    try:
        if path.is_file():
            path.unlink()
    except OSError:
        pass


def request_close() -> None:
    """Ask the splash to exit and terminate its PID if still alive."""
    stop_path().write_text("1", encoding="utf-8")
    path = pid_path()
    if not path.is_file():
        return
    try:
        pid = int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        try:
            path.unlink()
        except OSError:
            pass
        return
    _kill_pid(pid)
    try:
        if path.is_file():
            path.unlink()
    except OSError:
        pass


def spawn_if_needed() -> bool:
    """Start the FUSS splash in a detached process if one is not already up."""
    if already_running():
        return True
    script = splash_script()
    if not script.is_file():
        return False
    # Intentional start: clear a prior stop so the new splash is allowed to paint.
    clear_stop()
    kwargs: dict = {
        "args": [sys.executable, str(script)],
        "cwd": str(script.parent.parent.parent),
        "env": os.environ.copy(),
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
    }
    if sys.platform == "win32":
        kwargs["creationflags"] = (
            getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
            | getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
        )
        kwargs["start_new_session"] = True
    else:
        kwargs["start_new_session"] = True
    try:
        subprocess.Popen(**kwargs)
    except OSError:
        return False
    return True
