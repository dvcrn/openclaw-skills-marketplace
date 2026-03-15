"""
Trip briefings — assembled at fire time from live data.

Each briefing pulls fresh data from weather, packing, visa_check, transfers
and formats everything into one consolidated message per checkpoint.

Called by pre_trip.py cron payloads at D-14 / D-7 / D-3 / D-1.
"""
from __future__ import annotations
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Optional
import os

from clawtourism.models import Trip
from clawtourism.store import TripStore
from clawtourism import weather, packing, visa_check, transfers, packing_profile

TRIPS_DIR = Path(os.environ.get("CLAWTOURISM_TRIPS_DIR",
    Path(__file__).parent.parent.parent.parent / "memory" / "trips"))


def _load_trip(trip_id: str) -> Optional[dict]:
    p = TRIPS_DIR / f"{trip_id}.json"
    if p.exists():
        return json.loads(p.read_text())
    return None


def _destination_cities(trip: dict) -> list[str]:
    """Extract all destination cities from a trip."""
    cities = []
    if trip.get("destination"):
        cities.append(trip["destination"])
    # Add hotel cities
    for h in trip.get("hotels", []):
        if h.get("address"):
            cities.append(h["address"].split(",")[-1].strip())
    # Add cruise ports
    if trip.get("cruise"):
        cities.extend(trip["cruise"].get("itinerary", []))
    return list(dict.fromkeys(cities))  # deduplicate, preserve order


def _has_kids(trip: dict) -> bool:
    travellers = trip.get("travellers", [])
    return any(t in travellers for t in ["Zoe Hyatt", "Lenny Hyatt"])


def _is_cruise(trip: dict) -> bool:
    return bool(trip.get("cruise"))


def _primary_airport(trip: dict) -> Optional[str]:
    """Best guess at arrival airport from flights."""
    for f in trip.get("flights", []):
        if f.get("arrival_airport"):
            return f["arrival_airport"]
    return None


# ─── D-14 briefing ───────────────────────────────────────────────────────────

def generate_d14(trip_id: str) -> str:
    trip = _load_trip(trip_id)
    if not trip:
        return f"⚠️ Trip {trip_id} not found."

    dest = trip.get("destination", "your trip")
    cities = _destination_cities(trip)
    has_kids = _has_kids(trip)
    cruise = _is_cruise(trip)

    sections = [f"🧳 *{dest} in 2 weeks!*\n"]

    # Static checklist (visa was already sent at trip creation)
    checklist = [
        "• Book any restaurants not yet reserved",
        "• Check passport expiry" + (" — Zoe + Lenny passports too" if has_kids else ""),
        "• Travel insurance confirmed?",
        "• Excursions / activities booked?",
    ]
    if cruise:
        checklist.append("• Complete cruise online check-in")
    sections.append("*Checklist:*\n" + "\n".join(checklist))

    return "\n\n".join(s for s in sections if s)


# ─── D-7 briefing ────────────────────────────────────────────────────────────

def generate_d7(trip_id: str) -> str:
    trip = _load_trip(trip_id)
    if not trip:
        return f"⚠️ Trip {trip_id} not found."

    dest = trip.get("destination", "your trip")
    start_str = trip.get("start_date", "")
    has_kids = _has_kids(trip)
    cruise = _is_cruise(trip)
    cities = _destination_cities(trip)

    sections = [f"✈️ *{dest} in 1 week*\n"]

    # Packing — use member profile if available, otherwise full generated list
    try:
        start = date.fromisoformat(start_str)
        forecasts = weather.get_forecast(dest, start, days=7) if dest else []
        formal_nights = 2 if cruise else 0
        from clawtourism.models import Trip as TripModel
        mock_trip = TripModel(
            trip_id=trip_id,
            destination=dest,
            start_date=date.fromisoformat(start_str),
            end_date=date.fromisoformat(trip.get("end_date", start_str)),
        )
        pack = packing.generate(
            mock_trip,
            forecasts=forecasts,
            has_young_kids=any("Lenny" in t for t in trip.get("travellers", [])),
            has_older_kids=any("Zoe" in t for t in trip.get("travellers", [])),
            is_cruise=cruise,
            formal_dinner_nights=formal_nights,
        )
        # Use packing profile if member has one (default: yonatan for family trips)
        profile = packing_profile.get_profile("yonatan")
        sections.append(
            packing_profile.format_briefing(profile, pack.categories, dest)
        )
    except Exception:
        sections.append(
            "*Packing reminder:*\n• Documents, clothes, electronics, meds"
            + (" + kids items" if has_kids else "")
        )

    # FX rate reminder
    dest_lower = dest.lower() if dest else ""
    currency_note = None
    if any(c in dest_lower for c in ["spain", "barcelona", "italy", "france", "greece", "malta"]):
        currency_note = "💱 Heading to Eurozone — worth loading Revolut/checking your card FX rate"
    elif any(c in dest_lower for c in ["usa", "new york", "miami", "angeles"]):
        currency_note = "💱 Heading to USD — worth loading Revolut/checking your card FX rate"
    if currency_note:
        sections.append(currency_note)

    # Other checklist items
    extra = [
        "• Prescriptions packed (+ spare supply)?",
        "• Notify credit cards of travel dates",
        "• Download offline maps",
    ]
    if has_kids:
        extra.append("• Kids snacks + entertainment for flights?")
    sections.append("\n".join(extra))

    return "\n\n".join(s for s in sections if s)


# ─── D-3 briefing ────────────────────────────────────────────────────────────

def generate_d3(trip_id: str) -> str:
    trip = _load_trip(trip_id)
    if not trip:
        return f"⚠️ Trip {trip_id} not found."

    dest = trip.get("destination", "your trip")
    start_str = trip.get("start_date", "")
    has_kids = _has_kids(trip)

    sections = [f"🗂️ *{dest} — 3 days to go*\n"]

    # Weather forecast — fresh
    try:
        start = date.fromisoformat(start_str)
        forecasts = weather.get_forecast(dest, start, days=5)
        if forecasts:
            sections.append(weather.format_forecast_block(dest, forecasts))
    except Exception:
        pass

    # Logistics checklist
    checklist = [
        "• Boarding passes + hotel refs saved offline",
        "• Luggage weighed?",
        "• Car / taxi to airport arranged?",
        "• Emergency contacts noted",
    ]
    if has_kids:
        checklist.append("• Stroller at door? (Lenny)")
        checklist.append("• Kids' car seats arranged?")
    sections.append("*Checklist:*\n" + "\n".join(checklist))

    return "\n\n".join(s for s in sections if s)


# ─── D-1 briefing ────────────────────────────────────────────────────────────

def generate_d1(trip_id: str) -> str:
    trip = _load_trip(trip_id)
    if not trip:
        return f"⚠️ Trip {trip_id} not found."

    dest = trip.get("destination", "your trip")
    start_str = trip.get("start_date", "")
    has_kids = _has_kids(trip)

    sections = [f"🚨 *Tomorrow: {dest}!*\n"]

    # Weather at destination for arrival day
    try:
        start = date.fromisoformat(start_str)
        forecasts = weather.get_forecast(dest, start, days=2)
        if forecasts:
            sections.append(weather.format_forecast_block(dest, forecasts[:2]))
    except Exception:
        pass

    # Transfer suggestions
    try:
        airport_code = _primary_airport(trip)
        if airport_code:
            opts = transfers.get_transfer_options(airport_code, has_kids=has_kids)
            if opts:
                arrival_label = f"{airport_code} airport"
                sections.append(transfers.format_transfers(arrival_label, dest, opts))
    except Exception:
        pass

    # Final checklist
    checklist = [
        "• Bags packed and weighed?",
        "• Passport in bag (not drawer!)?",
        "• Phone charged?",
        "• I'll track gate + flight status on the day ✈️",
    ]
    if has_kids:
        checklist.append("• Stroller + car seat at the door?")
    sections.append("\n".join(checklist))

    return "\n\n".join(s for s in sections if s)


# ─── Dispatch ────────────────────────────────────────────────────────────────

GENERATORS = {
    14: generate_d14,
    7:  generate_d7,
    3:  generate_d3,
    1:  generate_d1,
}


def generate(trip_id: str, days_before: int) -> str:
    fn = GENERATORS.get(days_before)
    if not fn:
        return f"No briefing defined for D-{days_before}."
    return fn(trip_id)


if __name__ == "__main__":
    import sys
    trip_id = sys.argv[1] if len(sys.argv) > 1 else "msc-cruise-mar-2026"
    day = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    print(generate(trip_id, day))
