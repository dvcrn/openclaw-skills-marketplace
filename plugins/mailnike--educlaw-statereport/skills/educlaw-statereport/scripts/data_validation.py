"""EduClaw State Reporting — data_validation domain module

Validation rule library, pre-submission validation runs, error dashboard,
error assignment, resolution tracking, bulk assignment, and escalation.

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
except ImportError:
    pass

SKILL = "educlaw-statereport"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

VALID_CATEGORIES = (
    "enrollment", "demographics", "sped", "el",
    "attendance", "discipline", "staff", "calendar"
)
VALID_SEVERITIES = ("critical", "major", "minor", "warning")
VALID_RESOLUTION_STATUSES = ("open", "in_progress", "resolved", "deferred", "state_waived")
VALID_RESOLUTION_METHODS = ("data_corrected", "descriptor_mapped", "state_exception", "data_not_available", "")
VALID_ERROR_SOURCES = ("edfi_api", "state_portal", "internal_validation")
VALID_ERROR_LEVELS = ("1", "2", "3")
VALID_ERROR_CATEGORIES = (
    "enrollment", "demographics", "sped", "el",
    "attendance", "discipline", "staff", "calendar", "other"
)


# ─────────────────────────────────────────────────────────────────────────────
# VALIDATION RULE LIBRARY
# ─────────────────────────────────────────────────────────────────────────────

def add_validation_rule(conn, args):
    rule_code = getattr(args, "rule_code", None)
    category = getattr(args, "category", None)
    severity = getattr(args, "severity", None)
    name = getattr(args, "name", None)

    if not rule_code:
        err("--rule-code is required")
    if not category:
        err("--category is required")
    if category not in VALID_CATEGORIES:
        err(f"--category must be one of: {', '.join(VALID_CATEGORIES)}")
    if not severity:
        err("--severity is required")
    if severity not in VALID_SEVERITIES:
        err(f"--severity must be one of: {', '.join(VALID_SEVERITIES)}")
    if not name:
        err("--name is required")

    # Check unique rule_code
    if conn.execute("SELECT id FROM sr_validation_rule WHERE rule_code = ?", (rule_code,)).fetchone():
        err(f"Rule code '{rule_code}' already exists")

    rule_id = str(uuid.uuid4())
    now = _now_iso()

    applicable_windows = getattr(args, "applicable_windows", None) or "[]"
    applicable_states = getattr(args, "applicable_states", None) or "[]"

    try:
        conn.execute(
            """INSERT INTO sr_validation_rule
               (id, rule_code, category, severity, name, description,
                applicable_windows, applicable_states, is_federal_rule,
                sql_query, error_message_template, is_active,
                created_at, updated_at, created_by)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (rule_id, rule_code, category, severity, name,
             getattr(args, "description", None) or "",
             applicable_windows, applicable_states,
             int(getattr(args, "is_federal_rule", None) or 0),
             getattr(args, "sql_query", None) or "",
             getattr(args, "error_message_template", None) or "",
             1, now, now, getattr(args, "user_id", None) or "")
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        err(f"Cannot create validation rule: {e}")

    audit(conn, "sr_validation_rule", rule_id, "INSERT", getattr(args, "user_id", None) or "")
    ok({"id": rule_id, "rule_code": rule_code, "message": "Validation rule created"})


def update_validation_rule(conn, args):
    rule_id = getattr(args, "rule_id", None)
    rule_code = getattr(args, "rule_code", None)

    if rule_id:
        row = conn.execute("SELECT id FROM sr_validation_rule WHERE id = ?", (rule_id,)).fetchone()
    elif rule_code:
        row = conn.execute("SELECT id FROM sr_validation_rule WHERE rule_code = ?", (rule_code,)).fetchone()
    else:
        err("--rule-id or --rule-code is required")

    if not row:
        err("Validation rule not found")

    updates = {}
    for field in [
        "category", "severity", "name", "description",
        "applicable_windows", "applicable_states", "is_federal_rule",
        "sql_query", "error_message_template"
    ]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    if not updates:
        err("No fields to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE sr_validation_rule SET {set_clause} WHERE id = ?",
        list(updates.values()) + [row["id"]]
    )
    conn.commit()
    audit(conn, "sr_validation_rule", row["id"], "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": row["id"], "message": "Validation rule updated"})


def get_validation_rule(conn, args):
    rule_id = getattr(args, "rule_id", None)
    rule_code = getattr(args, "rule_code", None)

    if rule_id:
        row = conn.execute("SELECT * FROM sr_validation_rule WHERE id = ?", (rule_id,)).fetchone()
    elif rule_code:
        row = conn.execute("SELECT * FROM sr_validation_rule WHERE rule_code = ?", (rule_code,)).fetchone()
    else:
        err("--rule-id or --rule-code is required")

    if not row:
        err("Validation rule not found")

    rec = dict(row)
    for field in ["applicable_windows", "applicable_states"]:
        try:
            rec[field] = json.loads(rec[field])
        except (json.JSONDecodeError, TypeError):
            rec[field] = []
    ok(rec)


def list_validation_rules(conn, args):
    conditions = []
    params = []

    category = getattr(args, "category", None)
    if category:
        conditions.append("category = ?")
        params.append(category)

    severity = getattr(args, "severity", None)
    if severity:
        conditions.append("severity = ?")
        params.append(severity)

    is_active = getattr(args, "is_active", None)
    if is_active is not None:
        conditions.append("is_active = ?")
        params.append(int(is_active))

    is_federal_rule = getattr(args, "is_federal_rule", None)
    if is_federal_rule is not None:
        conditions.append("is_federal_rule = ?")
        params.append(int(is_federal_rule))

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    limit = int(getattr(args, "limit", None) or 100)
    offset = int(getattr(args, "offset", None) or 0)

    rows = conn.execute(
        f"SELECT * FROM sr_validation_rule {where} ORDER BY category, severity, rule_code LIMIT ? OFFSET ?",
        params + [limit, offset]
    ).fetchall()

    result = []
    for r in rows:
        rec = dict(r)
        for field in ["applicable_windows", "applicable_states"]:
            try:
                rec[field] = json.loads(rec[field])
            except (json.JSONDecodeError, TypeError):
                rec[field] = []
        result.append(rec)

    ok({"rules": result, "count": len(result)})


def toggle_validation_rule(conn, args):
    rule_id = getattr(args, "rule_id", None)
    rule_code = getattr(args, "rule_code", None)

    if rule_id:
        row = conn.execute("SELECT id, is_active FROM sr_validation_rule WHERE id = ?", (rule_id,)).fetchone()
    elif rule_code:
        row = conn.execute("SELECT id, is_active FROM sr_validation_rule WHERE rule_code = ?", (rule_code,)).fetchone()
    else:
        err("--rule-id or --rule-code is required")

    if not row:
        err("Validation rule not found")

    # Check if explicit is_active provided, otherwise toggle
    new_active = getattr(args, "is_active", None)
    if new_active is not None:
        new_active = int(new_active)
    else:
        new_active = 1 - int(row["is_active"])

    now = _now_iso()
    conn.execute(
        "UPDATE sr_validation_rule SET is_active = ?, updated_at = ? WHERE id = ?",
        (new_active, now, row["id"])
    )
    conn.commit()
    state = "activated" if new_active else "deactivated"
    ok({"id": row["id"], "is_active": new_active, "message": f"Validation rule {state}"})


def seed_validation_rules(conn, args):
    """Load built-in federal/common rule library. Skips existing rule_codes."""
    company_id = getattr(args, "company_id", None)
    user_id = getattr(args, "user_id", None) or ""

    SEED_RULES = [
        # DEMO rules
        ("DEMO-001", "demographics", "critical", "SSID Required",
         "All active students must have an assigned SSID",
         "[]", "[]", 1,
         "SELECT s.id as student_id FROM educlaw_student s LEFT JOIN sr_student_supplement ss ON ss.student_id = s.id WHERE (ss.id IS NULL OR ss.ssid_status != 'assigned') AND s.status='active'",
         "Student {student_id} missing assigned SSID"),
        ("DEMO-002", "demographics", "critical", "Race/Ethnicity Required",
         "All students must have race/ethnicity codes set",
         "[]", "[]", 1,
         "SELECT s.id as student_id FROM educlaw_student s JOIN sr_student_supplement ss ON ss.student_id=s.id WHERE (ss.race_codes='[]' OR ss.race_codes='') AND s.status='active'",
         "Student {student_id} missing race/ethnicity"),
        ("DEMO-003", "demographics", "major", "Date of Birth Reasonable",
         "Student age must be between 3 and 21 years",
         "[]", "[]", 1,
         "SELECT id as student_id FROM educlaw_student WHERE (CAST(strftime('%Y',date('now')) AS INT) - CAST(substr(date_of_birth,1,4) AS INT)) NOT BETWEEN 3 AND 21 AND status='active'",
         "Student {student_id} has unreasonable age (DOB: {date_of_birth})"),
        ("DEMO-004", "demographics", "major", "Home Language Required for EL",
         "EL students must have home language code",
         "[]", "[]", 1,
         "SELECT student_id FROM sr_student_supplement WHERE is_el=1 AND home_language_code=''",
         "EL student {student_id} missing home language code"),
        ("DEMO-005", "demographics", "major", "EL Entry Date Required",
         "EL students must have EL entry date",
         "[]", "[]", 1,
         "SELECT student_id FROM sr_student_supplement WHERE is_el=1 AND el_entry_date=''",
         "EL student {student_id} missing EL entry date"),
        ("DEMO-006", "demographics", "minor", "Proficiency Instrument for EL",
         "EL students should have proficiency instrument on record",
         "[]", "[]", 1,
         "SELECT student_id FROM sr_student_supplement WHERE is_el=1 AND english_proficiency_instrument=''",
         "EL student {student_id} missing proficiency instrument"),
        ("DEMO-007", "demographics", "major", "SPED Entry Date Required",
         "SPED students must have SPED entry date",
         "[]", "[]", 1,
         "SELECT student_id FROM sr_student_supplement WHERE is_sped=1 AND sped_entry_date=''",
         "SPED student {student_id} missing SPED entry date"),
        ("DEMO-008", "demographics", "minor", "Race Rollup Consistency",
         "Race federal rollup must match is_hispanic_latino and race_codes",
         "[]", "[]", 1,
         "SELECT student_id FROM sr_student_supplement WHERE race_federal_rollup='' AND (is_hispanic_latino=1 OR race_codes != '[]')",
         "Student {student_id} has race data but empty federal rollup"),
        ("DEMO-009", "demographics", "warning", "Military Connection Type",
         "Military connected students should have connection type specified",
         "[]", "[]", 1,
         "SELECT student_id FROM sr_student_supplement WHERE is_military_connected=1 AND military_connection_type=''",
         "Military connected student {student_id} missing connection type"),
        ("DEMO-010", "demographics", "warning", "Homeless Residence Type",
         "Homeless students should have nighttime residence type",
         "[]", "[]", 1,
         "SELECT student_id FROM sr_student_supplement WHERE is_homeless=1 AND homeless_primary_nighttime_residence=''",
         "Homeless student {student_id} missing residence type"),
        # ENROLL rules
        ("ENROLL-001", "enrollment", "critical", "Active Enrollment Required",
         "Every active student must have an active program enrollment",
         "[]", "[]", 1,
         "SELECT s.id as student_id FROM educlaw_student s LEFT JOIN educlaw_program_enrollment pe ON pe.student_id=s.id AND pe.enrollment_status='active' WHERE s.status='active' AND pe.id IS NULL",
         "Student {student_id} has no active enrollment"),
        ("ENROLL-002", "enrollment", "critical", "Enrollment Date Required",
         "All enrollments must have an enrollment date",
         "[]", "[]", 1,
         "SELECT student_id FROM educlaw_program_enrollment WHERE enrollment_date='' AND enrollment_status='active'",
         "Enrollment for student {student_id} missing enrollment date"),
        ("ENROLL-003", "enrollment", "major", "No Duplicate Active Enrollments",
         "Student cannot have more than one active enrollment in same program",
         "[]", "[]", 1,
         "SELECT student_id FROM educlaw_program_enrollment WHERE enrollment_status='active' GROUP BY student_id, program_id HAVING COUNT(*)>1",
         "Student {student_id} has duplicate active enrollments"),
        ("ENROLL-004", "enrollment", "major", "Enrollment Status Valid",
         "All enrollment records must have valid status",
         "[]", "[]", 1,
         "SELECT student_id FROM educlaw_program_enrollment WHERE enrollment_status NOT IN ('active','completed','withdrawn','suspended')",
         "Enrollment for student {student_id} has invalid status"),
        ("ENROLL-005", "enrollment", "minor", "Grade Level Present",
         "All active students should have grade level set",
         "[]", "[]", 1,
         "SELECT id as student_id FROM educlaw_student WHERE grade_level='' AND status='active'",
         "Student {student_id} missing grade level"),
        ("ENROLL-006", "enrollment", "warning", "Cohort Year Present",
         "Active students should have cohort year",
         "[]", "[]", 0,
         "SELECT id as student_id FROM educlaw_student WHERE cohort_year=0 AND status='active'",
         "Student {student_id} missing cohort year"),
        # SPED rules
        ("SPED-001", "sped", "critical", "Disability Category Required",
         "SPED students must have disability category in placement record",
         "[]", "[]", 1,
         "SELECT ss.student_id FROM sr_student_supplement ss JOIN sr_sped_placement sp ON sp.student_id=ss.student_id WHERE ss.is_sped=1 AND sp.disability_category=''",
         "SPED student {student_id} missing disability category"),
        ("SPED-002", "sped", "critical", "Educational Environment Required",
         "SPED placement must have educational environment code",
         "[]", "[]", 1,
         "SELECT ss.student_id FROM sr_student_supplement ss JOIN sr_sped_placement sp ON sp.student_id=ss.student_id WHERE ss.is_sped=1 AND sp.educational_environment=''",
         "SPED student {student_id} missing educational environment"),
        ("SPED-003", "sped", "major", "SPED Placement Required",
         "All is_sped=1 students must have a sped_placement record",
         "[]", "[]", 1,
         "SELECT ss.student_id FROM sr_student_supplement ss LEFT JOIN sr_sped_placement sp ON sp.student_id=ss.student_id WHERE ss.is_sped=1 AND sp.id IS NULL",
         "SPED student {student_id} missing SPED placement record"),
        ("SPED-004", "sped", "major", "IEP Start Date Required",
         "Active SPED placements must have IEP start date",
         "[]", "[]", 1,
         "SELECT student_id FROM sr_sped_placement WHERE iep_start_date='' AND sped_program_exit_date=''",
         "SPED placement for student {student_id} missing IEP start date"),
        ("SPED-005", "sped", "minor", "IEP Review Date Required",
         "Active SPED placements should have IEP annual review date",
         "[]", "[]", 1,
         "SELECT student_id FROM sr_sped_placement WHERE iep_review_date='' AND sped_program_exit_date=''",
         "SPED placement for student {student_id} missing IEP review date"),
        ("SPED-006", "sped", "major", "SPED Entry Date in Placement",
         "SPED placement entry date must be present",
         "[]", "[]", 1,
         "SELECT student_id FROM sr_sped_placement WHERE sped_program_entry_date=''",
         "SPED placement for student {student_id} missing entry date"),
        ("SPED-007", "sped", "critical", "MDR Required for IDEA Suspension",
         "IDEA students with >10 day suspension must have MDR completed",
         "[]", "[]", 1,
         "SELECT student_id FROM sr_discipline_action WHERE mdr_required=1 AND (mdr_outcome='' OR mdr_outcome='pending')",
         "Student {student_id} has pending MDR for >10 day suspension"),
        ("SPED-008", "sped", "minor", "Transition Plan for Older Students",
         "SPED students 14+ should have transition plan flag set",
         "[]", "[]", 0,
         "SELECT sp.student_id FROM sr_sped_placement sp JOIN educlaw_student s ON s.id=sp.student_id WHERE CAST(strftime('%Y',date('now')) AS INT)-CAST(substr(s.date_of_birth,1,4) AS INT)>=14 AND sp.is_transition_plan_required=0 AND sp.sped_program_exit_date=''",
         "Student {student_id} is 14+ and may need transition plan flag"),
        # EL rules
        ("EL-001", "el", "critical", "EL Program Record Required",
         "EL students must have an EL program enrollment record",
         "[]", "[]", 1,
         "SELECT ss.student_id FROM sr_student_supplement ss LEFT JOIN sr_el_program ep ON ep.student_id=ss.student_id WHERE ss.is_el=1 AND ep.id IS NULL",
         "EL student {student_id} missing EL program record"),
        ("EL-002", "el", "major", "EL Program Type Required",
         "EL program record must have program type",
         "[]", "[]", 1,
         "SELECT student_id FROM sr_el_program WHERE program_type='' AND exit_date=''",
         "Active EL program for student {student_id} missing program type"),
        ("EL-003", "el", "major", "EL Program Entry Date Required",
         "EL program must have entry date",
         "[]", "[]", 1,
         "SELECT student_id FROM sr_el_program WHERE entry_date=''",
         "EL program for student {student_id} missing entry date"),
        ("EL-004", "el", "minor", "Proficiency Level for EL Program",
         "Active EL programs should have current proficiency level",
         "[]", "[]", 1,
         "SELECT student_id FROM sr_el_program WHERE proficiency_level='' AND exit_date=''",
         "Active EL program for student {student_id} missing proficiency level"),
        ("EL-005", "el", "minor", "RFEP Date Required When Exited",
         "RFEP students must have RFEP date in supplement",
         "[]", "[]", 1,
         "SELECT student_id FROM sr_student_supplement WHERE is_rfep=1 AND rfep_date=''",
         "RFEP student {student_id} missing RFEP date"),
        ("EL-006", "el", "warning", "EL Exit Reason Required",
         "EL program records with exit date should have exit reason",
         "[]", "[]", 0,
         "SELECT student_id FROM sr_el_program WHERE exit_date!='' AND exit_reason=''",
         "EL program for student {student_id} has exit date but no exit reason"),
        ("EL-007", "el", "major", "EL Flag Consistency",
         "Students with active EL program should have is_el=1 in supplement",
         "[]", "[]", 1,
         "SELECT ep.student_id FROM sr_el_program ep LEFT JOIN sr_student_supplement ss ON ss.student_id=ep.student_id WHERE ep.exit_date='' AND ss.is_el=0",
         "Student {student_id} has active EL program but is_el=0 in supplement"),
        ("EL-008", "el", "major", "Home Language for Non-English Students",
         "Students with non-English home language should have EL flag evaluated",
         "[]", "[]", 0,
         "SELECT student_id FROM sr_student_supplement WHERE home_language_code NOT IN ('','eng','en') AND is_el=0 AND is_rfep=0",
         "Student {student_id} has non-English home language but no EL flag"),
        # ATTEND rules
        ("ATTEND-001", "attendance", "critical", "Attendance Records Required",
         "All active students must have at least one attendance record",
         "[]", "[]", 1,
         "SELECT s.id as student_id FROM educlaw_student s LEFT JOIN educlaw_student_attendance sa ON sa.student_id=s.id WHERE s.status='active' AND sa.id IS NULL",
         "Student {student_id} has no attendance records"),
        ("ATTEND-002", "attendance", "major", "Attendance Date Valid",
         "Attendance dates must be valid ISO format",
         "[]", "[]", 1,
         "SELECT DISTINCT student_id FROM educlaw_student_attendance WHERE attendance_date='' OR length(attendance_date)<10",
         "Student {student_id} has attendance record with invalid date"),
        ("ATTEND-003", "attendance", "critical", "Attendance Status Required",
         "All attendance records must have a status",
         "[]", "[]", 1,
         "SELECT DISTINCT student_id FROM educlaw_student_attendance WHERE attendance_status=''",
         "Student {student_id} has attendance record missing status"),
        ("ATTEND-004", "attendance", "major", "No Attendance Outside Enrollment",
         "Attendance date should fall within student enrollment period",
         "[]", "[]", 1,
         "SELECT sa.student_id FROM educlaw_student_attendance sa LEFT JOIN educlaw_program_enrollment pe ON pe.student_id=sa.student_id AND sa.attendance_date>=pe.enrollment_date WHERE pe.id IS NULL AND sa.id IS NOT NULL",
         "Student {student_id} has attendance outside enrollment period"),
        ("ATTEND-005", "attendance", "minor", "Section Present for Section Attendance",
         "Section-level attendance records should reference a valid section",
         "[]", "[]", 0,
         "SELECT DISTINCT student_id FROM educlaw_student_attendance WHERE section_id IS NOT NULL AND section_id NOT IN (SELECT id FROM educlaw_section)",
         "Student {student_id} attendance references invalid section"),
        ("ATTEND-006", "attendance", "warning", "Half Day Attendance",
         "Half-day attendance records should be reviewed",
         "[]", "[]", 0,
         "SELECT student_id, COUNT(*) as cnt FROM educlaw_student_attendance WHERE attendance_status='half_day' GROUP BY student_id HAVING cnt > 20",
         "Student {student_id} has excessive half-day absences"),
        ("ATTEND-007", "attendance", "major", "Marked By Required",
         "Attendance records should show who marked them",
         "[]", "[]", 0,
         "SELECT DISTINCT student_id FROM educlaw_student_attendance WHERE marked_by=''",
         "Student {student_id} has attendance marked by unknown user"),
        ("ATTEND-008", "attendance", "critical", "Attendance Status Valid",
         "Attendance status must be a valid value",
         "[]", "[]", 1,
         "SELECT DISTINCT student_id FROM educlaw_student_attendance WHERE attendance_status NOT IN ('present','absent','tardy','excused','half_day')",
         "Student {student_id} has invalid attendance status"),
        # DISC rules
        ("DISC-001", "discipline", "major", "Incident Has Students",
         "Every discipline incident must have at least one student attached",
         "[]", "[]", 1,
         "SELECT id as incident_id FROM sr_discipline_incident WHERE student_count_involved=0",
         "Discipline incident {incident_id} has no students attached"),
        ("DISC-002", "discipline", "critical", "MDR for IDEA Student 10+ Days",
         "IDEA students suspended >10 days must have MDR completed",
         "[]", "[]", 1,
         "SELECT student_id FROM sr_discipline_action WHERE mdr_required=1 AND mdr_outcome NOT IN ('manifestation','not_manifestation')",
         "Student {student_id} IDEA suspension >10 days requires completed MDR"),
        ("DISC-003", "discipline", "major", "Incident Date Required",
         "All discipline incidents must have an incident date",
         "[]", "[]", 1,
         "SELECT id as incident_id FROM sr_discipline_incident WHERE incident_date=''",
         "Discipline incident {incident_id} missing incident date"),
        ("DISC-004", "discipline", "major", "Incident Type Required",
         "All discipline incidents must have an incident type",
         "[]", "[]", 1,
         "SELECT id as incident_id FROM sr_discipline_incident WHERE incident_type=''",
         "Discipline incident {incident_id} missing incident type"),
        ("DISC-005", "discipline", "minor", "Action Dates Required",
         "Discipline actions should have start and end dates",
         "[]", "[]", 0,
         "SELECT id as action_id FROM sr_discipline_action WHERE start_date='' AND action_type!='no_action'",
         "Discipline action {action_id} missing start date"),
        ("DISC-006", "discipline", "major", "Days Removed Non-Negative",
         "Days removed from school cannot be negative",
         "[]", "[]", 1,
         "SELECT id as action_id FROM sr_discipline_action WHERE days_removed < 0",
         "Discipline action {action_id} has negative days_removed"),
        # STAFF rules
        ("STAFF-001", "staff", "major", "Section Must Have Instructor",
         "All active sections must have an assigned instructor",
         "[]", "[]", 1,
         "SELECT id as section_id FROM educlaw_section WHERE instructor_id IS NULL AND status='open'",
         "Section {section_id} has no assigned instructor"),
        ("STAFF-002", "staff", "major", "Instructor Must Be Employee",
         "All instructors must reference a valid employee record",
         "[]", "[]", 1,
         "SELECT i.id as instructor_id FROM educlaw_instructor i LEFT JOIN employee e ON e.id=i.employee_id WHERE e.id IS NULL",
         "Instructor {instructor_id} references invalid employee"),
        ("STAFF-003", "staff", "minor", "Instructor Bio Optional",
         "Active instructors should have bio or credentials",
         "[]", "[]", 0,
         "SELECT id as instructor_id FROM educlaw_instructor WHERE bio='' AND credentials='[]' AND is_active=1",
         "Instructor {instructor_id} missing bio and credentials"),
        ("STAFF-004", "staff", "warning", "Max Teaching Load",
         "Instructors should not exceed max teaching load",
         "[]", "[]", 0,
         "SELECT instructor_id, COUNT(*) as sections FROM educlaw_section WHERE status='open' GROUP BY instructor_id HAVING sections > 8",
         "Instructor {instructor_id} may exceed teaching load"),
        ("STAFF-005", "staff", "major", "Open Sections Have Valid Status",
         "Sections in active use must have valid status",
         "[]", "[]", 1,
         "SELECT id as section_id FROM educlaw_section WHERE status NOT IN ('draft','scheduled','open','closed','cancelled')",
         "Section {section_id} has invalid status"),
    ]

    now = _now_iso()
    inserted = 0
    skipped = 0

    for (rule_code, category, severity, name, description,
         applicable_windows, applicable_states, is_federal,
         sql_query, error_msg_template) in SEED_RULES:

        existing = conn.execute(
            "SELECT id FROM sr_validation_rule WHERE rule_code = ?", (rule_code,)
        ).fetchone()
        if existing:
            skipped += 1
            continue

        rule_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO sr_validation_rule
               (id, rule_code, category, severity, name, description,
                applicable_windows, applicable_states, is_federal_rule,
                sql_query, error_message_template, is_active,
                created_at, updated_at, created_by)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (rule_id, rule_code, category, severity, name, description,
             applicable_windows, applicable_states, is_federal,
             sql_query, error_msg_template, 1, now, now,
             getattr(args, "user_id", None) or "system")
        )
        inserted += 1

    conn.commit()
    ok({"inserted": inserted, "skipped": skipped,
        "total_seed_rules": len(SEED_RULES),
        "message": f"Validation rule seed complete: {inserted} inserted, {skipped} skipped"})


# ─────────────────────────────────────────────────────────────────────────────
# VALIDATION RUN ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def run_validation(conn, args):
    """Execute all active applicable rules for a collection window."""
    window_id = getattr(args, "window_id", None)
    company_id = getattr(args, "company_id", None)
    user_id = getattr(args, "user_id", None) or "system"

    if not window_id:
        err("--window-id is required")
    if not company_id:
        err("--company-id is required")

    window = conn.execute("SELECT * FROM sr_collection_window WHERE id = ?", (window_id,)).fetchone()
    if not window:
        err(f"Collection window {window_id} not found")

    window_type = window["window_type"]
    now = _now_iso()

    # Clear prior unresolved results for this window
    conn.execute(
        "DELETE FROM sr_validation_result WHERE collection_window_id = ? AND is_resolved = 0",
        (window_id,)
    )

    # Get active rules applicable to this window
    rules = conn.execute(
        "SELECT * FROM sr_validation_rule WHERE is_active = 1",
        ()
    ).fetchall()

    total_violations = 0
    rules_run = 0

    for rule in rules:
        # Check if rule applies to this window type
        try:
            applicable_windows = json.loads(rule["applicable_windows"])
        except Exception:
            applicable_windows = []

        if applicable_windows and window_type not in applicable_windows:
            continue

        sql_query = rule["sql_query"]
        if not sql_query:
            continue

        rules_run += 1

        try:
            violations = conn.execute(sql_query).fetchall()
        except Exception as e:
            # Log rule execution error but continue
            violations = []

        for viol in violations:
            viol_dict = dict(viol)
            student_id = viol_dict.get("student_id")
            staff_id = viol_dict.get("staff_id")

            # Create validation result
            result_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO sr_validation_result
                   (id, collection_window_id, run_at, run_by, rule_id,
                    student_id, staff_id, error_detail, is_resolved, resolved_at,
                    company_id, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (result_id, window_id, now, user_id, rule["id"],
                 student_id, staff_id,
                 json.dumps(viol_dict),
                 0, "", company_id, now)
            )

            # Create corresponding submission error
            error_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO sr_submission_error
                   (id, collection_window_id, submission_id, error_source,
                    error_level, severity, error_code, error_category,
                    error_message, student_id, staff_id, record_type,
                    field_name, field_value, resolution_status, resolution_method,
                    resolved_by, resolved_at, resolution_notes, assigned_to,
                    assigned_at, state_ticket_id, company_id, created_at, updated_at, created_by)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (error_id, window_id, None, "internal_validation",
                 "2", rule["severity"], rule["rule_code"], rule["category"],
                 rule["error_message_template"].replace("{student_id}", student_id or ""),
                 student_id, staff_id, rule["category"],
                 "", json.dumps(viol_dict),
                 "open", "",
                 "", "", "", "", "", "",
                 company_id, now, now, user_id)
            )
            total_violations += 1

    conn.commit()

    ok({
        "window_id": window_id,
        "rules_run": rules_run,
        "total_violations": total_violations,
        "run_at": now,
        "message": f"Validation complete: {rules_run} rules run, {total_violations} violations found"
    })


def run_validation_for_student(conn, args):
    """Run all applicable rules for a single student."""
    window_id = getattr(args, "window_id", None)
    student_id = getattr(args, "student_id", None)
    company_id = getattr(args, "company_id", None)
    user_id = getattr(args, "user_id", None) or "system"

    if not window_id:
        err("--window-id is required")
    if not student_id:
        err("--student-id is required")
    if not company_id:
        err("--company-id is required")

    if not conn.execute("SELECT id FROM sr_collection_window WHERE id = ?", (window_id,)).fetchone():
        err(f"Collection window {window_id} not found")
    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        err(f"Student {student_id} not found")

    # Clear prior results for this student/window
    conn.execute(
        "DELETE FROM sr_validation_result WHERE collection_window_id = ? AND student_id = ? AND is_resolved = 0",
        (window_id, student_id)
    )

    now = _now_iso()
    rules = conn.execute("SELECT * FROM sr_validation_rule WHERE is_active = 1").fetchall()
    violations_found = 0

    for rule in rules:
        sql_query = rule["sql_query"]
        if not sql_query:
            continue

        # Run only student-scoped rules
        if "student_id" not in sql_query:
            continue

        try:
            violations = conn.execute(sql_query).fetchall()
            student_violations = [dict(v) for v in violations if v.get("student_id") == student_id]
        except Exception:
            student_violations = []

        for viol_dict in student_violations:
            result_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO sr_validation_result
                   (id, collection_window_id, run_at, run_by, rule_id,
                    student_id, staff_id, error_detail, is_resolved, resolved_at,
                    company_id, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (result_id, window_id, now, user_id, rule["id"],
                 student_id, None, json.dumps(viol_dict),
                 0, "", company_id, now)
            )

            error_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO sr_submission_error
                   (id, collection_window_id, submission_id, error_source,
                    error_level, severity, error_code, error_category,
                    error_message, student_id, staff_id, record_type,
                    field_name, field_value, resolution_status, resolution_method,
                    resolved_by, resolved_at, resolution_notes, assigned_to,
                    assigned_at, state_ticket_id, company_id, created_at, updated_at, created_by)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (error_id, window_id, None, "internal_validation",
                 "2", rule["severity"], rule["rule_code"], rule["category"],
                 rule["error_message_template"].replace("{student_id}", student_id),
                 student_id, None, rule["category"],
                 "", json.dumps(viol_dict),
                 "open", "", "", "", "", "", "", "",
                 company_id, now, now, user_id)
            )
            violations_found += 1

    conn.commit()
    ok({"window_id": window_id, "student_id": student_id,
        "violations_found": violations_found, "run_at": now,
        "message": f"Student validation complete: {violations_found} violations found"})


def get_validation_results(conn, args):
    """Get validation results for a window with summary counts by severity."""
    window_id = getattr(args, "window_id", None)
    if not window_id:
        err("--window-id is required")

    limit = int(getattr(args, "limit", None) or 100)
    offset = int(getattr(args, "offset", None) or 0)

    rows = conn.execute(
        """SELECT vr.*, vru.rule_code, vru.category, vru.severity, vru.name as rule_name
           FROM sr_validation_result vr
           JOIN sr_validation_rule vru ON vru.id = vr.rule_id
           WHERE vr.collection_window_id = ?
           ORDER BY vru.severity, vru.category
           LIMIT ? OFFSET ?""",
        (window_id, limit, offset)
    ).fetchall()

    # Summary by severity
    summary = conn.execute(
        """SELECT vru.severity, COUNT(*) as count
           FROM sr_validation_result vr
           JOIN sr_validation_rule vru ON vru.id = vr.rule_id
           WHERE vr.collection_window_id = ? AND vr.is_resolved = 0
           GROUP BY vru.severity""",
        (window_id,)
    ).fetchall()

    ok({
        "window_id": window_id,
        "results": [dict(r) for r in rows],
        "count": len(rows),
        "summary_by_severity": {r["severity"]: r["count"] for r in summary}
    })


# ─────────────────────────────────────────────────────────────────────────────
# SUBMISSION ERROR MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

def assign_submission_error(conn, args):
    error_id = getattr(args, "error_id", None)
    assigned_to = getattr(args, "assigned_to", None)

    if not error_id:
        err("--error-id is required")
    if not assigned_to:
        err("--assigned-to is required")

    row = conn.execute("SELECT id FROM sr_submission_error WHERE id = ?", (error_id,)).fetchone()
    if not row:
        err(f"Submission error {error_id} not found")

    now = _now_iso()
    conn.execute(
        """UPDATE sr_submission_error
           SET assigned_to = ?, assigned_at = ?, resolution_status = 'in_progress', updated_at = ?
           WHERE id = ?""",
        (assigned_to, now, now, error_id)
    )
    conn.commit()
    audit(conn, "sr_submission_error", error_id, "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": error_id, "assigned_to": assigned_to, "assigned_at": now,
        "message": "Error assigned"})


def update_error_resolution(conn, args):
    error_id = getattr(args, "error_id", None)
    resolution_status = getattr(args, "resolution_status", None)

    if not error_id:
        err("--error-id is required")
    if not resolution_status:
        err("--resolution-status is required")
    if resolution_status not in VALID_RESOLUTION_STATUSES:
        err(f"--resolution-status must be one of: {', '.join(VALID_RESOLUTION_STATUSES)}")

    row = conn.execute("SELECT id FROM sr_submission_error WHERE id = ?", (error_id,)).fetchone()
    if not row:
        err(f"Submission error {error_id} not found")

    resolution_method = getattr(args, "resolution_method", None) or ""
    if resolution_method and resolution_method not in VALID_RESOLUTION_METHODS:
        err(f"--resolution-method must be one of: {', '.join(VALID_RESOLUTION_METHODS)}")

    now = _now_iso()
    user_id = getattr(args, "user_id", None) or ""

    updates = {
        "resolution_status": resolution_status,
        "updated_at": now
    }
    if resolution_status == "resolved":
        updates["resolved_by"] = user_id
        updates["resolved_at"] = now
    if resolution_method:
        updates["resolution_method"] = resolution_method
    notes = getattr(args, "resolution_notes", None)
    if notes:
        updates["resolution_notes"] = notes

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE sr_submission_error SET {set_clause} WHERE id = ?",
        list(updates.values()) + [error_id]
    )
    conn.commit()

    # If resolved, also mark corresponding validation result as resolved
    if resolution_status == "resolved":
        conn.execute(
            """UPDATE sr_validation_result SET is_resolved = 1, resolved_at = ?
               WHERE collection_window_id = (
                   SELECT collection_window_id FROM sr_submission_error WHERE id = ?
               ) AND error_detail LIKE '%' || (
                   SELECT COALESCE(student_id,'') FROM sr_submission_error WHERE id = ?
               ) || '%'""",
            (now, error_id, error_id)
        )
        conn.commit()

    audit(conn, "sr_submission_error", error_id, "UPDATE", user_id)
    ok({"id": error_id, "resolution_status": resolution_status,
        "message": f"Error {resolution_status}"})


def list_submission_errors(conn, args):
    window_id = getattr(args, "window_id", None)
    if not window_id:
        err("--window-id is required")

    conditions = ["collection_window_id = ?"]
    params = [window_id]

    severity = getattr(args, "severity", None)
    if severity:
        conditions.append("severity = ?")
        params.append(severity)

    resolution_status = getattr(args, "resolution_status", None)
    if resolution_status:
        conditions.append("resolution_status = ?")
        params.append(resolution_status)

    error_category = getattr(args, "error_category", None)
    if error_category:
        conditions.append("error_category = ?")
        params.append(error_category)

    student_id = getattr(args, "student_id", None)
    if student_id:
        conditions.append("student_id = ?")
        params.append(student_id)

    assigned_to = getattr(args, "assigned_to", None)
    if assigned_to:
        conditions.append("assigned_to = ?")
        params.append(assigned_to)

    where = " AND ".join(conditions)
    limit = int(getattr(args, "limit", None) or 100)
    offset = int(getattr(args, "offset", None) or 0)

    rows = conn.execute(
        f"""SELECT * FROM sr_submission_error WHERE {where}
            ORDER BY severity, created_at LIMIT ? OFFSET ?""",
        params + [limit, offset]
    ).fetchall()

    ok({"errors": [dict(r) for r in rows], "count": len(rows)})


def get_error_dashboard(conn, args):
    """Error count summary by severity × category × resolution_status."""
    window_id = getattr(args, "window_id", None)
    if not window_id:
        err("--window-id is required")

    rows = conn.execute(
        """SELECT severity, error_category, resolution_status, COUNT(*) as count
           FROM sr_submission_error
           WHERE collection_window_id = ?
           GROUP BY severity, error_category, resolution_status
           ORDER BY severity, error_category""",
        (window_id,)
    ).fetchall()

    # Totals by severity
    by_severity = conn.execute(
        """SELECT severity, COUNT(*) as total,
               SUM(CASE WHEN resolution_status='open' THEN 1 ELSE 0 END) as open_count,
               SUM(CASE WHEN resolution_status='resolved' THEN 1 ELSE 0 END) as resolved_count
           FROM sr_submission_error WHERE collection_window_id = ?
           GROUP BY severity""",
        (window_id,)
    ).fetchall()

    ok({
        "window_id": window_id,
        "breakdown": [dict(r) for r in rows],
        "by_severity": {r["severity"]: dict(r) for r in by_severity},
    })


def bulk_assign_errors(conn, args):
    """Assign multiple errors to a staff member."""
    error_ids_raw = getattr(args, "error_ids", None)
    assigned_to = getattr(args, "assigned_to", None)

    if not error_ids_raw:
        err("--error-ids is required (JSON array of error IDs)")
    if not assigned_to:
        err("--assigned-to is required")

    try:
        error_ids = json.loads(error_ids_raw) if isinstance(error_ids_raw, str) else error_ids_raw
        if not isinstance(error_ids, list):
            err("--error-ids must be a JSON array")
    except (json.JSONDecodeError, TypeError):
        err("--error-ids must be valid JSON array")

    now = _now_iso()
    assigned_count = 0

    for eid in error_ids:
        result = conn.execute(
            """UPDATE sr_submission_error
               SET assigned_to = ?, assigned_at = ?, resolution_status = 'in_progress', updated_at = ?
               WHERE id = ?""",
            (assigned_to, now, now, eid)
        )
        if result.rowcount > 0:
            assigned_count += 1

    conn.commit()
    ok({"assigned_count": assigned_count, "assigned_to": assigned_to,
        "message": f"{assigned_count} errors assigned to {assigned_to}"})


def escalate_error(conn, args):
    """Escalate error to state help desk; records state_ticket_id."""
    error_id = getattr(args, "error_id", None)
    state_ticket_id = getattr(args, "state_ticket_id", None)

    if not error_id:
        err("--error-id is required")
    if not state_ticket_id:
        err("--state-ticket-id is required")

    row = conn.execute("SELECT id FROM sr_submission_error WHERE id = ?", (error_id,)).fetchone()
    if not row:
        err(f"Submission error {error_id} not found")

    now = _now_iso()
    conn.execute(
        "UPDATE sr_submission_error SET state_ticket_id = ?, resolution_status = 'in_progress', updated_at = ? WHERE id = ?",
        (state_ticket_id, now, error_id)
    )
    conn.commit()
    audit(conn, "sr_submission_error", error_id, "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": error_id, "state_ticket_id": state_ticket_id,
        "message": "Error escalated to state help desk"})


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────
ACTIONS = {
    "add-validation-rule": add_validation_rule,
    "update-validation-rule": update_validation_rule,
    "get-validation-rule": get_validation_rule,
    "list-validation-rules": list_validation_rules,
    "update-validation-rule-status": toggle_validation_rule,
    "import-validation-rules": seed_validation_rules,
    "apply-validation": run_validation,
    "apply-student-validation": run_validation_for_student,
    "get-validation-results": get_validation_results,
    "assign-submission-error": assign_submission_error,
    "update-error-resolution": update_error_resolution,
    "list-submission-errors": list_submission_errors,
    "get-error-dashboard": get_error_dashboard,
    "assign-errors": bulk_assign_errors,
    "submit-error-escalation": escalate_error,
}
