#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def evaluate(data: dict, *, strict: bool = False) -> dict:
    risk = str(data.get("risk", "medium")).lower()
    preflight_ok = bool(data.get("preflight_ok", False))
    rollback_ready = bool(data.get("rollback_ready", False))
    health_ok = bool(data.get("health_ok", False))
    critical_path_ok = bool(data.get("critical_path_ok", False))
    hitl_confirmed = bool(data.get("hitl_confirmed", False))
    irreversible = bool(data.get("irreversible", False))

    messaging_path_changed = bool(data.get("messaging_path_changed", False))
    credentials_changed = bool(data.get("credentials_changed", False))
    billing_side_effects = bool(data.get("billing_side_effects", False))
    security_posture_reduced = bool(data.get("security_posture_reduced", False))

    blockers: list[str] = []
    gate_reasons: list[str] = []

    if not preflight_ok:
        blockers.append("preflight_not_passed")
        gate_reasons.append("Preflight checklist is not fully satisfied")
    if not rollback_ready:
        blockers.append("rollback_not_ready")
        gate_reasons.append("Rollback path is not ready")
    if not health_ok:
        blockers.append("health_checks_failed")
        gate_reasons.append("Health checks failed")
    if not critical_path_ok:
        blockers.append("critical_path_failed")
        gate_reasons.append("Critical user path validation failed")

    high_risk = risk == "high"
    high_impact = any([irreversible, messaging_path_changed, credentials_changed, billing_side_effects, security_posture_reduced])

    if high_risk and not hitl_confirmed:
        blockers.append("missing_hitl_confirmation")
        gate_reasons.append("High-risk change requires explicit HITL confirmation")

    if irreversible and high_risk and not hitl_confirmed:
        blockers.append("irreversible_change_without_hitl")
        gate_reasons.append("Irreversible high-risk change attempted without HITL")

    if high_impact and not hitl_confirmed:
        blockers.append("high_impact_change_without_hitl")
        gate_reasons.append("High-impact change requires HITL confirmation")

    hard_rollback = any(
        b in blockers
        for b in ["health_checks_failed", "critical_path_failed", "irreversible_change_without_hitl"]
    )

    if hard_rollback:
        verdict = "Rollback"
    elif blockers:
        verdict = "Conditional Go"
    else:
        verdict = "Go"

    # strict mode enforces no-Go when hard gates are violated by policy
    if strict and risk == "high" and not hitl_confirmed and verdict == "Go":
        verdict = "Conditional Go"

    score = 100
    penalties = {
        "preflight_not_passed": 20,
        "rollback_not_ready": 20,
        "health_checks_failed": 30,
        "critical_path_failed": 30,
        "missing_hitl_confirmation": 25,
        "irreversible_change_without_hitl": 40,
        "high_impact_change_without_hitl": 25,
    }
    for b in blockers:
        score -= penalties.get(b, 10)
    score = max(0, score)

    return {
        "risk": risk,
        "strict_mode": bool(strict),
        "safety_score": score,
        "verdict": verdict,
        "blockers": sorted(set(blockers)),
        "gate_reasons": gate_reasons,
        "input_summary": {
            "preflight_ok": preflight_ok,
            "rollback_ready": rollback_ready,
            "health_ok": health_ok,
            "critical_path_ok": critical_path_ok,
            "hitl_confirmed": hitl_confirmed,
            "irreversible": irreversible,
            "messaging_path_changed": messaging_path_changed,
            "credentials_changed": credentials_changed,
            "billing_side_effects": billing_side_effects,
            "security_posture_reduced": security_posture_reduced,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Deterministic change-safety gate evaluator")
    ap.add_argument("--input", required=True, help="Path to change check JSON")
    ap.add_argument("--out", default="", help="Optional output file")
    ap.add_argument("--strict", action="store_true", help="Enable strict policy gate mode")
    args = ap.parse_args()

    result = evaluate(load(args.input), strict=args.strict)
    out = json.dumps(result, ensure_ascii=False, indent=2)

    if args.out:
        Path(args.out).write_text(out + "\n", encoding="utf-8")

    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
