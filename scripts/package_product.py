#!/usr/bin/env python3
"""
package_product.py
Bundles product assets into a downloadable zip file.

Usage: python3 scripts/package_product.py [--id product-id]
"""

import argparse
import json
import shutil
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

from lib.utils import write_file, ROOT, log


def package_product(product_id_arg: str = None) -> dict:
    if product_id_arg:
        pid = product_id_arg
        meta_path = ROOT / f"products/{pid}/meta.json"
        with open(meta_path) as f:
            meta = json.load(f)
    else:
        # Find most recently generated unpackaged product
        products_dir = ROOT / "products"
        if not products_dir.exists():
            raise RuntimeError("No products directory found")

        candidates = []
        for d in products_dir.iterdir():
            meta_path = d / "meta.json"
            if meta_path.exists():
                with open(meta_path) as f:
                    m = json.load(f)
                if m.get("status") == "generated":
                    candidates.append((d.name, m))

        if not candidates:
            raise RuntimeError("No generated products found. Run generate_product first.")

        candidates.sort(key=lambda x: x[1].get("created_at", ""))
        pid, meta = candidates[-1]

    log("package-product", f"Packaging: {meta['title']} ({pid})")

    assets_dir = ROOT / f"products/{pid}/assets"
    zip_path = ROOT / f"products/{pid}/package.zip"

    # Build zip
    folder_name = "".join(c for c in meta["title"] if c.isalnum() or c in " -_").strip()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for asset_file in assets_dir.rglob("*"):
            if asset_file.is_file():
                arc_name = f"{folder_name}/{asset_file.relative_to(assets_dir)}"
                zf.write(asset_file, arc_name)

    size_kb = round(zip_path.stat().st_size / 1024, 1)
    log("package-product", f"Created package.zip ({size_kb}KB)")

    # Copy zip into site/ so GitHub Pages can serve it
    site_zip_dir = ROOT / f"site/products/{pid}"
    site_zip_dir.mkdir(parents=True, exist_ok=True)
    site_zip_path = site_zip_dir / "package.zip"
    shutil.copy2(zip_path, site_zip_path)
    log("package-product", f"Copied to site/products/{pid}/package.zip")

    # Update meta — package_path is now relative to site root
    meta["status"] = "packaged"
    meta["package_path"] = f"products/{pid}/package.zip"
    write_file(f"products/{pid}/meta.json", json.dumps(meta, indent=2, ensure_ascii=False) + "\n")

    return meta


def main():
    parser = argparse.ArgumentParser(description="Package product assets into zip")
    parser.add_argument("--id", default=None, help="Product ID to package")
    args = parser.parse_args()
    package_product(args.id)


if __name__ == "__main__":
    main()
