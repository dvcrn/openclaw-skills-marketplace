#!/usr/bin/env python3
"""
Guardian Daily Digest Script
-----------------------------
Generates and outputs the daily security digest for delivery
to the agent's primary channel via OpenClaw message infrastructure.

When run via OpenClaw cron with message delivery enabled, the stdout
will be automatically sent to the configured channel.

Usage (in crontab):
  0 9 * * * openclaw run "python3 skills/guardian/scripts/daily_digest.py" --deliver-to=agent
  
Or as a standalone script for testing:
  python3 scripts/daily_digest.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def skill_root() -> Path:
    """Return the Guardian skill root."""
    return Path(__file__).resolve().parents[1]


# Shared config loader (prefers OpenClaw config → guardian config.json)
sys.path.insert(0, str(skill_root()))
sys.path.insert(0, str(skill_root() / "core"))
from settings import load_config  # type: ignore  # noqa: E402


def _load_config_audit() -> Dict[str, Any]:
    """Load current config audit payload used by dashboard panel."""
    try:
        from scripts.serve import build_config_audit_payload  # type: ignore

        return build_config_audit_payload()
    except Exception:
        return {"score": None, "grade": "?", "issues": []}


def _find_top_critical_issue(issues: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Return the highest-priority critical issue if present."""
    for issue in issues:
        if str(issue.get("severity", "")).lower() == "critical":
            return issue
    return None


def _format_config_health_section(config_audit: Dict[str, Any]) -> str:
    """Format config health digest section."""
    score = config_audit.get("score")
    grade = config_audit.get("grade") or "?"
    issues = config_audit.get("issues") or []

    score_text = f"{score}/100" if isinstance(score, int) else "unknown"
    lines = [
        "",
        "**Config Health:**",
        f"  • Score: {score_text} ({grade})",
    ]

    top_critical = _find_top_critical_issue(issues)
    if top_critical:
        title = str(top_critical.get("title", "Critical issue detected")).strip()
        desc = str(top_critical.get("description", "")).strip()
        fix = str(top_critical.get("fix", "")).strip()
        lines.append(f"  • Top critical: 🔴 {title}")
        if desc:
            lines.append(f"    {desc}")
        if fix:
            lines.append(f"    Fix: `{fix}`")
    else:
        lines.append("  • Top critical: ✅ None")

    return "\n".join(lines)


def main() -> int:
    """Generate and output the daily digest."""
    cfg = load_config()

    # Check if daily digest is enabled
    if not cfg.get("alerts", {}).get("daily_digest", True):
        # Digest disabled in config — exit silently
        return 0

    # Check if Guardian is enabled
    if not cfg.get("enabled", True):
        # Guardian disabled — skip digest
        return 0

    # Generate the report using admin.py
    admin_script = skill_root() / "scripts" / "admin.py"
    try:
        result = subprocess.run(
            [sys.executable, str(admin_script), "report", "--deliver"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        if result.returncode != 0:
            sys.stderr.write(f"Report generation failed: {result.stderr}\n")
            return 1

        report_text = result.stdout.strip()
        if not report_text:
            sys.stderr.write("Report generated but was empty\n")
            return 1

        config_audit = _load_config_audit()
        digest_text = report_text + _format_config_health_section(config_audit)

        # Output the report to stdout (will be delivered by OpenClaw infrastructure)
        print(digest_text)
        return 0

    except subprocess.TimeoutExpired:
        sys.stderr.write("Report generation timed out\n")
        return 1
    except Exception as e:
        sys.stderr.write(f"Unexpected error: {e}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
