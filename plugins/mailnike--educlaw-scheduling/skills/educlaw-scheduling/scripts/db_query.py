#!/usr/bin/env python3
"""EduClaw Advanced Scheduling — db_query.py (unified router)

Routes 56 actions across 4 domain modules:
  schedule_patterns (10) | master_schedule (24) |
  conflict_resolution (8) | room_assignment (14)

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout, exit 0 on success, exit 1 on error.
"""
import argparse
import json
import os
import sys

# Add shared lib to path
try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection, ensure_db_exists, DEFAULT_DB_PATH
    from erpclaw_lib.validation import check_input_lengths
    from erpclaw_lib.response import ok, err
    from erpclaw_lib.dependencies import check_required_tables
except ImportError:
    import json as _json
    print(_json.dumps({
        "status": "error",
        "error": "ERPClaw foundation not installed. Install erpclaw first.",
        "suggestion": "clawhub install erpclaw"
    }))
    sys.exit(1)

# Add this script's directory so domain modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from schedule_patterns import ACTIONS as SCHEDULE_PATTERNS_ACTIONS
from master_schedule import ACTIONS as MASTER_SCHEDULE_ACTIONS
from conflict_resolution import ACTIONS as CONFLICT_RESOLUTION_ACTIONS
from room_assignment import ACTIONS as ROOM_ASSIGNMENT_ACTIONS

# ---------------------------------------------------------------------------
# Merge all domain actions into one router
# ---------------------------------------------------------------------------
SKILL = "educlaw-scheduling"
REQUIRED_TABLES = ["company", "educlaw_schedule_pattern"]

ACTIONS = {}
ACTIONS.update(SCHEDULE_PATTERNS_ACTIONS)
ACTIONS.update(MASTER_SCHEDULE_ACTIONS)
ACTIONS.update(CONFLICT_RESOLUTION_ACTIONS)
ACTIONS.update(ROOM_ASSIGNMENT_ACTIONS)
ACTIONS["status"] = lambda conn, args: ok({
    "skill": SKILL,
    "version": "1.0.0",
    "actions_available": len([k for k in ACTIONS if k != "status"]),
    "domains": ["schedule_patterns", "master_schedule",
                "conflict_resolution", "room_assignment"],
    "database": DEFAULT_DB_PATH,
})


def main():
    parser = argparse.ArgumentParser(description="educlaw-scheduling")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # ── Shared ────────────────────────────────────────────────────────────
    parser.add_argument("--company-id")
    parser.add_argument("--user-id")
    parser.add_argument("--search")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--offset", type=int, default=0)

    # ── Schedule Pattern ──────────────────────────────────────────────────
    parser.add_argument("--pattern-id")
    parser.add_argument("--schedule-pattern-id")
    parser.add_argument("--name")
    parser.add_argument("--description")
    parser.add_argument("--notes")
    parser.add_argument("--pattern-type")          # traditional|block_4x4|block_ab|...
    parser.add_argument("--cycle-days", type=int)
    parser.add_argument("--total-periods-per-cycle", type=int)
    parser.add_argument("--is-active")

    # ── Day Type ──────────────────────────────────────────────────────────
    parser.add_argument("--day-type-id")
    parser.add_argument("--code")                  # day type code e.g. "A", "B"
    parser.add_argument("--sort-order", type=int)

    # ── Bell Period ───────────────────────────────────────────────────────
    parser.add_argument("--bell-period-id")
    parser.add_argument("--period-number")
    parser.add_argument("--period-name")
    parser.add_argument("--start-time")            # HH:MM
    parser.add_argument("--end-time")              # HH:MM
    parser.add_argument("--duration-minutes", type=int)
    parser.add_argument("--period-type")           # class|break|lunch|...
    parser.add_argument("--applies-to-day-types")  # JSON array of day_type IDs

    # ── Date Range (get-day-type-calendar / get-pattern-calendar) ─────────
    parser.add_argument("--date-range-start")      # YYYY-MM-DD
    parser.add_argument("--date-range-end")        # YYYY-MM-DD

    # ── Master Schedule ───────────────────────────────────────────────────
    parser.add_argument("--master-schedule-id")
    parser.add_argument("--academic-term-id")
    parser.add_argument("--schedule-status")       # draft|building|review|published|locked|archived
    parser.add_argument("--build-notes")
    parser.add_argument("--cloned-from-id")
    parser.add_argument("--naming-series")
    parser.add_argument("--target-academic-term-id")  # for create-schedule-clone
    parser.add_argument("--published-by")
    parser.add_argument("--locked-by")

    # ── Section Meeting ───────────────────────────────────────────────────
    parser.add_argument("--section-id")
    parser.add_argument("--section-meeting-id")
    parser.add_argument("--section-meeting-id-b")  # for update-room-swap (meeting B)
    parser.add_argument("--room-id")
    parser.add_argument("--instructor-id")
    parser.add_argument("--meeting-type")          # regular|lab|exam|field_trip|make_up
    parser.add_argument("--meeting-mode")          # in_person|hybrid|online
    parser.add_argument("--meeting-is-active")     # 0|1 (separate from --is-active for meetings)

    # ── Course Request ────────────────────────────────────────────────────
    parser.add_argument("--course-request-id")
    parser.add_argument("--student-id")
    parser.add_argument("--course-id")
    parser.add_argument("--request-priority", type=int)
    parser.add_argument("--is-alternate")
    parser.add_argument("--alternate-for-course-id")
    parser.add_argument("--request-status")        # draft|submitted|approved|scheduled|...
    parser.add_argument("--fulfilled-section-id")
    parser.add_argument("--prerequisite-override")
    parser.add_argument("--prerequisite-override-by")
    parser.add_argument("--prerequisite-override-note")
    parser.add_argument("--has-iep-flag")
    parser.add_argument("--submitted-by")
    parser.add_argument("--approved-by")
    parser.add_argument("--min-requests", type=int)  # singleton analysis threshold

    # ── Conflict Resolution ───────────────────────────────────────────────
    parser.add_argument("--conflict-id")
    parser.add_argument("--conflict-type")         # instructor_double_booking|room_double_booking|...
    parser.add_argument("--severity")              # critical|high|medium|low
    parser.add_argument("--conflict-status")       # open|resolving|resolved|accepted|superseded
    parser.add_argument("--resolution-notes")
    parser.add_argument("--resolved-by")
    parser.add_argument("--section-meeting-id-a")  # conflict meeting reference A

    # ── Room Booking ──────────────────────────────────────────────────────
    parser.add_argument("--booking-id")
    parser.add_argument("--booking-type")          # class|exam|event|maintenance|admin|other
    parser.add_argument("--booking-title")
    parser.add_argument("--booked-by")
    parser.add_argument("--booking-status")        # confirmed|tentative|cancelled
    parser.add_argument("--cancellation-reason")
    parser.add_argument("--accessibility-required")
    parser.add_argument("--target-room-id")        # for assign-room-emergency, update-room-swap

    # ── Room Search ───────────────────────────────────────────────────────
    parser.add_argument("--room-type")             # classroom|lab|auditorium|gym|library|office
    parser.add_argument("--capacity", type=int)
    parser.add_argument("--building")
    parser.add_argument("--features")             # JSON array of required facility features

    # ── Instructor Constraints ────────────────────────────────────────────
    parser.add_argument("--constraint-id")
    parser.add_argument("--constraint-type")       # unavailable|preferred|max_periods_per_day|...
    parser.add_argument("--constraint-value", type=int)
    parser.add_argument("--constraint-notes")
    parser.add_argument("--priority")             # hard|soft|preference

    # ── Credit Hours (get-contact-hours) ──────────────────────────────────
    parser.add_argument("--credit-hours")

    args, _unknown = parser.parse_known_args()
    check_input_lengths(args)

    # Map --is-active from string to int if provided for section meetings
    # (sections use --meeting-is-active to avoid collision)
    if hasattr(args, "meeting_is_active") and args.meeting_is_active is not None:
        args.is_active = args.meeting_is_active

    db_path = args.db_path or DEFAULT_DB_PATH
    ensure_db_exists(db_path)
    conn = get_connection(db_path)

    _dep = check_required_tables(conn, REQUIRED_TABLES)
    if _dep:
        _dep["suggestion"] = (
            "clawhub install erpclaw && clawhub install educlaw && "
            "clawhub install educlaw-scheduling"
        )
        print(json.dumps(_dep, indent=2))
        conn.close()
        sys.exit(1)

    try:
        ACTIONS[args.action](conn, args)
    except SystemExit:
        raise
    except Exception as e:
        conn.rollback()
        sys.stderr.write(f"[{SKILL}] {e}\n")
        err(str(e))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
