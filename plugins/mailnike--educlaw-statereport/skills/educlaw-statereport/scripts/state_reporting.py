"""EduClaw State Reporting — state_reporting domain module

Collection windows, snapshot engine, ADA/ADM calculation, chronic absenteeism,
ADA funding dashboard, enrollment and CRDC reports, org-to-NCES mapping.

Imported by db_query.py (unified router).
"""
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection
    from erpclaw_lib.response import ok, err
    from erpclaw_lib.audit import audit
    from erpclaw_lib.decimal_utils import to_decimal
except ImportError:
    def to_decimal(v, places=4):
        try:
            return Decimal(str(v)).quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP)
        except Exception:
            return Decimal("0")

SKILL = "educlaw-statereport"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

VALID_WINDOW_TYPES = (
    "fall_enrollment", "fall_sped", "winter_update", "spring_enrollment",
    "eoy_attendance", "eoy_discipline", "eoy_grades", "staffing", "crdc", "summer_correction"
)
VALID_WINDOW_STATUSES = (
    "upcoming", "open", "data_entry", "validation", "snapshot", "submitted", "certified", "closed"
)
WINDOW_STATUS_ORDER = [
    "upcoming", "open", "data_entry", "validation", "snapshot", "submitted", "certified", "closed"
]
VALID_RECORD_TYPES = (
    "student_enrollment", "attendance_summary", "sped_placement",
    "el_program", "discipline_summary", "staff_assignment"
)


# ─────────────────────────────────────────────────────────────────────────────
# COLLECTION WINDOW
# ─────────────────────────────────────────────────────────────────────────────

def add_collection_window(conn, args):
    company_id = getattr(args, "company_id", None)
    name = getattr(args, "name", None)
    state_code = getattr(args, "state_code", None)
    window_type = getattr(args, "window_type", None)
    school_year = getattr(args, "school_year", None)

    if not company_id:
        err("--company-id is required")
    if not name:
        err("--name is required")
    if not state_code:
        err("--state-code is required")
    if not window_type:
        err("--window-type is required")
    if window_type not in VALID_WINDOW_TYPES:
        err(f"--window-type must be one of: {', '.join(VALID_WINDOW_TYPES)}")
    if not school_year:
        err("--school-year is required")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    # Optional FK: academic_year_id
    academic_year_id = getattr(args, "academic_year_id", None)
    if academic_year_id:
        if not conn.execute("SELECT id FROM educlaw_academic_year WHERE id = ?", (academic_year_id,)).fetchone():
            err(f"Academic year {academic_year_id} not found")

    # Optional FK: edfi_config_id
    edfi_config_id = getattr(args, "edfi_config_id", None)
    if edfi_config_id:
        if not conn.execute("SELECT id FROM sr_edfi_config WHERE id = ?", (edfi_config_id,)).fetchone():
            err(f"Ed-Fi config {edfi_config_id} not found")

    required_data_categories = getattr(args, "required_data_categories", None) or "[]"

    window_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO sr_collection_window
               (id, name, state_code, window_type, school_year, academic_year_id,
                open_date, close_date, snapshot_date, status,
                required_data_categories, description, is_federal_required,
                edfi_config_id, company_id, created_at, updated_at, created_by)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (window_id, name, state_code, window_type, int(school_year),
             academic_year_id,
             getattr(args, "open_date", None) or "",
             getattr(args, "close_date", None) or "",
             getattr(args, "snapshot_date", None) or "",
             "upcoming",
             required_data_categories,
             getattr(args, "description", None) or "",
             int(getattr(args, "is_federal_required", None) or 0),
             edfi_config_id,
             company_id, now, now, getattr(args, "user_id", None) or "")
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        err(f"Cannot create collection window: {e}")

    audit(conn, "sr_collection_window", window_id, "INSERT", getattr(args, "user_id", None) or "")
    ok({"id": window_id, "name": name, "window_type": window_type,
        "school_year": int(school_year), "window_status": "upcoming",
        "message": "Collection window created"})


def update_collection_window(conn, args):
    window_id = getattr(args, "window_id", None)
    if not window_id:
        err("--window-id is required")

    row = conn.execute("SELECT * FROM sr_collection_window WHERE id = ?", (window_id,)).fetchone()
    if not row:
        err(f"Collection window {window_id} not found")

    # Only allow updates if status is upcoming or open
    current_status = row["status"]
    if current_status not in ("upcoming", "open"):
        err(f"Cannot update window in status '{current_status}'. Only upcoming/open windows can be updated.")

    updates = {}
    for field in [
        "name", "open_date", "close_date", "snapshot_date",
        "description", "is_federal_required", "edfi_config_id",
        "required_data_categories"
    ]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    if not updates:
        err("No fields to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE sr_collection_window SET {set_clause} WHERE id = ?",
        list(updates.values()) + [window_id]
    )
    conn.commit()
    audit(conn, "sr_collection_window", window_id, "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": window_id, "message": "Collection window updated"})


def get_collection_window(conn, args):
    window_id = getattr(args, "window_id", None)
    if not window_id:
        err("--window-id is required")

    row = conn.execute("SELECT * FROM sr_collection_window WHERE id = ?", (window_id,)).fetchone()
    if not row:
        err(f"Collection window {window_id} not found")

    window = dict(row)
    try:
        window["required_data_categories"] = json.loads(window["required_data_categories"])
    except (json.JSONDecodeError, TypeError):
        window["required_data_categories"] = []

    # Attach snapshot summary if exists
    snapshot = conn.execute(
        "SELECT * FROM sr_snapshot WHERE collection_window_id = ?", (window_id,)
    ).fetchone()
    window["snapshot"] = dict(snapshot) if snapshot else None

    # Error count summary
    error_counts = conn.execute(
        """SELECT severity, resolution_status, COUNT(*) as count
           FROM sr_submission_error WHERE collection_window_id = ?
           GROUP BY severity, resolution_status""",
        (window_id,)
    ).fetchall()
    window["error_summary"] = [dict(r) for r in error_counts]

    ok(window)


def list_collection_windows(conn, args):
    company_id = getattr(args, "company_id", None)
    if not company_id:
        err("--company-id is required")

    conditions = ["company_id = ?"]
    params = [company_id]

    status_filter = getattr(args, "window_status", None)
    if status_filter:
        conditions.append("status = ?")
        params.append(status_filter)

    school_year = getattr(args, "school_year", None)
    if school_year:
        conditions.append("school_year = ?")
        params.append(int(school_year))

    state_code = getattr(args, "state_code", None)
    if state_code:
        conditions.append("state_code = ?")
        params.append(state_code)

    window_type = getattr(args, "window_type", None)
    if window_type:
        conditions.append("window_type = ?")
        params.append(window_type)

    where = " AND ".join(conditions)
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)

    rows = conn.execute(
        f"SELECT * FROM sr_collection_window WHERE {where} ORDER BY school_year DESC, open_date LIMIT ? OFFSET ?",
        params + [limit, offset]
    ).fetchall()

    result = []
    for r in rows:
        rec = dict(r)
        try:
            rec["required_data_categories"] = json.loads(rec["required_data_categories"])
        except (json.JSONDecodeError, TypeError):
            rec["required_data_categories"] = []
        result.append(rec)

    ok({"windows": result, "count": len(result)})


def advance_window_status(conn, args):
    window_id = getattr(args, "window_id", None)
    if not window_id:
        err("--window-id is required")

    row = conn.execute("SELECT * FROM sr_collection_window WHERE id = ?", (window_id,)).fetchone()
    if not row:
        err(f"Collection window {window_id} not found")

    current_status = row["status"]
    if current_status == "closed":
        err("Window is already closed and cannot be advanced")

    current_idx = WINDOW_STATUS_ORDER.index(current_status)
    next_status = WINDOW_STATUS_ORDER[current_idx + 1]

    # Validate prerequisites for transition to snapshot
    if next_status == "snapshot":
        critical_errors = conn.execute(
            """SELECT COUNT(*) FROM sr_submission_error
               WHERE collection_window_id = ? AND severity = 'critical' AND resolution_status = 'open'""",
            (window_id,)
        ).fetchone()[0]
        if critical_errors > 0:
            err(f"Cannot advance to snapshot: {critical_errors} critical unresolved error(s) exist. "
                f"Resolve all critical errors before taking snapshot.")

    now = _now_iso()
    conn.execute(
        "UPDATE sr_collection_window SET status = ?, updated_at = ? WHERE id = ?",
        (next_status, now, window_id)
    )
    conn.commit()
    audit(conn, "sr_collection_window", window_id, "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": window_id, "previous_status": current_status,
        "window_status": next_status,
        "message": f"Window advanced from '{current_status}' to '{next_status}'"})


# ─────────────────────────────────────────────────────────────────────────────
# SNAPSHOT ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def take_snapshot(conn, args):
    window_id = getattr(args, "window_id", None)
    user_id = getattr(args, "user_id", None) or ""

    if not window_id:
        err("--window-id is required")

    window = conn.execute("SELECT * FROM sr_collection_window WHERE id = ?", (window_id,)).fetchone()
    if not window:
        err(f"Collection window {window_id} not found")

    company_id = window["company_id"]
    school_year = window["school_year"]

    # Check no existing snapshot
    existing = conn.execute(
        "SELECT id FROM sr_snapshot WHERE collection_window_id = ?", (window_id,)
    ).fetchone()
    if existing:
        err(f"Snapshot already exists for this window: {existing['id']}")

    now = _now_iso()

    # Gather student counts
    total_students = conn.execute(
        "SELECT COUNT(*) FROM educlaw_student WHERE company_id = ? AND status = 'active'",
        (company_id,)
    ).fetchone()[0]

    total_enrollment = conn.execute(
        """SELECT COUNT(*) FROM educlaw_program_enrollment
           WHERE company_id = ? AND enrollment_status = 'active'""",
        (company_id,)
    ).fetchone()[0]

    total_sped = conn.execute(
        "SELECT COUNT(*) FROM sr_student_supplement WHERE company_id = ? AND is_sped = 1",
        (company_id,)
    ).fetchone()[0]

    total_el = conn.execute(
        "SELECT COUNT(*) FROM sr_student_supplement WHERE company_id = ? AND is_el = 1",
        (company_id,)
    ).fetchone()[0]

    total_econ = conn.execute(
        "SELECT COUNT(*) FROM sr_student_supplement WHERE company_id = ? AND is_economically_disadvantaged = 1",
        (company_id,)
    ).fetchone()[0]

    total_homeless = conn.execute(
        "SELECT COUNT(*) FROM sr_student_supplement WHERE company_id = ? AND is_homeless = 1",
        (company_id,)
    ).fetchone()[0]

    error_count = conn.execute(
        """SELECT COUNT(*) FROM sr_submission_error
           WHERE collection_window_id = ? AND resolution_status = 'open'""",
        (window_id,)
    ).fetchone()[0]

    snapshot_id = str(uuid.uuid4())

    conn.execute(
        """INSERT INTO sr_snapshot
           (id, collection_window_id, snapshot_taken_at, snapshot_taken_by,
            total_students, total_enrollment, total_sped, total_el,
            total_economically_disadvantaged, total_homeless,
            ada_total, adm_total, chronic_absenteeism_count, error_count_at_snapshot,
            snapshot_status, certified_by, certified_at, certification_notes,
            company_id, created_at, updated_at, created_by)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (snapshot_id, window_id, now, user_id,
         total_students, total_enrollment, total_sped, total_el,
         total_econ, total_homeless,
         "", "", 0, error_count,
         "draft", "", "", "",
         company_id, now, now, user_id)
    )

    # Freeze student enrollment records (INSERT-only snapshot records)
    enrolled_students = conn.execute(
        """SELECT pe.student_id, s.first_name, s.last_name, s.grade_level,
                  pe.enrollment_date, pe.enrollment_status, pe.program_id
           FROM educlaw_program_enrollment pe
           JOIN educlaw_student s ON s.id = pe.student_id
           WHERE pe.company_id = ? AND pe.enrollment_status = 'active'""",
        (company_id,)
    ).fetchall()

    for student_row in enrolled_students:
        student_id = student_row["student_id"]
        # Get supplement data
        supp = conn.execute(
            "SELECT * FROM sr_student_supplement WHERE student_id = ?", (student_id,)
        ).fetchone()

        data_json = {
            "student_id": student_id,
            "first_name": student_row["first_name"],
            "last_name": student_row["last_name"],
            "grade_level": student_row["grade_level"],
            "enrollment_date": student_row["enrollment_date"],
            "enrollment_status": student_row["enrollment_status"],
        }
        if supp:
            data_json["ssid"] = supp["ssid"]
            data_json["race_federal_rollup"] = supp["race_federal_rollup"]
            data_json["is_el"] = supp["is_el"]
            data_json["is_sped"] = supp["is_sped"]
            try:
                data_json["race_codes"] = json.loads(supp["race_codes"])
            except Exception:
                data_json["race_codes"] = []

        rec_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO sr_snapshot_record
               (id, snapshot_id, student_id, record_type, data_json, school_year,
                company_id, created_at)
               VALUES (?,?,?,?,?,?,?,?)""",
            (rec_id, snapshot_id, student_id, "student_enrollment",
             json.dumps(data_json), school_year, company_id, now)
        )

    # Update window status to snapshot
    conn.execute(
        "UPDATE sr_collection_window SET status = 'snapshot', updated_at = ? WHERE id = ?",
        (now, window_id)
    )

    conn.commit()
    audit(conn, "sr_snapshot", snapshot_id, "INSERT", user_id)
    ok({"id": snapshot_id, "collection_window_id": window_id,
        "total_students": total_students, "total_enrollment": total_enrollment,
        "total_sped": total_sped, "total_el": total_el,
        "snapshot_status": "draft",
        "message": "Snapshot taken successfully"})


def get_snapshot(conn, args):
    snapshot_id = getattr(args, "snapshot_id", None)
    window_id = getattr(args, "window_id", None)

    if snapshot_id:
        row = conn.execute("SELECT * FROM sr_snapshot WHERE id = ?", (snapshot_id,)).fetchone()
    elif window_id:
        row = conn.execute(
            "SELECT * FROM sr_snapshot WHERE collection_window_id = ?", (window_id,)
        ).fetchone()
    else:
        err("--snapshot-id or --window-id is required")

    if not row:
        err("Snapshot not found")

    ok(dict(row))


def list_snapshot_records(conn, args):
    snapshot_id = getattr(args, "snapshot_id", None)
    if not snapshot_id:
        err("--snapshot-id is required")

    conditions = ["snapshot_id = ?"]
    params = [snapshot_id]

    record_type = getattr(args, "record_type", None)
    if record_type:
        conditions.append("record_type = ?")
        params.append(record_type)

    where = " AND ".join(conditions)
    limit = int(getattr(args, "limit", None) or 100)
    offset = int(getattr(args, "offset", None) or 0)

    rows = conn.execute(
        f"SELECT * FROM sr_snapshot_record WHERE {where} ORDER BY created_at LIMIT ? OFFSET ?",
        params + [limit, offset]
    ).fetchall()

    result = []
    for r in rows:
        rec = dict(r)
        try:
            rec["data_json"] = json.loads(rec["data_json"])
        except (json.JSONDecodeError, TypeError):
            rec["data_json"] = {}
        result.append(rec)

    ok({"records": result, "count": len(result)})


# ─────────────────────────────────────────────────────────────────────────────
# ADA / ADM CALCULATION
# ─────────────────────────────────────────────────────────────────────────────

def calculate_ada(conn, args):
    """Calculate ADA/ADM for a collection window or date range."""
    company_id = getattr(args, "company_id", None)
    date_from = getattr(args, "date_from", None)
    date_to = getattr(args, "date_to", None)
    school_year = getattr(args, "school_year", None)

    if not company_id:
        err("--company-id is required")

    # Resolve date range from school_year if not given
    if not date_from and school_year:
        yr = int(school_year)
        date_from = f"{yr-1}-07-01"
        date_to = f"{yr}-06-30"
    elif not date_from:
        err("--date-from or --school-year is required")

    if not date_to:
        date_to = _now_iso()[:10]

    # Count school days (days with any attendance record)
    school_days = conn.execute(
        """SELECT COUNT(DISTINCT attendance_date) FROM educlaw_student_attendance
           WHERE company_id = ? AND attendance_date >= ? AND attendance_date <= ?""",
        (company_id, date_from, date_to)
    ).fetchone()[0]

    if school_days == 0:
        ok({"company_id": company_id, "date_from": date_from, "date_to": date_to,
            "school_days": 0, "ada": "0.0000", "adm": "0.0000",
            "ada_rate": "0.0000",
            "message": "No attendance records found for this period"})
        return

    # Total enrolled (ADM = average daily membership)
    total_enrolled = conn.execute(
        "SELECT COUNT(*) FROM educlaw_program_enrollment WHERE company_id = ? AND enrollment_status = 'active'",
        (company_id,)
    ).fetchone()[0]

    # Present + half_day attendance
    # ADA = sum of attendance credits / school_days
    # present = 1.0, half_day = 0.5, absent/tardy/excused = 0
    present_count = conn.execute(
        """SELECT COUNT(*) FROM educlaw_student_attendance
           WHERE company_id = ? AND attendance_date >= ? AND attendance_date <= ?
           AND attendance_status = 'present'""",
        (company_id, date_from, date_to)
    ).fetchone()[0]

    half_day_count = conn.execute(
        """SELECT COUNT(*) FROM educlaw_student_attendance
           WHERE company_id = ? AND attendance_date >= ? AND attendance_date <= ?
           AND attendance_status = 'half_day'""",
        (company_id, date_from, date_to)
    ).fetchone()[0]

    total_attendance_credits = Decimal(str(present_count)) + Decimal(str(half_day_count)) * Decimal("0.5")
    ada = (total_attendance_credits / Decimal(str(school_days))).quantize(
        Decimal("0.0001"), rounding=ROUND_HALF_UP
    )
    adm = Decimal(str(total_enrolled))
    ada_rate = (ada / adm * Decimal("100")).quantize(
        Decimal("0.0001"), rounding=ROUND_HALF_UP
    ) if adm > 0 else Decimal("0")

    ok({
        "company_id": company_id,
        "date_from": date_from,
        "date_to": date_to,
        "school_days": school_days,
        "total_enrolled_adm": total_enrolled,
        "present_days": present_count,
        "half_days": half_day_count,
        "ada": str(ada),
        "adm": str(adm),
        "ada_rate_pct": str(ada_rate),
        "message": "ADA/ADM calculated"
    })


def get_ada_dashboard(conn, args):
    """Real-time ADA with trend and funding impact."""
    company_id = getattr(args, "company_id", None)
    school_year = getattr(args, "school_year", None)
    per_pupil_rate = getattr(args, "per_pupil_rate", None) or "10000"

    if not company_id:
        err("--company-id is required")
    if not school_year:
        err("--school-year is required")

    yr = int(school_year)
    date_from = f"{yr-1}-07-01"
    date_to = _now_iso()[:10]

    # Current ADA
    school_days = conn.execute(
        """SELECT COUNT(DISTINCT attendance_date) FROM educlaw_student_attendance
           WHERE company_id = ? AND attendance_date >= ? AND attendance_date <= ?""",
        (company_id, date_from, date_to)
    ).fetchone()[0]

    present_count = conn.execute(
        """SELECT COUNT(*) FROM educlaw_student_attendance
           WHERE company_id = ? AND attendance_date >= ? AND attendance_date <= ?
           AND attendance_status = 'present'""",
        (company_id, date_from, date_to)
    ).fetchone()[0]

    half_day_count = conn.execute(
        """SELECT COUNT(*) FROM educlaw_student_attendance
           WHERE company_id = ? AND attendance_date >= ? AND attendance_date <= ?
           AND attendance_status = 'half_day'""",
        (company_id, date_from, date_to)
    ).fetchone()[0]

    total_enrolled = conn.execute(
        "SELECT COUNT(*) FROM educlaw_program_enrollment WHERE company_id = ? AND enrollment_status = 'active'",
        (company_id,)
    ).fetchone()[0]

    if school_days > 0 and total_enrolled > 0:
        total_credits = Decimal(str(present_count)) + Decimal(str(half_day_count)) * Decimal("0.5")
        ada = (total_credits / Decimal(str(school_days))).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        ada_rate = (ada / Decimal(str(total_enrolled)) * Decimal("100")).quantize(
            Decimal("0.0001"), rounding=ROUND_HALF_UP
        )
        # Projected annual ADA (180 school days typical)
        projected_annual_ada = ada
        # Funding impact: ADA × per_pupil_rate
        ppr = Decimal(str(per_pupil_rate))
        funding_allocation = (ada * ppr).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        # 1% ADA improvement impact
        one_pct_impact = (ada * Decimal("0.01") * ppr).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        ada = Decimal("0")
        ada_rate = Decimal("0")
        projected_annual_ada = Decimal("0")
        funding_allocation = Decimal("0")
        one_pct_impact = Decimal("0")

    ok({
        "company_id": company_id,
        "school_year": yr,
        "school_days_to_date": school_days,
        "current_enrollment_adm": total_enrolled,
        "current_ada": str(ada),
        "current_ada_rate_pct": str(ada_rate),
        "projected_annual_ada": str(projected_annual_ada),
        "per_pupil_rate": str(per_pupil_rate),
        "estimated_funding_allocation": str(funding_allocation),
        "one_pct_improvement_value": str(one_pct_impact),
        "message": "ADA dashboard calculated"
    })


def identify_chronic_absenteeism(conn, args):
    """Flag students with ≥10% absent days for a school year."""
    company_id = getattr(args, "company_id", None)
    school_year = getattr(args, "school_year", None)
    threshold_pct = Decimal(str(getattr(args, "threshold", None) or "10"))

    if not company_id:
        err("--company-id is required")
    if not school_year:
        err("--school-year is required")

    yr = int(school_year)
    date_from = f"{yr-1}-07-01"
    date_to = f"{yr}-06-30"

    # Count school days
    school_days = conn.execute(
        """SELECT COUNT(DISTINCT attendance_date) FROM educlaw_student_attendance
           WHERE company_id = ? AND attendance_date >= ? AND attendance_date <= ?""",
        (company_id, date_from, date_to)
    ).fetchone()[0]

    if school_days == 0:
        ok({"company_id": company_id, "school_year": yr, "threshold_pct": str(threshold_pct),
            "school_days": 0, "chronic_absentees": [], "count": 0,
            "message": "No attendance records found"})
        return

    threshold_days = (Decimal(str(school_days)) * threshold_pct / Decimal("100")).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )

    # Get per-student absent counts
    absent_counts = conn.execute(
        """SELECT student_id, COUNT(*) as absent_days
           FROM educlaw_student_attendance
           WHERE company_id = ? AND attendance_date >= ? AND attendance_date <= ?
           AND attendance_status IN ('absent', 'excused')
           GROUP BY student_id
           HAVING COUNT(*) >= ?""",
        (company_id, date_from, date_to, int(threshold_days))
    ).fetchall()

    result = []
    for row in absent_counts:
        student = conn.execute(
            "SELECT first_name, last_name, grade_level FROM educlaw_student WHERE id = ?",
            (row["student_id"],)
        ).fetchone()
        absent_pct = (Decimal(str(row["absent_days"])) / Decimal(str(school_days)) * Decimal("100")).quantize(
            Decimal("0.1"), rounding=ROUND_HALF_UP
        )
        result.append({
            "student_id": row["student_id"],
            "first_name": student["first_name"] if student else "",
            "last_name": student["last_name"] if student else "",
            "grade_level": student["grade_level"] if student else "",
            "absent_days": row["absent_days"],
            "school_days": school_days,
            "absent_pct": str(absent_pct),
        })

    ok({
        "company_id": company_id,
        "school_year": yr,
        "school_days": school_days,
        "threshold_pct": str(threshold_pct),
        "threshold_days": int(threshold_days),
        "count": len(result),
        "chronic_absentees": result
    })


# ─────────────────────────────────────────────────────────────────────────────
# REPORTS
# ─────────────────────────────────────────────────────────────────────────────

def get_data_readiness_report(conn, args):
    """Compute data readiness score per category (0-100)."""
    company_id = getattr(args, "company_id", None)
    if not company_id:
        err("--company-id is required")

    # Total active students
    total = conn.execute(
        "SELECT COUNT(*) FROM educlaw_student WHERE company_id = ? AND status = 'active'",
        (company_id,)
    ).fetchone()[0]

    if total == 0:
        ok({"company_id": company_id, "total_students": 0, "scores": {},
            "overall_score": "0", "message": "No active students found"})
        return

    # Demographics: has supplement + SSID assigned + race set
    demo_complete = conn.execute(
        """SELECT COUNT(*) FROM sr_student_supplement ss
           JOIN educlaw_student s ON s.id = ss.student_id
           WHERE ss.company_id = ? AND s.status = 'active'
           AND ss.ssid_status = 'assigned' AND ss.race_codes != '[]'""",
        (company_id,)
    ).fetchone()[0]

    # SPED: all is_sped=1 students have a placement
    sped_students = conn.execute(
        "SELECT COUNT(*) FROM sr_student_supplement WHERE company_id = ? AND is_sped = 1",
        (company_id,)
    ).fetchone()[0]

    sped_with_placement = conn.execute(
        """SELECT COUNT(DISTINCT ss.student_id)
           FROM sr_student_supplement ss
           JOIN sr_sped_placement sp ON sp.student_id = ss.student_id
           WHERE ss.company_id = ? AND ss.is_sped = 1""",
        (company_id,)
    ).fetchone()[0]

    # EL: all is_el=1 students have EL program
    el_students = conn.execute(
        "SELECT COUNT(*) FROM sr_student_supplement WHERE company_id = ? AND is_el = 1",
        (company_id,)
    ).fetchone()[0]

    el_with_program = conn.execute(
        """SELECT COUNT(DISTINCT ss.student_id)
           FROM sr_student_supplement ss
           JOIN sr_el_program ep ON ep.student_id = ss.student_id
           WHERE ss.company_id = ? AND ss.is_el = 1""",
        (company_id,)
    ).fetchone()[0]

    # Attendance: students with at least 1 attendance record
    students_with_attendance = conn.execute(
        """SELECT COUNT(DISTINCT sa.student_id)
           FROM educlaw_student_attendance sa
           JOIN educlaw_student s ON s.id = sa.student_id
           WHERE sa.company_id = ? AND s.status = 'active'""",
        (company_id,)
    ).fetchone()[0]

    def pct(num, den):
        if den == 0:
            return "100"
        return str((Decimal(str(num)) / Decimal(str(den)) * Decimal("100")).quantize(
            Decimal("0.1"), rounding=ROUND_HALF_UP
        ))

    scores = {
        "demographics": pct(demo_complete, total),
        "sped": pct(sped_with_placement, sped_students) if sped_students > 0 else "100",
        "el": pct(el_with_program, el_students) if el_students > 0 else "100",
        "attendance": pct(students_with_attendance, total),
    }

    # Overall: average of all category scores
    score_values = [Decimal(v) for v in scores.values()]
    overall = (sum(score_values) / Decimal(str(len(score_values)))).quantize(
        Decimal("0.1"), rounding=ROUND_HALF_UP
    )

    ok({
        "company_id": company_id,
        "total_students": total,
        "scores": scores,
        "overall_score": str(overall),
        "details": {
            "demo_students_complete": demo_complete,
            "sped_students": sped_students,
            "sped_with_placement": sped_with_placement,
            "el_students": el_students,
            "el_with_program": el_with_program,
            "students_with_attendance": students_with_attendance,
        }
    })


def generate_enrollment_report(conn, args):
    """Enrollment counts disaggregated by race, grade level, EL, SPED, economic status."""
    company_id = getattr(args, "company_id", None)
    school_year = getattr(args, "school_year", None)

    if not company_id:
        err("--company-id is required")
    if not school_year:
        err("--school-year is required")

    # By race
    by_race = conn.execute(
        """SELECT ss.race_federal_rollup, COUNT(*) as count
           FROM educlaw_program_enrollment pe
           JOIN sr_student_supplement ss ON ss.student_id = pe.student_id
           WHERE pe.company_id = ? AND pe.enrollment_status = 'active'
           GROUP BY ss.race_federal_rollup""",
        (company_id,)
    ).fetchall()

    # By grade level
    by_grade = conn.execute(
        """SELECT s.grade_level, COUNT(*) as count
           FROM educlaw_program_enrollment pe
           JOIN educlaw_student s ON s.id = pe.student_id
           WHERE pe.company_id = ? AND pe.enrollment_status = 'active'
           GROUP BY s.grade_level ORDER BY s.grade_level""",
        (company_id,)
    ).fetchall()

    # EL, SPED, economic counts
    by_subgroup = conn.execute(
        """SELECT
               SUM(ss.is_el) as el_count,
               SUM(ss.is_sped) as sped_count,
               SUM(ss.is_economically_disadvantaged) as econ_disadv_count,
               SUM(ss.is_homeless) as homeless_count,
               SUM(ss.is_migrant) as migrant_count,
               SUM(ss.is_foster_care) as foster_count
           FROM educlaw_program_enrollment pe
           JOIN sr_student_supplement ss ON ss.student_id = pe.student_id
           WHERE pe.company_id = ? AND pe.enrollment_status = 'active'""",
        (company_id,)
    ).fetchone()

    # Apply small-cell suppression N<10
    race_rows = []
    for r in by_race:
        row = dict(r)
        if row["count"] < 10:
            row["count"] = "<10"
            row["suppressed"] = True
        race_rows.append(row)

    ok({
        "company_id": company_id,
        "school_year": int(school_year),
        "by_race": race_rows,
        "by_grade_level": [dict(r) for r in by_grade],
        "subgroup_counts": dict(by_subgroup) if by_subgroup else {},
    })


def generate_crdc_report(conn, args):
    """CRDC-formatted data export by race/sex/disability subgroups."""
    company_id = getattr(args, "company_id", None)
    school_year = getattr(args, "school_year", None)

    if not company_id:
        err("--company-id is required")
    if not school_year:
        err("--school-year is required")

    yr = int(school_year)

    # Enrollment by race × sex
    enrollment_by_subgroup = conn.execute(
        """SELECT ss.race_federal_rollup, s.gender, COUNT(*) as count
           FROM educlaw_program_enrollment pe
           JOIN educlaw_student s ON s.id = pe.student_id
           LEFT JOIN sr_student_supplement ss ON ss.student_id = pe.student_id
           WHERE pe.company_id = ? AND pe.enrollment_status = 'active'
           GROUP BY ss.race_federal_rollup, s.gender""",
        (company_id,)
    ).fetchall()

    # Discipline by race × sex × action_type
    discipline_by_subgroup = conn.execute(
        """SELECT ss.race_federal_rollup, s.gender, da.action_type, COUNT(*) as count
           FROM sr_discipline_action da
           JOIN educlaw_student s ON s.id = da.student_id
           LEFT JOIN sr_student_supplement ss ON ss.student_id = da.student_id
           JOIN sr_discipline_incident di ON di.id = da.incident_id
           WHERE da.company_id = ? AND di.school_year = ?
           GROUP BY ss.race_federal_rollup, s.gender, da.action_type""",
        (company_id, yr)
    ).fetchall()

    # IDEA students enrolled
    idea_enrollment = conn.execute(
        """SELECT ss.race_federal_rollup, s.gender, COUNT(*) as count
           FROM educlaw_program_enrollment pe
           JOIN educlaw_student s ON s.id = pe.student_id
           JOIN sr_student_supplement ss ON ss.student_id = pe.student_id
           WHERE pe.company_id = ? AND pe.enrollment_status = 'active' AND ss.is_sped = 1
           GROUP BY ss.race_federal_rollup, s.gender""",
        (company_id,)
    ).fetchall()

    def suppress(rows):
        result = []
        for r in rows:
            row = dict(r)
            if row["count"] < 10:
                row["count"] = "<10"
                row["suppressed"] = True
            result.append(row)
        return result

    ok({
        "company_id": company_id,
        "school_year": yr,
        "enrollment_by_race_sex": suppress(enrollment_by_subgroup),
        "discipline_by_race_sex_action": suppress(discipline_by_subgroup),
        "idea_enrollment_by_race_sex": suppress(idea_enrollment),
        "note": "Cells with N<10 are suppressed per CRDC privacy requirements"
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────
ACTIONS = {
    "add-collection-window": add_collection_window,
    "update-collection-window": update_collection_window,
    "get-collection-window": get_collection_window,
    "list-collection-windows": list_collection_windows,
    "apply-window-status": advance_window_status,
    "create-snapshot": take_snapshot,
    "get-snapshot": get_snapshot,
    "list-snapshot-records": list_snapshot_records,
    "generate-ada": calculate_ada,
    "get-ada-dashboard": get_ada_dashboard,
    "list-chronic-absenteeism": identify_chronic_absenteeism,
    "get-data-readiness-report": get_data_readiness_report,
    "generate-enrollment-report": generate_enrollment_report,
    "generate-crdc-report": generate_crdc_report,
}
