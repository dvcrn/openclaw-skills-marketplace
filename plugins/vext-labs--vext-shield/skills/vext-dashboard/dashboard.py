#!/usr/bin/env python3
"""VEXT Shield — Security Status Dashboard.

Aggregates data from all VEXT Shield components into a comprehensive
security posture report with scoring and grading.

Usage:
    python3 dashboard.py               # Generate dashboard
    python3 dashboard.py --output report.md
    python3 dashboard.py --json

Built by Vext Labs.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from shared.report_generator import ReportGenerator
from shared.utils import find_vext_shield_dir, score_to_grade, timestamp_str


def find_latest_report(reports_dir: Path, prefix: str) -> Path | None:
    """Find the most recent report file matching a prefix."""
    if not reports_dir.exists():
        return None
    candidates = sorted(
        [f for f in reports_dir.iterdir() if f.name.startswith(prefix) and f.suffix == ".md"],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def parse_scan_summary(report_path: Path | None) -> dict[str, Any] | None:
    """Extract summary data from a scan report."""
    if report_path is None or not report_path.exists():
        return None

    content = report_path.read_text(encoding="utf-8", errors="replace")
    summary: dict[str, Any] = {
        "last_run": datetime.fromtimestamp(
            report_path.stat().st_mtime, tz=timezone.utc
        ).strftime("%Y-%m-%d %H:%M UTC"),
        "total": 0,
        "clean": 0,
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
    }

    # Parse from markdown table
    for line in content.split("\n"):
        if "[CLEAN]" in line:
            summary["clean"] += 1
            summary["total"] += 1
        elif "[LOW]" in line:
            summary["low"] += 1
            summary["total"] += 1
        elif "[MEDIUM]" in line:
            summary["medium"] += 1
            summary["total"] += 1
        elif "[HIGH]" in line:
            summary["high"] += 1
            summary["total"] += 1
        elif "[CRITICAL]" in line:
            summary["critical"] += 1
            summary["total"] += 1

    return summary if summary["total"] > 0 else None


def parse_audit_grade(report_path: Path | None) -> dict[str, Any] | None:
    """Extract grade from an audit report."""
    if report_path is None or not report_path.exists():
        return None

    content = report_path.read_text(encoding="utf-8", errors="replace")
    result: dict[str, Any] = {
        "last_run": datetime.fromtimestamp(
            report_path.stat().st_mtime, tz=timezone.utc
        ).strftime("%Y-%m-%d %H:%M UTC"),
    }

    for line in content.split("\n"):
        if "Security Grade:" in line:
            # Parse "**Security Grade:** A (95/100)"
            parts = line.split("**Security Grade:**")
            if len(parts) > 1:
                grade_part = parts[1].strip()
                result["grade"] = grade_part.split()[0] if grade_part else "?"
                # Extract score
                if "(" in grade_part and "/" in grade_part:
                    score_str = grade_part.split("(")[1].split("/")[0]
                    try:
                        result["score"] = int(score_str)
                    except ValueError:
                        result["score"] = 0
            break

    return result if "grade" in result else None


def count_monitor_alerts(shield_dir: Path) -> dict[str, Any]:
    """Count recent monitor alerts from log file."""
    log_path = shield_dir / "monitor.log"
    if not log_path.exists():
        return {"total": 0, "critical": 0, "high": 0, "medium": 0}

    counts = {"total": 0, "critical": 0, "high": 0, "medium": 0}
    try:
        for line in log_path.read_text(encoding="utf-8", errors="replace").split("\n"):
            if not line.strip():
                continue
            counts["total"] += 1
            if "[CRITICAL]" in line:
                counts["critical"] += 1
            elif "[HIGH]" in line:
                counts["high"] += 1
            elif "[MEDIUM]" in line:
                counts["medium"] += 1
    except OSError:
        pass

    return counts


def count_firewall_violations(shield_dir: Path) -> dict[str, Any]:
    """Count firewall violations and rules."""
    result: dict[str, Any] = {"rules": 0, "violations_today": 0, "blocked": 0}

    policy_path = shield_dir / "firewall-policy.json"
    if policy_path.exists():
        try:
            data = json.loads(policy_path.read_text(encoding="utf-8"))
            result["rules"] = len(data.get("rules", []))
        except (json.JSONDecodeError, OSError):
            pass

    violations_path = shield_dir / "firewall-violations.json"
    if violations_path.exists():
        try:
            violations = json.loads(violations_path.read_text(encoding="utf-8"))
            result["blocked"] = len(violations)
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            result["violations_today"] = sum(
                1 for v in violations if v.get("timestamp", "").startswith(today)
            )
        except (json.JSONDecodeError, OSError):
            pass

    return result


def get_recent_alerts(shield_dir: Path, limit: int = 20) -> list[dict[str, str]]:
    """Get the most recent alerts from the monitor log."""
    log_path = shield_dir / "monitor.log"
    if not log_path.exists():
        return []

    alerts: list[dict[str, str]] = []
    try:
        lines = log_path.read_text(encoding="utf-8", errors="replace").strip().split("\n")
        for line in reversed(lines[-limit:]):
            if not line.strip():
                continue
            # Parse: [timestamp] [severity] [category] message
            parts = line.split("] ", 3)
            if len(parts) >= 4:
                alerts.append({
                    "time": parts[0].strip("["),
                    "severity": parts[1].strip("["),
                    "message": parts[3] if len(parts) > 3 else parts[2],
                })
            else:
                alerts.append({"time": "?", "severity": "INFO", "message": line})
    except OSError:
        pass

    return alerts


def compute_overall_score(
    scan_summary: dict[str, Any] | None,
    audit_data: dict[str, Any] | None,
    monitor_alerts: dict[str, Any],
    fw_violations: dict[str, Any],
) -> tuple[int, str]:
    """Compute overall security score from all components."""
    score = 100

    # Scan results impact (40 points max)
    if scan_summary:
        score -= scan_summary.get("critical", 0) * 15
        score -= scan_summary.get("high", 0) * 8
        score -= scan_summary.get("medium", 0) * 3
        score -= scan_summary.get("low", 0) * 1

    # Audit grade impact (25 points max)
    if audit_data:
        audit_score = audit_data.get("score", 100)
        score -= max(0, (100 - audit_score)) // 4

    # Monitor alerts impact (20 points max)
    score -= min(20, monitor_alerts.get("critical", 0) * 10 + monitor_alerts.get("high", 0) * 5)

    # Firewall violations impact (15 points max)
    score -= min(15, fw_violations.get("violations_today", 0) * 3)

    score = max(0, min(100, score))
    return score, score_to_grade(score)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="VEXT Shield — Security Status Dashboard",
    )
    parser.add_argument("--output", type=Path, help="Custom output path")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    shield_dir = find_vext_shield_dir()
    reports_dir = shield_dir / "reports"

    print("VEXT Shield — Generating security dashboard...\n")

    # Gather data from all components
    scan_report = find_latest_report(reports_dir, "scan-")
    scan_summary = parse_scan_summary(scan_report)

    audit_report = find_latest_report(reports_dir, "audit-")
    audit_data = parse_audit_grade(audit_report)

    monitor_alerts = count_monitor_alerts(shield_dir)
    fw_violations = count_firewall_violations(shield_dir)
    recent_alerts = get_recent_alerts(shield_dir)

    # Compute overall score
    score, grade = compute_overall_score(scan_summary, audit_data, monitor_alerts, fw_violations)

    # Build component status
    components: list[dict[str, Any]] = []
    components.append({
        "name": "Skill Scanner",
        "last_run": scan_summary.get("last_run", "Never") if scan_summary else "Never",
        "status": f"{scan_summary.get('critical', 0)} critical, {scan_summary.get('high', 0)} high" if scan_summary else "Not run",
        "findings_count": scan_summary.get("total", 0) if scan_summary else 0,
    })
    components.append({
        "name": "Installation Audit",
        "last_run": audit_data.get("last_run", "Never") if audit_data else "Never",
        "status": f"Grade {audit_data.get('grade', '?')}" if audit_data else "Not run",
        "findings_count": 0,
    })
    components.append({
        "name": "Runtime Monitor",
        "last_run": "Check log" if monitor_alerts.get("total", 0) > 0 else "Never",
        "status": f"{monitor_alerts.get('total', 0)} alerts" if monitor_alerts.get("total", 0) > 0 else "No alerts",
        "findings_count": monitor_alerts.get("total", 0),
    })
    components.append({
        "name": "Firewall",
        "last_run": "Active" if fw_violations.get("rules", 0) > 0 else "Not configured",
        "status": f"{fw_violations.get('rules', 0)} rules, {fw_violations.get('violations_today', 0)} violations today",
        "findings_count": fw_violations.get("violations_today", 0),
    })

    # Build dashboard data
    dashboard_data: dict[str, Any] = {
        "score": score,
        "grade": grade,
        "components": components,
        "scan_summary": scan_summary,
        "firewall_summary": fw_violations,
        "alerts": recent_alerts,
    }

    # Generate output
    if args.json:
        output = json.dumps(dashboard_data, indent=2)
    else:
        generator = ReportGenerator()
        output = generator.generate_dashboard_report(dashboard_data)

    # Save
    if args.output:
        output_path = args.output
    else:
        reports_dir.mkdir(parents=True, exist_ok=True)
        ext = ".json" if args.json else ".md"
        output_path = reports_dir / f"dashboard-{timestamp_str()}{ext}"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")

    # Print summary
    print(f"  Overall Security Grade: {grade} ({score}/100)\n")
    for c in components:
        print(f"  {c['name']:<20} {c['status']}")
    print(f"\n  Dashboard saved to: {output_path}")


if __name__ == "__main__":
    main()
