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


def _ask_user(status: UpdateStatus) -> bool:
    """Return True if the user chose Update now."""
    try:
        import tkinter as tk
        from tkinter import ttk
    except Exception:  # noqa: BLE001
        return True  # no GUI - apply so published main still wins

    decision = {"update": False}
    root = tk.Tk()
    root.title("EVALATHAN update")
    root.attributes("-topmost", True)
    root.resizable(False, False)
    try:
        root.configure(bg="#111111")
    except Exception:  # noqa: BLE001
        pass

    frame = ttk.Frame(root, padding=18)
    frame.grid(row=0, column=0, sticky="nsew")
    msg = (
        "A newer Evalathan desk is on GitHub.\n\n"
        f"This PC:  {_short(status.local) or '?'}\n"
        f"Published: {_short(status.remote) or '?'}\n\n"
        "Update now so Windows and Mac desks match main?"
    )
    label = ttk.Label(frame, text=msg, justify="left")
    label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))

    def on_update() -> None:
        decision["update"] = True
        root.destroy()

    def on_skip() -> None:
        decision["update"] = False
        root.destroy()

    btn_update = ttk.Button(frame, text="Update now", command=on_update)
    btn_skip = ttk.Button(frame, text="Not now", command=on_skip)
    btn_update.grid(row=1, column=0, padx=(0, 8), sticky="ew")
    btn_skip.grid(row=1, column=1, sticky="ew")
    root.protocol("WM_DELETE_WINDOW", on_skip)
    root.update_idletasks()
    w, h = root.winfo_reqwidth(), root.winfo_reqheight()
    x = max(40, (root.winfo_screenwidth() - w) // 2)
    y = max(40, (root.winfo_screenheight() - h) // 3)
    root.geometry(f"+{x}+{y}")
    root.lift()
    root.focus_force()
    root.mainloop()
    return bool(decision["update"])


def _show_done(sha: str) -> None:
    try:
        import tkinter as tk
        from tkinter import ttk
    except Exception:  # noqa: BLE001
        return
    root = tk.Tk()
    root.title("EVALATHAN")
    root.attributes("-topmost", True)
    root.resizable(False, False)
    frame = ttk.Frame(root, padding=18)
    frame.grid(row=0, column=0)
    ttk.Label(
        frame,
        text=f"Updated to {_short(sha) or 'published main'}.\nRestarting the desk…",
        justify="left",
    ).grid(row=0, column=0, pady=(0, 12))
    ttk.Button(frame, text="OK", command=root.destroy).grid(row=1, column=0)
    root.after(2200, root.destroy)
    root.update_idletasks()
    w, h = root.winfo_reqwidth(), root.winfo_reqheight()
    x = max(40, (root.winfo_screenwidth() - w) // 2)
    y = max(40, (root.winfo_screenheight() - h) // 3)
    root.geometry(f"+{x}+{y}")
    root.mainloop()


def _reexec_desk() -> None:
    """Replace this process with a fresh open_desk so new ui/v2 loads."""
    os.environ["EVALATHAN_RELAUNCHED"] = "1"
    os.environ["EVALATHAN_SKIP_UPDATE"] = "1"  # already on main; skip second popup
    code = (
        "from evalathan.webdesk import open_desk; raise SystemExit(open_desk())"
    )
    os.execv(sys.executable, [sys.executable, "-c", code])


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
    if status.error or not status.behind:
        return

    if interactive and not _ask_user(status):
        return

    ok, detail = apply_published_main(status.repo)
    if not ok:
        print(f"Evalathan update failed: {detail}", flush=True)
        return
    if interactive:
        _show_done(detail if len(detail) <= 12 else status.remote)
    try:
        _reexec_desk()
    except OSError as exc:
        print(f"Evalathan updated but could not restart: {exc}", flush=True)
