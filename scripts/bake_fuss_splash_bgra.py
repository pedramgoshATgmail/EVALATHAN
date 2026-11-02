"""Bake premultiplied BGRA splash frames (4x coverage AA, no color-key rim).

Run from repo root:
  .venv\\Scripts\\python.exe scripts/bake_fuss_splash_bgra.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "ui" / "v2" / "launch_splash.py"
ASSETS = ROOT / "ui" / "v2" / "assets"
SIZE = 220


def _load_splash():
    spec = importlib.util.spec_from_file_location("launch_splash_bake", UI)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    mod = _load_splash()
    logo = ASSETS / "fuss-splash.png"
    if not logo.is_file():
        print("missing", logo, file=sys.stderr)
        return 1

    base = mod._build_base_rgba(logo, SIZE, supersample=8)
    for phase in range(3):
        frame = mod._draw_caption(base, phase)
        data = mod._rgba_to_premultiplied_bgra(frame)
        out = ASSETS / f"fuss-splash-p{phase}.bgra"
        out.write_bytes(data)
        corner_a = data[3]
        top = data[(1 * SIZE + SIZE // 2) * 4 : (1 * SIZE + SIZE // 2) * 4 + 4]
        print(
            f"phase {phase} wrote {out.name} corner_a={corner_a} "
            f"y1_center_bgra={list(top)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
