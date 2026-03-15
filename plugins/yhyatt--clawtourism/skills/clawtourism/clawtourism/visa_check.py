"""
Visa check — Israeli passport entry requirements by destination country.
No API key required — curated lookup table.
Updated: 2026-03. Source: Passport Index / Henley Passport Index.

Israeli passport (biometric): Henley rank ~24, ~166 visa-free destinations.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class VisaRequirement:
    country: str
    requirement: str    # "visa-free", "e-visa", "visa-on-arrival", "visa-required"
    stay_days: Optional[int]
    notes: str = ""
    apply_url: str = ""

    @property
    def emoji(self) -> str:
        return {
            "visa-free": "✅",
            "e-visa": "⚡",
            "visa-on-arrival": "🛬",
            "visa-required": "🔴",
        }.get(self.requirement, "❓")

    def format(self) -> str:
        days_str = f" (up to {self.stay_days} days)" if self.stay_days else ""
        line = f"{self.emoji} *{self.country}*: {self.requirement}{days_str}"
        if self.notes:
            line += f"\n   _{self.notes}_"
        if self.apply_url and self.requirement in ("e-visa", "visa-required"):
            line += f"\n   Apply: {self.apply_url}"
        return line


# Israeli passport visa requirements — curated, commonly visited
_REQUIREMENTS: dict[str, VisaRequirement] = {

    # Europe (Schengen — visa-free 90/180)
    "france":        VisaRequirement("France", "visa-free", 90, "Schengen area"),
    "germany":       VisaRequirement("Germany", "visa-free", 90, "Schengen area"),
    "spain":         VisaRequirement("Spain", "visa-free", 90, "Schengen area"),
    "italy":         VisaRequirement("Italy", "visa-free", 90, "Schengen area"),
    "greece":        VisaRequirement("Greece", "visa-free", 90, "Schengen area"),
    "portugal":      VisaRequirement("Portugal", "visa-free", 90, "Schengen area"),
    "netherlands":   VisaRequirement("Netherlands", "visa-free", 90, "Schengen area"),
    "switzerland":   VisaRequirement("Switzerland", "visa-free", 90, "Schengen area"),
    "austria":       VisaRequirement("Austria", "visa-free", 90, "Schengen area"),
    "czech republic":VisaRequirement("Czech Republic", "visa-free", 90, "Schengen area"),
    "croatia":       VisaRequirement("Croatia", "visa-free", 90, "EU/Schengen"),
    "montenegro":    VisaRequirement("Montenegro", "visa-free", 30),
    "malta":         VisaRequirement("Malta", "visa-free", 90, "Schengen area"),

    # UK
    "united kingdom":VisaRequirement("United Kingdom", "visa-free", 180,
                                      "ETA required from 2025 — apply online before travel",
                                      "https://www.gov.uk/guidance/apply-for-an-electronic-travel-authorisation-eta"),

    # Americas
    "usa":           VisaRequirement("USA", "visa-free", 90,
                                      "ESTA required — apply 72h+ before travel. $21",
                                      "https://esta.cbp.dhs.gov"),
    "united states": VisaRequirement("USA", "visa-free", 90,
                                      "ESTA required — apply 72h+ before travel. $21",
                                      "https://esta.cbp.dhs.gov"),
    "canada":        VisaRequirement("Canada", "e-visa", 180,
                                      "eTA required — CAD $7, instant approval usually",
                                      "https://www.canada.ca/en/immigration-refugees-citizenship/services/visit-canada/eta.html"),

    # Asia
    "japan":         VisaRequirement("Japan", "visa-free", 90),
    "south korea":   VisaRequirement("South Korea", "visa-free", 90),
    "thailand":      VisaRequirement("Thailand", "visa-free", 30),
    "dubai":         VisaRequirement("UAE", "visa-free", 90),
    "uae":           VisaRequirement("UAE", "visa-free", 90),
    "india":         VisaRequirement("India", "e-visa", 60,
                                      "e-Visa required. Apply 4+ days before arrival",
                                      "https://indianvisaonline.gov.in"),
    "indonesia":     VisaRequirement("Indonesia", "visa-on-arrival", 30,
                                      "VoA available at major airports — $35"),
    "vietnam":       VisaRequirement("Vietnam", "e-visa", 90,
                                      "e-Visa required. ~$25, 3 business days",
                                      "https://evisa.xuatnhapcanh.gov.vn"),

    # Middle East
    "jordan":        VisaRequirement("Jordan", "visa-on-arrival", 30,
                                      "JD 40 (~$56) at Aqaba/Airport. Wadi Rum area free"),
    "egypt":         VisaRequirement("Egypt", "visa-on-arrival", 30,
                                      "$25 at airport. Sinai-only stamp cheaper"),
    "turkey":        VisaRequirement("Turkey", "e-visa", 90,
                                      "$50 e-Visa required",
                                      "https://www.evisa.gov.tr"),

    # Note: Several Arab/Muslim-majority countries restrict Israeli passport
    "saudi arabia":  VisaRequirement("Saudi Arabia", "visa-required", None,
                                      "Israel–Saudi normalisation ongoing (2026); check current status"),
    "lebanon":       VisaRequirement("Lebanon", "visa-required", None,
                                      "Israeli passport not valid for entry"),
    "iran":          VisaRequirement("Iran", "visa-required", None,
                                      "Israeli passport not valid for entry"),
}

_CITY_TO_COUNTRY = {
    "barcelona": "spain", "madrid": "spain",
    "new york": "usa", "nyc": "usa", "los angeles": "usa",
    "london": "united kingdom",
    "paris": "france",
    "rome": "italy", "florence": "italy", "venice": "italy",
    "athens": "greece", "mykonos": "greece", "santorini": "greece",
    "amsterdam": "netherlands",
    "dubai": "uae", "abu dhabi": "uae",
    "tokyo": "japan", "osaka": "japan",
    "bangkok": "thailand", "phuket": "thailand",
    "toronto": "canada",
    "istanbul": "turkey",
    "valletta": "malta",
    "dubrovnik": "croatia", "split": "croatia",
    "kotor": "montenegro",
}


def check(destination: str) -> Optional[VisaRequirement]:
    """Look up visa requirement for Israeli passport to destination."""
    key = destination.lower().strip()
    # Try city → country mapping first
    country_key = _CITY_TO_COUNTRY.get(key, key)
    return _REQUIREMENTS.get(country_key)


def check_trip_destinations(cities: list[str]) -> list[VisaRequirement]:
    """Check all unique destinations for a trip."""
    seen = set()
    results = []
    for city in cities:
        req = check(city)
        if req and req.country not in seen:
            seen.add(req.country)
            results.append(req)
    return results


def format_visa_block(requirements: list[VisaRequirement]) -> str:
    if not requirements:
        return ""
    lines = ["🛂 *Entry requirements (Israeli passport):*\n"]
    for req in requirements:
        lines.append(req.format())
        lines.append("")
    return "\n".join(lines)
