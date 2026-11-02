"""Global desk update ask: on launch, if origin/main is ahead, prompt then sync."""

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
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists() and (parent / "ui" / "v2" / "index.html").is_file():
            return parent
    return None


def _git(repo: Path, *args: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _short(sha: str) -> str:
    return (sha or "").strip()[:7]


def _log(msg: str) -> None:
    try:
        from evalathan.desk_store import state_dir

        path = state_dir() / "update.log"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(msg.rstrip() + "\n")
    except Exception:  # noqa: BLE001
        pass


def check_for_update(repo: Path | None = None, *, fetch: bool = True) -> UpdateStatus:
    root = repo or repo_root()
    if root is None:
        return UpdateStatus(Path("."), "", "", False, error="not a git checkout")
    if shutil.which("git") is None:
        return UpdateStatus(root, "", "", False, error="git not found")
    if fetch:
        fetched = _git(root, "fetch", "origin", "main")
        if fetched.returncode != 0:
            fetched = _git(root, "fetch", "origin")
            if fetched.returncode != 0:
                err = (fetched.stderr or fetched.stdout or "fetch failed").strip()
                return UpdateStatus(root, "", "", False, error=err[:240])
    local_p = _git(root, "rev-parse", "HEAD")
    remote_p = _git(root, "rev-parse", "origin/main")
    if local_p.returncode != 0 or remote_p.returncode != 0:
        return UpdateStatus(root, "", "", False, error="could not resolve HEAD/origin/main")
    local = local_p.stdout.strip()
    remote = remote_p.stdout.strip()
    return UpdateStatus(root, local, remote, behind=(bool(remote) and local != remote))


def _refresh_desktop_launcher(repo: Path) -> None:
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
    _git(repo, "checkout", "main")
    reset = _git(repo, "reset", "--hard", "origin/main")
    if reset.returncode != 0:
        err = (reset.stderr or reset.stdout or "reset failed").strip()
        return False, err[:240]
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", str(repo)],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    _refresh_desktop_launcher(repo)
    after = _git(repo, "rev-parse", "HEAD")
    return True, _short(after.stdout)


def _close_splash() -> None:
    try:
        from evalathan.launch_splash import request_close

        request_close()
    except Exception:  # noqa: BLE001
        pass


def _spawn_splash() -> None:
    try:
        from evalathan.launch_splash import clear_stop, spawn_if_needed

        clear_stop()
        spawn_if_needed()
    except Exception:  # noqa: BLE001
        pass


def _native_ask(status: UpdateStatus) -> bool | None:
    """OS-native Yes/No - reliable on Windows and Mac. None if unavailable."""
    title = "EVALATHAN"
    body = (
        "A newer Evalathan desk is on GitHub.\n\n"
        f"This PC:   {_short(status.local) or '?'}\n"
        f"Published: {_short(status.remote) or '?'}\n\n"
        "Update now to the latest GitHub version?"
    )
    if sys.platform == "win32":
        try:
            import ctypes

            # Yes/No + Question + Topmost + SetForeground
            flags = 0x04 | 0x20 | 0x40000 | 0x10000
            result = ctypes.windll.user32.MessageBoxW(0, body, title, flags)
            return result == 6  # IDYES
        except Exception as exc:  # noqa: BLE001
            _log(f"MessageBoxW failed: {exc}")
            return None
    if sys.platform == "darwin":
        try:
            safe = (
                body.replace("\\", "\\\\")
                .replace('"', '\\"')
                .replace("\n", "\\n")
            )
            script = (
                f'set answer to button returned of (display dialog "{safe}" '
                f'with title "{title}" buttons {{"Not now", "Update now"}} '
                f'default button "Update now" with icon note)'
            )
            proc = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=600,
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
    import tkinter as tk

    decision = {"update": True}
    card = "#141414"
    edge = "#2e2e2e"
    text = "#f4f4f4"
    muted = "#a3a3a3"
    accent = "#d8e04a"
    blue = "#7eb8ff"
    family = "Helvetica Neue" if sys.platform == "darwin" else "Segoe UI"

    root = tk.Tk()
    root.title("EVALATHAN")
    root.configure(bg="#0a0a0a")
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
        body, text="EVALATHAN", bg=card, fg=accent, font=(family, 10, "bold"), anchor="w"
    ).pack(fill="x")
    tk.Label(
        body,
        text="Update available",
        bg=card,
        fg=text,
        font=(family, 18, "bold"),
        anchor="w",
        pady=(10, 0),
    ).pack(fill="x")
    tk.Label(
        body,
        text="GitHub has a newer desk than this install.\nUpdate now so you match every other machine.",
        bg=card,
        fg=muted,
        font=(family, 11),
        justify="left",
        anchor="w",
        pady=(12, 0),
    ).pack(fill="x")

    meta = tk.Frame(body, bg="#1a1a1a", padx=14, pady=12)
    meta.pack(fill="x", pady=(18, 0))
    mono = ("Menlo", 10) if sys.platform == "darwin" else ("Consolas", 10)
    tk.Label(meta, text="This PC", bg="#1a1a1a", fg=muted, font=(family, 9)).grid(
        row=0, column=0, sticky="w"
    )
    tk.Label(
        meta, text=_short(status.local) or "?", bg="#1a1a1a", fg=text, font=mono
    ).grid(row=0, column=1, sticky="e", padx=(24, 0))
    tk.Label(
        meta, text="GitHub", bg="#1a1a1a", fg=muted, font=(family, 9), pady=(6, 0)
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
        relief="flat",
        bd=0,
        padx=20,
        pady=11,
        font=(family, 11),
        cursor="hand2",
    ).pack(side="right")
    tk.Button(
        actions,
        text="Update now",
        command=on_update,
        bg=accent,
        fg="#111",
        relief="flat",
        bd=0,
        padx=22,
        pady=11,
        font=(family, 11, "bold"),
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


def ask_user_to_update(status: UpdateStatus) -> bool:
    """
    Ask Update now / Not now.
    Windows: close splash then native MessageBox (always visible).
    Mac: splash may stay; native osascript dialog (always visible).
    Fallback: tk card, then auto-yes if UI impossible.
    """
    _close_splash()
    if sys.platform == "darwin":
        _spawn_splash()
        try:
            import time

            time.sleep(0.35)
        except Exception:  # noqa: BLE001
            pass

    native = _native_ask(status)
    if native is not None:
        _log(f"ask native choice={'update' if native else 'skip'}")
        return native
    try:
        choice = _tk_ask(status)
        _log(f"ask tk choice={'update' if choice else 'skip'}")
        return choice
    except Exception as exc:  # noqa: BLE001
        _log(f"ask UI failed ({exc}); defaulting to Update now")
        return True


def _reexec_desk() -> None:
    os.environ["EVALATHAN_SKIP_UPDATE"] = "1"
    os.environ["EVALATHAN_RELAUNCHED"] = "1"
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
    subprocess.Popen(**kwargs)
    _log("reexec: spawned open_desk")
    raise SystemExit(42)


def _migrate_stale_macos_app(repo: Path) -> None:
    """Rewrite Desktop Evalathan.app if it still silent-resets instead of asking."""
    if sys.platform != "darwin":
        return
    app = Path.home() / "Desktop" / "Evalathan.app" / "Contents" / "MacOS" / "Evalathan"
    if not app.is_file():
        return
    try:
        text = app.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return
    if "sync_or_prompt" not in text:
        _log("migrating Desktop Evalathan.app to update-ask launcher")
        _refresh_desktop_launcher(repo)


def ensure_published_main(*, interactive: bool = True) -> None:
    """
    Every launch: fetch GitHub. If behind, popup asks Update now / Not now.
    Update now -> hard-reset to origin/main, refresh Desktop launcher, relaunch desk.
    """
    if os.environ.get("EVALATHAN_SKIP_UPDATE", "").strip() in ("1", "true", "yes"):
        return
    if os.environ.get("EVALATHAN_RELAUNCHED", "").strip() == "1":
        os.environ.pop("EVALATHAN_RELAUNCHED", None)
        return

    root = repo_root()
    if root is not None:
        _migrate_stale_macos_app(root)

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
            apply = ask_user_to_update(status)
        except Exception as exc:  # noqa: BLE001
            _log(f"ask crashed ({exc}); applying update")
            apply = True
    if not apply:
        _log("user chose Not now")
        return

    _spawn_splash()
    ok, detail = apply_published_main(status.repo)
    if not ok:
        _log(f"apply failed: {detail}")
        print(f"Evalathan update failed: {detail}", flush=True)
        return
    _log(f"apply ok: {detail}")
    _reexec_desk()


def sync_or_prompt() -> int:
    """Launcher entry. Exit 42 = desk already relaunched after Update now."""
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
