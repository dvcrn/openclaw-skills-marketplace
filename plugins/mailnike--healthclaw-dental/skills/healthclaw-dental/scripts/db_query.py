#!/usr/bin/env python3
"""HealthClaw Dental — unified action router.

Usage: python3 db_query.py --action <action-name> [flags]

Routes all 12 dental actions to the dental domain module.
"""
import argparse
import os
import sys

# Shared library
sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
# Domain module (same directory)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from erpclaw_lib.db import get_connection
from erpclaw_lib.response import ok, err

from dental import ACTIONS as DENTAL_ACTIONS

# Merge all actions
ACTIONS = {}
ACTIONS.update(DENTAL_ACTIONS)


def build_parser():
    parser = argparse.ArgumentParser(description="HealthClaw Dental — dental expansion")
    parser.add_argument("--action", required=True, help="Action to execute")

    # Common flags
    parser.add_argument("--company-id")
    parser.add_argument("--patient-id")
    parser.add_argument("--encounter-id")
    parser.add_argument("--provider-id")

    # Tooth chart flags
    parser.add_argument("--tooth-chart-id")
    parser.add_argument("--tooth-number")
    parser.add_argument("--tooth-system", default="universal")
    parser.add_argument("--surface")
    parser.add_argument("--condition")
    parser.add_argument("--condition-detail")
    parser.add_argument("--noted-date")
    parser.add_argument("--noted-by-id")

    # Dental procedure flags
    parser.add_argument("--cdt-code")
    parser.add_argument("--cdt-description")
    parser.add_argument("--quadrant")
    parser.add_argument("--procedure-date")
    parser.add_argument("--fee")

    # Treatment plan flags
    parser.add_argument("--treatment-plan-id")
    parser.add_argument("--plan-name")
    parser.add_argument("--plan-date")
    parser.add_argument("--phases")
    parser.add_argument("--estimated-total")
    parser.add_argument("--insurance-estimate")
    parser.add_argument("--patient-estimate")

    # Perio exam flags
    parser.add_argument("--perio-exam-id")
    parser.add_argument("--exam-date")
    parser.add_argument("--measurements")
    parser.add_argument("--bleeding-sites")
    parser.add_argument("--furcation-data")
    parser.add_argument("--mobility-data")
    parser.add_argument("--recession-data")
    parser.add_argument("--plaque-score")

    # Compare perio flags
    parser.add_argument("--exam-id-1")
    parser.add_argument("--exam-id-2")

    # Common optional
    parser.add_argument("--status")
    parser.add_argument("--notes")
    parser.add_argument("--search")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--offset", type=int, default=0)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    action = args.action

    if action == "status":
        ok({
            "skill": "healthclaw-dental",
            "version": "1.0.0",
            "actions_available": len(ACTIONS),
            "tables": [
                "healthclaw_tooth_chart",
                "healthclaw_dental_procedure",
                "healthclaw_treatment_plan",
                "healthclaw_perio_exam",
            ],
            "parent": "healthclaw",
            "status": "ok",
        })
        return

    if action not in ACTIONS:
        err(f"Unknown action: {action}. Available: {', '.join(sorted(ACTIONS.keys()))}")

    conn = get_connection()
    try:
        ACTIONS[action](conn, args)
    except SystemExit:
        raise
    except Exception as e:
        err(f"Internal error in {action}: {str(e)}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
