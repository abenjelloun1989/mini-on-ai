#!/usr/bin/env python3
"""
generate_thumbnails.py
Generates branded 1280x720 PNG thumbnails for every product.
Saves to products/{id}/assets/thumbnail.png
Updates meta.json and product-catalog.json with thumbnail path.
"""

import json
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
CATALOG_PATH = ROOT / "data" / "product-catalog.json"
PRODUCTS_DIR = ROOT / "products"
THUMB_DIR = ROOT / "site" / "images" / "thumbnails"

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_PATH = "/System/Library/Fonts/HelveticaNeue.ttc"

def _font(size, bold=False):
    # Index 0 = regular, index 4 = bold in HelveticaNeue.ttc
    idx = 4 if bold else 0
    try:
        return ImageFont.truetype(FONT_PATH, size, index=idx)
    except Exception:
        return ImageFont.load_default()

# ── Brand colors per category ─────────────────────────────────────────────────
CATEGORY_COLORS = {
    "n8n-template":      "#7c3aed",  # purple
    "prompt-packs":      "#1d4ed8",  # blue
    "mini-guide":        "#15803d",  # green
    "claude-code-skill": "#c2410c",  # orange/red
    "checklist":         "#b91c1c",  # red
    "swipe-file":        "#0f766e",  # teal
}
DEFAULT_COLOR = "#334155"  # slate fallback

CATEGORY_LABELS = {
    "n8n-template":      "n8n Template",
    "prompt-packs":      "Prompt Pack",
    "mini-guide":        "Mini Guide",
    "claude-code-skill": "Claude Code Skill",
    "checklist":         "Checklist",
    "swipe-file":        "Swipe File",
}

# ── Canvas ────────────────────────────────────────────────────────────────────
W, H = 1280, 720


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def darken(rgb, factor=0.75):
    return tuple(int(c * factor) for c in rgb)


def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.ellipse([x0, y0, x0 + 2*radius, y0 + 2*radius], fill=fill)
    draw.ellipse([x1 - 2*radius, y0, x1, y0 + 2*radius], fill=fill)
    draw.ellipse([x0, y1 - 2*radius, x0 + 2*radius, y1], fill=fill)
    draw.ellipse([x1 - 2*radius, y1 - 2*radius, x1, y1], fill=fill)


def generate_thumbnail(title: str, category: str, output_path: Path):
    bg_hex = CATEGORY_COLORS.get(category, DEFAULT_COLOR)
    bg_rgb = hex_to_rgb(bg_hex)
    dark_rgb = darken(bg_rgb, 0.6)

    img = Image.new("RGB", (W, H), bg_rgb)
    draw = ImageDraw.Draw(img)

    # ── Subtle gradient-like dark strip at bottom ──────────────────────────
    for i in range(200):
        alpha = i / 200
        blended = tuple(int(bg_rgb[c] * (1 - alpha) + dark_rgb[c] * alpha) for c in range(3))
        draw.rectangle([0, H - 200 + i, W, H - 200 + i + 1], fill=blended)

    # ── Decorative circles (top-right) ────────────────────────────────────
    lighter = tuple(min(255, int(c * 1.25)) for c in bg_rgb)
    draw.ellipse([W - 300, -150, W + 100, 250], fill=lighter, outline=None)
    draw.ellipse([W - 200, -50, W + 50, 200], fill=darken(bg_rgb, 0.85))

    # ── Category badge (top-left) ─────────────────────────────────────────
    badge_font = _font(28, bold=True)
    label = CATEGORY_LABELS.get(category, category).upper()
    badge_padding = (20, 10)
    try:
        bbox = draw.textbbox((0, 0), label, font=badge_font)
        bw = bbox[2] - bbox[0] + badge_padding[0] * 2
        bh = bbox[3] - bbox[1] + badge_padding[1] * 2
    except Exception:
        bw, bh = 200, 50
    badge_x, badge_y = 64, 60
    draw_rounded_rect(draw, (badge_x, badge_y, badge_x + bw, badge_y + bh), 8, (255, 255, 255, 40))
    draw.rectangle([badge_x, badge_y, badge_x + bw, badge_y + bh], fill=(255, 255, 255, 30))
    # Semi-transparent badge using a slightly lighter color
    badge_fill = tuple(min(255, int(c + 40)) for c in bg_rgb)
    draw_rounded_rect(draw, (badge_x, badge_y, badge_x + bw, badge_y + bh), 8, badge_fill)
    draw.text((badge_x + badge_padding[0], badge_y + badge_padding[1]), label, font=badge_font, fill=(255, 255, 255))

    # ── Product title ─────────────────────────────────────────────────────
    title_font = _font(72, bold=True)
    small_title_font = _font(56, bold=True)

    # Wrap title to fit width
    max_width = W - 128
    wrapped = textwrap.wrap(title, width=28)
    if len(wrapped) > 3:
        wrapped = wrapped[:3]
        wrapped[-1] = wrapped[-1][:20] + "…"

    # Use smaller font if title is long
    use_font = title_font if len(wrapped) <= 2 and max(len(l) for l in wrapped) <= 22 else small_title_font

    line_h = use_font.size + 16
    total_h = line_h * len(wrapped)
    start_y = (H - total_h) // 2 + 20  # slightly below center

    for i, line in enumerate(wrapped):
        draw.text((64, start_y + i * line_h), line, font=use_font, fill=(255, 255, 255))

    # ── Bottom watermark ──────────────────────────────────────────────────
    wm_font = _font(32)
    draw.text((64, H - 64), "mini-on-ai.com", font=wm_font, fill=(255, 255, 255, 180))

    # ── Right accent bar ──────────────────────────────────────────────────
    draw.rectangle([W - 8, 0, W, H], fill=darken(bg_rgb, 0.5))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG", optimize=True)


def run():
    THUMB_DIR.mkdir(parents=True, exist_ok=True)

    with open(CATALOG_PATH) as f:
        catalog = json.load(f)

    ok = 0
    for product in catalog["products"]:
        pid = product["id"]
        title = product["title"]
        category = product.get("category", "")

        # Write to site/images/thumbnails/{id}.png
        thumb_path = THUMB_DIR / f"{pid}.png"
        generate_thumbnail(title, category, thumb_path)

        # Path relative to site root (used in <img src="...">)
        site_thumb = f"images/thumbnails/{pid}.png"

        # Update meta.json
        meta_path = PRODUCTS_DIR / pid / "meta.json"
        if meta_path.exists():
            with open(meta_path) as f:
                meta = json.load(f)
            meta["thumbnail"] = site_thumb
            with open(meta_path, "w") as f:
                json.dump(meta, f, indent=2)

        # Update catalog entry
        product["thumbnail"] = site_thumb
        ok += 1
        print(f"[thumbnails] {pid}")

    with open(CATALOG_PATH, "w") as f:
        json.dump(catalog, f, indent=2)

    print(f"\n[thumbnails] Done — {ok} thumbnails generated.")


if __name__ == "__main__":
    run()
