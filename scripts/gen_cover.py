#!/usr/bin/env python3
"""
gen_cover.py
Generates a single branded cover image for all products.

Output: site/images/cover-default.png (1280x640)

Usage: python3 scripts/gen_cover.py
"""

import struct
import zlib
import math
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
OUTPUT = ROOT / "site" / "images" / "cover-default.png"

WIDTH, HEIGHT = 1280, 640
INDIGO = (99, 102, 241)       # #6366F1
INDIGO_DARK = (67, 56, 202)   # #4338CA
WHITE = (255, 255, 255)
LIGHT_BG = (238, 242, 255)    # very light indigo tint


# ── PNG encoder (pure Python, no Pillow) ─────────────────────────────────────

def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    c = chunk_type + data
    return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)


def _make_png(pixels: list) -> bytes:
    """pixels: list of HEIGHT rows, each row is list of (R,G,B) tuples."""
    raw = b""
    for row in pixels:
        raw += b"\x00"  # filter type: None
        for r, g, b in row:
            raw += bytes([r, g, b])
    compressed = zlib.compress(raw, 9)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    ihdr = _png_chunk(b"IHDR", ihdr_data)
    idat = _png_chunk(b"IDAT", compressed)
    iend = _png_chunk(b"IEND", b"")
    return sig + ihdr + idat + iend


# ── Drawing primitives ────────────────────────────────────────────────────────

def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def blend(base, overlay, alpha):
    """Alpha blend overlay onto base. alpha in [0,1]."""
    return tuple(int(base[i] * (1 - alpha) + overlay[i] * alpha) for i in range(3))


def in_rounded_rect(px, py, x, y, w, h, r):
    if px < x or px > x + w or py < y or py > y + h:
        return False
    corners = [(x + r, y + r), (x + w - r, y + r),
               (x + r, y + h - r), (x + w - r, y + h - r)]
    for cx, cy in corners:
        if abs(px - cx) <= r and abs(py - cy) <= r:
            dist = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
            if dist > r:
                return False
    return True


def in_circle(px, py, cx, cy, r):
    return math.sqrt((px - cx) ** 2 + (py - cy) ** 2) <= r


def draw_text_pixels(pixels, text, x0, y0, scale, color, char_w=5, char_h=7):
    """Minimal bitmap font renderer using a 5x7 font map."""
    FONT = {
        'm': [[1,0,1,0,1],[1,1,1,1,1],[1,0,1,0,1],[1,0,1,0,1],[1,0,1,0,1],[0,0,0,0,0],[0,0,0,0,0]],
        'i': [[0,1,1,0,0],[0,1,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,1,1,1,0],[0,0,0,0,0],[0,0,0,0,0]],
        'n': [[0,0,0,0,0],[1,0,1,0,0],[1,1,1,1,0],[1,0,0,1,0],[1,0,0,1,0],[0,0,0,0,0],[0,0,0,0,0]],
        'o': [[0,0,0,0,0],[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0],[0,0,0,0,0],[0,0,0,0,0]],
        '-': [[0,0,0,0,0],[0,0,0,0,0],[0,1,1,1,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],
        'a': [[0,0,0,0,0],[0,1,1,1,0],[1,0,0,1,0],[1,1,1,1,0],[1,0,0,1,0],[0,0,0,0,0],[0,0,0,0,0]],
        ' ': [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],
        'A': [[0,1,1,1,0],[1,0,0,0,1],[1,1,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[0,0,0,0,0],[0,0,0,0,0]],
        'I': [[0,1,1,1,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,1,1,1,0],[0,0,0,0,0],[0,0,0,0,0]],
        'D': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0],[0,0,0,0,0],[0,0,0,0,0]],
        'g': [[0,0,0,0,0],[0,1,1,1,0],[1,0,0,1,0],[0,1,1,1,0],[0,0,0,1,0],[0,1,1,1,0],[0,0,0,0,0]],
        'i': [[0,0,0,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,0,0,0]],
        't': [[0,1,0,0,0],[1,1,1,0,0],[0,1,0,0,0],[0,1,0,0,0],[0,0,1,1,0],[0,0,0,0,0],[0,0,0,0,0]],
        'l': [[0,1,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,1,1,1,0],[0,0,0,0,0],[0,0,0,0,0]],
        'P': [[1,1,1,1,0],[1,0,0,0,1],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],
        'r': [[0,0,0,0,0],[1,0,1,1,0],[1,1,0,0,1],[1,0,0,0,0],[1,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],
        'd': [[0,0,0,1,0],[0,0,0,1,0],[0,1,1,1,0],[1,0,0,1,0],[0,1,1,1,0],[0,0,0,0,0],[0,0,0,0,0]],
        'u': [[0,0,0,0,0],[1,0,0,1,0],[1,0,0,1,0],[1,0,0,1,0],[0,1,1,1,0],[0,0,0,0,0],[0,0,0,0,0]],
        'c': [[0,0,0,0,0],[0,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[0,1,1,1,0],[0,0,0,0,0],[0,0,0,0,0]],
        's': [[0,0,0,0,0],[0,1,1,1,0],[1,1,0,0,0],[0,0,1,1,0],[1,1,1,0,0],[0,0,0,0,0],[0,0,0,0,0]],
        'e': [[0,0,0,0,0],[0,1,1,1,0],[1,0,0,1,0],[1,1,1,1,0],[0,1,1,0,0],[0,0,0,0,0],[0,0,0,0,0]],
        'k': [[1,0,0,0,0],[1,0,0,1,0],[1,1,1,0,0],[1,0,0,1,0],[1,0,0,0,1],[0,0,0,0,0],[0,0,0,0,0]],
        'p': [[0,0,0,0,0],[1,1,1,1,0],[1,0,0,0,1],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[0,0,0,0,0]],
        'f': [[0,0,1,1,0],[0,1,0,0,0],[1,1,1,1,0],[0,1,0,0,0],[0,1,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],
        'w': [[0,0,0,0,0],[1,0,0,0,1],[1,0,1,0,1],[1,1,0,1,1],[1,0,0,0,1],[0,0,0,0,0],[0,0,0,0,0]],
        'h': [[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,0,0,0,0],[0,0,0,0,0]],
        'v': [[0,0,0,0,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,0,0,0]],
        'y': [[0,0,0,0,0],[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[1,0,0,0,0],[0,0,0,0,0]],
        'b': [[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,1],[1,1,1,1,0],[0,0,0,0,0],[0,0,0,0,0]],
        'x': [[0,0,0,0,0],[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0],[0,1,0,1,0],[1,0,0,0,1],[0,0,0,0,0]],
        'z': [[0,0,0,0,0],[1,1,1,1,1],[0,0,0,1,0],[0,0,1,0,0],[1,1,1,1,1],[0,0,0,0,0],[0,0,0,0,0]],
        'q': [[0,0,0,0,0],[0,1,1,0,0],[1,0,0,1,0],[0,1,1,1,0],[0,0,0,1,0],[0,0,0,0,0],[0,0,0,0,0]],
        'j': [[0,0,0,1,0],[0,0,0,0,0],[0,0,0,1,0],[0,0,0,1,0],[1,0,0,1,0],[0,1,1,0,0],[0,0,0,0,0]],
        'M': [[1,0,0,0,1],[1,1,0,1,1],[1,0,1,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,0,0,0,0],[0,0,0,0,0]],
        'N': [[1,0,0,0,1],[1,1,0,0,1],[1,0,1,0,1],[1,0,0,1,1],[1,0,0,0,1],[0,0,0,0,0],[0,0,0,0,0]],
        'O': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0],[0,0,0,0,0],[0,0,0,0,0]],
    }

    cx = x0
    for ch in text:
        bitmap = FONT.get(ch)
        if bitmap is None:
            cx += (char_w + 1) * scale
            continue
        for row_idx, row in enumerate(bitmap):
            for col_idx, bit in enumerate(row):
                if bit:
                    for dy in range(scale):
                        for dx in range(scale):
                            px = cx + col_idx * scale + dx
                            py = y0 + row_idx * scale + dy
                            if 0 <= py < HEIGHT and 0 <= px < WIDTH:
                                pixels[py][px] = color
        cx += (char_w + 1) * scale


# ── Compose cover ─────────────────────────────────────────────────────────────

def make_cover():
    # Initialize canvas with indigo gradient background
    pixels = []
    for y in range(HEIGHT):
        row = []
        t = y / HEIGHT
        base_color = lerp_color(INDIGO, INDIGO_DARK, t * 0.6)
        for x in range(WIDTH):
            tx = x / WIDTH
            c = lerp_color(base_color, INDIGO_DARK, tx * 0.3)
            row.append(c)
        pixels.append(row)

    # Subtle diagonal stripe texture (very light, creates depth)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if (x + y) % 80 < 2:
                pixels[y][x] = blend(pixels[y][x], WHITE, 0.04)

    # Large decorative circle (top-right, semi-transparent)
    cx1, cy1, r1 = 1100, 80, 260
    for y in range(max(0, cy1 - r1), min(HEIGHT, cy1 + r1)):
        for x in range(max(0, cx1 - r1), min(WIDTH, cx1 + r1)):
            d = math.sqrt((x - cx1) ** 2 + (y - cy1) ** 2)
            if r1 - 18 <= d <= r1:
                pixels[y][x] = blend(pixels[y][x], WHITE, 0.10)

    # Smaller decorative circle (bottom-left)
    cx2, cy2, r2 = 140, 560, 140
    for y in range(max(0, cy2 - r2), min(HEIGHT, cy2 + r2)):
        for x in range(max(0, cx2 - r2), min(WIDTH, cx2 + r2)):
            d = math.sqrt((x - cx2) ** 2 + (y - cy2) ** 2)
            if r2 - 14 <= d <= r2:
                pixels[y][x] = blend(pixels[y][x], WHITE, 0.08)

    # 2x2 tiles logo mark (top-left area, large decorative)
    tile_size = 72
    tile_gap = 14
    logo_x, logo_y = 80, 220
    tile_positions = [
        (logo_x, logo_y, 1.0),
        (logo_x + tile_size + tile_gap, logo_y, 0.35),
        (logo_x, logo_y + tile_size + tile_gap, 0.60),
        (logo_x + tile_size + tile_gap, logo_y + tile_size + tile_gap, 0.18),
    ]
    for tx, ty, alpha in tile_positions:
        for py in range(ty, ty + tile_size):
            for px in range(tx, tx + tile_size):
                if 0 <= py < HEIGHT and 0 <= px < WIDTH:
                    # Rounded corners (radius 14)
                    r = 14
                    if in_rounded_rect(px, py, tx, ty, tile_size, tile_size, r):
                        pixels[py][px] = blend(pixels[py][px], WHITE, alpha)

    # White card (center-right, main content area)
    card_x, card_y = 380, 100
    card_w, card_h = 820, 440
    card_r = 24
    for py in range(card_y, card_y + card_h):
        for px in range(card_x, card_x + card_w):
            if in_rounded_rect(px, py, card_x, card_y, card_w, card_h, card_r):
                pixels[py][px] = WHITE

    # Indigo accent bar (left edge of card)
    bar_w = 8
    for py in range(card_y + card_r, card_y + card_h - card_r):
        for px in range(card_x, card_x + bar_w):
            pixels[py][px] = INDIGO

    # Small 2x2 tile mark inside card (top-right of card)
    sm_size = 22
    sm_gap = 5
    sm_x = card_x + card_w - 100
    sm_y = card_y + 36
    sm_tiles = [
        (sm_x, sm_y, 1.0),
        (sm_x + sm_size + sm_gap, sm_y, 0.35),
        (sm_x, sm_y + sm_size + sm_gap, 0.60),
        (sm_x + sm_size + sm_gap, sm_y + sm_size + sm_gap, 0.18),
    ]
    for tx, ty, alpha in sm_tiles:
        for py in range(ty, ty + sm_size):
            for px in range(tx, tx + sm_size):
                if in_rounded_rect(px, py, tx, ty, sm_size, sm_size, 4):
                    pixels[py][px] = blend(WHITE, INDIGO, alpha)

    # Brand name "mini-on-ai" (large text on card)
    draw_text_pixels(pixels, "mini-on-ai", card_x + 50, card_y + 80, 8, INDIGO)

    # Tagline text
    draw_text_pixels(pixels, "AI-powered digital products", card_x + 50, card_y + 175, 4, (100, 102, 160))

    # Decorative horizontal rule
    rule_y = card_y + 230
    for px in range(card_x + 50, card_x + card_w - 50):
        pixels[rule_y][px] = (220, 221, 245)

    # Three feature bullets (row of chips)
    chip_data = [
        ("Prompt Packs", card_x + 50, card_y + 260),
        ("Checklists", card_x + 280, card_y + 260),
        ("Guides & Templates", card_x + 470, card_y + 260),
    ]
    chip_h = 40
    for label, cx, cy in chip_data:
        cw = len(label) * 13 + 28
        for py in range(cy, cy + chip_h):
            for px in range(cx, cx + cw):
                if in_rounded_rect(px, py, cx, cy, cw, chip_h, 20):
                    pixels[py][px] = LIGHT_BG
        draw_text_pixels(pixels, label, cx + 14, cy + 12, 2, INDIGO)

    # CTA button shape
    btn_x, btn_y = card_x + 50, card_y + 340
    btn_w, btn_h = 240, 52
    for py in range(btn_y, btn_y + btn_h):
        for px in range(btn_x, btn_x + btn_w):
            if in_rounded_rect(px, py, btn_x, btn_y, btn_w, btn_h, 26):
                pixels[py][px] = INDIGO
    draw_text_pixels(pixels, "Download now", btn_x + 28, btn_y + 16, 3, WHITE)

    # URL text at bottom of card
    draw_text_pixels(pixels, "mini-on-ai.com", card_x + 50, card_y + 415, 3, (160, 162, 200))

    return pixels


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"Generating cover ({WIDTH}x{HEIGHT})...")
    pixels = make_cover()
    png_data = _make_png(pixels)
    with open(OUTPUT, "wb") as f:
        f.write(png_data)
    size_kb = len(png_data) // 1024
    print(f"✅ Saved: {OUTPUT} ({size_kb} KB)")


if __name__ == "__main__":
    main()
