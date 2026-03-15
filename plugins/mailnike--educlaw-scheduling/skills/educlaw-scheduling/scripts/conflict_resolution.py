"""EduClaw Advanced Scheduling — conflict_resolution domain module

Actions: generate-conflict-check, list-conflicts, get-conflict, complete-conflict,
         accept-conflict, get-conflict-summary, get-singleton-conflict-map,
         get-student-conflict-report

11 conflict types: instructor_double_booking, room_double_booking, student_conflict,
instructor_overload, instructor_contract_violation, capacity_exceeded,
room_type_mismatch, credential_mismatch, singleton_overlap, contact_hours_deficit,
room_shortage

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

SKILL = "educlaw-scheduling"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

VALID_CONFLICT_TYPES = (
    "instructor_double_booking", "room_double_booking", "student_conflict",
    "instructor_overload", "instructor_contract_violation", "capacity_exceeded",
    "room_type_mismatch", "credential_mismatch", "singleton_overlap",
    "contact_hours_deficit", "room_shortage",
)
VALID_SEVERITIES = ("critical", "high", "medium", "low")
VALID_CONFLICT_STATUSES = ("open", "resolving", "resolved", "accepted", "superseded")

# Severity mapping per conflict type
_CONFLICT_SEVERITY = {
    "instructor_double_booking":    "critical",
    "room_double_booking":          "critical",
    "student_conflict":             "high",
    "instructor_overload":          "high",
    "instructor_contract_violation": "high",
    "capacity_exceeded":            "high",
    "singleton_overlap":            "high",
    "room_shortage":                "high",
    "room_type_mismatch":           "medium",
    "credential_mismatch":          "medium",
    "contact_hours_deficit":        "medium",
}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _insert_conflict(conn, master_id, conflict_type, description,
                     meeting_a=None, meeting_b=None,
                     instructor_id=None, room_id=None, student_id=None,
                     company_id=""):
    """Insert a schedule conflict record."""
    severity = _CONFLICT_SEVERITY.get(conflict_type, "medium")
    conflict_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute(
        """INSERT INTO educlaw_schedule_conflict
           (id, master_schedule_id, conflict_type, severity,
            section_meeting_id_a, section_meeting_id_b,
            instructor_id, room_id, student_id,
            description, conflict_status, resolution_notes,
            resolved_by, resolved_at, company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', '', '', '', ?, ?, ?, '')""",
        (conflict_id, master_id, conflict_type, severity,
         meeting_a, meeting_b, instructor_id, room_id, student_id,
         description, company_id, now, now)
    )
    return conflict_id


def _update_open_conflicts(conn, master_id):
    """Refresh open_conflicts count on master_schedule."""
    count = conn.execute(
        "SELECT COUNT(*) FROM educlaw_schedule_conflict "
        "WHERE master_schedule_id = ? AND conflict_status = 'open'",
        (master_id,)
    ).fetchone()[0]
    conn.execute(
        "UPDATE educlaw_master_schedule SET open_conflicts = ?, updated_at = datetime('now') "
        "WHERE id = ?",
        (count, master_id)
    )
    return count


def _get_master_company(conn, master_id):
    row = conn.execute(
        "SELECT company_id FROM educlaw_master_schedule WHERE id = ?", (master_id,)
    ).fetchone()
    return row["company_id"] if row else ""


# ─────────────────────────────────────────────────────────────────────────────
# CONFLICT CHECKERS (each returns list of new conflict IDs inserted)
# ─────────────────────────────────────────────────────────────────────────────

def _check_instructor_double_booking(conn, master_id, company_id):
    """CRITICAL: Same instructor in two meetings at same day_type + bell_period."""
    conflicts = []
    rows = conn.execute(
        """SELECT sm1.id as meeting_a, sm2.id as meeting_b,
                  sm1.instructor_id, sm1.day_type_id, sm1.bell_period_id,
                  dt.code as day_code, bp.period_name
           FROM educlaw_section_meeting sm1
           JOIN educlaw_section_meeting sm2
             ON sm1.master_schedule_id = sm2.master_schedule_id
             AND sm1.instructor_id = sm2.instructor_id
             AND sm1.day_type_id = sm2.day_type_id
             AND sm1.bell_period_id = sm2.bell_period_id
             AND sm1.id < sm2.id
           JOIN educlaw_day_type dt ON dt.id = sm1.day_type_id
           JOIN educlaw_bell_period bp ON bp.id = sm1.bell_period_id
           WHERE sm1.master_schedule_id = ? AND sm1.is_active = 1 AND sm2.is_active = 1
             AND sm1.instructor_id IS NOT NULL""",
        (master_id,)
    ).fetchall()
    for r in rows:
        rd = dict(r)
        desc = (f"Instructor double-booked on {rd['day_code']} / {rd['period_name']} "
                f"(meetings {rd['meeting_a'][:8]}… and {rd['meeting_b'][:8]}…)")
        cid = _insert_conflict(conn, master_id, "instructor_double_booking", desc,
                               meeting_a=rd["meeting_a"], meeting_b=rd["meeting_b"],
                               instructor_id=rd["instructor_id"], company_id=company_id)
        conflicts.append(cid)
    return conflicts


def _check_room_double_booking(conn, master_id, company_id):
    """CRITICAL: Same room booked twice in the same slot."""
    conflicts = []
    rows = conn.execute(
        """SELECT rb1.id as booking_a, rb2.id as booking_b,
                  rb1.room_id, rb1.day_type_id, rb1.bell_period_id,
                  dt.code as day_code, bp.period_name,
                  rb1.section_meeting_id as meeting_a,
                  rb2.section_meeting_id as meeting_b
           FROM educlaw_room_booking rb1
           JOIN educlaw_room_booking rb2
             ON rb1.room_id = rb2.room_id
             AND rb1.day_type_id = rb2.day_type_id
             AND rb1.bell_period_id = rb2.bell_period_id
             AND rb1.id < rb2.id
           JOIN educlaw_day_type dt ON dt.id = rb1.day_type_id
           JOIN educlaw_bell_period bp ON bp.id = rb1.bell_period_id
           WHERE (rb1.master_schedule_id = ? OR rb2.master_schedule_id = ?)
             AND rb1.booking_status != 'cancelled'
             AND rb2.booking_status != 'cancelled'""",
        (master_id, master_id)
    ).fetchall()
    for r in rows:
        rd = dict(r)
        desc = (f"Room double-booked on {rd['day_code']} / {rd['period_name']} "
                f"(room {rd['room_id'][:8]}…)")
        cid = _insert_conflict(conn, master_id, "room_double_booking", desc,
                               meeting_a=rd["meeting_a"], meeting_b=rd["meeting_b"],
                               room_id=rd["room_id"], company_id=company_id)
        conflicts.append(cid)
    return conflicts


def _check_student_conflicts(conn, master_id, company_id):
    """HIGH: Student enrolled in two sections placed at the same slot."""
    conflicts = []
    rows = conn.execute(
        """SELECT ce.student_id, sm.day_type_id, sm.bell_period_id,
                  GROUP_CONCAT(sm.id, ',') as meeting_ids,
                  COUNT(*) as cnt,
                  dt.code as day_code, bp.period_name
           FROM educlaw_section_meeting sm
           JOIN educlaw_course_enrollment ce ON ce.section_id = sm.section_id
           JOIN educlaw_day_type dt ON dt.id = sm.day_type_id
           JOIN educlaw_bell_period bp ON bp.id = sm.bell_period_id
           WHERE sm.master_schedule_id = ? AND sm.is_active = 1
             AND ce.enrollment_status = 'enrolled'
           GROUP BY ce.student_id, sm.day_type_id, sm.bell_period_id
           HAVING cnt > 1""",
        (master_id,)
    ).fetchall()
    for r in rows:
        rd = dict(r)
        meeting_ids = rd["meeting_ids"].split(",")
        meeting_a = meeting_ids[0] if len(meeting_ids) > 0 else None
        meeting_b = meeting_ids[1] if len(meeting_ids) > 1 else None
        desc = (f"Student {rd['student_id'][:8]}… has {rd['cnt']} sections "
                f"at {rd['day_code']} / {rd['period_name']}")
        cid = _insert_conflict(conn, master_id, "student_conflict", desc,
                               meeting_a=meeting_a, meeting_b=meeting_b,
                               student_id=rd["student_id"], company_id=company_id)
        conflicts.append(cid)
    return conflicts


def _check_instructor_overload(conn, master_id, company_id):
    """HIGH: Instructor exceeds their max_periods_per_day constraint."""
    conflicts = []
    rows = conn.execute(
        """SELECT sm.instructor_id, sm.day_type_id, COUNT(*) as period_count,
                  dt.code as day_code
           FROM educlaw_section_meeting sm
           JOIN educlaw_day_type dt ON dt.id = sm.day_type_id
           WHERE sm.master_schedule_id = ? AND sm.is_active = 1
             AND sm.instructor_id IS NOT NULL
           GROUP BY sm.instructor_id, sm.day_type_id""",
        (master_id,)
    ).fetchall()

    for r in rows:
        rd = dict(r)
        # Check constraint
        constraint = conn.execute(
            """SELECT constraint_value FROM educlaw_instructor_constraint
               WHERE instructor_id = ? AND constraint_type = 'max_periods_per_day'
                 AND is_active = 1
                 AND (day_type_id IS NULL OR day_type_id = ?)
               ORDER BY (day_type_id IS NOT NULL) DESC LIMIT 1""",
            (rd["instructor_id"], rd["day_type_id"])
        ).fetchone()
        if constraint and rd["period_count"] > constraint["constraint_value"]:
            desc = (f"Instructor {rd['instructor_id'][:8]}… has {rd['period_count']} periods "
                    f"on {rd['day_code']} (max allowed: {constraint['constraint_value']})")
            cid = _insert_conflict(conn, master_id, "instructor_overload", desc,
                                   instructor_id=rd["instructor_id"], company_id=company_id)
            conflicts.append(cid)
    return conflicts


def _check_instructor_contract_violation(conn, master_id, company_id):
    """HIGH: Instructor placed in a period they marked as unavailable."""
    conflicts = []
    rows = conn.execute(
        """SELECT sm.id as meeting_id, sm.instructor_id,
                  sm.day_type_id, sm.bell_period_id,
                  dt.code as day_code, bp.period_name,
                  ic.id as constraint_id
           FROM educlaw_section_meeting sm
           JOIN educlaw_instructor_constraint ic
             ON ic.instructor_id = sm.instructor_id
             AND ic.constraint_type = 'unavailable'
             AND ic.is_active = 1
             AND (ic.day_type_id IS NULL OR ic.day_type_id = sm.day_type_id)
             AND (ic.bell_period_id IS NULL OR ic.bell_period_id = sm.bell_period_id)
           JOIN educlaw_day_type dt ON dt.id = sm.day_type_id
           JOIN educlaw_bell_period bp ON bp.id = sm.bell_period_id
           WHERE sm.master_schedule_id = ? AND sm.is_active = 1""",
        (master_id,)
    ).fetchall()
    for r in rows:
        rd = dict(r)
        desc = (f"Instructor {rd['instructor_id'][:8]}… assigned to unavailable period "
                f"{rd['day_code']} / {rd['period_name']} (constraint {rd['constraint_id'][:8]}…)")
        cid = _insert_conflict(conn, master_id, "instructor_contract_violation", desc,
                               meeting_a=rd["meeting_id"], instructor_id=rd["instructor_id"],
                               company_id=company_id)
        conflicts.append(cid)
    return conflicts


def _check_capacity_exceeded(conn, master_id, company_id):
    """HIGH: Section enrollment exceeds assigned room capacity."""
    conflicts = []
    rows = conn.execute(
        """SELECT sm.id as meeting_id, sm.room_id, sm.section_id,
                  s.current_enrollment, s.max_enrollment,
                  r.capacity, r.room_number, r.building
           FROM educlaw_section_meeting sm
           JOIN educlaw_section s ON s.id = sm.section_id
           JOIN educlaw_room r ON r.id = sm.room_id
           WHERE sm.master_schedule_id = ? AND sm.is_active = 1
             AND sm.room_id IS NOT NULL
             AND s.current_enrollment > r.capacity""",
        (master_id,)
    ).fetchall()
    for r in rows:
        rd = dict(r)
        desc = (f"Section enrollment ({rd['current_enrollment']}) exceeds room capacity "
                f"({rd['capacity']}) in {rd['building']} {rd['room_number']}")
        cid = _insert_conflict(conn, master_id, "capacity_exceeded", desc,
                               meeting_a=rd["meeting_id"], room_id=rd["room_id"],
                               company_id=company_id)
        conflicts.append(cid)
    return conflicts


def _check_room_type_mismatch(conn, master_id, company_id):
    """MEDIUM: Lab course placed in non-lab room."""
    conflicts = []
    rows = conn.execute(
        """SELECT sm.id as meeting_id, sm.room_id,
                  c.course_type, r.room_type,
                  r.room_number, r.building, c.name as course_name
           FROM educlaw_section_meeting sm
           JOIN educlaw_section s ON s.id = sm.section_id
           JOIN educlaw_course c ON c.id = s.course_id
           JOIN educlaw_room r ON r.id = sm.room_id
           WHERE sm.master_schedule_id = ? AND sm.is_active = 1
             AND sm.room_id IS NOT NULL
             AND c.course_type = 'lab' AND r.room_type != 'lab'""",
        (master_id,)
    ).fetchall()
    for r in rows:
        rd = dict(r)
        desc = (f"Lab course '{rd['course_name']}' assigned to {rd['room_type']} room "
                f"{rd['building']} {rd['room_number']} (requires lab room)")
        cid = _insert_conflict(conn, master_id, "room_type_mismatch", desc,
                               meeting_a=rd["meeting_id"], room_id=rd["room_id"],
                               company_id=company_id)
        conflicts.append(cid)
    return conflicts


def _check_credential_mismatch(conn, master_id, company_id):
    """MEDIUM: Instructor has no credentials/specializations listed."""
    conflicts = []
    rows = conn.execute(
        """SELECT sm.id as meeting_id, sm.instructor_id,
                  i.credentials, i.specializations,
                  c.name as course_name, c.course_code
           FROM educlaw_section_meeting sm
           JOIN educlaw_section s ON s.id = sm.section_id
           JOIN educlaw_course c ON c.id = s.course_id
           JOIN educlaw_instructor i ON i.id = sm.instructor_id
           WHERE sm.master_schedule_id = ? AND sm.is_active = 1
             AND sm.instructor_id IS NOT NULL""",
        (master_id,)
    ).fetchall()
    for r in rows:
        rd = dict(r)
        try:
            creds = json.loads(rd["credentials"]) if rd["credentials"] else []
            specs = json.loads(rd["specializations"]) if rd["specializations"] else []
        except (json.JSONDecodeError, TypeError):
            creds, specs = [], []
        if not creds and not specs:
            desc = (f"Instructor {rd['instructor_id'][:8]}… teaching '{rd['course_name']}' "
                    "has no credentials or specializations on file")
            cid = _insert_conflict(conn, master_id, "credential_mismatch", desc,
                                   meeting_a=rd["meeting_id"],
                                   instructor_id=rd["instructor_id"],
                                   company_id=company_id)
            conflicts.append(cid)
    return conflicts


def _check_singleton_overlap(conn, master_id, company_id):
    """HIGH: Two singleton courses (1 section each) placed at the same slot."""
    conflicts = []
    # Find courses with exactly 1 section in this master schedule
    singleton_sections = conn.execute(
        """SELECT sm.section_id, s.course_id
           FROM educlaw_section_meeting sm
           JOIN educlaw_section s ON s.id = sm.section_id
           WHERE sm.master_schedule_id = ? AND sm.is_active = 1
           GROUP BY s.course_id
           HAVING COUNT(DISTINCT sm.section_id) = 1""",
        (master_id,)
    ).fetchall()

    singleton_section_ids = set(r["section_id"] for r in singleton_sections)

    if len(singleton_section_ids) < 2:
        return conflicts

    # Find pairs of singleton sections at the same slot
    rows = conn.execute(
        """SELECT sm1.id as meeting_a, sm2.id as meeting_b,
                  sm1.section_id as section_a, sm2.section_id as section_b,
                  sm1.day_type_id, sm1.bell_period_id,
                  dt.code as day_code, bp.period_name
           FROM educlaw_section_meeting sm1
           JOIN educlaw_section_meeting sm2
             ON sm1.master_schedule_id = sm2.master_schedule_id
             AND sm1.day_type_id = sm2.day_type_id
             AND sm1.bell_period_id = sm2.bell_period_id
             AND sm1.id < sm2.id
           JOIN educlaw_day_type dt ON dt.id = sm1.day_type_id
           JOIN educlaw_bell_period bp ON bp.id = sm1.bell_period_id
           WHERE sm1.master_schedule_id = ? AND sm1.is_active = 1 AND sm2.is_active = 1""",
        (master_id,)
    ).fetchall()

    for r in rows:
        rd = dict(r)
        if rd["section_a"] in singleton_section_ids and rd["section_b"] in singleton_section_ids:
            desc = (f"Two singleton sections placed at same slot {rd['day_code']} / "
                    f"{rd['period_name']} — students needing both cannot be scheduled")
            cid = _insert_conflict(conn, master_id, "singleton_overlap", desc,
                                   meeting_a=rd["meeting_a"], meeting_b=rd["meeting_b"],
                                   company_id=company_id)
            conflicts.append(cid)
    return conflicts


def _check_contact_hours_deficit(conn, master_id, company_id):
    """MEDIUM: Section has fewer meetings than credit hours × 50 min requires."""
    conflicts = []
    rows = conn.execute(
        """SELECT s.id as section_id, s.course_id, c.name as course_name,
                  c.credit_hours, COUNT(sm.id) as meeting_count,
                  SUM(bp.duration_minutes) as total_minutes
           FROM educlaw_section s
           JOIN educlaw_course c ON c.id = s.course_id
           LEFT JOIN educlaw_section_meeting sm ON sm.section_id = s.id
             AND sm.master_schedule_id = ? AND sm.is_active = 1
           LEFT JOIN educlaw_bell_period bp ON bp.id = sm.bell_period_id
             AND bp.period_type = 'class'
           WHERE s.academic_term_id = (
               SELECT academic_term_id FROM educlaw_master_schedule WHERE id = ?
           )
           GROUP BY s.id
           HAVING meeting_count = 0 OR total_minutes < CAST(c.credit_hours AS REAL) * 50""",
        (master_id, master_id)
    ).fetchall()

    for r in rows:
        rd = dict(r)
        try:
            required_minutes = float(rd["credit_hours"]) * 50
        except (TypeError, ValueError):
            required_minutes = 0
        actual_minutes = rd["total_minutes"] or 0
        if actual_minutes < required_minutes:
            desc = (f"Section of '{rd['course_name']}' has {actual_minutes} contact minutes "
                    f"(requires {int(required_minutes)} for {rd['credit_hours']} credit hours)")
            cid = _insert_conflict(conn, master_id, "contact_hours_deficit", desc,
                                   company_id=company_id)
            conflicts.append(cid)
    return conflicts


def _check_room_shortage(conn, master_id, company_id):
    """HIGH: More sections scheduled in a slot than available rooms."""
    conflicts = []
    rows = conn.execute(
        """SELECT sm.day_type_id, sm.bell_period_id,
                  COUNT(*) as meetings_needing_rooms,
                  SUM(CASE WHEN sm.room_id IS NOT NULL THEN 1 ELSE 0 END) as assigned,
                  dt.code as day_code, bp.period_name
           FROM educlaw_section_meeting sm
           JOIN educlaw_day_type dt ON dt.id = sm.day_type_id
           JOIN educlaw_bell_period bp ON bp.id = sm.bell_period_id
           WHERE sm.master_schedule_id = ? AND sm.is_active = 1
           GROUP BY sm.day_type_id, sm.bell_period_id
           HAVING assigned < meetings_needing_rooms""",
        (master_id,)
    ).fetchall()

    for r in rows:
        rd = dict(r)
        gap = rd["meetings_needing_rooms"] - rd["assigned"]
        desc = (f"{gap} section(s) on {rd['day_code']} / {rd['period_name']} "
                f"have no room assigned ({rd['assigned']}/{rd['meetings_needing_rooms']} assigned)")
        cid = _insert_conflict(conn, master_id, "room_shortage", desc,
                               company_id=company_id)
        conflicts.append(cid)
    return conflicts


# ─────────────────────────────────────────────────────────────────────────────
# RUN CONFLICT CHECK
# ─────────────────────────────────────────────────────────────────────────────

def run_conflict_check(conn, args):
    """Run all 11 conflict checks for a master schedule. Supersedes old open conflicts."""
    master_id = getattr(args, "master_schedule_id", None)
    if not master_id:
        err("--master-schedule-id is required")

    master_row = conn.execute(
        "SELECT * FROM educlaw_master_schedule WHERE id = ?", (master_id,)
    ).fetchone()
    if not master_row:
        err(f"Master schedule {master_id} not found")

    company_id = master_row["company_id"]

    # Supersede existing open conflicts
    conn.execute(
        """UPDATE educlaw_schedule_conflict
           SET conflict_status = 'superseded', updated_at = datetime('now')
           WHERE master_schedule_id = ? AND conflict_status = 'open'""",
        (master_id,)
    )

    all_new = []
    results = {}

    checks = [
        ("instructor_double_booking",    _check_instructor_double_booking),
        ("room_double_booking",          _check_room_double_booking),
        ("student_conflict",             _check_student_conflicts),
        ("instructor_overload",          _check_instructor_overload),
        ("instructor_contract_violation", _check_instructor_contract_violation),
        ("capacity_exceeded",            _check_capacity_exceeded),
        ("room_type_mismatch",           _check_room_type_mismatch),
        ("credential_mismatch",          _check_credential_mismatch),
        ("singleton_overlap",            _check_singleton_overlap),
        ("contact_hours_deficit",        _check_contact_hours_deficit),
        ("room_shortage",                _check_room_shortage),
    ]

    for check_name, check_fn in checks:
        try:
            found = check_fn(conn, master_id, company_id)
            results[check_name] = len(found)
            all_new.extend(found)
        except Exception as e:
            results[check_name] = f"error: {e}"

    open_count = _update_open_conflicts(conn, master_id)

    critical_open = conn.execute(
        """SELECT COUNT(*) FROM educlaw_schedule_conflict
           WHERE master_schedule_id = ? AND conflict_status = 'open'
             AND severity = 'critical'""",
        (master_id,)
    ).fetchone()[0]

    audit(conn, SKILL, "generate-conflict-check", "educlaw_master_schedule", master_id,
          new_values={"new_conflicts": len(all_new), "open_conflicts": open_count})
    conn.commit()

    ok({
        "master_schedule_id": master_id,
        "new_conflicts_found": len(all_new),
        "open_conflicts": open_count,
        "critical_open": critical_open,
        "can_publish": critical_open == 0,
        "results_by_type": results,
    })


# ─────────────────────────────────────────────────────────────────────────────
# CONFLICT MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

def list_conflicts(conn, args):
    """List schedule conflicts with optional filters."""
    master_id = getattr(args, "master_schedule_id", None)
    if not master_id:
        err("--master-schedule-id is required")

    query = "SELECT * FROM educlaw_schedule_conflict WHERE master_schedule_id = ?"
    params = [master_id]

    if getattr(args, "conflict_type", None):
        query += " AND conflict_type = ?"; params.append(args.conflict_type)
    if getattr(args, "severity", None):
        query += " AND severity = ?"; params.append(args.severity)
    if getattr(args, "conflict_status", None):
        query += " AND conflict_status = ?"; params.append(args.conflict_status)

    query += " ORDER BY severity, conflict_type"
    limit = int(getattr(args, "limit", None) or 100)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"conflicts": [dict(r) for r in rows], "count": len(rows)})


def get_conflict(conn, args):
    """Get a single conflict record by ID."""
    conflict_id = getattr(args, "conflict_id", None)
    if not conflict_id:
        err("--conflict-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_schedule_conflict WHERE id = ?", (conflict_id,)
    ).fetchone()
    if not row:
        err(f"Conflict {conflict_id} not found")

    data = dict(row)

    # Enrich with meeting details
    if data.get("section_meeting_id_a"):
        m = conn.execute(
            """SELECT sm.*, s.section_number, c.name as course_name
               FROM educlaw_section_meeting sm
               JOIN educlaw_section s ON s.id = sm.section_id
               JOIN educlaw_course c ON c.id = s.course_id
               WHERE sm.id = ?""",
            (data["section_meeting_id_a"],)
        ).fetchone()
        if m:
            data["meeting_a_details"] = dict(m)

    if data.get("section_meeting_id_b"):
        m = conn.execute(
            """SELECT sm.*, s.section_number, c.name as course_name
               FROM educlaw_section_meeting sm
               JOIN educlaw_section s ON s.id = sm.section_id
               JOIN educlaw_course c ON c.id = s.course_id
               WHERE sm.id = ?""",
            (data["section_meeting_id_b"],)
        ).fetchone()
        if m:
            data["meeting_b_details"] = dict(m)

    ok(data)


def resolve_conflict(conn, args):
    """Mark a conflict as resolved with notes."""
    conflict_id = getattr(args, "conflict_id", None)
    resolution_notes = getattr(args, "resolution_notes", None)
    resolved_by = getattr(args, "resolved_by", None) or getattr(args, "user_id", None) or ""

    if not conflict_id:
        err("--conflict-id is required")
    if not resolution_notes:
        err("--resolution-notes is required")

    row = conn.execute(
        "SELECT * FROM educlaw_schedule_conflict WHERE id = ?", (conflict_id,)
    ).fetchone()
    if not row:
        err(f"Conflict {conflict_id} not found")

    conflict = dict(row)
    if conflict["conflict_status"] in ("resolved", "accepted", "superseded"):
        err(f"Conflict is already {conflict['conflict_status']}")

    now = _now_iso()
    conn.execute(
        """UPDATE educlaw_schedule_conflict
           SET conflict_status = 'resolved', resolution_notes = ?,
               resolved_by = ?, resolved_at = ?, updated_at = datetime('now')
           WHERE id = ?""",
        (resolution_notes, resolved_by, now, conflict_id)
    )

    _update_open_conflicts(conn, conflict["master_schedule_id"])

    audit(conn, SKILL, "complete-conflict", "educlaw_schedule_conflict", conflict_id,
          new_values={"conflict_status": "resolved", "resolved_by": resolved_by})
    conn.commit()
    ok({"id": conflict_id, "conflict_status": "resolved",
        "resolved_by": resolved_by, "resolved_at": now})


def accept_conflict(conn, args):
    """Accept/acknowledge a conflict as a known exception (won't fix)."""
    conflict_id = getattr(args, "conflict_id", None)
    resolution_notes = getattr(args, "resolution_notes", None) or ""
    resolved_by = getattr(args, "resolved_by", None) or getattr(args, "user_id", None) or ""

    if not conflict_id:
        err("--conflict-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_schedule_conflict WHERE id = ?", (conflict_id,)
    ).fetchone()
    if not row:
        err(f"Conflict {conflict_id} not found")

    conflict = dict(row)
    if conflict["severity"] == "critical":
        err("CRITICAL conflicts cannot be accepted — they must be resolved before publishing. "
            "Use complete-conflict instead.")
    if conflict["conflict_status"] in ("resolved", "accepted", "superseded"):
        err(f"Conflict is already {conflict['conflict_status']}")

    now = _now_iso()
    conn.execute(
        """UPDATE educlaw_schedule_conflict
           SET conflict_status = 'accepted', resolution_notes = ?,
               resolved_by = ?, resolved_at = ?, updated_at = datetime('now')
           WHERE id = ?""",
        (resolution_notes or "Accepted as known exception", resolved_by, now, conflict_id)
    )

    _update_open_conflicts(conn, conflict["master_schedule_id"])

    audit(conn, SKILL, "accept-conflict", "educlaw_schedule_conflict", conflict_id,
          new_values={"conflict_status": "accepted", "resolved_by": resolved_by})
    conn.commit()
    ok({"id": conflict_id, "conflict_status": "accepted",
        "resolved_by": resolved_by, "resolved_at": now})


def get_conflict_summary(conn, args):
    """Get conflict summary counts by type and severity for a master schedule."""
    master_id = getattr(args, "master_schedule_id", None)
    if not master_id:
        err("--master-schedule-id is required")

    if not conn.execute(
        "SELECT id FROM educlaw_master_schedule WHERE id = ?", (master_id,)
    ).fetchone():
        err(f"Master schedule {master_id} not found")

    by_severity = conn.execute(
        """SELECT severity,
                  SUM(CASE WHEN conflict_status = 'open' THEN 1 ELSE 0 END) as open,
                  SUM(CASE WHEN conflict_status = 'resolving' THEN 1 ELSE 0 END) as resolving,
                  SUM(CASE WHEN conflict_status = 'resolved' THEN 1 ELSE 0 END) as resolved,
                  SUM(CASE WHEN conflict_status = 'accepted' THEN 1 ELSE 0 END) as accepted,
                  COUNT(*) as total
           FROM educlaw_schedule_conflict
           WHERE master_schedule_id = ? AND conflict_status != 'superseded'
           GROUP BY severity
           ORDER BY CASE severity
               WHEN 'critical' THEN 1 WHEN 'high' THEN 2
               WHEN 'medium' THEN 3 ELSE 4 END""",
        (master_id,)
    ).fetchall()

    by_type = conn.execute(
        """SELECT conflict_type,
                  SUM(CASE WHEN conflict_status = 'open' THEN 1 ELSE 0 END) as open,
                  COUNT(*) as total
           FROM educlaw_schedule_conflict
           WHERE master_schedule_id = ? AND conflict_status != 'superseded'
           GROUP BY conflict_type
           ORDER BY open DESC""",
        (master_id,)
    ).fetchall()

    totals = conn.execute(
        """SELECT
               SUM(CASE WHEN conflict_status = 'open' THEN 1 ELSE 0 END) as total_open,
               SUM(CASE WHEN conflict_status IN ('resolved','accepted') THEN 1 ELSE 0 END) as total_closed,
               SUM(CASE WHEN severity = 'critical' AND conflict_status = 'open' THEN 1 ELSE 0 END) as critical_open
           FROM educlaw_schedule_conflict
           WHERE master_schedule_id = ? AND conflict_status != 'superseded'""",
        (master_id,)
    ).fetchone()

    td = dict(totals)
    ok({
        "master_schedule_id": master_id,
        "total_open": td["total_open"] or 0,
        "total_closed": td["total_closed"] or 0,
        "critical_open": td["critical_open"] or 0,
        "can_publish": (td["critical_open"] or 0) == 0,
        "by_severity": [dict(r) for r in by_severity],
        "by_type": [dict(r) for r in by_type],
    })


def get_singleton_conflict_map(conn, args):
    """Map singleton courses against each other to identify scheduling conflicts."""
    master_id = getattr(args, "master_schedule_id", None)
    if not master_id:
        err("--master-schedule-id is required")

    if not conn.execute(
        "SELECT id FROM educlaw_master_schedule WHERE id = ?", (master_id,)
    ).fetchone():
        err(f"Master schedule {master_id} not found")

    # Find singleton courses (only one section placed in master schedule)
    singletons = conn.execute(
        """SELECT s.course_id, c.course_code, c.name as course_name,
                  sm.id as meeting_id, sm.day_type_id, sm.bell_period_id,
                  dt.code as day_code, bp.period_name,
                  bp.start_time, bp.end_time
           FROM educlaw_section_meeting sm
           JOIN educlaw_section s ON s.id = sm.section_id
           JOIN educlaw_course c ON c.id = s.course_id
           JOIN educlaw_day_type dt ON dt.id = sm.day_type_id
           JOIN educlaw_bell_period bp ON bp.id = sm.bell_period_id
           WHERE sm.master_schedule_id = ? AND sm.is_active = 1
           GROUP BY s.course_id
           HAVING COUNT(DISTINCT sm.section_id) = 1
           ORDER BY dt.sort_order, bp.sort_order""",
        (master_id,)
    ).fetchall()

    singleton_list = [dict(s) for s in singletons]

    # Find pairs placed at the same slot
    slot_map = {}
    for s in singleton_list:
        key = (s["day_type_id"], s["bell_period_id"])
        slot_map.setdefault(key, []).append(s)

    conflicts = []
    for slot, courses in slot_map.items():
        if len(courses) > 1:
            conflicts.append({
                "day_code": courses[0]["day_code"],
                "period_name": courses[0]["period_name"],
                "start_time": courses[0]["start_time"],
                "end_time": courses[0]["end_time"],
                "conflicting_courses": [
                    {"course_id": c["course_id"], "course_code": c["course_code"],
                     "course_name": c["course_name"]} for c in courses
                ],
            })

    ok({
        "master_schedule_id": master_id,
        "singleton_courses": len(singleton_list),
        "singleton_conflicts": len(conflicts),
        "conflict_slots": conflicts,
        "all_singletons": singleton_list,
    })


def get_student_conflict_report(conn, args):
    """List students who have schedule conflicts in a master schedule."""
    master_id = getattr(args, "master_schedule_id", None)
    if not master_id:
        err("--master-schedule-id is required")

    if not conn.execute(
        "SELECT id FROM educlaw_master_schedule WHERE id = ?", (master_id,)
    ).fetchone():
        err(f"Master schedule {master_id} not found")

    # Students with open student_conflict records
    conflict_students = conn.execute(
        """SELECT DISTINCT sc.student_id,
                  s.first_name || ' ' || s.last_name as student_name,
                  COUNT(*) as conflict_count
           FROM educlaw_schedule_conflict sc
           LEFT JOIN educlaw_student s ON s.id = sc.student_id
           WHERE sc.master_schedule_id = ? AND sc.conflict_type = 'student_conflict'
             AND sc.conflict_status = 'open' AND sc.student_id IS NOT NULL
           GROUP BY sc.student_id""",
        (master_id,)
    ).fetchall()

    # Students enrolled in multiple sections that share the same slot
    enrollment_conflicts = conn.execute(
        """SELECT ce.student_id,
                  s2.first_name || ' ' || s2.last_name as student_name,
                  sm.day_type_id, sm.bell_period_id,
                  dt.code as day_code, bp.period_name,
                  GROUP_CONCAT(c.course_code, ', ') as conflicting_courses,
                  COUNT(*) as cnt
           FROM educlaw_section_meeting sm
           JOIN educlaw_course_enrollment ce ON ce.section_id = sm.section_id
           JOIN educlaw_section s ON s.id = sm.section_id
           JOIN educlaw_course c ON c.id = s.course_id
           JOIN educlaw_day_type dt ON dt.id = sm.day_type_id
           JOIN educlaw_bell_period bp ON bp.id = sm.bell_period_id
           LEFT JOIN educlaw_student s2 ON s2.id = ce.student_id
           WHERE sm.master_schedule_id = ? AND sm.is_active = 1
             AND ce.enrollment_status = 'enrolled'
           GROUP BY ce.student_id, sm.day_type_id, sm.bell_period_id
           HAVING cnt > 1
           ORDER BY cnt DESC""",
        (master_id,)
    ).fetchall()

    ok({
        "master_schedule_id": master_id,
        "students_with_registered_conflicts": len(conflict_students),
        "conflict_student_list": [dict(r) for r in conflict_students],
        "enrollment_conflict_details": [dict(r) for r in enrollment_conflicts],
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

ACTIONS = {
    "generate-conflict-check":    run_conflict_check,
    "list-conflicts":             list_conflicts,
    "get-conflict":               get_conflict,
    "complete-conflict":          resolve_conflict,
    "accept-conflict":            accept_conflict,
    "get-conflict-summary":       get_conflict_summary,
    "get-singleton-conflict-map": get_singleton_conflict_map,
    "get-student-conflict-report": get_student_conflict_report,
}
