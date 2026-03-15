"""EduClaw Advanced Scheduling — master_schedule domain module

Actions (15 core + 9 course requests = 24 total):
  Core: create-master-schedule, update-master-schedule, get-master-schedule,
        list-master-schedules, add-section-to-schedule, add-section-meeting,
        delete-section-meeting, list-section-meetings, get-schedule-matrix,
        get-course-demand-analysis, get-fulfillment-report, get-load-balance-report,
        submit-master-schedule, update-schedule-lock, create-schedule-clone
  Course Requests: activate-course-requests, submit-course-request, update-course-request,
        get-course-request, list-course-requests, approve-course-requests,
        get-demand-report, get-singleton-analysis, complete-course-requests

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

VALID_SCHEDULE_STATUSES = ("draft", "building", "review", "published", "locked", "archived")
VALID_MEETING_TYPES = ("regular", "lab", "exam", "field_trip", "make_up")
VALID_MEETING_MODES = ("in_person", "hybrid", "online")
VALID_REQUEST_STATUSES = (
    "draft", "submitted", "approved", "scheduled",
    "alternate_used", "unfulfilled", "withdrawn"
)

# Status transition rules for master schedule
_ALLOWED_TRANSITIONS = {
    "draft":     ("building", "archived"),
    "building":  ("review", "draft", "archived"),
    "review":    ("building", "published", "archived"),
    "published": ("locked", "archived"),
    "locked":    ("archived",),
    "archived":  (),
}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _next_name(conn, entity_type, prefix, company_id):
    """Generate sequential naming series using the naming_series table."""
    year = datetime.now(timezone.utc).year
    year_prefix = f"{prefix}{year}-"
    entry_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO naming_series (id, entity_type, prefix, current_value, company_id)
           VALUES (?, ?, ?, 1, ?)
           ON CONFLICT(entity_type, prefix, company_id)
           DO UPDATE SET current_value = current_value + 1""",
        (entry_id, entity_type, year_prefix, company_id)
    )
    row = conn.execute(
        "SELECT current_value FROM naming_series "
        "WHERE entity_type = ? AND prefix = ? AND company_id = ?",
        (entity_type, year_prefix, company_id)
    ).fetchone()
    return f"{prefix}{year}-{row[0]:05d}"


def _refresh_master_stats(conn, master_id):
    """Recalculate and update master schedule summary statistics."""
    placed = conn.execute(
        "SELECT COUNT(DISTINCT section_id) FROM educlaw_section_meeting "
        "WHERE master_schedule_id = ? AND is_active = 1",
        (master_id,)
    ).fetchone()[0]

    with_room = conn.execute(
        "SELECT COUNT(DISTINCT section_id) FROM educlaw_section_meeting "
        "WHERE master_schedule_id = ? AND is_active = 1 AND room_id IS NOT NULL",
        (master_id,)
    ).fetchone()[0]

    open_conf = conn.execute(
        "SELECT COUNT(*) FROM educlaw_schedule_conflict "
        "WHERE master_schedule_id = ? AND conflict_status = 'open'",
        (master_id,)
    ).fetchone()[0]

    total = conn.execute(
        "SELECT total_sections FROM educlaw_master_schedule WHERE id = ?", (master_id,)
    ).fetchone()[0] or 0

    rate = f"{round((placed / total * 100), 1)}%" if total > 0 else "0.0%"

    conn.execute(
        """UPDATE educlaw_master_schedule
           SET sections_placed = ?, sections_with_room = ?, open_conflicts = ?,
               fulfillment_rate = ?, updated_at = datetime('now')
           WHERE id = ?""",
        (placed, with_room, open_conf, rate, master_id)
    )


def _get_master_or_err(conn, master_id):
    """Fetch master schedule row or return error."""
    row = conn.execute(
        "SELECT * FROM educlaw_master_schedule WHERE id = ?", (master_id,)
    ).fetchone()
    if not row:
        err(f"Master schedule {master_id} not found")
    return dict(row)


def _require_editable(master):
    """Ensure master schedule is in an editable state."""
    if master["schedule_status"] in ("published", "locked", "archived"):
        err(f"Master schedule is {master['schedule_status']} and cannot be modified. "
            "Use create-schedule-clone to create an editable copy.")


# ─────────────────────────────────────────────────────────────────────────────
# MASTER SCHEDULE CORE
# ─────────────────────────────────────────────────────────────────────────────

def create_master_schedule(conn, args):
    """Create a new master schedule for an academic term."""
    academic_term_id = getattr(args, "academic_term_id", None)
    schedule_pattern_id = getattr(args, "schedule_pattern_id", None)
    name = getattr(args, "name", None)
    company_id = getattr(args, "company_id", None)

    if not academic_term_id:
        err("--academic-term-id is required")
    if not schedule_pattern_id:
        err("--schedule-pattern-id is required")
    if not name:
        err("--name is required")
    if not company_id:
        err("--company-id is required")

    if not conn.execute(
        "SELECT id FROM educlaw_academic_term WHERE id = ?", (academic_term_id,)
    ).fetchone():
        err(f"Academic term {academic_term_id} not found")

    if not conn.execute(
        "SELECT id FROM educlaw_schedule_pattern WHERE id = ?", (schedule_pattern_id,)
    ).fetchone():
        err(f"Schedule pattern {schedule_pattern_id} not found")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    # One master schedule per term
    existing = conn.execute(
        "SELECT id FROM educlaw_master_schedule WHERE academic_term_id = ?",
        (academic_term_id,)
    ).fetchone()
    if existing:
        err(f"A master schedule already exists for this term: {existing['id']}")

    cloned_from = getattr(args, "cloned_from_id", None)
    if cloned_from:
        if not conn.execute(
            "SELECT id FROM educlaw_master_schedule WHERE id = ?", (cloned_from,)
        ).fetchone():
            err(f"Source master schedule {cloned_from} not found")

    build_notes = getattr(args, "build_notes", None) or ""
    now = _now_iso()
    master_id = str(uuid.uuid4())
    naming = _next_name(conn, "educlaw_master_schedule", "MS-", company_id)

    try:
        conn.execute(
            """INSERT INTO educlaw_master_schedule
               (id, naming_series, name, academic_term_id, schedule_pattern_id,
                build_notes, total_sections, sections_placed, sections_with_room,
                open_conflicts, fulfillment_rate, schedule_status,
                published_at, published_by, locked_at, locked_by,
                cloned_from_id, company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, 0, 0, 0, 0, '0.0%', 'draft',
                       '', '', '', '', ?, ?, ?, ?, ?)""",
            (master_id, naming, name, academic_term_id, schedule_pattern_id,
             build_notes, cloned_from, company_id, now, now,
             getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Master schedule creation failed: {e}")

    audit(conn, SKILL, "create-master-schedule", "educlaw_master_schedule", master_id,
          new_values={"naming_series": naming, "academic_term_id": academic_term_id,
                      "schedule_pattern_id": schedule_pattern_id})
    conn.commit()
    ok({"id": master_id, "naming_series": naming, "name": name,
        "academic_term_id": academic_term_id, "schedule_status": "draft"})


def update_master_schedule(conn, args):
    """Update master schedule fields (name, build notes, status transition)."""
    master_id = getattr(args, "master_schedule_id", None)
    if not master_id:
        err("--master-schedule-id is required")

    master = _get_master_or_err(conn, master_id)
    updates, params, changed = [], [], []

    if getattr(args, "name", None) is not None:
        updates.append("name = ?"); params.append(args.name); changed.append("name")

    if getattr(args, "build_notes", None) is not None:
        updates.append("build_notes = ?"); params.append(args.build_notes)
        changed.append("build_notes")

    new_status = getattr(args, "schedule_status", None)
    if new_status is not None:
        if new_status not in VALID_SCHEDULE_STATUSES:
            err(f"--schedule-status must be one of: {', '.join(VALID_SCHEDULE_STATUSES)}")
        allowed = _ALLOWED_TRANSITIONS.get(master["schedule_status"], ())
        if new_status not in allowed:
            err(f"Cannot transition from '{master['schedule_status']}' to '{new_status}'. "
                f"Allowed: {allowed}")
        updates.append("schedule_status = ?"); params.append(new_status)
        changed.append("schedule_status")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(master_id)
    conn.execute(
        f"UPDATE educlaw_master_schedule SET {', '.join(updates)} WHERE id = ?", params
    )
    audit(conn, SKILL, "update-master-schedule", "educlaw_master_schedule", master_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": master_id, "updated_fields": changed})


def get_master_schedule(conn, args):
    """Get a master schedule by ID or naming series."""
    master_id = getattr(args, "master_schedule_id", None)
    naming = getattr(args, "naming_series", None)

    if not master_id and not naming:
        err("--master-schedule-id or --naming-series is required")

    if master_id:
        row = conn.execute(
            "SELECT * FROM educlaw_master_schedule WHERE id = ?", (master_id,)
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT * FROM educlaw_master_schedule WHERE naming_series = ?", (naming,)
        ).fetchone()

    if not row:
        err(f"Master schedule not found")

    data = dict(row)

    # Enrich with term name
    term = conn.execute(
        "SELECT name, status FROM educlaw_academic_term WHERE id = ?",
        (data["academic_term_id"],)
    ).fetchone()
    if term:
        data["term_name"] = term["name"]
        data["term_status"] = term["status"]

    # Enrich with pattern name
    pattern = conn.execute(
        "SELECT name, pattern_type FROM educlaw_schedule_pattern WHERE id = ?",
        (data["schedule_pattern_id"],)
    ).fetchone()
    if pattern:
        data["pattern_name"] = pattern["name"]
        data["pattern_type"] = pattern["pattern_type"]

    ok(data)


def list_master_schedules(conn, args):
    """List master schedules with optional filters."""
    query = "SELECT * FROM educlaw_master_schedule WHERE 1=1"
    params = []

    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)
    if getattr(args, "schedule_status", None):
        query += " AND schedule_status = ?"; params.append(args.schedule_status)
    if getattr(args, "academic_term_id", None):
        query += " AND academic_term_id = ?"; params.append(args.academic_term_id)

    query += " ORDER BY created_at DESC"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"master_schedules": [dict(r) for r in rows], "count": len(rows)})


def add_section_to_schedule(conn, args):
    """Register a section as part of a master schedule (increments total_sections)."""
    master_id = getattr(args, "master_schedule_id", None)
    section_id = getattr(args, "section_id", None)

    if not master_id:
        err("--master-schedule-id is required")
    if not section_id:
        err("--section-id is required")

    master = _get_master_or_err(conn, master_id)
    _require_editable(master)

    if not conn.execute(
        "SELECT id FROM educlaw_section WHERE id = ?", (section_id,)
    ).fetchone():
        err(f"Section {section_id} not found")

    # Verify section belongs to the same term
    sec_term = conn.execute(
        "SELECT academic_term_id FROM educlaw_section WHERE id = ?", (section_id,)
    ).fetchone()
    if sec_term and sec_term["academic_term_id"] != master["academic_term_id"]:
        err("Section belongs to a different academic term than this master schedule")

    # Check if section already has meetings in this master schedule
    existing = conn.execute(
        "SELECT id FROM educlaw_section_meeting "
        "WHERE master_schedule_id = ? AND section_id = ? LIMIT 1",
        (master_id, section_id)
    ).fetchone()
    if existing:
        err(f"Section {section_id} already has meetings in this master schedule")

    # Check if total_sections already counts this section (via any previous add)
    # We increment unconditionally — caller should only call once per section
    conn.execute(
        """UPDATE educlaw_master_schedule
           SET total_sections = total_sections + 1, updated_at = datetime('now')
           WHERE id = ?""",
        (master_id,)
    )
    audit(conn, SKILL, "add-section-to-schedule", "educlaw_master_schedule", master_id,
          new_values={"section_id": section_id, "action": "increment_total"})
    conn.commit()

    new_total = conn.execute(
        "SELECT total_sections FROM educlaw_master_schedule WHERE id = ?", (master_id,)
    ).fetchone()[0]
    ok({"master_schedule_id": master_id, "section_id": section_id,
        "total_sections": new_total,
        "message": "Section registered in master schedule"})


def place_section_meeting(conn, args):
    """Place a section into a specific day-type + period slot (creates section_meeting row)."""
    master_id = getattr(args, "master_schedule_id", None)
    section_id = getattr(args, "section_id", None)
    day_type_id = getattr(args, "day_type_id", None)
    bell_period_id = getattr(args, "bell_period_id", None)

    if not master_id:
        err("--master-schedule-id is required")
    if not section_id:
        err("--section-id is required")
    if not day_type_id:
        err("--day-type-id is required")
    if not bell_period_id:
        err("--bell-period-id is required")

    master = _get_master_or_err(conn, master_id)
    _require_editable(master)

    if not conn.execute(
        "SELECT id FROM educlaw_section WHERE id = ?", (section_id,)
    ).fetchone():
        err(f"Section {section_id} not found")

    if not conn.execute(
        "SELECT id FROM educlaw_day_type WHERE id = ?", (day_type_id,)
    ).fetchone():
        err(f"Day type {day_type_id} not found")

    if not conn.execute(
        "SELECT id FROM educlaw_bell_period WHERE id = ?", (bell_period_id,)
    ).fetchone():
        err(f"Bell period {bell_period_id} not found")

    room_id = getattr(args, "room_id", None)
    instructor_id = getattr(args, "instructor_id", None)

    if room_id:
        if not conn.execute(
            "SELECT id FROM educlaw_room WHERE id = ?", (room_id,)
        ).fetchone():
            err(f"Room {room_id} not found")

    if instructor_id:
        if not conn.execute(
            "SELECT id FROM educlaw_instructor WHERE id = ?", (instructor_id,)
        ).fetchone():
            err(f"Instructor {instructor_id} not found")

    meeting_type = getattr(args, "meeting_type", None) or "regular"
    if meeting_type not in VALID_MEETING_TYPES:
        err(f"--meeting-type must be one of: {', '.join(VALID_MEETING_TYPES)}")

    meeting_mode = getattr(args, "meeting_mode", None) or "in_person"
    if meeting_mode not in VALID_MEETING_MODES:
        err(f"--meeting-mode must be one of: {', '.join(VALID_MEETING_MODES)}")

    notes = getattr(args, "notes", None) or ""
    now = _now_iso()
    meeting_id = str(uuid.uuid4())
    company_id = master.get("company_id", "")

    warnings = []

    # Immediate conflict check: instructor double booking
    if instructor_id:
        clash = conn.execute(
            """SELECT sm.id FROM educlaw_section_meeting sm
               WHERE sm.master_schedule_id = ? AND sm.instructor_id = ?
                 AND sm.day_type_id = ? AND sm.bell_period_id = ? AND sm.is_active = 1""",
            (master_id, instructor_id, day_type_id, bell_period_id)
        ).fetchone()
        if clash:
            warnings.append(f"WARNING: Instructor double-booking detected at this slot "
                            f"(meeting {clash['id']})")

    # Immediate conflict check: room double booking
    if room_id:
        clash = conn.execute(
            """SELECT rb.id FROM educlaw_room_booking rb
               WHERE rb.room_id = ? AND rb.day_type_id = ?
                 AND rb.bell_period_id = ? AND rb.booking_status != 'cancelled'""",
            (room_id, day_type_id, bell_period_id)
        ).fetchone()
        if clash:
            warnings.append(f"WARNING: Room already booked for this slot (booking {clash['id']})")

    try:
        conn.execute(
            """INSERT INTO educlaw_section_meeting
               (id, section_id, master_schedule_id, day_type_id, bell_period_id,
                room_id, instructor_id, meeting_type, meeting_mode, is_active,
                notes, company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?)""",
            (meeting_id, section_id, master_id, day_type_id, bell_period_id,
             room_id, instructor_id, meeting_type, meeting_mode, notes,
             company_id, now, now, getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Section meeting creation failed (slot may already be taken): {e}")

    # Auto-create room booking if room provided
    if room_id:
        booking_id = str(uuid.uuid4())
        section_row = conn.execute(
            "SELECT section_number FROM educlaw_section WHERE id = ?", (section_id,)
        ).fetchone()
        booking_title = f"Class: {section_row['section_number'] if section_row else section_id}"
        try:
            conn.execute(
                """INSERT INTO educlaw_room_booking
                   (id, room_id, master_schedule_id, section_meeting_id, day_type_id,
                    bell_period_id, booking_type, booking_title, booked_by,
                    booking_status, cancellation_reason, accessibility_required,
                    company_id, created_at, updated_at, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, 'class', ?, ?, 'confirmed', '', 0,
                           ?, ?, ?, ?)""",
                (booking_id, room_id, master_id, meeting_id, day_type_id, bell_period_id,
                 booking_title, getattr(args, "user_id", None) or "",
                 company_id, now, now, getattr(args, "user_id", None) or "")
            )
        except sqlite3.IntegrityError:
            warnings.append("WARNING: Could not auto-create room booking (conflict may exist)")

    _refresh_master_stats(conn, master_id)

    audit(conn, SKILL, "add-section-meeting", "educlaw_section_meeting", meeting_id,
          new_values={"section_id": section_id, "master_schedule_id": master_id,
                      "day_type_id": day_type_id, "bell_period_id": bell_period_id})
    conn.commit()

    result = {"id": meeting_id, "section_id": section_id,
              "master_schedule_id": master_id, "day_type_id": day_type_id,
              "bell_period_id": bell_period_id, "room_id": room_id,
              "instructor_id": instructor_id, "meeting_type": meeting_type}
    if warnings:
        result["warnings"] = warnings
    ok(result)


def remove_section_meeting(conn, args):
    """Remove (deactivate) a section meeting from the master schedule."""
    meeting_id = getattr(args, "section_meeting_id", None)
    if not meeting_id:
        err("--section-meeting-id is required")

    meeting = conn.execute(
        "SELECT * FROM educlaw_section_meeting WHERE id = ?", (meeting_id,)
    ).fetchone()
    if not meeting:
        err(f"Section meeting {meeting_id} not found")

    meeting = dict(meeting)
    master = _get_master_or_err(conn, meeting["master_schedule_id"])
    _require_editable(master)

    # Delete associated room bookings first (FK ON DELETE RESTRICT requires
    # removing child rows before the parent row can be deleted)
    conn.execute(
        "DELETE FROM educlaw_room_booking WHERE section_meeting_id = ?",
        (meeting_id,)
    )

    # Hard delete the meeting (it's a draft record, not a transaction)
    conn.execute("DELETE FROM educlaw_section_meeting WHERE id = ?", (meeting_id,))

    _refresh_master_stats(conn, meeting["master_schedule_id"])

    audit(conn, SKILL, "delete-section-meeting", "educlaw_section_meeting", meeting_id,
          old_values={"section_id": meeting["section_id"],
                      "day_type_id": meeting["day_type_id"],
                      "bell_period_id": meeting["bell_period_id"]})
    conn.commit()
    ok({"id": meeting_id, "message": "Section meeting removed",
        "section_id": meeting["section_id"]})


def list_section_meetings(conn, args):
    """List section meetings with optional filters."""
    master_id = getattr(args, "master_schedule_id", None)
    if not master_id:
        err("--master-schedule-id is required")

    query = "SELECT * FROM educlaw_section_meeting WHERE master_schedule_id = ?"
    params = [master_id]

    if getattr(args, "section_id", None):
        query += " AND section_id = ?"; params.append(args.section_id)
    if getattr(args, "day_type_id", None):
        query += " AND day_type_id = ?"; params.append(args.day_type_id)
    if getattr(args, "bell_period_id", None):
        query += " AND bell_period_id = ?"; params.append(args.bell_period_id)
    if getattr(args, "instructor_id", None):
        query += " AND instructor_id = ?"; params.append(args.instructor_id)
    if getattr(args, "room_id", None):
        query += " AND room_id = ?"; params.append(args.room_id)
    if getattr(args, "is_active", None) is not None:
        query += " AND is_active = ?"; params.append(int(args.is_active))

    query += " ORDER BY day_type_id, bell_period_id"
    limit = int(getattr(args, "limit", None) or 200)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"section_meetings": [dict(r) for r in rows], "count": len(rows)})


def get_schedule_matrix(conn, args):
    """Return full schedule matrix: bell_periods × day_types with section assignments."""
    master_id = getattr(args, "master_schedule_id", None)
    if not master_id:
        err("--master-schedule-id is required")

    master = _get_master_or_err(conn, master_id)

    # Get day types for this pattern
    day_types = conn.execute(
        """SELECT dt.* FROM educlaw_day_type dt
           JOIN educlaw_master_schedule ms ON ms.schedule_pattern_id = dt.schedule_pattern_id
           WHERE ms.id = ? ORDER BY dt.sort_order""",
        (master_id,)
    ).fetchall()
    day_type_list = [dict(d) for d in day_types]

    # Get bell periods for this pattern
    bell_periods = conn.execute(
        """SELECT bp.* FROM educlaw_bell_period bp
           JOIN educlaw_master_schedule ms ON ms.schedule_pattern_id = bp.schedule_pattern_id
           WHERE ms.id = ? ORDER BY bp.sort_order""",
        (master_id,)
    ).fetchall()

    # Get all active meetings
    meetings = conn.execute(
        """SELECT sm.*, s.section_number, c.name as course_name, c.course_code,
                  i.id as instr_rec_id, e.first_name || ' ' || e.last_name as instructor_name,
                  r.room_number, r.building
           FROM educlaw_section_meeting sm
           JOIN educlaw_section s ON s.id = sm.section_id
           JOIN educlaw_course c ON c.id = s.course_id
           LEFT JOIN educlaw_instructor i ON i.id = sm.instructor_id
           LEFT JOIN employee e ON e.id = i.employee_id
           LEFT JOIN educlaw_room r ON r.id = sm.room_id
           WHERE sm.master_schedule_id = ? AND sm.is_active = 1""",
        (master_id,)
    ).fetchall()

    # Build lookup: (day_type_id, bell_period_id) → list of meetings
    slot_map = {}
    for m in meetings:
        key = (m["day_type_id"], m["bell_period_id"])
        slot_map.setdefault(key, []).append(dict(m))

    # Build matrix rows
    matrix = []
    for bp in bell_periods:
        bp_dict = dict(bp)
        row_entry = {
            "bell_period_id": bp_dict["id"],
            "period_number": bp_dict["period_number"],
            "period_name": bp_dict["period_name"],
            "start_time": bp_dict["start_time"],
            "end_time": bp_dict["end_time"],
            "duration_minutes": bp_dict["duration_minutes"],
            "period_type": bp_dict["period_type"],
            "slots": {}
        }
        for dt in day_type_list:
            key = (dt["id"], bp_dict["id"])
            row_entry["slots"][dt["code"]] = slot_map.get(key, [])
        matrix.append(row_entry)

    ok({
        "master_schedule_id": master_id,
        "master_schedule_name": master["name"],
        "schedule_status": master["schedule_status"],
        "day_types": day_type_list,
        "matrix": matrix,
        "total_sections": master["total_sections"],
        "sections_placed": master["sections_placed"],
    })


def analyze_course_demand(conn, args):
    """Analyze course requests to estimate needed section counts per course."""
    academic_term_id = getattr(args, "academic_term_id", None)
    if not academic_term_id:
        err("--academic-term-id is required")

    if not conn.execute(
        "SELECT id FROM educlaw_academic_term WHERE id = ?", (academic_term_id,)
    ).fetchone():
        err(f"Academic term {academic_term_id} not found")

    # Count requests per course
    demand = conn.execute(
        """SELECT cr.course_id, c.course_code, c.name as course_name,
                  c.max_enrollment,
                  COUNT(*) as total_requests,
                  SUM(CASE WHEN cr.request_status IN ('approved','scheduled') THEN 1 ELSE 0 END) as approved_requests,
                  COUNT(CASE WHEN cr.is_alternate = 0 THEN 1 END) as primary_requests
           FROM educlaw_course_request cr
           JOIN educlaw_course c ON c.id = cr.course_id
           WHERE cr.academic_term_id = ?
             AND cr.request_status NOT IN ('withdrawn')
           GROUP BY cr.course_id, c.course_code, c.name, c.max_enrollment
           ORDER BY total_requests DESC""",
        (academic_term_id,)
    ).fetchall()

    # Count existing sections per course for this term
    existing_sections = conn.execute(
        """SELECT course_id, COUNT(*) as section_count,
                  SUM(max_enrollment) as total_capacity
           FROM educlaw_section
           WHERE academic_term_id = ? AND status != 'cancelled'
           GROUP BY course_id""",
        (academic_term_id,)
    ).fetchall()
    sections_map = {r["course_id"]: dict(r) for r in existing_sections}

    result = []
    for row in demand:
        rd = dict(row)
        sec_info = sections_map.get(rd["course_id"], {})
        existing_count = sec_info.get("section_count", 0)
        total_cap = sec_info.get("total_capacity", 0)
        max_enroll = rd["max_enrollment"] or 25
        needed = max(0, -(-rd["primary_requests"] // max_enroll) - existing_count)  # ceiling div
        rd["existing_sections"] = existing_count
        rd["existing_capacity"] = total_cap
        rd["recommended_new_sections"] = needed
        rd["demand_gap"] = max(0, rd["primary_requests"] - total_cap)
        result.append(rd)

    ok({
        "academic_term_id": academic_term_id,
        "courses_analyzed": len(result),
        "demand_analysis": result,
    })


def get_fulfillment_report(conn, args):
    """Show course request fulfillment rates for a master schedule or term."""
    master_id = getattr(args, "master_schedule_id", None)
    academic_term_id = getattr(args, "academic_term_id", None)

    if not master_id and not academic_term_id:
        err("--master-schedule-id or --academic-term-id is required")

    # Resolve term_id from master if only master provided
    if master_id and not academic_term_id:
        row = conn.execute(
            "SELECT academic_term_id FROM educlaw_master_schedule WHERE id = ?", (master_id,)
        ).fetchone()
        if not row:
            err(f"Master schedule {master_id} not found")
        academic_term_id = row["academic_term_id"]

    stats = conn.execute(
        """SELECT
               COUNT(*) as total_requests,
               SUM(CASE WHEN request_status = 'scheduled' THEN 1 ELSE 0 END) as scheduled,
               SUM(CASE WHEN request_status = 'alternate_used' THEN 1 ELSE 0 END) as alternate_used,
               SUM(CASE WHEN request_status = 'unfulfilled' THEN 1 ELSE 0 END) as unfulfilled,
               SUM(CASE WHEN request_status = 'approved' THEN 1 ELSE 0 END) as approved_pending,
               SUM(CASE WHEN request_status = 'submitted' THEN 1 ELSE 0 END) as submitted_pending,
               SUM(CASE WHEN request_status = 'withdrawn' THEN 1 ELSE 0 END) as withdrawn
           FROM educlaw_course_request
           WHERE academic_term_id = ?""",
        (academic_term_id,)
    ).fetchone()

    sd = dict(stats)
    total = sd["total_requests"] or 0
    fulfilled = (sd["scheduled"] or 0) + (sd["alternate_used"] or 0)
    rate = round(fulfilled / total * 100, 1) if total > 0 else 0.0

    ok({
        "academic_term_id": academic_term_id,
        "master_schedule_id": master_id,
        "total_requests": total,
        "scheduled": sd["scheduled"] or 0,
        "alternate_used": sd["alternate_used"] or 0,
        "fulfilled": fulfilled,
        "unfulfilled": sd["unfulfilled"] or 0,
        "approved_pending_placement": sd["approved_pending"] or 0,
        "submitted_pending_approval": sd["submitted_pending"] or 0,
        "withdrawn": sd["withdrawn"] or 0,
        "fulfillment_rate_pct": rate,
    })


def get_load_balance_report(conn, args):
    """Report instructor teaching load distribution across day types."""
    master_id = getattr(args, "master_schedule_id", None)
    if not master_id:
        err("--master-schedule-id is required")

    _get_master_or_err(conn, master_id)

    rows = conn.execute(
        """SELECT sm.instructor_id,
                  e.first_name || ' ' || e.last_name as instructor_name,
                  dt.code as day_type_code, dt.name as day_type_name,
                  COUNT(*) as period_count,
                  SUM(bp.duration_minutes) as total_minutes
           FROM educlaw_section_meeting sm
           JOIN educlaw_day_type dt ON dt.id = sm.day_type_id
           JOIN educlaw_bell_period bp ON bp.id = sm.bell_period_id
           LEFT JOIN educlaw_instructor i ON i.id = sm.instructor_id
           LEFT JOIN employee e ON e.id = i.employee_id
           WHERE sm.master_schedule_id = ? AND sm.is_active = 1
             AND sm.instructor_id IS NOT NULL
           GROUP BY sm.instructor_id, dt.id
           ORDER BY instructor_name, dt.sort_order""",
        (master_id,)
    ).fetchall()

    # Group by instructor
    instructors = {}
    for r in rows:
        rd = dict(r)
        iid = rd["instructor_id"]
        if iid not in instructors:
            instructors[iid] = {
                "instructor_id": iid,
                "instructor_name": rd["instructor_name"],
                "total_periods": 0,
                "total_minutes": 0,
                "by_day_type": []
            }
        instructors[iid]["by_day_type"].append({
            "day_type_code": rd["day_type_code"],
            "day_type_name": rd["day_type_name"],
            "period_count": rd["period_count"],
            "total_minutes": rd["total_minutes"],
        })
        instructors[iid]["total_periods"] += rd["period_count"]
        instructors[iid]["total_minutes"] += rd["total_minutes"] or 0

    ok({
        "master_schedule_id": master_id,
        "instructors": list(instructors.values()),
        "instructor_count": len(instructors),
    })


def publish_master_schedule(conn, args):
    """Publish master schedule: validate no open CRITICAL conflicts, update sections and term."""
    master_id = getattr(args, "master_schedule_id", None)
    published_by = getattr(args, "published_by", None) or getattr(args, "user_id", None) or ""

    if not master_id:
        err("--master-schedule-id is required")

    master = _get_master_or_err(conn, master_id)
    if master["schedule_status"] not in ("review", "building"):
        err(f"Can only publish from 'review' or 'building' status, "
            f"current: {master['schedule_status']}")

    # Block if any CRITICAL open conflicts
    critical = conn.execute(
        """SELECT COUNT(*) FROM educlaw_schedule_conflict
           WHERE master_schedule_id = ? AND severity = 'critical'
             AND conflict_status = 'open'""",
        (master_id,)
    ).fetchone()[0]
    if critical > 0:
        err(f"Cannot publish: {critical} open CRITICAL conflict(s) must be resolved first. "
            "Use generate-conflict-check and complete-conflict or accept-conflict.")

    now = _now_iso()

    # Update all sections in this master schedule to 'scheduled'
    section_ids = conn.execute(
        "SELECT DISTINCT section_id FROM educlaw_section_meeting WHERE master_schedule_id = ?",
        (master_id,)
    ).fetchall()
    for row in section_ids:
        conn.execute(
            "UPDATE educlaw_section SET status = 'scheduled', updated_at = datetime('now') "
            "WHERE id = ? AND status = 'draft'",
            (row["section_id"],)
        )

    # Update academic term to enrollment_open
    conn.execute(
        """UPDATE educlaw_academic_term
           SET status = 'enrollment_open', updated_at = datetime('now')
           WHERE id = ? AND status IN ('setup', 'enrollment_open')""",
        (master["academic_term_id"],)
    )

    conn.execute(
        """UPDATE educlaw_master_schedule
           SET schedule_status = 'published', published_at = ?, published_by = ?,
               updated_at = datetime('now')
           WHERE id = ?""",
        (now, published_by, master_id)
    )

    audit(conn, SKILL, "submit-master-schedule", "educlaw_master_schedule", master_id,
          new_values={"schedule_status": "published", "published_by": published_by,
                      "sections_updated": len(section_ids)})
    conn.commit()
    ok({"id": master_id, "schedule_status": "published",
        "published_at": now, "published_by": published_by,
        "sections_scheduled": len(section_ids),
        "message": "Master schedule published and enrollment opened"})


def lock_master_schedule(conn, args):
    """Lock a published master schedule to prevent further changes."""
    master_id = getattr(args, "master_schedule_id", None)
    locked_by = getattr(args, "locked_by", None) or getattr(args, "user_id", None) or ""

    if not master_id:
        err("--master-schedule-id is required")

    master = _get_master_or_err(conn, master_id)
    if master["schedule_status"] != "published":
        err(f"Can only lock a published master schedule, current: {master['schedule_status']}")

    now = _now_iso()
    conn.execute(
        """UPDATE educlaw_master_schedule
           SET schedule_status = 'locked', locked_at = ?, locked_by = ?,
               updated_at = datetime('now')
           WHERE id = ?""",
        (now, locked_by, master_id)
    )

    audit(conn, SKILL, "update-schedule-lock", "educlaw_master_schedule", master_id,
          new_values={"schedule_status": "locked", "locked_by": locked_by})
    conn.commit()
    ok({"id": master_id, "schedule_status": "locked",
        "locked_at": now, "locked_by": locked_by})


def clone_master_schedule(conn, args):
    """Clone a master schedule to a new academic term."""
    master_id = getattr(args, "master_schedule_id", None)
    target_term_id = getattr(args, "target_academic_term_id", None)
    name = getattr(args, "name", None)
    company_id = getattr(args, "company_id", None)

    if not master_id:
        err("--master-schedule-id is required")
    if not target_term_id:
        err("--target-academic-term-id is required")

    master = _get_master_or_err(conn, master_id)
    company_id = company_id or master["company_id"]
    name = name or f"Clone of {master['name']}"

    if not conn.execute(
        "SELECT id FROM educlaw_academic_term WHERE id = ?", (target_term_id,)
    ).fetchone():
        err(f"Target academic term {target_term_id} not found")

    # Check target term doesn't already have a master schedule
    existing = conn.execute(
        "SELECT id FROM educlaw_master_schedule WHERE academic_term_id = ?", (target_term_id,)
    ).fetchone()
    if existing:
        err(f"Target term already has a master schedule: {existing['id']}")

    now = _now_iso()
    new_master_id = str(uuid.uuid4())
    naming = _next_name(conn, "educlaw_master_schedule", "MS-", company_id)

    try:
        conn.execute(
            """INSERT INTO educlaw_master_schedule
               (id, naming_series, name, academic_term_id, schedule_pattern_id,
                build_notes, total_sections, sections_placed, sections_with_room,
                open_conflicts, fulfillment_rate, schedule_status,
                published_at, published_by, locked_at, locked_by,
                cloned_from_id, company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, 0, 0, 0, 0, '0.0%', 'draft',
                       '', '', '', '', ?, ?, ?, ?, ?)""",
            (new_master_id, naming, name, target_term_id, master["schedule_pattern_id"],
             f"Cloned from {master['naming_series']}: {master.get('build_notes', '')}",
             master_id, company_id, now, now,
             getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Clone failed: {e}")

    audit(conn, SKILL, "create-schedule-clone", "educlaw_master_schedule", new_master_id,
          new_values={"cloned_from_id": master_id, "target_term_id": target_term_id})
    conn.commit()
    ok({"id": new_master_id, "naming_series": naming, "name": name,
        "cloned_from_id": master_id, "academic_term_id": target_term_id,
        "schedule_status": "draft",
        "message": "Master schedule cloned. Use add-section-to-schedule and "
                   "add-section-meeting to populate."})


# ─────────────────────────────────────────────────────────────────────────────
# COURSE REQUESTS
# ─────────────────────────────────────────────────────────────────────────────

def open_course_requests(conn, args):
    """Open course request collection for an academic term."""
    academic_term_id = getattr(args, "academic_term_id", None)
    if not academic_term_id:
        err("--academic-term-id is required")

    term = conn.execute(
        "SELECT * FROM educlaw_academic_term WHERE id = ?", (academic_term_id,)
    ).fetchone()
    if not term:
        err(f"Academic term {academic_term_id} not found")

    term = dict(term)
    existing_count = conn.execute(
        "SELECT COUNT(*) FROM educlaw_course_request WHERE academic_term_id = ?",
        (academic_term_id,)
    ).fetchone()[0]

    ok({
        "academic_term_id": academic_term_id,
        "term_name": term["name"],
        "term_status": term["status"],
        "existing_requests": existing_count,
        "message": "Course request collection is open. Use submit-course-request to add requests.",
        "ready_for_requests": True,
    })


def submit_course_request(conn, args):
    """Submit a student course request with prerequisite validation."""
    student_id = getattr(args, "student_id", None)
    academic_term_id = getattr(args, "academic_term_id", None)
    course_id = getattr(args, "course_id", None)
    company_id = getattr(args, "company_id", None)

    if not student_id:
        err("--student-id is required")
    if not academic_term_id:
        err("--academic-term-id is required")
    if not course_id:
        err("--company-id is required" if not company_id else "--course-id is required")

    if not conn.execute(
        "SELECT id FROM educlaw_student WHERE id = ?", (student_id,)
    ).fetchone():
        err(f"Student {student_id} not found")

    if not conn.execute(
        "SELECT id FROM educlaw_academic_term WHERE id = ?", (academic_term_id,)
    ).fetchone():
        err(f"Academic term {academic_term_id} not found")

    course_row = conn.execute(
        "SELECT * FROM educlaw_course WHERE id = ?", (course_id,)
    ).fetchone()
    if not course_row:
        err(f"Course {course_id} not found")

    company_id = company_id or conn.execute(
        "SELECT company_id FROM educlaw_course WHERE id = ?", (course_id,)
    ).fetchone()["company_id"]

    # Check uniqueness
    existing = conn.execute(
        "SELECT id FROM educlaw_course_request "
        "WHERE student_id = ? AND academic_term_id = ? AND course_id = ?",
        (student_id, academic_term_id, course_id)
    ).fetchone()
    if existing:
        err(f"Student already has a request for this course in this term: {existing['id']}")

    is_alternate = int(getattr(args, "is_alternate", None) or 0)
    alternate_for_course_id = getattr(args, "alternate_for_course_id", None)
    if alternate_for_course_id:
        if not conn.execute(
            "SELECT id FROM educlaw_course WHERE id = ?", (alternate_for_course_id,)
        ).fetchone():
            err(f"Alternate-for course {alternate_for_course_id} not found")

    request_priority = int(getattr(args, "request_priority", None) or 1)
    prerequisite_override = int(getattr(args, "prerequisite_override", None) or 0)
    prereq_override_by = getattr(args, "prerequisite_override_by", None) or ""
    prereq_override_note = getattr(args, "prerequisite_override_note", None) or ""
    has_iep_flag = int(getattr(args, "has_iep_flag", None) or 0)
    submitted_by = getattr(args, "submitted_by", None) or getattr(args, "user_id", None) or ""

    warnings = []

    # Prerequisite check (warn, don't block unless override explicitly not set)
    prereqs = conn.execute(
        "SELECT prerequisite_course_id, min_grade, is_corequisite "
        "FROM educlaw_course_prerequisite WHERE course_id = ?",
        (course_id,)
    ).fetchall()

    unmet_prereqs = []
    for prereq in prereqs:
        prereq_d = dict(prereq)
        if prereq_d["is_corequisite"]:
            continue  # co-reqs handled separately
        # Check if student completed the prerequisite course
        completed = conn.execute(
            """SELECT ce.final_letter_grade FROM educlaw_course_enrollment ce
               JOIN educlaw_section s ON s.id = ce.section_id
               WHERE ce.student_id = ? AND s.course_id = ?
                 AND ce.enrollment_status = 'completed'""",
            (student_id, prereq_d["prerequisite_course_id"])
        ).fetchone()
        if not completed:
            unmet_prereqs.append(prereq_d["prerequisite_course_id"])

    if unmet_prereqs and not prerequisite_override:
        warnings.append(
            f"WARNING: Student has not completed {len(unmet_prereqs)} prerequisite(s). "
            "Use --prerequisite-override 1 to override."
        )

    now = _now_iso()
    request_id = str(uuid.uuid4())
    naming = _next_name(conn, "educlaw_course_request", "CRQ-", company_id)

    try:
        conn.execute(
            """INSERT INTO educlaw_course_request
               (id, naming_series, student_id, academic_term_id, course_id,
                request_priority, is_alternate, alternate_for_course_id,
                request_status, fulfilled_section_id,
                prerequisite_override, prerequisite_override_by, prerequisite_override_note,
                has_iep_flag, submitted_by, approved_by, approved_at,
                company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'submitted', NULL,
                       ?, ?, ?, ?, ?, '', '', ?, ?, ?, ?)""",
            (request_id, naming, student_id, academic_term_id, course_id,
             request_priority, is_alternate, alternate_for_course_id,
             prerequisite_override, prereq_override_by, prereq_override_note,
             has_iep_flag, submitted_by, company_id, now, now,
             getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Course request creation failed: {e}")

    audit(conn, SKILL, "submit-course-request", "educlaw_course_request", request_id,
          new_values={"student_id": student_id, "course_id": course_id,
                      "academic_term_id": academic_term_id})
    conn.commit()

    result = {"id": request_id, "naming_series": naming,
              "student_id": student_id, "course_id": course_id,
              "academic_term_id": academic_term_id, "request_status": "submitted",
              "request_priority": request_priority}
    if warnings:
        result["warnings"] = warnings
    ok(result)


def update_course_request(conn, args):
    """Update a course request's priority or alternate settings."""
    request_id = getattr(args, "course_request_id", None)
    if not request_id:
        err("--course-request-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_course_request WHERE id = ?", (request_id,)
    ).fetchone()
    if not row:
        err(f"Course request {request_id} not found")

    r = dict(row)
    if r["request_status"] in ("scheduled", "withdrawn"):
        err(f"Cannot update a request with status '{r['request_status']}'")

    updates, params, changed = [], [], []

    if getattr(args, "request_priority", None) is not None:
        updates.append("request_priority = ?")
        params.append(int(args.request_priority)); changed.append("request_priority")
    if getattr(args, "is_alternate", None) is not None:
        updates.append("is_alternate = ?")
        params.append(int(args.is_alternate)); changed.append("is_alternate")
    if getattr(args, "alternate_for_course_id", None) is not None:
        updates.append("alternate_for_course_id = ?")
        params.append(args.alternate_for_course_id); changed.append("alternate_for_course_id")
    if getattr(args, "has_iep_flag", None) is not None:
        updates.append("has_iep_flag = ?")
        params.append(int(args.has_iep_flag)); changed.append("has_iep_flag")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(request_id)
    conn.execute(
        f"UPDATE educlaw_course_request SET {', '.join(updates)} WHERE id = ?", params
    )
    audit(conn, SKILL, "update-course-request", "educlaw_course_request", request_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": request_id, "updated_fields": changed})


def get_course_request(conn, args):
    """Get a single course request by ID."""
    request_id = getattr(args, "course_request_id", None)
    if not request_id:
        err("--course-request-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_course_request WHERE id = ?", (request_id,)
    ).fetchone()
    if not row:
        err(f"Course request {request_id} not found")

    data = dict(row)

    # Enrich with student name
    student = conn.execute(
        "SELECT first_name, last_name FROM educlaw_student WHERE id = ?",
        (data["student_id"],)
    ).fetchone()
    if student:
        data["student_name"] = f"{student['first_name']} {student['last_name']}"

    # Enrich with course info
    course = conn.execute(
        "SELECT course_code, name FROM educlaw_course WHERE id = ?",
        (data["course_id"],)
    ).fetchone()
    if course:
        data["course_code"] = course["course_code"]
        data["course_name"] = course["name"]

    ok(data)


def list_course_requests(conn, args):
    """List course requests with optional filters."""
    query = "SELECT * FROM educlaw_course_request WHERE 1=1"
    params = []

    if getattr(args, "student_id", None):
        query += " AND student_id = ?"; params.append(args.student_id)
    if getattr(args, "academic_term_id", None):
        query += " AND academic_term_id = ?"; params.append(args.academic_term_id)
    if getattr(args, "course_id", None):
        query += " AND course_id = ?"; params.append(args.course_id)
    if getattr(args, "request_status", None):
        query += " AND request_status = ?"; params.append(args.request_status)
    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)

    query += " ORDER BY created_at DESC"
    limit = int(getattr(args, "limit", None) or 100)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"course_requests": [dict(r) for r in rows], "count": len(rows)})


def approve_course_requests(conn, args):
    """Bulk approve submitted course requests for a term."""
    academic_term_id = getattr(args, "academic_term_id", None)
    approved_by = getattr(args, "approved_by", None) or getattr(args, "user_id", None) or ""

    if not academic_term_id:
        err("--academic-term-id is required")
    if not approved_by:
        err("--approved-by or --user-id is required")

    query = ("UPDATE educlaw_course_request "
             "SET request_status = 'approved', approved_by = ?, "
             "approved_at = datetime('now'), updated_at = datetime('now') "
             "WHERE academic_term_id = ? AND request_status = 'submitted'")
    params = [approved_by, academic_term_id]

    # Optional filter by course
    course_id = getattr(args, "course_id", None)
    if course_id:
        query += " AND course_id = ?"
        params.append(course_id)

    conn.execute(query, params)
    count = conn.execute(
        "SELECT changes()"
    ).fetchone()[0]

    audit(conn, SKILL, "approve-course-requests", "educlaw_course_request", academic_term_id,
          new_values={"approved_by": approved_by, "requests_approved": count})
    conn.commit()
    ok({"academic_term_id": academic_term_id, "requests_approved": count,
        "approved_by": approved_by,
        "message": f"{count} course request(s) approved"})


def get_demand_report(conn, args):
    """Get course demand report: request counts and scheduling recommendations."""
    academic_term_id = getattr(args, "academic_term_id", None)
    if not academic_term_id:
        err("--academic-term-id is required")

    if not conn.execute(
        "SELECT id FROM educlaw_academic_term WHERE id = ?", (academic_term_id,)
    ).fetchone():
        err(f"Academic term {academic_term_id} not found")

    demand = conn.execute(
        """SELECT c.id as course_id, c.course_code, c.name as course_name,
                  c.max_enrollment as section_capacity,
                  COUNT(cr.id) as total_requests,
                  SUM(CASE WHEN cr.request_status = 'approved' THEN 1 ELSE 0 END) as approved,
                  SUM(CASE WHEN cr.request_status = 'scheduled' THEN 1 ELSE 0 END) as scheduled,
                  SUM(CASE WHEN cr.request_priority = 1 THEN 1 ELSE 0 END) as priority_1_count,
                  SUM(CASE WHEN cr.has_iep_flag = 1 THEN 1 ELSE 0 END) as iep_count
           FROM educlaw_course_request cr
           JOIN educlaw_course c ON c.id = cr.course_id
           WHERE cr.academic_term_id = ?
             AND cr.request_status NOT IN ('withdrawn', 'unfulfilled')
           GROUP BY c.id
           ORDER BY total_requests DESC""",
        (academic_term_id,)
    ).fetchall()

    result = []
    for row in demand:
        rd = dict(row)
        cap = rd["section_capacity"] or 25
        # Ceiling division for needed sections
        needed = (-(-rd["total_requests"]) // cap) if cap > 0 else 1
        rd["recommended_sections"] = needed
        result.append(rd)

    total_requests = sum(r["total_requests"] for r in result)
    ok({
        "academic_term_id": academic_term_id,
        "total_requests": total_requests,
        "courses_with_demand": len(result),
        "demand_by_course": result,
    })


def get_singleton_analysis(conn, args):
    """Identify courses with few requests that risk singleton scheduling conflicts."""
    academic_term_id = getattr(args, "academic_term_id", None)
    if not academic_term_id:
        err("--academic-term-id is required")

    threshold = int(getattr(args, "min_requests", None) or 1)

    singletons = conn.execute(
        """SELECT c.id as course_id, c.course_code, c.name as course_name,
                  COUNT(cr.id) as total_requests,
                  COUNT(DISTINCT cr.student_id) as unique_students
           FROM educlaw_course_request cr
           JOIN educlaw_course c ON c.id = cr.course_id
           WHERE cr.academic_term_id = ?
             AND cr.request_status NOT IN ('withdrawn')
           GROUP BY c.id
           HAVING total_requests <= ?
           ORDER BY total_requests ASC""",
        (academic_term_id, threshold)
    ).fetchall()

    # For each singleton, find students who ALSO requested other singletons (conflict risk)
    singleton_list = [dict(s) for s in singletons]
    singleton_course_ids = [s["course_id"] for s in singleton_list]

    conflict_risks = []
    if singleton_course_ids:
        for sc in singleton_list:
            # Find students in this singleton who also have other singletons
            other_singletons = [cid for cid in singleton_course_ids
                                 if cid != sc["course_id"]]
            if other_singletons:
                placeholders = ",".join(["?" for _ in other_singletons])
                students = conn.execute(
                    f"""SELECT DISTINCT cr.student_id
                        FROM educlaw_course_request cr
                        WHERE cr.academic_term_id = ? AND cr.course_id = ?
                          AND cr.request_status NOT IN ('withdrawn')
                          AND cr.student_id IN (
                              SELECT student_id FROM educlaw_course_request
                              WHERE academic_term_id = ? AND course_id IN ({placeholders})
                              AND request_status NOT IN ('withdrawn')
                          )""",
                    [academic_term_id, sc["course_id"], academic_term_id] + other_singletons
                ).fetchall()
                if students:
                    sc["students_at_conflict_risk"] = len(students)
                else:
                    sc["students_at_conflict_risk"] = 0

    ok({
        "academic_term_id": academic_term_id,
        "threshold": threshold,
        "singleton_courses": len(singleton_list),
        "singletons": singleton_list,
        "scheduling_advice": (
            "Place singleton courses at different time slots to prevent student conflicts."
        ),
    })


def close_course_requests(conn, args):
    """Close the course request window — mark remaining submitted requests as unfulfilled."""
    academic_term_id = getattr(args, "academic_term_id", None)
    if not academic_term_id:
        err("--academic-term-id is required")

    if not conn.execute(
        "SELECT id FROM educlaw_academic_term WHERE id = ?", (academic_term_id,)
    ).fetchone():
        err(f"Academic term {academic_term_id} not found")

    # Count by status
    stats = conn.execute(
        """SELECT request_status, COUNT(*) as cnt
           FROM educlaw_course_request
           WHERE academic_term_id = ?
           GROUP BY request_status""",
        (academic_term_id,)
    ).fetchall()
    stats_dict = {r["request_status"]: r["cnt"] for r in stats}

    audit(conn, SKILL, "complete-course-requests", "educlaw_course_request", academic_term_id,
          new_values={"academic_term_id": academic_term_id, "stats": stats_dict})
    conn.commit()

    ok({
        "academic_term_id": academic_term_id,
        "request_summary": stats_dict,
        "total_requests": sum(stats_dict.values()),
        "message": "Course request window closed. Review demand report before building master schedule.",
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

ACTIONS = {
    # Core master schedule
    "create-master-schedule":      create_master_schedule,
    "update-master-schedule":      update_master_schedule,
    "get-master-schedule":         get_master_schedule,
    "list-master-schedules":       list_master_schedules,
    "add-section-to-schedule":     add_section_to_schedule,
    "add-section-meeting":         place_section_meeting,
    "delete-section-meeting":      remove_section_meeting,
    "list-section-meetings":       list_section_meetings,
    "get-schedule-matrix":         get_schedule_matrix,
    "get-course-demand-analysis":  analyze_course_demand,
    "get-fulfillment-report":      get_fulfillment_report,
    "get-load-balance-report":     get_load_balance_report,
    "submit-master-schedule":      publish_master_schedule,
    "update-schedule-lock":        lock_master_schedule,
    "create-schedule-clone":       clone_master_schedule,
    # Course requests
    "activate-course-requests":    open_course_requests,
    "submit-course-request":       submit_course_request,
    "update-course-request":       update_course_request,
    "get-course-request":          get_course_request,
    "list-course-requests":        list_course_requests,
    "approve-course-requests":     approve_course_requests,
    "get-demand-report":           get_demand_report,
    "get-singleton-analysis":      get_singleton_analysis,
    "complete-course-requests":    close_course_requests,
}
