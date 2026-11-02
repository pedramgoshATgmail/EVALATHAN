"""Persist Hydra desk run sets on disk so saved evals survive restart."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def state_dir() -> Path:
    """User-local Evalathan state folder (not inside the clone's temp tree)."""
    override = os.environ.get("EVALATHAN_STATE_DIR", "").strip()
    if override:
        path = Path(override)
    else:
        path = Path.home() / ".evalathan"
    path.mkdir(parents=True, exist_ok=True)
    return path


def runs_path() -> Path:
    return state_dir() / "run_sets.json"


def load_run_sets() -> list[Any]:
    path = runs_path()
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("runSets"), list):
        return data["runSets"]
    return []


def save_run_sets(run_sets: list[Any]) -> Path:
    if not isinstance(run_sets, list):
        raise ValueError("run_sets must be a JSON array.")
    path = runs_path()
    payload = json.dumps(run_sets[:24], ensure_ascii=False, indent=2)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(payload + "\n", encoding="utf-8")
    tmp.replace(path)
    return path
