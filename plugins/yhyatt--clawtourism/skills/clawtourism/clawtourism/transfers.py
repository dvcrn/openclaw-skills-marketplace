"""
Transfer suggestions — airport / cruise pier → hotel / Airbnb.
Proactive: fires when flight arrival + accommodation address are both known.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class TransferOption:
    mode: str           # "taxi", "train", "bus", "shuttle", "subway"
    description: str
    duration: str       # "~35 min"
    cost: str           # "₪180", "€5.50", "free"
    booking_tip: str = ""
    kids_note: str = ""

    def format(self) -> str:
        line = f"  🚕 *{self.mode.title()}*: {self.description}"
        line += f" — {self.duration}, {self.cost}"
        if self.booking_tip:
            line += f"\n    _{self.booking_tip}_"
        if self.kids_note:
            line += f"\n    👶 {self.kids_note}"
        return line


# ─── Transfer data per airport/port → city ───────────────────────────────────

_TRANSFERS: dict[str, list[TransferOption]] = {

    # Tel Aviv
    "TLV": [
        TransferOption("taxi/Gett", "Gett or bolt from arrivals hall",
                       "~35 min to city centre", "₪120–160", "book via Gett app"),
        TransferOption("train", "Israel Railways to Tel Aviv Savidor / HaShalom",
                       "~20 min", "₪6.50", "runs 06:00–22:00 (not Shabbat)",
                       kids_note="Strollers welcome, elevators at major stations"),
        TransferOption("shared sherut", "Shared taxi, departs when full",
                       "45–60 min", "₪25/person", "HaYovel sherut stand, exit 3"),
    ],

    # New York — EWR (Newark)
    "EWR": [
        TransferOption("taxi/Uber", "Uber/Lyft from arrivals — pool option available",
                       "~35 min (off-peak)", "$50–80", "surge pricing likely peak hours"),
        TransferOption("train", "NJ Transit + PATH → Manhattan (Penn Station or WTC)",
                       "~45 min", "$15–17", "AirTrain ($9) + NJ Transit ($8)",
                       kids_note="Under 5 free; PATH has elevators"),
        TransferOption("shared shuttle", "NYC Airporter / Go Airlink to Midtown hotels",
                       "~50 min", "$30–35/person", "nycairporter.com — book ahead"),
    ],

    # New York — JFK
    "JFK": [
        TransferOption("taxi", "Yellow cab, flat rate to Manhattan",
                       "~45 min", "$70 flat + tolls + tip"),
        TransferOption("subway", "AirTrain + A/E train → Midtown",
                       "~55 min", "$10", "cheapest option",
                       kids_note="Strollers at busy times can be tricky on A train"),
        TransferOption("Uber/Lyft", "Meet at designated rideshare lot",
                       "~40 min", "$55–90", "surge pricing during peak"),
    ],

    # Barcelona — Airport (BCN)
    "BCN": [
        TransferOption("Aerobús", "Direct bus to Plaça Catalunya every 5 min",
                       "~35 min", "€6.75", "aerobusbarcelona.es",
                       kids_note="Under 4 free"),
        TransferOption("taxi", "Taxi stand outside arrivals T1 / T2",
                       "~25 min", "€35–45", "metered + airport supplement"),
        TransferOption("metro L9 Sud", "Metro to city (change at Torrassa or Zona Universitaria)",
                       "~45 min", "€5.15 (zone 2)", "slower but cheap"),
    ],

    # MSC Cruise — Barcelona port
    "BCN_PORT": [
        TransferOption("taxi", "From Barcelona Port (World Trade Centre end)",
                       "~10 min to centre", "€12–18", "plenty of taxis at pier"),
        TransferOption("walking", "15-min walk to Las Ramblas / Gothic Quarter",
                       "15 min", "free", kids_note="Flat, stroller-friendly"),
        TransferOption("Bus 120", "Local bus to Barceloneta / Passeig de Gràcia",
                       "~20 min", "€2.40"),
    ],

    # Athens — Piraeus port (cruise)
    "PIRAEUS": [
        TransferOption("metro M1", "Piraeus → Monastiraki (city centre) — Line 1 (Green)",
                       "~25 min", "€1.20", "runs frequently",
                       kids_note="Elevators at main stations"),
        TransferOption("taxi", "From port entrance",
                       "~20 min to Acropolis area", "€20–30", "negotiate or use meter"),
        TransferOption("tram", "Tram to Syntagma (city centre)",
                       "~45 min", "€1.40", "scenic but slow"),
    ],
}


def get_transfer_options(
    airport_or_port_code: str,
    has_kids: bool = False,
    destination_hint: str = "",
) -> list[TransferOption]:
    """Return transfer options for a given airport/port code."""
    key = airport_or_port_code.upper()
    options = _TRANSFERS.get(key, [])
    return options


def format_transfers(
    from_label: str,
    to_label: str,
    options: list[TransferOption],
) -> str:
    if not options:
        return ""
    lines = [f"🚕 *Transfers: {from_label} → {to_label}*\n"]
    for opt in options:
        lines.append(opt.format())
    return "\n".join(lines)


def get_airport_code_for_city(city: str) -> Optional[str]:
    """Best-guess airport code from city name."""
    _MAP = {
        "tel aviv": "TLV", "israel": "TLV",
        "new york": "EWR",  # default to EWR (Yonatan's usual)
        "barcelona": "BCN",
        "athens": "PIRAEUS",
    }
    return _MAP.get(city.lower())
