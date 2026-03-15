"""EduClaw State Reporting — discipline domain module

CRDC-aligned discipline incident tracking: incidents, student involvement,
disciplinary actions (ISS/OSS/expulsion), MDR workflow, discipline summary reports.

Imported by db_query.py (unified router).
"""
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection
    from erpclaw_lib.response import ok, err
    from erpclaw_lib.audit import audit
    from erpclaw_lib.naming import get_next_name
    import erpclaw_lib.naming as _naming_lib
    # Register educlaw-statereport discipline naming series
    _naming_lib.ENTITY_PREFIXES.setdefault("INC", "INC-")
except ImportError:
    pass

SKILL = "educlaw-statereport"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

VALID_INCIDENT_TYPES = (
    "bullying", "harassment_race", "harassment_sex", "harassment_disability",
    "harassment_other", "drug_alcohol", "physical_assault_student",
    "physical_assault_staff", "weapons_firearm", "weapons_other",
    "vandalism", "robbery", "sexual_offense", "restraint", "seclusion",
    "insubordination", "other"
)
VALID_CAMPUS_LOCATIONS = (
    "classroom", "hallway", "cafeteria", "restroom", "playground",
    "gymnasium", "school_bus", "off_campus", "online", "other", ""
)
VALID_ROLES = ("offender", "victim", "witness")
VALID_ACTION_TYPES = (
    "iss", "oss_1_10", "oss_gt10", "expulsion_with_services",
    "expulsion_without_services", "alternative_placement",
    "law_enforcement_referral", "school_related_arrest", "no_action"
)
VALID_MDR_OUTCOMES = ("manifestation", "not_manifestation", "not_required", "pending", "")


# ─────────────────────────────────────────────────────────────────────────────
# DISCIPLINE INCIDENT
# ─────────────────────────────────────────────────────────────────────────────

def add_discipline_incident(conn, args):
    company_id = getattr(args, "company_id", None)
    school_year = getattr(args, "school_year", None)
    incident_date = getattr(args, "incident_date", None)
    incident_type = getattr(args, "incident_type", None)

    if not company_id:
        err("--company-id is required")
    if not school_year:
        err("--school-year is required")
    if not incident_date:
        err("--incident-date is required")
    if not incident_type:
        err("--incident-type is required")
    if incident_type not in VALID_INCIDENT_TYPES:
        err(f"--incident-type must be one of: {', '.join(VALID_INCIDENT_TYPES)}")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    campus_location = getattr(args, "campus_location", None) or ""
    if campus_location and campus_location not in VALID_CAMPUS_LOCATIONS:
        err(f"--campus-location must be one of: {', '.join(VALID_CAMPUS_LOCATIONS)}")

    incident_id = str(uuid.uuid4())
    naming_series = get_next_name(conn, "INC", int(school_year), company_id)
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO sr_discipline_incident
               (id, naming_series, company_id, school_year, incident_date, incident_time,
                incident_type, incident_description, campus_location, reported_by,
                student_count_involved, created_at, updated_at, created_by)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (incident_id, naming_series, company_id, int(school_year),
             incident_date,
             getattr(args, "incident_time", None) or "",
             incident_type,
             getattr(args, "incident_description", None) or "",
             campus_location,
             getattr(args, "reported_by", None) or "",
             0, now, now, getattr(args, "user_id", None) or "")
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        err(f"Cannot create discipline incident: {e}")

    audit(conn, "sr_discipline_incident", incident_id, "INSERT", getattr(args, "user_id", None) or "")
    ok({"id": incident_id, "naming_series": naming_series, "message": "Discipline incident created"})


def update_discipline_incident(conn, args):
    incident_id = getattr(args, "incident_id", None)
    if not incident_id:
        err("--incident-id is required")

    row = conn.execute("SELECT id FROM sr_discipline_incident WHERE id = ?", (incident_id,)).fetchone()
    if not row:
        err(f"Discipline incident {incident_id} not found")

    updates = {}
    for field in [
        "incident_type", "incident_description", "campus_location",
        "incident_date", "incident_time", "reported_by"
    ]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    if not updates:
        err("No fields to update")

    if "incident_type" in updates and updates["incident_type"] not in VALID_INCIDENT_TYPES:
        err(f"--incident-type must be one of: {', '.join(VALID_INCIDENT_TYPES)}")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE sr_discipline_incident SET {set_clause} WHERE id = ?",
        list(updates.values()) + [incident_id]
    )
    conn.commit()
    audit(conn, "sr_discipline_incident", incident_id, "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": incident_id, "message": "Discipline incident updated"})


def get_discipline_incident(conn, args):
    incident_id = getattr(args, "incident_id", None)
    if not incident_id:
        err("--incident-id is required")

    row = conn.execute("SELECT * FROM sr_discipline_incident WHERE id = ?", (incident_id,)).fetchone()
    if not row:
        err(f"Discipline incident {incident_id} not found")

    incident = dict(row)

    # Get students involved
    students = conn.execute(
        """SELECT ds.*, s.first_name, s.last_name, s.full_name
           FROM sr_discipline_student ds
           JOIN educlaw_student s ON s.id = ds.student_id
           WHERE ds.incident_id = ?""",
        (incident_id,)
    ).fetchall()
    incident["students"] = [dict(s) for s in students]

    # Get actions
    actions = conn.execute(
        "SELECT * FROM sr_discipline_action WHERE incident_id = ? ORDER BY created_at",
        (incident_id,)
    ).fetchall()
    incident["actions"] = [dict(a) for a in actions]

    ok(incident)


def list_discipline_incidents(conn, args):
    company_id = getattr(args, "company_id", None)
    if not company_id:
        err("--company-id is required")

    conditions = ["company_id = ?"]
    params = [company_id]

    school_year = getattr(args, "school_year", None)
    if school_year:
        conditions.append("school_year = ?")
        params.append(int(school_year))

    incident_type = getattr(args, "incident_type", None)
    if incident_type:
        conditions.append("incident_type = ?")
        params.append(incident_type)

    date_from = getattr(args, "date_from", None)
    if date_from:
        conditions.append("incident_date >= ?")
        params.append(date_from)

    date_to = getattr(args, "date_to", None)
    if date_to:
        conditions.append("incident_date <= ?")
        params.append(date_to)

    where = " AND ".join(conditions)
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)

    rows = conn.execute(
        f"SELECT * FROM sr_discipline_incident WHERE {where} ORDER BY incident_date DESC LIMIT ? OFFSET ?",
        params + [limit, offset]
    ).fetchall()

    ok({"incidents": [dict(r) for r in rows], "count": len(rows)})


def delete_discipline_incident(conn, args):
    incident_id = getattr(args, "incident_id", None)
    if not incident_id:
        err("--incident-id is required")

    row = conn.execute("SELECT id FROM sr_discipline_incident WHERE id = ?", (incident_id,)).fetchone()
    if not row:
        err(f"Discipline incident {incident_id} not found")

    # Block delete if students are attached
    student_count = conn.execute(
        "SELECT COUNT(*) FROM sr_discipline_student WHERE incident_id = ?", (incident_id,)
    ).fetchone()[0]
    if student_count > 0:
        err(f"Cannot delete incident with {student_count} student(s) attached. Remove students first.")

    conn.execute("DELETE FROM sr_discipline_incident WHERE id = ?", (incident_id,))
    conn.commit()
    audit(conn, "sr_discipline_incident", incident_id, "DELETE", getattr(args, "user_id", None) or "")
    ok({"id": incident_id, "message": "Discipline incident deleted"})


# ─────────────────────────────────────────────────────────────────────────────
# DISCIPLINE STUDENT (junction)
# ─────────────────────────────────────────────────────────────────────────────

def add_discipline_student(conn, args):
    incident_id = getattr(args, "incident_id", None)
    student_id = getattr(args, "student_id", None)
    role = getattr(args, "role", None)
    company_id = getattr(args, "company_id", None)

    if not incident_id:
        err("--incident-id is required")
    if not student_id:
        err("--student-id is required")
    if not role:
        err("--role is required")
    if role not in VALID_ROLES:
        err(f"--role must be one of: {', '.join(VALID_ROLES)}")
    if not company_id:
        err("--company-id is required")

    if not conn.execute("SELECT id FROM sr_discipline_incident WHERE id = ?", (incident_id,)).fetchone():
        err(f"Discipline incident {incident_id} not found")
    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        err(f"Student {student_id} not found")

    # Auto-populate IDEA and 504 flags from sr_student_supplement
    supp = conn.execute(
        "SELECT is_sped, is_504 FROM sr_student_supplement WHERE student_id = ?",
        (student_id,)
    ).fetchone()
    is_idea = int(supp["is_sped"]) if supp else 0
    is_504 = int(supp["is_504"]) if supp else 0

    # Override if explicitly provided
    if getattr(args, "is_idea_student", None) is not None:
        is_idea = int(getattr(args, "is_idea_student", None))
    if getattr(args, "is_504_student", None) is not None:
        is_504 = int(getattr(args, "is_504_student", None))

    ds_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO sr_discipline_student
               (id, incident_id, student_id, role, is_idea_student, is_504_student,
                company_id, created_at, created_by)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (ds_id, incident_id, student_id, role, is_idea, is_504,
             company_id, now, getattr(args, "user_id", None) or "")
        )
        # Update student_count_involved on incident
        conn.execute(
            """UPDATE sr_discipline_incident
               SET student_count_involved = (
                   SELECT COUNT(*) FROM sr_discipline_student WHERE incident_id = ?
               ), updated_at = ?
               WHERE id = ?""",
            (incident_id, now, incident_id)
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        err(f"Cannot add student to incident: {e}")

    audit(conn, "sr_discipline_student", ds_id, "INSERT", getattr(args, "user_id", None) or "")
    ok({"id": ds_id, "incident_id": incident_id, "student_id": student_id,
        "is_idea_student": is_idea, "is_504_student": is_504,
        "message": "Student added to discipline incident"})


def update_discipline_student(conn, args):
    discipline_student_id = getattr(args, "discipline_student_id", None)
    if not discipline_student_id:
        err("--discipline-student-id is required")

    row = conn.execute(
        "SELECT id FROM sr_discipline_student WHERE id = ?", (discipline_student_id,)
    ).fetchone()
    if not row:
        err(f"Discipline student record {discipline_student_id} not found")

    updates = {}
    role = getattr(args, "role", None)
    if role is not None:
        if role not in VALID_ROLES:
            err(f"--role must be one of: {', '.join(VALID_ROLES)}")
        updates["role"] = role

    for field in ["is_idea_student", "is_504_student"]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = int(val)

    if not updates:
        err("No fields to update")

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE sr_discipline_student SET {set_clause} WHERE id = ?",
        list(updates.values()) + [discipline_student_id]
    )
    conn.commit()
    audit(conn, "sr_discipline_student", discipline_student_id, "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": discipline_student_id, "message": "Discipline student record updated"})


def remove_discipline_student(conn, args):
    discipline_student_id = getattr(args, "discipline_student_id", None)
    if not discipline_student_id:
        err("--discipline-student-id is required")

    row = conn.execute(
        "SELECT id, incident_id FROM sr_discipline_student WHERE id = ?",
        (discipline_student_id,)
    ).fetchone()
    if not row:
        err(f"Discipline student record {discipline_student_id} not found")

    incident_id = row["incident_id"]
    now = _now_iso()

    # Cascade delete their actions
    conn.execute(
        "DELETE FROM sr_discipline_action WHERE discipline_student_id = ?",
        (discipline_student_id,)
    )
    conn.execute("DELETE FROM sr_discipline_student WHERE id = ?", (discipline_student_id,))

    # Update student count
    conn.execute(
        """UPDATE sr_discipline_incident
           SET student_count_involved = (
               SELECT COUNT(*) FROM sr_discipline_student WHERE incident_id = ?
           ), updated_at = ?
           WHERE id = ?""",
        (incident_id, now, incident_id)
    )
    conn.commit()
    audit(conn, "sr_discipline_student", discipline_student_id, "DELETE", getattr(args, "user_id", None) or "")
    ok({"id": discipline_student_id, "message": "Student removed from incident"})


def list_discipline_students(conn, args):
    incident_id = getattr(args, "incident_id", None)
    if not incident_id:
        err("--incident-id is required")

    rows = conn.execute(
        """SELECT ds.*, s.first_name, s.last_name, s.full_name, s.grade_level
           FROM sr_discipline_student ds
           JOIN educlaw_student s ON s.id = ds.student_id
           WHERE ds.incident_id = ?
           ORDER BY ds.role, s.last_name""",
        (incident_id,)
    ).fetchall()

    ok({"students": [dict(r) for r in rows], "count": len(rows)})


# ─────────────────────────────────────────────────────────────────────────────
# DISCIPLINE ACTION
# ─────────────────────────────────────────────────────────────────────────────

def add_discipline_action(conn, args):
    discipline_student_id = getattr(args, "discipline_student_id", None)
    action_type = getattr(args, "action_type", None)
    company_id = getattr(args, "company_id", None)

    if not discipline_student_id:
        err("--discipline-student-id is required")
    if not action_type:
        err("--action-type is required")
    if action_type not in VALID_ACTION_TYPES:
        err(f"--action-type must be one of: {', '.join(VALID_ACTION_TYPES)}")
    if not company_id:
        err("--company-id is required")

    ds_row = conn.execute(
        "SELECT id, incident_id, student_id, is_idea_student FROM sr_discipline_student WHERE id = ?",
        (discipline_student_id,)
    ).fetchone()
    if not ds_row:
        err(f"Discipline student record {discipline_student_id} not found")

    incident_id = ds_row["incident_id"]
    student_id = ds_row["student_id"]
    is_idea = int(ds_row["is_idea_student"])

    days_removed = int(getattr(args, "days_removed", None) or 0)
    if days_removed < 0:
        err("--days-removed cannot be negative")

    # Auto-set mdr_required: IDEA student + days_removed > 10
    mdr_required = 0
    if is_idea and days_removed > 10:
        mdr_required = 1

    # Allow override
    if getattr(args, "mdr_required", None) is not None:
        mdr_required = int(getattr(args, "mdr_required", None))

    mdr_outcome = getattr(args, "mdr_outcome", None) or ""
    if mdr_outcome and mdr_outcome not in VALID_MDR_OUTCOMES:
        err(f"--mdr-outcome must be one of: {', '.join(VALID_MDR_OUTCOMES)}")

    action_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO sr_discipline_action
               (id, discipline_student_id, incident_id, student_id, action_type,
                start_date, end_date, days_removed, alternative_services_provided,
                alternative_services_description, mdr_required, mdr_outcome, mdr_date,
                company_id, created_at, updated_at, created_by)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (action_id, discipline_student_id, incident_id, student_id, action_type,
             getattr(args, "start_date", None) or "",
             getattr(args, "end_date", None) or "",
             days_removed,
             int(getattr(args, "alternative_services_provided", None) or 0),
             getattr(args, "alternative_services_description", None) or "",
             mdr_required, mdr_outcome,
             getattr(args, "mdr_date", None) or "",
             company_id, now, now, getattr(args, "user_id", None) or "")
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        err(f"Cannot create discipline action: {e}")

    audit(conn, "sr_discipline_action", action_id, "INSERT", getattr(args, "user_id", None) or "")
    ok({"id": action_id, "action_type": action_type, "mdr_required": mdr_required,
        "message": "Discipline action added"})


def update_discipline_action(conn, args):
    action_id = getattr(args, "action_id", None)
    if not action_id:
        err("--action-id is required")

    row = conn.execute("SELECT id FROM sr_discipline_action WHERE id = ?", (action_id,)).fetchone()
    if not row:
        err(f"Discipline action {action_id} not found")

    updates = {}
    for field in [
        "action_type", "start_date", "end_date", "days_removed",
        "alternative_services_provided", "alternative_services_description",
        "mdr_required", "mdr_outcome", "mdr_date"
    ]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    if "action_type" in updates and updates["action_type"] not in VALID_ACTION_TYPES:
        err(f"--action-type must be one of: {', '.join(VALID_ACTION_TYPES)}")
    if "mdr_outcome" in updates and updates["mdr_outcome"] not in VALID_MDR_OUTCOMES:
        err(f"--mdr-outcome must be one of: {', '.join(VALID_MDR_OUTCOMES)}")

    if not updates:
        err("No fields to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE sr_discipline_action SET {set_clause} WHERE id = ?",
        list(updates.values()) + [action_id]
    )
    conn.commit()
    audit(conn, "sr_discipline_action", action_id, "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": action_id, "message": "Discipline action updated"})


def record_mdr_outcome(conn, args):
    action_id = getattr(args, "action_id", None)
    mdr_outcome = getattr(args, "mdr_outcome", None)
    mdr_date = getattr(args, "mdr_date", None)

    if not action_id:
        err("--action-id is required")
    if not mdr_outcome:
        err("--mdr-outcome is required")
    if mdr_outcome not in VALID_MDR_OUTCOMES:
        err(f"--mdr-outcome must be one of: {', '.join(VALID_MDR_OUTCOMES)}")

    row = conn.execute("SELECT id FROM sr_discipline_action WHERE id = ?", (action_id,)).fetchone()
    if not row:
        err(f"Discipline action {action_id} not found")

    now = _now_iso()
    conn.execute(
        """UPDATE sr_discipline_action
           SET mdr_outcome = ?, mdr_date = ?, updated_at = ?
           WHERE id = ?""",
        (mdr_outcome, mdr_date or now[:10], now, action_id)
    )
    conn.commit()
    audit(conn, "sr_discipline_action", action_id, "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": action_id, "mdr_outcome": mdr_outcome, "message": "MDR outcome recorded"})


def get_discipline_action(conn, args):
    action_id = getattr(args, "action_id", None)
    if not action_id:
        err("--action-id is required")

    row = conn.execute("SELECT * FROM sr_discipline_action WHERE id = ?", (action_id,)).fetchone()
    if not row:
        err(f"Discipline action {action_id} not found")

    ok(dict(row))


def list_discipline_actions(conn, args):
    conditions = []
    params = []

    student_id = getattr(args, "student_id", None)
    if student_id:
        conditions.append("student_id = ?")
        params.append(student_id)

    company_id = getattr(args, "company_id", None)
    if company_id:
        conditions.append("company_id = ?")
        params.append(company_id)

    action_type = getattr(args, "action_type", None)
    if action_type:
        conditions.append("action_type = ?")
        params.append(action_type)

    mdr_required = getattr(args, "mdr_required", None)
    if mdr_required is not None:
        conditions.append("mdr_required = ?")
        params.append(int(mdr_required))

    incident_id = getattr(args, "incident_id", None)
    if incident_id:
        conditions.append("incident_id = ?")
        params.append(incident_id)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)

    rows = conn.execute(
        f"SELECT * FROM sr_discipline_action {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [limit, offset]
    ).fetchall()

    ok({"actions": [dict(r) for r in rows], "count": len(rows)})


def get_discipline_summary(conn, args):
    company_id = getattr(args, "company_id", None)
    school_year = getattr(args, "school_year", None)

    if not company_id:
        err("--company-id is required")
    if not school_year:
        err("--school-year is required")

    # CRDC-formatted summary: counts by action_type × race × sex × IDEA status
    rows = conn.execute(
        """SELECT
               da.action_type,
               ss.race_federal_rollup,
               s.gender,
               ds.is_idea_student,
               COUNT(*) as count,
               SUM(da.days_removed) as total_days_removed
           FROM sr_discipline_action da
           JOIN sr_discipline_student ds ON ds.id = da.discipline_student_id
           JOIN educlaw_student s ON s.id = da.student_id
           LEFT JOIN sr_student_supplement ss ON ss.student_id = da.student_id
           JOIN sr_discipline_incident di ON di.id = da.incident_id
           WHERE da.company_id = ? AND di.school_year = ?
           GROUP BY da.action_type, ss.race_federal_rollup, s.gender, ds.is_idea_student
           ORDER BY da.action_type, ss.race_federal_rollup""",
        (company_id, int(school_year))
    ).fetchall()

    # Total incident count
    incident_count = conn.execute(
        "SELECT COUNT(*) FROM sr_discipline_incident WHERE company_id = ? AND school_year = ?",
        (company_id, int(school_year))
    ).fetchone()[0]

    # Total students involved
    student_count = conn.execute(
        """SELECT COUNT(DISTINCT ds.student_id)
           FROM sr_discipline_student ds
           JOIN sr_discipline_incident di ON di.id = ds.incident_id
           WHERE di.company_id = ? AND di.school_year = ?""",
        (company_id, int(school_year))
    ).fetchone()[0]

    # MDR required but pending count
    mdr_pending = conn.execute(
        """SELECT COUNT(*) FROM sr_discipline_action da
           JOIN sr_discipline_incident di ON di.id = da.incident_id
           WHERE da.company_id = ? AND di.school_year = ?
           AND da.mdr_required = 1 AND (da.mdr_outcome = '' OR da.mdr_outcome = 'pending')""",
        (company_id, int(school_year))
    ).fetchone()[0]

    summary_rows = []
    for r in rows:
        cell = dict(r)
        # Apply small-cell suppression N<10
        if cell["count"] < 10:
            cell["suppressed"] = True
        summary_rows.append(cell)

    ok({
        "school_year": int(school_year),
        "company_id": company_id,
        "total_incidents": incident_count,
        "total_students_involved": student_count,
        "mdr_pending_count": mdr_pending,
        "summary": summary_rows
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────
ACTIONS = {
    "add-discipline-incident": add_discipline_incident,
    "update-discipline-incident": update_discipline_incident,
    "get-discipline-incident": get_discipline_incident,
    "list-discipline-incidents": list_discipline_incidents,
    "delete-discipline-incident": delete_discipline_incident,
    "add-discipline-student": add_discipline_student,
    "update-discipline-student": update_discipline_student,
    "delete-discipline-student": remove_discipline_student,
    "list-discipline-students": list_discipline_students,
    "add-discipline-action": add_discipline_action,
    "update-discipline-action": update_discipline_action,
    "record-mdr-outcome": record_mdr_outcome,
    "get-discipline-action": get_discipline_action,
    "list-discipline-actions": list_discipline_actions,
    "get-discipline-summary": get_discipline_summary,
}
