"""Check GitHub main on desk launch; popup to apply published updates."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class UpdateStatus:
    repo: Path
    local: str
    remote: str
    behind: bool
    error: str = ""


def repo_root() -> Path | None:
    """Editable checkout root (folder with .git and ui/v2)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists() and (parent / "ui" / "v2" / "index.html").is_file():
            return parent
    return None


def _git(repo: Path, *args: str, timeout: int = 45) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _short(sha: str) -> str:
    return (sha or "").strip()[:7]


def check_for_update(repo: Path | None = None, *, fetch: bool = True) -> UpdateStatus:
    """Fetch origin (optional) and compare HEAD to origin/main."""
    root = repo or repo_root()
    if root is None:
        return UpdateStatus(Path("."), "", "", False, error="not a git checkout")
    if shutil.which("git") is None:
        return UpdateStatus(root, "", "", False, error="git not found")
    if fetch:
        fetched = _git(root, "fetch", "origin", "main", timeout=60)
        if fetched.returncode != 0:
            fetched = _git(root, "fetch", "origin", timeout=60)
            if fetched.returncode != 0:
                err = (fetched.stderr or fetched.stdout or "fetch failed").strip()
                return UpdateStatus(root, "", "", False, error=err[:240])
    local_p = _git(root, "rev-parse", "HEAD")
    remote_p = _git(root, "rev-parse", "origin/main")
    if local_p.returncode != 0 or remote_p.returncode != 0:
        return UpdateStatus(
            root,
            "",
            "",
            False,
            error="could not resolve HEAD or origin/main",
        )
    local = local_p.stdout.strip()
    remote = remote_p.stdout.strip()
    return UpdateStatus(
        root, local, remote, behind=(local != remote and bool(remote))
    )


def _refresh_desktop_launcher(repo: Path) -> None:
    """Re-write Desktop Evalathan.app / .lnk so daily clicks use the latest launch path."""
    try:
        if sys.platform == "darwin":
            script = repo / "install_desktop_app.sh"
            if script.is_file():
                subprocess.run(
                    ["bash", str(script)],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    check=False,
                )
        elif sys.platform == "win32":
            script = repo / "install_desktop_app.ps1"
            if script.is_file():
                subprocess.run(
                    [
                        "powershell",
                        "-NoProfile",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-File",
                        str(script),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    check=False,
                )
    except Exception:  # noqa: BLE001
        pass


def apply_published_main(repo: Path) -> tuple[bool, str]:
    """Hard-reset this checkout to origin/main. Returns (ok, message)."""
    _git(repo, "checkout", "main")
    reset = _git(repo, "reset", "--hard", "origin/main")
    if reset.returncode != 0:
        err = (reset.stderr or reset.stdout or "reset failed").strip()
        return False, err[:240]
    py = sys.executable
    pip = subprocess.run(
        [py, "-m", "pip", "install", "-e", str(repo)],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    _refresh_desktop_launcher(repo)
    if pip.returncode != 0:
        return True, "files updated; pip refresh warned"
    after = _git(repo, "rev-parse", "HEAD")
    return True, _short(after.stdout)


def _log(msg: str) -> None:
    try:
        from evalathan.desk_store import state_dir

        path = state_dir() / "update.log"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(msg.rstrip() + "\n")
    except Exception:  # noqa: BLE001
        pass


def _close_splash() -> None:
    try:
        from evalathan.launch_splash import request_close

        request_close()
    except Exception:  # noqa: BLE001
        pass


def _spawn_fuss_splash() -> None:
    try:
        from evalathan.launch_splash import clear_stop, spawn_if_needed

        clear_stop()
        spawn_if_needed()
    except Exception:  # noqa: BLE001
        pass


def _ui_font(size: int, weight: str = "normal") -> tuple:
    family = "Helvetica Neue" if sys.platform == "darwin" else "Segoe UI"
    if weight == "bold":
        return (family, size, "bold")
    return (family, size)


def _native_ask(status: UpdateStatus) -> bool | None:
    """OS-native Yes/No. Returns None if native UI is unavailable."""
    title = "EVALATHAN update"
    body = (
        "A newer desk is on GitHub.\n\n"
        f"This PC:   {_short(status.local) or '?'}\n"
        f"Published: {_short(status.remote) or '?'}\n\n"
        "Update now so this machine matches main?"
    )
    if sys.platform == "win32":
        try:
            import ctypes

            # MB_YESNO | MB_ICONQUESTION | MB_TOPMOST | MB_SETFOREGROUND
            flags = 0x04 | 0x20 | 0x40000 | 0x10000
            result = ctypes.windll.user32.MessageBoxW(0, body, title, flags)
            return result == 6  # IDYES
        except Exception as exc:  # noqa: BLE001
            _log(f"MessageBoxW failed: {exc}")
            return None
    if sys.platform == "darwin":
        try:
            # escape for AppleScript
            safe = body.replace("\\", "\\\\").replace('"', '\\"')
            script = (
                f'display dialog "{safe}" with title "{title}" '
                'buttons {"Not now", "Update now"} default button "Update now" '
                "with icon note"
            )
            proc = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )
            if proc.returncode != 0:
                return False
            return "Update now" in (proc.stdout or "")
        except Exception as exc:  # noqa: BLE001
            _log(f"osascript failed: {exc}")
            return None
    return None


def _tk_ask(status: UpdateStatus) -> bool:
    """Lime-accent Evalathan reminder card (sits above FUSS on Mac)."""
    import tkinter as tk

    decision = {"update": True}  # default Update if closed oddly
    ink = "#0a0a0a"
    card = "#141414"
    edge = "#2e2e2e"
    text = "#f4f4f4"
    muted = "#a3a3a3"
    accent = "#d8e04a"
    blue = "#7eb8ff"

    root = tk.Tk()
    root.title("EVALATHAN")
    root.configure(bg=ink)
    root.resizable(False, False)
    try:
        root.attributes("-topmost", True)
    except Exception:  # noqa: BLE001
        pass

    shell = tk.Frame(root, bg=edge, padx=1, pady=1)
    shell.pack(fill="both", expand=True)
    tk.Frame(shell, bg=accent, height=3).pack(fill="x")
    body = tk.Frame(shell, bg=card, padx=32, pady=28)
    body.pack(fill="both", expand=True)

    tk.Label(
        body, text="EVALATHAN", bg=card, fg=accent, font=_ui_font(10, "bold"), anchor="w"
    ).pack(fill="x")
    tk.Label(
        body,
        text="A newer desk is ready",
        bg=card,
        fg=text,
        font=_ui_font(18, "bold"),
        anchor="w",
        pady=(10, 0),
    ).pack(fill="x")
    tk.Label(
        body,
        text=(
            "GitHub main moved ahead of this install.\n"
            "Update now so your desk matches every other machine."
        ),
        bg=card,
        fg=muted,
        font=_ui_font(11),
        justify="left",
        anchor="w",
        pady=(12, 0),
    ).pack(fill="x")

    meta = tk.Frame(body, bg="#1a1a1a", padx=14, pady=12)
    meta.pack(fill="x", pady=(18, 0))
    mono = ("Menlo", 10) if sys.platform == "darwin" else ("Consolas", 10)
    tk.Label(meta, text="This PC", bg="#1a1a1a", fg=muted, font=_ui_font(9)).grid(
        row=0, column=0, sticky="w"
    )
    tk.Label(
        meta, text=_short(status.local) or "?", bg="#1a1a1a", fg=text, font=mono
    ).grid(row=0, column=1, sticky="e", padx=(24, 0))
    tk.Label(
        meta, text="Published", bg="#1a1a1a", fg=muted, font=_ui_font(9), pady=(6, 0)
    ).grid(row=1, column=0, sticky="w")
    tk.Label(
        meta,
        text=_short(status.remote) or "?",
        bg="#1a1a1a",
        fg=blue,
        font=mono,
        pady=(6, 0),
    ).grid(row=1, column=1, sticky="e", padx=(24, 0))
    meta.columnconfigure(1, weight=1)

    actions = tk.Frame(body, bg=card)
    actions.pack(fill="x", pady=(22, 0))

    def on_update() -> None:
        decision["update"] = True
        root.destroy()

    def on_skip() -> None:
        decision["update"] = False
        root.destroy()

    tk.Button(
        actions,
        text="Not now",
        command=on_skip,
        bg="#1f1f1f",
        fg=muted,
        activebackground="#2a2a2a",
        activeforeground=text,
        relief="flat",
        bd=0,
        padx=20,
        pady=11,
        font=_ui_font(11),
        cursor="hand2",
    ).pack(side="right")
    tk.Button(
        actions,
        text="Update now",
        command=on_update,
        bg=accent,
        fg="#111",
        activebackground="#e8f05a",
        activeforeground="#111",
        relief="flat",
        bd=0,
        padx=22,
        pady=11,
        font=_ui_font(11, "bold"),
        cursor="hand2",
    ).pack(side="right", padx=(0, 10))

    root.protocol("WM_DELETE_WINDOW", on_skip)
    root.update_idletasks()
    w = max(460, root.winfo_reqwidth())
    h = root.winfo_reqheight()
    x = max(40, (root.winfo_screenwidth() - w) // 2)
    y = max(40, (root.winfo_screenheight() - h) // 3)
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.lift()
    root.focus_force()
    root.mainloop()
    return bool(decision["update"])


def _ask_user(status: UpdateStatus) -> bool:
    """
    Mac: FUSS circle first, then reminder card on top.
    Windows: drop splash so the ask cannot sit under the circle, then card / native box.
    """
    if sys.platform == "win32":
        _close_splash()
    else:
        _spawn_fuss_splash()
        try:
            import time

            time.sleep(0.45)
        except Exception:  # noqa: BLE001
            pass

    # Prefer native box on Windows (always visible). Mac keeps the branded card.
    if sys.platform == "win32":
        native = _native_ask(status)
        if native is not None:
            _log(f"ask_user native windows choice={'update' if native else 'skip'}")
            return native

    try:
        choice = _tk_ask(status)
        _log(f"ask_user tk choice={'update' if choice else 'skip'}")
        return choice
    except Exception as exc:  # noqa: BLE001
        _log(f"ask_user tk failed: {exc}")
        native = _native_ask(status)
        if native is not None:
            _log(f"ask_user native fallback choice={'update' if native else 'skip'}")
            return native
        # Dialog impossible - apply so the globe stays on published main.
        _log("ask_user unavailable; auto-applying published main")
        return True


def _reexec_desk() -> None:
    """Start a fresh open_desk and exit this process."""
    os.environ["EVALATHAN_RELAUNCHED"] = "1"
    os.environ["EVALATHAN_SKIP_UPDATE"] = "1"
    code = "from evalathan.webdesk import open_desk; raise SystemExit(open_desk())"
    env = os.environ.copy()
    kwargs: dict = {
        "args": [sys.executable, "-c", code],
        "env": env,
        "stdin": subprocess.DEVNULL,
        "close_fds": True,
    }
    if sys.platform == "win32":
        kwargs["creationflags"] = (
            getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
            | getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
        )
        kwargs["stdout"] = subprocess.DEVNULL
        kwargs["stderr"] = subprocess.DEVNULL
    else:
        kwargs["start_new_session"] = True
    try:
        subprocess.Popen(**kwargs)
        _log("reexec: spawned fresh open_desk")
    except OSError as exc:
        _log(f"reexec Popen failed ({exc}); trying execv")
        os.execv(sys.executable, [sys.executable, "-c", code])
        return
    # 42 = desk already relaunched; launchers must not open a second window.
    raise SystemExit(42)


def _migrate_legacy_desktop_launcher(repo: Path) -> None:
    if sys.platform != "darwin":
        return
    app = Path.home() / "Desktop" / "Evalathan.app" / "Contents" / "MacOS" / "Evalathan"
    if not app.is_file():
        return
    try:
        text = app.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return
    # Refresh Desktop app whenever install script exists (picks up launcher fixes).
    if "reset --hard" in text or "Prefetch only" in text:
        _refresh_desktop_launcher(repo)


def ensure_published_main(*, interactive: bool = True) -> None:
    """
    If origin/main is ahead: ask Update now / Not now, then apply + relaunch.
    If the ask UI fails, auto-apply so installs cannot stay stuck forever.
    """
    if os.environ.get("EVALATHAN_SKIP_UPDATE", "").strip() in ("1", "true", "yes"):
        _log("ensure: SKIP_UPDATE set")
        return
    if os.environ.get("EVALATHAN_RELAUNCHED", "").strip() == "1":
        os.environ.pop("EVALATHAN_RELAUNCHED", None)
        _log("ensure: RELAUNCHED one-shot clear")
        return

    root = repo_root()
    if root is not None:
        _migrate_legacy_desktop_launcher(root)

    status = check_for_update(fetch=True)
    _log(
        f"check repo={status.repo} local={_short(status.local)} "
        f"remote={_short(status.remote)} behind={status.behind} err={status.error!r}"
    )
    if status.error or not status.behind:
        return

    apply = True
    if interactive:
        try:
            apply = _ask_user(status)
        except Exception as exc:  # noqa: BLE001
            _log(f"ensure ask crashed ({exc}); auto-applying")
            apply = True
    if not apply:
        _log("ensure: user chose Not now")
        return

    _spawn_fuss_splash()
    ok, detail = apply_published_main(status.repo)
    if not ok:
        _log(f"apply failed: {detail}")
        print(f"Evalathan update failed: {detail}", flush=True)
        return
    _log(f"apply ok: {detail}")
    try:
        _reexec_desk()
    except SystemExit:
        raise
    except OSError as exc:
        _log(f"reexec failed: {exc}")
        print(f"Evalathan updated but could not restart: {exc}", flush=True)


def sync_or_prompt() -> int:
    """CLI/launcher entry: run ensure_published_main. 42 = desk already relaunched."""
    try:
        ensure_published_main(interactive=True)
    except SystemExit as exc:
        code = exc.code
        return int(code) if isinstance(code, int) else 0
    except Exception as exc:  # noqa: BLE001
        _log(f"sync_or_prompt failed: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(sync_or_prompt())
