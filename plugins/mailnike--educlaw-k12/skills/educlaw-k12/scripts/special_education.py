"""EduClaw K-12 — special_education domain module

Actions: create-sped-referral, update-sped-referral, get-sped-referral,
list-sped-referrals, add-sped-evaluation, list-sped-evaluations,
record-sped-eligibility, get-sped-eligibility, add-iep, update-iep,
activate-iep, add-iep-amendment, get-active-iep, get-iep, list-iep-deadlines,
list-reevaluation-due, add-iep-goal, list-iep-goals, add-iep-service,
list-iep-services, record-iep-service-session, list-iep-service-logs,
get-service-compliance-report, add-iep-team-member, record-iep-progress,
generate-iep-progress-report, add-504-plan, update-504-plan, get-active-504-plan

Imported by scripts/db_query.py.
"""
import json
import os
import sys
import uuid
from datetime import datetime, date, timezone, timedelta

sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
from erpclaw_lib.db import get_connection
from erpclaw_lib.decimal_utils import to_decimal
from erpclaw_lib.naming import get_next_name
from erpclaw_lib.response import ok, err, row_to_dict, rows_to_list
from erpclaw_lib.audit import audit
from erpclaw_lib.query_helpers import resolve_company_id

SKILL = "educlaw-k12"

_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _log_ferpa(conn, user_id, student_id, data_category, company_id,
               access_type="view", access_reason=""):
    """Insert FERPA data access log (silently ignores failures)."""
    try:
        conn.execute(
            """INSERT INTO educlaw_data_access_log
               (id, user_id, student_id, data_category, access_type, access_reason,
                is_emergency_access, ip_address, company_id, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, 0, '', ?, ?, ?)""",
            (str(uuid.uuid4()), user_id or "", student_id, data_category,
             access_type, access_reason, company_id, _now_iso(), user_id or "")
        )
    except Exception:
        pass


def _parse_json(value, default=None):
    if value is None:
        return default if default is not None else []
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return default if default is not None else []


def _add_calendar_days(date_str, days):
    """Add calendar days to an ISO date string. Returns empty string on error."""
    try:
        d = date.fromisoformat(date_str)
        return (d + timedelta(days=days)).isoformat()
    except Exception:
        return ""


def _student_age_at(student_id, ref_date_str, conn):
    """Calculate student age at a given date. Returns 0 on error."""
    try:
        row = conn.execute(
            "SELECT date_of_birth FROM educlaw_student WHERE id = ?", (student_id,)
        ).fetchone()
        if not row or not row["date_of_birth"]:
            return 0
        dob = date.fromisoformat(row["date_of_birth"])
        ref = date.fromisoformat(ref_date_str) if ref_date_str else date.today()
        return (ref - dob).days // 365
    except Exception:
        return 0




# ─────────────────────────────────────────────────────────────────────────────
# ACTION: create-sped-referral
# ─────────────────────────────────────────────────────────────────────────────

def create_sped_referral(conn, args):
    """Create a special ed referral record; begin status lifecycle."""
    student_id = getattr(args, "student_id", None) or None
    referral_source = getattr(args, "referral_source", None) or None
    referral_date = getattr(args, "referral_date", None) or datetime.now().strftime("%Y-%m-%d")
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    created_by = getattr(args, "user_id", None) or ""

    if not student_id:
        return err("--student-id is required")
    if not referral_source:
        return err("--referral-source is required")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    referral_reason = getattr(args, "referral_reason", None) or ""
    areas_of_concern = getattr(args, "areas_of_concern", None) or "[]"
    prior_interventions = getattr(args, "prior_interventions", None) or ""

    naming_series = get_next_name(conn, "educlaw_k12_sped_referral", company_id=company_id)
    referral_id = str(uuid.uuid4())
    now = _now_iso()

    conn.execute(
        """INSERT INTO educlaw_k12_sped_referral
           (id, naming_series, student_id, referral_date, referral_source,
            referral_reason, areas_of_concern, prior_interventions,
            referral_status, consent_request_date, consent_received_date,
            consent_denied_date, evaluation_deadline,
            company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'received', '', '', '', '', ?, ?, ?, ?)""",
        (referral_id, naming_series, student_id, referral_date, referral_source,
         referral_reason, areas_of_concern, prior_interventions,
         company_id, now, now, created_by)
    )
    conn.commit()
    audit(conn, SKILL, "create-sped-referral", "educlaw_k12_sped_referral",
          referral_id, description=f"Created referral {naming_series}")
    return ok({"id": referral_id, "naming_series": naming_series,
               "referral_status": "received", "referral_date": referral_date,
               "message": "Special education referral created"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: update-sped-referral
# ─────────────────────────────────────────────────────────────────────────────

def update_sped_referral(conn, args):
    """Update referral status, consent dates, evaluation deadline."""
    referral_id = getattr(args, "referral_id", None) or None
    if not referral_id:
        return err("--referral-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_k12_sped_referral WHERE id = ?", (referral_id,)
    ).fetchone()
    if not row:
        return err(f"SPED referral {referral_id} not found")

    updates = {}
    for field in ["referral_status", "referral_reason", "areas_of_concern",
                  "prior_interventions", "consent_request_date",
                  "consent_received_date", "consent_denied_date"]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    # Auto-calculate evaluation_deadline when consent_received_date is set
    consent_received = updates.get("consent_received_date") or row["consent_received_date"]
    if "consent_received_date" in updates and updates["consent_received_date"]:
        deadline = _add_calendar_days(updates["consent_received_date"], 60)
        if deadline:
            updates["evaluation_deadline"] = deadline

    eval_deadline = getattr(args, "evaluation_deadline", None)
    if eval_deadline:
        updates["evaluation_deadline"] = eval_deadline

    if not updates:
        return err("No fields provided to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE educlaw_k12_sped_referral SET {set_clause} WHERE id = ?",
        list(updates.values()) + [referral_id]
    )
    conn.commit()
    audit(conn, SKILL, "update-sped-referral", "educlaw_k12_sped_referral", referral_id)
    return ok({"id": referral_id, "message": "SPED referral updated",
               "evaluation_deadline": updates.get("evaluation_deadline", row["evaluation_deadline"])})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: get-sped-referral
# ─────────────────────────────────────────────────────────────────────────────

def get_sped_referral(conn, args):
    """Get a single referral with linked evaluations; FERPA log."""
    referral_id = getattr(args, "referral_id", None) or None
    user_id = getattr(args, "user_id", None) or ""

    if not referral_id:
        return err("--referral-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_k12_sped_referral WHERE id = ?", (referral_id,)
    ).fetchone()
    if not row:
        return err(f"SPED referral {referral_id} not found")

    data = row_to_dict(row)
    data["areas_of_concern"] = _parse_json(data.get("areas_of_concern"), [])

    evaluations = conn.execute(
        "SELECT * FROM educlaw_k12_sped_evaluation WHERE referral_id = ? ORDER BY evaluation_date",
        (referral_id,)
    ).fetchall()
    eval_list = rows_to_list(evaluations)
    for ev in eval_list:
        ev["scores"] = _parse_json(ev.get("scores"), {})
    data["evaluations"] = eval_list

    _log_ferpa(conn, user_id, data["student_id"], "special_education", data["company_id"])
    conn.commit()
    return ok(data)



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-sped-referrals
# ─────────────────────────────────────────────────────────────────────────────

def list_sped_referrals(conn, args):
    """List referrals with filters."""
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    student_id = getattr(args, "student_id", None) or None
    referral_status = getattr(args, "referral_status", None) or None
    approaching_deadline = getattr(args, "approaching_deadline", None) or None
    limit = getattr(args, "limit", None) or 50
    offset = getattr(args, "offset", None) or 0

    query = "SELECT * FROM educlaw_k12_sped_referral WHERE company_id = ?"
    params = [company_id]

    if student_id:
        query += " AND student_id = ?"
        params.append(student_id)
    if referral_status:
        query += " AND referral_status = ?"
        params.append(referral_status)
    if approaching_deadline:
        query += " AND evaluation_deadline != '' AND evaluation_deadline <= ?"
        params.append(approaching_deadline)

    query += " ORDER BY referral_date DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()
    return ok({"referrals": rows_to_list(rows), "count": len(rows)})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-sped-evaluation
# ─────────────────────────────────────────────────────────────────────────────

def add_sped_evaluation(conn, args):
    """Add an immutable evaluation component record to a referral."""
    referral_id = getattr(args, "referral_id", None) or None
    student_id = getattr(args, "student_id", None) or None
    evaluation_type = getattr(args, "evaluation_type", None) or None
    created_by = getattr(args, "user_id", None) or ""

    if not referral_id:
        return err("--referral-id is required")
    if not student_id:
        return err("--student-id is required")
    if not evaluation_type:
        return err("--evaluation-type is required")

    if not conn.execute(
        "SELECT id FROM educlaw_k12_sped_referral WHERE id = ?", (referral_id,)
    ).fetchone():
        return err(f"SPED referral {referral_id} not found")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    evaluator_name = getattr(args, "evaluator_name", None) or ""
    evaluator_role = getattr(args, "evaluator_role", None) or ""
    evaluation_date = getattr(args, "evaluation_date", None) or ""
    instrument_used = getattr(args, "instrument_used", None) or ""
    findings_summary = getattr(args, "findings_summary", None) or ""
    scores = getattr(args, "scores", None) or "{}"

    now = _now_iso()
    eval_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_sped_evaluation
           (id, referral_id, student_id, evaluation_type, evaluator_name,
            evaluator_role, evaluation_date, instrument_used,
            findings_summary, scores, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (eval_id, referral_id, student_id, evaluation_type, evaluator_name,
         evaluator_role, evaluation_date, instrument_used,
         findings_summary, scores, now, created_by)
    )
    conn.commit()
    audit(conn, SKILL, "add-sped-evaluation", "educlaw_k12_sped_evaluation", eval_id)
    return ok({"id": eval_id, "evaluation_type": evaluation_type,
               "message": "SPED evaluation added"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-sped-evaluations
# ─────────────────────────────────────────────────────────────────────────────

def list_sped_evaluations(conn, args):
    """List all evaluation components for a referral."""
    referral_id = getattr(args, "referral_id", None) or None
    if not referral_id:
        return err("--referral-id is required")

    rows = conn.execute(
        "SELECT * FROM educlaw_k12_sped_evaluation WHERE referral_id = ? ORDER BY evaluation_date",
        (referral_id,)
    ).fetchall()
    result = rows_to_list(rows)
    for r in result:
        r["scores"] = _parse_json(r.get("scores"), {})
    return ok({"referral_id": referral_id, "evaluations": result, "count": len(result)})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: record-sped-eligibility
# ─────────────────────────────────────────────────────────────────────────────

def record_sped_eligibility(conn, args):
    """Create immutable eligibility determination; auto-calculate IEP deadline."""
    referral_id = getattr(args, "referral_id", None) or None
    student_id = getattr(args, "student_id", None) or None
    eligibility_meeting_date = getattr(args, "eligibility_meeting_date", None) or ""
    is_eligible = int(bool(getattr(args, "is_eligible", None) or 0))
    primary_disability = getattr(args, "primary_disability", None) or "not_applicable"
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    created_by = getattr(args, "user_id", None) or ""
    user_id = getattr(args, "user_id", None) or ""

    if not referral_id:
        return err("--referral-id is required")
    if not student_id:
        return err("--student-id is required")

    if not conn.execute(
        "SELECT id FROM educlaw_k12_sped_referral WHERE id = ?", (referral_id,)
    ).fetchone():
        return err(f"SPED referral {referral_id} not found")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    # Check uniqueness: one eligibility per referral
    existing = conn.execute(
        "SELECT id FROM educlaw_k12_sped_eligibility WHERE referral_id = ?", (referral_id,)
    ).fetchone()
    if existing:
        return err(f"Eligibility determination already exists for referral {referral_id}")

    # Auto-calculate IEP deadline = eligibility_meeting_date + 30 days
    iep_deadline = ""
    if eligibility_meeting_date:
        iep_deadline = _add_calendar_days(eligibility_meeting_date, 30)

    disability_categories = getattr(args, "disability_categories", None) or "[]"
    adverse_educational_effect = getattr(args, "adverse_educational_effect", None) or ""
    eligibility_status = getattr(args, "eligibility_status", None) or (
        "eligible" if is_eligible else "ineligible")
    ineligibility_reason = getattr(args, "ineligibility_reason", None) or ""
    team_members_present = getattr(args, "team_members_present", None) or "[]"
    parent_consent_date = getattr(args, "parent_consent_date", None) or ""

    # Business rule: if not eligible, disability_categories must be empty
    if not is_eligible:
        disability_categories = "[]"
        primary_disability = "not_applicable"

    now = _now_iso()
    elig_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_sped_eligibility
           (id, referral_id, student_id, eligibility_meeting_date, iep_deadline,
            is_eligible, disability_categories, primary_disability,
            adverse_educational_effect, eligibility_status, ineligibility_reason,
            team_members_present, parent_consent_date,
            company_id, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (elig_id, referral_id, student_id, eligibility_meeting_date, iep_deadline,
         is_eligible, disability_categories, primary_disability,
         adverse_educational_effect, eligibility_status, ineligibility_reason,
         team_members_present, parent_consent_date,
         company_id, now, created_by)
    )

    # Update referral status to evaluation_complete
    conn.execute(
        "UPDATE educlaw_k12_sped_referral SET referral_status = 'evaluation_complete', "
        "updated_at = ? WHERE id = ?",
        (now, referral_id)
    )

    _log_ferpa(conn, user_id, student_id, "special_education", company_id,
               access_reason="eligibility_determination")
    conn.commit()
    audit(conn, SKILL, "record-sped-eligibility", "educlaw_k12_sped_eligibility", elig_id)
    return ok({
        "id": elig_id,
        "is_eligible": bool(is_eligible),
        "eligibility_status": eligibility_status,
        "iep_deadline": iep_deadline,
        "message": "SPED eligibility determination recorded",
    })



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: get-sped-eligibility
# ─────────────────────────────────────────────────────────────────────────────

def get_sped_eligibility(conn, args):
    """Get eligibility determination for a student; FERPA log."""
    student_id = getattr(args, "student_id", None) or None
    eligibility_id = getattr(args, "eligibility_id", None) or None
    user_id = getattr(args, "user_id", None) or ""

    if not student_id and not eligibility_id:
        return err("--student-id or --eligibility-id is required")

    if eligibility_id:
        row = conn.execute(
            "SELECT * FROM educlaw_k12_sped_eligibility WHERE id = ?", (eligibility_id,)
        ).fetchone()
    else:
        row = conn.execute(
            """SELECT e.* FROM educlaw_k12_sped_eligibility e
               WHERE e.student_id = ?
               ORDER BY e.created_at DESC LIMIT 1""",
            (student_id,)
        ).fetchone()

    if not row:
        return err("SPED eligibility determination not found")

    data = row_to_dict(row)
    data["disability_categories"] = _parse_json(data.get("disability_categories"), [])
    data["team_members_present"] = _parse_json(data.get("team_members_present"), [])

    _log_ferpa(conn, user_id, data["student_id"], "special_education", data["company_id"])
    conn.commit()
    return ok(data)



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-iep
# ─────────────────────────────────────────────────────────────────────────────

def add_iep(conn, args):
    """Create a new IEP in draft status; auto-set transition_plan_required if student ≥ 16."""
    student_id = getattr(args, "student_id", None) or None
    eligibility_id = getattr(args, "eligibility_id", None) or None
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    created_by = getattr(args, "user_id", None) or ""

    if not student_id:
        return err("--student-id is required")
    if not eligibility_id:
        return err("--eligibility-id is required")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    if not conn.execute(
        "SELECT id FROM educlaw_k12_sped_eligibility WHERE id = ?", (eligibility_id,)
    ).fetchone():
        return err(f"SPED eligibility {eligibility_id} not found")

    iep_start_date = getattr(args, "iep_start_date", None) or ""
    iep_meeting_date = getattr(args, "iep_meeting_date", None) or iep_start_date
    iep_end_date = getattr(args, "iep_end_date", None) or ""
    annual_review_due_date = getattr(args, "annual_review_due_date", None) or iep_end_date
    triennial_reevaluation_due_date = getattr(
        args, "triennial_reevaluation_due_date", None) or ""
    iep_version = int(getattr(args, "iep_version", None) or 1)
    is_amendment = int(bool(getattr(args, "is_amendment", None) or 0))
    parent_iep_id = getattr(args, "parent_iep_id", None) or None

    # Validate parent_iep_id if provided
    if parent_iep_id:
        if not conn.execute("SELECT id FROM educlaw_k12_iep WHERE id = ?", (parent_iep_id,)).fetchone():
            return err(f"Parent IEP {parent_iep_id} not found")

    plaafp_academic = getattr(args, "plaafp_academic", None) or ""
    plaafp_functional = getattr(args, "plaafp_functional", None) or ""
    lre_percentage_general_ed = getattr(args, "lre_percentage_general_ed", None) or ""
    lre_justification = getattr(args, "lre_justification", None) or ""
    supplementary_aids = getattr(args, "supplementary_aids", None) or ""
    program_modifications = getattr(args, "program_modifications", None) or ""
    state_assessment_participation = getattr(
        args, "state_assessment_participation", None) or "with_accommodations"
    state_assessment_accommodations = getattr(
        args, "state_assessment_accommodations", None) or ""
    progress_report_frequency = getattr(
        args, "progress_report_frequency", None) or "quarterly"
    transition_postsecondary_goal = getattr(args, "transition_postsecondary_goal", None) or ""
    transition_employment_goal = getattr(args, "transition_employment_goal", None) or ""
    transition_independent_living_goal = getattr(
        args, "transition_independent_living_goal", None) or ""

    # Auto-set transition_plan_required for students ≥ 16
    student_age = _student_age_at(student_id, iep_start_date or None, conn)
    transition_plan_required_arg = getattr(args, "transition_plan_required", None)
    if transition_plan_required_arg is not None:
        transition_plan_required = int(bool(transition_plan_required_arg))
    else:
        transition_plan_required = 1 if student_age >= 16 else 0

    now = _now_iso()
    current_year = datetime.now().year
    naming_series = get_next_name(conn, "educlaw_k12_iep", year=current_year, company_id=company_id)
    iep_id = str(uuid.uuid4())

    conn.execute(
        """INSERT INTO educlaw_k12_iep
           (id, naming_series, student_id, eligibility_id, iep_version,
            is_amendment, parent_iep_id, iep_meeting_date, iep_start_date,
            iep_end_date, annual_review_due_date, triennial_reevaluation_due_date,
            plaafp_academic, plaafp_functional, lre_percentage_general_ed,
            lre_justification, supplementary_aids, program_modifications,
            state_assessment_participation, state_assessment_accommodations,
            transition_plan_required, transition_postsecondary_goal,
            transition_employment_goal, transition_independent_living_goal,
            progress_report_frequency, iep_status, parent_consent_date,
            company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                   ?, ?, ?, ?, ?, 'draft', '', ?, ?, ?, ?)""",
        (iep_id, naming_series, student_id, eligibility_id, iep_version,
         is_amendment, parent_iep_id, iep_meeting_date, iep_start_date,
         iep_end_date, annual_review_due_date, triennial_reevaluation_due_date,
         plaafp_academic, plaafp_functional, lre_percentage_general_ed,
         lre_justification, supplementary_aids, program_modifications,
         state_assessment_participation, state_assessment_accommodations,
         transition_plan_required, transition_postsecondary_goal,
         transition_employment_goal, transition_independent_living_goal,
         progress_report_frequency, company_id, now, now, created_by)
    )
    conn.commit()
    audit(conn, SKILL, "add-iep", "educlaw_k12_iep",
          iep_id, description=f"Created IEP {naming_series}")
    return ok({
        "id": iep_id,
        "naming_series": naming_series,
        "iep_status": "draft",
        "iep_version": iep_version,
        "transition_plan_required": bool(transition_plan_required),
        "message": "IEP created in draft status",
    })



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: update-iep
# ─────────────────────────────────────────────────────────────────────────────

def update_iep(conn, args):
    """Update IEP draft fields (PLAAFP, LRE, assessment, transition, dates)."""
    iep_id = getattr(args, "iep_id", None) or None
    if not iep_id:
        return err("--iep-id is required")

    row = conn.execute("SELECT * FROM educlaw_k12_iep WHERE id = ?", (iep_id,)).fetchone()
    if not row:
        return err(f"IEP {iep_id} not found")
    if row["iep_status"] not in ("draft",):
        return err(f"Cannot update IEP with status '{row['iep_status']}'. Only draft IEPs can be updated.")

    updates = {}
    str_fields = [
        "iep_meeting_date", "iep_start_date", "iep_end_date",
        "annual_review_due_date", "triennial_reevaluation_due_date",
        "plaafp_academic", "plaafp_functional", "lre_percentage_general_ed",
        "lre_justification", "supplementary_aids", "program_modifications",
        "state_assessment_participation", "state_assessment_accommodations",
        "transition_postsecondary_goal", "transition_employment_goal",
        "transition_independent_living_goal", "progress_report_frequency",
        "parent_consent_date",
    ]
    for field in str_fields:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    for int_field in ["iep_version", "is_amendment", "transition_plan_required"]:
        val = getattr(args, int_field, None)
        if val is not None:
            updates[int_field] = int(val)

    if not updates:
        return err("No fields provided to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE educlaw_k12_iep SET {set_clause} WHERE id = ?",
        list(updates.values()) + [iep_id]
    )
    conn.commit()
    audit(conn, SKILL, "update-iep", "educlaw_k12_iep", iep_id)
    return ok({"id": iep_id, "message": "IEP updated"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: activate-iep
# ─────────────────────────────────────────────────────────────────────────────

def activate_iep(conn, args):
    """Set IEP status to active; record parent consent; set prior IEP to superseded."""
    iep_id = getattr(args, "iep_id", None) or None
    parent_consent_date = getattr(args, "parent_consent_date", None) or (
        datetime.now().strftime("%Y-%m-%d"))

    if not iep_id:
        return err("--iep-id is required")

    iep = conn.execute("SELECT * FROM educlaw_k12_iep WHERE id = ?", (iep_id,)).fetchone()
    if not iep:
        return err(f"IEP {iep_id} not found")
    if iep["iep_status"] != "draft":
        return err(f"Can only activate a draft IEP. Current status: {iep['iep_status']}")

    now = _now_iso()
    student_id = iep["student_id"]

    # Set any existing active IEP for this student to superseded
    conn.execute(
        """UPDATE educlaw_k12_iep SET iep_status = 'superseded', updated_at = ?
           WHERE student_id = ? AND iep_status = 'active' AND id != ?""",
        (now, student_id, iep_id)
    )

    # Activate this IEP
    conn.execute(
        """UPDATE educlaw_k12_iep
           SET iep_status = 'active', parent_consent_date = ?, updated_at = ?
           WHERE id = ?""",
        (parent_consent_date, now, iep_id)
    )
    conn.commit()
    audit(conn, SKILL, "activate-iep", "educlaw_k12_iep", iep_id, description="IEP activated")
    return ok({
        "id": iep_id,
        "iep_status": "active",
        "parent_consent_date": parent_consent_date,
        "message": "IEP activated successfully",
    })



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-iep-amendment
# ─────────────────────────────────────────────────────────────────────────────

def amend_iep(conn, args):
    """Create mid-year amendment: new IEP record with is_amendment=1; prior IEP → amended."""
    iep_id = getattr(args, "iep_id", None) or None
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    created_by = getattr(args, "user_id", None) or ""

    if not iep_id:
        return err("--iep-id (prior active IEP ID) is required")

    prior_iep = conn.execute(
        "SELECT * FROM educlaw_k12_iep WHERE id = ?", (iep_id,)
    ).fetchone()
    if not prior_iep:
        return err(f"IEP {iep_id} not found")
    if prior_iep["iep_status"] != "active":
        return err(f"Can only amend an active IEP. Current status: {prior_iep['iep_status']}")

    now = _now_iso()
    current_year = datetime.now().year
    naming_series = get_next_name(conn, "educlaw_k12_iep", year=current_year, company_id=company_id)
    new_iep_id = str(uuid.uuid4())
    new_version = (prior_iep["iep_version"] or 1) + 1

    # Create amended IEP inheriting fields from prior
    conn.execute(
        """INSERT INTO educlaw_k12_iep
           (id, naming_series, student_id, eligibility_id, iep_version,
            is_amendment, parent_iep_id, iep_meeting_date, iep_start_date,
            iep_end_date, annual_review_due_date, triennial_reevaluation_due_date,
            plaafp_academic, plaafp_functional, lre_percentage_general_ed,
            lre_justification, supplementary_aids, program_modifications,
            state_assessment_participation, state_assessment_accommodations,
            transition_plan_required, transition_postsecondary_goal,
            transition_employment_goal, transition_independent_living_goal,
            progress_report_frequency, iep_status, parent_consent_date,
            company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                   ?, ?, ?, ?, ?, 'draft', '', ?, ?, ?, ?)""",
        (new_iep_id, naming_series, prior_iep["student_id"], prior_iep["eligibility_id"],
         new_version, iep_id,
         getattr(args, "iep_meeting_date", None) or prior_iep["iep_meeting_date"],
         prior_iep["iep_start_date"], prior_iep["iep_end_date"],
         prior_iep["annual_review_due_date"], prior_iep["triennial_reevaluation_due_date"],
         prior_iep["plaafp_academic"], prior_iep["plaafp_functional"],
         prior_iep["lre_percentage_general_ed"], prior_iep["lre_justification"],
         prior_iep["supplementary_aids"], prior_iep["program_modifications"],
         prior_iep["state_assessment_participation"], prior_iep["state_assessment_accommodations"],
         prior_iep["transition_plan_required"], prior_iep["transition_postsecondary_goal"],
         prior_iep["transition_employment_goal"], prior_iep["transition_independent_living_goal"],
         prior_iep["progress_report_frequency"],
         company_id, now, now, created_by)
    )

    # Mark prior IEP as amended
    conn.execute(
        "UPDATE educlaw_k12_iep SET iep_status = 'amended', updated_at = ? WHERE id = ?",
        (now, iep_id)
    )
    conn.commit()
    audit(conn, SKILL, "add-iep-amendment", "educlaw_k12_iep",
          new_iep_id, description=f"Amendment of IEP {iep_id}")
    return ok({
        "id": new_iep_id,
        "naming_series": naming_series,
        "iep_status": "draft",
        "is_amendment": True,
        "parent_iep_id": iep_id,
        "iep_version": new_version,
        "message": "IEP amendment created in draft status",
    })



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: get-active-iep
# ─────────────────────────────────────────────────────────────────────────────

def get_active_iep(conn, args):
    """Get the currently active IEP for a student with goals, services, and team; FERPA log."""
    student_id = getattr(args, "student_id", None) or None
    user_id = getattr(args, "user_id", None) or ""

    if not student_id:
        return err("--student-id is required")

    iep = conn.execute(
        "SELECT * FROM educlaw_k12_iep WHERE student_id = ? AND iep_status = 'active'",
        (student_id,)
    ).fetchone()
    if not iep:
        return err(f"No active IEP found for student {student_id}")

    return _get_iep_with_children(conn, iep, user_id)



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: get-iep
# ─────────────────────────────────────────────────────────────────────────────

def get_iep(conn, args):
    """Get a specific IEP by ID with all child records; FERPA log."""
    iep_id = getattr(args, "iep_id", None) or None
    user_id = getattr(args, "user_id", None) or ""

    if not iep_id:
        return err("--iep-id is required")

    iep = conn.execute(
        "SELECT * FROM educlaw_k12_iep WHERE id = ?", (iep_id,)
    ).fetchone()
    if not iep:
        return err(f"IEP {iep_id} not found")

    return _get_iep_with_children(conn, iep, user_id)



def _get_iep_with_children(conn, iep_row, user_id):
    """Shared logic: fetch IEP with goals, services, team members; FERPA log."""
    iep_dict = row_to_dict(iep_row)
    iep_id = iep_dict["id"]
    student_id = iep_dict["student_id"]
    company_id = iep_dict["company_id"]

    # Goals
    goals = conn.execute(
        "SELECT * FROM educlaw_k12_iep_goal WHERE iep_id = ? ORDER BY sort_order, created_at",
        (iep_id,)
    ).fetchall()
    iep_dict["goals"] = rows_to_list(goals)

    # Services
    services = conn.execute(
        "SELECT * FROM educlaw_k12_iep_service WHERE iep_id = ? ORDER BY service_type",
        (iep_id,)
    ).fetchall()
    iep_dict["services"] = rows_to_list(services)

    # Team members
    team = conn.execute(
        "SELECT * FROM educlaw_k12_iep_team_member WHERE iep_id = ? ORDER BY member_type",
        (iep_id,)
    ).fetchall()
    iep_dict["team_members"] = rows_to_list(team)

    _log_ferpa(conn, user_id, student_id, "special_education", company_id)
    conn.commit()
    return ok(iep_dict)


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-iep-deadlines
# ─────────────────────────────────────────────────────────────────────────────

def list_iep_deadlines(conn, args):
    """List students with IEP annual review due within a configurable window."""
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    days_window = int(getattr(args, "days_window", None) or 30)

    today = datetime.now().strftime("%Y-%m-%d")
    cutoff = (datetime.now() + timedelta(days=days_window)).strftime("%Y-%m-%d")

    rows = conn.execute(
        """SELECT i.id, i.naming_series, i.student_id, i.annual_review_due_date,
                  i.iep_status, i.iep_version,
                  s.full_name, s.grade_level
           FROM educlaw_k12_iep i
           JOIN educlaw_student s ON i.student_id = s.id
           WHERE i.company_id = ?
             AND i.iep_status = 'active'
             AND i.annual_review_due_date != ''
             AND i.annual_review_due_date <= ?
             AND i.annual_review_due_date >= ?
           ORDER BY i.annual_review_due_date""",
        (company_id, cutoff, today)
    ).fetchall()

    return ok({
        "days_window": days_window,
        "cutoff_date": cutoff,
        "iep_deadlines": rows_to_list(rows),
        "count": len(rows),
    })



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-reevaluation-due
# ─────────────────────────────────────────────────────────────────────────────

def list_reevaluation_due(conn, args):
    """List students with triennial re-evaluation due within a configurable window."""
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    days_window = int(getattr(args, "days_window", None) or 90)

    today = datetime.now().strftime("%Y-%m-%d")
    cutoff = (datetime.now() + timedelta(days=days_window)).strftime("%Y-%m-%d")

    rows = conn.execute(
        """SELECT i.id, i.naming_series, i.student_id, i.triennial_reevaluation_due_date,
                  i.iep_status,
                  s.full_name, s.grade_level
           FROM educlaw_k12_iep i
           JOIN educlaw_student s ON i.student_id = s.id
           WHERE i.company_id = ?
             AND i.iep_status = 'active'
             AND i.triennial_reevaluation_due_date != ''
             AND i.triennial_reevaluation_due_date <= ?
             AND i.triennial_reevaluation_due_date >= ?
           ORDER BY i.triennial_reevaluation_due_date""",
        (company_id, cutoff, today)
    ).fetchall()

    return ok({
        "days_window": days_window,
        "cutoff_date": cutoff,
        "reevaluations_due": rows_to_list(rows),
        "count": len(rows),
    })



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-iep-goal
# ─────────────────────────────────────────────────────────────────────────────

def add_iep_goal(conn, args):
    """Add an immutable measurable annual goal to an IEP."""
    iep_id = getattr(args, "iep_id", None) or None
    student_id = getattr(args, "student_id", None) or None
    goal_area = getattr(args, "goal_area", None) or None
    measurement_method = getattr(args, "measurement_method", None) or None
    monitoring_frequency = getattr(args, "monitoring_frequency", None) or None
    created_by = getattr(args, "user_id", None) or ""

    if not iep_id:
        return err("--iep-id is required")
    if not student_id:
        return err("--student-id is required")
    if not goal_area:
        return err("--goal-area is required")
    if not measurement_method:
        return err("--measurement-method is required")
    if not monitoring_frequency:
        return err("--monitoring-frequency is required")

    if not conn.execute("SELECT id FROM educlaw_k12_iep WHERE id = ?", (iep_id,)).fetchone():
        return err(f"IEP {iep_id} not found")
    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    goal_description = getattr(args, "goal_description", None) or ""
    baseline_performance = getattr(args, "baseline_performance", None) or ""
    target_performance = getattr(args, "target_performance", None) or ""
    responsible_provider = getattr(args, "responsible_provider", None) or ""
    sort_order = int(getattr(args, "sort_order", None) or 0)

    now = _now_iso()
    goal_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_iep_goal
           (id, iep_id, student_id, goal_area, goal_description, baseline_performance,
            target_performance, measurement_method, monitoring_frequency,
            responsible_provider, sort_order, is_met, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)""",
        (goal_id, iep_id, student_id, goal_area, goal_description, baseline_performance,
         target_performance, measurement_method, monitoring_frequency,
         responsible_provider, sort_order, now, created_by)
    )
    conn.commit()
    audit(conn, SKILL, "add-iep-goal", "educlaw_k12_iep_goal", goal_id)
    return ok({"id": goal_id, "goal_area": goal_area, "message": "IEP goal added"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-iep-goals
# ─────────────────────────────────────────────────────────────────────────────

def list_iep_goals(conn, args):
    """List all goals for an IEP."""
    iep_id = getattr(args, "iep_id", None) or None
    if not iep_id:
        return err("--iep-id is required")

    rows = conn.execute(
        "SELECT * FROM educlaw_k12_iep_goal WHERE iep_id = ? ORDER BY sort_order, created_at",
        (iep_id,)
    ).fetchall()
    return ok({"iep_id": iep_id, "goals": rows_to_list(rows), "count": len(rows)})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-iep-service
# ─────────────────────────────────────────────────────────────────────────────

def add_iep_service(conn, args):
    """Add an immutable mandated service to an IEP."""
    iep_id = getattr(args, "iep_id", None) or None
    student_id = getattr(args, "student_id", None) or None
    service_type = getattr(args, "service_type", None) or None
    service_setting = getattr(args, "service_setting", None) or None
    created_by = getattr(args, "user_id", None) or ""

    if not iep_id:
        return err("--iep-id is required")
    if not student_id:
        return err("--student-id is required")
    if not service_type:
        return err("--service-type is required")
    if not service_setting:
        return err("--service-setting is required")

    if not conn.execute("SELECT id FROM educlaw_k12_iep WHERE id = ?", (iep_id,)).fetchone():
        return err(f"IEP {iep_id} not found")
    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    frequency_minutes_per_week = int(getattr(args, "frequency_minutes_per_week", None) or 0)
    provider_name = getattr(args, "provider_name", None) or ""
    provider_role = getattr(args, "provider_role", None) or ""
    start_date = getattr(args, "start_date", None) or ""
    end_date = getattr(args, "end_date", None) or ""

    now = _now_iso()
    service_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_iep_service
           (id, iep_id, student_id, service_type, service_setting,
            frequency_minutes_per_week, provider_name, provider_role,
            start_date, end_date, total_minutes_delivered, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)""",
        (service_id, iep_id, student_id, service_type, service_setting,
         frequency_minutes_per_week, provider_name, provider_role,
         start_date, end_date, now, created_by)
    )
    conn.commit()
    audit(conn, SKILL, "add-iep-service", "educlaw_k12_iep_service", service_id)
    return ok({"id": service_id, "service_type": service_type,
               "frequency_minutes_per_week": frequency_minutes_per_week,
               "message": "IEP service added"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-iep-services
# ─────────────────────────────────────────────────────────────────────────────

def list_iep_services(conn, args):
    """List all services for an IEP."""
    iep_id = getattr(args, "iep_id", None) or None
    if not iep_id:
        return err("--iep-id is required")

    rows = conn.execute(
        "SELECT * FROM educlaw_k12_iep_service WHERE iep_id = ? ORDER BY service_type",
        (iep_id,)
    ).fetchall()
    return ok({"iep_id": iep_id, "services": rows_to_list(rows), "count": len(rows)})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: record-iep-service-session
# ─────────────────────────────────────────────────────────────────────────────

def log_iep_service_session(conn, args):
    """Record an immutable service delivery session; update total_minutes_delivered."""
    iep_service_id = getattr(args, "iep_service_id", None) or None
    student_id = getattr(args, "student_id", None) or None
    session_date = getattr(args, "session_date", None) or None
    minutes_delivered = int(getattr(args, "minutes_delivered", None) or 0)
    created_by = getattr(args, "user_id", None) or ""

    if not iep_service_id:
        return err("--iep-service-id is required")
    if not student_id:
        return err("--student-id is required")
    if not session_date:
        return err("--session-date is required")

    if not conn.execute(
        "SELECT id FROM educlaw_k12_iep_service WHERE id = ?", (iep_service_id,)
    ).fetchone():
        return err(f"IEP service {iep_service_id} not found")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    session_notes = getattr(args, "session_notes", None) or ""
    provider_name = getattr(args, "provider_name", None) or ""
    is_makeup_session = int(bool(getattr(args, "is_makeup_session", None) or 0))
    was_session_missed = int(bool(getattr(args, "was_session_missed", None) or 0))
    missed_reason = getattr(args, "missed_reason", None) or ""

    now = _now_iso()
    log_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_iep_service_log
           (id, iep_service_id, student_id, session_date, minutes_delivered,
            session_notes, provider_name, is_makeup_session, was_session_missed,
            missed_reason, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (log_id, iep_service_id, student_id, session_date, minutes_delivered,
         session_notes, provider_name, is_makeup_session, was_session_missed,
         missed_reason, now, created_by)
    )

    # Business rule: increment total_minutes_delivered when session was delivered
    if not was_session_missed and minutes_delivered > 0:
        conn.execute(
            """UPDATE educlaw_k12_iep_service
               SET total_minutes_delivered = total_minutes_delivered + ?
               WHERE id = ?""",
            (minutes_delivered, iep_service_id)
        )

    conn.commit()
    audit(conn, SKILL, "record-iep-service-session", "educlaw_k12_iep_service_log", log_id)
    return ok({"id": log_id, "minutes_delivered": minutes_delivered,
               "was_session_missed": bool(was_session_missed),
               "message": "IEP service session logged"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-iep-service-logs
# ─────────────────────────────────────────────────────────────────────────────

def list_iep_service_logs(conn, args):
    """List session logs for a specific IEP service."""
    iep_service_id = getattr(args, "iep_service_id", None) or None
    if not iep_service_id:
        return err("--iep-service-id is required")

    limit = getattr(args, "limit", None) or 100
    offset = getattr(args, "offset", None) or 0

    rows = conn.execute(
        """SELECT * FROM educlaw_k12_iep_service_log
           WHERE iep_service_id = ?
           ORDER BY session_date DESC LIMIT ? OFFSET ?""",
        (iep_service_id, limit, offset)
    ).fetchall()
    return ok({"iep_service_id": iep_service_id, "logs": rows_to_list(rows),
               "count": len(rows)})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: get-service-compliance-report
# ─────────────────────────────────────────────────────────────────────────────

def get_service_compliance_report(conn, args):
    """Compare planned vs. actual service minutes for each IEP service; flag gaps."""
    student_id = getattr(args, "student_id", None) or None
    iep_id = getattr(args, "iep_id", None) or None

    if not student_id and not iep_id:
        return err("--student-id or --iep-id is required")

    if iep_id:
        iep = conn.execute("SELECT * FROM educlaw_k12_iep WHERE id = ?", (iep_id,)).fetchone()
    else:
        iep = conn.execute(
            "SELECT * FROM educlaw_k12_iep WHERE student_id = ? AND iep_status = 'active'",
            (student_id,)
        ).fetchone()

    if not iep:
        return err("No IEP found")

    iep_dict = row_to_dict(iep)
    iep_id = iep_dict["id"]

    services = conn.execute(
        "SELECT * FROM educlaw_k12_iep_service WHERE iep_id = ?", (iep_id,)
    ).fetchall()

    # Calculate weeks elapsed between IEP start and today
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        iep_start = date.fromisoformat(iep_dict["iep_start_date"])
        days_elapsed = max(0, (date.today() - iep_start).days)
        weeks_elapsed = days_elapsed / 7.0
    except Exception:
        weeks_elapsed = 0

    compliance_data = []
    overall_gap = 0

    for svc in services:
        s = row_to_dict(svc)
        planned_total = int(s["frequency_minutes_per_week"] or 0) * weeks_elapsed
        actual_total = int(s["total_minutes_delivered"] or 0)
        gap = max(0, planned_total - actual_total)
        pct = (actual_total / planned_total * 100) if planned_total > 0 else 100

        compliance_data.append({
            "service_id": s["id"],
            "service_type": s["service_type"],
            "service_setting": s["service_setting"],
            "provider_name": s["provider_name"],
            "frequency_minutes_per_week": s["frequency_minutes_per_week"],
            "weeks_elapsed": round(weeks_elapsed, 1),
            "planned_minutes": round(planned_total, 0),
            "actual_minutes": actual_total,
            "gap_minutes": round(gap, 0),
            "compliance_pct": round(pct, 1),
            "status": "on_track" if gap == 0 else ("minor_gap" if gap < 60 else "significant_gap"),
        })
        overall_gap += gap

    return ok({
        "iep_id": iep_id,
        "student_id": iep_dict["student_id"],
        "weeks_elapsed": round(weeks_elapsed, 1),
        "services": compliance_data,
        "total_gap_minutes": round(overall_gap, 0),
        "overall_status": "on_track" if overall_gap == 0 else "gap_detected",
    })



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-iep-team-member
# ─────────────────────────────────────────────────────────────────────────────

def add_iep_team_member(conn, args):
    """Add an immutable team member record to an IEP."""
    iep_id = getattr(args, "iep_id", None) or None
    member_type = getattr(args, "member_type", None) or None
    member_name = getattr(args, "member_name", None) or ""
    created_by = getattr(args, "user_id", None) or ""

    if not iep_id:
        return err("--iep-id is required")
    if not member_type:
        return err("--member-type is required")

    if not conn.execute("SELECT id FROM educlaw_k12_iep WHERE id = ?", (iep_id,)).fetchone():
        return err(f"IEP {iep_id} not found")

    guardian_id = getattr(args, "guardian_id", None) or None
    instructor_id = getattr(args, "instructor_id", None) or None

    if guardian_id:
        if not conn.execute("SELECT id FROM educlaw_guardian WHERE id = ?", (guardian_id,)).fetchone():
            return err(f"Guardian {guardian_id} not found")

    if instructor_id:
        if not conn.execute(
            "SELECT id FROM educlaw_instructor WHERE id = ?", (instructor_id,)
        ).fetchone():
            return err(f"Instructor {instructor_id} not found")

    member_role = getattr(args, "member_role", None) or ""
    attended_meeting = int(bool(getattr(args, "attended_meeting", None) if getattr(args, "attended_meeting", None) is not None else 1))
    excused_absence = int(bool(getattr(args, "excused_absence", None) or 0))
    excusal_notes = getattr(args, "excusal_notes", None) or ""
    signature_date = getattr(args, "signature_date", None) or ""

    now = _now_iso()
    member_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_iep_team_member
           (id, iep_id, member_type, member_name, member_role,
            guardian_id, instructor_id, attended_meeting, excused_absence,
            excusal_notes, signature_date, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (member_id, iep_id, member_type, member_name, member_role,
         guardian_id, instructor_id, attended_meeting, excused_absence,
         excusal_notes, signature_date, now, created_by)
    )
    conn.commit()
    audit(conn, SKILL, "add-iep-team-member", "educlaw_k12_iep_team_member", member_id)
    return ok({"id": member_id, "member_type": member_type, "member_name": member_name,
               "message": "IEP team member added"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: record-iep-progress
# ─────────────────────────────────────────────────────────────────────────────

def record_iep_progress(conn, args):
    """Record immutable progress note for a goal in a reporting period."""
    iep_goal_id = getattr(args, "iep_goal_id", None) or None
    student_id = getattr(args, "student_id", None) or None
    reporting_period = getattr(args, "reporting_period", None) or ""
    progress_date = getattr(args, "progress_date", None) or datetime.now().strftime("%Y-%m-%d")
    progress_rating = getattr(args, "progress_rating", None) or None
    created_by = getattr(args, "user_id", None) or ""

    if not iep_goal_id:
        return err("--iep-goal-id is required")
    if not student_id:
        return err("--student-id is required")
    if not progress_rating:
        return err("--progress-rating is required")

    if not conn.execute(
        "SELECT id FROM educlaw_k12_iep_goal WHERE id = ?", (iep_goal_id,)
    ).fetchone():
        return err(f"IEP goal {iep_goal_id} not found")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    current_performance = getattr(args, "current_performance", None) or ""
    evidence = getattr(args, "evidence", None) or ""
    notes_for_parents = getattr(args, "notes_for_parents", None) or ""
    documented_by = getattr(args, "documented_by", None) or created_by

    now = _now_iso()
    progress_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_iep_progress
           (id, iep_goal_id, student_id, reporting_period, progress_date,
            progress_rating, current_performance, evidence, notes_for_parents,
            documented_by, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (progress_id, iep_goal_id, student_id, reporting_period, progress_date,
         progress_rating, current_performance, evidence, notes_for_parents,
         documented_by, now, created_by)
    )
    conn.commit()
    audit(conn, SKILL, "record-iep-progress", "educlaw_k12_iep_progress", progress_id)
    return ok({"id": progress_id, "progress_rating": progress_rating,
               "reporting_period": reporting_period, "message": "IEP progress recorded"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: generate-iep-progress-report
# ─────────────────────────────────────────────────────────────────────────────

def generate_iep_progress_report(conn, args):
    """Parent-facing progress report: all goals with current progress for a reporting period."""
    student_id = getattr(args, "student_id", None) or None
    iep_id = getattr(args, "iep_id", None) or None
    reporting_period = getattr(args, "reporting_period", None) or None
    user_id = getattr(args, "user_id", None) or ""

    if not student_id and not iep_id:
        return err("--student-id or --iep-id is required")

    if iep_id:
        iep = conn.execute("SELECT * FROM educlaw_k12_iep WHERE id = ?", (iep_id,)).fetchone()
    else:
        iep = conn.execute(
            "SELECT * FROM educlaw_k12_iep WHERE student_id = ? AND iep_status = 'active'",
            (student_id,)
        ).fetchone()

    if not iep:
        return err("No IEP found")

    iep_dict = row_to_dict(iep)
    iep_id = iep_dict["id"]
    student_id = iep_dict["student_id"]
    company_id = iep_dict["company_id"]

    # Get student info
    student = conn.execute(
        "SELECT full_name, grade_level FROM educlaw_student WHERE id = ?", (student_id,)
    ).fetchone()

    goals = conn.execute(
        "SELECT * FROM educlaw_k12_iep_goal WHERE iep_id = ? ORDER BY sort_order",
        (iep_id,)
    ).fetchall()

    goal_reports = []
    for goal in goals:
        g = row_to_dict(goal)
        # Get most recent progress for this reporting period
        if reporting_period:
            progress = conn.execute(
                """SELECT * FROM educlaw_k12_iep_progress
                   WHERE iep_goal_id = ? AND reporting_period = ?
                   ORDER BY progress_date DESC LIMIT 1""",
                (goal["id"], reporting_period)
            ).fetchone()
        else:
            progress = conn.execute(
                """SELECT * FROM educlaw_k12_iep_progress
                   WHERE iep_goal_id = ?
                   ORDER BY progress_date DESC LIMIT 1""",
                (goal["id"],)
            ).fetchone()

        g["latest_progress"] = row_to_dict(progress) if progress else None
        goal_reports.append(g)

    _log_ferpa(conn, user_id, student_id, "special_education", company_id,
               access_reason="progress_report_generation")
    conn.commit()

    return ok({
        "iep_id": iep_id,
        "student_id": student_id,
        "student_name": student["full_name"] if student else "",
        "grade_level": student["grade_level"] if student else "",
        "reporting_period": reporting_period,
        "iep_naming_series": iep_dict["naming_series"],
        "progress_report_frequency": iep_dict["progress_report_frequency"],
        "goals": goal_reports,
        "goal_count": len(goal_reports),
    })



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-504-plan
# ─────────────────────────────────────────────────────────────────────────────

def add_504_plan(conn, args):
    """Create a Section 504 accommodation plan."""
    student_id = getattr(args, "student_id", None) or None
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    created_by = getattr(args, "user_id", None) or ""

    if not student_id:
        return err("--student-id is required")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    meeting_date = getattr(args, "meeting_date", None) or ""
    disability_description = getattr(args, "disability_description", None) or ""
    eligibility_basis = getattr(args, "eligibility_basis", None) or ""
    plan_start_date = getattr(args, "plan_start_date", None) or ""
    plan_end_date = getattr(args, "plan_end_date", None) or ""
    review_date = getattr(args, "review_date", None) or ""
    accommodations = getattr(args, "accommodations", None) or "[]"
    team_members_json = getattr(args, "team_members_json", None) or "[]"
    parent_consent_date = getattr(args, "parent_consent_date", None) or ""

    now = _now_iso()
    current_year = datetime.now().year
    naming_series = get_next_name(conn, "educlaw_k12_504_plan", year=current_year, company_id=company_id)
    plan_id = str(uuid.uuid4())

    conn.execute(
        """INSERT INTO educlaw_k12_504_plan
           (id, naming_series, student_id, meeting_date, disability_description,
            eligibility_basis, plan_start_date, plan_end_date, review_date,
            accommodations, team_members, parent_consent_date, plan_status,
            company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, ?)""",
        (plan_id, naming_series, student_id, meeting_date, disability_description,
         eligibility_basis, plan_start_date, plan_end_date, review_date,
         accommodations, team_members_json, parent_consent_date,
         company_id, now, now, created_by)
    )
    conn.commit()
    audit(conn, SKILL, "add-504-plan", "educlaw_k12_504_plan",
          plan_id, description=f"Created 504 plan {naming_series}")
    return ok({"id": plan_id, "naming_series": naming_series,
               "plan_status": "active", "message": "Section 504 plan created"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: update-504-plan
# ─────────────────────────────────────────────────────────────────────────────

def update_504_plan(conn, args):
    """Update 504 plan accommodations, dates, or status."""
    plan_id = getattr(args, "plan_504_id", None) or getattr(args, "plan_id", None) or None
    if not plan_id:
        return err("--plan-504-id is required")

    if not conn.execute(
        "SELECT id FROM educlaw_k12_504_plan WHERE id = ?", (plan_id,)
    ).fetchone():
        return err(f"504 plan {plan_id} not found")

    updates = {}
    for field in ["meeting_date", "disability_description", "eligibility_basis",
                  "plan_start_date", "plan_end_date", "review_date",
                  "accommodations", "parent_consent_date", "plan_status"]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    # team_members DB column is updated via --team-members-json argparse flag
    team_members_val = getattr(args, "team_members_json", None)
    if team_members_val is not None:
        updates["team_members"] = team_members_val

    if not updates:
        return err("No fields provided to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE educlaw_k12_504_plan SET {set_clause} WHERE id = ?",
        list(updates.values()) + [plan_id]
    )
    conn.commit()
    audit(conn, SKILL, "update-504-plan", "educlaw_k12_504_plan", plan_id)
    return ok({"id": plan_id, "message": "504 plan updated"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: get-active-504-plan
# ─────────────────────────────────────────────────────────────────────────────

def get_active_504_plan(conn, args):
    """Get the currently active 504 plan for a student; FERPA log."""
    student_id = getattr(args, "student_id", None) or None
    user_id = getattr(args, "user_id", None) or ""

    if not student_id:
        return err("--student-id is required")

    row = conn.execute(
        """SELECT * FROM educlaw_k12_504_plan
           WHERE student_id = ? AND plan_status = 'active'
           ORDER BY created_at DESC LIMIT 1""",
        (student_id,)
    ).fetchone()
    if not row:
        return err(f"No active 504 plan found for student {student_id}")

    data = row_to_dict(row)
    data["accommodations"] = _parse_json(data.get("accommodations"), [])
    data["team_members"] = _parse_json(data.get("team_members"), [])

    _log_ferpa(conn, user_id, student_id, "special_education", data["company_id"])
    conn.commit()
    return ok(data)


# ─── ACTIONS registry ────────────────────────────────────────────────────────
ACTIONS = {
    "create-sped-referral": create_sped_referral,
    "update-sped-referral": update_sped_referral,
    "get-sped-referral": get_sped_referral,
    "list-sped-referrals": list_sped_referrals,
    "add-sped-evaluation": add_sped_evaluation,
    "list-sped-evaluations": list_sped_evaluations,
    "record-sped-eligibility": record_sped_eligibility,
    "get-sped-eligibility": get_sped_eligibility,
    "add-iep": add_iep,
    "update-iep": update_iep,
    "activate-iep": activate_iep,
    "add-iep-amendment": amend_iep,
    "get-active-iep": get_active_iep,
    "get-iep": get_iep,
    "list-iep-deadlines": list_iep_deadlines,
    "list-reevaluation-due": list_reevaluation_due,
    "add-iep-goal": add_iep_goal,
    "list-iep-goals": list_iep_goals,
    "add-iep-service": add_iep_service,
    "list-iep-services": list_iep_services,
    "record-iep-service-session": log_iep_service_session,
    "list-iep-service-logs": list_iep_service_logs,
    "get-service-compliance-report": get_service_compliance_report,
    "add-iep-team-member": add_iep_team_member,
    "record-iep-progress": record_iep_progress,
    "generate-iep-progress-report": generate_iep_progress_report,
    "add-504-plan": add_504_plan,
    "update-504-plan": update_504_plan,
    "get-active-504-plan": get_active_504_plan,
}
