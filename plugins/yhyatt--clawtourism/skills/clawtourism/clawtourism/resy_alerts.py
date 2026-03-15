"""
Resy / reservation release-day alert system.
Stores planned restaurants with their platform + release window.
Generates cron specs: T-1hr warning + T=0 "book NOW" alert.
"""
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import os

TRIPS_DIR = Path(os.environ.get("KAITRAVEL_TRIPS_DIR",
    Path(__file__).parent.parent.parent.parent / "memory" / "travel"))

# Release rules per platform (days ahead, release time local to restaurant city)
PLATFORM_RULES = {
    "resy":       {"days_ahead": 28, "release_time": "00:00", "tz": "America/New_York"},
    "opentable":  {"days_ahead": 30, "release_time": "09:00", "tz": "America/New_York"},
    "thefork":    {"days_ahead": None, "release_time": None,  "tz": None},  # real-time
    "sevenrooms": {"days_ahead": 30, "release_time": "10:00", "tz": "America/New_York"},
}

# NYC restaurants to watch — confirmed target list for June 2026 guys trip
NYC_WATCHLIST = [
    {"name": "Don Angie",  "platform": "resy",      "cuisine": "Italian", "neighborhood": "West Village"},
    {"name": "Lilia",      "platform": "resy",      "cuisine": "Italian", "neighborhood": "Williamsburg"},
    {"name": "Tatiana",    "platform": "resy",      "cuisine": "Modern American", "neighborhood": "Lincoln Center"},
    {"name": "Carbone",    "platform": "resy",      "cuisine": "Italian-American", "neighborhood": "Greenwich Village"},
    {"name": "Le Bernardin", "platform": "resy",    "cuisine": "French seafood", "neighborhood": "Midtown"},
    {"name": "Atomix",     "platform": "resy",      "cuisine": "Korean tasting", "neighborhood": "Flatiron"},
    {"name": "Gage & Tollner", "platform": "resy",  "cuisine": "Chophouse", "neighborhood": "Downtown Brooklyn"},
]


def get_resy_alert_specs(restaurant_name: str, dinner_date: str,
                          platform: str = "resy", party_size: int = 6) -> list[dict]:
    """
    Generate two cron specs for a restaurant:
    - T-1hr: "Reservations open TOMORROW at midnight"
    - T=0: "Reservations open NOW — book immediately"

    dinner_date: "YYYY-MM-DD" (the actual dinner date)
    """
    rule = PLATFORM_RULES.get(platform)
    if not rule or not rule["days_ahead"]:
        return []

    dinner_dt = datetime.strptime(dinner_date, "%Y-%m-%d")
    release_dt = dinner_dt - timedelta(days=rule["days_ahead"])
    release_time_str = rule["release_time"]
    release_tz = ZoneInfo(rule["tz"])

    # Release moment in local tz
    release_h, release_m = map(int, release_time_str.split(":"))
    release_local = release_dt.replace(hour=release_h, minute=release_m,
                                        tzinfo=release_tz)
    warning_local = release_local - timedelta(hours=1)

    # Convert to Israel time for cron expression
    israel_tz = ZoneInfo("Asia/Jerusalem")
    release_il = release_local.astimezone(israel_tz)
    warning_il = warning_local.astimezone(israel_tz)

    def cron_expr(dt: datetime) -> str:
        return f"{dt.minute} {dt.hour} {dt.day} {dt.month} *"

    slug = restaurant_name.lower().replace(" ", "_").replace("&", "and")

    return [
        {
            "name": f"resy-warn-{slug}-{dinner_date}",
            "schedule": {
                "kind": "cron",
                "expr": cron_expr(warning_il),
                "tz": "Asia/Jerusalem",
            },
            "payload_text": (
                f"⏰ *Heads up!* {restaurant_name} opens reservations in *1 hour* "
                f"for {dinner_date} (party of {party_size}).\n"
                f"Platform: {platform.title()} — be ready to book at midnight ET.\n"
                f"Open now to have it ready: https://resy.com"
            ),
        },
        {
            "name": f"resy-now-{slug}-{dinner_date}",
            "schedule": {
                "kind": "cron",
                "expr": cron_expr(release_il),
                "tz": "Asia/Jerusalem",
            },
            "payload_text": (
                f"🚨 *Book NOW!* {restaurant_name} just opened for {dinner_date}.\n"
                f"Party of {party_size} — slots go in minutes.\n"
                f"➡️ https://resy.com (search {restaurant_name})"
            ),
        },
    ]


def list_watchlist_status() -> str:
    """Summary of NYC watchlist — what's set up, what's pending."""
    lines = ["*NYC June 2026 — Restaurant Watchlist*\n"]
    for r in NYC_WATCHLIST:
        lines.append(f"• {r['name']} ({r['neighborhood']}) — {r['platform'].title()} "
                     f"[dinner date: *TBD* — cron pending]")
    lines.append("\n_Set dinner dates to activate Resy crons._")
    return "\n".join(lines)


if __name__ == "__main__":
    # Preview: what crons would look like for Don Angie on Jun 24
    specs = get_resy_alert_specs("Don Angie", "2026-06-24", party_size=6)
    for s in specs:
        print(f"{s['name']}")
        print(f"  Cron: {s['schedule']['expr']} (Asia/Jerusalem)")
        print(f"  Message: {s['payload_text'][:80]}...")
        print()

    print(list_watchlist_status())
