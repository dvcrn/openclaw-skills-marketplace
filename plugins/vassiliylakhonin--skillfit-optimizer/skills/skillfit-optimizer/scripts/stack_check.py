#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def score(available: int, total: int) -> int:
    if total == 0:
        return 0
    return round((available / total) * 100)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main() -> int:
    p = argparse.ArgumentParser(description="Deterministic stack checker for SkillFit Optimizer")
    p.add_argument("--bins", nargs="+", default=[], help="Command binaries to verify")
    p.add_argument("--json", action="store_true", help="Output JSON")
    p.add_argument("--out", default="", help="Optional output file path")
    p.add_argument("--history-path", default="", help="Optional history file path")
    p.add_argument("--report-json", default="", help="Optional report JSON path")
    p.add_argument("--slo", type=int, default=80, help="Availability SLO threshold (default: 80)")
    args = p.parse_args()

    checks = []
    for b in args.bins:
        path = shutil.which(b)
        checks.append({"bin": b, "available": bool(path), "path": path})

    available = sum(1 for c in checks if c["available"])
    total = len(checks)
    availability_score = score(available, total)
    missing_bins = [c["bin"] for c in checks if not c["available"]]

    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_bins": total,
        "available_bins": available,
        "missing_bins": missing_bins,
        "availability_score": availability_score,
        "slo_threshold": int(args.slo),
        "gate": "pass" if availability_score >= int(args.slo) else "fail",
        "checks": checks,
    }

    if args.history_path:
        history_path = Path(args.history_path)
        history_path.parent.mkdir(parents=True, exist_ok=True)
        previous = load_json(history_path)
        prev_runs = previous.get("runs") if isinstance(previous, dict) else None
        prev_last = prev_runs[-1] if isinstance(prev_runs, list) and prev_runs else None

        if isinstance(prev_last, dict):
            prev_score = int(prev_last.get("availability_score", 0))
            prev_missing = set(prev_last.get("missing_bins") or [])
            curr_missing = set(missing_bins)
            result["delta"] = {
                "previous_availability_score": prev_score,
                "current_availability_score": availability_score,
                "score_delta": availability_score - prev_score,
                "resolved_missing_bins": sorted(prev_missing - curr_missing),
                "new_missing_bins": sorted(curr_missing - prev_missing),
            }

        runs = prev_runs if isinstance(prev_runs, list) else []
        runs.append(result)
        history_path.write_text(json.dumps({"runs": runs[-200:]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8")

    if args.report_json:
        report_path = Path(args.report_json)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(output + "\n", encoding="utf-8")

    if args.json or True:
        print(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
