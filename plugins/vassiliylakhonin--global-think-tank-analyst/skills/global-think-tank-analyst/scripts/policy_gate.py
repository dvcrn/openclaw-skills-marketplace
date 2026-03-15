#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_TOP = [
    "executive_summary",
    "policy_objective",
    "current_context",
    "stakeholder_map",
    "policy_options",
    "scenario_analysis",
    "risk_register",
    "implementation_pathway",
    "monitoring_framework",
    "assumptions",
    "evidence_quality",
    "confidence",
    "final_verdict",
]


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def evaluate(doc: dict) -> dict:
    missing = [k for k in REQUIRED_TOP if k not in doc]

    options_n = len(doc.get("policy_options", []) or [])
    risks_n = len(doc.get("risk_register", []) or [])
    has_why_now = bool((doc.get("executive_summary") or {}).get("why_now"))

    score = 100
    if missing:
        score -= min(50, len(missing) * 4)
    if options_n < 2:
        score -= 20
    if risks_n < 3:
        score -= 10
    if not has_why_now:
        score -= 10

    score = max(0, score)

    if score >= 85 and not missing and options_n >= 2:
        verdict = "Pass"
    elif score >= 65:
        verdict = "Conditional Pass"
    else:
        verdict = "Fail"

    return {
        "score": score,
        "verdict": verdict,
        "missing_sections": missing,
        "policy_options_count": options_n,
        "risk_count": risks_n,
        "checks": {
            "has_why_now": has_why_now,
            "has_min_options": options_n >= 2,
            "has_min_risks": risks_n >= 3,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Deterministic policy memo gate")
    ap.add_argument("--input", required=True, help="Path to policy memo JSON")
    ap.add_argument("--out", default="", help="Optional output file")
    args = ap.parse_args()

    result = evaluate(load(args.input))
    text = json.dumps(result, ensure_ascii=False, indent=2)

    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")

    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
