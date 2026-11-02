"""Serve Evalathan ui/v2 with the real Hydra evaluate API (same path as the old Tk desk)."""
from __future__ import annotations

import sys
from pathlib import Path

# Allow `python ui/v2/serve.py` from a checkout without install
_ROOT = Path(__file__).resolve().parents[2]
_SRC = _ROOT / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from evalathan.webdesk import open_desk  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(open_desk())
