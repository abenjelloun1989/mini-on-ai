"""
gumroad_stats.py — Fetch sales and download data from Gumroad API.

Usage:
    python3 scripts/gumroad_stats.py [--days N]

Output:
    Telegram-formatted HTML summary of sales, revenue, top products, and referrers.
    Prints to stdout. Used by the /stats Telegram command.
"""

import argparse
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

# Project root
ROOT = Path(__file__).parent.parent.resolve()
load_dotenv(ROOT / ".env")

GUMROAD_API = "https://api.gumroad.com/v2"


def _token() -> str:
    t = os.getenv("GUMROAD_API_TOKEN", "")
    if not t:
        raise RuntimeError("GUMROAD_API_TOKEN not set in .env")
    return t


def fetch_all_sales(days: int = 30) -> list:
    """Fetch all sales from Gumroad for the last N days, handling pagination."""
    token = _token()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    sales = []
    page_key = None

    while True:
        params = {}
        if page_key:
            params["page_key"] = page_key

        try:
            resp = requests.get(
                f"{GUMROAD_API}/sales",
                headers={"Authorization": f"Bearer {token}"},
                params=params,
                timeout=15,
            )
        except requests.RequestException as e:
            print(f"❌ Network error fetching sales: {e}", file=sys.stderr)
            break

        if resp.status_code == 401:
            print("❌ Gumroad API: unauthorized. Check GUMROAD_API_TOKEN.", file=sys.stderr)
            break
        if resp.status_code != 200:
            print(f"❌ Gumroad API error {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
            break

        data = resp.json()
        page_sales = data.get("sales", [])

        if not page_sales:
            break

        # Filter to the date window; stop paginating once we're past the cutoff
        reached_cutoff = False
        for sale in page_sales:
            created_raw = sale.get("created_at", "")
            try:
                # Gumroad returns ISO 8601: "2026-04-01T12:34:56Z"
                created = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                created = datetime.now(timezone.utc)

            if created >= cutoff:
                sales.append(sale)
            else:
                reached_cutoff = True

        next_page_key = data.get("next_page_key")
        if reached_cutoff or not next_page_key:
            break
        page_key = next_page_key

    return sales


def summarize(sales: list, days: int) -> str:
    """Format a Telegram-ready HTML summary of sales data."""
    paid = [s for s in sales if s.get("price", 0) > 0]
    free = [s for s in sales if s.get("price", 0) == 0]

    total_revenue_cents = sum(s.get("price", 0) for s in paid)
    total_revenue = total_revenue_cents / 100

    # Top products by revenue
    product_revenue: dict = defaultdict(int)
    product_count: dict = defaultdict(int)
    for s in paid:
        name = s.get("product_name", "Unknown")
        product_revenue[name] += s.get("price", 0)
        product_count[name] += 1

    top_products = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:5]

    # Top free downloads
    free_downloads: dict = defaultdict(int)
    for s in free:
        name = s.get("product_name", "Unknown")
        free_downloads[name] += 1
    top_free = sorted(free_downloads.items(), key=lambda x: x[1], reverse=True)[:3]

    # Referrer breakdown (paid sales only)
    referrers: dict = defaultdict(int)
    for s in paid:
        ref = s.get("referrer") or "direct"
        # Simplify referrer to domain or UTM source
        if "utm_source=" in ref:
            try:
                utm = [p for p in ref.split("&") if "utm_source=" in p][0]
                ref = utm.split("=")[1]
            except IndexError:
                pass
        elif ref.startswith("http"):
            try:
                from urllib.parse import urlparse
                ref = urlparse(ref).netloc or ref
            except Exception:
                pass
        referrers[ref] += 1
    top_refs = sorted(referrers.items(), key=lambda x: x[1], reverse=True)[:5]

    # Format output
    lines = [f"📊 <b>Sales — last {days} days</b>\n"]

    lines.append(f"Revenue: <b>${total_revenue:.2f}</b>")
    lines.append(f"Paid sales: <b>{len(paid)}</b>  |  Free downloads: <b>{len(free)}</b>")

    lines.append("\n<b>Top products (paid):</b>")
    if top_products:
        for name, rev in top_products:
            count = product_count[name]
            lines.append(f"  • {name[:45]} — ${rev / 100:.2f} ({count}×)")
    else:
        lines.append("  — none yet")

    if top_free:
        lines.append("\n<b>Top free downloads:</b>")
        for name, count in top_free:
            lines.append(f"  • {name[:45]} — {count}×")

    lines.append("\n<b>Referrers (paid):</b>")
    if top_refs:
        for ref, count in top_refs:
            lines.append(f"  • {ref[:40]} — {count}×")
    else:
        lines.append("  — none yet")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Fetch Gumroad sales stats")
    parser.add_argument("--days", type=int, default=30, help="Number of days to look back (default: 30)")
    args = parser.parse_args()

    try:
        sales = fetch_all_sales(days=args.days)
        print(summarize(sales, days=args.days))
    except RuntimeError as e:
        print(f"❌ {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
