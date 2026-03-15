"""
Pre-trip checklist — D-14, D-7, D-3, D-1 cron specs per trip.
Family trips only (Mode B). Group trips handled by group agent.

Crons fire as agentTurn (isolated). The payload instructs the agent to call
briefing.generate(trip_id, days_before), which fetches live data (weather,
packing list, visa, transfers) at fire time and sends the result to Telegram.
"""
import json
from datetime import date, datetime, timedelta
from pathlib import Path
import os

TRIPS_DIR = Path(os.environ.get("CLAWTOURISM_TRIPS_DIR",
    Path(__file__).parent.parent.parent.parent / "memory" / "trips"))

FAMILY_TRAVELLERS = {"Louise Hyatt", "Zoe Hyatt", "Lenny Hyatt"}


def is_family_trip(trip: dict) -> bool:
    travellers = set(trip.get("travellers", []))
    return bool(travellers & FAMILY_TRAVELLERS)


def get_checklist_cron_specs(trip: dict) -> list[dict]:
    """
    Generate D-14, D-7, D-3, D-1 agentTurn cron specs for a family trip.
    Each cron calls briefing.generate() at fire time for live data.
    """
    if not is_family_trip(trip):
        return []

    start = trip.get("start_date", "")
    trip_id = trip["trip_id"]
    destination = trip.get("destination", "trip")

    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d")
    except ValueError:
        return []

    specs = []

    # Checkpoint descriptions (used in cron name + agent instruction context)
    checkpoint_intros = {
        14: f"{destination} is in 2 weeks",
        7:  f"{destination} is in 1 week",
        3:  f"{destination} is in 3 days",
        1:  f"Tomorrow: {destination}",
    }

    for days_before, intro in checkpoint_intros.items():
        alert_date = start_dt - timedelta(days=days_before)
        if alert_date.date() <= date.today():
            continue  # Already past — skip

        payload = (
            f"[ClawTourism pre-trip D-{days_before}] {intro}.\n\n"
            f"Run the following Python and send the output to Yonatan on Telegram:\n\n"
            f"```python\n"
            f"from clawtourism.briefing import generate\n"
            f"print(generate('{trip_id}', {days_before}))\n"
            f"```\n\n"
            f"Send the result as a Telegram message to 5553808416. "
            f"Do not add commentary — send the briefing content as-is."
        )

        specs.append({
            "name": f"pretripcheck-{trip_id}-d{days_before}",
            "schedule": {
                "kind": "cron",
                "expr": f"0 9 {alert_date.day} {alert_date.month} *",
                "tz": "Asia/Jerusalem",
            },
            "sessionTarget": "isolated",
            "payload": {
                "kind": "agentTurn",
                "message": payload,
            },
            "delivery": {
                "mode": "none",  # agent sends to Telegram directly
            },
        })

    return specs


if __name__ == "__main__":
    for trip_file in TRIPS_DIR.glob("*.json"):
        trip = json.loads(trip_file.read_text())
        specs = get_checklist_cron_specs(trip)
        if specs:
            print(f"\n{trip['trip_id']} — {len(specs)} checklist crons:")
            for s in specs:
                print(f"  {s['name']} @ {s['schedule']['expr']}")
