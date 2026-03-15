from __future__ import annotations

import argparse

from common import load_json, utc_now_iso, write_json
from memory_store import apply_feedback, load_memory, save_memory


def main() -> int:
    parser = argparse.ArgumentParser(description="Review feedback and update memory for future cycles.")
    parser.add_argument("--mission", default="data/mission.json", help="Mission JSON path.")
    parser.add_argument("--feedback", required=True, help="Feedback JSON path.")
    parser.add_argument("--memory", default="data/memory.json", help="Persistent memory JSON path.")
    parser.add_argument("--output", default="data/feedback_report.json", help="Feedback report JSON path.")
    args = parser.parse_args()

    mission = load_json(args.mission)
    feedback = load_json(args.feedback).get("items", [])
    memory = load_memory(args.memory)
    updated_at = utc_now_iso()
    new_memory = apply_feedback(memory, feedback, updated_at)
    save_memory(args.memory, new_memory)

    positive = [item for item in feedback if item.get("result") == "positive"]
    negative = [item for item in feedback if item.get("result") == "negative"]
    report = {
        "generated_at": updated_at,
        "mission_name": mission.get("name"),
        "positive_count": len(positive),
        "negative_count": len(negative),
        "top_success_topics": sorted(
            new_memory["successful_topics"].items(),
            key=lambda pair: pair[1],
            reverse=True,
        )[:5],
        "top_action_types": sorted(
            new_memory["successful_action_types"].items(),
            key=lambda pair: pair[1],
            reverse=True,
        )[:5],
        "high_signal_accounts": sorted(
            new_memory["high_signal_accounts"].items(),
            key=lambda pair: pair[1],
            reverse=True,
        )[:5],
        "avoid_accounts": sorted(
            new_memory["avoid_accounts"].items(),
            key=lambda pair: pair[1],
            reverse=True,
        )[:5],
        "recommendation": build_recommendation(new_memory),
    }
    output_path = write_json(args.output, report)
    print(f"Wrote feedback report to {output_path}")
    print(report["recommendation"])
    return 0


def build_recommendation(memory: dict) -> str:
    success_topics = sorted(memory["successful_topics"].items(), key=lambda pair: pair[1], reverse=True)
    high_signal_accounts = sorted(memory["high_signal_accounts"].items(), key=lambda pair: pair[1], reverse=True)
    if success_topics and high_signal_accounts:
        return (
            f"Lean harder into topics like {success_topics[0][0]} and prioritize accounts like "
            f"{high_signal_accounts[0][0]} in the next cycle."
        )
    if success_topics:
        return f"Lean harder into topics like {success_topics[0][0]} in the next cycle."
    return "Not enough feedback yet. Keep collecting reviewed outcomes."


if __name__ == "__main__":
    raise SystemExit(main())
