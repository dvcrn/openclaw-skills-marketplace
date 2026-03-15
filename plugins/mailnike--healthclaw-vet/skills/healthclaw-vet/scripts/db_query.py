#!/usr/bin/env python3
"""HealthClaw Vet — unified action router.

Usage: python3 db_query.py --action <action-name> [flags]

Routes all 12 vet actions to the vet domain module.
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

from vet import ACTIONS as VET_ACTIONS

# Merge all actions
ACTIONS = {}
ACTIONS.update(VET_ACTIONS)


def build_parser():
    parser = argparse.ArgumentParser(description="HealthClaw Vet — veterinary expansion")
    parser.add_argument("--action", required=True, help="Action to execute")

    # Common flags
    parser.add_argument("--company-id")
    parser.add_argument("--patient-id")

    # Animal patient flags
    parser.add_argument("--animal-patient-id")
    parser.add_argument("--species")
    parser.add_argument("--breed")
    parser.add_argument("--color")
    parser.add_argument("--weight-kg")
    parser.add_argument("--microchip-id")
    parser.add_argument("--spay-neuter-status")
    parser.add_argument("--reproductive-status")

    # Boarding flags
    parser.add_argument("--boarding-id")
    parser.add_argument("--check-in-date")
    parser.add_argument("--check-out-date")
    parser.add_argument("--kennel-number")
    parser.add_argument("--feeding-instructions")
    parser.add_argument("--medication-schedule")
    parser.add_argument("--special-needs")
    parser.add_argument("--daily-rate")

    # Dosing flags
    parser.add_argument("--medication-name")
    parser.add_argument("--dose-per-kg")
    parser.add_argument("--dose-unit", default="mg")
    parser.add_argument("--route")
    parser.add_argument("--frequency")
    parser.add_argument("--weight-date")

    # Owner link flags
    parser.add_argument("--owner-link-id")
    parser.add_argument("--owner-name")
    parser.add_argument("--owner-phone")
    parser.add_argument("--owner-email")
    parser.add_argument("--relationship")
    parser.add_argument("--is-primary", type=int)
    parser.add_argument("--financial-responsibility", type=int)

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
            "skill": "healthclaw-vet",
            "version": "1.0.0",
            "actions_available": len(ACTIONS),
            "tables": [
                "healthclaw_animal_patient",
                "healthclaw_boarding",
                "healthclaw_weight_dosing",
                "healthclaw_owner_link",
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
