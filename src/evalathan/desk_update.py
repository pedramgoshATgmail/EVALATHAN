"""Check GitHub main on desk launch; optional popup to apply published updates."""

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
            # Fall back to full fetch when the remote refspec is older.
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
    # Refresh editable install so src/ matches the new tree.
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


def _spawn_fuss_splash() -> None:
    """FUSS circular splash - show first (Mac order), keep up through update + relaunch."""
    try:
        from evalathan.launch_splash import clear_stop, spawn_if_needed

        clear_stop()
        spawn_if_needed()
    except Exception:  # noqa: BLE001
        pass


def _ui_font(size: int, weight: str = "normal") -> tuple:
    family = "Segoe UI" if sys.platform == "win32" else "Helvetica Neue"
    if weight == "bold":
        return (family, size, "bold")
    return (family, size)


def _ask_user(status: UpdateStatus) -> bool:
    """
    Mac order: FUSS circle is already up (or we start it), then this card sits on top.
    Return True if the user chose Update now.
    """
    _spawn_fuss_splash()
    try:
        import time

        time.sleep(0.35)  # let the circle paint before the reminder card
    except Exception:  # noqa: BLE001
        pass

    try:
        import tkinter as tk
    except Exception as exc:  # noqa: BLE001
        _log(f"ask_user no tkinter: {exc}")
        return True

    decision = {"update": False}
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

    # Outer hairline + lime accent bar (desk reminder, not a system alert)
    shell = tk.Frame(root, bg=edge, padx=1, pady=1)
    shell.pack(fill="both", expand=True)
    accent_bar = tk.Frame(shell, bg=accent, height=3)
    accent_bar.pack(fill="x")
    body = tk.Frame(shell, bg=card, padx=32, pady=28)
    body.pack(fill="both", expand=True)

    tk.Label(
        body,
        text="EVALATHAN",
        bg=card,
        fg=accent,
        font=_ui_font(10, "bold"),
        anchor="w",
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
    tk.Label(
        meta,
        text="This PC",
        bg="#1a1a1a",
        fg=muted,
        font=_ui_font(9),
        anchor="w",
    ).grid(row=0, column=0, sticky="w")
    tk.Label(
        meta,
        text=_short(status.local) or "?",
        bg="#1a1a1a",
        fg=text,
        font=("Consolas", 10) if sys.platform == "win32" else ("Menlo", 10),
        anchor="e",
    ).grid(row=0, column=1, sticky="e", padx=(24, 0))
    tk.Label(
        meta,
        text="Published",
        bg="#1a1a1a",
        fg=muted,
        font=_ui_font(9),
        anchor="w",
        pady=(6, 0),
    ).grid(row=1, column=0, sticky="w")
    tk.Label(
        meta,
        text=_short(status.remote) or "?",
        bg="#1a1a1a",
        fg=blue,
        font=("Consolas", 10) if sys.platform == "win32" else ("Menlo", 10),
        anchor="e",
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

    skip = tk.Button(
        actions,
        text="Not now",
        command=on_skip,
        bg="#1f1f1f",
        fg=muted,
        activebackground="#2a2a2a",
        activeforeground=text,
        relief="flat",
        bd=0,
        highlightthickness=0,
        padx=20,
        pady=11,
        font=_ui_font(11),
        cursor="hand2",
    )
    skip.pack(side="right")

    update = tk.Button(
        actions,
        text="Update now",
        command=on_update,
        bg=accent,
        fg="#111",
        activebackground="#e8f05a",
        activeforeground="#111",
        relief="flat",
        bd=0,
        highlightthickness=0,
        padx=22,
        pady=11,
        font=_ui_font(11, "bold"),
        cursor="hand2",
    )
    update.pack(side="right", padx=(0, 10))

    root.protocol("WM_DELETE_WINDOW", on_skip)
    root.update_idletasks()
    w = max(460, root.winfo_reqwidth())
    h = root.winfo_reqheight()
    x = max(40, (root.winfo_screenwidth() - w) // 2)
    y = max(40, (root.winfo_screenheight() - h) // 3)
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.lift()
    root.focus_force()
    try:
        update.focus_set()
    except Exception:  # noqa: BLE001
        pass
    root.mainloop()
    _log(f"ask_user behind={status.behind} choice={'update' if decision['update'] else 'skip'}")
    return bool(decision["update"])


def _reexec_desk() -> None:
    """Start a fresh open_desk (FUSS splash already up) and exit this process."""
    os.environ["EVALATHAN_RELAUNCHED"] = "1"
    os.environ["EVALATHAN_SKIP_UPDATE"] = "1"  # already on main; skip second popup
    code = (
        "from evalathan.webdesk import open_desk; raise SystemExit(open_desk())"
    )
    env = os.environ.copy()
    kwargs: dict = {
        "args": [sys.executable, "-c", code],
        "env": env,
        "stdin": subprocess.DEVNULL,
        "close_fds": True,
    }
    if sys.platform == "win32":
        # Detach so the Desktop .bat parent can exit without killing the new desk.
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
    raise SystemExit(0)


def _migrate_legacy_desktop_launcher(repo: Path) -> None:
    """
    Older Mac Evalathan.app scripts silent-reset before open_desk, so the
    update popup never appeared. Rewrite those launchers once to fetch-only.
    """
    if sys.platform != "darwin":
        return
    app = Path.home() / "Desktop" / "Evalathan.app" / "Contents" / "MacOS" / "Evalathan"
    if not app.is_file():
        return
    try:
        text = app.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return
    if "reset --hard" in text:
        _refresh_desktop_launcher(repo)


def ensure_published_main(*, interactive: bool = True) -> None:
    """
    On desk launch: if origin/main is ahead, show an update popup.
    Update now applies hard-reset to published main and restarts the desk.
    Not now continues with the local tree.
    """
    if os.environ.get("EVALATHAN_SKIP_UPDATE", "").strip() in ("1", "true", "yes"):
        return
    if os.environ.get("EVALATHAN_RELAUNCHED", "").strip() == "1":
        # Clear one-shot relaunch flag for future cold starts.
        os.environ.pop("EVALATHAN_RELAUNCHED", None)
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

    if interactive and not _ask_user(status):
        return

    # Agree -> keep FUSS circle up, pull, relaunch desk (no second OK).
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
