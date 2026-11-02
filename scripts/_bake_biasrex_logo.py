"""Bake Biasrex emblem into glossary card + white/grey UI assets.

Black-theme desk emblem (biasrex-logo.png / .webp) is intentionally NOT overwritten.
White-screen / glossary use assets/BIASREX_full_trans_FINAL.png.
"""
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "BIASREX_full_trans_FINAL.png"
BLACK_UI = ROOT / "ui" / "v2" / "assets" / "biasrex-logo.png"
GREY_FACTOR = 0.38


def grey_from_white(white: Image.Image, factor: float = GREY_FACTOR) -> Image.Image:
    gray = ImageOps.grayscale(white)
    g = Image.eval(gray, lambda p: int(p * factor))
    a = white.split()[-1]
    return Image.merge("RGBA", (g, g, g, a))


def main() -> None:
    src = Image.open(SRC).convert("RGBA")
    if src.size != (630, 655):
        raise SystemExit(f"unexpected source size {src.size}; expected 630x655")

    # Size lock only - do not replace black art.
    black_ref = Image.open(BLACK_UI).convert("RGBA")
    if black_ref.size != (630, 655):
        raise SystemExit(f"unexpected black UI size {black_ref.size}")

    white = src.copy()
    grey = grey_from_white(white)

    outs = {
        ROOT / "assets" / "glossary" / "cards" / "biasrex.png": white,
        ROOT / "ui" / "v2" / "assets" / "biasrex-logo-white.png": white,
        ROOT / "ui" / "v2" / "assets" / "biasrex-logo-grey.png": grey,
    }
    webps = {
        ROOT / "ui" / "v2" / "assets" / "biasrex-logo-white.webp": white,
        ROOT / "ui" / "v2" / "assets" / "biasrex-logo-grey.webp": grey,
    }

    for path, im in outs.items():
        im.save(path, "PNG", optimize=True)
        print(path.relative_to(ROOT), im.size, path.stat().st_size)
    for path, im in webps.items():
        im.save(path, "WEBP", quality=90, method=6)
        print(path.relative_to(ROOT), im.size, path.stat().st_size)
    print("left untouched", BLACK_UI.relative_to(ROOT), black_ref.size)


if __name__ == "__main__":
    main()
