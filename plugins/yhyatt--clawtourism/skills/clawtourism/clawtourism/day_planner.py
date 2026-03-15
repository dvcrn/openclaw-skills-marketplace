"""
Day Planner — morning / afternoon / evening suggestions for every trip day.

Works identically for:
  - Cruise port days (add back_by_time constraint)
  - Regular city days (hotel / Airbnb based)
  - Multi-city itineraries

Activity data is curated per city. For TLV / BCN / NYC, also queries ClawEvents
when available. All suggestions are opt-out per group member.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, time
from typing import Optional

from clawtourism.weather import DayForecast


@dataclass
class Activity:
    name: str
    description: str
    duration_h: float = 2.0
    cost_approx: str = ""           # e.g. "€10", "free", "€50–80"
    booking_tip: str = ""
    kids_friendly: bool = True
    indoor: bool = False


@dataclass
class DayPlan:
    city: str
    date: date
    morning: list[Activity] = field(default_factory=list)
    afternoon: list[Activity] = field(default_factory=list)
    evening: list[Activity] = field(default_factory=list)
    weather: Optional[DayForecast] = None
    back_by: Optional[time] = None  # cruise constraint

    def format(self, day_num: Optional[int] = None) -> str:
        day_label = f"Day {day_num} — " if day_num else ""
        header = f"🗓️ *{day_label}{self.city} ({self.date.strftime('%a %b %-d')})*"
        if self.back_by:
            header += f"\n⚓ Back on ship by {self.back_by.strftime('%H:%M')}"
        if self.weather:
            header += f"\n🌤️ {self.weather.summary}"
            if self.weather.packing_hint:
                header += f" — {self.weather.packing_hint}"

        sections = []
        for emoji, label, items in [
            ("☀️", "Morning", self.morning),
            ("🌤️", "Afternoon", self.afternoon),
            ("🌙", "Evening", self.evening),
        ]:
            if not items:
                continue
            block = [f"\n{emoji} *{label}*"]
            for a in items:
                line = f"  • *{a.name}*"
                if a.description:
                    line += f" — {a.description}"
                extras = []
                if a.cost_approx:
                    extras.append(a.cost_approx)
                if a.booking_tip:
                    extras.append(a.booking_tip)
                if extras:
                    line += f"\n    _{', '.join(extras)}_"
                block.append(line)
            sections.append("\n".join(block))

        return header + "".join(sections)


# ─── Curated activity data ────────────────────────────────────────────────────

_CITIES: dict[str, dict] = {

    "barcelona": {
        "morning": [
            Activity("Sagrada Família", "Gaudí's masterpiece — book online night before, queues start 8am",
                     2.5, "€26–36", "book at sagradafamilia.org", kids_friendly=True, indoor=True),
            Activity("Boqueria Market", "Iconic market on Las Ramblas — breakfast + fresh fruit",
                     1.0, "free entry", kids_friendly=True),
            Activity("Park Güell", "Free zones accessible without ticket; paid monumental zone €10",
                     2.0, "free/€10", "paid zone: parkguell.barcelona", kids_friendly=True),
            Activity("Gothic Quarter walk", "Carrer del Bisbe, Cathedral, Plaça Reial",
                     1.5, "free", kids_friendly=True),
        ],
        "afternoon": [
            Activity("Barceloneta Beach", "City beach — 15min walk or metro L4",
                     2.0, "free", kids_friendly=True),
            Activity("Picasso Museum", "Medieval palaces, Picasso's early works",
                     2.0, "€12", "book online to skip queue", indoor=True),
            Activity("El Born neighbourhood", "Trendy bars, boutiques, Santa Maria del Mar basilica",
                     1.5, "free", kids_friendly=True),
            Activity("Camp Nou tour", "Football museum + stadium tour",
                     2.0, "€26", "if game day, skip — traffic", kids_friendly=True, indoor=True),
        ],
        "evening": [
            Activity("Tapas at Bar del Pla", "Born neighbourhood staple — patatas bravas, croquetas",
                     2.0, "€25–35/person", "reservations via TheFork"),
            Activity("El Xampanyet", "Classic cava bar in Born — no reservations, arrive early",
                     1.5, "€15–20/person"),
            Activity("Pacha / Razzmatazz", "Nightlife — Pacha (house/pop), Razzmatazz (indie/electronic)",
                     4.0, "€20–30 entry", "check Xceed for tickets", kids_friendly=False),
            Activity("Sunset at Bunkers del Carmel", "Best 360° view of the city — bring drinks",
                     1.5, "free", kids_friendly=True),
        ],
    },

    "new york": {
        "morning": [
            Activity("Central Park", "Morning run or walk — Bethesda Fountain, Bow Bridge",
                     1.5, "free", kids_friendly=True),
            Activity("High Line", "Elevated park — great views, open from 7am",
                     1.5, "free", kids_friendly=True),
            Activity("Brooklyn Bridge walk", "Start Manhattan side, walk to DUMBO",
                     1.5, "free", kids_friendly=True),
            Activity("MoMA", "Modern art — reserve online",
                     2.5, "$30", "moma.org", indoor=True),
        ],
        "afternoon": [
            Activity("The Met", "Metropolitan Museum of Art — can spend 3+ hours",
                     3.0, "$30 suggested", "metmuseum.org", indoor=True),
            Activity("DUMBO + Brooklyn Bridge Park", "Views of Manhattan, Jane's Carousel, pebble beach",
                     2.0, "free", kids_friendly=True),
            Activity("Chelsea Market", "Food hall, boutiques, Google NYC building outside",
                     1.5, "free entry", kids_friendly=True),
            Activity("One World Trade + 9/11 Memorial", "Memorial pools + museum",
                     2.0, "memorial free / museum $33", "911memorial.org", indoor=True),
        ],
        "evening": [
            Activity("Don Angie", "Acclaimed Italian — book via Resy 28 days ahead",
                     2.5, "$80–120/person", "resy.com — midnight release"),
            Activity("Smalls Jazz Club", "Greenwich Village institution — sets start 7:30pm & 10:30pm",
                     2.5, "$25 cover", "smallslive.com", kids_friendly=False),
            Activity("Rooftop bar — 230 Fifth", "Midtown views, heated in spring",
                     2.0, "$20–30 drinks min", kids_friendly=False),
            Activity("Comedy Cellar", "Top NYC stand-up, cellar below Macdougal St",
                     2.0, "$20–30", "comedycellar.com", kids_friendly=False),
        ],
    },

    "tel aviv": {
        "morning": [
            Activity("Carmel Market", "Shuk haCarmel — shakshuka breakfast, fresh produce",
                     1.5, "free entry", kids_friendly=True),
            Activity("Tel Aviv beach", "Gordon or Frishman — swim + coffee at beach café",
                     2.0, "free", kids_friendly=True),
            Activity("White City walk", "Bauhaus architecture tour, Dizengoff area",
                     1.5, "free (self-guided)", kids_friendly=True),
            Activity("Jaffa Old City", "Clock tower, flea market, port views — 30min from centre",
                     2.0, "free", kids_friendly=True),
        ],
        "afternoon": [
            Activity("Tel Aviv Museum of Art", "Strong contemporary + Impressionist collection",
                     2.5, "₪60", "tamuseum.org.il", indoor=True),
            Activity("Neve Tzedek", "Boutique neighbourhood — galleries, cafés, Suzanne Dellal Centre",
                     1.5, "free", kids_friendly=True),
            Activity("Yarkon Park", "Huge city park — bike rental, paddle boats",
                     2.0, "free / ₪30 bikes", kids_friendly=True),
        ],
        "evening": [
            Activity("Florentine neighbourhood", "Bars, street art, nightlife hub",
                     3.0, "", kids_friendly=False),
            Activity("Lev Cinema", "Boutique cinema at Dizengoff Center — art house films",
                     2.5, "₪45", "lev.co.il"),
            Activity("HaBasta", "Market-to-table Tel Aviv classic, Carmel Market area",
                     2.5, "₪150–200/person", "reserve ahead — habasta.co.il"),
        ],
    },
}

# Cruise port cities mapped to city keys
_PORT_ALIASES = {
    "barcelona": "barcelona", "rome": "rome", "civitavecchia": "rome",
    "athens": "athens", "piraeus": "athens", "valletta": "valletta",
    "dubrovnik": "dubrovnik", "kotor": "kotor", "split": "split",
}


def plan_day(
    city: str,
    trip_date: date,
    weather: Optional[DayForecast] = None,
    has_kids: bool = False,
    back_by: Optional[time] = None,      # cruise: must be back on ship by this time
    prefer_indoor: bool = False,          # if weather is bad
    day_num: Optional[int] = None,
) -> DayPlan:
    city_key = city.lower()
    city_key = _PORT_ALIASES.get(city_key, city_key)
    data = _CITIES.get(city_key, {})

    def pick(slot: str, n: int = 2) -> list[Activity]:
        items = data.get(slot, [])
        if has_kids:
            items = [a for a in items if a.kids_friendly]
        if prefer_indoor or (weather and weather.rain_mm > 5):
            items = sorted(items, key=lambda a: not a.indoor)
        return items[:n]

    return DayPlan(
        city=city.title(),
        date=trip_date,
        morning=pick("morning", 2),
        afternoon=pick("afternoon", 2),
        evening=pick("evening", 2) if not back_by else [],
        weather=weather,
        back_by=back_by,
    )
