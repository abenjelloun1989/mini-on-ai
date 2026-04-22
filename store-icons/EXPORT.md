# Store Icon Export Guide

## Required sizes (Chrome Web Store)

| Size  | Use                          |
|-------|------------------------------|
| 16px  | Browser toolbar icon         |
| 48px  | Extensions management page   |
| 128px | Chrome Web Store listing     |

## Source SVGs

Two SVGs per extension — **use the right one per size**:

| Extension    | 16px source                                    | 48/128px source                                |
|-------------|------------------------------------------------|------------------------------------------------|
| ClauseGuard  | `clauseguard/store-assets/clauseguard-16.svg`  | `clauseguard/store-assets/clauseguard-128.svg`  |
| InvoiceGuard | `invoiceguard/store-assets/invoiceguard-16.svg`| `invoiceguard/store-assets/invoiceguard-128.svg`|
| JobGuard     | `jobguard/store-assets/jobguard-16.svg`        | `jobguard/store-assets/jobguard-128.svg`        |

### Why two sources?

At 16px (Chrome toolbar), fine details disappear. The `*-16.svg` files use a pure solid-fill silhouette with no strokes or overlay badges. The `*-128.svg` files include the overlay details (clock, magnifier) that read clearly at larger sizes.

| Extension    | 16px approach                                 |
|-------------|-----------------------------------------------|
| ClauseGuard  | White filled shield + indigo checkmark cutout |
| InvoiceGuard | White filled receipt + tiny clock badge       |
| JobGuard     | White filled briefcase, no magnifier          |

## Option A — Node.js + Sharp (recommended)

```bash
cd /Users/minion/Dev/mini-on-factory
npm install --prefix /tmp/sharp-tmp sharp   # one-time install

node --input-type=module <<'EOF'
import { createRequire } from 'module';
const require = createRequire('/tmp/sharp-tmp/');
const sharp = require('sharp');
import { readFileSync, mkdirSync } from 'fs';

const icons = [
  { name: 'clauseguard',  src16: 'clauseguard/store-assets/clauseguard-16.svg',   src128: 'clauseguard/store-assets/clauseguard-128.svg',   dest: 'clauseguard/icons' },
  { name: 'invoiceguard', src16: 'invoiceguard/store-assets/invoiceguard-16.svg',  src128: 'invoiceguard/store-assets/invoiceguard-128.svg',  dest: 'invoiceguard/icons' },
  { name: 'jobguard',     src16: 'jobguard/store-assets/jobguard-16.svg',          src128: 'jobguard/store-assets/jobguard-128.svg',          dest: 'jobguard/icons' },
];

for (const { name, src16, src128, dest } of icons) {
  mkdirSync(dest, { recursive: true });
  // 16px — dedicated simplified icon
  await sharp(readFileSync(src16)).resize(16, 16).png().toFile(`${dest}/icon-16.png`);
  await sharp(readFileSync(src16)).resize(16, 16).png().toFile(`${dest}/icon16.png`);
  // 48px and 128px — full detail icon
  await sharp(readFileSync(src128)).resize(48, 48).png().toFile(`${dest}/icon-48.png`);
  await sharp(readFileSync(src128)).resize(48, 48).png().toFile(`${dest}/icon48.png`);
  await sharp(readFileSync(src128)).resize(128, 128).png().toFile(`${dest}/icon-128.png`);
  await sharp(readFileSync(src128)).resize(128, 128).png().toFile(`${dest}/icon128.png`);
  console.log(`✓ ${name}`);
}
console.log('Done!');
EOF
```

## Option B — Inkscape (free desktop app)

```bash
# 16px — use dedicated simplified icons
inkscape clauseguard/store-assets/clauseguard-16.svg   --export-type=png --export-width=16  --export-filename=clauseguard/icons/icon16.png
inkscape invoiceguard/store-assets/invoiceguard-16.svg --export-type=png --export-width=16  --export-filename=invoiceguard/icons/icon16.png
inkscape jobguard/store-assets/jobguard-16.svg         --export-type=png --export-width=16  --export-filename=jobguard/icons/icon16.png

# 48px and 128px — use full detail icons
inkscape clauseguard/store-assets/clauseguard-128.svg   --export-type=png --export-width=48  --export-filename=clauseguard/icons/icon48.png
inkscape clauseguard/store-assets/clauseguard-128.svg   --export-type=png --export-width=128 --export-filename=clauseguard/icons/icon128.png
inkscape invoiceguard/store-assets/invoiceguard-128.svg --export-type=png --export-width=48  --export-filename=invoiceguard/icons/icon48.png
inkscape invoiceguard/store-assets/invoiceguard-128.svg --export-type=png --export-width=128 --export-filename=invoiceguard/icons/icon128.png
inkscape jobguard/store-assets/jobguard-128.svg         --export-type=png --export-width=48  --export-filename=jobguard/icons/icon48.png
inkscape jobguard/store-assets/jobguard-128.svg         --export-type=png --export-width=128 --export-filename=jobguard/icons/icon128.png
```

## CWS submission checklist

- [ ] PNG format (not JPEG, not SVG)
- [ ] Solid background (no transparency on 128px — CWS rejects transparent icons)
- [ ] No text at 16px or 48px
- [ ] No screenshots or UI elements in the icon
- [ ] All three sizes supplied per extension
- [ ] 16px and 48px/128px generated from their respective source files
