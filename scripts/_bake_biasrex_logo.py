"""Bake Biasrex emblem into glossary card + UI logo assets (black / white / grey)."""
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]

# Black UI emblem (size/placement lock).
BLACK_UI = ROOT / "ui" / "v2" / "assets" / "biasrex-logo.png"
# Full-transparent emblem for white / light backgrounds (and glossary card).
SRC_WHITE = ROOT / "assets" / "BIASREX_full_trans_FINAL.png"
# Grey theme: copy of white-screen logo, darkened to peer engine grey midtones (~63-66).
GREY_FACTOR = 0.38


def fit_to_black_canvas(src: Path, target_w: int, target_h: int) -> Image.Image:
    """Scale the full source frame into the black UI canvas; do not tight-crop alpha."""
    im = Image.open(src).convert("RGBA")
    fitted = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    scale = min(target_w / im.width, target_h / im.height)
    nw = int(round(im.width * scale))
    nh = int(round(im.height * scale))
    resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
    ox = (target_w - nw) // 2
    oy = (target_h - nh) // 2
    fitted.paste(resized, (ox, oy), resized)
    return fitted


def grey_from_white(white: Image.Image, factor: float = GREY_FACTOR) -> Image.Image:
    """Grey-mode art = white-screen emblem, luminance matched to Benchrex/Dehydrus greys."""
    gray = ImageOps.grayscale(white)
    g = Image.eval(gray, lambda p: int(p * factor))
    a = white.split()[-1]
    return Image.merge("RGBA", (g, g, g, a))


def main() -> None:
    black = Image.open(BLACK_UI).convert("RGBA")
    target_w, target_h = black.size
    if (target_w, target_h) != (630, 655):
        raise SystemExit(f"unexpected black UI size {target_w}x{target_h}")

    white = fit_to_black_canvas(SRC_WHITE, target_w, target_h)
    grey = grey_from_white(white)

    card_path = ROOT / "assets" / "glossary" / "cards" / "biasrex.png"
    white_png = ROOT / "ui" / "v2" / "assets" / "biasrex-logo-white.png"
    white_webp = ROOT / "ui" / "v2" / "assets" / "biasrex-logo-white.webp"
    grey_png = ROOT / "ui" / "v2" / "assets" / "biasrex-logo-grey.png"
    grey_webp = ROOT / "ui" / "v2" / "assets" / "biasrex-logo-grey.webp"

    white.save(card_path, "PNG", optimize=True)
    white.save(white_png, "PNG", optimize=True)
    white.save(white_webp, "WEBP", quality=90, method=6)
    grey.save(grey_png, "PNG", optimize=True)
    grey.save(grey_webp, "WEBP", quality=90, method=6)

    for p in (card_path, white_png, white_webp, grey_png, grey_webp):
        im = Image.open(p)
        print(p.relative_to(ROOT), im.size, im.mode, p.stat().st_size)


if __name__ == "__main__":
    main()
