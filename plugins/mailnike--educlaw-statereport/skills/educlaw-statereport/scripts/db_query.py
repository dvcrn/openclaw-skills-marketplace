#!/usr/bin/env python3
"""EduClaw State Reporting — db_query.py (unified router)

Routes all actions across 6 domain modules: demographics, discipline,
ed_fi, state_reporting, data_validation, submission_tracking.

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
        "error": "ERPClaw foundation not installed. Install erpclaw first: clawhub install erpclaw",
        "suggestion": "clawhub install erpclaw && clawhub install educlaw"
    }))
    sys.exit(1)

# Add this script's directory so domain modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from demographics import ACTIONS as DEMOGRAPHICS_ACTIONS
from discipline import ACTIONS as DISCIPLINE_ACTIONS
from ed_fi import ACTIONS as EDFI_ACTIONS
from state_reporting import ACTIONS as STATE_REPORTING_ACTIONS
from data_validation import ACTIONS as DATA_VALIDATION_ACTIONS
from submission_tracking import ACTIONS as SUBMISSION_TRACKING_ACTIONS

# ---------------------------------------------------------------------------
# Merge all domain actions into one router
# ---------------------------------------------------------------------------
SKILL = "educlaw-statereport"
REQUIRED_TABLES = ["company", "educlaw_student", "sr_collection_window"]

ACTIONS = {}
ACTIONS.update(DEMOGRAPHICS_ACTIONS)
ACTIONS.update(DISCIPLINE_ACTIONS)
ACTIONS.update(EDFI_ACTIONS)
ACTIONS.update(STATE_REPORTING_ACTIONS)
ACTIONS.update(DATA_VALIDATION_ACTIONS)
ACTIONS.update(SUBMISSION_TRACKING_ACTIONS)
ACTIONS["status"] = lambda conn, args: ok({
    "skill": SKILL,
    "version": "1.0.0",
    "actions_available": len([k for k in ACTIONS if k != "status"]),
    "domains": ["demographics", "discipline", "ed_fi", "state_reporting",
                "data_validation", "submission_tracking"],
    "database": DEFAULT_DB_PATH,
})


def main():
    parser = argparse.ArgumentParser(description="educlaw-statereport")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # ── Shared ────────────────────────────────────────────────────────────
    parser.add_argument("--company-id")
    parser.add_argument("--user-id")
    parser.add_argument("--search")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--offset", type=int, default=0)

    # ── Student / Demographics ─────────────────────────────────────────────
    parser.add_argument("--student-id")
    parser.add_argument("--supplement-id")
    parser.add_argument("--ssid")
    parser.add_argument("--ssid-state-code")
    parser.add_argument("--ssid-status")
    parser.add_argument("--is-hispanic-latino")
    parser.add_argument("--race-codes")           # JSON array
    parser.add_argument("--is-el")
    parser.add_argument("--el-entry-date")
    parser.add_argument("--home-language-code")
    parser.add_argument("--native-language-code")
    parser.add_argument("--english-proficiency-level")
    parser.add_argument("--english-proficiency-instrument")
    parser.add_argument("--el-exit-date")
    parser.add_argument("--is-rfep")
    parser.add_argument("--rfep-date")
    parser.add_argument("--is-sped")
    parser.add_argument("--is-504")
    parser.add_argument("--sped-entry-date")
    parser.add_argument("--sped-exit-date")
    parser.add_argument("--is-economically-disadvantaged")
    parser.add_argument("--lunch-program-status")
    parser.add_argument("--is-migrant")
    parser.add_argument("--is-homeless")
    parser.add_argument("--homeless-primary-nighttime-residence")
    parser.add_argument("--is-foster-care")
    parser.add_argument("--is-military-connected")
    parser.add_argument("--military-connection-type")
    parser.add_argument("--missing-ssid")
    parser.add_argument("--missing-race")

    # ── SPED Placement ────────────────────────────────────────────────────
    parser.add_argument("--placement-id")
    parser.add_argument("--school-year")
    parser.add_argument("--disability-category")
    parser.add_argument("--secondary-disability")
    parser.add_argument("--educational-environment")
    parser.add_argument("--sped-program-entry-date")
    parser.add_argument("--sped-program-exit-date")
    parser.add_argument("--sped-exit-reason")
    parser.add_argument("--iep-start-date")
    parser.add_argument("--iep-review-date")
    parser.add_argument("--is-transition-plan-required")
    parser.add_argument("--lre-percentage")
    parser.add_argument("--is-early-childhood")
    parser.add_argument("--early-childhood-environment")

    # ── SPED Service ──────────────────────────────────────────────────────
    parser.add_argument("--sped-placement-id")
    parser.add_argument("--service-id")
    parser.add_argument("--service-type")
    parser.add_argument("--provider-type")
    parser.add_argument("--minutes-per-week")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")

    # ── EL Program ────────────────────────────────────────────────────────
    parser.add_argument("--el-program-id")
    parser.add_argument("--program-type")
    parser.add_argument("--entry-date")
    parser.add_argument("--exit-date")
    parser.add_argument("--exit-reason")
    parser.add_argument("--english-proficiency-assessed-date")
    parser.add_argument("--proficiency-level")
    parser.add_argument("--proficiency-instrument")
    parser.add_argument("--is-parent-waived")
    parser.add_argument("--waiver-date")
    parser.add_argument("--active-only")

    # ── Discipline ────────────────────────────────────────────────────────
    parser.add_argument("--incident-id")
    parser.add_argument("--incident-date")
    parser.add_argument("--incident-time")
    parser.add_argument("--incident-type")
    parser.add_argument("--incident-description")
    parser.add_argument("--campus-location")
    parser.add_argument("--reported-by")
    parser.add_argument("--discipline-student-id")
    parser.add_argument("--role")
    parser.add_argument("--is-idea-student")
    parser.add_argument("--is-504-student")
    parser.add_argument("--action-id")
    parser.add_argument("--action-type")
    parser.add_argument("--days-removed")
    parser.add_argument("--alternative-services-provided")
    parser.add_argument("--alternative-services-description")
    parser.add_argument("--mdr-required")
    parser.add_argument("--mdr-outcome")
    parser.add_argument("--mdr-date")
    parser.add_argument("--date-from")
    parser.add_argument("--date-to")

    # ── Ed-Fi Config ──────────────────────────────────────────────────────
    parser.add_argument("--config-id")
    parser.add_argument("--profile-name")
    parser.add_argument("--state-code")
    parser.add_argument("--ods-base-url")
    parser.add_argument("--oauth-token-url")
    parser.add_argument("--oauth-client-id")
    parser.add_argument("--oauth-client-secret")
    parser.add_argument("--api-version")
    parser.add_argument("--is-active")

    # ── Org Mapping ───────────────────────────────────────────────────────
    parser.add_argument("--mapping-id")
    parser.add_argument("--nces-lea-id")
    parser.add_argument("--nces-school-id")
    parser.add_argument("--state-lea-id")
    parser.add_argument("--state-school-id")
    parser.add_argument("--edfi-lea-id")
    parser.add_argument("--edfi-school-id")
    parser.add_argument("--crdc-school-id")
    parser.add_argument("--is-title-i-school")
    parser.add_argument("--title-i-status")

    # ── Descriptor Mapping ────────────────────────────────────────────────
    parser.add_argument("--desc-id")
    parser.add_argument("--descriptor-type")
    parser.add_argument("--internal-code")
    parser.add_argument("--edfi-descriptor-uri")
    parser.add_argument("--description")
    parser.add_argument("--mappings")             # JSON array for bulk import

    # ── Ed-Fi Sync ────────────────────────────────────────────────────────
    parser.add_argument("--collection-window-id")
    parser.add_argument("--resource-type")
    parser.add_argument("--internal-id")
    parser.add_argument("--sync-status")

    # ── Collection Window ─────────────────────────────────────────────────
    parser.add_argument("--window-id")
    parser.add_argument("--name")
    parser.add_argument("--window-type")
    parser.add_argument("--window-status")
    parser.add_argument("--open-date")
    parser.add_argument("--close-date")
    parser.add_argument("--snapshot-date")
    parser.add_argument("--required-data-categories")  # JSON
    parser.add_argument("--is-federal-required")
    parser.add_argument("--edfi-config-id")
    parser.add_argument("--academic-year-id")

    # ── Snapshot ──────────────────────────────────────────────────────────
    parser.add_argument("--snapshot-id")
    parser.add_argument("--record-type")

    # ── ADA / Attendance ──────────────────────────────────────────────────
    parser.add_argument("--per-pupil-rate")
    parser.add_argument("--threshold")

    # ── Validation Rule ───────────────────────────────────────────────────
    parser.add_argument("--rule-id")
    parser.add_argument("--rule-code")
    parser.add_argument("--category")
    parser.add_argument("--severity")
    parser.add_argument("--applicable-windows")   # JSON
    parser.add_argument("--applicable-states")    # JSON
    parser.add_argument("--is-federal-rule")
    parser.add_argument("--sql-query")
    parser.add_argument("--error-message-template")

    # ── Submission Error ──────────────────────────────────────────────────
    parser.add_argument("--error-id")
    parser.add_argument("--error-ids")            # JSON array
    parser.add_argument("--error-source")
    parser.add_argument("--error-level")
    parser.add_argument("--error-code")
    parser.add_argument("--error-category")
    parser.add_argument("--error-message")
    parser.add_argument("--field-name")
    parser.add_argument("--field-value")
    parser.add_argument("--resolution-status")
    parser.add_argument("--resolution-method")
    parser.add_argument("--resolved-by")
    parser.add_argument("--resolution-notes")
    parser.add_argument("--assigned-to")
    parser.add_argument("--state-ticket-id")

    # ── Submission Tracking ───────────────────────────────────────────────
    parser.add_argument("--submission-id")
    parser.add_argument("--submission-type")
    parser.add_argument("--submission-method")
    parser.add_argument("--submission-status")
    parser.add_argument("--submitted-at")
    parser.add_argument("--submitted-by")
    parser.add_argument("--records-submitted")
    parser.add_argument("--records-accepted")
    parser.add_argument("--records-rejected")
    parser.add_argument("--state-confirmation-id")
    parser.add_argument("--state-confirmed-at")
    parser.add_argument("--amendment-reason")
    parser.add_argument("--linked-submission-id")
    parser.add_argument("--original-submission-id")
    parser.add_argument("--snapshot-status")

    # ── Certification ─────────────────────────────────────────────────────
    parser.add_argument("--certified-by")
    parser.add_argument("--certification-notes")

    args, _unknown = parser.parse_known_args()
    check_input_lengths(args)

    db_path = args.db_path or DEFAULT_DB_PATH
    ensure_db_exists(db_path)
    conn = get_connection(db_path)

    _dep = check_required_tables(conn, ["company"])
    if _dep:
        _dep["suggestion"] = "clawhub install erpclaw && clawhub install educlaw && clawhub install educlaw-statereport"
        print(json.dumps(_dep, indent=2))
        conn.close()
        sys.exit(1)

    try:
        ACTIONS[args.action](conn, args)
    except Exception as e:
        conn.rollback()
        sys.stderr.write(f"[{SKILL}] {e}\n")
        err(str(e))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
