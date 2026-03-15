#!/usr/bin/env python3
"""HealthClaw Mental — unified action router.

Usage: python3 db_query.py --action <action-name> [flags]

Routes all 14 mental health actions to the mental domain module.
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

from mental import ACTIONS as MENTAL_ACTIONS

# Merge all actions
ACTIONS = {}
ACTIONS.update(MENTAL_ACTIONS)


def build_parser():
    parser = argparse.ArgumentParser(description="HealthClaw Mental — mental health expansion")
    parser.add_argument("--action", required=True, help="Action to execute")

    # Common flags
    parser.add_argument("--company-id")
    parser.add_argument("--patient-id")
    parser.add_argument("--encounter-id")
    parser.add_argument("--provider-id")

    # Therapy session flags
    parser.add_argument("--therapy-session-id")
    parser.add_argument("--session-type")
    parser.add_argument("--modality")
    parser.add_argument("--duration-minutes", type=int)
    parser.add_argument("--session-number", type=int)

    # Assessment flags
    parser.add_argument("--assessment-id")
    parser.add_argument("--instrument")
    parser.add_argument("--responses")
    parser.add_argument("--score", type=int)
    parser.add_argument("--severity")
    parser.add_argument("--administered-date")
    parser.add_argument("--administered-by-id")

    # Compare assessment flags
    parser.add_argument("--assessment-id-1")
    parser.add_argument("--assessment-id-2")

    # Treatment goal flags
    parser.add_argument("--treatment-goal-id")
    parser.add_argument("--goal-description")
    parser.add_argument("--target-date")
    parser.add_argument("--baseline-measure")
    parser.add_argument("--current-measure")
    parser.add_argument("--goal-status")

    # Group session flags
    parser.add_argument("--group-session-id")
    parser.add_argument("--session-date")
    parser.add_argument("--group-name")
    parser.add_argument("--group-type")
    parser.add_argument("--topic")
    parser.add_argument("--max-participants", type=int, default=12)
    parser.add_argument("--participant-ids")

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
            "skill": "healthclaw-mental",
            "version": "1.0.0",
            "actions_available": len(ACTIONS),
            "tables": [
                "healthclaw_therapy_session",
                "healthclaw_assessment",
                "healthclaw_treatment_goal",
                "healthclaw_group_session",
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
