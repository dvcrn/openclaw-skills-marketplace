#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

DIMENSIONS = ["correctness", "relevance", "actionability", "risk", "tool_reliability"]


def load(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def mean(vals: list[float]) -> float:
    return round(sum(vals) / len(vals), 2) if vals else 0.0


def thresholds_for_risk(risk: str) -> tuple[float, float, float]:
    key = (risk or "medium").lower()
    if key == "low":
        return 3.6, 3.0, 3.5
    if key == "high":
        return 4.3, 4.0, 4.2
    return 4.0, 3.6, 3.8


def evaluate(cases: list[dict], *, risk: str, strict: bool, synthetic: bool) -> dict:
    if not cases:
        return {
            "total_cases": 0,
            "dimension_averages": {d: 0.0 for d in DIMENSIONS},
            "overall_score": 0.0,
            "critical_min_score": 0.0,
            "tool_reliability_avg": 0.0,
            "verdict": "No-Go",
            "gate_reasons": ["No evaluation cases provided"],
            "failure_clusters": {},
            "by_task_type": {},
            "by_risk_level": {},
            "deltas": {},
        }

    by_dim: dict[str, list[float]] = {d: [] for d in DIMENSIONS}
    by_task = defaultdict(lambda: {"count": 0, "scores": []})
    by_risk = defaultdict(lambda: {"count": 0, "scores": []})
    cluster_counts = Counter()

    critical_cases = []
    for c in cases:
        scores = c.get("scores", {})
        normalized_scores = {}
        for d in DIMENSIONS:
            v = float(scores.get(d, 0))
            if v < 1:
                v = 1
            if v > 5:
                v = 5
            by_dim[d].append(v)
            normalized_scores[d] = v

        task = str(c.get("task_type") or "unknown").lower()
        level = str(c.get("risk_level") or "low").lower()
        cluster = str(c.get("failure_cluster") or "").strip()

        case_mean = mean(list(normalized_scores.values()))
        by_task[task]["count"] += 1
        by_task[task]["scores"].append(case_mean)
        by_risk[level]["count"] += 1
        by_risk[level]["scores"].append(case_mean)

        if level == "high":
            critical_cases.append(normalized_scores)

        if cluster:
            cluster_counts[cluster] += 1

    dim_avg = {d: mean(v) for d, v in by_dim.items()}
    overall = mean(list(dim_avg.values()))
    tool_rel = dim_avg.get("tool_reliability", 0.0)

    critical_min = 5.0
    if critical_cases:
        critical_min = round(min(min(case[d] for d in DIMENSIONS) for case in critical_cases), 2)

    overall_th, critical_th, tool_th = thresholds_for_risk(risk)
    gate_reasons = []
    if overall < overall_th:
        gate_reasons.append(f"overall_score {overall} < threshold {overall_th}")
    if critical_min < critical_th:
        gate_reasons.append(f"critical_min_score {critical_min} < threshold {critical_th}")
    if tool_rel < tool_th:
        gate_reasons.append(f"tool_reliability_avg {tool_rel} < threshold {tool_th}")
    if synthetic and (risk or "medium").lower() == "high":
        gate_reasons.append("synthetic-only evidence is not enough for high-risk Go")

    if critical_min < critical_th:
        verdict = "No-Go"
    elif gate_reasons:
        verdict = "Conditional Go"
    else:
        verdict = "Go"

    if strict and verdict == "Go":
        pass

    by_task_summary = {k: round(mean(v["scores"]), 2) for k, v in by_task.items()}
    by_risk_summary = {k: round(mean(v["scores"]), 2) for k, v in by_risk.items()}

    return {
        "total_cases": len(cases),
        "risk_level": (risk or "medium").lower(),
        "synthetic": bool(synthetic),
        "thresholds": {
            "overall_score": overall_th,
            "critical_min_score": critical_th,
            "tool_reliability_avg": tool_th,
        },
        "dimension_averages": dim_avg,
        "overall_score": overall,
        "critical_min_score": critical_min,
        "tool_reliability_avg": tool_rel,
        "by_task_type": by_task_summary,
        "by_risk_level": by_risk_summary,
        "failure_clusters": dict(cluster_counts),
        "verdict": verdict,
        "gate_reasons": gate_reasons,
        "deltas": {
            "overall_delta": 0.0,
            "critical_delta": 0.0,
            "tool_reliability_delta": 0.0,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Deterministic scorer for Agent Evals Lab")
    ap.add_argument("--input", required=True, help="Path to evaluation cases JSON")
    ap.add_argument("--out", default="", help="Optional output file path")
    ap.add_argument("--risk", default="medium", choices=["low", "medium", "high"], help="Risk profile")
    ap.add_argument("--strict", action="store_true", help="Enable strict deterministic gate mode")
    ap.add_argument("--synthetic", action="store_true", help="Mark evaluation as synthetic")
    args = ap.parse_args()

    data = load(args.input)
    cases = data.get("cases", data if isinstance(data, list) else [])
    result = evaluate(cases, risk=args.risk, strict=args.strict, synthetic=args.synthetic)

    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
