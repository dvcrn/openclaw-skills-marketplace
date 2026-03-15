#!/usr/bin/env python3
"""EduClaw K-12 — db_query.py (unified router)

Routes all 76 actions across 4 domain modules:
  discipline (15), health_records (20), special_education (29), grade_promotion (12)

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
        "error": "ERPClaw foundation not installed. Run: clawhub install erpclaw",
        "suggestion": "clawhub install erpclaw"
    }))
    sys.exit(1)

# Add scripts dir so domain modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from discipline import ACTIONS as DISCIPLINE_ACTIONS
from health_records import ACTIONS as HEALTH_ACTIONS
from special_education import ACTIONS as SPED_ACTIONS
from grade_promotion import ACTIONS as PROMOTION_ACTIONS

# ─────────────────────────────────────────────────────────────────────────────
# Merge all domain actions into one router
# ─────────────────────────────────────────────────────────────────────────────
SKILL = "educlaw-k12"
REQUIRED_TABLES = ["company", "educlaw_student", "educlaw_k12_discipline_incident"]

ACTIONS = {}
ACTIONS.update(DISCIPLINE_ACTIONS)
ACTIONS.update(HEALTH_ACTIONS)
ACTIONS.update(SPED_ACTIONS)
ACTIONS.update(PROMOTION_ACTIONS)
ACTIONS["status"] = lambda conn, args: ok({
    "skill": SKILL,
    "version": "1.0.0",
    "actions_available": len([k for k in ACTIONS if k != "status"]),
    "domains": ["discipline", "health_records", "special_education", "grade_promotion"],
    "database": DEFAULT_DB_PATH,
})


def main():
    parser = argparse.ArgumentParser(description="educlaw-k12")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # ── Shared ────────────────────────────────────────────────────────────
    parser.add_argument("--company-id")
    parser.add_argument("--user-id")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--date-from")
    parser.add_argument("--date-to")
    parser.add_argument("--search")
    parser.add_argument("--message")
    parser.add_argument("--notes")
    parser.add_argument("--description")
    parser.add_argument("--name")
    parser.add_argument("--days-ahead", type=int, default=30)
    parser.add_argument("--days-window", type=int, default=30)
    parser.add_argument("--dry-run", action="store_true", default=False)

    # ── Student / Academic Year ───────────────────────────────────────────
    parser.add_argument("--student-id")
    parser.add_argument("--academic-year-id")
    parser.add_argument("--academic-term-id")
    parser.add_argument("--grade-level")

    # ── Discipline: Incident ──────────────────────────────────────────────
    parser.add_argument("--incident-id")
    parser.add_argument("--incident-date")
    parser.add_argument("--incident-time")
    parser.add_argument("--location")
    parser.add_argument("--location-detail")
    parser.add_argument("--incident-type")
    parser.add_argument("--severity")
    parser.add_argument("--is-reported-to-law-enforcement")
    parser.add_argument("--is-mandatory-report")
    parser.add_argument("--mandatory-report-date")
    parser.add_argument("--mandatory-report-agency")
    parser.add_argument("--is-title-ix")
    parser.add_argument("--incident-status")
    parser.add_argument("--reviewed-by")

    # ── Discipline: Student Involvement ───────────────────────────────────
    parser.add_argument("--role")
    parser.add_argument("--is-idea-eligible")
    parser.add_argument("--discipline-student-id")

    # ── Discipline: Action ────────────────────────────────────────────────
    parser.add_argument("--action-type")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--duration-days")
    parser.add_argument("--administered-by")

    # ── Discipline: MDR ───────────────────────────────────────────────────
    parser.add_argument("--mdr-id")
    parser.add_argument("--iep-id")
    parser.add_argument("--mdr-date")
    parser.add_argument("--question-1-result")
    parser.add_argument("--question-2-result")
    parser.add_argument("--determination")
    parser.add_argument("--outcome-action")
    parser.add_argument("--fba-required")
    parser.add_argument("--bip-required")
    parser.add_argument("--fba-bip-notes")
    parser.add_argument("--parent-notified-date")
    parser.add_argument("--procedural-safeguards-sent")

    # ── Health: Profile ───────────────────────────────────────────────────
    parser.add_argument("--health-profile-id")
    parser.add_argument("--allergies")
    parser.add_argument("--chronic-conditions")
    parser.add_argument("--physician-name")
    parser.add_argument("--physician-phone")
    parser.add_argument("--physician-address")
    parser.add_argument("--health-insurance-carrier")
    parser.add_argument("--health-insurance-id")
    parser.add_argument("--blood-type")
    parser.add_argument("--height-cm")
    parser.add_argument("--weight-kg")
    parser.add_argument("--vision-screening-date")
    parser.add_argument("--hearing-screening-date")
    parser.add_argument("--dental-screening-date")
    parser.add_argument("--activity-restriction")
    parser.add_argument("--activity-restriction-notes")
    parser.add_argument("--is-provisional-immunization")
    parser.add_argument("--provisional-enrollment-end-date")
    parser.add_argument("--is-mckinney-vento")
    parser.add_argument("--emergency-instructions")
    parser.add_argument("--profile-status")
    parser.add_argument("--last-verified-date")
    parser.add_argument("--last-verified-by")

    # ── Health: Office Visit ──────────────────────────────────────────────
    parser.add_argument("--visit-id")
    parser.add_argument("--visit-date")
    parser.add_argument("--visit-time")
    parser.add_argument("--chief-complaint")
    parser.add_argument("--complaint-detail")
    parser.add_argument("--temperature")
    parser.add_argument("--pulse")
    parser.add_argument("--assessment")
    parser.add_argument("--treatment-provided")
    parser.add_argument("--disposition")
    parser.add_argument("--parent-contacted")
    parser.add_argument("--parent-contact-time")
    parser.add_argument("--parent-response")
    parser.add_argument("--is-emergency")

    # ── Health: Medication ────────────────────────────────────────────────
    parser.add_argument("--medication-id")
    parser.add_argument("--medication-name")
    parser.add_argument("--dosage")
    parser.add_argument("--route")
    parser.add_argument("--frequency")
    parser.add_argument("--administration-times")
    parser.add_argument("--prescribing-physician")
    parser.add_argument("--physician-authorization-date")
    parser.add_argument("--supply-count", type=int)
    parser.add_argument("--supply-low-threshold", type=int)
    parser.add_argument("--storage-instructions")
    parser.add_argument("--administration-instructions")
    parser.add_argument("--is-controlled-substance")
    parser.add_argument("--medication-status")

    # ── Health: Medication Log ────────────────────────────────────────────
    parser.add_argument("--student-medication-id")
    parser.add_argument("--log-date")
    parser.add_argument("--log-time")
    parser.add_argument("--dose-given")
    parser.add_argument("--student-response")
    parser.add_argument("--is-refused")
    parser.add_argument("--refusal-reason")

    # ── Health: Immunization ──────────────────────────────────────────────
    parser.add_argument("--vaccine-name")
    parser.add_argument("--cvx-code")
    parser.add_argument("--dose-number", type=int, default=1)
    parser.add_argument("--administration-date")
    parser.add_argument("--lot-number")
    parser.add_argument("--manufacturer")
    parser.add_argument("--provider-name")
    parser.add_argument("--provider-type")
    parser.add_argument("--source")
    parser.add_argument("--iis-record-id")
    parser.add_argument("--corrects-record-id")

    # ── Health: Immunization Waiver ───────────────────────────────────────
    parser.add_argument("--waiver-id")
    parser.add_argument("--waiver-type")
    parser.add_argument("--waiver-basis")
    parser.add_argument("--issuing-physician")
    parser.add_argument("--issue-date")
    parser.add_argument("--expiry-date")
    parser.add_argument("--waiver-status")

    # ── Health: Compliance ────────────────────────────────────────────────
    parser.add_argument("--approaching-deadline")

    # ── SpEd: Referral ────────────────────────────────────────────────────
    parser.add_argument("--referral-id")
    parser.add_argument("--referral-date")
    parser.add_argument("--referral-source")
    parser.add_argument("--referral-reason")
    parser.add_argument("--areas-of-concern")
    parser.add_argument("--prior-interventions")
    parser.add_argument("--referral-status")
    parser.add_argument("--consent-request-date")
    parser.add_argument("--consent-received-date")
    parser.add_argument("--consent-denied-date")
    parser.add_argument("--evaluation-deadline")

    # ── SpEd: Evaluation ──────────────────────────────────────────────────
    parser.add_argument("--evaluation-type")
    parser.add_argument("--evaluator-name")
    parser.add_argument("--evaluator-role")
    parser.add_argument("--evaluation-date")
    parser.add_argument("--instrument-used")
    parser.add_argument("--findings-summary")
    parser.add_argument("--scores")

    # ── SpEd: Eligibility ─────────────────────────────────────────────────
    parser.add_argument("--eligibility-id")
    parser.add_argument("--eligibility-meeting-date")
    parser.add_argument("--is-eligible")
    parser.add_argument("--disability-categories")
    parser.add_argument("--primary-disability")
    parser.add_argument("--adverse-educational-effect")
    parser.add_argument("--eligibility-status")
    parser.add_argument("--ineligibility-reason")
    parser.add_argument("--team-members-present")
    parser.add_argument("--parent-consent-date")

    # ── SpEd: IEP ─────────────────────────────────────────────────────────
    parser.add_argument("--iep-version", type=int, default=1)
    parser.add_argument("--is-amendment")
    parser.add_argument("--parent-iep-id")
    parser.add_argument("--iep-meeting-date")
    parser.add_argument("--iep-start-date")
    parser.add_argument("--iep-end-date")
    parser.add_argument("--annual-review-due-date")
    parser.add_argument("--triennial-reevaluation-due-date")
    parser.add_argument("--plaafp-academic")
    parser.add_argument("--plaafp-functional")
    parser.add_argument("--lre-percentage-general-ed")
    parser.add_argument("--lre-justification")
    parser.add_argument("--supplementary-aids")
    parser.add_argument("--program-modifications")
    parser.add_argument("--state-assessment-participation")
    parser.add_argument("--state-assessment-accommodations")
    parser.add_argument("--transition-plan-required")
    parser.add_argument("--transition-postsecondary-goal")
    parser.add_argument("--transition-employment-goal")
    parser.add_argument("--transition-independent-living-goal")
    parser.add_argument("--progress-report-frequency")
    parser.add_argument("--iep-status")

    # ── SpEd: IEP Goal ────────────────────────────────────────────────────
    parser.add_argument("--iep-goal-id")
    parser.add_argument("--goal-area")
    parser.add_argument("--goal-description")
    parser.add_argument("--baseline-performance")
    parser.add_argument("--target-performance")
    parser.add_argument("--measurement-method")
    parser.add_argument("--monitoring-frequency")
    parser.add_argument("--responsible-provider")
    parser.add_argument("--sort-order", type=int, default=0)

    # ── SpEd: IEP Service ─────────────────────────────────────────────────
    parser.add_argument("--iep-service-id")
    parser.add_argument("--service-type")
    parser.add_argument("--service-setting")
    parser.add_argument("--frequency-minutes-per-week", type=int, default=0)
    parser.add_argument("--provider-role")

    # ── SpEd: IEP Service Log ─────────────────────────────────────────────
    parser.add_argument("--session-date")
    parser.add_argument("--minutes-delivered", type=int, default=0)
    parser.add_argument("--session-notes")
    parser.add_argument("--is-makeup-session")
    parser.add_argument("--was-session-missed")
    parser.add_argument("--missed-reason")

    # ── SpEd: IEP Team Member ─────────────────────────────────────────────
    parser.add_argument("--member-type")
    parser.add_argument("--member-name")
    parser.add_argument("--member-role")
    parser.add_argument("--guardian-id")
    parser.add_argument("--instructor-id")
    parser.add_argument("--attended-meeting")
    parser.add_argument("--excused-absence")
    parser.add_argument("--excusal-notes")
    parser.add_argument("--signature-date")

    # ── SpEd: IEP Progress ────────────────────────────────────────────────
    parser.add_argument("--reporting-period")
    parser.add_argument("--progress-date")
    parser.add_argument("--progress-rating")
    parser.add_argument("--current-performance")
    parser.add_argument("--evidence")
    parser.add_argument("--notes-for-parents")
    parser.add_argument("--documented-by")

    # ── SpEd: 504 Plan ────────────────────────────────────────────────────
    parser.add_argument("--plan-504-id")
    parser.add_argument("--plan-id")
    parser.add_argument("--meeting-date")
    parser.add_argument("--disability-description")
    parser.add_argument("--eligibility-basis")
    parser.add_argument("--plan-start-date")
    parser.add_argument("--plan-end-date")
    parser.add_argument("--review-date")
    parser.add_argument("--accommodations")
    parser.add_argument("--team-members-json")
    parser.add_argument("--plan-status")

    # ── Grade Promotion: Review ───────────────────────────────────────────
    parser.add_argument("--review-id")
    parser.add_argument("--gpa-ytd")
    parser.add_argument("--attendance-rate-ytd")
    parser.add_argument("--failing-subjects")
    parser.add_argument("--discipline-incident-count", type=int)
    parser.add_argument("--teacher-recommendation")
    parser.add_argument("--teacher-rationale")
    parser.add_argument("--counselor-recommendation")
    parser.add_argument("--counselor-notes")
    parser.add_argument("--prior-retention-count", type=int, default=0)
    parser.add_argument("--interventions-tried")
    parser.add_argument("--review-status")
    # --is-idea-eligible already defined in Discipline: Student Involvement section

    # ── Grade Promotion: Decision ─────────────────────────────────────────
    parser.add_argument("--decision-id")
    parser.add_argument("--promotion-review-id")
    parser.add_argument("--decision")
    parser.add_argument("--decision-date")
    parser.add_argument("--decided-by")
    parser.add_argument("--rationale")
    parser.add_argument("--conditions")
    parser.add_argument("--parent-notified-by")
    parser.add_argument("--notification-method")
    parser.add_argument("--appeal-deadline")
    parser.add_argument("--next-grade-level")

    # ── Grade Promotion: Intervention Plan ────────────────────────────────
    parser.add_argument("--intervention-plan-id")
    parser.add_argument("--trigger")
    parser.add_argument("--intervention-types")
    parser.add_argument("--academic-targets")
    parser.add_argument("--attendance-target")
    parser.add_argument("--assigned-staff")
    parser.add_argument("--parent-notification-date")
    parser.add_argument("--outcome-notes")
    parser.add_argument("--promotion-review-id-optional", dest="promotion_review_id_optional")

    # ── Grade Promotion: At-risk ──────────────────────────────────────────
    parser.add_argument("--gpa-threshold")
    parser.add_argument("--attendance-threshold")

    args, _unknown = parser.parse_known_args()
    check_input_lengths(args)

    db_path = getattr(args, "db_path", None) or DEFAULT_DB_PATH
    ensure_db_exists(db_path)
    conn = get_connection(db_path)

    _dep = check_required_tables(conn, REQUIRED_TABLES)
    if _dep:
        _dep["suggestion"] = (
            "clawhub install erpclaw && "
            "clawhub install educlaw && "
            "python3 init_db.py"
        )
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
