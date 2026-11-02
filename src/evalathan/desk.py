"""A small window: paste a GitHub link or a folder, then evaluate it."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

_GITHUB = re.compile(
    r"^https?://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?(?:/.*)?$",
    re.IGNORECASE,
)


def classify(text: str) -> tuple[str, str]:
    """Return ('github', url) or ('path', text). Empty text is refused."""
    raw = text.strip().strip('"')
    if not raw:
        raise ValueError("Paste a GitHub link or a folder on this PC.")
    if _GITHUB.match(raw):
        return "github", raw
    return "path", raw


def checkout_name(url: str) -> str:
    match = _GITHUB.match(url.strip())
    if not match:
        raise ValueError("That is not a github.com link to a repository.")
    owner = match.group("owner")
    repo = match.group("repo")
    if owner in {".", ".."} or repo in {".", ".."}:
        raise ValueError("That GitHub link is not a repository.")
    return f"{owner}__{repo}"


def prepare(text: str, scans: Path | None = None) -> tuple[Path, str]:
    """Turn a pasted link or folder into a directory Hydra can read."""
    kind, raw = classify(text)
    if kind == "path":
        folder = Path(raw).expanduser()
        if not folder.is_dir():
            raise ValueError(f"That folder was not found: {folder}")
        return folder, ""
    root = scans if scans is not None else Path.home() / "evalathan-scans"
    root.mkdir(parents=True, exist_ok=True)
    dest = root / checkout_name(raw)
    if (dest / ".git").is_dir():
        return dest, f"Using the copy already downloaded at {dest}"
    try:
        subprocess.run(
            ["git", "clone", raw, str(dest)],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise ValueError(
            "Git is not installed, so a GitHub link cannot be downloaded. "
            "Paste a folder on this PC, or install Git for Windows."
        ) from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise ValueError(detail or "Git could not download that repository.") from exc
    return dest, f"Downloaded to {dest}"


def add_heading(frame, root) -> None:
    """HYDRA at the left. The mark sits at the top-right corner."""
    import tkinter as tk
    from tkinter import ttk

    head = ttk.Frame(frame)
    head.pack(fill="x")
    ttk.Label(head, text="HYDRA", font=("Segoe UI", 18, "bold")).pack(side="left")
    logo_path = Path(__file__).with_name("hydra-logo.png")
    if not logo_path.is_file():
        return
    image = tk.PhotoImage(file=str(logo_path))
    step = max(1, round(image.height() / round(56 * 1.12 * 1.16 * 1.11)))
    shown = image.subsample(step, step) if step > 1 else image
    root.iconphoto(True, shown)
    root._hydra_logo = image
    root._hydra_mark = shown
    ttk.Label(head, image=shown).pack(side="right")


def open_desk() -> int:
    """Open the ui/v2 browser desk; Evaluate still runs prepare() + Hydra conduct()."""
    from evalathan.webdesk import open_desk as open_web_desk

    return open_web_desk()
