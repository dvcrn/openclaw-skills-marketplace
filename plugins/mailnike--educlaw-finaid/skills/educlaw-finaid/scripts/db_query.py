#!/usr/bin/env python3
"""EduClaw Financial Aid — db_query.py (unified router)

Routes all actions across 4 domain modules: financial_aid, scholarships, work_study, loan_tracking.

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

from financial_aid import ACTIONS as FINANCIAL_AID_ACTIONS
from scholarships import ACTIONS as SCHOLARSHIPS_ACTIONS
from work_study import ACTIONS as WORK_STUDY_ACTIONS
from loan_tracking import ACTIONS as LOAN_TRACKING_ACTIONS

# ---------------------------------------------------------------------------
# Merge all domain actions into one router
# ---------------------------------------------------------------------------
SKILL = "educlaw-finaid"
REQUIRED_TABLES = ["company", "finaid_aid_year"]

ACTIONS = {}
ACTIONS.update(FINANCIAL_AID_ACTIONS)
ACTIONS.update(SCHOLARSHIPS_ACTIONS)
ACTIONS.update(WORK_STUDY_ACTIONS)
ACTIONS.update(LOAN_TRACKING_ACTIONS)
ACTIONS["status"] = lambda conn, args: ok({
    "skill": SKILL,
    "version": "1.0.0",
    "actions_available": len([k for k in ACTIONS if k != "status"]),
    "domains": ["financial_aid", "scholarships", "work_study", "loan_tracking"],
    "database": DEFAULT_DB_PATH,
})


def main():
    parser = argparse.ArgumentParser(description="educlaw-finaid")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # -- Shared IDs --
    parser.add_argument("--company-id")
    parser.add_argument("--id")
    parser.add_argument("--student-id")
    parser.add_argument("--aid-year-id")
    parser.add_argument("--academic-term-id")

    # -- financial_aid: aid year --
    parser.add_argument("--aid-year-code")
    parser.add_argument("--description")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--pell-max-award")
    parser.add_argument("--is-active", type=int)

    # -- financial_aid: pell schedule --
    parser.add_argument("--rows")  # JSON array
    parser.add_argument("--pell-index", type=int)
    parser.add_argument("--full-time-annual")
    parser.add_argument("--three-quarter-time")
    parser.add_argument("--half-time")
    parser.add_argument("--less-than-half-time")

    # -- financial_aid: fund allocation --
    parser.add_argument("--fund-type")
    parser.add_argument("--fund-name")
    parser.add_argument("--total-allocation")
    parser.add_argument("--committed-amount")

    # -- financial_aid: COA --
    parser.add_argument("--enrollment-status")
    parser.add_argument("--living-arrangement")
    parser.add_argument("--tuition-fees")
    parser.add_argument("--books-supplies")
    parser.add_argument("--room-board")
    parser.add_argument("--transportation")
    parser.add_argument("--personal-expenses")
    parser.add_argument("--loan-fees")
    parser.add_argument("--program-id")

    # -- financial_aid: ISIR --
    parser.add_argument("--sai")
    parser.add_argument("--receipt-date")
    parser.add_argument("--dependency-status")
    parser.add_argument("--pell-index-isir")
    parser.add_argument("--verification-flag", type=int)
    parser.add_argument("--verification-group")
    parser.add_argument("--transaction-number", type=int, default=1)
    parser.add_argument("--fafsa-submission-id")
    parser.add_argument("--nslds-default-flag", type=int)
    parser.add_argument("--nslds-overpayment-flag", type=int)
    parser.add_argument("--selective-service-flag", type=int)
    parser.add_argument("--citizenship-flag", type=int)
    parser.add_argument("--agi")
    parser.add_argument("--household-size", type=int)
    parser.add_argument("--family-members-in-college", type=int)
    parser.add_argument("--raw-isir-data")
    parser.add_argument("--reviewed-by")
    parser.add_argument("--is-active-transaction", type=int)

    # -- financial_aid: c-flag --
    parser.add_argument("--isir-id")
    parser.add_argument("--cflag-code")
    parser.add_argument("--cflag-description")
    parser.add_argument("--blocks-disbursement", type=int)
    parser.add_argument("--resolution-status")
    parser.add_argument("--resolution-date")
    parser.add_argument("--resolved-by")
    parser.add_argument("--resolution-notes")

    # -- financial_aid: verification --
    parser.add_argument("--verification-request-id")
    parser.add_argument("--deadline-date")
    parser.add_argument("--requested-date")
    parser.add_argument("--completed-date")
    parser.add_argument("--assigned-to")
    parser.add_argument("--document-type")
    parser.add_argument("--document-description")
    parser.add_argument("--is-required", type=int)
    parser.add_argument("--submission-status")
    parser.add_argument("--submitted-date")
    parser.add_argument("--reviewed-date")
    parser.add_argument("--rejection-reason")
    parser.add_argument("--document-reference")

    # -- financial_aid: award package --
    parser.add_argument("--program-enrollment-id")
    parser.add_argument("--isir-id-pkg", dest="isir_id")
    parser.add_argument("--cost-of-attendance-id")
    parser.add_argument("--financial-need")
    parser.add_argument("--acceptance-deadline")
    parser.add_argument("--packaged-by")
    parser.add_argument("--approved-by")
    parser.add_argument("--approved-at")
    parser.add_argument("--notes")
    parser.add_argument("--offered-date")
    parser.add_argument("--accepted-date")

    # -- financial_aid: award --
    parser.add_argument("--award-package-id")
    parser.add_argument("--aid-type")
    parser.add_argument("--aid-source")
    parser.add_argument("--fund-source-id")
    parser.add_argument("--offered-amount")
    parser.add_argument("--accepted-amount")
    parser.add_argument("--gl-account-id")
    parser.add_argument("--acceptance-status")
    parser.add_argument("--acceptance-date")
    parser.add_argument("--award-id")

    # -- financial_aid: disbursement --
    parser.add_argument("--amount")
    parser.add_argument("--disbursement-date")
    parser.add_argument("--disbursement-type")
    parser.add_argument("--disbursement-number", type=int)
    parser.add_argument("--cod-status")
    parser.add_argument("--cod-response-date")
    parser.add_argument("--is-credit-balance", type=int)
    parser.add_argument("--disbursed-by")
    parser.add_argument("--r2t4-id")
    parser.add_argument("--return-date")
    parser.add_argument("--original-disbursement-id")

    # -- financial_aid: SAP --
    parser.add_argument("--gpa-earned")
    parser.add_argument("--gpa-threshold")
    parser.add_argument("--credits-attempted")
    parser.add_argument("--credits-completed")
    parser.add_argument("--completion-threshold")
    parser.add_argument("--max-timeframe-credits")
    parser.add_argument("--projected-credits-remaining")
    parser.add_argument("--transfer-credits-attempted")
    parser.add_argument("--transfer-credits-completed")
    parser.add_argument("--sap-status")
    parser.add_argument("--evaluation-type")
    parser.add_argument("--evaluation-date")
    parser.add_argument("--evaluated-by")
    parser.add_argument("--sap-evaluation-id")

    # -- financial_aid: SAP appeal --
    parser.add_argument("--appeal-reason")
    parser.add_argument("--reason-narrative")
    parser.add_argument("--academic-plan")
    parser.add_argument("--supporting-documents")
    parser.add_argument("--probation-term-id")
    parser.add_argument("--probation-conditions")
    parser.add_argument("--decision-rationale")
    parser.add_argument("--reviewed-date-appeal", dest="reviewed_date_appeal")

    # -- financial_aid: R2T4 --
    parser.add_argument("--withdrawal-type")
    parser.add_argument("--withdrawal-date")
    parser.add_argument("--last-date-of-attendance")
    parser.add_argument("--determination-date")
    parser.add_argument("--payment-period-start")
    parser.add_argument("--payment-period-end")
    parser.add_argument("--payment-period-days", type=int)
    parser.add_argument("--institution-return-date")
    parser.add_argument("--calculated-by")
    parser.add_argument("--r2t4-status")

    # -- financial_aid: professional judgment --
    parser.add_argument("--pj-type")
    parser.add_argument("--pj-reason")
    parser.add_argument("--data-element-changed")
    parser.add_argument("--original-value")
    parser.add_argument("--adjusted-value")
    parser.add_argument("--effective-date")
    parser.add_argument("--authorized-by")
    parser.add_argument("--authorization-date")
    parser.add_argument("--supervisor-review-required", type=int)
    parser.add_argument("--supervisor-reviewed-by")
    parser.add_argument("--supervisor-review-date")

    # -- scholarships --
    parser.add_argument("--scholarship-program-id")
    parser.add_argument("--scholarship-application-id")
    parser.add_argument("--name")
    parser.add_argument("--code")
    parser.add_argument("--scholarship-type")
    parser.add_argument("--funding-source")
    parser.add_argument("--award-method")
    parser.add_argument("--award-amount-type")
    parser.add_argument("--award-amount")
    parser.add_argument("--min-award")
    parser.add_argument("--max-award")
    parser.add_argument("--annual-budget")
    parser.add_argument("--max-recipients", type=int)
    parser.add_argument("--renewal-eligible", type=int)
    parser.add_argument("--renewal-gpa-minimum")
    parser.add_argument("--renewal-credits-minimum")
    parser.add_argument("--eligibility-criteria")
    parser.add_argument("--application-deadline")
    parser.add_argument("--award-period")
    parser.add_argument("--applies-to-aid-type")
    parser.add_argument("--essay-response")
    parser.add_argument("--gpa-at-application")
    parser.add_argument("--reviewer-id")
    parser.add_argument("--review-notes")
    parser.add_argument("--denial-reason")
    parser.add_argument("--award-term-id")
    parser.add_argument("--gpa-at-evaluation")
    parser.add_argument("--renewal-status")

    # -- work_study --
    parser.add_argument("--job-id")
    parser.add_argument("--job-title")
    parser.add_argument("--department-id")
    parser.add_argument("--supervisor-id")
    parser.add_argument("--job-type")
    parser.add_argument("--pay-rate")
    parser.add_argument("--hours-per-week")
    parser.add_argument("--total-positions", type=int)
    parser.add_argument("--assignment-id")
    parser.add_argument("--award-limit")
    parser.add_argument("--pay-period-start")
    parser.add_argument("--pay-period-end")
    parser.add_argument("--hours-worked")
    parser.add_argument("--supervisor-approved-by")
    parser.add_argument("--timesheet-id")

    # -- loan_tracking --
    parser.add_argument("--loan-type")
    parser.add_argument("--loan-period-start")
    parser.add_argument("--loan-period-end")
    parser.add_argument("--loan-amount")
    parser.add_argument("--first-disbursement-amount")
    parser.add_argument("--second-disbursement-amount")
    parser.add_argument("--origination-fee")
    parser.add_argument("--interest-rate")
    parser.add_argument("--cod-loan-id")
    parser.add_argument("--cod-origination-status")
    parser.add_argument("--cod-origination-date")
    parser.add_argument("--mpn-signed-date")
    parser.add_argument("--entrance-counseling-required", type=int)
    parser.add_argument("--entrance-counseling-date")
    parser.add_argument("--exit-counseling-date")
    parser.add_argument("--exit-counseling-required", type=int)
    parser.add_argument("--borrower-id")
    parser.add_argument("--borrower-type")
    parser.add_argument("--loan-status")

    # -- Shared --
    parser.add_argument("--search")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--status")

    args, _unknown = parser.parse_known_args()
    check_input_lengths(args)

    db_path = args.db_path or DEFAULT_DB_PATH
    ensure_db_exists(db_path)
    conn = get_connection(db_path)

    _dep = check_required_tables(conn, REQUIRED_TABLES)
    if _dep:
        _dep["suggestion"] = "clawhub install erpclaw && clawhub install educlaw-finaid"
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
