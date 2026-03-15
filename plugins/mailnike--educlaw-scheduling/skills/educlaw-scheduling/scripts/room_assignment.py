"""EduClaw Advanced Scheduling — room_assignment domain module

Actions (10 room booking + 4 instructor constraints = 14 total):
  Room Booking: assign-room, propose-room, assign-rooms, delete-room-assignment,
                add-room-block, update-room-swap, get-room-availability,
                get-room-utilization-report, list-rooms-by-features,
                assign-room-emergency
  Instructor Constraints: add-instructor-constraint, update-instructor-constraint,
                          list-instructor-constraints, delete-instructor-constraint

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

VALID_BOOKING_TYPES = ("class", "exam", "event", "maintenance", "admin", "other")
VALID_BOOKING_STATUSES = ("confirmed", "tentative", "cancelled")
VALID_CONSTRAINT_TYPES = (
    "unavailable", "preferred", "max_periods_per_day",
    "max_consecutive_periods", "requires_prep_period", "preferred_building"
)
VALID_PRIORITIES = ("hard", "soft", "preference")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _validate_json_list(value, field_name):
    if value is None:
        return []
    try:
        parsed = json.loads(value) if isinstance(value, str) else value
        if not isinstance(parsed, list):
            err(f"{field_name} must be a JSON array")
        return parsed
    except (json.JSONDecodeError, TypeError):
        err(f"{field_name} must be valid JSON")


def _is_room_available(conn, room_id, day_type_id, bell_period_id, exclude_booking_id=None):
    """Check if a room is available at a given slot. Returns True if available."""
    query = (
        "SELECT id FROM educlaw_room_booking "
        "WHERE room_id = ? AND day_type_id = ? AND bell_period_id = ? "
        "AND booking_status != 'cancelled'"
    )
    params = [room_id, day_type_id, bell_period_id]
    if exclude_booking_id:
        query += " AND id != ?"
        params.append(exclude_booking_id)
    return conn.execute(query, params).fetchone() is None


def _create_room_booking(conn, room_id, master_id, meeting_id, day_type_id, bell_period_id,
                         booking_type, booking_title, booked_by, accessibility_required,
                         company_id, user_id=""):
    """Insert a room booking record and return its ID."""
    booking_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute(
        """INSERT INTO educlaw_room_booking
           (id, room_id, master_schedule_id, section_meeting_id, day_type_id, bell_period_id,
            booking_type, booking_title, booked_by, booking_status, cancellation_reason,
            accessibility_required, company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'confirmed', '', ?, ?, ?, ?, ?)""",
        (booking_id, room_id, master_id, meeting_id, day_type_id, bell_period_id,
         booking_type, booking_title, booked_by, accessibility_required,
         company_id, now, now, user_id)
    )
    return booking_id


def _refresh_sections_with_room(conn, master_id):
    """Update sections_with_room count on master_schedule."""
    count = conn.execute(
        "SELECT COUNT(DISTINCT section_id) FROM educlaw_section_meeting "
        "WHERE master_schedule_id = ? AND is_active = 1 AND room_id IS NOT NULL",
        (master_id,)
    ).fetchone()[0]
    conn.execute(
        "UPDATE educlaw_master_schedule SET sections_with_room = ?, "
        "updated_at = datetime('now') WHERE id = ?",
        (count, master_id)
    )


# ─────────────────────────────────────────────────────────────────────────────
# ROOM BOOKING
# ─────────────────────────────────────────────────────────────────────────────

def assign_room(conn, args):
    """Assign a room to a section meeting and create room booking."""
    meeting_id = getattr(args, "section_meeting_id", None)
    room_id = getattr(args, "room_id", None)

    if not meeting_id:
        err("--section-meeting-id is required")
    if not room_id:
        err("--room-id is required")

    meeting = conn.execute(
        "SELECT * FROM educlaw_section_meeting WHERE id = ?", (meeting_id,)
    ).fetchone()
    if not meeting:
        err(f"Section meeting {meeting_id} not found")
    meeting = dict(meeting)

    if not conn.execute("SELECT id FROM educlaw_room WHERE id = ?", (room_id,)).fetchone():
        err(f"Room {room_id} not found")

    # Check room availability
    if not _is_room_available(conn, room_id, meeting["day_type_id"], meeting["bell_period_id"]):
        err(f"Room {room_id} is already booked for this slot. "
            "Use propose-room to find available alternatives.")

    booking_type = getattr(args, "booking_type", None) or "class"
    if booking_type not in VALID_BOOKING_TYPES:
        err(f"--booking-type must be one of: {', '.join(VALID_BOOKING_TYPES)}")

    booked_by = getattr(args, "booked_by", None) or getattr(args, "user_id", None) or ""
    accessibility_required = int(getattr(args, "accessibility_required", None) or 0)
    company_id = meeting.get("company_id", "")
    master_id = meeting["master_schedule_id"]

    # Get section info for booking title
    sec = conn.execute(
        "SELECT s.section_number, c.name FROM educlaw_section s "
        "JOIN educlaw_course c ON c.id = s.course_id WHERE s.id = ?",
        (meeting["section_id"],)
    ).fetchone()
    booking_title = f"Class: {sec['section_number'] if sec else meeting['section_id']}"

    # Cancel existing booking if any
    old_booking = conn.execute(
        "SELECT id FROM educlaw_room_booking WHERE section_meeting_id = ? "
        "AND booking_status != 'cancelled'",
        (meeting_id,)
    ).fetchone()
    if old_booking:
        conn.execute(
            "UPDATE educlaw_room_booking SET booking_status = 'cancelled', "
            "cancellation_reason = 'Room reassigned', updated_at = datetime('now') WHERE id = ?",
            (old_booking["id"],)
        )

    booking_id = _create_room_booking(
        conn, room_id, master_id, meeting_id,
        meeting["day_type_id"], meeting["bell_period_id"],
        booking_type, booking_title, booked_by, accessibility_required,
        company_id, getattr(args, "user_id", None) or ""
    )

    # Update meeting's room_id
    conn.execute(
        "UPDATE educlaw_section_meeting SET room_id = ?, updated_at = datetime('now') WHERE id = ?",
        (room_id, meeting_id)
    )

    _refresh_sections_with_room(conn, master_id)

    audit(conn, SKILL, "assign-room", "educlaw_section_meeting", meeting_id,
          new_values={"room_id": room_id, "booking_id": booking_id})
    conn.commit()
    ok({"meeting_id": meeting_id, "room_id": room_id, "booking_id": booking_id,
        "booking_status": "confirmed"})


def suggest_room(conn, args):
    """Suggest available rooms for a section meeting, ranked by fit."""
    meeting_id = getattr(args, "section_meeting_id", None)
    if not meeting_id:
        err("--section-meeting-id is required")

    meeting = conn.execute(
        "SELECT * FROM educlaw_section_meeting WHERE id = ?", (meeting_id,)
    ).fetchone()
    if not meeting:
        err(f"Section meeting {meeting_id} not found")
    meeting = dict(meeting)

    # Get section info
    sec_info = conn.execute(
        "SELECT s.max_enrollment, s.current_enrollment, c.course_type "
        "FROM educlaw_section s JOIN educlaw_course c ON c.id = s.course_id "
        "WHERE s.id = ?",
        (meeting["section_id"],)
    ).fetchone()

    min_capacity = int(sec_info["current_enrollment"] if sec_info else 0)
    required_room_type = None
    if sec_info and sec_info["course_type"] == "lab":
        required_room_type = "lab"

    # Optional overrides from args
    room_type_filter = getattr(args, "room_type", None) or required_room_type
    accessibility = int(getattr(args, "accessibility_required", None) or 0)
    company_id = getattr(args, "company_id", None) or meeting.get("company_id", "")

    # Find all non-booked rooms at this slot
    booked_rooms = conn.execute(
        """SELECT DISTINCT room_id FROM educlaw_room_booking
           WHERE day_type_id = ? AND bell_period_id = ? AND booking_status != 'cancelled'""",
        (meeting["day_type_id"], meeting["bell_period_id"])
    ).fetchall()
    booked_room_ids = {r["room_id"] for r in booked_rooms}

    # Query available rooms
    query = """
        SELECT r.*,
               (SELECT COUNT(*) FROM educlaw_room_booking rb
                WHERE rb.room_id = r.id AND rb.booking_status != 'cancelled') as total_bookings
        FROM educlaw_room r
        WHERE r.is_active = 1 AND r.capacity >= ?
    """
    params = [min_capacity]

    if company_id:
        query += " AND r.company_id = ?"
        params.append(company_id)
    if room_type_filter:
        query += " AND r.room_type = ?"
        params.append(room_type_filter)

    query += " ORDER BY r.capacity ASC"

    all_rooms = conn.execute(query, params).fetchall()

    suggestions = []
    for room in all_rooms:
        rd = dict(room)
        if rd["id"] in booked_room_ids:
            continue

        # Score: lower utilization = better score
        score = 100
        # Capacity fit: penalize over-capacity rooms
        cap_diff = rd["capacity"] - min_capacity
        if cap_diff < 0:
            continue  # skip undersized
        score -= min(cap_diff // 5, 20)  # slight penalty for oversized rooms

        # Accessibility bonus
        facilities = _validate_json_list(rd.get("facilities"), "facilities")
        if accessibility and "accessible" in facilities:
            score += 10

        rd["facilities"] = facilities
        rd["availability_score"] = score
        rd["current_booking_count"] = rd.pop("total_bookings", 0)
        suggestions.append(rd)

    # Sort by score descending, then capacity ascending
    suggestions.sort(key=lambda r: (-r["availability_score"], r["capacity"]))

    ok({
        "meeting_id": meeting_id,
        "day_type_id": meeting["day_type_id"],
        "bell_period_id": meeting["bell_period_id"],
        "minimum_capacity_needed": min_capacity,
        "required_room_type": required_room_type,
        "suggestions": suggestions[:10],  # top 10
        "total_available": len(suggestions),
    })


def bulk_assign_rooms(conn, args):
    """Automatically assign rooms to all unassigned meetings in a master schedule."""
    master_id = getattr(args, "master_schedule_id", None)
    if not master_id:
        err("--master-schedule-id is required")

    master = conn.execute(
        "SELECT * FROM educlaw_master_schedule WHERE id = ?", (master_id,)
    ).fetchone()
    if not master:
        err(f"Master schedule {master_id} not found")
    master = dict(master)

    if master["schedule_status"] in ("published", "locked", "archived"):
        err(f"Master schedule is {master['schedule_status']} and cannot be modified")

    room_type_filter = getattr(args, "room_type", None)
    company_id = master["company_id"]
    user_id = getattr(args, "user_id", None) or ""

    # Get all unassigned meetings
    unassigned = conn.execute(
        """SELECT sm.*, s.current_enrollment, c.course_type
           FROM educlaw_section_meeting sm
           JOIN educlaw_section s ON s.id = sm.section_id
           JOIN educlaw_course c ON c.id = s.course_id
           WHERE sm.master_schedule_id = ? AND sm.is_active = 1 AND sm.room_id IS NULL""",
        (master_id,)
    ).fetchall()

    assigned_count = 0
    failed_count = 0
    now = _now_iso()

    for meeting in unassigned:
        m = dict(meeting)
        min_cap = m["current_enrollment"] or 0
        needed_type = "lab" if m["course_type"] == "lab" else None
        if room_type_filter:
            needed_type = room_type_filter

        # Find first available room with enough capacity
        rq = ("SELECT r.id, r.room_number, r.building FROM educlaw_room r "
              "WHERE r.is_active = 1 AND r.capacity >= ? AND r.company_id = ?")
        rp = [min_cap, company_id]
        if needed_type:
            rq += " AND r.room_type = ?"
            rp.append(needed_type)
        rq += " ORDER BY r.capacity ASC"

        candidate_rooms = conn.execute(rq, rp).fetchall()

        assigned = False
        for room in candidate_rooms:
            rid = room["id"]
            if _is_room_available(conn, rid, m["day_type_id"], m["bell_period_id"]):
                # Assign
                sec = conn.execute(
                    "SELECT section_number FROM educlaw_section WHERE id = ?",
                    (m["section_id"],)
                ).fetchone()
                title = f"Class: {sec['section_number'] if sec else m['section_id']}"
                booking_id = str(uuid.uuid4())
                conn.execute(
                    """INSERT INTO educlaw_room_booking
                       (id, room_id, master_schedule_id, section_meeting_id, day_type_id,
                        bell_period_id, booking_type, booking_title, booked_by,
                        booking_status, cancellation_reason, accessibility_required,
                        company_id, created_at, updated_at, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, 'class', ?, ?, 'confirmed', '', 0,
                               ?, ?, ?, ?)""",
                    (booking_id, rid, master_id, m["id"], m["day_type_id"],
                     m["bell_period_id"], title, user_id, company_id, now, now, user_id)
                )
                conn.execute(
                    "UPDATE educlaw_section_meeting SET room_id = ?, updated_at = datetime('now') "
                    "WHERE id = ?",
                    (rid, m["id"])
                )
                assigned = True
                assigned_count += 1
                break

        if not assigned:
            failed_count += 1

    _refresh_sections_with_room(conn, master_id)

    audit(conn, SKILL, "assign-rooms", "educlaw_master_schedule", master_id,
          new_values={"assigned": assigned_count, "failed": failed_count})
    conn.commit()
    ok({
        "master_schedule_id": master_id,
        "meetings_considered": len(unassigned),
        "rooms_assigned": assigned_count,
        "rooms_not_found": failed_count,
        "message": f"Bulk room assignment complete: {assigned_count} assigned, "
                   f"{failed_count} could not be assigned"
    })


def unassign_room(conn, args):
    """Remove room assignment from a section meeting."""
    meeting_id = getattr(args, "section_meeting_id", None)
    booking_id = getattr(args, "booking_id", None)

    if not meeting_id and not booking_id:
        err("--section-meeting-id or --booking-id is required")

    if meeting_id:
        meeting = conn.execute(
            "SELECT * FROM educlaw_section_meeting WHERE id = ?", (meeting_id,)
        ).fetchone()
        if not meeting:
            err(f"Section meeting {meeting_id} not found")
        meeting = dict(meeting)
        master_id = meeting["master_schedule_id"]

        # Cancel booking
        conn.execute(
            """UPDATE educlaw_room_booking
               SET booking_status = 'cancelled', cancellation_reason = 'Room unassigned',
                   updated_at = datetime('now')
               WHERE section_meeting_id = ? AND booking_status != 'cancelled'""",
            (meeting_id,)
        )

        old_room = meeting["room_id"]
        conn.execute(
            "UPDATE educlaw_section_meeting SET room_id = NULL, updated_at = datetime('now') "
            "WHERE id = ?",
            (meeting_id,)
        )
        _refresh_sections_with_room(conn, master_id)

        audit(conn, SKILL, "delete-room-assignment", "educlaw_section_meeting", meeting_id,
              old_values={"room_id": old_room})
        conn.commit()
        ok({"meeting_id": meeting_id, "room_unassigned": old_room,
            "message": "Room unassigned from meeting"})

    else:
        booking = conn.execute(
            "SELECT * FROM educlaw_room_booking WHERE id = ?", (booking_id,)
        ).fetchone()
        if not booking:
            err(f"Booking {booking_id} not found")
        booking = dict(booking)

        conn.execute(
            """UPDATE educlaw_room_booking
               SET booking_status = 'cancelled', cancellation_reason = 'Manually unassigned',
                   updated_at = datetime('now')
               WHERE id = ?""",
            (booking_id,)
        )
        if booking.get("section_meeting_id"):
            conn.execute(
                "UPDATE educlaw_section_meeting SET room_id = NULL, "
                "updated_at = datetime('now') WHERE id = ?",
                (booking["section_meeting_id"],)
            )
            if booking.get("master_schedule_id"):
                _refresh_sections_with_room(conn, booking["master_schedule_id"])

        audit(conn, SKILL, "delete-room-assignment", "educlaw_room_booking", booking_id,
              old_values={"booking_status": booking["booking_status"]})
        conn.commit()
        ok({"booking_id": booking_id, "room_id": booking["room_id"],
            "booking_status": "cancelled"})


def block_room(conn, args):
    """Block a room for a non-class purpose (event, maintenance, exam, etc.)."""
    room_id = getattr(args, "room_id", None)
    day_type_id = getattr(args, "day_type_id", None)
    bell_period_id = getattr(args, "bell_period_id", None)
    booking_title = getattr(args, "booking_title", None)
    booked_by = getattr(args, "booked_by", None) or getattr(args, "user_id", None) or ""

    if not room_id:
        err("--room-id is required")
    if not day_type_id:
        err("--day-type-id is required")
    if not bell_period_id:
        err("--bell-period-id is required")
    if not booking_title:
        err("--booking-title is required")

    if not conn.execute("SELECT id FROM educlaw_room WHERE id = ?", (room_id,)).fetchone():
        err(f"Room {room_id} not found")
    if not conn.execute("SELECT id FROM educlaw_day_type WHERE id = ?", (day_type_id,)).fetchone():
        err(f"Day type {day_type_id} not found")
    if not conn.execute("SELECT id FROM educlaw_bell_period WHERE id = ?", (bell_period_id,)).fetchone():
        err(f"Bell period {bell_period_id} not found")

    # Check availability
    if not _is_room_available(conn, room_id, day_type_id, bell_period_id):
        err(f"Room {room_id} is already booked for this slot")

    booking_type = getattr(args, "booking_type", None) or "admin"
    if booking_type not in VALID_BOOKING_TYPES:
        err(f"--booking-type must be one of: {', '.join(VALID_BOOKING_TYPES)}")

    master_id = getattr(args, "master_schedule_id", None)
    accessibility = int(getattr(args, "accessibility_required", None) or 0)
    company_id = getattr(args, "company_id", None) or ""

    booking_id = str(uuid.uuid4())
    now = _now_iso()

    conn.execute(
        """INSERT INTO educlaw_room_booking
           (id, room_id, master_schedule_id, section_meeting_id, day_type_id,
            bell_period_id, booking_type, booking_title, booked_by,
            booking_status, cancellation_reason, accessibility_required,
            company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, NULL, ?, ?, ?, ?, ?, 'confirmed', '', ?, ?, ?, ?, ?)""",
        (booking_id, room_id, master_id, day_type_id, bell_period_id,
         booking_type, booking_title, booked_by, accessibility,
         company_id, now, now, getattr(args, "user_id", None) or "")
    )

    audit(conn, SKILL, "add-room-block", "educlaw_room_booking", booking_id,
          new_values={"room_id": room_id, "booking_type": booking_type, "title": booking_title})
    conn.commit()
    ok({"booking_id": booking_id, "room_id": room_id, "booking_type": booking_type,
        "booking_title": booking_title, "booking_status": "confirmed"})


def swap_rooms(conn, args):
    """Swap room assignments between two section meetings."""
    meeting_id_a = getattr(args, "section_meeting_id", None)
    meeting_id_b = getattr(args, "section_meeting_id_b", None)

    if not meeting_id_a:
        err("--section-meeting-id is required (meeting A)")
    if not meeting_id_b:
        err("--section-meeting-id-b is required (meeting B)")

    meeting_a = conn.execute(
        "SELECT * FROM educlaw_section_meeting WHERE id = ?", (meeting_id_a,)
    ).fetchone()
    if not meeting_a:
        err(f"Section meeting {meeting_id_a} not found")
    meeting_a = dict(meeting_a)

    meeting_b = conn.execute(
        "SELECT * FROM educlaw_section_meeting WHERE id = ?", (meeting_id_b,)
    ).fetchone()
    if not meeting_b:
        err(f"Section meeting {meeting_id_b} not found")
    meeting_b = dict(meeting_b)

    if meeting_a["master_schedule_id"] != meeting_b["master_schedule_id"]:
        err("Both meetings must belong to the same master schedule")

    room_a = meeting_a.get("room_id")
    room_b = meeting_b.get("room_id")

    if not room_a and not room_b:
        err("Neither meeting has a room assigned")

    master_id = meeting_a["master_schedule_id"]
    company_id = meeting_a.get("company_id", "")
    user_id = getattr(args, "user_id", None) or ""
    now = _now_iso()

    # Cancel existing bookings for both
    conn.execute(
        """UPDATE educlaw_room_booking
           SET booking_status = 'cancelled', cancellation_reason = 'Room swap',
               updated_at = datetime('now')
           WHERE section_meeting_id IN (?, ?) AND booking_status != 'cancelled'""",
        (meeting_id_a, meeting_id_b)
    )

    # Assign room_b to meeting_a and room_a to meeting_b
    if room_b:
        conn.execute(
            "UPDATE educlaw_section_meeting SET room_id = ?, updated_at = datetime('now') WHERE id = ?",
            (room_b, meeting_id_a)
        )
        sec = conn.execute("SELECT section_number FROM educlaw_section WHERE id = ?",
                           (meeting_a["section_id"],)).fetchone()
        title_a = f"Class: {sec['section_number'] if sec else meeting_a['section_id']}"
        conn.execute(
            """INSERT INTO educlaw_room_booking
               (id, room_id, master_schedule_id, section_meeting_id, day_type_id,
                bell_period_id, booking_type, booking_title, booked_by,
                booking_status, cancellation_reason, accessibility_required,
                company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, 'class', ?, ?, 'confirmed', '', 0, ?, ?, ?, ?)""",
            (str(uuid.uuid4()), room_b, master_id, meeting_id_a,
             meeting_a["day_type_id"], meeting_a["bell_period_id"],
             title_a, user_id, company_id, now, now, user_id)
        )
    else:
        conn.execute(
            "UPDATE educlaw_section_meeting SET room_id = NULL, updated_at = datetime('now') WHERE id = ?",
            (meeting_id_a,)
        )

    if room_a:
        conn.execute(
            "UPDATE educlaw_section_meeting SET room_id = ?, updated_at = datetime('now') WHERE id = ?",
            (room_a, meeting_id_b)
        )
        sec = conn.execute("SELECT section_number FROM educlaw_section WHERE id = ?",
                           (meeting_b["section_id"],)).fetchone()
        title_b = f"Class: {sec['section_number'] if sec else meeting_b['section_id']}"
        conn.execute(
            """INSERT INTO educlaw_room_booking
               (id, room_id, master_schedule_id, section_meeting_id, day_type_id,
                bell_period_id, booking_type, booking_title, booked_by,
                booking_status, cancellation_reason, accessibility_required,
                company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, 'class', ?, ?, 'confirmed', '', 0, ?, ?, ?, ?)""",
            (str(uuid.uuid4()), room_a, master_id, meeting_id_b,
             meeting_b["day_type_id"], meeting_b["bell_period_id"],
             title_b, user_id, company_id, now, now, user_id)
        )
    else:
        conn.execute(
            "UPDATE educlaw_section_meeting SET room_id = NULL, updated_at = datetime('now') WHERE id = ?",
            (meeting_id_b,)
        )

    _refresh_sections_with_room(conn, master_id)

    audit(conn, SKILL, "update-room-swap", "educlaw_section_meeting", meeting_id_a,
          new_values={"swapped_with": meeting_id_b, "room_a": room_a, "room_b": room_b})
    conn.commit()
    ok({"meeting_a": meeting_id_a, "meeting_b": meeting_id_b,
        "room_now_in_a": room_b, "room_now_in_b": room_a,
        "message": "Rooms swapped successfully"})


def get_room_availability(conn, args):
    """Get a room's availability across all periods in a master schedule."""
    room_id = getattr(args, "room_id", None)
    master_id = getattr(args, "master_schedule_id", None)

    if not room_id:
        err("--room-id is required")
    if not master_id:
        err("--master-schedule-id is required")

    room = conn.execute("SELECT * FROM educlaw_room WHERE id = ?", (room_id,)).fetchone()
    if not room:
        err(f"Room {room_id} not found")
    room = dict(room)

    master = conn.execute(
        "SELECT * FROM educlaw_master_schedule WHERE id = ?", (master_id,)
    ).fetchone()
    if not master:
        err(f"Master schedule {master_id} not found")
    master = dict(master)

    # Get all day types and bell periods for this pattern
    day_types = conn.execute(
        """SELECT dt.* FROM educlaw_day_type dt
           WHERE dt.schedule_pattern_id = ? ORDER BY dt.sort_order""",
        (master["schedule_pattern_id"],)
    ).fetchall()

    bell_periods = conn.execute(
        """SELECT bp.* FROM educlaw_bell_period bp
           WHERE bp.schedule_pattern_id = ? ORDER BY bp.sort_order""",
        (master["schedule_pattern_id"],)
    ).fetchall()

    # Get all bookings for this room (across all master schedules — room is a shared resource)
    bookings = conn.execute(
        """SELECT day_type_id, bell_period_id, booking_type, booking_title,
                  booking_status, section_meeting_id
           FROM educlaw_room_booking
           WHERE room_id = ? AND booking_status != 'cancelled'""",
        (room_id,)
    ).fetchall()
    booked_slots = {(b["day_type_id"], b["bell_period_id"]): dict(b) for b in bookings}

    availability_grid = []
    total_periods = 0
    available_periods = 0

    for bp in bell_periods:
        bp_dict = dict(bp)
        if bp_dict["period_type"] != "class":
            continue
        row_entry = {
            "bell_period_id": bp_dict["id"],
            "period_number": bp_dict["period_number"],
            "period_name": bp_dict["period_name"],
            "start_time": bp_dict["start_time"],
            "end_time": bp_dict["end_time"],
            "slots": {}
        }
        for dt in day_types:
            total_periods += 1
            key = (dt["id"], bp_dict["id"])
            if key in booked_slots:
                booking = booked_slots[key]
                row_entry["slots"][dt["code"]] = {
                    "available": False,
                    "booking_type": booking["booking_type"],
                    "booking_title": booking["booking_title"],
                }
            else:
                row_entry["slots"][dt["code"]] = {"available": True}
                available_periods += 1
        availability_grid.append(row_entry)

    ok({
        "room_id": room_id,
        "room_number": room["room_number"],
        "building": room["building"],
        "capacity": room["capacity"],
        "room_type": room["room_type"],
        "master_schedule_id": master_id,
        "total_class_periods": total_periods,
        "available_periods": available_periods,
        "booked_periods": total_periods - available_periods,
        "utilization_pct": round((total_periods - available_periods) / total_periods * 100, 1)
                           if total_periods > 0 else 0.0,
        "availability_grid": availability_grid,
    })


def get_room_utilization_report(conn, args):
    """Report room utilization across a master schedule."""
    master_id = getattr(args, "master_schedule_id", None)
    if not master_id:
        err("--master-schedule-id is required")

    master = conn.execute(
        "SELECT * FROM educlaw_master_schedule WHERE id = ?", (master_id,)
    ).fetchone()
    if not master:
        err(f"Master schedule {master_id} not found")
    master = dict(master)

    # Count total available class periods per room (pattern × day_types × class bell periods)
    total_class_periods = conn.execute(
        """SELECT COUNT(*) FROM educlaw_day_type dt
           CROSS JOIN educlaw_bell_period bp
           WHERE dt.schedule_pattern_id = ? AND bp.schedule_pattern_id = ?
             AND bp.period_type = 'class'""",
        (master["schedule_pattern_id"], master["schedule_pattern_id"])
    ).fetchone()[0]

    # Room booking counts
    rows = conn.execute(
        """SELECT rb.room_id, r.room_number, r.building, r.capacity, r.room_type,
                  COUNT(*) as booked_periods,
                  SUM(CASE WHEN rb.booking_type = 'class' THEN 1 ELSE 0 END) as class_periods
           FROM educlaw_room_booking rb
           JOIN educlaw_room r ON r.id = rb.room_id
           WHERE rb.master_schedule_id = ? AND rb.booking_status != 'cancelled'
           GROUP BY rb.room_id
           ORDER BY r.building, r.room_number""",
        (master_id,)
    ).fetchall()

    report = []
    for r in rows:
        rd = dict(r)
        util_pct = round(rd["booked_periods"] / total_class_periods * 100, 1) \
                   if total_class_periods > 0 else 0.0
        rd["total_available_periods"] = total_class_periods
        rd["utilization_pct"] = util_pct
        report.append(rd)

    ok({
        "master_schedule_id": master_id,
        "total_class_periods_per_room": total_class_periods,
        "rooms": report,
        "room_count": len(report),
    })


def search_rooms_by_features(conn, args):
    """Search for rooms matching capacity, type, building, and facilities criteria."""
    company_id = getattr(args, "company_id", None)

    query = "SELECT * FROM educlaw_room WHERE is_active = 1"
    params = []

    if company_id:
        query += " AND company_id = ?"; params.append(company_id)

    room_type = getattr(args, "room_type", None)
    if room_type:
        query += " AND room_type = ?"; params.append(room_type)

    capacity = getattr(args, "capacity", None)
    if capacity:
        query += " AND capacity >= ?"; params.append(int(capacity))

    building = getattr(args, "building", None)
    if building:
        query += " AND building LIKE ?"; params.append(f"%{building}%")

    query += " ORDER BY building, room_number"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rooms = conn.execute(query, params).fetchall()

    # Filter by features if provided
    features_filter_raw = getattr(args, "features", None)
    features_filter = _validate_json_list(features_filter_raw, "features") if features_filter_raw else []

    result = []
    for r in rooms:
        rd = dict(r)
        try:
            facilities = json.loads(rd["facilities"]) if rd["facilities"] else []
        except (json.JSONDecodeError, TypeError):
            facilities = []
        rd["facilities"] = facilities

        if features_filter:
            if not all(f in facilities for f in features_filter):
                continue
        result.append(rd)

    ok({"rooms": result, "count": len(result)})


def emergency_reassign_room(conn, args):
    """Move all bookings from a source room to a target room for a master schedule."""
    source_room_id = getattr(args, "room_id", None)
    target_room_id = getattr(args, "target_room_id", None)
    master_id = getattr(args, "master_schedule_id", None)

    if not source_room_id:
        err("--room-id is required (source room)")
    if not target_room_id:
        err("--target-room-id is required")
    if not master_id:
        err("--master-schedule-id is required")

    if not conn.execute("SELECT id FROM educlaw_room WHERE id = ?", (source_room_id,)).fetchone():
        err(f"Source room {source_room_id} not found")
    if not conn.execute("SELECT id FROM educlaw_room WHERE id = ?", (target_room_id,)).fetchone():
        err(f"Target room {target_room_id} not found")
    if not conn.execute(
        "SELECT id FROM educlaw_master_schedule WHERE id = ?", (master_id,)
    ).fetchone():
        err(f"Master schedule {master_id} not found")

    # Get all active bookings in source room for this master schedule
    source_bookings = conn.execute(
        """SELECT * FROM educlaw_room_booking
           WHERE room_id = ? AND master_schedule_id = ? AND booking_status != 'cancelled'""",
        (source_room_id, master_id)
    ).fetchall()

    if not source_bookings:
        ok({"source_room_id": source_room_id, "target_room_id": target_room_id,
            "bookings_moved": 0, "message": "No active bookings found in source room"})
        return

    # Check for conflicts in target room
    conflicts = []
    for bk in source_bookings:
        bk_d = dict(bk)
        if not _is_room_available(conn, target_room_id,
                                  bk_d["day_type_id"], bk_d["bell_period_id"]):
            conflicts.append(f"Slot {bk_d['day_type_id']}/{bk_d['bell_period_id']} "
                             "already booked in target room")

    if conflicts:
        err(f"Cannot reassign: target room has conflicts:\n" + "\n".join(conflicts))

    now = _now_iso()
    user_id = getattr(args, "user_id", None) or ""
    moved = 0

    for bk in source_bookings:
        bk_d = dict(bk)
        # Cancel old booking
        conn.execute(
            """UPDATE educlaw_room_booking
               SET booking_status = 'cancelled',
                   cancellation_reason = 'Emergency room reassignment',
                   updated_at = datetime('now')
               WHERE id = ?""",
            (bk_d["id"],)
        )
        # Create new booking in target room
        new_booking_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO educlaw_room_booking
               (id, room_id, master_schedule_id, section_meeting_id, day_type_id,
                bell_period_id, booking_type, booking_title, booked_by,
                booking_status, cancellation_reason, accessibility_required,
                company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'confirmed', '', ?, ?, ?, ?, ?)""",
            (new_booking_id, target_room_id, master_id, bk_d.get("section_meeting_id"),
             bk_d["day_type_id"], bk_d["bell_period_id"],
             bk_d["booking_type"], bk_d["booking_title"],
             user_id, bk_d["accessibility_required"],
             bk_d["company_id"], now, now, user_id)
        )
        # Update section_meeting.room_id
        if bk_d.get("section_meeting_id"):
            conn.execute(
                "UPDATE educlaw_section_meeting SET room_id = ?, updated_at = datetime('now') "
                "WHERE id = ?",
                (target_room_id, bk_d["section_meeting_id"])
            )
        moved += 1

    audit(conn, SKILL, "assign-room-emergency", "educlaw_room_booking", master_id,
          new_values={"source_room": source_room_id, "target_room": target_room_id,
                      "bookings_moved": moved})
    conn.commit()
    ok({"source_room_id": source_room_id, "target_room_id": target_room_id,
        "master_schedule_id": master_id, "bookings_moved": moved,
        "message": f"Emergency reassignment complete: {moved} booking(s) moved"})


# ─────────────────────────────────────────────────────────────────────────────
# INSTRUCTOR CONSTRAINTS
# ─────────────────────────────────────────────────────────────────────────────

def add_instructor_constraint(conn, args):
    """Add a scheduling constraint for an instructor in a term."""
    instructor_id = getattr(args, "instructor_id", None)
    academic_term_id = getattr(args, "academic_term_id", None)
    constraint_type = getattr(args, "constraint_type", None)
    company_id = getattr(args, "company_id", None)

    if not instructor_id:
        err("--instructor-id is required")
    if not academic_term_id:
        err("--academic-term-id is required")
    if not constraint_type:
        err("--constraint-type is required")
    if constraint_type not in VALID_CONSTRAINT_TYPES:
        err(f"--constraint-type must be one of: {', '.join(VALID_CONSTRAINT_TYPES)}")

    if not conn.execute(
        "SELECT id FROM educlaw_instructor WHERE id = ?", (instructor_id,)
    ).fetchone():
        err(f"Instructor {instructor_id} not found")

    if not conn.execute(
        "SELECT id FROM educlaw_academic_term WHERE id = ?", (academic_term_id,)
    ).fetchone():
        err(f"Academic term {academic_term_id} not found")

    day_type_id = getattr(args, "day_type_id", None)
    bell_period_id = getattr(args, "bell_period_id", None)

    if day_type_id:
        if not conn.execute(
            "SELECT id FROM educlaw_day_type WHERE id = ?", (day_type_id,)
        ).fetchone():
            err(f"Day type {day_type_id} not found")

    if bell_period_id:
        if not conn.execute(
            "SELECT id FROM educlaw_bell_period WHERE id = ?", (bell_period_id,)
        ).fetchone():
            err(f"Bell period {bell_period_id} not found")

    constraint_value = int(getattr(args, "constraint_value", None) or 0)
    constraint_notes = getattr(args, "constraint_notes", None) or ""
    priority = getattr(args, "priority", None) or "preference"
    if priority not in VALID_PRIORITIES:
        err(f"--priority must be one of: {', '.join(VALID_PRIORITIES)}")

    company_id = company_id or conn.execute(
        "SELECT company_id FROM educlaw_instructor WHERE id = ?", (instructor_id,)
    ).fetchone()["company_id"]

    is_active = int(getattr(args, "is_active", None) or 1)
    now = _now_iso()
    constraint_id = str(uuid.uuid4())

    try:
        conn.execute(
            """INSERT INTO educlaw_instructor_constraint
               (id, instructor_id, academic_term_id, constraint_type,
                day_type_id, bell_period_id, constraint_value, constraint_notes,
                priority, is_active, company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (constraint_id, instructor_id, academic_term_id, constraint_type,
             day_type_id, bell_period_id, constraint_value, constraint_notes,
             priority, is_active, company_id, now, now,
             getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Constraint creation failed: {e}")

    audit(conn, SKILL, "add-instructor-constraint", "educlaw_instructor_constraint", constraint_id,
          new_values={"instructor_id": instructor_id, "constraint_type": constraint_type,
                      "academic_term_id": academic_term_id})
    conn.commit()
    ok({"id": constraint_id, "instructor_id": instructor_id,
        "constraint_type": constraint_type, "priority": priority,
        "academic_term_id": academic_term_id})


def update_instructor_constraint(conn, args):
    """Update an instructor constraint's value, notes, priority, or active status."""
    constraint_id = getattr(args, "constraint_id", None)
    if not constraint_id:
        err("--constraint-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_instructor_constraint WHERE id = ?", (constraint_id,)
    ).fetchone()
    if not row:
        err(f"Instructor constraint {constraint_id} not found")

    updates, params, changed = [], [], []

    if getattr(args, "constraint_value", None) is not None:
        updates.append("constraint_value = ?")
        params.append(int(args.constraint_value)); changed.append("constraint_value")
    if getattr(args, "constraint_notes", None) is not None:
        updates.append("constraint_notes = ?")
        params.append(args.constraint_notes); changed.append("constraint_notes")
    if getattr(args, "priority", None) is not None:
        if args.priority not in VALID_PRIORITIES:
            err(f"--priority must be one of: {', '.join(VALID_PRIORITIES)}")
        updates.append("priority = ?"); params.append(args.priority); changed.append("priority")
    if getattr(args, "is_active", None) is not None:
        updates.append("is_active = ?")
        params.append(int(args.is_active)); changed.append("is_active")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(constraint_id)
    conn.execute(
        f"UPDATE educlaw_instructor_constraint SET {', '.join(updates)} WHERE id = ?", params
    )
    audit(conn, SKILL, "update-instructor-constraint", "educlaw_instructor_constraint",
          constraint_id, new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": constraint_id, "updated_fields": changed})


def list_instructor_constraints(conn, args):
    """List instructor constraints with optional filters."""
    query = "SELECT * FROM educlaw_instructor_constraint WHERE 1=1"
    params = []

    if getattr(args, "instructor_id", None):
        query += " AND instructor_id = ?"; params.append(args.instructor_id)
    if getattr(args, "academic_term_id", None):
        query += " AND academic_term_id = ?"; params.append(args.academic_term_id)
    if getattr(args, "constraint_type", None):
        query += " AND constraint_type = ?"; params.append(args.constraint_type)
    if getattr(args, "is_active", None) is not None:
        query += " AND is_active = ?"; params.append(int(args.is_active))
    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)

    query += " ORDER BY instructor_id, constraint_type"
    limit = int(getattr(args, "limit", None) or 100)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"instructor_constraints": [dict(r) for r in rows], "count": len(rows)})


def delete_instructor_constraint(conn, args):
    """Delete an instructor constraint (hard delete — it's a configuration record)."""
    constraint_id = getattr(args, "constraint_id", None)
    if not constraint_id:
        err("--constraint-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_instructor_constraint WHERE id = ?", (constraint_id,)
    ).fetchone()
    if not row:
        err(f"Instructor constraint {constraint_id} not found")

    constraint = dict(row)
    conn.execute("DELETE FROM educlaw_instructor_constraint WHERE id = ?", (constraint_id,))

    audit(conn, SKILL, "delete-instructor-constraint", "educlaw_instructor_constraint",
          constraint_id, old_values={"constraint_type": constraint["constraint_type"],
                                     "instructor_id": constraint["instructor_id"]})
    conn.commit()
    ok({"id": constraint_id, "message": "Instructor constraint deleted",
        "instructor_id": constraint["instructor_id"],
        "constraint_type": constraint["constraint_type"]})


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

ACTIONS = {
    # Room booking
    "assign-room":                  assign_room,
    "propose-room":                 suggest_room,
    "assign-rooms":                 bulk_assign_rooms,
    "delete-room-assignment":       unassign_room,
    "add-room-block":               block_room,
    "update-room-swap":             swap_rooms,
    "get-room-availability":        get_room_availability,
    "get-room-utilization-report":  get_room_utilization_report,
    "list-rooms-by-features":       search_rooms_by_features,
    "assign-room-emergency":        emergency_reassign_room,
    # Instructor constraints
    "add-instructor-constraint":    add_instructor_constraint,
    "update-instructor-constraint": update_instructor_constraint,
    "list-instructor-constraints":  list_instructor_constraints,
    "delete-instructor-constraint": delete_instructor_constraint,
}
