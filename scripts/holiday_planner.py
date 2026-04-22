#!/usr/bin/env python3
"""
holiday_planner.py v2
3-phase pipeline: ideation → targeted price search → weather enrichment.
Features: serendipity mode, real weather via wttr.in, comparison table.
"""

import json
import os
import re
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

DEFAULT_DEPARTURE = "25 rue Henri Chapron, Asnières-sur-Seine (92600)"


def _parse_attendees(attendees_str: str) -> tuple:
    """Returns (n_adults, n_children). Falls back to (2, 1) if unparseable."""
    s = (attendees_str or "").lower()
    adult_match = re.search(r'(\d+)\s*adulte', s)
    child_match = re.search(r'(\d+)\s*enfant', s)
    extra_adults = len(re.findall(r'grand-m[eè]re|mamie|papy|grand-p[eè]re|belle-m[eè]re|beau-p[eè]re', s))
    n_adults = int(adult_match.group(1)) if adult_match else 2
    n_adults += extra_adults
    n_children = int(child_match.group(1)) if child_match else 1
    return n_adults, n_children


def build_family_profile(attendees: str, departure: str) -> str:
    group = (attendees or "").strip() or "2 adults + 1 young child with a stroller"
    origin = (departure or "").strip() or DEFAULT_DEPARTURE
    has_stroller = any(w in group.lower() for w in ("stroller", "poussette", "enfant", "bébé", "bebe"))
    stroller_lines = (
        "- Need stroller-friendly accommodation (lift, ground floor, or stroller storage)\n"
        "- Prefer direct train; stroller must fit in the car/aisle without forced folding"
    ) if has_stroller else ""
    return f"""Family profile (always apply):
- Travelers: {group}
- Departure address: {origin}
- NO CAR — only public transport, walkable areas, or taxis
- Car acceptable ONLY if <1h driving (e.g. airport to hotel by taxi)
{stroller_lines}
- Prefer direct train or short flight; no connections when possible
- Door-to-door = home → RER/Metro to station/airport + travel + transfer at destination + walk/taxi to accommodation
- From Asnières: ~20min to Saint-Lazare, ~35min to Gare du Nord/Est, ~45min to CDG by RER B
- A 2h TGV = ~3h–3h30 door-to-door. A 1h flight = ~4h–4h30 door-to-door. A 2h flight = ~5h–5h30 door-to-door.
- REJECT any proposal whose realistic door-to-door time exceeds the journey_time constraint."""


TRIP_TYPE_RULES = """
TRIP TYPE RULES (mandatory):
- If trip_type contains "repos", "relax", "détente", "farniente", "calme", "repose", "se reposer", "lazy": propose ZERO hiking, randonnée, or trekking. Think beach/pool lounging, spa, slow village strolls, seaside promenade.
- Do NOT propose randonnée, hiking, or trekking unless the user explicitly asks for it.
- "Nature" alone ≠ randonnée. A lakeside village, a beach park, a château garden all count as nature without hiking.
- If trip_type says "zéro marche" or "zéro randonnée": treat as full relax, avoid any walking-heavy activities.
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
    "restaurants": [
      {"name": "Restaurant name", "distinction": "Bib Gourmand / Étoile / Assiette Michelin / Recommandé", "price_range": "~35€/pers", "specialty": "Cuisine type or signature dish", "michelin_url": "https://guide.michelin.com/fr/..."}
    ],
    "booking_links": [
      {"label": "🚄 Réserver le train", "url": "https://..."},
      {"label": "🏨 Chercher hôtels", "url": "https://..."},
      {"label": "🏠 Chercher Airbnb", "url": "https://..."}
    ]
  }
]
"""

def build_url_formats(n_adults: int, n_children: int) -> str:
    child_age = 2
    return f"""URL formats to pre-fill (use exact dates and destinations):
- SNCF Connect: https://www.sncf-connect.com/app/trips/search?wishOriginLabel=Paris&wishDestinationLabel={{DEST}}&travelDate={{YYYY-MM-DD}}
- Skyscanner FR: https://www.skyscanner.fr/transport/vols/{{FROM_IATA}}/{{TO_IATA}}/{{YYMMDD}}/{{YYMMDD}}/?adults={n_adults}&children={n_children}
- Booking.com FR: https://www.booking.com/searchresults.fr.html?ss={{DEST_ENCODED}}&checkin={{YYYY-MM-DD}}&checkout={{YYYY-MM-DD}}&group_adults={n_adults}&group_children={n_children}&age={child_age}
- Airbnb FR: https://www.airbnb.fr/s/{{DEST_SLUG}}/homes?checkin={{YYYY-MM-DD}}&checkout={{YYYY-MM-DD}}&adults={n_adults}&children={n_children}
- Kayak FR: https://www.kayak.fr/vols/{{FROM_IATA}}-{{TO_IATA}}/{{YYYY-MM-DD}}/{{YYYY-MM-DD}}/{n_adults}adultes/enfants-{child_age}
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
        with urllib.request.urlopen(req, timeout=10) as r:  # nosec B310 -- URL constructed from hardcoded https:// base
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
    family_profile = build_family_profile(constraints.get("attendees", ""), constraints.get("departure", ""))
    lines = []
    for key in ("dates", "budget", "attendees", "destination", "trip_type", "journey_time", "accommodation", "nights", "extras"):
        val = constraints.get(key, "").strip()
        if val:
            lines.append(f"- {key}: {val}")
    constraints_block = "\n".join(lines) or "Pas de contraintes spécifiques."

    prompt = f"""You are a family travel expert for French families.
{family_profile}
{TRIP_TYPE_RULES}

Given these travel constraints, brainstorm 5 distinct candidate destinations.
Return ONLY a valid JSON array, no text before or after:

[
  {{
    "destination": "City, Country",
    "city_en": "CityInEnglish",
    "transport": "train OR flight",
    "duration_note": "DOOR-TO-DOOR time (include home→station + travel + arrival transfer). e.g. ~3h30 door-to-door (2h TGV + 1h30 transfers)",
    "why_short": "one sentence why it fits the constraints"
  }}
]

Rules:
- All 5 must be genuinely different (different countries or regions, mix of transport modes)
- duration_note MUST be door-to-door, not just travel time — add ~20min for home→station and ~15-30min at destination
- Respect the journey_time constraint strictly using door-to-door time
- All must be accessible without a car

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
    attendees = constraints.get("attendees", "2 adultes + 1 enfant")
    journey_time = constraints.get("journey_time", "non précisé")
    gastronomy = constraints.get("gastronomy", "").strip()
    n_adults, n_children = _parse_attendees(attendees)
    n_total = n_adults + n_children

    family_profile = build_family_profile(attendees, constraints.get("departure", ""))
    url_formats = build_url_formats(n_adults, n_children)

    gastronomy_block = ""
    if gastronomy:
        gastronomy_block = f"""
GASTRONOMY:
The traveler is a food enthusiast who consults the Michelin Guide. Budget per meal: {gastronomy}.
- Search: "guide michelin [destination] bib gourmand" or "meilleures tables [destination] michelin"
- Include 2-3 real restaurant picks in the `restaurants` field: Bib Gourmand, Assiette Michelin, or highly recommended non-starred tables
- Destinations with a strong gastronomic scene should be preferred when equal on other criteria
- michelin_url should point to guide.michelin.com if the restaurant is listed there
"""

    candidates_list = "\n".join(
        f"{i+1}. {c.get('destination')} — {c.get('transport')} — {c.get('duration_note')} — {c.get('why_short')}"
        for i, c in enumerate(candidates)
    )

    return f"""You are a family travel price researcher.
{family_profile}
{TRIP_TYPE_RULES}{gastronomy_block}

I have these {len(candidates)} candidate destinations.
Dates: {dates}
Budget total: {budget}
Nights: {nights}
Group: {attendees} ({n_total} people total)
Accommodation preference: {accommodation}
Max journey time: {journey_time}

Candidates:
{candidates_list}

Your job:
1. For each candidate, search for REAL prices:
   - "[transport mode] Paris [destination] [dates] prix" (SNCF for trains, Skyscanner for flights)
   - "hôtel [destination] [dates] famille booking.com prix"
   {"- 'guide michelin [destination] bib gourmand' for restaurant picks" if gastronomy else ""}
   Use the EXACT dates in your searches.

2. After searching, select the 3 BEST proposals (budget fit + weather + accessibility + trip_type match{" + gastronomic quality" if gastronomy else ""}).

3. Return ONLY a valid JSON array of exactly 3 proposals:
{PROPOSAL_JSON_SCHEMA}

{url_formats}

PRICING RULES (critical):
- total_transport_eur = price per person × {n_total} people (or sum of actual per-seat prices found)
- total_accommodation_eur must fit ALL {n_total} people — check room capacity, price may be higher than standard
- price_per_person_eur × {n_total} must equal total_transport_eur
- total_estimate_eur = total_transport_eur + total_accommodation_eur (+ any mandatory taxi/transfer)

JOURNEY TIME RULES (critical):
- journey_time_note MUST show door-to-door breakdown: e.g. "~3h15 door-to-door (20min home→Gare du Nord + 2h TGV + 15min taxi)"
- If realistic door-to-door exceeds the max journey time constraint ({journey_time}), DROP that destination
- Do not confuse travel time with door-to-door time

Other rules:
- Note if prices are higher due to school holidays or peak season
- Stroller note must be specific to the destination
- All booking URLs must have dates pre-filled
- If no gastronomy was requested, leave `restaurants` as an empty array []"""


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
    attendees = constraints.get("attendees", "2 adultes + 1 enfant")
    journey_time = constraints.get("journey_time", "non précisé")
    gastronomy = constraints.get("gastronomy", "").strip()
    n_adults, n_children = _parse_attendees(attendees)

    family_profile = build_family_profile(attendees, constraints.get("departure", ""))
    url_formats = build_url_formats(n_adults, n_children)
    gastronomy_line = f"\n- Gastronomie: {gastronomy} — chercher tables Michelin Bib Gourmand ou recommandées" if gastronomy else ""

    prompt = f"""You are a family travel deal hunter. SERENDIPITY MODE — no destination specified!
{family_profile}
{TRIP_TYPE_RULES}

The traveler wants to be surprised. Find them unexpected, great-value destinations!

Trip details:
- Dates: {dates}
- Budget: {budget}
- Nights: {nights}
- Trip type: {trip_type or "open to anything"}
- Max journey time: {journey_time}
- Group: {attendees}{gastronomy_line}

Use web_search to discover deals:
1. Search: "week-end famille pas cher depuis Paris {dates} train"
2. Search: "destination originale famille France {dates} pas cher"
3. Search: "vol pas cher Paris famille {dates} Skyscanner"
4. Search for hotel prices once you have candidates
{"5. Search: 'guide michelin [destination] bib gourmand' for each candidate" if gastronomy else ""}

Find 3-5 unexpected places the traveler never would have thought of — hidden gems, unusual destinations, great deals.
Then build 3 full proposals with real prices for the best ones.

Return ONLY a valid JSON array of exactly 3 proposals:
{PROPOSAL_JSON_SCHEMA}

{url_formats}

PRICING RULES: total_transport_eur and total_accommodation_eur must cover ALL {n_adults + n_children} people.
JOURNEY TIME RULES: journey_time_note must be door-to-door. Drop any destination exceeding {journey_time}.
{"GASTRONOMY: include 2-3 Michelin-listed or recommended restaurants in the `restaurants` field." if gastronomy else "If no gastronomy requested, leave `restaurants` as []."}"""

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
    attendees = constraints.get("attendees", "2 adultes + 1 enfant")
    n_adults, n_children = _parse_attendees(attendees)
    family_profile = build_family_profile(attendees, constraints.get("departure", ""))
    url_formats = build_url_formats(n_adults, n_children)

    lines = []
    labels = {
        "dates": "Dates", "budget": "Budget", "attendees": "Voyageurs",
        "destination": "Destination", "trip_type": "Ambiance",
        "journey_time": "Durée max", "accommodation": "Hébergement",
        "nights": "Nuits", "extras": "Extras",
    }
    for key, label in labels.items():
        val = constraints.get(key, "").strip()
        if val:
            lines.append(f"- {label}: {val}")
    block = "\n".join(lines) or "Pas de contraintes spécifiques."

    prompt = f"""You are an expert family travel planner for French families.
{family_profile}
{TRIP_TYPE_RULES}
{url_formats}

Travel constraints:
{block}

Generate exactly 3 distinct trip proposals. Return ONLY a valid JSON array:
{PROPOSAL_JSON_SCHEMA}

PRICING RULES: total_transport_eur and total_accommodation_eur must cover ALL {n_adults + n_children} people.
JOURNEY TIME RULES: journey_time_note must be door-to-door (include home→station + travel + arrival transfer).
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
