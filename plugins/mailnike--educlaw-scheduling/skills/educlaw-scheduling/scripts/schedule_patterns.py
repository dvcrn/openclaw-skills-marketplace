"""EduClaw Advanced Scheduling — schedule_patterns domain module

Actions: add-schedule-pattern, update-schedule-pattern, get-schedule-pattern,
list-schedule-patterns, add-day-type, add-bell-period, activate-schedule-pattern,
get-day-type-calendar, get-pattern-calendar, get-contact-hours

Imported by db_query.py (unified router).
"""
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timedelta, timezone

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection
    from erpclaw_lib.response import ok, err
    from erpclaw_lib.audit import audit
except ImportError:
    pass

SKILL = "educlaw-scheduling"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

VALID_PATTERN_TYPES = (
    "traditional", "block_4x4", "block_ab", "trimester",
    "rotating_drop", "semester", "custom"
)
VALID_PERIOD_TYPES = (
    "class", "break", "lunch", "homeroom", "advisory", "flex", "passing"
)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _validate_json_list(value, field_name):
    """Parse and validate a JSON array argument, returning a list."""
    if value is None:
        return []
    try:
        parsed = json.loads(value) if isinstance(value, str) else value
        if not isinstance(parsed, list):
            err(f"{field_name} must be a JSON array")
        return parsed
    except (json.JSONDecodeError, TypeError):
        err(f"{field_name} must be valid JSON")


def _parse_time_to_minutes(t):
    """Convert HH:MM string to total minutes since midnight."""
    try:
        h, m = t.split(":")
        return int(h) * 60 + int(m)
    except Exception:
        return 0


# ─────────────────────────────────────────────────────────────────────────────
# SCHEDULE PATTERN
# ─────────────────────────────────────────────────────────────────────────────

def add_schedule_pattern(conn, args):
    """Create a new named schedule pattern."""
    name = getattr(args, "name", None)
    pattern_type = getattr(args, "pattern_type", None)
    cycle_days = getattr(args, "cycle_days", None)
    company_id = getattr(args, "company_id", None)

    if not name:
        err("--name is required")
    if not pattern_type:
        err("--pattern-type is required")
    if pattern_type not in VALID_PATTERN_TYPES:
        err(f"--pattern-type must be one of: {', '.join(VALID_PATTERN_TYPES)}")
    if cycle_days is None:
        err("--cycle-days is required")
    cycle_days = int(cycle_days)
    if cycle_days < 1:
        err("--cycle-days must be >= 1")
    if not company_id:
        err("--company-id is required")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    description = getattr(args, "description", None) or ""
    notes = getattr(args, "notes", None) or ""
    total_periods = int(getattr(args, "total_periods_per_cycle", None) or 0)
    is_active = int(getattr(args, "is_active", None) or 0)  # inactive until explicitly activated
    now = _now_iso()
    pattern_id = str(uuid.uuid4())

    try:
        conn.execute(
            """INSERT INTO educlaw_schedule_pattern
               (id, name, description, pattern_type, cycle_days, total_periods_per_cycle,
                notes, is_active, company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (pattern_id, name, description, pattern_type, cycle_days, total_periods,
             notes, is_active, company_id, now, now,
             getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Schedule pattern creation failed: {e}")

    audit(conn, SKILL, "add-schedule-pattern", "educlaw_schedule_pattern", pattern_id,
          new_values={"name": name, "pattern_type": pattern_type, "cycle_days": cycle_days})
    conn.commit()
    ok({"id": pattern_id, "name": name, "pattern_type": pattern_type,
        "cycle_days": cycle_days, "is_active": is_active})


def update_schedule_pattern(conn, args):
    """Update a schedule pattern's descriptive fields."""
    pattern_id = getattr(args, "pattern_id", None)
    if not pattern_id:
        err("--pattern-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_schedule_pattern WHERE id = ?", (pattern_id,)
    ).fetchone()
    if not row:
        err(f"Schedule pattern {pattern_id} not found")

    updates, params, changed = [], [], []

    if getattr(args, "name", None) is not None:
        updates.append("name = ?"); params.append(args.name); changed.append("name")
    if getattr(args, "description", None) is not None:
        updates.append("description = ?"); params.append(args.description)
        changed.append("description")
    if getattr(args, "notes", None) is not None:
        updates.append("notes = ?"); params.append(args.notes); changed.append("notes")
    if getattr(args, "total_periods_per_cycle", None) is not None:
        updates.append("total_periods_per_cycle = ?")
        params.append(int(args.total_periods_per_cycle))
        changed.append("total_periods_per_cycle")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(pattern_id)
    conn.execute(
        f"UPDATE educlaw_schedule_pattern SET {', '.join(updates)} WHERE id = ?", params
    )
    audit(conn, SKILL, "update-schedule-pattern", "educlaw_schedule_pattern", pattern_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"id": pattern_id, "updated_fields": changed})


def get_schedule_pattern(conn, args):
    """Get a schedule pattern with its day types and bell periods."""
    pattern_id = getattr(args, "pattern_id", None)
    if not pattern_id:
        err("--pattern-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_schedule_pattern WHERE id = ?", (pattern_id,)
    ).fetchone()
    if not row:
        err(f"Schedule pattern {pattern_id} not found")

    data = dict(row)
    day_types = conn.execute(
        "SELECT * FROM educlaw_day_type WHERE schedule_pattern_id = ? ORDER BY sort_order",
        (pattern_id,)
    ).fetchall()
    data["day_types"] = [dict(d) for d in day_types]

    bell_periods = conn.execute(
        "SELECT * FROM educlaw_bell_period WHERE schedule_pattern_id = ? ORDER BY sort_order",
        (pattern_id,)
    ).fetchall()
    for bp in bell_periods:
        bp_dict = dict(bp)
        bp_dict["applies_to_day_types"] = _validate_json_list(
            bp_dict.get("applies_to_day_types"), "applies_to_day_types"
        )
        data.setdefault("bell_periods", []).append(bp_dict)

    if "bell_periods" not in data:
        data["bell_periods"] = []

    ok(data)


def list_schedule_patterns(conn, args):
    """List schedule patterns with optional filters."""
    query = "SELECT * FROM educlaw_schedule_pattern WHERE 1=1"
    params = []

    company_id = getattr(args, "company_id", None)
    if company_id:
        query += " AND company_id = ?"; params.append(company_id)

    pattern_type = getattr(args, "pattern_type", None)
    if pattern_type:
        query += " AND pattern_type = ?"; params.append(pattern_type)

    is_active = getattr(args, "is_active", None)
    if is_active is not None:
        query += " AND is_active = ?"; params.append(int(is_active))

    search = getattr(args, "search", None)
    if search:
        query += " AND (name LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY name"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"schedule_patterns": [dict(r) for r in rows], "count": len(rows)})


# ─────────────────────────────────────────────────────────────────────────────
# DAY TYPE
# ─────────────────────────────────────────────────────────────────────────────

def add_day_type(conn, args):
    """Add a named day type to a schedule pattern (e.g., 'Day A', 'Day B')."""
    schedule_pattern_id = getattr(args, "schedule_pattern_id", None)
    code = getattr(args, "code", None)
    name = getattr(args, "name", None)

    if not schedule_pattern_id:
        err("--schedule-pattern-id is required")
    if not code:
        err("--code is required")
    if not name:
        err("--name is required")

    if not conn.execute(
        "SELECT id FROM educlaw_schedule_pattern WHERE id = ?", (schedule_pattern_id,)
    ).fetchone():
        err(f"Schedule pattern {schedule_pattern_id} not found")

    sort_order = int(getattr(args, "sort_order", None) or 0)
    company_id = getattr(args, "company_id", None) or ""
    now = _now_iso()
    day_type_id = str(uuid.uuid4())

    try:
        conn.execute(
            """INSERT INTO educlaw_day_type
               (id, schedule_pattern_id, code, name, sort_order, company_id, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (day_type_id, schedule_pattern_id, code, name, sort_order, company_id, now,
             getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Day type creation failed (code may already exist in this pattern): {e}")

    audit(conn, SKILL, "add-day-type", "educlaw_day_type", day_type_id,
          new_values={"schedule_pattern_id": schedule_pattern_id, "code": code, "name": name})
    conn.commit()
    ok({"id": day_type_id, "schedule_pattern_id": schedule_pattern_id,
        "code": code, "name": name, "sort_order": sort_order})


# ─────────────────────────────────────────────────────────────────────────────
# BELL PERIOD
# ─────────────────────────────────────────────────────────────────────────────

def add_bell_period(conn, args):
    """Add a named time slot (bell period) to a schedule pattern."""
    schedule_pattern_id = getattr(args, "schedule_pattern_id", None)
    period_number = getattr(args, "period_number", None)
    period_name = getattr(args, "period_name", None)
    start_time = getattr(args, "start_time", None)
    end_time = getattr(args, "end_time", None)
    duration_minutes = getattr(args, "duration_minutes", None)

    if not schedule_pattern_id:
        err("--schedule-pattern-id is required")
    if not period_number:
        err("--period-number is required")
    if not period_name:
        err("--period-name is required")
    if not start_time:
        err("--start-time is required")
    if not end_time:
        err("--end-time is required")
    if duration_minutes is None:
        err("--duration-minutes is required")

    duration_minutes = int(duration_minutes)
    if duration_minutes <= 0:
        err("--duration-minutes must be > 0")

    if not conn.execute(
        "SELECT id FROM educlaw_schedule_pattern WHERE id = ?", (schedule_pattern_id,)
    ).fetchone():
        err(f"Schedule pattern {schedule_pattern_id} not found")

    period_type = getattr(args, "period_type", None) or "class"
    if period_type not in VALID_PERIOD_TYPES:
        err(f"--period-type must be one of: {', '.join(VALID_PERIOD_TYPES)}")

    applies_to_raw = getattr(args, "applies_to_day_types", None)
    applies_to = _validate_json_list(applies_to_raw, "applies_to_day_types")
    applies_to_str = json.dumps(applies_to)

    sort_order = int(getattr(args, "sort_order", None) or 0)
    company_id = getattr(args, "company_id", None) or ""
    now = _now_iso()
    period_id = str(uuid.uuid4())

    try:
        conn.execute(
            """INSERT INTO educlaw_bell_period
               (id, schedule_pattern_id, period_number, period_name, start_time, end_time,
                duration_minutes, period_type, applies_to_day_types, sort_order,
                company_id, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (period_id, schedule_pattern_id, period_number, period_name, start_time, end_time,
             duration_minutes, period_type, applies_to_str, sort_order, company_id, now,
             getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Bell period creation failed (period_number may already exist in this pattern): {e}")

    audit(conn, SKILL, "add-bell-period", "educlaw_bell_period", period_id,
          new_values={"schedule_pattern_id": schedule_pattern_id,
                      "period_number": period_number, "period_name": period_name})
    conn.commit()
    ok({"id": period_id, "schedule_pattern_id": schedule_pattern_id,
        "period_number": period_number, "period_name": period_name,
        "start_time": start_time, "end_time": end_time, "duration_minutes": duration_minutes})


# ─────────────────────────────────────────────────────────────────────────────
# ACTIVATE PATTERN
# ─────────────────────────────────────────────────────────────────────────────

def activate_schedule_pattern(conn, args):
    """Activate a schedule pattern after validating it has day types and bell periods."""
    pattern_id = getattr(args, "pattern_id", None)
    if not pattern_id:
        err("--pattern-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_schedule_pattern WHERE id = ?", (pattern_id,)
    ).fetchone()
    if not row:
        err(f"Schedule pattern {pattern_id} not found")

    # Validate at least one day type
    day_count = conn.execute(
        "SELECT COUNT(*) FROM educlaw_day_type WHERE schedule_pattern_id = ?", (pattern_id,)
    ).fetchone()[0]
    if day_count == 0:
        err("Cannot activate: pattern must have at least one day type. "
            "Use add-day-type to add day types first.")

    # Validate at least one bell period
    period_count = conn.execute(
        "SELECT COUNT(*) FROM educlaw_bell_period WHERE schedule_pattern_id = ?", (pattern_id,)
    ).fetchone()[0]
    if period_count == 0:
        err("Cannot activate: pattern must have at least one bell period. "
            "Use add-bell-period to add bell periods first.")

    conn.execute(
        "UPDATE educlaw_schedule_pattern SET is_active = 1, updated_at = datetime('now') WHERE id = ?",
        (pattern_id,)
    )
    audit(conn, SKILL, "activate-schedule-pattern", "educlaw_schedule_pattern", pattern_id,
          new_values={"is_active": 1})
    conn.commit()
    ok({"id": pattern_id, "is_active": 1,
        "day_types": day_count, "bell_periods": period_count,
        "message": "Schedule pattern activated"})


# ─────────────────────────────────────────────────────────────────────────────
# MAP DAY TYPE TO DATES
# ─────────────────────────────────────────────────────────────────────────────

def map_day_type_to_dates(conn, args):
    """Map day types to calendar dates over a date range (cycling rotation)."""
    pattern_id = getattr(args, "pattern_id", None)
    date_range_start = getattr(args, "date_range_start", None)
    date_range_end = getattr(args, "date_range_end", None)

    if not pattern_id:
        err("--pattern-id is required")
    if not date_range_start:
        err("--date-range-start is required")
    if not date_range_end:
        err("--date-range-end is required")

    row = conn.execute(
        "SELECT * FROM educlaw_schedule_pattern WHERE id = ?", (pattern_id,)
    ).fetchone()
    if not row:
        err(f"Schedule pattern {pattern_id} not found")

    day_types = conn.execute(
        "SELECT * FROM educlaw_day_type WHERE schedule_pattern_id = ? ORDER BY sort_order, code",
        (pattern_id,)
    ).fetchall()
    if not day_types:
        err("Pattern has no day types defined")

    day_type_list = [dict(d) for d in day_types]

    try:
        start_dt = datetime.strptime(date_range_start, "%Y-%m-%d")
        end_dt = datetime.strptime(date_range_end, "%Y-%m-%d")
    except ValueError:
        err("Dates must be in YYYY-MM-DD format")

    if start_dt > end_dt:
        err("date-range-start must be before date-range-end")

    # Build calendar: skip weekends by default (Mon-Fri only)
    calendar = []
    current = start_dt
    cycle_index = 0
    n_types = len(day_type_list)

    while current <= end_dt:
        # Skip Saturday (5) and Sunday (6)
        if current.weekday() < 5:
            dt = day_type_list[cycle_index % n_types]
            calendar.append({
                "date": current.strftime("%Y-%m-%d"),
                "weekday": current.strftime("%A"),
                "day_type_id": dt["id"],
                "day_type_code": dt["code"],
                "day_type_name": dt["name"],
            })
            cycle_index += 1
        current += timedelta(days=1)

    ok({
        "pattern_id": pattern_id,
        "pattern_name": dict(row)["name"],
        "date_range_start": date_range_start,
        "date_range_end": date_range_end,
        "total_school_days": len(calendar),
        "cycle_length": n_types,
        "calendar": calendar,
    })


# ─────────────────────────────────────────────────────────────────────────────
# GET PATTERN CALENDAR
# ─────────────────────────────────────────────────────────────────────────────

def get_pattern_calendar(conn, args):
    """Get a pattern's day types and bell periods laid out as a weekly grid."""
    pattern_id = getattr(args, "pattern_id", None)
    if not pattern_id:
        err("--pattern-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_schedule_pattern WHERE id = ?", (pattern_id,)
    ).fetchone()
    if not row:
        err(f"Schedule pattern {pattern_id} not found")

    pattern = dict(row)

    day_types = conn.execute(
        "SELECT * FROM educlaw_day_type WHERE schedule_pattern_id = ? ORDER BY sort_order",
        (pattern_id,)
    ).fetchall()
    day_type_list = [dict(d) for d in day_types]

    bell_periods = conn.execute(
        """SELECT * FROM educlaw_bell_period WHERE schedule_pattern_id = ?
           ORDER BY sort_order, start_time""",
        (pattern_id,)
    ).fetchall()

    # Build grid: period → day_types grid
    grid = []
    total_class_minutes = 0
    for bp in bell_periods:
        bp_dict = dict(bp)
        applies = _validate_json_list(bp_dict.get("applies_to_day_types"), "applies_to_day_types")
        # If empty applies_to_day_types, period applies to ALL day types
        effective_days = applies if applies else [dt["id"] for dt in day_type_list]
        bp_dict["applies_to_day_types"] = applies
        bp_dict["effective_day_type_ids"] = effective_days
        bp_dict["occurrences_per_cycle"] = len(effective_days)
        if bp_dict["period_type"] == "class":
            total_class_minutes += bp_dict["duration_minutes"] * len(effective_days)
        grid.append(bp_dict)

    ok({
        "pattern_id": pattern_id,
        "pattern_name": pattern["name"],
        "pattern_type": pattern["pattern_type"],
        "cycle_days": pattern["cycle_days"],
        "is_active": pattern["is_active"],
        "day_types": day_type_list,
        "bell_periods": grid,
        "total_class_minutes_per_cycle": total_class_minutes,
        "total_class_hours_per_cycle": round(total_class_minutes / 60, 2),
    })


# ─────────────────────────────────────────────────────────────────────────────
# CALCULATE CONTACT HOURS
# ─────────────────────────────────────────────────────────────────────────────

def calculate_contact_hours(conn, args):
    """Calculate expected contact hours for a section (or pattern) per cycle."""
    pattern_id = getattr(args, "pattern_id", None)
    section_id = getattr(args, "section_id", None)
    master_schedule_id = getattr(args, "master_schedule_id", None)

    if not pattern_id:
        err("--pattern-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_schedule_pattern WHERE id = ?", (pattern_id,)
    ).fetchone()
    if not row:
        err(f"Schedule pattern {pattern_id} not found")

    pattern = dict(row)

    if section_id and master_schedule_id:
        # Calculate from actual placed meetings
        meetings = conn.execute(
            """SELECT sm.*, bp.duration_minutes, bp.period_type, bp.period_name
               FROM educlaw_section_meeting sm
               JOIN educlaw_bell_period bp ON bp.id = sm.bell_period_id
               WHERE sm.section_id = ? AND sm.master_schedule_id = ? AND sm.is_active = 1""",
            (section_id, master_schedule_id)
        ).fetchall()

        meeting_list = [dict(m) for m in meetings]
        total_minutes = sum(m["duration_minutes"] for m in meeting_list
                            if m["period_type"] == "class")
        total_all_minutes = sum(m["duration_minutes"] for m in meeting_list)

        ok({
            "pattern_id": pattern_id,
            "section_id": section_id,
            "master_schedule_id": master_schedule_id,
            "meetings_per_cycle": len(meeting_list),
            "class_minutes_per_cycle": total_minutes,
            "class_hours_per_cycle": round(total_minutes / 60, 2),
            "total_minutes_per_cycle": total_all_minutes,
            "meetings": meeting_list,
        })
    else:
        # Theoretical: all class periods in the pattern
        day_types = conn.execute(
            "SELECT id FROM educlaw_day_type WHERE schedule_pattern_id = ?", (pattern_id,)
        ).fetchall()
        all_day_type_ids = [d["id"] for d in day_types]

        periods = conn.execute(
            """SELECT * FROM educlaw_bell_period WHERE schedule_pattern_id = ?
               ORDER BY sort_order""",
            (pattern_id,)
        ).fetchall()

        breakdown = []
        total_class_minutes = 0
        for p in periods:
            pd = dict(p)
            applies = _validate_json_list(pd.get("applies_to_day_types"), "applies_to_day_types")
            effective = applies if applies else all_day_type_ids
            occurrences = len(effective)
            minutes = pd["duration_minutes"] * occurrences
            if pd["period_type"] == "class":
                total_class_minutes += minutes
            breakdown.append({
                "period_number": pd["period_number"],
                "period_name": pd["period_name"],
                "period_type": pd["period_type"],
                "duration_minutes": pd["duration_minutes"],
                "occurrences_per_cycle": occurrences,
                "total_minutes": minutes,
            })

        ok({
            "pattern_id": pattern_id,
            "pattern_name": pattern["name"],
            "cycle_days": pattern["cycle_days"],
            "class_minutes_per_cycle": total_class_minutes,
            "class_hours_per_cycle": round(total_class_minutes / 60, 2),
            "breakdown": breakdown,
        })


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

ACTIONS = {
    "add-schedule-pattern":    add_schedule_pattern,
    "update-schedule-pattern": update_schedule_pattern,
    "get-schedule-pattern":    get_schedule_pattern,
    "list-schedule-patterns":  list_schedule_patterns,
    "add-day-type":            add_day_type,
    "add-bell-period":         add_bell_period,
    "activate-schedule-pattern": activate_schedule_pattern,
    "get-day-type-calendar":   map_day_type_to_dates,
    "get-pattern-calendar":    get_pattern_calendar,
    "get-contact-hours":       calculate_contact_hours,
}
