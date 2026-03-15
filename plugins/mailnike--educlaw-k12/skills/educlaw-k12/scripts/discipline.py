"""EduClaw K-12 — discipline domain module

Actions: add-discipline-incident, update-discipline-incident, add-discipline-student,
add-discipline-action, complete-discipline-incident, get-discipline-incident,
list-discipline-incidents, get-discipline-history, get-cumulative-suspension-days,
add-manifestation-review, update-manifestation-review, add-pbis-recognition,
add-discipline-notification, generate-discipline-report, generate-discipline-state-report

Imported by scripts/db_query.py.
"""
import json
import os
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
from erpclaw_lib.db import get_connection
from erpclaw_lib.decimal_utils import to_decimal
from erpclaw_lib.naming import get_next_name
from erpclaw_lib.response import ok, err, row_to_dict, rows_to_list
from erpclaw_lib.audit import audit
from erpclaw_lib.query_helpers import resolve_company_id

SKILL = "educlaw-k12"

SUSPENSION_TYPES = {"in_school_suspension", "out_of_school_suspension"}

_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _log_ferpa(conn, user_id, student_id, data_category, company_id,
               access_type="view", access_reason="", is_emergency=False):
    """Insert a FERPA data access log entry. Silently ignores failures."""
    try:
        conn.execute(
            """INSERT INTO educlaw_data_access_log
               (id, user_id, student_id, data_category, access_type, access_reason,
                is_emergency_access, ip_address, company_id, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (str(uuid.uuid4()), user_id or "", student_id, data_category,
             access_type, access_reason, int(is_emergency), "",
             company_id, _now_iso(), user_id or "")
        )
    except Exception:
        pass


def _recalc_cumulative_suspension(conn, discipline_student_id):
    """Recalculate and update cumulative_suspension_days_ytd for a discipline_student.

    Sums all ISS + OSS duration_days across the same academic year for this student.
    Returns the new total as a Decimal string.
    """
    # Get student_id and incident_id from discipline_student
    ds = conn.execute(
        "SELECT student_id, incident_id FROM educlaw_k12_discipline_student WHERE id = ?",
        (discipline_student_id,)
    ).fetchone()
    if not ds:
        return "0"

    student_id = ds["student_id"]
    incident_id = ds["incident_id"]

    # Get academic_year_id from the incident
    inc = conn.execute(
        "SELECT academic_year_id FROM educlaw_k12_discipline_incident WHERE id = ?",
        (incident_id,)
    ).fetchone()
    if not inc:
        return "0"

    academic_year_id = inc["academic_year_id"]

    # Sum all suspension duration_days for this student in this academic year
    rows = conn.execute(
        """SELECT da.duration_days
           FROM educlaw_k12_discipline_action da
           JOIN educlaw_k12_discipline_student ds2 ON da.discipline_student_id = ds2.id
           JOIN educlaw_k12_discipline_incident di ON ds2.incident_id = di.id
           WHERE ds2.student_id = ?
             AND di.academic_year_id = ?
             AND da.action_type IN ('in_school_suspension', 'out_of_school_suspension')""",
        (student_id, academic_year_id)
    ).fetchall()

    total = to_decimal("0")
    for row in rows:
        try:
            total += to_decimal(row["duration_days"] or "0")
        except Exception:
            pass

    total_str = str(total)

    # Update this discipline_student record
    conn.execute(
        "UPDATE educlaw_k12_discipline_student SET cumulative_suspension_days_ytd = ? WHERE id = ?",
        (total_str, discipline_student_id)
    )

    # Check MDR threshold for IDEA-eligible students
    ds_full = conn.execute(
        "SELECT is_idea_eligible FROM educlaw_k12_discipline_student WHERE id = ?",
        (discipline_student_id,)
    ).fetchone()
    if ds_full and ds_full["is_idea_eligible"]:
        if total >= to_decimal("10"):
            conn.execute(
                "UPDATE educlaw_k12_discipline_student SET mdr_required = 1 WHERE id = ?",
                (discipline_student_id,)
            )

    return total_str


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-discipline-incident
# ─────────────────────────────────────────────────────────────────────────────

def add_discipline_incident(conn, args):
    """Create a new discipline incident header record."""
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    incident_date = getattr(args, "incident_date", None) or None
    incident_time = getattr(args, "incident_time", None) or ""
    location = getattr(args, "location", None) or None
    incident_type = getattr(args, "incident_type", None) or None
    severity = getattr(args, "severity", None) or None
    academic_year_id = getattr(args, "academic_year_id", None) or None
    academic_term_id = getattr(args, "academic_term_id", None) or None
    description = getattr(args, "description", None) or ""
    location_detail = getattr(args, "location_detail", None) or ""
    is_reported_to_law_enforcement = int(bool(getattr(args, "is_reported_to_law_enforcement", None) or 0))
    is_mandatory_report = int(bool(getattr(args, "is_mandatory_report", None) or 0))
    mandatory_report_date = getattr(args, "mandatory_report_date", None) or ""
    mandatory_report_agency = getattr(args, "mandatory_report_agency", None) or ""
    is_title_ix = int(bool(getattr(args, "is_title_ix", None) or 0))
    created_by = getattr(args, "user_id", None) or ""

    if not incident_date:
        return err("--incident-date is required")
    if not location:
        return err("--location is required")
    if not incident_type:
        return err("--incident-type is required")
    if not severity:
        return err("--severity is required")
    if not academic_year_id:
        return err("--academic-year-id is required")

    # Validate academic_year_id
    if not conn.execute(
        "SELECT id FROM educlaw_academic_year WHERE id = ?", (academic_year_id,)
    ).fetchone():
        return err(f"Academic year {academic_year_id} not found")

    # Validate optional academic_term_id
    if academic_term_id:
        if not conn.execute(
            "SELECT id FROM educlaw_academic_term WHERE id = ?", (academic_term_id,)
        ).fetchone():
            return err(f"Academic term {academic_term_id} not found")

    now = _now_iso()
    current_year = datetime.now().year
    naming_series = get_next_name(conn, "educlaw_k12_discipline_incident", year=current_year, company_id=company_id)
    incident_id = str(uuid.uuid4())

    conn.execute(
        """INSERT INTO educlaw_k12_discipline_incident
           (id, naming_series, incident_date, incident_time, location, location_detail,
            incident_type, severity, description, is_reported_to_law_enforcement,
            is_mandatory_report, mandatory_report_date, mandatory_report_agency,
            is_title_ix, incident_status, academic_year_id, academic_term_id,
            company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?, ?, ?, ?, ?, ?)""",
        (incident_id, naming_series, incident_date, incident_time, location, location_detail,
         incident_type, severity, description, is_reported_to_law_enforcement,
         is_mandatory_report, mandatory_report_date, mandatory_report_agency,
         is_title_ix, academic_year_id, academic_term_id,
         company_id, now, now, created_by)
    )
    conn.commit()
    audit(conn, SKILL, "add-discipline-incident", "educlaw_k12_discipline_incident",
          incident_id, description=f"Created incident {naming_series}")
    return ok({"id": incident_id, "naming_series": naming_series,
               "incident_status": "open", "message": "Discipline incident created"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: update-discipline-incident
# ─────────────────────────────────────────────────────────────────────────────

def update_discipline_incident(conn, args):
    """Update an open discipline incident."""
    incident_id = getattr(args, "incident_id", None) or None
    if not incident_id:
        return err("--incident-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_k12_discipline_incident WHERE id = ?",
        (incident_id,)
    ).fetchone()
    if not row:
        return err(f"Discipline incident {incident_id} not found")
    if row["incident_status"] == "closed":
        return err("Cannot update a closed incident")

    updates = {}
    for field in ["incident_date", "incident_time", "location", "location_detail",
                  "incident_type", "severity", "description", "mandatory_report_date",
                  "mandatory_report_agency", "reviewed_by"]:
        val = getattr(args, field.replace("_", "_"), None)
        # argparse uses hyphens, convert
        argname = field.replace("_", "_")
        val = getattr(args, argname, None)
        if val is not None:
            updates[field] = val

    for int_field in ["is_reported_to_law_enforcement", "is_mandatory_report", "is_title_ix"]:
        val = getattr(args, int_field, None)
        if val is not None:
            updates[int_field] = int(bool(val))

    incident_status = getattr(args, "incident_status", None) or None
    if incident_status:
        updates["incident_status"] = incident_status

    if not updates:
        return err("No fields provided to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE educlaw_k12_discipline_incident SET {set_clause} WHERE id = ?",
        list(updates.values()) + [incident_id]
    )
    conn.commit()
    audit(conn, SKILL, "update-discipline-incident", "educlaw_k12_discipline_incident",
          incident_id)
    return ok({"id": incident_id, "message": "Discipline incident updated"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-discipline-student
# ─────────────────────────────────────────────────────────────────────────────

def add_discipline_student(conn, args):
    """Add a student's involvement in a discipline incident."""
    incident_id = getattr(args, "incident_id", None) or None
    student_id = getattr(args, "student_id", None) or None
    role = getattr(args, "role", None) or None
    is_idea_eligible = int(bool(getattr(args, "is_idea_eligible", None) or 0))
    notes = getattr(args, "notes", None) or ""
    created_by = getattr(args, "user_id", None) or ""

    if not incident_id:
        return err("--incident-id is required")
    if not student_id:
        return err("--student-id is required")
    if not role:
        return err("--role is required")

    if not conn.execute(
        "SELECT id FROM educlaw_k12_discipline_incident WHERE id = ?", (incident_id,)
    ).fetchone():
        return err(f"Discipline incident {incident_id} not found")

    if not conn.execute(
        "SELECT id FROM educlaw_student WHERE id = ?", (student_id,)
    ).fetchone():
        return err(f"Student {student_id} not found")

    # Check if student already added to this incident
    existing = conn.execute(
        "SELECT id FROM educlaw_k12_discipline_student WHERE incident_id = ? AND student_id = ?",
        (incident_id, student_id)
    ).fetchone()
    if existing:
        return err(f"Student {student_id} already added to incident {incident_id}")

    now = _now_iso()
    ds_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_discipline_student
           (id, incident_id, student_id, role, is_idea_eligible,
            cumulative_suspension_days_ytd, mdr_required, notes, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, '0', 0, ?, ?, ?)""",
        (ds_id, incident_id, student_id, role, is_idea_eligible, notes, now, created_by)
    )
    conn.commit()
    audit(conn, SKILL, "add-discipline-student", "educlaw_k12_discipline_student", ds_id)
    return ok({"id": ds_id, "message": "Student added to discipline incident"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-discipline-action
# ─────────────────────────────────────────────────────────────────────────────

def add_discipline_action(conn, args):
    """Add a consequence/action to a student's incident involvement."""
    discipline_student_id = getattr(args, "discipline_student_id", None) or None
    action_type = getattr(args, "action_type", None) or None
    start_date = getattr(args, "start_date", None) or ""
    end_date = getattr(args, "end_date", None) or ""
    duration_days = getattr(args, "duration_days", None) or "0"
    administered_by = getattr(args, "administered_by", None) or ""
    notes = getattr(args, "notes", None) or ""
    created_by = getattr(args, "user_id", None) or ""

    if not discipline_student_id:
        return err("--discipline-student-id is required")
    if not action_type:
        return err("--action-type is required")

    if not conn.execute(
        "SELECT id FROM educlaw_k12_discipline_student WHERE id = ?",
        (discipline_student_id,)
    ).fetchone():
        return err(f"Discipline student record {discipline_student_id} not found")

    # Validate duration_days is a valid decimal
    try:
        dur = to_decimal(duration_days)
    except Exception:
        return err("--duration-days must be a valid number")

    now = _now_iso()
    action_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_discipline_action
           (id, discipline_student_id, action_type, start_date, end_date,
            duration_days, administered_by, notes, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (action_id, discipline_student_id, action_type, start_date, end_date,
         str(dur), administered_by, notes, now, now, created_by)
    )

    # If suspension type: recalculate cumulative days
    new_cumulative = "0"
    mdr_required = False
    if action_type in SUSPENSION_TYPES:
        new_cumulative = _recalc_cumulative_suspension(conn, discipline_student_id)
        cumulative_dec = to_decimal(new_cumulative)
        ds_row = conn.execute(
            "SELECT is_idea_eligible, mdr_required FROM educlaw_k12_discipline_student WHERE id = ?",
            (discipline_student_id,)
        ).fetchone()
        if ds_row and ds_row["is_idea_eligible"]:
            mdr_required = cumulative_dec >= to_decimal("10")

    conn.commit()
    audit(conn, SKILL, "add-discipline-action", "educlaw_k12_discipline_action", action_id)

    response = {
        "id": action_id,
        "message": "Discipline action added",
        "action_type": action_type,
    }
    if action_type in SUSPENSION_TYPES:
        response["cumulative_suspension_days_ytd"] = new_cumulative
        if mdr_required:
            response["mdr_alert"] = "MDR required: IDEA-eligible student has reached 10+ suspension days"
        elif to_decimal(new_cumulative) >= to_decimal("8"):
            response["mdr_warning"] = "Warning: approaching MDR threshold (8+ suspension days for IDEA-eligible student)"
    return ok(response)



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: complete-discipline-incident
# ─────────────────────────────────────────────────────────────────────────────

def close_discipline_incident(conn, args):
    """Mark incident as closed; set reviewed_by and reviewed_at."""
    incident_id = getattr(args, "incident_id", None) or None
    reviewed_by = getattr(args, "reviewed_by", None) or ""

    if not incident_id:
        return err("--incident-id is required")

    row = conn.execute(
        "SELECT incident_status FROM educlaw_k12_discipline_incident WHERE id = ?",
        (incident_id,)
    ).fetchone()
    if not row:
        return err(f"Discipline incident {incident_id} not found")
    if row["incident_status"] == "closed":
        return err("Incident is already closed")

    now = _now_iso()
    conn.execute(
        """UPDATE educlaw_k12_discipline_incident
           SET incident_status = 'closed', reviewed_by = ?, reviewed_at = ?, updated_at = ?
           WHERE id = ?""",
        (reviewed_by, now, now, incident_id)
    )
    conn.commit()
    audit(conn, SKILL, "complete-discipline-incident", "educlaw_k12_discipline_incident",
          incident_id, description="Incident closed")
    return ok({"id": incident_id, "incident_status": "closed",
               "reviewed_at": now, "message": "Incident closed successfully"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: get-discipline-incident
# ─────────────────────────────────────────────────────────────────────────────

def get_discipline_incident(conn, args):
    """Get a single incident with all student involvements and actions; FERPA log."""
    incident_id = getattr(args, "incident_id", None) or None
    user_id = getattr(args, "user_id", None) or ""

    if not incident_id:
        return err("--incident-id is required")

    incident = conn.execute(
        "SELECT * FROM educlaw_k12_discipline_incident WHERE id = ?",
        (incident_id,)
    ).fetchone()
    if not incident:
        return err(f"Discipline incident {incident_id} not found")

    incident_dict = row_to_dict(incident)
    company_id = incident_dict["company_id"]

    # Get student involvements
    students = conn.execute(
        """SELECT ds.*, s.first_name, s.last_name, s.full_name, s.grade_level
           FROM educlaw_k12_discipline_student ds
           JOIN educlaw_student s ON ds.student_id = s.id
           WHERE ds.incident_id = ?""",
        (incident_id,)
    ).fetchall()

    students_list = []
    for ds in students:
        ds_dict = row_to_dict(ds)
        # Get actions for this student
        actions = conn.execute(
            "SELECT * FROM educlaw_k12_discipline_action WHERE discipline_student_id = ?",
            (ds_dict["id"],)
        ).fetchall()
        ds_dict["actions"] = rows_to_list(actions)
        students_list.append(ds_dict)
        # FERPA log per student
        _log_ferpa(conn, user_id, ds_dict["student_id"], "discipline", company_id)

    incident_dict["students"] = students_list
    conn.commit()  # commit FERPA logs
    return ok(incident_dict)



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-discipline-incidents
# ─────────────────────────────────────────────────────────────────────────────

def list_discipline_incidents(conn, args):
    """List incidents with optional filters."""
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    academic_year_id = getattr(args, "academic_year_id", None) or None
    date_from = getattr(args, "date_from", None) or None
    date_to = getattr(args, "date_to", None) or None
    incident_status = getattr(args, "incident_status", None) or None
    severity = getattr(args, "severity", None) or None
    student_id = getattr(args, "student_id", None) or None
    incident_type = getattr(args, "incident_type", None) or None
    limit = getattr(args, "limit", None) or 50
    offset = getattr(args, "offset", None) or 0

    if student_id:
        # Filter by student involvement
        query = """SELECT DISTINCT di.*
                   FROM educlaw_k12_discipline_incident di
                   JOIN educlaw_k12_discipline_student ds ON di.id = ds.incident_id
                   WHERE di.company_id = ? AND ds.student_id = ?"""
        params = [company_id, student_id]
    else:
        query = "SELECT * FROM educlaw_k12_discipline_incident WHERE company_id = ?"
        params = [company_id]

    if academic_year_id:
        query += " AND di.academic_year_id = ?" if student_id else " AND academic_year_id = ?"
        params.append(academic_year_id)
    if date_from:
        query += " AND di.incident_date >= ?" if student_id else " AND incident_date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND di.incident_date <= ?" if student_id else " AND incident_date <= ?"
        params.append(date_to)
    if incident_status:
        query += " AND di.incident_status = ?" if student_id else " AND incident_status = ?"
        params.append(incident_status)
    if severity:
        query += " AND di.severity = ?" if student_id else " AND severity = ?"
        params.append(severity)
    if incident_type:
        query += " AND di.incident_type = ?" if student_id else " AND incident_type = ?"
        params.append(incident_type)

    query += " ORDER BY incident_date DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()
    return ok({"incidents": rows_to_list(rows), "count": len(rows)})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: get-discipline-history
# ─────────────────────────────────────────────────────────────────────────────

def get_discipline_history(conn, args):
    """Get complete discipline history for a student across all years; FERPA log."""
    student_id = getattr(args, "student_id", None) or None
    user_id = getattr(args, "user_id", None) or ""
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)

    if not student_id:
        return err("--student-id is required")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    incidents_raw = conn.execute(
        """SELECT di.*, ds.id AS ds_id, ds.role, ds.is_idea_eligible,
                  ds.cumulative_suspension_days_ytd, ds.mdr_required, ds.notes AS student_notes
           FROM educlaw_k12_discipline_student ds
           JOIN educlaw_k12_discipline_incident di ON ds.incident_id = di.id
           WHERE ds.student_id = ?
           ORDER BY di.incident_date DESC""",
        (student_id,)
    ).fetchall()

    history = []
    for row in incidents_raw:
        d = row_to_dict(row)
        # Get actions
        actions = conn.execute(
            "SELECT * FROM educlaw_k12_discipline_action WHERE discipline_student_id = ?",
            (d["ds_id"],)
        ).fetchall()
        d["actions"] = rows_to_list(actions)
        history.append(d)

    _log_ferpa(conn, user_id, student_id, "discipline", company_id)
    conn.commit()

    return ok({"student_id": student_id, "incident_count": len(history), "history": history})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: get-cumulative-suspension-days
# ─────────────────────────────────────────────────────────────────────────────

def get_cumulative_suspension_days(conn, args):
    """Get year-to-date total suspension days for a student; flag MDR threshold."""
    student_id = getattr(args, "student_id", None) or None
    academic_year_id = getattr(args, "academic_year_id", None) or None

    if not student_id:
        return err("--student-id is required")
    if not academic_year_id:
        return err("--academic-year-id is required")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    rows = conn.execute(
        """SELECT da.duration_days, da.action_type
           FROM educlaw_k12_discipline_action da
           JOIN educlaw_k12_discipline_student ds ON da.discipline_student_id = ds.id
           JOIN educlaw_k12_discipline_incident di ON ds.incident_id = di.id
           WHERE ds.student_id = ?
             AND di.academic_year_id = ?
             AND da.action_type IN ('in_school_suspension', 'out_of_school_suspension')""",
        (student_id, academic_year_id)
    ).fetchall()

    total = to_decimal("0")
    iss_days = to_decimal("0")
    oss_days = to_decimal("0")
    for row in rows:
        try:
            d = to_decimal(row["duration_days"] or "0")
            total += d
            if row["action_type"] == "in_school_suspension":
                iss_days += d
            else:
                oss_days += d
        except Exception:
            pass

    # Check if student has active IEP
    active_iep = conn.execute(
        """SELECT id FROM educlaw_k12_iep
           WHERE student_id = ? AND iep_status = 'active'""",
        (student_id,)
    ).fetchone()
    is_idea_eligible = bool(active_iep)

    mdr_status = "not_applicable"
    if is_idea_eligible:
        if total >= to_decimal("10"):
            mdr_status = "mdr_required"
        elif total >= to_decimal("8"):
            mdr_status = "approaching_threshold"

    return ok({
        "student_id": student_id,
        "academic_year_id": academic_year_id,
        "total_suspension_days": str(total),
        "iss_days": str(iss_days),
        "oss_days": str(oss_days),
        "is_idea_eligible": is_idea_eligible,
        "mdr_status": mdr_status,
        "mdr_threshold": "10",
        "warning_threshold": "8",
    })



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-manifestation-review
# ─────────────────────────────────────────────────────────────────────────────

def add_manifestation_review(conn, args):
    """Create MDR record linked to discipline incident and active IEP."""
    discipline_student_id = getattr(args, "discipline_student_id", None) or None
    student_id = getattr(args, "student_id", None) or None
    iep_id = getattr(args, "iep_id", None) or None
    mdr_date = getattr(args, "mdr_date", None) or ""
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    created_by = getattr(args, "user_id", None) or ""
    notes = getattr(args, "notes", None) or ""

    if not discipline_student_id:
        return err("--discipline-student-id is required")
    if not student_id:
        return err("--student-id is required")
    if not iep_id:
        return err("--iep-id is required")

    if not conn.execute(
        "SELECT id FROM educlaw_k12_discipline_student WHERE id = ?",
        (discipline_student_id,)
    ).fetchone():
        return err(f"Discipline student record {discipline_student_id} not found")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    if not conn.execute("SELECT id FROM educlaw_k12_iep WHERE id = ?", (iep_id,)).fetchone():
        return err(f"IEP {iep_id} not found")

    now = _now_iso()
    mdr_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_manifestation_review
           (id, discipline_student_id, student_id, iep_id, mdr_date,
            question_1_result, question_2_result, determination, outcome_action,
            fba_required, bip_required, fba_bip_notes, parent_notified_date,
            procedural_safeguards_sent, notes, company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, 'not_determined', 'not_determined', 'pending', 'pending',
                   0, 0, '', '', 0, ?, ?, ?, ?, ?)""",
        (mdr_id, discipline_student_id, student_id, iep_id, mdr_date,
         notes, company_id, now, now, created_by)
    )
    conn.commit()
    audit(conn, SKILL, "add-manifestation-review", "educlaw_k12_manifestation_review", mdr_id)
    return ok({"id": mdr_id, "message": "Manifestation Determination Review created",
               "determination": "pending"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: update-manifestation-review
# ─────────────────────────────────────────────────────────────────────────────

def update_manifestation_review(conn, args):
    """Update MDR with question results, determination, outcome, and parent notification."""
    mdr_id = getattr(args, "mdr_id", None) or None
    if not mdr_id:
        return err("--mdr-id is required")

    if not conn.execute(
        "SELECT id FROM educlaw_k12_manifestation_review WHERE id = ?", (mdr_id,)
    ).fetchone():
        return err(f"Manifestation review {mdr_id} not found")

    updates = {}
    for field in ["mdr_date", "question_1_result", "question_2_result", "determination",
                  "outcome_action", "fba_bip_notes", "parent_notified_date", "notes"]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    for int_field in ["fba_required", "bip_required", "procedural_safeguards_sent"]:
        val = getattr(args, int_field, None)
        if val is not None:
            updates[int_field] = int(bool(val))

    if not updates:
        return err("No fields provided to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE educlaw_k12_manifestation_review SET {set_clause} WHERE id = ?",
        list(updates.values()) + [mdr_id]
    )
    conn.commit()
    audit(conn, SKILL, "update-manifestation-review", "educlaw_k12_manifestation_review", mdr_id)
    return ok({"id": mdr_id, "message": "Manifestation review updated"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-pbis-recognition
# ─────────────────────────────────────────────────────────────────────────────

def add_pbis_recognition(conn, args):
    """Record a positive behavior recognition event for a student.

    Stored as a discipline_incident with incident_type='other_minor', severity='minor',
    and description prefixed with '[PBIS]'. A corresponding discipline_student record
    is also created with role='bystander' (positive recognition context).
    """
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    student_id = getattr(args, "student_id", None) or None
    academic_year_id = getattr(args, "academic_year_id", None) or None
    incident_date = getattr(args, "incident_date", None) or None
    description = getattr(args, "description", None) or ""
    location = getattr(args, "location", None) or "other"
    incident_time = getattr(args, "incident_time", None) or ""
    academic_term_id = getattr(args, "academic_term_id", None) or None
    created_by = getattr(args, "user_id", None) or ""

    if not student_id:
        return err("--student-id is required")
    if not academic_year_id:
        return err("--academic-year-id is required")
    if not incident_date:
        return err("--incident-date is required")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    if not conn.execute(
        "SELECT id FROM educlaw_academic_year WHERE id = ?", (academic_year_id,)
    ).fetchone():
        return err(f"Academic year {academic_year_id} not found")

    pbis_description = f"[PBIS] {description}" if description else "[PBIS Recognition]"
    now = _now_iso()
    current_year = datetime.now().year
    naming_series = get_next_name(conn, "educlaw_k12_discipline_incident", year=current_year, company_id=company_id)
    incident_id = str(uuid.uuid4())

    conn.execute(
        """INSERT INTO educlaw_k12_discipline_incident
           (id, naming_series, incident_date, incident_time, location, location_detail,
            incident_type, severity, description, is_reported_to_law_enforcement,
            is_mandatory_report, mandatory_report_date, mandatory_report_agency,
            is_title_ix, incident_status, academic_year_id, academic_term_id,
            company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, '', 'other_minor', 'minor', ?, 0, 0, '', '',
                   0, 'closed', ?, ?, ?, ?, ?, ?)""",
        (incident_id, naming_series, incident_date, incident_time, location,
         pbis_description, academic_year_id, academic_term_id,
         company_id, now, now, created_by)
    )

    # Add student involvement as recognition recipient
    ds_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_discipline_student
           (id, incident_id, student_id, role, is_idea_eligible,
            cumulative_suspension_days_ytd, mdr_required, notes, created_at, created_by)
           VALUES (?, ?, ?, 'bystander', 0, '0', 0, ?, ?, ?)""",
        (ds_id, incident_id, student_id, "PBIS positive recognition", now, created_by)
    )
    conn.commit()
    audit(conn, SKILL, "add-pbis-recognition", "educlaw_k12_discipline_incident",
          incident_id, description=f"PBIS recognition for student {student_id}")
    return ok({"id": incident_id, "discipline_student_id": ds_id,
               "naming_series": naming_series, "message": "PBIS recognition recorded"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-discipline-notification
# ─────────────────────────────────────────────────────────────────────────────

def notify_guardians_discipline(conn, args):
    """Create educlaw_notification records for all guardians of involved students."""
    incident_id = getattr(args, "incident_id", None) or None
    user_id = getattr(args, "user_id", None) or ""
    message = getattr(args, "message", None) or ""

    if not incident_id:
        return err("--incident-id is required")

    incident = conn.execute(
        "SELECT * FROM educlaw_k12_discipline_incident WHERE id = ?",
        (incident_id,)
    ).fetchone()
    if not incident:
        return err(f"Discipline incident {incident_id} not found")

    company_id = incident["company_id"]
    naming_series = incident["naming_series"]

    # Get all students involved (offenders and victims)
    students = conn.execute(
        """SELECT ds.student_id, ds.role, s.full_name
           FROM educlaw_k12_discipline_student ds
           JOIN educlaw_student s ON ds.student_id = s.id
           WHERE ds.incident_id = ? AND ds.role IN ('offender', 'victim')""",
        (incident_id,)
    ).fetchall()

    notifications_created = 0
    now = _now_iso()

    for student_row in students:
        student_id = student_row["student_id"]
        student_name = student_row["full_name"]

        # Get guardians for this student
        guardians = conn.execute(
            """SELECT sg.guardian_id
               FROM educlaw_student_guardian sg
               WHERE sg.student_id = ? AND sg.receives_communications = 1""",
            (student_id,)
        ).fetchall()

        notif_title = f"Discipline Incident {naming_series} — {student_name}"
        notif_msg = message or (
            f"A discipline incident ({naming_series}) has been recorded involving "
            f"{student_name}. Please contact the school for details."
        )

        for g_row in guardians:
            notif_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO educlaw_notification
                   (id, recipient_type, recipient_id, notification_type, title, message,
                    reference_type, reference_id, is_read, sent_via, sent_at,
                    company_id, created_at, created_by)
                   VALUES (?, 'guardian', ?, 'announcement', ?, ?, 'discipline_incident',
                           ?, 0, 'system', ?, ?, ?, ?)""",
                (notif_id, g_row["guardian_id"], notif_title, notif_msg,
                 incident_id, now, company_id, now, user_id)
            )
            notifications_created += 1

        _log_ferpa(conn, user_id, student_id, "discipline", company_id,
                   access_reason="guardian notification")

    conn.commit()
    return ok({"incident_id": incident_id, "notifications_created": notifications_created,
               "message": f"Created {notifications_created} guardian notification(s)"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: generate-discipline-report
# ─────────────────────────────────────────────────────────────────────────────

def generate_discipline_report(conn, args):
    """School-wide discipline analytics: incidents by type/severity/location."""
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    academic_year_id = getattr(args, "academic_year_id", None) or None
    date_from = getattr(args, "date_from", None) or None
    date_to = getattr(args, "date_to", None) or None

    where_parts = ["di.company_id = ?"]
    params = [company_id]
    if academic_year_id:
        where_parts.append("di.academic_year_id = ?")
        params.append(academic_year_id)
    if date_from:
        where_parts.append("di.incident_date >= ?")
        params.append(date_from)
    if date_to:
        where_parts.append("di.incident_date <= ?")
        params.append(date_to)
    where_clause = " AND ".join(where_parts)

    # Total incidents
    total = conn.execute(
        f"SELECT COUNT(*) as cnt FROM educlaw_k12_discipline_incident di WHERE {where_clause}",
        params
    ).fetchone()["cnt"]

    # By type
    by_type = conn.execute(
        f"""SELECT incident_type, COUNT(*) as cnt
            FROM educlaw_k12_discipline_incident di WHERE {where_clause}
            GROUP BY incident_type ORDER BY cnt DESC""",
        params
    ).fetchall()

    # By severity
    by_severity = conn.execute(
        f"""SELECT severity, COUNT(*) as cnt
            FROM educlaw_k12_discipline_incident di WHERE {where_clause}
            GROUP BY severity ORDER BY cnt DESC""",
        params
    ).fetchall()

    # By location
    by_location = conn.execute(
        f"""SELECT location, COUNT(*) as cnt
            FROM educlaw_k12_discipline_incident di WHERE {where_clause}
            GROUP BY location ORDER BY cnt DESC""",
        params
    ).fetchall()

    # By status
    by_status = conn.execute(
        f"""SELECT incident_status, COUNT(*) as cnt
            FROM educlaw_k12_discipline_incident di WHERE {where_clause}
            GROUP BY incident_status""",
        params
    ).fetchall()

    # PBIS ratio (incidents with [PBIS] prefix)
    pbis_count = conn.execute(
        f"""SELECT COUNT(*) as cnt FROM educlaw_k12_discipline_incident di
            WHERE {where_clause} AND description LIKE '[PBIS]%'""",
        params
    ).fetchone()["cnt"]

    # Top students by incident count
    top_students = conn.execute(
        f"""SELECT ds.student_id, s.full_name, s.grade_level, COUNT(*) as incident_count
            FROM educlaw_k12_discipline_student ds
            JOIN educlaw_k12_discipline_incident di ON ds.incident_id = di.id
            JOIN educlaw_student s ON ds.student_id = s.id
            WHERE {where_clause} AND ds.role = 'offender'
            GROUP BY ds.student_id ORDER BY incident_count DESC LIMIT 10""",
        params
    ).fetchall()

    corrective_total = total - pbis_count
    pbis_ratio = (
        f"{pbis_count}/{corrective_total}"
        if corrective_total > 0
        else f"{pbis_count}/0"
    )

    return ok({
        "company_id": company_id,
        "academic_year_id": academic_year_id,
        "date_range": {"from": date_from, "to": date_to},
        "total_incidents": total,
        "pbis_recognitions": pbis_count,
        "corrective_incidents": corrective_total,
        "pbis_to_corrective_ratio": pbis_ratio,
        "by_type": rows_to_list(by_type),
        "by_severity": rows_to_list(by_severity),
        "by_location": rows_to_list(by_location),
        "by_status": rows_to_list(by_status),
        "top_students_by_incidents": rows_to_list(top_students),
    })



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: generate-discipline-state-report
# ─────────────────────────────────────────────────────────────────────────────

def generate_discipline_state_report(conn, args):
    """State-format discipline report: suspensions/expulsions by grade/disability status."""
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    academic_year_id = getattr(args, "academic_year_id", None) or None

    if not academic_year_id:
        return err("--academic-year-id is required")

    # Suspension actions in this year
    suspension_rows = conn.execute(
        """SELECT da.action_type, da.duration_days,
                  s.grade_level, s.gender,
                  ds.is_idea_eligible
           FROM educlaw_k12_discipline_action da
           JOIN educlaw_k12_discipline_student ds ON da.discipline_student_id = ds.id
           JOIN educlaw_k12_discipline_incident di ON ds.incident_id = di.id
           JOIN educlaw_student s ON ds.student_id = s.id
           WHERE di.company_id = ?
             AND di.academic_year_id = ?
             AND da.action_type IN
               ('in_school_suspension','out_of_school_suspension','expulsion_referral')""",
        (company_id, academic_year_id)
    ).fetchall()

    by_grade = {}
    by_disability = {"idea_eligible": 0, "not_idea_eligible": 0}
    iss_count = 0
    oss_count = 0
    expulsion_count = 0
    total_suspension_days = to_decimal("0")

    for row in suspension_rows:
        grade = row["grade_level"] or "unknown"
        if grade not in by_grade:
            by_grade[grade] = {"iss": 0, "oss": 0, "expulsion_referral": 0}

        if row["action_type"] == "in_school_suspension":
            iss_count += 1
            by_grade[grade]["iss"] += 1
            try:
                total_suspension_days += to_decimal(row["duration_days"] or "0")
            except Exception:
                pass
        elif row["action_type"] == "out_of_school_suspension":
            oss_count += 1
            by_grade[grade]["oss"] += 1
            try:
                total_suspension_days += to_decimal(row["duration_days"] or "0")
            except Exception:
                pass
        elif row["action_type"] == "expulsion_referral":
            expulsion_count += 1
            by_grade[grade]["expulsion_referral"] += 1

        if row["is_idea_eligible"]:
            by_disability["idea_eligible"] += 1
        else:
            by_disability["not_idea_eligible"] += 1

    # MDR records
    mdr_count = conn.execute(
        """SELECT COUNT(*) as cnt FROM educlaw_k12_manifestation_review mr
           JOIN educlaw_k12_discipline_student ds ON mr.discipline_student_id = ds.id
           JOIN educlaw_k12_discipline_incident di ON ds.incident_id = di.id
           WHERE di.company_id = ? AND di.academic_year_id = ?""",
        (company_id, academic_year_id)
    ).fetchone()["cnt"]

    return ok({
        "company_id": company_id,
        "academic_year_id": academic_year_id,
        "report_type": "state_discipline_report",
        "total_iss_incidents": iss_count,
        "total_oss_incidents": oss_count,
        "total_expulsion_referrals": expulsion_count,
        "total_suspension_days": str(total_suspension_days),
        "by_grade_level": by_grade,
        "by_disability_status": by_disability,
        "mdr_proceedings": mdr_count,
    })


# ─── ACTIONS registry ────────────────────────────────────────────────────────
ACTIONS = {
    "add-discipline-incident": add_discipline_incident,
    "update-discipline-incident": update_discipline_incident,
    "add-discipline-student": add_discipline_student,
    "add-discipline-action": add_discipline_action,
    "complete-discipline-incident": close_discipline_incident,
    "get-discipline-incident": get_discipline_incident,
    "list-discipline-incidents": list_discipline_incidents,
    "get-discipline-history": get_discipline_history,
    "get-cumulative-suspension-days": get_cumulative_suspension_days,
    "add-manifestation-review": add_manifestation_review,
    "update-manifestation-review": update_manifestation_review,
    "add-pbis-recognition": add_pbis_recognition,
    "add-discipline-notification": notify_guardians_discipline,
    "generate-discipline-report": generate_discipline_report,
    "generate-discipline-state-report": generate_discipline_state_report,
}
