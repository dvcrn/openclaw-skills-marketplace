"""
Packing list generator — weather-aware, kids-aware, trip-type aware.
Called at D-7 for family trips and on-demand for group trips.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from clawtourism.models import Trip, CruiseBooking
from clawtourism.weather import DayForecast


@dataclass
class PackingList:
    trip_id: str
    destination: str
    nights: int
    categories: dict[str, list[str]] = field(default_factory=dict)

    def format(self) -> str:
        lines = [f"🧳 *Packing list — {self.destination} ({self.nights} nights)*\n"]
        for cat, items in self.categories.items():
            lines.append(f"*{cat}*")
            for item in items:
                lines.append(f"  • {item}")
            lines.append("")
        return "\n".join(lines)


def _is_warm(forecasts: list[DayForecast]) -> bool:
    return bool(forecasts) and sum(f.temp_max for f in forecasts) / len(forecasts) > 22

def _has_rain(forecasts: list[DayForecast]) -> bool:
    return any(f.rain_mm > 3 for f in forecasts)

def _has_cold(forecasts: list[DayForecast]) -> bool:
    return bool(forecasts) and any(f.temp_min < 12 for f in forecasts)


def generate(
    trip: Trip,
    forecasts: Optional[list[DayForecast]] = None,
    has_young_kids: bool = False,       # Lenny (toddler)
    has_older_kids: bool = False,       # Zoe (5.5)
    is_cruise: bool = False,
    formal_dinner_nights: int = 0,
) -> PackingList:
    nights = trip.nights
    warm = _is_warm(forecasts or [])
    rain = _has_rain(forecasts or [])
    cold = _has_cold(forecasts or [])
    dest = trip.destination

    # --- Documents ---
    docs = [
        "Passports (check expiry — 6+ months from return)",
        "Booking refs (flights, hotel, cruise) — offline copy",
        "Travel insurance documents",
        "Credit cards (notify bank of travel)",
    ]
    if is_cruise:
        docs.append("Cruise check-in confirmation + cabin number")
    if has_young_kids or has_older_kids:
        docs.append("Kids' passports + birth certificates")

    # --- Clothes ---
    if warm:
        base_tops = max(5, nights // 2)
        clothes = [
            f"T-shirts / light tops ×{base_tops}",
            f"Shorts / light trousers ×{max(3, nights // 3)}",
            "Swimwear ×2",
            "Sandals + comfortable walking shoes",
        ]
    else:
        clothes = [
            f"Shirts / tops ×{max(4, nights // 2)}",
            f"Trousers / jeans ×{max(2, nights // 4)}",
            "Light jacket / fleece",
            "Comfortable walking shoes + one smarter pair",
        ]

    if cold:
        clothes.append("Warm layer / down jacket")
    if rain:
        clothes.append("Rain jacket / packable waterproof")
    if formal_dinner_nights > 0:
        clothes.append(f"Smart/formal outfit ×{min(formal_dinner_nights, 2)} (formal dinner nights)")
    if is_cruise:
        clothes.append("Lanyard / cabin key holder")

    # --- Electronics ---
    electronics = [
        "Phone + charger",
        "Powerbank",
        "Universal adapter" if dest not in ("Israel", "Tel Aviv") else None,
        "Earbuds / headphones",
        "Camera (optional)",
    ]
    electronics = [e for e in electronics if e]

    # --- Toiletries ---
    toiletries = [
        "Sunscreen SPF 50+" if warm else "Sunscreen",
        "Deodorant, toothbrush, toothpaste",
        "Shampoo / conditioner (travel size)",
        "Razor",
        "After-sun / moisturizer" if warm else None,
    ]
    toiletries = [t for t in toiletries if t]

    # --- Meds ---
    meds = [
        "Paracetamol / ibuprofen",
        "Antihistamine",
        "Any prescription medications (enough for trip + 3 days)",
        "Plasters / small first aid",
    ]
    if is_cruise:
        meds.append("Motion sickness tablets")
    if has_young_kids:
        meds.extend([
            "Kids' paracetamol (Acamol syrup)",
            "Kids' antihistamine syrup",
            "Ear drops",
        ])

    # --- Kids (if applicable) ---
    kids_items = []
    if has_young_kids:
        kids_items.extend([
            f"Pull-ups / nappies ×{nights * 6} (Lenny)",
            "Swim nappies ×4",
            "Stroller + rain cover",
            "Kids' sunscreen 50+",
            "Snacks (plane + first day)",
            "Comfort toy / blanket",
            "Baby carrier / sling",
        ])
    if has_older_kids:
        kids_items.extend([
            "Kids' sunscreen (Zoe)",
            "Swim vest / floaties",
            "Entertainment: tablet + headphones, colouring book",
            "Kids' snacks",
        ])
    if is_cruise and (has_young_kids or has_older_kids):
        kids_items.append("Kids' formal outfit ×1 (formal dinner night)")

    categories: dict[str, list[str]] = {
        "📄 Documents": docs,
        "👕 Clothes": clothes,
        "🔌 Electronics": electronics,
        "🪥 Toiletries": toiletries,
        "💊 Meds": meds,
    }
    if kids_items:
        categories["👶 Kids"] = kids_items

    return PackingList(
        trip_id=trip.trip_id,
        destination=dest,
        nights=nights,
        categories=categories,
    )
