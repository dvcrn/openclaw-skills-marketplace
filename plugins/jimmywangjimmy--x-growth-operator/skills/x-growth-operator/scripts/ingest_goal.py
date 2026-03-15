from __future__ import annotations

import argparse
from pathlib import Path

from common import normalize_text, utc_now_iso, write_json


def parse_sections(raw_text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = "summary"
    sections[current] = []

    for line in raw_text.splitlines():
        stripped = line.strip()
        lowered = stripped.lower().rstrip(":")
        if lowered in {
            "goals",
            "audience",
            "voice",
            "priority topics",
            "watch keywords",
            "watch accounts",
            "banned topics",
            "preferred cta",
            "risk tolerance",
        }:
            current = lowered
            sections.setdefault(current, [])
            continue
        if stripped.startswith("- "):
            sections.setdefault(current, []).append(stripped[2:].strip())
        elif stripped:
            sections.setdefault(current, []).append(stripped)

    return sections


def mission_from_text(raw_text: str) -> dict:
    sections = parse_sections(raw_text)
    summary = " ".join(sections.get("summary", []))
    goals = sections.get("goals", [])
    audience = sections.get("audience", [])
    voice = sections.get("voice", [])
    topics = sections.get("priority topics", [])
    keywords = sections.get("watch keywords", [])
    accounts = sections.get("watch accounts", [])
    banned = sections.get("banned topics", [])
    cta = " ".join(sections.get("preferred cta", []))
    risk_tolerance = sections.get("risk tolerance", ["medium"])[0].lower()

    headline = sections.get("summary", ["Untitled mission"])[0].lstrip("# ").strip()
    goal = goals[0] if goals else normalize_text(summary)

    mission = {
        "name": headline or "Untitled mission",
        "goal": goal or "Grow targeted X awareness",
        "account_handle": "",
        "audience": audience,
        "voice": ", ".join(voice) if voice else "direct, clear, credible",
        "primary_topics": topics,
        "watch_keywords": keywords,
        "watch_accounts": accounts,
        "banned_topics": banned,
        "cta": cta or "Invite qualified readers to learn more",
        "risk_tolerance": risk_tolerance if risk_tolerance in {"low", "medium", "high"} else "medium",
        "autonomy_mode": "review",
        "source_summary": normalize_text(summary),
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
    }
    return mission


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a mission.json from a brief or prompt.")
    parser.add_argument("--doc", help="Path to a source brief or uploaded document text export.")
    parser.add_argument("--prompt", help="Inline natural language mission prompt.")
    parser.add_argument("--mission", default="data/mission.json", help="Output mission JSON path.")
    args = parser.parse_args()

    if not args.doc and not args.prompt:
        parser.error("Provide either --doc or --prompt.")

    raw_text = args.prompt or Path(args.doc).read_text(encoding="utf-8")
    mission = mission_from_text(raw_text)
    output_path = write_json(args.mission, mission)

    print(f"Wrote mission to {output_path}")
    print(f"Mission goal: {mission['goal']}")
    print(f"Watching {len(mission['watch_accounts'])} accounts and {len(mission['watch_keywords'])} keywords")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
