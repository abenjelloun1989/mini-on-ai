#!/usr/bin/env python3
"""
holiday_planner.py v2
3-phase pipeline: ideation → targeted price search → weather enrichment.
Features: serendipity mode, real weather via wttr.in, comparison table.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

import anthropic
from lib.utils import read_json, write_json, log, timestamp, extract_json, log_token_usage, ROOT
from lib.claude_cli import claude_call

RESEARCH_MODEL = "claude-sonnet-4-6"
HAIKU_MODEL = "claude-haiku-4-5-20251001"

# French school holidays 2025-2026 (source: education.gouv.fr)
FRENCH_SCHOOL_HOLIDAYS_2026 = [
    ("Toussaint 2025",          date(2025, 10, 18), date(2025, 11,  3), "Zones A, B, C"),
    ("Noël 2025-2026",          date(2025, 12, 20), date(2026,  1,  5), "Zones A, B, C"),
    ("Hiver 2026 — Zone A",     date(2026,  2,  7), date(2026,  2, 23), "Zone A"),
    ("Hiver 2026 — Zone B",     date(2026,  2, 14), date(2026,  3,  2), "Zone B"),
    ("Hiver 2026 — Zone C",     date(2026,  2, 21), date(2026,  3,  9), "Zone C (Paris)"),
    ("Printemps 2026 — Zone A", date(2026,  4, 11), date(2026,  4, 27), "Zone A"),
    ("Printemps 2026 — Zone B", date(2026,  4, 18), date(2026,  5,  4), "Zone B"),
    ("Printemps 2026 — Zone C", date(2026,  4, 25), date(2026,  5, 11), "Zone C (Paris)"),
    ("Grandes vacances 2026",   date(2026,  7,  4), date(2026,  8, 31), "Zones A, B, C"),
]

FAMILY_PROFILE = """
Family profile (always apply):
- 2 adults + 1 young child with a stroller
- NO CAR — only public transport, walkable areas, or taxis
- Car acceptable ONLY if <1h driving (e.g. airport to hotel by taxi)
- Traveling from Paris, France
- Need stroller-friendly accommodation (lift, ground floor, or stroller storage)
- Prefer direct train or short flight; no connections when possible
- Door-to-door journey time = home→station/airport + travel + transfers + destination arrival
- A 2h flight = roughly 4-5h door-to-door
"""

PROPOSAL_JSON_SCHEMA = """
[
  {
    "title": "Catchy trip title",
    "destination": "City, Country",
    "emoji": "🏖️",
    "why": "2-3 sentences why this matches the constraints. Mention stroller accessibility.",
    "transport": {
      "description": "e.g. TGV Paris-Gare de Lyon → Lyon Part-Dieu direct",
      "type": "train",
      "duration": "2h05",
      "price_per_person_eur": 55,
      "total_transport_eur": 165,
      "search_url": "https://www.sncf-connect.com/...",
      "notes": "Direct, no connections. Stroller folds on the platform."
    },
    "accommodation": {
      "description": "e.g. Mercure Lyon Centre Beaux-Arts 4★",
      "type": "hotel",
      "price_per_night_eur": 130,
      "total_accommodation_eur": 390,
      "search_url": "https://www.booking.com/...",
      "notes": "Lift available, central location, 5min walk from station."
    },
    "total_estimate_eur": 555,
    "nights": 3,
    "journey_time_note": "~2h45 door-to-door from Paris",
    "weather_note": "will be updated",
    "stroller_note": "Specific info about stroller accessibility in this destination",
    "booking_links": [
      {"label": "🚄 Réserver le train", "url": "https://..."},
      {"label": "🏨 Chercher hôtels", "url": "https://..."},
      {"label": "🏠 Chercher Airbnb", "url": "https://..."}
    ]
  }
]
"""

URL_FORMATS = """
URL formats to pre-fill (use exact dates and destinations):
- SNCF Connect: https://www.sncf-connect.com/app/trips/search?wishOriginLabel=Paris&wishDestinationLabel={DEST}&travelDate={YYYY-MM-DD}
- Skyscanner FR: https://www.skyscanner.fr/transport/vols/{FROM_IATA}/{TO_IATA}/{YYMMDD}/{YYMMDD}/?adults=2&children=1
- Booking.com FR: https://www.booking.com/searchresults.fr.html?ss={DEST_ENCODED}&checkin={YYYY-MM-DD}&checkout={YYYY-MM-DD}&group_adults=2&group_children=1&age=2
- Airbnb FR: https://www.airbnb.fr/s/{DEST_SLUG}/homes?checkin={YYYY-MM-DD}&checkout={YYYY-MM-DD}&adults=2&children=1
- Kayak FR: https://www.kayak.fr/vols/{FROM_IATA}-{TO_IATA}/{YYYY-MM-DD}/{YYYY-MM-DD}/2adultes/enfants-2
"""


# ---------------------------------------------------------------------------
# School holiday check (runs in the bot before launching research)
# ---------------------------------------------------------------------------

def check_school_holidays(dates_str: str) -> list:
    """
    Return list of (label, zones) for holiday periods that might overlap.
    Uses keyword matching — intentionally broad to avoid false negatives.
    """
    dates_lower = dates_str.lower()

    # Month keywords → relevant holiday indices in FRENCH_SCHOOL_HOLIDAYS_2026
    month_to_indices = {
        "octobre": [0], "novembre": [0],
        "décembre": [1], "decembre": [1], "janvier": [1],
        "février": [2, 3, 4], "fevrier": [2, 3, 4], "mars": [2, 3, 4],
        "avril": [5, 6, 7], "mai": [5, 6, 7],
        "juillet": [8], "août": [8], "aout": [8],
    }

    seen = set()
    matches = []
    for kw, indices in month_to_indices.items():
        if kw in dates_lower:
            for i in indices:
                if i not in seen:
                    seen.add(i)
                    label, _, _, zones = FRENCH_SCHOOL_HOLIDAYS_2026[i]
                    matches.append((label, zones))
    return matches


# ---------------------------------------------------------------------------
# Real weather via wttr.in
# ---------------------------------------------------------------------------

def fetch_weather(city: str) -> str:
    """Fetch real weather forecast via wttr.in. Returns a short description."""
    try:
        city_name = city.split(",")[0].strip()
        encoded = urllib.parse.quote(city_name)
        url = f"https://wttr.in/{encoded}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "holiday-planner/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))

        weather_days = data.get("weather", [])
        if weather_days:
            temps = [int(w.get("avgtempC", 0)) for w in weather_days]
            avg_temp = sum(temps) // max(len(temps), 1)
            # Get description from midday forecast of first day
            hourly = weather_days[0].get("hourly", [])
            midday = hourly[len(hourly) // 2] if hourly else {}
            desc = midday.get("weatherDesc", [{}])[0].get("value", "")
            if desc:
                return f"~{avg_temp}°C, {desc}"
            return f"~{avg_temp}°C"

        current = data.get("current_condition", [{}])[0]
        temp = current.get("temp_C", "?")
        desc = current.get("weatherDesc", [{}])[0].get("value", "")
        return f"{temp}°C, {desc}" if desc else f"{temp}°C"

    except Exception as e:
        log("holiday", f"wttr.in failed for {city}: {e}")
        return ""


def _enrich_with_weather(proposals: list) -> list:
    """Replace weather_note with real forecast from wttr.in."""
    for p in proposals:
        city = p.get("destination", "")
        if city:
            weather = fetch_weather(city)
            if weather:
                p["weather_note"] = weather
    return proposals


# ---------------------------------------------------------------------------
# Phase 1: Ideation — 5 candidate destinations (fast, no web search)
# ---------------------------------------------------------------------------

def _phase1_ideation(client, constraints: dict) -> list:
    """
    Ask Claude Haiku to brainstorm 5 candidate destinations.
    Returns list of dicts: {destination, city_en, transport, duration_note, why_short}
    """
    lines = []
    for key in ("dates", "budget", "destination", "trip_type", "journey_time", "accommodation", "nights", "extras"):
        val = constraints.get(key, "").strip()
        if val:
            lines.append(f"- {key}: {val}")
    constraints_block = "\n".join(lines) or "Pas de contraintes spécifiques."

    prompt = f"""You are a family travel expert for French families.
{FAMILY_PROFILE}

Given these travel constraints, brainstorm 5 distinct candidate destinations.
Return ONLY a valid JSON array, no text before or after:

[
  {{
    "destination": "City, Country",
    "city_en": "CityInEnglish",
    "transport": "train OR flight",
    "duration_note": "e.g. 2h30 direct TGV from Paris",
    "why_short": "one sentence why it fits the constraints"
  }}
]

Rules:
- All 5 must be genuinely different (different countries or regions, mix of transport modes)
- Respect the journey time constraint strictly (door-to-door)
- All must be accessible by stroller without a car

Constraints:
{constraints_block}"""

    try:
        response = client.messages.create(
            model=HAIKU_MODEL,
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        log_token_usage("holiday-ideation", response.usage, HAIKU_MODEL)
        text = "".join(b.text for b in response.content if hasattr(b, "text"))
        candidates = extract_json(text, array=True)
        if candidates:
            log("holiday", f"Phase 1: {len(candidates)} candidates — {[c.get('destination','?') for c in candidates]}")
        return candidates or []
    except Exception as e:
        log("holiday", f"Phase 1 ideation failed: {e}")
        return []


# ---------------------------------------------------------------------------
# Phase 2: Targeted price search — enriches candidates, returns 3 proposals
# ---------------------------------------------------------------------------

def _build_price_search_prompt(candidates: list, constraints: dict) -> str:
    dates = constraints.get("dates", "dates non précisées")
    budget = constraints.get("budget", "non précisé")
    nights = constraints.get("nights", "?")
    accommodation = constraints.get("accommodation", "hôtel ou Airbnb")

    candidates_list = "\n".join(
        f"{i+1}. {c.get('destination')} — {c.get('transport')} — {c.get('duration_note')} — {c.get('why_short')}"
        for i, c in enumerate(candidates)
    )

    return f"""You are a family travel price researcher.
{FAMILY_PROFILE}

I have these {len(candidates)} candidate destinations for a trip from Paris.
Dates: {dates}
Budget total: {budget}
Nights: {nights}
Accommodation preference: {accommodation}

Candidates:
{candidates_list}

Your job:
1. For each candidate, search for REAL prices with these specific queries:
   - "[transport mode] Paris [destination] [dates] prix" (use SNCF for trains, Skyscanner for flights)
   - "hôtel [destination] [dates] famille booking.com prix"
   Use the EXACT dates from the constraints in your searches.

2. After searching, select the 3 BEST proposals for this family (budget fit + weather + accessibility).

3. Return ONLY a valid JSON array of exactly 3 proposals:
{PROPOSAL_JSON_SCHEMA}

{URL_FORMATS}

Rules:
- Prices must be realistic for the given dates (use prices you found in searches, not estimates)
- Always note if prices are higher due to school holidays or peak season
- Stroller note must be specific to the destination
- All booking URLs must have dates pre-filled"""


def _run_web_search_loop(client, prompt: str, max_uses: int = 12) -> str:
    """
    Run agentic web search via claude CLI (uses Pro subscription, not API credits).
    The CLI handles the tool-call loop internally — no need to manage iterations.
    `client` is kept as a parameter for API fallback compatibility but is not used here.
    """
    try:
        text, usage = claude_call(
            prompt,
            tools=["WebSearch"],
            timeout=300,  # 5 minutes max for web research
        )
        if usage:
            log("holiday", f"CLI web search usage: {usage}")
        return text
    except Exception as e:
        log("holiday", f"CLI web search failed: {e} — falling back to direct API")
        # Fallback: direct API without web search (knowledge-based)
        tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": max_uses}]
        messages = [{"role": "user", "content": prompt}]

        for iteration in range(15):
            response = client.messages.create(
                model=RESEARCH_MODEL,
                max_tokens=5000,
                tools=tools,
                messages=messages,
                betas=["web-search-2025-03-05"],
            )

            final_text = ""
            tool_uses = []
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text
                elif getattr(block, "type", "") == "tool_use":
                    tool_uses.append(block)

            if response.stop_reason == "end_turn" or not tool_uses:
                log_token_usage("holiday-research", response.usage, RESEARCH_MODEL)
                return final_text.strip()

            messages.append({"role": "assistant", "content": response.content})
            tool_results = [
                {"type": "tool_result", "tool_use_id": tu.id, "content": ""}
                for tu in tool_uses
            ]
            messages.append({"role": "user", "content": tool_results})
            time.sleep(0.5)

        return ""


def _phase2_price_search(client, candidates: list, constraints: dict) -> list:
    """Use web_search to find real prices for candidates. Returns 3 proposals."""
    prompt = _build_price_search_prompt(candidates, constraints)
    try:
        text = _run_web_search_loop(client, prompt, max_uses=12)
        if text:
            proposals = extract_json(text, array=True)
            if proposals:
                log("holiday", f"Phase 2: {len(proposals)} proposals via targeted price search")
                return proposals
    except Exception as e:
        log("holiday", f"Phase 2 price search failed: {e}")
    return []


# ---------------------------------------------------------------------------
# Serendipity mode — no destination, find deals via web search
# ---------------------------------------------------------------------------

def _serendipity_research(client, constraints: dict) -> list:
    """Search for unexpected deals when no destination is specified."""
    dates = constraints.get("dates", "prochaines vacances")
    budget = constraints.get("budget", "budget raisonnable")
    nights = constraints.get("nights", "quelques nuits")
    trip_type = constraints.get("trip_type", "")

    prompt = f"""You are a family travel deal hunter. SERENDIPITY MODE — no destination specified!
{FAMILY_PROFILE}

The traveler wants to be surprised. Find them unexpected, great-value destinations!

Trip details:
- Dates: {dates}
- Budget: {budget}
- Nights: {nights}
- Trip type: {trip_type or "open to anything"}

Use web_search to discover deals:
1. Search: "week-end famille pas cher depuis Paris {dates} train"
2. Search: "destination originale famille France {dates} pas cher"
3. Search: "vol pas cher Paris famille {dates} Skyscanner"
4. Search for hotel prices once you have candidates

Find 3-5 unexpected places the traveler never would have thought of — hidden gems, unusual destinations, great deals.
Then build 3 full proposals with real prices for the best ones.

Return ONLY a valid JSON array of exactly 3 proposals:
{PROPOSAL_JSON_SCHEMA}

{URL_FORMATS}"""

    try:
        text = _run_web_search_loop(client, prompt, max_uses=10)
        if text:
            proposals = extract_json(text, array=True)
            if proposals:
                log("holiday", f"Serendipity: {len(proposals)} proposals found")
                return proposals
    except Exception as e:
        log("holiday", f"Serendipity search failed: {e}")
    return []


# ---------------------------------------------------------------------------
# Fallback: knowledge-based (no web search)
# ---------------------------------------------------------------------------

def _fallback_research(client, constraints: dict) -> list:
    """Knowledge-based research without web search — last resort."""
    lines = []
    labels = {
        "dates": "Dates", "budget": "Budget", "destination": "Destination",
        "trip_type": "Type", "journey_time": "Durée max", "accommodation": "Hébergement",
        "nights": "Nuits", "extras": "Extras",
    }
    for key, label in labels.items():
        val = constraints.get(key, "").strip()
        if val:
            lines.append(f"- {label}: {val}")
    block = "\n".join(lines) or "Pas de contraintes spécifiques."

    prompt = f"""You are an expert family travel planner for French families.
{FAMILY_PROFILE}
{URL_FORMATS}

Travel constraints:
{block}

Generate exactly 3 distinct trip proposals. Return ONLY a valid JSON array:
{PROPOSAL_JSON_SCHEMA}

Make prices realistic for the given period. All 3 proposals must be different destinations."""

    try:
        # Use CLI (Pro subscription) for Sonnet call
        text, usage = claude_call(prompt, timeout=120)
        if usage:
            log("holiday", f"CLI fallback usage: {usage}")
        proposals = extract_json(text, array=True)
        if proposals:
            log("holiday", f"Fallback: {len(proposals)} proposals via knowledge")
        return proposals or []
    except Exception as e:
        log("holiday", f"CLI fallback failed: {e} — trying direct API")
        try:
            response = client.messages.create(
                model=RESEARCH_MODEL,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}],
            )
            log_token_usage("holiday-fallback", response.usage, RESEARCH_MODEL)
            text = "".join(b.text for b in response.content if hasattr(b, "text"))
            proposals = extract_json(text, array=True)
            if proposals:
                log("holiday", f"Fallback: {len(proposals)} proposals via knowledge (API)")
            return proposals or []
        except Exception as e2:
            log("holiday", f"Fallback research failed entirely: {e2}")
            return []


# ---------------------------------------------------------------------------
# Main research pipeline
# ---------------------------------------------------------------------------

def research_trips(constraints: dict) -> list:
    """
    3-phase pipeline:
    1. Ideation (fast, no tools)
    2. Targeted price search (web_search)
    3. Weather enrichment (wttr.in)
    Serendipity mode when no destination specified.
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    dest = constraints.get("destination", "").lower().strip()
    serendipity = dest in ("", "ouvert", "open", "pas de préférence", "surprise",
                           "n'importe où", "aucune", "aucune idée", "sans préférence")

    if serendipity:
        log("holiday", "🎲 Serendipity mode — searching for unexpected deals")
        proposals = _serendipity_research(client, constraints)
    else:
        # Phase 1: fast ideation
        candidates = _phase1_ideation(client, constraints)

        if candidates:
            # Phase 2: targeted price searches
            proposals = _phase2_price_search(client, candidates, constraints)
        else:
            log("holiday", "Phase 1 returned no candidates — using fallback")
            proposals = []

        if not proposals:
            log("holiday", "Phase 2 returned no proposals — using fallback")
            proposals = _fallback_research(client, constraints)

    if not proposals:
        return []

    # Phase 3: enrich with real weather
    proposals = _enrich_with_weather(proposals)

    return proposals


# ---------------------------------------------------------------------------
# Telegram output
# ---------------------------------------------------------------------------

def send_results(proposals: list) -> None:
    """Send comparison table then first proposal."""
    from telegram_notify import send_holiday_proposal, send_comparison_table, send_telegram

    total = len(proposals)

    # Comparison table first
    try:
        send_comparison_table(proposals)
        time.sleep(1)
    except Exception as e:
        log("holiday", f"Comparison table send failed: {e}")

    # Then first proposal
    try:
        send_holiday_proposal(proposals[0], 1, total)
    except Exception as e:
        log("holiday", f"Failed to send first proposal: {e}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    state = read_json("data/holiday-state.json")

    if state.get("status") != "researching":
        log("holiday", f"Unexpected state: {state.get('status')} — expected 'researching'")
        sys.exit(1)

    constraints = state.get("constraints", {})
    if not constraints:
        log("holiday", "No constraints found in state")
        sys.exit(1)

    log("holiday", f"Researching trips — constraints: {list(constraints.keys())}")

    try:
        proposals = research_trips(constraints)
    except Exception as e:
        log("holiday", f"Research failed: {e}")
        from telegram_notify import send_telegram
        send_telegram(f"❌ La recherche de voyage a échoué: {e}\n\nRéessayez avec /holidays")
        state["status"] = "idle"
        write_json("data/holiday-state.json", state)
        sys.exit(1)

    if not proposals:
        from telegram_notify import send_telegram
        send_telegram("❌ Je n'ai pas pu générer de propositions. Réessayez avec /holidays")
        state["status"] = "idle"
        write_json("data/holiday-state.json", state)
        sys.exit(1)

    state["proposals"] = proposals
    state["status"] = "done"
    state["current_proposal_index"] = 0
    state["completed_at"] = timestamp()
    write_json("data/holiday-state.json", state)

    send_results(proposals)
    log("holiday", f"Done — {len(proposals)} proposals sent to Telegram")


if __name__ == "__main__":
    main()
