"""
trend_sources.py
Fetches real trend signals from public data sources.
Used by trend_scan.py to ground idea generation in actual demand.

Sources:
  - Google Trends (pytrends) — rising search queries for work/AI/business topics
"""

import time
import warnings

warnings.filterwarnings("ignore")

# Keyword groups targeting audiences who buy digital tools
TREND_KEYWORD_GROUPS = [
    ["AI tools", "AI assistant", "ChatGPT prompts"],
    ["freelance work", "side hustle", "online business"],
    ["remote work", "work from home", "productivity tools"],
    ["content creation", "social media marketing", "digital marketing"],
    ["small business", "entrepreneur", "startup"],
    ["email marketing", "copywriting", "sales funnel"],
]


def get_google_trends_rising(max_terms: int = 25) -> list[str]:
    """
    Fetch rising search queries from Google Trends for work/business topics.
    Returns a deduplicated list of rising query strings.
    Falls back to empty list on any error.
    """
    try:
        from pytrends.request import TrendReq
        pt = TrendReq(hl="en-US", tz=0, timeout=(10, 30))

        rising = []
        seen = set()

        for group in TREND_KEYWORD_GROUPS:
            try:
                pt.build_payload(group, timeframe="now 7-d", geo="US")
                related = pt.related_queries()
                for kw, data in related.items():
                    if data and data.get("rising") is not None and len(data["rising"]) > 0:
                        for _, row in data["rising"].head(3).iterrows():
                            query = row["query"].strip().lower()
                            # Skip noise: very short, purely numeric, or already seen
                            if len(query) > 8 and not query.isdigit() and query not in seen:
                                rising.append(query)
                                seen.add(query)
                time.sleep(0.5)  # be polite to the API
            except Exception:
                continue  # skip this group on error, try next

        return rising[:max_terms]

    except Exception:
        return []
