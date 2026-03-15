#!/usr/bin/env python3
"""HealthClaw Home Health — unified action router.

Usage: python3 db_query.py --action <action-name> [flags]

Routes all 12 home health actions to the homehealth domain module.
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

from homehealth import ACTIONS as HOMEHEALTH_ACTIONS

# Merge all actions
ACTIONS = {}
ACTIONS.update(HOMEHEALTH_ACTIONS)


def build_parser():
    parser = argparse.ArgumentParser(description="HealthClaw Home Health — home health expansion")
    parser.add_argument("--action", required=True, help="Action to execute")

    # Common flags
    parser.add_argument("--company-id")
    parser.add_argument("--patient-id")
    parser.add_argument("--clinician-id")

    # Home visit flags
    parser.add_argument("--home-visit-id")
    parser.add_argument("--visit-date")
    parser.add_argument("--visit-type")
    parser.add_argument("--start-time")
    parser.add_argument("--end-time")
    parser.add_argument("--travel-time-minutes", type=int)
    parser.add_argument("--mileage")
    parser.add_argument("--visit-status")

    # Care plan flags
    parser.add_argument("--care-plan-id")
    parser.add_argument("--certifying-physician-id")
    parser.add_argument("--start-of-care")
    parser.add_argument("--certification-period-start")
    parser.add_argument("--certification-period-end")
    parser.add_argument("--frequency")
    parser.add_argument("--goals")
    parser.add_argument("--plan-status")

    # OASIS assessment flags
    parser.add_argument("--assessment-type")
    parser.add_argument("--assessment-date")
    parser.add_argument("--m-items")

    # Aide assignment flags
    parser.add_argument("--aide-assignment-id")
    parser.add_argument("--aide-id")
    parser.add_argument("--assignment-start")
    parser.add_argument("--assignment-end")
    parser.add_argument("--days-of-week")
    parser.add_argument("--visit-time")
    parser.add_argument("--tasks")
    parser.add_argument("--supervisor-id")
    parser.add_argument("--supervision-due-date")

    # Common optional
    parser.add_argument("--status")
    parser.add_argument("--notes")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--offset", type=int, default=0)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    action = args.action

    if action == "status":
        ok({
            "skill": "healthclaw-homehealth",
            "version": "1.0.0",
            "actions_available": len(ACTIONS),
            "tables": [
                "healthclaw_home_visit",
                "healthclaw_care_plan",
                "healthclaw_oasis_assessment",
                "healthclaw_aide_assignment",
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
