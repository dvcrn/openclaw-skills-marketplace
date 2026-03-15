from __future__ import annotations

import argparse
from typing import Any

from common import load_json, utc_now_iso, write_json


def rank_actions(mission: dict[str, Any], opportunities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = []
    for item in opportunities:
        action = item.get("recommended_action", "observe")
        priority = "high" if item.get("score", 0) >= 70 else "medium" if item.get("score", 0) >= 45 else "low"
        if action == "observe":
            continue

        plan.append({
            "opportunity_id": item.get("id"),
            "priority": priority,
            "action_type": action,
            "target_account": item.get("source_account"),
            "target_url": item.get("url"),
            "score": item.get("score"),
            "risk_level": item.get("risk_level"),
            "why_now": "; ".join(item.get("reasons", [])[:3]),
            "cta": mission.get("cta", ""),
        })

    priority_order = {"high": 0, "medium": 1, "low": 2}
    return sorted(plan, key=lambda item: (priority_order[item["priority"]], -item["score"]))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a ranked action plan from scored X opportunities.")
    parser.add_argument("--mission", default="data/mission.json", help="Mission JSON path.")
    parser.add_argument("--opportunities", default="data/opportunities_scored.json", help="Scored opportunities JSON path.")
    parser.add_argument("--output", default="data/action_plan.json", help="Output action plan JSON path.")
    parser.add_argument("--top", type=int, default=5, help="Maximum planned actions.")
    args = parser.parse_args()

    mission = load_json(args.mission)
    opportunities = load_json(args.opportunities).get("items", [])
    plan_items = rank_actions(mission, opportunities)[: args.top]

    payload = {
        "generated_at": utc_now_iso(),
        "mission_name": mission.get("name"),
        "count": len(plan_items),
        "items": plan_items,
    }
    output_path = write_json(args.output, payload)
    print(f"Wrote {len(plan_items)} planned actions to {output_path}")
    for item in plan_items:
        print(f"- {item['priority']} {item['action_type']} for {item['target_account']} score={item['score']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
