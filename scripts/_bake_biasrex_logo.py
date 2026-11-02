"""One-shot: bake Biasrex emblem into glossary card + UI logo assets."""
from pathlib import Path

from PIL import Image, ImageOps

SRC = Path(
    r"C:\Users\admin\.cursor\projects\c-Users-admin-Desktop-Altnoble-Clients-AckmanZiff-AZ-Agent-CHARLIE-07-14-2026-az-signal-engine-main\assets\BIASREX_FINAL-b8e0e828-39cb-4d51-ad34-67737527e8ff.png"
)
ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    # Keep interior black matte (same as Benchrex / Dehydrus emblems).
    # Outside the circle is already transparent in the source.
    cleaned = Image.open(SRC).convert("RGBA")

    bbox = cleaned.getbbox()
    pad = 8
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(cleaned.width, x1 + pad)
    y1 = min(cleaned.height, y1 + pad)
    cropped = cleaned.crop((x0, y0, x1, y1))

    target_w, target_h = 630, 655
    fitted = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    scale = min(target_w / cropped.width, target_h / cropped.height)
    nw = int(round(cropped.width * scale))
    nh = int(round(cropped.height * scale))
    resized = cropped.resize((nw, nh), Image.Resampling.LANCZOS)
    ox = (target_w - nw) // 2
    oy = (target_h - nh) // 2
    fitted.paste(resized, (ox, oy), resized)

    card_path = ROOT / "assets" / "glossary" / "cards" / "biasrex.png"
    ui_png = ROOT / "ui" / "v2" / "assets" / "biasrex-logo.png"
    ui_webp = ROOT / "ui" / "v2" / "assets" / "biasrex-logo.webp"
    grey_png = ROOT / "ui" / "v2" / "assets" / "biasrex-logo-grey.png"
    grey_webp = ROOT / "ui" / "v2" / "assets" / "biasrex-logo-grey.webp"

    fitted.save(card_path, "PNG", optimize=True)
    fitted.save(ui_png, "PNG", optimize=True)
    fitted.save(ui_webp, "WEBP", quality=90, method=6)

    gray = ImageOps.grayscale(fitted)
    gray = Image.eval(gray, lambda p: int(p * 0.68))
    a = fitted.split()[-1]
    grey = Image.merge("RGBA", (gray, gray, gray, a))
    grey.save(grey_png, "PNG", optimize=True)
    grey.save(grey_webp, "WEBP", quality=90, method=6)

    for p in (card_path, ui_png, ui_webp, grey_png, grey_webp):
        im = Image.open(p)
        print(p.relative_to(ROOT), im.size, im.mode, p.stat().st_size)


if __name__ == "__main__":
    main()
