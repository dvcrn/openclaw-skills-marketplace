"""
Packing profile — per-member base template that survives across trips.

Each member has their own packing defaults stored in:
  memory/profiles/{member_slug}/packing_template.json

At D-7 the briefing loads their template, reminds them of it,
then appends trip-specific additions (weather, kids, cruise, destination).

Members opt in by setting up their template:
  "Kai, add noise-cancelling headphones to my packing template"
  "Kai, my base packing list: ..."
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
import os

PROFILES_DIR = Path(os.environ.get("CLAWTOURISM_PROFILES_DIR",
    Path(__file__).parent.parent.parent.parent / "memory" / "profiles"))

_DEFAULT_TEMPLATE: dict[str, list[str]] = {
    "📄 Documents": [
        "Passport",
        "Booking refs (offline copy)",
        "Travel insurance",
        "Credit cards",
    ],
    "👕 Clothes": [],          # Member fills in their defaults
    "🔌 Electronics": [
        "Phone + charger",
        "Powerbank",
        "Earbuds",
    ],
    "🪥 Toiletries": [
        "Deodorant",
        "Toothbrush + toothpaste",
    ],
    "💊 Meds": [
        "Paracetamol",
        "Any prescription meds",
    ],
}


class PackingProfile:
    """Persistent packing template for one member."""

    def __init__(self, member_slug: str):
        self.member_slug = member_slug
        self._path = PROFILES_DIR / member_slug / "packing_template.json"
        self._data: dict[str, list[str]] = {}
        self._load()

    def _load(self):
        if self._path.exists():
            self._data = json.loads(self._path.read_text())
        else:
            self._data = {}

    def _save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2, ensure_ascii=False))

    @property
    def has_template(self) -> bool:
        return bool(self._data)

    def get_template(self) -> dict[str, list[str]]:
        return self._data

    def set_template(self, categories: dict[str, list[str]]):
        self._data = categories
        self._save()

    def add_item(self, category: str, item: str):
        if category not in self._data:
            self._data[category] = []
        if item not in self._data[category]:
            self._data[category].append(item)
            self._save()

    def remove_item(self, category: str, item: str):
        if category in self._data and item in self._data[category]:
            self._data[category].remove(item)
            self._save()

    def initialize_defaults(self):
        """Seed with default template — called when member first opts in."""
        self._data = {k: list(v) for k, v in _DEFAULT_TEMPLATE.items()}
        self._save()


def format_briefing(
    profile: PackingProfile,
    trip_additions: dict[str, list[str]],
    destination: str,
) -> str:
    """
    Format the D-7 packing briefing:
    - Section 1: member's saved template ("Your usual")
    - Section 2: trip-specific additions ("For {destination}")

    If no template: show full merged list.
    """
    lines = []

    if profile.has_template:
        template = profile.get_template()

        # Your usual
        lines.append("🧳 *Your usual packing list:*")
        for cat, items in template.items():
            if items:
                lines.append(f"\n*{cat}*")
                for item in items:
                    lines.append(f"  • {item}")

        # Trip-specific additions
        additions = {
            cat: [i for i in items if not _in_template(i, template)]
            for cat, items in trip_additions.items()
        }
        additions = {k: v for k, v in additions.items() if v}

        if additions:
            lines.append(f"\n➕ *For {destination} specifically:*")
            for cat, items in additions.items():
                lines.append(f"\n*{cat}*")
                for item in items:
                    lines.append(f"  • {item}")

        lines.append("\n_To update your template: \"Kai, add X to my packing template\"_")

    else:
        # No template yet — show full list and offer to save
        lines.append(f"🧳 *Packing list for {destination}:*")
        all_items = {**trip_additions}
        for cat, items in all_items.items():
            if items:
                lines.append(f"\n*{cat}*")
                for item in items:
                    lines.append(f"  • {item}")

        lines.append(
            "\n💡 _Save this as your base template for future trips: "
            "\"Kai, save this as my packing template\"_"
        )

    return "\n".join(lines)


def _in_template(item: str, template: dict[str, list[str]]) -> bool:
    item_lower = item.lower()
    for items in template.values():
        if any(item_lower in i.lower() or i.lower() in item_lower for i in items):
            return True
    return False


def get_profile(member_slug: str) -> PackingProfile:
    return PackingProfile(member_slug)
