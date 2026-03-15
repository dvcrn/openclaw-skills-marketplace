"""
Flight Monitor — day-before alert + day-of polling via AeroDataBox.

Token budget: zero. All fetching is token-free. Alerts sent via Telegram.
Crons are registered per-flight by setup_flight_crons().
"""
import json
import os
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

AERODATABOX_KEY = os.environ.get("AERODATABOX_API_KEY", "")
AERODATABOX_BASE = "https://aerodatabox.p.rapidapi.com"
TRIPS_DIR = Path(os.environ.get("KAITRAVEL_TRIPS_DIR",
    Path(__file__).parent.parent.parent.parent / "memory/trips"))


# ─── AeroDataBox client ───────────────────────────────────────────────────────

def _adb_headers() -> dict:
    return {
        "X-RapidAPI-Key": AERODATABOX_KEY,
        "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com",
    }


def fetch_flight_status(flight_number: str, departure_date: str) -> Optional[dict]:
    """
    Fetch live flight status from AeroDataBox.
    departure_date: "YYYY-MM-DD"
    Returns normalized dict or None on failure.
    Free tier: 100 calls/month.
    """
    if not AERODATABOX_KEY:
        return None
    url = f"{AERODATABOX_BASE}/flights/number/{flight_number}/{departure_date}"
    try:
        r = requests.get(url, headers=_adb_headers(), timeout=10)
        if not r.ok:
            return None
        data = r.json()
        if not data:
            return None
        flight = data[0] if isinstance(data, list) else data
        dep = flight.get("departure", {})
        arr = flight.get("arrival", {})
        return {
            "flight_number": flight.get("number", flight_number),
            "status": flight.get("status", "unknown"),
            "departure": {
                "airport": dep.get("airport", {}).get("iata"),
                "terminal": dep.get("terminal"),
                "gate": dep.get("gate"),
                "scheduled_time": dep.get("scheduledTime", {}).get("local"),
                "revised_time": dep.get("revisedTime", {}).get("local"),
                "delay_min": dep.get("delay"),
            },
            "arrival": {
                "airport": arr.get("airport", {}).get("iata"),
                "terminal": arr.get("terminal"),
                "gate": arr.get("gate"),
                "scheduled_time": arr.get("scheduledTime", {}).get("local"),
                "revised_time": arr.get("revisedTime", {}).get("local"),
                "delay_min": arr.get("delay"),
            },
        }
    except Exception:
        return None


# ─── Alert formatters ─────────────────────────────────────────────────────────

def format_day_before_alert(flight: dict) -> str:
    fn = flight["flight_number"]
    dep_airport = flight["departure_airport"]
    dep_terminal = flight.get("departure_terminal", "")
    arr_airport = flight["arrival_airport"]
    dep_time = flight["departure_time"]
    dep_date = flight["departure_date"]
    seat = flight.get("seat", "")
    duration_min = flight.get("duration_min")
    duration_str = f"{duration_min // 60}h{duration_min % 60:02d}m" if duration_min else ""

    terminal_str = f" Terminal {dep_terminal}" if dep_terminal else ""
    seat_str = f" • Seat {seat}" if seat else ""
    duration_note = f" • {duration_str}" if duration_str else ""

    return (
        f"✈️ *Tomorrow: {fn}*\n"
        f"{dep_airport}{terminal_str} → {arr_airport}\n"
        f"Departure: *{dep_time}* on {dep_date}{seat_str}{duration_note}\n"
        f"Check-in usually opens 3h before. I'll track gate + status on the day."
    )


def format_day_of_update(flight_number: str, status: dict) -> Optional[str]:
    """Format a day-of status update. Returns None if nothing noteworthy."""
    dep = status.get("departure", {})
    gate = dep.get("gate")
    delay = dep.get("delay_min", 0) or 0
    revised = dep.get("revised_time")
    scheduled = dep.get("scheduled_time")
    flight_status = status.get("status", "").lower()

    parts = []
    if gate:
        parts.append(f"🚪 Gate *{gate}* assigned")
    if delay and delay > 15:
        parts.append(f"⚠️ Delayed *{delay} min*")
        if revised:
            parts.append(f"New departure: *{revised}*")
    if flight_status in ("boarding", "departed"):
        parts.append(f"🟢 Status: *{flight_status.title()}*")
    if flight_status == "cancelled":
        parts.append(f"🔴 *CANCELLED* — check airline app immediately")

    if not parts:
        return None

    return f"✈️ *{flight_number} update:* " + " • ".join(parts)


# ─── Trip loader ──────────────────────────────────────────────────────────────

def load_upcoming_flights(days_ahead: int = 60) -> list[dict]:
    """
    Load all flights from trip JSON files that depart within days_ahead.
    Returns list of flight dicts enriched with trip_id.
    """
    now = datetime.now(timezone.utc).date()
    cutoff = now + timedelta(days=days_ahead)
    flights = []

    for trip_file in TRIPS_DIR.glob("*.json"):
        try:
            trip = json.loads(trip_file.read_text())
        except Exception:
            continue
        trip_id = trip.get("trip_id", trip_file.stem)
        for f in trip.get("flights", []):
            dep_date_str = f.get("departure_date")
            if not dep_date_str:
                continue
            try:
                dep_date = datetime.strptime(dep_date_str, "%Y-%m-%d").date()
            except ValueError:
                continue
            if now <= dep_date <= cutoff:
                flights.append({**f, "trip_id": trip_id})

    return flights


# ─── Cron setup ──────────────────────────────────────────────────────────────

def get_cron_specs(flight: dict) -> list[dict]:
    """
    Generate cron job specs for a flight:
    - D-1 alert at 09:00 local (Asia/Jerusalem)
    - Day-of polling every 45 min from 3h before departure until +2h after
    Returns list of dicts suitable for the OpenClaw cron API.
    """
    fn = flight["flight_number"]
    dep_date = flight["departure_date"]
    dep_time = flight.get("departure_time", "00:00")
    trip_id = flight.get("trip_id", "unknown")

    try:
        dep_dt = datetime.strptime(f"{dep_date} {dep_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        return []

    d_minus_1 = (dep_dt - timedelta(days=1)).strftime("%Y-%m-%d")
    alert_text = format_day_before_alert(flight)

    specs = [
        {
            "name": f"flight-alert-d1-{fn}-{dep_date}",
            "schedule": {
                "kind": "cron",
                "expr": f"0 9 {d_minus_1[8:10]} {d_minus_1[5:7]} *",
                "tz": "Asia/Jerusalem",
            },
            "payload_text": (
                f"Send this flight reminder to Yonatan on Telegram:\n\n{alert_text}"
            ),
        },
        {
            "name": f"flight-poll-{fn}-{dep_date}",
            "schedule": {
                "kind": "cron",
                # Every 45 min, day of departure — OpenClaw will skip if not day-of
                "expr": f"*/45 * {dep_date[8:10]} {dep_date[5:7]} *",
                "tz": "Asia/Jerusalem",
            },
            "payload_text": (
                f"Poll AeroDataBox for flight {fn} on {dep_date} and send any noteworthy "
                f"updates (gate, delay >15min, boarding, cancellation) to Yonatan on Telegram. "
                f"Use flight_monitor.fetch_flight_status('{fn}', '{dep_date}'). "
                f"Only message if something changed since last check. If nothing new, reply HEARTBEAT_OK."
            ),
        },
    ]
    return specs


if __name__ == "__main__":
    flights = load_upcoming_flights(days_ahead=90)
    print(f"Found {len(flights)} upcoming flights:\n")
    for f in flights:
        print(f"  [{f['trip_id']}] {f['flight_number']} {f['departure_date']} "
              f"{f.get('departure_airport')}→{f.get('arrival_airport')}")
        alert = format_day_before_alert(f)
        print(f"  D-1 alert preview:\n{alert}\n")
