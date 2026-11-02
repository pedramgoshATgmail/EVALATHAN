"""Bake Biasrex emblem into glossary card + UI logo assets (black / white / grey)."""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path(
    r"C:\Users\admin\.cursor\projects\c-Users-admin-Desktop-Altnoble-Clients-AckmanZiff-AZ-Agent-CHARLIE-07-14-2026-az-signal-engine-main\assets"
)

# Black UI emblem (size/placement lock). White/grey uploads must match this canvas.
BLACK_UI = ROOT / "ui" / "v2" / "assets" / "biasrex-logo.png"
# Full-transparent emblem for white / light backgrounds (and glossary card).
SRC_WHITE = ASSETS / "BIASREX_full_trans_FINAL-5a2453cd-5d2d-491d-b336-32a8e3bbe07d.png"
# Grey-theme match (same geometry as black UI).
SRC_GREY = ASSETS / "BIASREX_GREY_MATCH-ababca29-7d11-47c2-a699-873c51da3d9a.png"


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


def main() -> None:
    target_w, target_h = Image.open(BLACK_UI).size
    if (target_w, target_h) != (630, 655):
        raise SystemExit(f"unexpected black UI size {target_w}x{target_h}")

    white = fit_to_black_canvas(SRC_WHITE, target_w, target_h)
    grey = fit_to_black_canvas(SRC_GREY, target_w, target_h)

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
