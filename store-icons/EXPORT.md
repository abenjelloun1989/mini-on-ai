# Store Icon Export Guide

## Required sizes (Chrome Web Store)

| Size  | Use                          |
|-------|------------------------------|
| 16px  | Browser toolbar icon         |
| 48px  | Extensions management page   |
| 128px | Chrome Web Store listing     |

## Source SVGs

| Extension    | SVG                                              | Background  |
|-------------|--------------------------------------------------|-------------|
| ClauseGuard  | `clauseguard/store-assets/clauseguard-128.svg`  | `#1e1b4b`   |
| InvoiceGuard | `invoiceguard/store-assets/invoiceguard-128.svg`| `#0d1a15`   |
| JobGuard     | `jobguard/store-assets/jobguard-128.svg`        | `#1c1503`   |

## Option A — Node.js + Sharp (recommended)

```bash
cd /Users/minion/Dev/mini-on-factory
npm install sharp   # one-time

node - <<'EOF'
import sharp from 'sharp';
import { readFileSync } from 'fs';
import { mkdirSync } from 'fs';

const icons = [
  { name: 'clauseguard',  src: 'clauseguard/store-assets/clauseguard-128.svg',  dest: 'clauseguard/icons' },
  { name: 'invoiceguard', src: 'invoiceguard/store-assets/invoiceguard-128.svg', dest: 'invoiceguard/icons' },
  { name: 'jobguard',     src: 'jobguard/store-assets/jobguard-128.svg',         dest: 'jobguard/icons' },
];
const sizes = [16, 48, 128];

for (const { name, src, dest } of icons) {
  mkdirSync(dest, { recursive: true });
  const svg = readFileSync(src);
  for (const size of sizes) {
    const out = `${dest}/icon-${size}.png`;
    await sharp(svg).resize(size, size).png().toFile(out);
    // Also write no-dash variant for Chrome compatibility
    await sharp(svg).resize(size, size).png().toFile(`${dest}/icon${size}.png`);
    console.log(`Wrote ${out}`);
  }
}
EOF
```

## Option B — Inkscape (free desktop app)

```bash
# For each extension:
inkscape clauseguard/store-assets/clauseguard-128.svg \
  --export-type=png --export-width=128 --export-filename=clauseguard/icons/icon-128.png
inkscape clauseguard/store-assets/clauseguard-128.svg \
  --export-type=png --export-width=48  --export-filename=clauseguard/icons/icon-48.png
inkscape clauseguard/store-assets/clauseguard-128.svg \
  --export-type=png --export-width=16  --export-filename=clauseguard/icons/icon-16.png

# Repeat for invoiceguard and jobguard
```

## After export — copy to both naming conventions

Chrome's manifest and the store both expect consistent filenames.
Run this after exporting:

```bash
for ext in clauseguard invoiceguard jobguard; do
  cp $ext/icons/icon-48.png  $ext/icons/icon48.png
  cp $ext/icons/icon-128.png $ext/icons/icon128.png
done
```

## CWS submission checklist

- [ ] PNG format (not JPEG, not SVG)
- [ ] Solid background (no transparency on 128px — CWS rejects transparent icons)
- [ ] No text at 16px or 48px
- [ ] No screenshots or UI elements in the icon
- [ ] All three sizes supplied per extension
- [ ] 16px: fine detail is lost — all three icons render readably at 16px (viewBox scaling handles it)
