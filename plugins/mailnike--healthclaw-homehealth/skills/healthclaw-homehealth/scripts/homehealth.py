"""HealthClaw Home Health — home health domain module

Actions for the home health expansion (4 tables, 12 actions).
Imported by db_query.py (unified router).
"""
import json
import os
import sys
import uuid
from decimal import Decimal

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection
    from erpclaw_lib.decimal_utils import to_decimal, round_currency
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
except ImportError:
    pass


# ---- Helpers ----------------------------------------------------------------

def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


VALID_VISIT_TYPES = ("skilled_nursing", "pt", "ot", "st", "aide", "msw")
VALID_VISIT_STATUSES = ("scheduled", "in_progress", "completed", "missed", "cancelled")
VALID_PLAN_STATUSES = ("active", "on_hold", "discharged", "expired", "recertified")
VALID_ASSESSMENT_TYPES = ("soc", "roc", "recert", "transfer", "discharge", "followup")
VALID_AIDE_STATUSES = ("active", "on_hold", "completed", "cancelled")


def _validate_enum(val, choices, label):
    if val not in choices:
        err(f"Invalid {label}: {val}. Must be one of: {', '.join(choices)}")


def _validate_json(val, label):
    """Validate that a string is valid JSON."""
    try:
        json.loads(val)
    except (json.JSONDecodeError, TypeError):
        err(f"--{label} must be valid JSON")


# ---------------------------------------------------------------------------
# 1. add-home-visit
# ---------------------------------------------------------------------------
def add_home_visit(conn, args):
    for req in ("patient_id", "company_id", "clinician_id", "visit_date", "visit_type"):
        if not getattr(args, req, None):
            err(f"--{req.replace('_', '-')} is required")

    # Validate patient exists
    if not conn.execute("SELECT id FROM healthclaw_patient WHERE id = ?", (args.patient_id,)).fetchone():
        err(f"Patient {args.patient_id} not found")

    # Validate clinician (employee) exists
    if not conn.execute("SELECT id FROM employee WHERE id = ?", (args.clinician_id,)).fetchone():
        err(f"Clinician {args.clinician_id} not found")

    _validate_enum(args.visit_type, VALID_VISIT_TYPES, "visit-type")

    visit_status = getattr(args, "visit_status", None) or "scheduled"
    _validate_enum(visit_status, VALID_VISIT_STATUSES, "visit-status")

    mileage = getattr(args, "mileage", None)
    if mileage is not None:
        mileage = str(round_currency(to_decimal(mileage)))

    visit_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute(
        """INSERT INTO healthclaw_home_visit
           (id, company_id, patient_id, clinician_id, visit_date, visit_type,
            start_time, end_time, travel_time_minutes, mileage, visit_status, notes,
            created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (visit_id, args.company_id, args.patient_id, args.clinician_id,
         args.visit_date, args.visit_type,
         getattr(args, "start_time", None), getattr(args, "end_time", None),
         getattr(args, "travel_time_minutes", None), mileage,
         visit_status, getattr(args, "notes", None), now, now)
    )
    audit(conn, "healthclaw_home_visit", visit_id, "add-home-visit", args.company_id)
    conn.commit()
    ok({"id": visit_id, "visit_type": args.visit_type, "visit_date": args.visit_date,
        "initial_status": visit_status})


# ---------------------------------------------------------------------------
# 2. update-home-visit
# ---------------------------------------------------------------------------
def update_home_visit(conn, args):
    visit_id = getattr(args, "home_visit_id", None)
    if not visit_id:
        err("--home-visit-id is required")
    if not conn.execute("SELECT id FROM healthclaw_home_visit WHERE id = ?", (visit_id,)).fetchone():
        err(f"Home visit {visit_id} not found")

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "visit_date": "visit_date", "start_time": "start_time",
        "end_time": "end_time", "notes": "notes",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            updates.append(f"{col_name} = ?"); params.append(val); changed.append(col_name)

    visit_type = getattr(args, "visit_type", None)
    if visit_type:
        _validate_enum(visit_type, VALID_VISIT_TYPES, "visit-type")
        updates.append("visit_type = ?"); params.append(visit_type); changed.append("visit_type")

    visit_status = getattr(args, "visit_status", None)
    if visit_status:
        _validate_enum(visit_status, VALID_VISIT_STATUSES, "visit-status")
        updates.append("visit_status = ?"); params.append(visit_status); changed.append("visit_status")

    travel_time = getattr(args, "travel_time_minutes", None)
    if travel_time is not None:
        updates.append("travel_time_minutes = ?"); params.append(travel_time); changed.append("travel_time_minutes")

    mileage = getattr(args, "mileage", None)
    if mileage is not None:
        mileage = str(round_currency(to_decimal(mileage)))
        updates.append("mileage = ?"); params.append(mileage); changed.append("mileage")

    if not updates:
        err("No fields to update")
    updates.append("updated_at = datetime('now')")
    params.append(visit_id)
    conn.execute(f"UPDATE healthclaw_home_visit SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_home_visit", visit_id, "update-home-visit", getattr(args, "company_id", None))
    conn.commit()
    ok({"id": visit_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 3. list-home-visits
# ---------------------------------------------------------------------------
def list_home_visits(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?"); params.append(args.patient_id)
    if getattr(args, "clinician_id", None):
        where.append("clinician_id = ?"); params.append(args.clinician_id)
    if getattr(args, "visit_type", None):
        where.append("visit_type = ?"); params.append(args.visit_type)
    if getattr(args, "visit_status", None):
        where.append("visit_status = ?"); params.append(args.visit_status)
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_home_visit WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_home_visit WHERE {where_sql} ORDER BY visit_date DESC LIMIT ? OFFSET ?", params
    ).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# 4. add-care-plan
# ---------------------------------------------------------------------------
def add_care_plan(conn, args):
    for req in ("patient_id", "company_id", "start_of_care", "certification_period_start", "certification_period_end"):
        if not getattr(args, req, None):
            err(f"--{req.replace('_', '-')} is required")

    # Validate patient exists
    if not conn.execute("SELECT id FROM healthclaw_patient WHERE id = ?", (args.patient_id,)).fetchone():
        err(f"Patient {args.patient_id} not found")
    # Validate certifying physician if provided
    cert_phys = getattr(args, "certifying_physician_id", None)
    if cert_phys:
        if not conn.execute("SELECT id FROM employee WHERE id = ?", (cert_phys,)).fetchone():
            err(f"Physician {cert_phys} not found")

    frequency = getattr(args, "frequency", None)
    if frequency:
        _validate_json(frequency, "frequency")

    goals = getattr(args, "goals", None)
    if goals:
        _validate_json(goals, "goals")

    plan_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute(
        """INSERT INTO healthclaw_care_plan
           (id, company_id, patient_id, certifying_physician_id,
            start_of_care, certification_period_start, certification_period_end,
            frequency, goals, plan_status, notes, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?)""",
        (plan_id, args.company_id, args.patient_id,
         getattr(args, "certifying_physician_id", None),
         args.start_of_care, args.certification_period_start, args.certification_period_end,
         frequency, goals, getattr(args, "notes", None), now, now)
    )
    audit(conn, "healthclaw_care_plan", plan_id, "add-care-plan", args.company_id)
    conn.commit()
    ok({"id": plan_id, "patient_id": args.patient_id, "start_of_care": args.start_of_care,
        "initial_status": "active"})


# ---------------------------------------------------------------------------
# 5. update-care-plan
# ---------------------------------------------------------------------------
def update_care_plan(conn, args):
    plan_id = getattr(args, "care_plan_id", None)
    if not plan_id:
        err("--care-plan-id is required")
    if not conn.execute("SELECT id FROM healthclaw_care_plan WHERE id = ?", (plan_id,)).fetchone():
        err(f"Care plan {plan_id} not found")

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "certification_period_start": "certification_period_start",
        "certification_period_end": "certification_period_end",
        "notes": "notes",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            updates.append(f"{col_name} = ?"); params.append(val); changed.append(col_name)

    plan_status = getattr(args, "plan_status", None)
    if plan_status:
        _validate_enum(plan_status, VALID_PLAN_STATUSES, "plan-status")
        updates.append("plan_status = ?"); params.append(plan_status); changed.append("plan_status")

    frequency = getattr(args, "frequency", None)
    if frequency:
        _validate_json(frequency, "frequency")
        updates.append("frequency = ?"); params.append(frequency); changed.append("frequency")

    goals = getattr(args, "goals", None)
    if goals:
        _validate_json(goals, "goals")
        updates.append("goals = ?"); params.append(goals); changed.append("goals")

    if not updates:
        err("No fields to update")
    updates.append("updated_at = datetime('now')")
    params.append(plan_id)
    conn.execute(f"UPDATE healthclaw_care_plan SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_care_plan", plan_id, "update-care-plan", getattr(args, "company_id", None))
    conn.commit()
    ok({"id": plan_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 6. get-care-plan
# ---------------------------------------------------------------------------
def get_care_plan(conn, args):
    plan_id = getattr(args, "care_plan_id", None)
    if not plan_id:
        err("--care-plan-id is required")
    row = conn.execute("SELECT * FROM healthclaw_care_plan WHERE id = ?", (plan_id,)).fetchone()
    if not row:
        err(f"Care plan {plan_id} not found")
    data = row_to_dict(row)
    # Parse JSON fields
    for field in ("frequency", "goals"):
        if data.get(field):
            try:
                data[field] = json.loads(data[field])
            except (json.JSONDecodeError, TypeError):
                pass
    ok(data)


# ---------------------------------------------------------------------------
# 7. list-care-plans
# ---------------------------------------------------------------------------
def list_care_plans(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?"); params.append(args.patient_id)
    if getattr(args, "plan_status", None):
        where.append("plan_status = ?"); params.append(args.plan_status)
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_care_plan WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_care_plan WHERE {where_sql} ORDER BY start_of_care DESC LIMIT ? OFFSET ?", params
    ).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# 8. add-oasis-assessment
# ---------------------------------------------------------------------------
def add_oasis_assessment(conn, args):
    for req in ("patient_id", "company_id", "clinician_id", "assessment_type", "assessment_date"):
        if not getattr(args, req, None):
            err(f"--{req.replace('_', '-')} is required")

    # Validate patient exists
    if not conn.execute("SELECT id FROM healthclaw_patient WHERE id = ?", (args.patient_id,)).fetchone():
        err(f"Patient {args.patient_id} not found")

    # Validate clinician (employee) exists
    if not conn.execute("SELECT id FROM employee WHERE id = ?", (args.clinician_id,)).fetchone():
        err(f"Clinician {args.clinician_id} not found")

    _validate_enum(args.assessment_type, VALID_ASSESSMENT_TYPES, "assessment-type")

    m_items = getattr(args, "m_items", None)
    if m_items:
        _validate_json(m_items, "m-items")

    assessment_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute(
        """INSERT INTO healthclaw_oasis_assessment
           (id, company_id, patient_id, clinician_id, assessment_type, assessment_date,
            m_items, notes, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (assessment_id, args.company_id, args.patient_id, args.clinician_id,
         args.assessment_type, args.assessment_date,
         m_items, getattr(args, "notes", None), now, now)
    )
    audit(conn, "healthclaw_oasis_assessment", assessment_id, "add-oasis-assessment", args.company_id)
    conn.commit()
    ok({"id": assessment_id, "assessment_type": args.assessment_type,
        "assessment_date": args.assessment_date})


# ---------------------------------------------------------------------------
# 9. list-oasis-assessments
# ---------------------------------------------------------------------------
def list_oasis_assessments(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?"); params.append(args.patient_id)
    if getattr(args, "assessment_type", None):
        where.append("assessment_type = ?"); params.append(args.assessment_type)
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_oasis_assessment WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_oasis_assessment WHERE {where_sql} ORDER BY assessment_date DESC LIMIT ? OFFSET ?", params
    ).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# 10. add-aide-assignment
# ---------------------------------------------------------------------------
def add_aide_assignment(conn, args):
    for req in ("patient_id", "company_id", "aide_id", "assignment_start"):
        if not getattr(args, req, None):
            err(f"--{req.replace('_', '-')} is required")

    # Validate patient exists
    if not conn.execute("SELECT id FROM healthclaw_patient WHERE id = ?", (args.patient_id,)).fetchone():
        err(f"Patient {args.patient_id} not found")

    # Validate aide (employee) exists
    if not conn.execute("SELECT id FROM employee WHERE id = ?", (args.aide_id,)).fetchone():
        err(f"Aide {args.aide_id} not found")

    days_of_week = getattr(args, "days_of_week", None)
    if days_of_week:
        _validate_json(days_of_week, "days-of-week")

    tasks = getattr(args, "tasks", None)
    if tasks:
        _validate_json(tasks, "tasks")

    supervisor_id = getattr(args, "supervisor_id", None)
    if supervisor_id:
        if not conn.execute("SELECT id FROM employee WHERE id = ?", (supervisor_id,)).fetchone():
            err(f"Supervisor {supervisor_id} not found")

    assign_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute(
        """INSERT INTO healthclaw_aide_assignment
           (id, company_id, patient_id, aide_id, assignment_start, assignment_end,
            days_of_week, visit_time, tasks, supervisor_id, supervision_due_date,
            status, notes, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?)""",
        (assign_id, args.company_id, args.patient_id, args.aide_id,
         args.assignment_start, getattr(args, "assignment_end", None),
         days_of_week, getattr(args, "visit_time", None), tasks,
         supervisor_id, getattr(args, "supervision_due_date", None),
         getattr(args, "notes", None), now, now)
    )
    audit(conn, "healthclaw_aide_assignment", assign_id, "add-aide-assignment", args.company_id)
    conn.commit()
    ok({"id": assign_id, "aide_id": args.aide_id, "assignment_start": args.assignment_start,
        "initial_status": "active"})


# ---------------------------------------------------------------------------
# 11. update-aide-assignment
# ---------------------------------------------------------------------------
def update_aide_assignment(conn, args):
    assign_id = getattr(args, "aide_assignment_id", None)
    if not assign_id:
        err("--aide-assignment-id is required")
    if not conn.execute("SELECT id FROM healthclaw_aide_assignment WHERE id = ?", (assign_id,)).fetchone():
        err(f"Aide assignment {assign_id} not found")

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "assignment_end": "assignment_end",
        "visit_time": "visit_time",
        "supervision_due_date": "supervision_due_date",
        "notes": "notes",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            updates.append(f"{col_name} = ?"); params.append(val); changed.append(col_name)

    status = getattr(args, "status", None)
    if status:
        _validate_enum(status, VALID_AIDE_STATUSES, "status")
        updates.append("status = ?"); params.append(status); changed.append("status")

    days_of_week = getattr(args, "days_of_week", None)
    if days_of_week:
        _validate_json(days_of_week, "days-of-week")
        updates.append("days_of_week = ?"); params.append(days_of_week); changed.append("days_of_week")

    tasks = getattr(args, "tasks", None)
    if tasks:
        _validate_json(tasks, "tasks")
        updates.append("tasks = ?"); params.append(tasks); changed.append("tasks")

    supervisor_id = getattr(args, "supervisor_id", None)
    if supervisor_id:
        if not conn.execute("SELECT id FROM employee WHERE id = ?", (supervisor_id,)).fetchone():
            err(f"Supervisor {supervisor_id} not found")
        updates.append("supervisor_id = ?"); params.append(supervisor_id); changed.append("supervisor_id")

    if not updates:
        err("No fields to update")
    updates.append("updated_at = datetime('now')")
    params.append(assign_id)
    conn.execute(f"UPDATE healthclaw_aide_assignment SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_aide_assignment", assign_id, "update-aide-assignment", getattr(args, "company_id", None))
    conn.commit()
    ok({"id": assign_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 12. list-aide-assignments
# ---------------------------------------------------------------------------
def list_aide_assignments(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?"); params.append(args.patient_id)
    if getattr(args, "aide_id", None):
        where.append("aide_id = ?"); params.append(args.aide_id)
    if getattr(args, "status", None):
        where.append("status = ?"); params.append(args.status)
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_aide_assignment WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_aide_assignment WHERE {where_sql} ORDER BY assignment_start DESC LIMIT ? OFFSET ?", params
    ).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# Action Router
# ---------------------------------------------------------------------------
ACTIONS = {
    "add-home-visit": add_home_visit,
    "update-home-visit": update_home_visit,
    "list-home-visits": list_home_visits,
    "add-care-plan": add_care_plan,
    "update-care-plan": update_care_plan,
    "get-care-plan": get_care_plan,
    "list-care-plans": list_care_plans,
    "add-oasis-assessment": add_oasis_assessment,
    "list-oasis-assessments": list_oasis_assessments,
    "add-aide-assignment": add_aide_assignment,
    "update-aide-assignment": update_aide_assignment,
    "list-aide-assignments": list_aide_assignments,
}
