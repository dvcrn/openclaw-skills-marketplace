"""EduClaw K-12 — health_records domain module

Actions: add-health-profile, update-health-profile, get-health-profile,
submit-health-profile-verification, get-emergency-health-info, add-office-visit,
list-office-visits, get-office-visit, add-student-medication,
update-student-medication, list-student-medications, record-medication-admin,
list-medication-logs, add-immunization, add-immunization-waiver,
update-immunization-waiver, get-immunization-record,
get-immunization-compliance, list-health-alerts, generate-immunization-report

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
from erpclaw_lib.response import ok, err, row_to_dict, rows_to_list
from erpclaw_lib.audit import audit
from erpclaw_lib.query_helpers import resolve_company_id

SKILL = "educlaw-k12"

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


def _parse_json_field(value, field_name, default=None):
    """Parse a JSON field, returning default on failure."""
    if value is None:
        return default if default is not None else []
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else []




# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-health-profile
# ─────────────────────────────────────────────────────────────────────────────

def add_health_profile(conn, args):
    """Create student health profile with allergies, conditions, physician info."""
    student_id = getattr(args, "student_id", None) or None
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    created_by = getattr(args, "user_id", None) or ""

    if not student_id:
        return err("--student-id is required")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    # Check for existing profile
    existing = conn.execute(
        "SELECT id FROM educlaw_k12_health_profile WHERE student_id = ?", (student_id,)
    ).fetchone()
    if existing:
        return err(f"Health profile already exists for student {student_id}")

    allergies = getattr(args, "allergies", None) or "[]"
    chronic_conditions = getattr(args, "chronic_conditions", None) or "[]"
    physician_name = getattr(args, "physician_name", None) or ""
    physician_phone = getattr(args, "physician_phone", None) or ""
    physician_address = getattr(args, "physician_address", None) or ""
    health_insurance_carrier = getattr(args, "health_insurance_carrier", None) or ""
    health_insurance_id = getattr(args, "health_insurance_id", None) or ""
    blood_type = getattr(args, "blood_type", None) or "unknown"
    height_cm = getattr(args, "height_cm", None) or ""
    weight_kg = getattr(args, "weight_kg", None) or ""
    activity_restriction = getattr(args, "activity_restriction", None) or "none"
    activity_restriction_notes = getattr(args, "activity_restriction_notes", None) or ""
    is_provisional_immunization = int(bool(
        getattr(args, "is_provisional_immunization", None) or 0))
    provisional_enrollment_end_date = getattr(args, "provisional_enrollment_end_date", None) or ""
    is_mckinney_vento = int(bool(getattr(args, "is_mckinney_vento", None) or 0))
    emergency_instructions = getattr(args, "emergency_instructions", None) or ""
    vision_screening_date = getattr(args, "vision_screening_date", None) or ""
    hearing_screening_date = getattr(args, "hearing_screening_date", None) or ""
    dental_screening_date = getattr(args, "dental_screening_date", None) or ""

    # Validate JSON fields
    _parse_json_field(allergies, "allergies")
    _parse_json_field(chronic_conditions, "chronic_conditions")

    now = _now_iso()
    profile_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_health_profile
           (id, student_id, allergies, chronic_conditions, physician_name, physician_phone,
            physician_address, health_insurance_carrier, health_insurance_id, blood_type,
            height_cm, weight_kg, vision_screening_date, hearing_screening_date,
            dental_screening_date, activity_restriction, activity_restriction_notes,
            is_provisional_immunization, provisional_enrollment_end_date, is_mckinney_vento,
            emergency_instructions, profile_status, last_verified_date, last_verified_by,
            company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                   'incomplete', '', '', ?, ?, ?, ?)""",
        (profile_id, student_id, allergies, chronic_conditions, physician_name,
         physician_phone, physician_address, health_insurance_carrier, health_insurance_id,
         blood_type, height_cm, weight_kg, vision_screening_date, hearing_screening_date,
         dental_screening_date, activity_restriction, activity_restriction_notes,
         is_provisional_immunization, provisional_enrollment_end_date, is_mckinney_vento,
         emergency_instructions, company_id, now, now, created_by)
    )
    conn.commit()
    audit(conn, SKILL, "add-health-profile", "educlaw_k12_health_profile", profile_id)
    return ok({"id": profile_id, "student_id": student_id,
               "profile_status": "incomplete", "message": "Health profile created"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: update-health-profile
# ─────────────────────────────────────────────────────────────────────────────

def update_health_profile(conn, args):
    """Update existing health profile."""
    student_id = getattr(args, "student_id", None) or None
    profile_id = getattr(args, "health_profile_id", None) or None

    if not student_id and not profile_id:
        return err("--student-id or --health-profile-id is required")

    if student_id:
        row = conn.execute(
            "SELECT * FROM educlaw_k12_health_profile WHERE student_id = ?",
            (student_id,)
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT * FROM educlaw_k12_health_profile WHERE id = ?",
            (profile_id,)
        ).fetchone()

    if not row:
        return err("Health profile not found")

    profile_id = row["id"]
    updates = {}

    str_fields = [
        "physician_name", "physician_phone", "physician_address",
        "health_insurance_carrier", "health_insurance_id", "blood_type",
        "height_cm", "weight_kg", "activity_restriction", "activity_restriction_notes",
        "vision_screening_date", "hearing_screening_date", "dental_screening_date",
        "provisional_enrollment_end_date", "emergency_instructions",
        "profile_status", "last_verified_date", "last_verified_by",
        "allergies", "chronic_conditions",
    ]
    for field in str_fields:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    for int_field in ["is_provisional_immunization", "is_mckinney_vento"]:
        val = getattr(args, int_field, None)
        if val is not None:
            updates[int_field] = int(bool(val))

    if not updates:
        return err("No fields provided to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE educlaw_k12_health_profile SET {set_clause} WHERE id = ?",
        list(updates.values()) + [profile_id]
    )
    conn.commit()
    audit(conn, SKILL, "update-health-profile", "educlaw_k12_health_profile", profile_id)
    return ok({"id": profile_id, "message": "Health profile updated"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: get-health-profile
# ─────────────────────────────────────────────────────────────────────────────

def get_health_profile(conn, args):
    """Get student health profile; FERPA log."""
    student_id = getattr(args, "student_id", None) or None
    user_id = getattr(args, "user_id", None) or ""

    if not student_id:
        return err("--student-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_k12_health_profile WHERE student_id = ?",
        (student_id,)
    ).fetchone()
    if not row:
        return err(f"Health profile not found for student {student_id}")

    data = row_to_dict(row)
    # Parse JSON fields
    data["allergies"] = _parse_json_field(data.get("allergies"), "allergies")
    data["chronic_conditions"] = _parse_json_field(data.get("chronic_conditions"), "chronic_conditions")

    _log_ferpa(conn, user_id, student_id, "health", data["company_id"])
    conn.commit()
    return ok(data)



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: submit-health-profile-verification
# ─────────────────────────────────────────────────────────────────────────────

def verify_health_profile(conn, args):
    """Nurse sets profile_status='active', last_verified_date, last_verified_by."""
    student_id = getattr(args, "student_id", None) or None
    last_verified_by = getattr(args, "last_verified_by", None) or (
        getattr(args, "user_id", None) or "")
    last_verified_date = getattr(args, "last_verified_date", None) or (
        datetime.now().strftime("%Y-%m-%d"))

    if not student_id:
        return err("--student-id is required")

    row = conn.execute(
        "SELECT id FROM educlaw_k12_health_profile WHERE student_id = ?",
        (student_id,)
    ).fetchone()
    if not row:
        return err(f"Health profile not found for student {student_id}")

    profile_id = row["id"]
    now = _now_iso()
    conn.execute(
        """UPDATE educlaw_k12_health_profile
           SET profile_status = 'active', last_verified_date = ?,
               last_verified_by = ?, updated_at = ?
           WHERE id = ?""",
        (last_verified_date, last_verified_by, now, profile_id)
    )
    conn.commit()
    audit(conn, SKILL, "submit-health-profile-verification", "educlaw_k12_health_profile", profile_id)
    return ok({"id": profile_id, "profile_status": "active",
               "last_verified_date": last_verified_date,
               "message": "Health profile verified"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: get-emergency-health-info
# ─────────────────────────────────────────────────────────────────────────────

def get_emergency_health_info(conn, args):
    """Quick emergency access: student allergies, EpiPen, emergency contacts; FERPA log."""
    student_id = getattr(args, "student_id", None) or None
    user_id = getattr(args, "user_id", None) or ""

    if not student_id:
        return err("--student-id is required")

    student = conn.execute(
        "SELECT id, full_name, date_of_birth, emergency_contact, grade_level, company_id "
        "FROM educlaw_student WHERE id = ?",
        (student_id,)
    ).fetchone()
    if not student:
        return err(f"Student {student_id} not found")

    student_data = row_to_dict(student)
    company_id = student_data["company_id"]

    try:
        emergency_contact = json.loads(student_data.get("emergency_contact") or "{}")
    except Exception:
        emergency_contact = {}

    profile = conn.execute(
        """SELECT allergies, emergency_instructions, blood_type, activity_restriction,
                  activity_restriction_notes, physician_name, physician_phone
           FROM educlaw_k12_health_profile WHERE student_id = ?""",
        (student_id,)
    ).fetchone()

    allergies = []
    emergency_instructions = ""
    blood_type = "unknown"
    physician_name = ""
    physician_phone = ""

    if profile:
        allergies = _parse_json_field(profile["allergies"], "allergies")
        emergency_instructions = profile["emergency_instructions"] or ""
        blood_type = profile["blood_type"] or "unknown"
        physician_name = profile["physician_name"] or ""
        physician_phone = profile["physician_phone"] or ""

    # Get guardians
    guardians = conn.execute(
        """SELECT g.full_name, g.phone, g.alternate_phone, sg.relationship, sg.is_emergency_contact
           FROM educlaw_student_guardian sg
           JOIN educlaw_guardian g ON sg.guardian_id = g.id
           WHERE sg.student_id = ?
           ORDER BY sg.is_primary_contact DESC, sg.is_emergency_contact DESC""",
        (student_id,)
    ).fetchall()

    _log_ferpa(conn, user_id, student_id, "health", company_id,
               is_emergency=True, access_reason="emergency_health_access")
    conn.commit()

    return ok({
        "student_id": student_id,
        "full_name": student_data["full_name"],
        "grade_level": student_data["grade_level"],
        "blood_type": blood_type,
        "allergies": allergies,
        "emergency_instructions": emergency_instructions,
        "physician_name": physician_name,
        "physician_phone": physician_phone,
        "emergency_contact": emergency_contact,
        "guardians": rows_to_list(guardians),
    })



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-office-visit
# ─────────────────────────────────────────────────────────────────────────────

def add_office_visit(conn, args):
    """Record an immutable nurse office visit."""
    student_id = getattr(args, "student_id", None) or None
    visit_date = getattr(args, "visit_date", None) or None
    chief_complaint = getattr(args, "chief_complaint", None) or None
    disposition = getattr(args, "disposition", None) or None
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    created_by = getattr(args, "user_id", None) or ""

    if not student_id:
        return err("--student-id is required")
    if not visit_date:
        return err("--visit-date is required")
    if not chief_complaint:
        return err("--chief-complaint is required")
    if not disposition:
        return err("--disposition is required")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    academic_term_id = getattr(args, "academic_term_id", None) or None
    if academic_term_id:
        if not conn.execute(
            "SELECT id FROM educlaw_academic_term WHERE id = ?", (academic_term_id,)
        ).fetchone():
            return err(f"Academic term {academic_term_id} not found")

    visit_time = getattr(args, "visit_time", None) or ""
    complaint_detail = getattr(args, "complaint_detail", None) or ""
    temperature = getattr(args, "temperature", None) or ""
    pulse = getattr(args, "pulse", None) or ""
    assessment = getattr(args, "assessment", None) or ""
    treatment_provided = getattr(args, "treatment_provided", None) or ""
    parent_contacted = int(bool(getattr(args, "parent_contacted", None) or 0))
    parent_contact_time = getattr(args, "parent_contact_time", None) or ""
    parent_response = getattr(args, "parent_response", None) or ""
    is_emergency = int(bool(getattr(args, "is_emergency", None) or 0))

    now = _now_iso()
    visit_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_health_visit
           (id, student_id, visit_date, visit_time, chief_complaint, complaint_detail,
            temperature, pulse, assessment, treatment_provided, disposition,
            parent_contacted, parent_contact_time, parent_response, is_emergency,
            academic_term_id, company_id, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (visit_id, student_id, visit_date, visit_time, chief_complaint, complaint_detail,
         temperature, pulse, assessment, treatment_provided, disposition,
         parent_contacted, parent_contact_time, parent_response, is_emergency,
         academic_term_id, company_id, now, created_by)
    )
    _log_ferpa(conn, created_by, student_id, "health", company_id,
               access_reason="nurse_visit_recorded")
    conn.commit()
    audit(conn, SKILL, "add-office-visit", "educlaw_k12_health_visit", visit_id)
    return ok({"id": visit_id, "visit_date": visit_date, "disposition": disposition,
               "message": "Office visit recorded"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-office-visits
# ─────────────────────────────────────────────────────────────────────────────

def list_office_visits(conn, args):
    """List office visits for a student with date/disposition filters; FERPA log."""
    student_id = getattr(args, "student_id", None) or None
    user_id = getattr(args, "user_id", None) or ""
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    date_from = getattr(args, "date_from", None) or None
    date_to = getattr(args, "date_to", None) or None
    disposition = getattr(args, "disposition", None) or None
    limit = getattr(args, "limit", None) or 50
    offset = getattr(args, "offset", None) or 0

    if not student_id:
        return err("--student-id is required")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    query = "SELECT * FROM educlaw_k12_health_visit WHERE student_id = ? AND company_id = ?"
    params = [student_id, company_id]

    if date_from:
        query += " AND visit_date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND visit_date <= ?"
        params.append(date_to)
    if disposition:
        query += " AND disposition = ?"
        params.append(disposition)

    query += " ORDER BY visit_date DESC, visit_time DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()

    _log_ferpa(conn, user_id, student_id, "health", company_id)
    conn.commit()
    return ok({"student_id": student_id, "visits": rows_to_list(rows), "count": len(rows)})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: get-office-visit
# ─────────────────────────────────────────────────────────────────────────────

def get_office_visit(conn, args):
    """Get a single office visit record; FERPA log."""
    visit_id = getattr(args, "visit_id", None) or None
    user_id = getattr(args, "user_id", None) or ""

    if not visit_id:
        return err("--visit-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_k12_health_visit WHERE id = ?",
        (visit_id,)
    ).fetchone()
    if not row:
        return err(f"Office visit {visit_id} not found")

    data = row_to_dict(row)
    _log_ferpa(conn, user_id, data["student_id"], "health", data["company_id"])
    conn.commit()
    return ok(data)



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-student-medication
# ─────────────────────────────────────────────────────────────────────────────

def add_student_medication(conn, args):
    """Add an authorized medication to a student's school medication list."""
    student_id = getattr(args, "student_id", None) or None
    medication_name = getattr(args, "medication_name", None) or None
    dosage = getattr(args, "dosage", None) or ""
    route = getattr(args, "route", None) or None
    frequency = getattr(args, "frequency", None) or None
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    created_by = getattr(args, "user_id", None) or ""

    if not student_id:
        return err("--student-id is required")
    if not medication_name:
        return err("--medication-name is required")
    if not route:
        return err("--route is required")
    if not frequency:
        return err("--frequency is required")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    administration_times = getattr(args, "administration_times", None) or "[]"
    prescribing_physician = getattr(args, "prescribing_physician", None) or ""
    physician_authorization_date = getattr(args, "physician_authorization_date", None) or ""
    start_date = getattr(args, "start_date", None) or ""
    end_date = getattr(args, "end_date", None) or ""
    supply_count = int(getattr(args, "supply_count", None) or 0)
    supply_low_threshold = int(getattr(args, "supply_low_threshold", None) or 5)
    storage_instructions = getattr(args, "storage_instructions", None) or ""
    administration_instructions = getattr(args, "administration_instructions", None) or ""
    is_controlled_substance = int(bool(getattr(args, "is_controlled_substance", None) or 0))

    now = _now_iso()
    med_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_student_medication
           (id, student_id, medication_name, dosage, route, frequency,
            administration_times, prescribing_physician, physician_authorization_date,
            start_date, end_date, supply_count, supply_low_threshold,
            storage_instructions, administration_instructions, is_controlled_substance,
            medication_status, company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, ?)""",
        (med_id, student_id, medication_name, dosage, route, frequency,
         administration_times, prescribing_physician, physician_authorization_date,
         start_date, end_date, supply_count, supply_low_threshold,
         storage_instructions, administration_instructions, is_controlled_substance,
         company_id, now, now, created_by)
    )
    conn.commit()
    audit(conn, SKILL, "add-student-medication", "educlaw_k12_student_medication", med_id)
    return ok({"id": med_id, "medication_name": medication_name,
               "medication_status": "active", "message": "Student medication added"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: update-student-medication
# ─────────────────────────────────────────────────────────────────────────────

def update_student_medication(conn, args):
    """Update medication status, supply count, end date, or instructions."""
    medication_id = getattr(args, "medication_id", None) or None
    if not medication_id:
        return err("--medication-id is required")

    if not conn.execute(
        "SELECT id FROM educlaw_k12_student_medication WHERE id = ?",
        (medication_id,)
    ).fetchone():
        return err(f"Medication {medication_id} not found")

    updates = {}
    str_fields = ["medication_name", "dosage", "route", "frequency",
                  "administration_times", "prescribing_physician",
                  "physician_authorization_date", "start_date", "end_date",
                  "storage_instructions", "administration_instructions", "medication_status"]
    for field in str_fields:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    for int_field in ["supply_count", "supply_low_threshold", "is_controlled_substance"]:
        val = getattr(args, int_field, None)
        if val is not None:
            updates[int_field] = int(val)

    if not updates:
        return err("No fields provided to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE educlaw_k12_student_medication SET {set_clause} WHERE id = ?",
        list(updates.values()) + [medication_id]
    )
    conn.commit()
    audit(conn, SKILL, "update-student-medication", "educlaw_k12_student_medication", medication_id)
    return ok({"id": medication_id, "message": "Student medication updated"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-student-medications
# ─────────────────────────────────────────────────────────────────────────────

def list_student_medications(conn, args):
    """List active (or all) medications for a student."""
    student_id = getattr(args, "student_id", None) or None
    medication_status = getattr(args, "medication_status", None) or None
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)

    if not student_id:
        return err("--student-id is required")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    query = "SELECT * FROM educlaw_k12_student_medication WHERE student_id = ? AND company_id = ?"
    params = [student_id, company_id]

    if medication_status:
        query += " AND medication_status = ?"
        params.append(medication_status)
    else:
        # Default to active only
        query += " AND medication_status = 'active'"

    query += " ORDER BY medication_name"
    rows = conn.execute(query, params).fetchall()

    result = rows_to_list(rows)
    for r in result:
        r["administration_times"] = _parse_json_field(r.get("administration_times"), "administration_times")
    return ok({"student_id": student_id, "medications": result, "count": len(result)})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: record-medication-admin
# ─────────────────────────────────────────────────────────────────────────────

def log_medication_admin(conn, args):
    """Record an immutable medication administration event; decrement supply count."""
    student_medication_id = getattr(args, "student_medication_id", None) or None
    student_id = getattr(args, "student_id", None) or None
    log_date = getattr(args, "log_date", None) or None
    log_time = getattr(args, "log_time", None) or None
    administered_by = getattr(args, "administered_by", None) or ""
    created_by = getattr(args, "user_id", None) or ""

    if not student_medication_id:
        return err("--student-medication-id is required")
    if not student_id:
        return err("--student-id is required")
    if not log_date:
        return err("--log-date is required")
    if not log_time:
        return err("--log-time is required")

    med = conn.execute(
        "SELECT * FROM educlaw_k12_student_medication WHERE id = ?",
        (student_medication_id,)
    ).fetchone()
    if not med:
        return err(f"Student medication {student_medication_id} not found")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    dose_given = getattr(args, "dose_given", None) or med["dosage"] or ""
    student_response = getattr(args, "student_response", None) or ""
    is_refused = int(bool(getattr(args, "is_refused", None) or 0))
    refusal_reason = getattr(args, "refusal_reason", None) or ""
    notes = getattr(args, "notes", None) or ""

    now = _now_iso()
    log_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_medication_log
           (id, student_medication_id, student_id, log_date, log_time,
            dose_given, administered_by, student_response, is_refused,
            refusal_reason, notes, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (log_id, student_medication_id, student_id, log_date, log_time,
         dose_given, administered_by, student_response, is_refused,
         refusal_reason, notes, now, created_by)
    )

    # Decrement supply count only if medication was actually given (not refused)
    if not is_refused:
        conn.execute(
            """UPDATE educlaw_k12_student_medication
               SET supply_count = MAX(0, supply_count - 1), updated_at = ?
               WHERE id = ?""",
            (now, student_medication_id)
        )

    conn.commit()
    audit(conn, SKILL, "record-medication-admin", "educlaw_k12_medication_log", log_id)

    # Check supply threshold
    updated_med = conn.execute(
        "SELECT supply_count, supply_low_threshold FROM educlaw_k12_student_medication WHERE id = ?",
        (student_medication_id,)
    ).fetchone()
    response = {"id": log_id, "is_refused": bool(is_refused), "message": "Medication administration logged"}
    if updated_med and updated_med["supply_count"] <= updated_med["supply_low_threshold"]:
        response["supply_alert"] = (
            f"Low supply alert: {updated_med['supply_count']} units remaining "
            f"(threshold: {updated_med['supply_low_threshold']})"
        )
    return ok(response)



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-medication-logs
# ─────────────────────────────────────────────────────────────────────────────

def list_medication_logs(conn, args):
    """List administration log entries for a student or specific medication."""
    student_id = getattr(args, "student_id", None) or None
    student_medication_id = getattr(args, "student_medication_id", None) or None
    date_from = getattr(args, "date_from", None) or None
    date_to = getattr(args, "date_to", None) or None
    limit = getattr(args, "limit", None) or 50
    offset = getattr(args, "offset", None) or 0

    if not student_id and not student_medication_id:
        return err("--student-id or --student-medication-id is required")

    if student_medication_id:
        query = "SELECT * FROM educlaw_k12_medication_log WHERE student_medication_id = ?"
        params = [student_medication_id]
    else:
        query = "SELECT * FROM educlaw_k12_medication_log WHERE student_id = ?"
        params = [student_id]

    if date_from:
        query += " AND log_date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND log_date <= ?"
        params.append(date_to)

    query += " ORDER BY log_date DESC, log_time DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()
    return ok({"logs": rows_to_list(rows), "count": len(rows)})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-immunization
# ─────────────────────────────────────────────────────────────────────────────

def add_immunization(conn, args):
    """Add an immutable immunization dose record with CVX code."""
    student_id = getattr(args, "student_id", None) or None
    vaccine_name = getattr(args, "vaccine_name", None) or None
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    created_by = getattr(args, "user_id", None) or ""

    if not student_id:
        return err("--student-id is required")
    if not vaccine_name:
        return err("--vaccine-name is required")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    cvx_code = getattr(args, "cvx_code", None) or ""
    dose_number = int(getattr(args, "dose_number", None) or 1)
    administration_date = getattr(args, "administration_date", None) or ""
    lot_number = getattr(args, "lot_number", None) or ""
    manufacturer = getattr(args, "manufacturer", None) or ""
    provider_name = getattr(args, "provider_name", None) or ""
    provider_type = getattr(args, "provider_type", None) or ""
    source = getattr(args, "source", None) or "manual"
    iis_record_id = getattr(args, "iis_record_id", None) or ""
    corrects_record_id = getattr(args, "corrects_record_id", None) or ""

    now = _now_iso()
    imm_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_immunization
           (id, student_id, vaccine_name, cvx_code, dose_number, administration_date,
            lot_number, manufacturer, provider_name, provider_type, source,
            iis_record_id, corrects_record_id, company_id, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (imm_id, student_id, vaccine_name, cvx_code, dose_number, administration_date,
         lot_number, manufacturer, provider_name, provider_type, source,
         iis_record_id, corrects_record_id, company_id, now, created_by)
    )
    conn.commit()
    audit(conn, SKILL, "add-immunization", "educlaw_k12_immunization", imm_id)
    return ok({"id": imm_id, "vaccine_name": vaccine_name, "dose_number": dose_number,
               "message": "Immunization record added"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-immunization-waiver
# ─────────────────────────────────────────────────────────────────────────────

def add_immunization_waiver(conn, args):
    """Add a vaccine exemption waiver."""
    student_id = getattr(args, "student_id", None) or None
    vaccine_name = getattr(args, "vaccine_name", None) or None
    waiver_type = getattr(args, "waiver_type", None) or None
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    created_by = getattr(args, "user_id", None) or ""

    if not student_id:
        return err("--student-id is required")
    if not vaccine_name:
        return err("--vaccine-name is required")
    if not waiver_type:
        return err("--waiver-type is required (medical/religious/philosophical)")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    issuing_physician = getattr(args, "issuing_physician", None) or ""
    # Medical waivers require a physician name
    if waiver_type == "medical" and not issuing_physician:
        return err("Medical waivers require --issuing-physician")

    cvx_code = getattr(args, "cvx_code", None) or ""
    waiver_basis = getattr(args, "waiver_basis", None) or ""
    issue_date = getattr(args, "issue_date", None) or ""
    expiry_date = getattr(args, "expiry_date", None) or ""

    now = _now_iso()
    waiver_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_immunization_waiver
           (id, student_id, vaccine_name, cvx_code, waiver_type, waiver_basis,
            issuing_physician, issue_date, expiry_date, waiver_status,
            company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, ?)""",
        (waiver_id, student_id, vaccine_name, cvx_code, waiver_type, waiver_basis,
         issuing_physician, issue_date, expiry_date, company_id, now, now, created_by)
    )
    conn.commit()
    audit(conn, SKILL, "add-immunization-waiver", "educlaw_k12_immunization_waiver", waiver_id)
    return ok({"id": waiver_id, "vaccine_name": vaccine_name, "waiver_type": waiver_type,
               "waiver_status": "active", "message": "Immunization waiver added"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: update-immunization-waiver
# ─────────────────────────────────────────────────────────────────────────────

def update_immunization_waiver(conn, args):
    """Update waiver status (expire/revoke)."""
    waiver_id = getattr(args, "waiver_id", None) or None
    if not waiver_id:
        return err("--waiver-id is required")

    if not conn.execute(
        "SELECT id FROM educlaw_k12_immunization_waiver WHERE id = ?", (waiver_id,)
    ).fetchone():
        return err(f"Immunization waiver {waiver_id} not found")

    updates = {}
    for field in ["waiver_status", "expiry_date", "issue_date", "waiver_basis", "issuing_physician"]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    if not updates:
        return err("No fields provided to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE educlaw_k12_immunization_waiver SET {set_clause} WHERE id = ?",
        list(updates.values()) + [waiver_id]
    )
    conn.commit()
    audit(conn, SKILL, "update-immunization-waiver", "educlaw_k12_immunization_waiver", waiver_id)
    return ok({"id": waiver_id, "message": "Immunization waiver updated"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: get-immunization-record
# ─────────────────────────────────────────────────────────────────────────────

def get_immunization_record(conn, args):
    """Get complete immunization history for a student (doses + waivers); FERPA log."""
    student_id = getattr(args, "student_id", None) or None
    user_id = getattr(args, "user_id", None) or ""
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)

    if not student_id:
        return err("--student-id is required")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    immunizations = conn.execute(
        """SELECT * FROM educlaw_k12_immunization
           WHERE student_id = ? AND company_id = ?
           ORDER BY vaccine_name, dose_number, administration_date""",
        (student_id, company_id)
    ).fetchall()

    waivers = conn.execute(
        """SELECT * FROM educlaw_k12_immunization_waiver
           WHERE student_id = ? AND company_id = ?
           ORDER BY vaccine_name""",
        (student_id, company_id)
    ).fetchall()

    _log_ferpa(conn, user_id, student_id, "health", company_id)
    conn.commit()

    return ok({
        "student_id": student_id,
        "immunizations": rows_to_list(immunizations),
        "waivers": rows_to_list(waivers),
        "immunization_count": len(immunizations),
        "waiver_count": len(waivers),
    })



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: get-immunization-compliance
# ─────────────────────────────────────────────────────────────────────────────

# Grade-level required vaccines (simplified; real rules are state-specific)
# Format: {grade_group: {vaccine_name: required_doses}}
REQUIRED_VACCINES_BY_GRADE = {
    "K-5": {
        "DTaP": 5, "MMR": 2, "Varicella": 2, "Hepatitis B": 3,
        "Hepatitis A": 2, "Polio": 4,
    },
    "6-8": {
        "DTaP": 5, "MMR": 2, "Varicella": 2, "Hepatitis B": 3,
        "Polio": 4, "Tdap": 1, "MenACWY": 1,
    },
    "9-12": {
        "DTaP": 5, "MMR": 2, "Varicella": 2, "Hepatitis B": 3,
        "Polio": 4, "Tdap": 1, "MenACWY": 2,
    },
}


def _grade_to_group(grade_level):
    """Map student grade_level string to vaccine requirement group."""
    gl = (grade_level or "").upper().strip()
    k_5 = {"K", "KINDERGARTEN", "1", "2", "3", "4", "5"}
    g_6_8 = {"6", "7", "8"}
    g_9_12 = {"9", "10", "11", "12"}
    if gl in k_5:
        return "K-5"
    if gl in g_6_8:
        return "6-8"
    if gl in g_9_12:
        return "9-12"
    return "K-5"  # default


def check_immunization_compliance(conn, args):
    """Check a student's immunization records against grade-level requirements."""
    student_id = getattr(args, "student_id", None) or None
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)

    if not student_id:
        return err("--student-id is required")

    student = conn.execute(
        "SELECT id, grade_level, full_name FROM educlaw_student WHERE id = ?",
        (student_id,)
    ).fetchone()
    if not student:
        return err(f"Student {student_id} not found")

    grade_group = _grade_to_group(student["grade_level"])
    required = REQUIRED_VACCINES_BY_GRADE.get(grade_group, {})

    # Count doses received
    dose_rows = conn.execute(
        """SELECT vaccine_name, COUNT(*) as dose_count
           FROM educlaw_k12_immunization
           WHERE student_id = ? AND company_id = ?
           GROUP BY vaccine_name""",
        (student_id, company_id)
    ).fetchall()
    doses_by_vaccine = {row["vaccine_name"]: row["dose_count"] for row in dose_rows}

    # Get active waivers
    today = datetime.now().strftime("%Y-%m-%d")
    waiver_rows = conn.execute(
        """SELECT vaccine_name, waiver_type, expiry_date
           FROM educlaw_k12_immunization_waiver
           WHERE student_id = ? AND company_id = ?
             AND waiver_status = 'active'
             AND (expiry_date = '' OR expiry_date >= ?)""",
        (student_id, company_id, today)
    ).fetchall()
    waived_vaccines = {row["vaccine_name"]: row["waiver_type"] for row in waiver_rows}

    # Get health profile for provisional status
    profile = conn.execute(
        "SELECT is_provisional_immunization, is_mckinney_vento FROM educlaw_k12_health_profile "
        "WHERE student_id = ?",
        (student_id,)
    ).fetchone()

    is_provisional = profile["is_provisional_immunization"] if profile else 0
    is_mckinney_vento = profile["is_mckinney_vento"] if profile else 0

    missing_vaccines = []
    compliant_vaccines = []

    for vaccine, required_doses in required.items():
        received = doses_by_vaccine.get(vaccine, 0)
        has_waiver = vaccine in waived_vaccines

        if has_waiver:
            compliant_vaccines.append({
                "vaccine": vaccine,
                "required_doses": required_doses,
                "doses_received": received,
                "waiver_type": waived_vaccines[vaccine],
                "compliant_via": "waiver",
            })
        elif received >= required_doses:
            compliant_vaccines.append({
                "vaccine": vaccine,
                "required_doses": required_doses,
                "doses_received": received,
                "compliant_via": "immunized",
            })
        else:
            missing_vaccines.append({
                "vaccine": vaccine,
                "required_doses": required_doses,
                "doses_received": received,
                "doses_missing": required_doses - received,
            })

    is_compliant = (
        len(missing_vaccines) == 0 or
        is_provisional or
        is_mckinney_vento
    )

    return ok({
        "student_id": student_id,
        "grade_group": grade_group,
        "is_compliant": is_compliant,
        "is_provisional_enrollment": bool(is_provisional),
        "is_mckinney_vento": bool(is_mckinney_vento),
        "compliant_vaccines": compliant_vaccines,
        "missing_vaccines": missing_vaccines,
        "missing_count": len(missing_vaccines),
    })



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-health-alerts
# ─────────────────────────────────────────────────────────────────────────────

def list_health_alerts(conn, args):
    """List students with urgent health concerns."""
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    today = datetime.now().strftime("%Y-%m-%d")
    # Days ahead for expiry warnings
    days_ahead = int(getattr(args, "days_ahead", None) or 30)

    from datetime import timedelta
    warning_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    alerts = []

    # 1. Students with severe allergies (EpiPen required)
    severe_allergy_rows = conn.execute(
        """SELECT hp.student_id, s.full_name, s.grade_level, hp.allergies, hp.emergency_instructions
           FROM educlaw_k12_health_profile hp
           JOIN educlaw_student s ON hp.student_id = s.id
           WHERE hp.company_id = ? AND hp.allergies != '[]'""",
        (company_id,)
    ).fetchall()

    for row in severe_allergy_rows:
        allergies = _parse_json_field(row["allergies"], "allergies")
        severe = [a for a in allergies if isinstance(a, dict) and
                  a.get("severity", "").lower() in ("severe", "anaphylactic")]
        if severe:
            alerts.append({
                "alert_type": "severe_allergy",
                "student_id": row["student_id"],
                "student_name": row["full_name"],
                "grade_level": row["grade_level"],
                "details": f"{len(severe)} severe allergy/allergies",
            })

    # 2. Expiring immunization waivers (within days_ahead days)
    expiring_waivers = conn.execute(
        """SELECT iw.student_id, s.full_name, s.grade_level,
                  iw.vaccine_name, iw.waiver_type, iw.expiry_date
           FROM educlaw_k12_immunization_waiver iw
           JOIN educlaw_student s ON iw.student_id = s.id
           WHERE iw.company_id = ?
             AND iw.waiver_status = 'active'
             AND iw.expiry_date != ''
             AND iw.expiry_date <= ?
             AND iw.expiry_date >= ?""",
        (company_id, warning_date, today)
    ).fetchall()

    for row in expiring_waivers:
        alerts.append({
            "alert_type": "expiring_waiver",
            "student_id": row["student_id"],
            "student_name": row["full_name"],
            "grade_level": row["grade_level"],
            "details": f"{row['waiver_type']} waiver for {row['vaccine_name']} expires {row['expiry_date']}",
        })

    # 3. Expiring provisional enrollment
    expiring_provisional = conn.execute(
        """SELECT hp.student_id, s.full_name, s.grade_level,
                  hp.provisional_enrollment_end_date
           FROM educlaw_k12_health_profile hp
           JOIN educlaw_student s ON hp.student_id = s.id
           WHERE hp.company_id = ?
             AND hp.is_provisional_immunization = 1
             AND hp.provisional_enrollment_end_date != ''
             AND hp.provisional_enrollment_end_date <= ?
             AND hp.provisional_enrollment_end_date >= ?""",
        (company_id, warning_date, today)
    ).fetchall()

    for row in expiring_provisional:
        alerts.append({
            "alert_type": "provisional_enrollment_expiring",
            "student_id": row["student_id"],
            "student_name": row["full_name"],
            "grade_level": row["grade_level"],
            "details": f"Provisional enrollment expires {row['provisional_enrollment_end_date']}",
        })

    # 4. Low medication supply
    low_supply = conn.execute(
        """SELECT sm.student_id, s.full_name, s.grade_level,
                  sm.medication_name, sm.supply_count, sm.supply_low_threshold
           FROM educlaw_k12_student_medication sm
           JOIN educlaw_student s ON sm.student_id = s.id
           WHERE sm.company_id = ?
             AND sm.medication_status = 'active'
             AND sm.supply_count <= sm.supply_low_threshold""",
        (company_id,)
    ).fetchall()

    for row in low_supply:
        alerts.append({
            "alert_type": "low_medication_supply",
            "student_id": row["student_id"],
            "student_name": row["full_name"],
            "grade_level": row["grade_level"],
            "details": (f"{row['medication_name']}: {row['supply_count']} units "
                        f"(threshold: {row['supply_low_threshold']})"),
        })

    return ok({"alerts": alerts, "alert_count": len(alerts), "company_id": company_id})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: generate-immunization-report
# ─────────────────────────────────────────────────────────────────────────────

def generate_immunization_report(conn, args):
    """School-wide immunization compliance report by grade level and vaccine."""
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    today = datetime.now().strftime("%Y-%m-%d")

    # Get all active students
    students = conn.execute(
        """SELECT id, grade_level, full_name
           FROM educlaw_student
           WHERE company_id = ? AND status = 'active'
           ORDER BY grade_level, last_name""",
        (company_id,)
    ).fetchall()

    by_grade = {}
    overall_compliant = 0
    overall_non_compliant = 0
    overall_provisional = 0
    overall_waiver = 0

    for student in students:
        student_id = student["id"]
        grade_level = student["grade_level"] or "unknown"
        grade_group = _grade_to_group(grade_level)

        if grade_level not in by_grade:
            by_grade[grade_level] = {
                "grade_level": grade_level,
                "total_students": 0,
                "compliant": 0,
                "non_compliant": 0,
                "provisional": 0,
            }
        by_grade[grade_level]["total_students"] += 1

        profile = conn.execute(
            "SELECT is_provisional_immunization, is_mckinney_vento FROM educlaw_k12_health_profile "
            "WHERE student_id = ?",
            (student_id,)
        ).fetchone()
        is_provisional = profile["is_provisional_immunization"] if profile else 0
        is_mckinney = profile["is_mckinney_vento"] if profile else 0

        if is_provisional or is_mckinney:
            by_grade[grade_level]["provisional"] += 1
            overall_provisional += 1
            continue

        required = REQUIRED_VACCINES_BY_GRADE.get(grade_group, {})
        dose_rows = conn.execute(
            """SELECT vaccine_name, COUNT(*) as dose_count
               FROM educlaw_k12_immunization
               WHERE student_id = ? AND company_id = ?
               GROUP BY vaccine_name""",
            (student_id, company_id)
        ).fetchall()
        doses_by_vaccine = {r["vaccine_name"]: r["dose_count"] for r in dose_rows}

        waiver_rows = conn.execute(
            """SELECT vaccine_name FROM educlaw_k12_immunization_waiver
               WHERE student_id = ? AND company_id = ? AND waiver_status = 'active'
                 AND (expiry_date = '' OR expiry_date >= ?)""",
            (student_id, company_id, today)
        ).fetchall()
        waived = {r["vaccine_name"] for r in waiver_rows}

        is_compliant = True
        for vaccine, required_doses in required.items():
            if vaccine not in waived and doses_by_vaccine.get(vaccine, 0) < required_doses:
                is_compliant = False
                break

        if is_compliant:
            by_grade[grade_level]["compliant"] += 1
            overall_compliant += 1
        else:
            by_grade[grade_level]["non_compliant"] += 1
            overall_non_compliant += 1

    total_students = len(students)
    return ok({
        "company_id": company_id,
        "report_date": today,
        "total_active_students": total_students,
        "overall_compliant": overall_compliant,
        "overall_non_compliant": overall_non_compliant,
        "overall_provisional": overall_provisional,
        "compliance_rate": (
            f"{(overall_compliant / (total_students - overall_provisional) * 100):.1f}%"
            if (total_students - overall_provisional) > 0 else "N/A"
        ),
        "by_grade_level": list(by_grade.values()),
    })


# ─── ACTIONS registry ────────────────────────────────────────────────────────
ACTIONS = {
    "add-health-profile": add_health_profile,
    "update-health-profile": update_health_profile,
    "get-health-profile": get_health_profile,
    "submit-health-profile-verification": verify_health_profile,
    "get-emergency-health-info": get_emergency_health_info,
    "add-office-visit": add_office_visit,
    "list-office-visits": list_office_visits,
    "get-office-visit": get_office_visit,
    "add-student-medication": add_student_medication,
    "update-student-medication": update_student_medication,
    "list-student-medications": list_student_medications,
    "record-medication-admin": log_medication_admin,
    "list-medication-logs": list_medication_logs,
    "add-immunization": add_immunization,
    "add-immunization-waiver": add_immunization_waiver,
    "update-immunization-waiver": update_immunization_waiver,
    "get-immunization-record": get_immunization_record,
    "get-immunization-compliance": check_immunization_compliance,
    "list-health-alerts": list_health_alerts,
    "generate-immunization-report": generate_immunization_report,
}
