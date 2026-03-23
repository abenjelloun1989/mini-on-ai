#!/usr/bin/env python3
"""
holiday_planner.py
Research trip options based on collected constraints and send 3 proposals to Telegram.

Usage:
  python3 scripts/holiday_planner.py   # reads constraints from data/holiday-state.json
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

import anthropic
from lib.utils import read_json, write_json, log, timestamp, extract_json, log_token_usage, ROOT

RESEARCH_MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are an expert family travel planner specializing in European trips for French families.

Family profile (fixed — always apply):
- 2 adults + 1 young child with a stroller
- NO CAR — must rely entirely on public transport, walkable areas, or taxis
- Car is acceptable ONLY if the driving time is less than 1 hour (e.g. airport to hotel)
- Traveling from France (assume Paris unless stated otherwise)
- Need stroller-friendly accommodation (lift, ground floor, or stroller storage)
- Prefer destinations reachable by direct train or short flight

Journey time rule (strict):
- Respect the traveler's stated max journey time
- Count door-to-door: home → station/airport + travel time + transfers + destination arrival
- A 2h flight = roughly 4-5h door-to-door when you include travel to/from airports
- Direct trains are preferred over connections (stroller + child makes connections harder)

Your job: suggest 3 distinct, realistic trip proposals based on the given constraints.
Each proposal must be genuinely different (different destination, or different vibe/type).

For each proposal you MUST:
1. Suggest a specific destination (not vague — e.g. "Barcelone" not "somewhere in Spain")
2. Estimate realistic prices for the travel period
3. Generate real pre-filled booking search URLs the traveler can click to see live prices
4. Explain stroller logistics (is the destination walkable? is the hotel accessible?)
5. State the realistic door-to-door journey time

URL formats to use:
- SNCF Connect: https://www.sncf-connect.com/app/trips/search?wishOriginLabel=Paris&wishDestinationLabel={DEST}&travelDate={YYYY-MM-DD}
- Skyscanner FR: https://www.skyscanner.fr/transport/vols/{FROM_IATA}/{TO_IATA}/{YYMMDD}/{YYMMDD}/?adults=2&children=1&childrenaGES=2
- Booking.com FR: https://www.booking.com/searchresults.fr.html?ss={DEST_URL_ENCODED}&checkin={YYYY-MM-DD}&checkout={YYYY-MM-DD}&group_adults=2&group_children=1&age=2
- Airbnb FR: https://www.airbnb.fr/s/{DEST_SLUG}/homes?checkin={YYYY-MM-DD}&checkout={YYYY-MM-DD}&adults=2&children=1
- Kayak FR: https://www.kayak.fr/vols/{FROM_IATA}-{TO_IATA}/{YYYY-MM-DD}/{YYYY-MM-DD}/2adultes/enfants-2

Always add a note that prices are estimates — traveler should click links to confirm live prices."""


def build_research_prompt(constraints: dict) -> str:
    lines = []
    key_labels = {
        "dates": "Dates / période",
        "budget": "Budget total",
        "destination": "Destination",
        "trip_type": "Type de voyage",
        "journey_time": "Durée max du trajet (porte-à-porte)",
        "accommodation": "Hébergement",
        "nights": "Nombre de nuits",
        "extras": "Contraintes / souhaits supplémentaires",
    }
    for key, label in key_labels.items():
        val = constraints.get(key, "").strip()
        if val:
            lines.append(f"- {label}: {val}")

    constraints_block = "\n".join(lines) if lines else "Pas de contraintes spécifiques — surprends-moi!"

    return f"""Voici les contraintes de voyage de la famille:

{constraints_block}

Génère exactement 3 propositions de voyage distinctes et réalistes.

Retourne UNIQUEMENT un tableau JSON valide (pas de texte avant ou après) avec cette structure exacte:

[
  {{
    "title": "Titre accrocheur du voyage",
    "destination": "Ville, Pays",
    "emoji": "🏖️",
    "why": "2-3 phrases expliquant pourquoi cette option correspond parfaitement à leurs contraintes. Mentionne spécifiquement l'accessibilité poussette et le transport sans voiture.",
    "transport": {{
      "description": "ex: TGV Paris-Barcelone direct ou Easyjet CDG-BCN",
      "type": "train ou vol",
      "duration": "ex: 4h30 direct",
      "price_per_person_eur": 85,
      "total_transport_eur": 255,
      "search_url": "URL pré-remplie SNCF Connect ou Skyscanner",
      "notes": "ex: Direct, pas de correspondance. Poussette acceptée dans le train."
    }},
    "accommodation": {{
      "description": "ex: Hôtel 4 étoiles à 200m de la plage",
      "type": "hotel ou airbnb",
      "price_per_night_eur": 120,
      "total_accommodation_eur": 720,
      "search_url": "URL pré-remplie Booking.com ou Airbnb",
      "notes": "ex: Ascenseur disponible, lit bébé sur demande, accès plage à plat."
    }},
    "total_estimate_eur": 975,
    "nights": 6,
    "journey_time_note": "ex: 4h30 porte-à-porte depuis Paris (30min RER + 3h30 TGV + 20min taxi)",
    "weather_note": "ex: 22°C en moyenne, ensoleillé, faible probabilité de pluie en avril",
    "stroller_note": "ex: Centre-ville plat et pavé, trottoirs larges, transports en commun accessibles",
    "booking_links": [
      {{"label": "🚄 Réserver le train", "url": "https://..."}},
      {{"label": "🏨 Chercher hôtels", "url": "https://..."}},
      {{"label": "🏠 Chercher Airbnb", "url": "https://..."}}
    ]
  }}
]

Les 3 propositions doivent être vraiment différentes — destinations différentes ou types d'expérience très différents (ex: bord de mer, montagne, city break).
Sois précis sur les destinations (pas "quelque part en Espagne" mais "Barcelone" ou "Malaga").
Les prix doivent être réalistes pour la période donnée.
Respecte STRICTEMENT la durée max de trajet — compte porte-à-porte (domicile → départ + trajet + arrivée destination).
La voiture n'est acceptable QUE si le trajet en voiture est inférieur à 1h (ex: aéroport → hôtel en taxi)."""


def research_trips(constraints: dict) -> list:
    """Use Claude to generate 3 trip proposals with booking URLs."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    prompt = build_research_prompt(constraints)

    log("holiday", "Starting trip research with Claude...")

    # Try with web_search tool first (Anthropic beta)
    proposals = _try_with_web_search(client, prompt)
    if proposals:
        log("holiday", f"Got {len(proposals)} proposals via web search")
        return proposals

    # Fallback: knowledge-based (no web search)
    log("holiday", "Using knowledge-based research (no web search)...")
    proposals = _research_knowledge_based(client, prompt)
    log("holiday", f"Got {len(proposals)} proposals via knowledge")
    return proposals


def _try_with_web_search(client, prompt: str) -> list:
    """Try research with Anthropic web_search tool. Returns [] on failure."""
    try:
        tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 6}]
        messages = [{"role": "user", "content": prompt}]

        for _ in range(12):  # max agentic iterations
            response = client.messages.create(
                model=RESEARCH_MODEL,
                max_tokens=4000,
                tools=tools,
                messages=messages,
            )

            # Collect text and tool_uses
            final_text = ""
            tool_uses = []
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text
                elif getattr(block, "type", "") == "tool_use":
                    tool_uses.append(block)

            if response.stop_reason == "end_turn" or not tool_uses:
                log_token_usage("holiday-research", response.usage, RESEARCH_MODEL)
                if final_text.strip():
                    return extract_json(final_text, array=True)
                return []

            # Continue agentic loop
            messages.append({"role": "assistant", "content": response.content})
            tool_results = [
                {"type": "tool_result", "tool_use_id": tu.id, "content": ""}
                for tu in tool_uses
            ]
            messages.append({"role": "user", "content": tool_results})
            time.sleep(0.5)

    except Exception as e:
        log("holiday", f"Web search approach failed: {e}")

    return []


def _research_knowledge_based(client, prompt: str) -> list:
    """Research without web search — Claude uses its knowledge."""
    response = client.messages.create(
        model=RESEARCH_MODEL,
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    log_token_usage("holiday-research", response.usage, RESEARCH_MODEL)
    text = ""
    for block in response.content:
        if hasattr(block, "text"):
            text += block.text
    return extract_json(text, array=True)


def send_first_proposal(proposals: list) -> None:
    """Send only the first proposal — user navigates to others via buttons."""
    from telegram_notify import send_holiday_proposal, send_telegram

    total = len(proposals)
    send_telegram(
        f"✅ <b>Recherche terminée — {total} option{'s' if total > 1 else ''} trouvée{'s' if total > 1 else ''}!</b>\n\n"
        f"Voici la première proposition:"
    )
    time.sleep(1)

    try:
        send_holiday_proposal(proposals[0], 1, total)
    except Exception as e:
        log("holiday", f"Failed to send first proposal: {e}")


def main():
    state = read_json("data/holiday-state.json")

    if state.get("status") != "researching":
        log("holiday", f"Unexpected state: {state.get('status')} — expected 'researching'")
        sys.exit(1)

    constraints = state.get("constraints", {})
    if not constraints:
        log("holiday", "No constraints found in state")
        sys.exit(1)

    log("holiday", f"Researching trips with constraints: {list(constraints.keys())}")

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

    send_first_proposal(proposals)
    log("holiday", "Done — proposals sent to Telegram")


if __name__ == "__main__":
    main()
