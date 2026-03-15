"""EduClaw State Reporting — demographics domain module

Actions for student demographic supplements: race/ethnicity, SSID, EL status,
SPED status, economic status, SPED placements, SPED services, EL program history.

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
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
except ImportError:
    pass

SKILL = "educlaw-statereport"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

VALID_SSID_STATUSES = ("pending", "assigned", "not_applicable")
VALID_RACE_CODES = {"WHITE", "BLACK", "ASIAN", "AIAN", "NHOPI"}
VALID_RACE_ROLLUPS = (
    "WHITE", "BLACK_OR_AFRICAN_AMERICAN", "ASIAN",
    "AMERICAN_INDIAN_OR_ALASKA_NATIVE", "NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER",
    "TWO_OR_MORE_RACES", "HISPANIC_OR_LATINO", ""
)
VALID_PROFICIENCY_INSTRUMENTS = ("WIDA_ACCESS", "ELPAC", "TELPAS", "LAS_LINKS", "IPT", "OTHER", "")
VALID_LUNCH_STATUSES = ("free", "reduced", "paid", "direct_certification", "")
VALID_HOMELESS_RESIDENCES = ("sheltered", "unsheltered", "doubled_up", "hotel_motel", "")
VALID_MILITARY_TYPES = ("active_duty", "veteran", "national_guard", "")

VALID_DISABILITY_CATEGORIES = ("AUT", "DB", "DD", "ED", "HI", "ID", "MD", "OHI", "OI", "SLD", "SLI", "TBI", "VI", "")
VALID_ED_ENVIRONMENTS = ("RC_80", "RC_40_79", "RC_LT40", "SC", "SS", "RF", "HH", "")
VALID_SPED_EXIT_REASONS = ("graduated", "dropped_out", "reached_max_age", "transferred", "died", "not_eligible", "")
VALID_EC_ENVIRONMENTS = ("early_childhood_program", "home", "part_time_ec_part_time_home", "")
VALID_SERVICE_TYPES = (
    "speech_language", "occupational_therapy", "physical_therapy", "counseling",
    "audiology", "orientation_mobility", "special_transportation",
    "behavior_intervention", "vision_services", "other"
)
VALID_PROVIDER_TYPES = ("school_employed", "contracted", "")

VALID_EL_PROGRAM_TYPES = (
    "pull_out", "push_in", "sheltered_english", "dual_language",
    "tbe_transitional", "tbe_developmental", "waiver", "content_based"
)
VALID_EL_EXIT_REASONS = ("reclassified", "parent_waiver", "transferred", "graduated", "")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _compute_race_rollup(is_hispanic, race_codes_list):
    """Compute federal race rollup per OMB rules."""
    if is_hispanic:
        return "HISPANIC_OR_LATINO"
    if not race_codes_list:
        return ""
    # Map internal codes to federal rollup names
    rollup_map = {
        "WHITE": "WHITE",
        "BLACK": "BLACK_OR_AFRICAN_AMERICAN",
        "ASIAN": "ASIAN",
        "AIAN": "AMERICAN_INDIAN_OR_ALASKA_NATIVE",
        "NHOPI": "NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER",
    }
    valid_races = [r for r in race_codes_list if r in rollup_map]
    if len(valid_races) == 0:
        return ""
    if len(valid_races) >= 2:
        return "TWO_OR_MORE_RACES"
    return rollup_map[valid_races[0]]


def _parse_race_codes(raw):
    """Parse and validate race codes JSON array."""
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    try:
        parsed = json.loads(raw)
        if not isinstance(parsed, list):
            return []
        return [c for c in parsed if c in VALID_RACE_CODES]
    except (json.JSONDecodeError, TypeError):
        return []


# ─────────────────────────────────────────────────────────────────────────────
# STUDENT SUPPLEMENT
# ─────────────────────────────────────────────────────────────────────────────

def add_student_supplement(conn, args):
    student_id = getattr(args, "student_id", None)
    company_id = getattr(args, "company_id", None)

    if not student_id:
        err("--student-id is required")
    if not company_id:
        err("--company-id is required")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        err(f"Student {student_id} not found")
    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    # Check uniqueness
    if conn.execute("SELECT id FROM sr_student_supplement WHERE student_id = ?", (student_id,)).fetchone():
        err(f"Supplement already exists for student {student_id}")

    supp_id = str(uuid.uuid4())
    now = _now_iso()

    ssid = getattr(args, "ssid", None) or ""
    ssid_state_code = getattr(args, "ssid_state_code", None) or ""
    ssid_status = getattr(args, "ssid_status", None) or "pending"
    if ssid_status not in VALID_SSID_STATUSES:
        err(f"--ssid-status must be one of: {', '.join(VALID_SSID_STATUSES)}")

    is_hispanic = int(getattr(args, "is_hispanic_latino", None) or 0)
    race_codes_raw = getattr(args, "race_codes", None) or "[]"
    race_codes_list = _parse_race_codes(race_codes_raw)
    race_federal_rollup = _compute_race_rollup(is_hispanic, race_codes_list)

    is_el = int(getattr(args, "is_el", None) or 0)
    el_entry_date = getattr(args, "el_entry_date", None) or ""
    home_language_code = getattr(args, "home_language_code", None) or ""
    native_language_code = getattr(args, "native_language_code", None) or ""
    english_proficiency_level = getattr(args, "english_proficiency_level", None) or ""
    english_proficiency_instrument = getattr(args, "english_proficiency_instrument", None) or ""
    if english_proficiency_instrument not in VALID_PROFICIENCY_INSTRUMENTS:
        err(f"--english-proficiency-instrument must be one of: {', '.join(VALID_PROFICIENCY_INSTRUMENTS)}")
    el_exit_date = getattr(args, "el_exit_date", None) or ""
    is_rfep = int(getattr(args, "is_rfep", None) or 0)
    rfep_date = getattr(args, "rfep_date", None) or ""

    is_sped = int(getattr(args, "is_sped", None) or 0)
    is_504 = int(getattr(args, "is_504", None) or 0)
    sped_entry_date = getattr(args, "sped_entry_date", None) or ""
    sped_exit_date = getattr(args, "sped_exit_date", None) or ""

    is_econ_disadv = int(getattr(args, "is_economically_disadvantaged", None) or 0)
    lunch_status = getattr(args, "lunch_program_status", None) or ""
    if lunch_status not in VALID_LUNCH_STATUSES:
        err(f"--lunch-program-status must be one of: {', '.join(VALID_LUNCH_STATUSES)}")

    is_migrant = int(getattr(args, "is_migrant", None) or 0)
    is_homeless = int(getattr(args, "is_homeless", None) or 0)
    homeless_residence = getattr(args, "homeless_primary_nighttime_residence", None) or ""
    if homeless_residence not in VALID_HOMELESS_RESIDENCES:
        err(f"--homeless-primary-nighttime-residence must be one of: {', '.join(VALID_HOMELESS_RESIDENCES)}")
    is_foster = int(getattr(args, "is_foster_care", None) or 0)
    is_military = int(getattr(args, "is_military_connected", None) or 0)
    military_type = getattr(args, "military_connection_type", None) or ""
    if military_type not in VALID_MILITARY_TYPES:
        err(f"--military-connection-type must be one of: {', '.join(VALID_MILITARY_TYPES)}")

    try:
        conn.execute(
            """INSERT INTO sr_student_supplement
               (id, student_id, ssid, ssid_state_code, ssid_status,
                is_hispanic_latino, race_codes, race_federal_rollup,
                is_el, el_entry_date, home_language_code, native_language_code,
                english_proficiency_level, english_proficiency_instrument,
                el_exit_date, is_rfep, rfep_date,
                is_sped, is_504, sped_entry_date, sped_exit_date,
                is_economically_disadvantaged, lunch_program_status,
                is_migrant, is_homeless, homeless_primary_nighttime_residence,
                is_foster_care, is_military_connected, military_connection_type,
                company_id, created_at, updated_at, created_by)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (supp_id, student_id, ssid, ssid_state_code, ssid_status,
             is_hispanic, json.dumps(race_codes_list), race_federal_rollup,
             is_el, el_entry_date, home_language_code, native_language_code,
             english_proficiency_level, english_proficiency_instrument,
             el_exit_date, is_rfep, rfep_date,
             is_sped, is_504, sped_entry_date, sped_exit_date,
             is_econ_disadv, lunch_status,
             is_migrant, is_homeless, homeless_residence,
             is_foster, is_military, military_type,
             company_id, now, now, getattr(args, "user_id", None) or "")
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        err(f"Cannot create supplement: {e}")

    audit(conn, "sr_student_supplement", supp_id, "INSERT", getattr(args, "user_id", None) or "")
    ok({"id": supp_id, "student_id": student_id, "race_federal_rollup": race_federal_rollup,
        "message": "Student supplement created"})


def update_student_supplement(conn, args):
    supplement_id = getattr(args, "supplement_id", None)
    student_id = getattr(args, "student_id", None)

    if not supplement_id and not student_id:
        err("--supplement-id or --student-id is required")

    if supplement_id:
        row = conn.execute("SELECT * FROM sr_student_supplement WHERE id = ?", (supplement_id,)).fetchone()
    else:
        row = conn.execute("SELECT * FROM sr_student_supplement WHERE student_id = ?", (student_id,)).fetchone()

    if not row:
        err("Student supplement not found")

    rec = dict(row)
    now = _now_iso()

    # Build updates
    updates = {}

    ssid = getattr(args, "ssid", None)
    if ssid is not None:
        updates["ssid"] = ssid

    ssid_state_code = getattr(args, "ssid_state_code", None)
    if ssid_state_code is not None:
        updates["ssid_state_code"] = ssid_state_code

    ssid_status = getattr(args, "ssid_status", None)
    if ssid_status is not None:
        if ssid_status not in VALID_SSID_STATUSES:
            err(f"--ssid-status must be one of: {', '.join(VALID_SSID_STATUSES)}")
        updates["ssid_status"] = ssid_status

    # Race/ethnicity — recompute rollup if either changes
    is_hispanic_raw = getattr(args, "is_hispanic_latino", None)
    race_codes_raw = getattr(args, "race_codes", None)

    if is_hispanic_raw is not None or race_codes_raw is not None:
        is_hispanic = int(is_hispanic_raw) if is_hispanic_raw is not None else rec["is_hispanic_latino"]
        if race_codes_raw is not None:
            race_codes_list = _parse_race_codes(race_codes_raw)
        else:
            race_codes_list = _parse_race_codes(rec["race_codes"])
        race_federal_rollup = _compute_race_rollup(is_hispanic, race_codes_list)
        updates["is_hispanic_latino"] = is_hispanic
        updates["race_codes"] = json.dumps(race_codes_list)
        updates["race_federal_rollup"] = race_federal_rollup

    for field in [
        "is_el", "el_entry_date", "home_language_code", "native_language_code",
        "english_proficiency_level", "el_exit_date", "is_rfep", "rfep_date",
        "is_sped", "is_504", "sped_entry_date", "sped_exit_date",
        "is_economically_disadvantaged", "lunch_program_status",
        "is_migrant", "is_homeless", "homeless_primary_nighttime_residence",
        "is_foster_care", "is_military_connected", "military_connection_type",
        "english_proficiency_instrument"
    ]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    if not updates:
        err("No fields to update")

    updates["updated_at"] = now
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [rec["id"]]

    try:
        conn.execute(f"UPDATE sr_student_supplement SET {set_clause} WHERE id = ?", values)
        conn.commit()
    except sqlite3.IntegrityError as e:
        err(f"Cannot update supplement: {e}")

    audit(conn, "sr_student_supplement", rec["id"], "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": rec["id"], "message": "Student supplement updated"})


def get_student_supplement(conn, args):
    student_id = getattr(args, "student_id", None)
    supplement_id = getattr(args, "supplement_id", None)

    if student_id:
        row = conn.execute("SELECT * FROM sr_student_supplement WHERE student_id = ?", (student_id,)).fetchone()
    elif supplement_id:
        row = conn.execute("SELECT * FROM sr_student_supplement WHERE id = ?", (supplement_id,)).fetchone()
    else:
        err("--student-id or --supplement-id is required")

    if not row:
        err("Student supplement not found")

    rec = dict(row)
    rec["race_codes"] = json.loads(rec["race_codes"]) if rec.get("race_codes") else []
    ok(rec)


def list_student_supplements(conn, args):
    company_id = getattr(args, "company_id", None)
    if not company_id:
        err("--company-id is required")

    conditions = ["ss.company_id = ?"]
    params = [company_id]

    missing_ssid = getattr(args, "missing_ssid", None)
    if missing_ssid and str(missing_ssid).lower() in ("1", "true", "yes"):
        conditions.append("ss.ssid_status = 'pending'")

    missing_race = getattr(args, "missing_race", None)
    if missing_race and str(missing_race).lower() in ("1", "true", "yes"):
        conditions.append("(ss.race_codes = '[]' OR ss.race_codes = '')")

    is_el = getattr(args, "is_el", None)
    if is_el is not None:
        conditions.append("ss.is_el = ?")
        params.append(int(is_el))

    is_sped = getattr(args, "is_sped", None)
    if is_sped is not None:
        conditions.append("ss.is_sped = ?")
        params.append(int(is_sped))

    search = getattr(args, "search", None)
    if search:
        conditions.append("(s.first_name LIKE ? OR s.last_name LIKE ? OR ss.ssid LIKE ?)")
        params += [f"%{search}%", f"%{search}%", f"%{search}%"]

    where = " AND ".join(conditions)
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)

    rows = conn.execute(
        f"""SELECT ss.*, s.first_name, s.last_name, s.full_name, s.grade_level
            FROM sr_student_supplement ss
            JOIN educlaw_student s ON s.id = ss.student_id
            WHERE {where}
            ORDER BY s.last_name, s.first_name
            LIMIT ? OFFSET ?""",
        params + [limit, offset]
    ).fetchall()

    result = []
    for r in rows:
        rec = dict(r)
        rec["race_codes"] = json.loads(rec["race_codes"]) if rec.get("race_codes") else []
        result.append(rec)
    ok({"supplements": result, "count": len(result)})


def assign_ssid(conn, args):
    student_id = getattr(args, "student_id", None)
    ssid = getattr(args, "ssid", None)
    ssid_state_code = getattr(args, "ssid_state_code", None)

    if not student_id:
        err("--student-id is required")
    if not ssid:
        err("--ssid is required")

    row = conn.execute("SELECT id FROM sr_student_supplement WHERE student_id = ?", (student_id,)).fetchone()
    if not row:
        err(f"No supplement found for student {student_id}. Run add-student-supplement first.")

    now = _now_iso()
    updates = {"ssid": ssid, "ssid_status": "assigned", "updated_at": now}
    if ssid_state_code:
        updates["ssid_state_code"] = ssid_state_code

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE sr_student_supplement SET {set_clause} WHERE student_id = ?",
        list(updates.values()) + [student_id]
    )
    conn.commit()
    audit(conn, "sr_student_supplement", row["id"], "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": row["id"], "ssid": ssid, "ssid_status": "assigned", "message": "SSID assigned"})


def set_student_race(conn, args):
    student_id = getattr(args, "student_id", None)
    race_codes_raw = getattr(args, "race_codes", None)
    is_hispanic_raw = getattr(args, "is_hispanic_latino", None)

    if not student_id:
        err("--student-id is required")

    row = conn.execute("SELECT * FROM sr_student_supplement WHERE student_id = ?", (student_id,)).fetchone()
    if not row:
        err(f"No supplement found for student {student_id}")

    rec = dict(row)
    is_hispanic = int(is_hispanic_raw) if is_hispanic_raw is not None else rec["is_hispanic_latino"]
    if race_codes_raw is not None:
        race_codes_list = _parse_race_codes(race_codes_raw)
    else:
        race_codes_list = _parse_race_codes(rec["race_codes"])

    race_federal_rollup = _compute_race_rollup(is_hispanic, race_codes_list)
    now = _now_iso()

    conn.execute(
        """UPDATE sr_student_supplement
           SET is_hispanic_latino = ?, race_codes = ?, race_federal_rollup = ?, updated_at = ?
           WHERE student_id = ?""",
        (is_hispanic, json.dumps(race_codes_list), race_federal_rollup, now, student_id)
    )
    conn.commit()
    audit(conn, "sr_student_supplement", rec["id"], "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": rec["id"], "race_codes": race_codes_list, "race_federal_rollup": race_federal_rollup,
        "message": "Race/ethnicity updated"})


def update_el_status(conn, args):
    student_id = getattr(args, "student_id", None)
    if not student_id:
        err("--student-id is required")

    row = conn.execute("SELECT id FROM sr_student_supplement WHERE student_id = ?", (student_id,)).fetchone()
    if not row:
        err(f"No supplement found for student {student_id}")

    updates = {}
    for field in [
        "is_el", "el_entry_date", "home_language_code", "native_language_code",
        "english_proficiency_level", "english_proficiency_instrument",
        "el_exit_date", "is_rfep", "rfep_date"
    ]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    if not updates:
        err("No EL fields to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE sr_student_supplement SET {set_clause} WHERE student_id = ?",
        list(updates.values()) + [student_id]
    )
    conn.commit()
    audit(conn, "sr_student_supplement", row["id"], "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": row["id"], "message": "EL status updated"})


def update_sped_status(conn, args):
    student_id = getattr(args, "student_id", None)
    if not student_id:
        err("--student-id is required")

    row = conn.execute("SELECT id FROM sr_student_supplement WHERE student_id = ?", (student_id,)).fetchone()
    if not row:
        err(f"No supplement found for student {student_id}")

    updates = {}
    for field in ["is_sped", "is_504", "sped_entry_date", "sped_exit_date"]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    if not updates:
        err("No SPED fields to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE sr_student_supplement SET {set_clause} WHERE student_id = ?",
        list(updates.values()) + [student_id]
    )
    conn.commit()
    audit(conn, "sr_student_supplement", row["id"], "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": row["id"], "message": "SPED status updated"})


def update_economic_status(conn, args):
    student_id = getattr(args, "student_id", None)
    if not student_id:
        err("--student-id is required")

    row = conn.execute("SELECT id FROM sr_student_supplement WHERE student_id = ?", (student_id,)).fetchone()
    if not row:
        err(f"No supplement found for student {student_id}")

    updates = {}
    is_econ = getattr(args, "is_economically_disadvantaged", None)
    if is_econ is not None:
        updates["is_economically_disadvantaged"] = int(is_econ)

    lunch_status = getattr(args, "lunch_program_status", None)
    if lunch_status is not None:
        if lunch_status not in VALID_LUNCH_STATUSES:
            err(f"--lunch-program-status must be one of: {', '.join(VALID_LUNCH_STATUSES)}")
        updates["lunch_program_status"] = lunch_status

    if not updates:
        err("No economic status fields to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE sr_student_supplement SET {set_clause} WHERE student_id = ?",
        list(updates.values()) + [student_id]
    )
    conn.commit()
    audit(conn, "sr_student_supplement", row["id"], "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": row["id"], "message": "Economic status updated"})


# ─────────────────────────────────────────────────────────────────────────────
# SPED PLACEMENT
# ─────────────────────────────────────────────────────────────────────────────

def add_sped_placement(conn, args):
    student_id = getattr(args, "student_id", None)
    school_year = getattr(args, "school_year", None)
    disability_category = getattr(args, "disability_category", None)
    educational_environment = getattr(args, "educational_environment", None)
    company_id = getattr(args, "company_id", None)

    if not student_id:
        err("--student-id is required")
    if not school_year:
        err("--school-year is required")
    if not company_id:
        err("--company-id is required")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        err(f"Student {student_id} not found")
    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    if disability_category and disability_category not in VALID_DISABILITY_CATEGORIES:
        err(f"--disability-category must be one of: {', '.join(VALID_DISABILITY_CATEGORIES)}")
    if educational_environment and educational_environment not in VALID_ED_ENVIRONMENTS:
        err(f"--educational-environment must be one of: {', '.join(VALID_ED_ENVIRONMENTS)}")

    # Check uniqueness (student + year)
    if conn.execute(
        "SELECT id FROM sr_sped_placement WHERE student_id = ? AND school_year = ?",
        (student_id, int(school_year))
    ).fetchone():
        err(f"SPED placement already exists for student {student_id} in year {school_year}")

    placement_id = str(uuid.uuid4())
    now = _now_iso()
    sped_exit_reason = getattr(args, "sped_exit_reason", None) or ""
    if sped_exit_reason and sped_exit_reason not in VALID_SPED_EXIT_REASONS:
        err(f"--sped-exit-reason must be one of: {', '.join(VALID_SPED_EXIT_REASONS)}")

    ec_env = getattr(args, "early_childhood_environment", None) or ""
    if ec_env and ec_env not in VALID_EC_ENVIRONMENTS:
        err(f"--early-childhood-environment must be one of: {', '.join(VALID_EC_ENVIRONMENTS)}")

    try:
        conn.execute(
            """INSERT INTO sr_sped_placement
               (id, student_id, school_year, disability_category, secondary_disability,
                educational_environment, sped_program_entry_date, sped_program_exit_date,
                sped_exit_reason, iep_start_date, iep_review_date,
                is_transition_plan_required, lre_percentage,
                is_early_childhood, early_childhood_environment,
                company_id, created_at, updated_at, created_by)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (placement_id, student_id, int(school_year),
             disability_category or "", getattr(args, "secondary_disability", None) or "",
             educational_environment or "",
             getattr(args, "sped_program_entry_date", None) or "",
             getattr(args, "sped_program_exit_date", None) or "",
             sped_exit_reason,
             getattr(args, "iep_start_date", None) or "",
             getattr(args, "iep_review_date", None) or "",
             int(getattr(args, "is_transition_plan_required", None) or 0),
             getattr(args, "lre_percentage", None) or "",
             int(getattr(args, "is_early_childhood", None) or 0),
             ec_env,
             company_id, now, now,
             getattr(args, "user_id", None) or "")
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        err(f"Cannot create SPED placement: {e}")

    audit(conn, "sr_sped_placement", placement_id, "INSERT", getattr(args, "user_id", None) or "")
    ok({"id": placement_id, "student_id": student_id, "school_year": int(school_year),
        "message": "SPED placement created"})


def update_sped_placement(conn, args):
    placement_id = getattr(args, "placement_id", None)
    if not placement_id:
        err("--placement-id is required")

    row = conn.execute("SELECT id FROM sr_sped_placement WHERE id = ?", (placement_id,)).fetchone()
    if not row:
        err(f"SPED placement {placement_id} not found")

    updates = {}
    for field in [
        "disability_category", "secondary_disability", "educational_environment",
        "sped_program_entry_date", "sped_program_exit_date", "sped_exit_reason",
        "iep_start_date", "iep_review_date", "is_transition_plan_required",
        "lre_percentage", "is_early_childhood", "early_childhood_environment"
    ]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    if not updates:
        err("No fields to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE sr_sped_placement SET {set_clause} WHERE id = ?",
        list(updates.values()) + [placement_id]
    )
    conn.commit()
    audit(conn, "sr_sped_placement", placement_id, "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": placement_id, "message": "SPED placement updated"})


def get_sped_placement(conn, args):
    student_id = getattr(args, "student_id", None)
    school_year = getattr(args, "school_year", None)
    placement_id = getattr(args, "placement_id", None)

    if placement_id:
        row = conn.execute("SELECT * FROM sr_sped_placement WHERE id = ?", (placement_id,)).fetchone()
    elif student_id and school_year:
        row = conn.execute(
            "SELECT * FROM sr_sped_placement WHERE student_id = ? AND school_year = ?",
            (student_id, int(school_year))
        ).fetchone()
    elif student_id:
        # Get most recent
        row = conn.execute(
            "SELECT * FROM sr_sped_placement WHERE student_id = ? ORDER BY school_year DESC LIMIT 1",
            (student_id,)
        ).fetchone()
    else:
        err("--placement-id, --student-id, or --student-id + --school-year required")

    if not row:
        err("SPED placement not found")

    ok(dict(row))


def list_sped_placements(conn, args):
    company_id = getattr(args, "company_id", None)
    if not company_id:
        err("--company-id is required")

    conditions = ["company_id = ?"]
    params = [company_id]

    school_year = getattr(args, "school_year", None)
    if school_year:
        conditions.append("school_year = ?")
        params.append(int(school_year))

    disability_category = getattr(args, "disability_category", None)
    if disability_category:
        conditions.append("disability_category = ?")
        params.append(disability_category)

    educational_environment = getattr(args, "educational_environment", None)
    if educational_environment:
        conditions.append("educational_environment = ?")
        params.append(educational_environment)

    where = " AND ".join(conditions)
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)

    rows = conn.execute(
        f"SELECT * FROM sr_sped_placement WHERE {where} ORDER BY school_year DESC, created_at LIMIT ? OFFSET ?",
        params + [limit, offset]
    ).fetchall()

    ok({"placements": [dict(r) for r in rows], "count": len(rows)})


# ─────────────────────────────────────────────────────────────────────────────
# SPED SERVICES
# ─────────────────────────────────────────────────────────────────────────────

def add_sped_service(conn, args):
    sped_placement_id = getattr(args, "sped_placement_id", None)
    student_id = getattr(args, "student_id", None)
    service_type = getattr(args, "service_type", None)
    company_id = getattr(args, "company_id", None)

    if not sped_placement_id:
        err("--sped-placement-id is required")
    if not service_type:
        err("--service-type is required")
    if not company_id:
        err("--company-id is required")
    if service_type not in VALID_SERVICE_TYPES:
        err(f"--service-type must be one of: {', '.join(VALID_SERVICE_TYPES)}")

    placement_row = conn.execute(
        "SELECT id, student_id FROM sr_sped_placement WHERE id = ?", (sped_placement_id,)
    ).fetchone()
    if not placement_row:
        err(f"SPED placement {sped_placement_id} not found")

    # Use student_id from placement if not provided
    if not student_id:
        student_id = placement_row["student_id"]

    provider_type = getattr(args, "provider_type", None) or ""
    if provider_type and provider_type not in VALID_PROVIDER_TYPES:
        err(f"--provider-type must be one of: {', '.join(VALID_PROVIDER_TYPES)}")

    service_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO sr_sped_service
               (id, sped_placement_id, student_id, service_type, provider_type,
                minutes_per_week, start_date, end_date,
                company_id, created_at, created_by)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (service_id, sped_placement_id, student_id, service_type, provider_type,
             int(getattr(args, "minutes_per_week", None) or 0),
             getattr(args, "start_date", None) or "",
             getattr(args, "end_date", None) or "",
             company_id, now, getattr(args, "user_id", None) or "")
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        err(f"Cannot create SPED service: {e}")

    audit(conn, "sr_sped_service", service_id, "INSERT", getattr(args, "user_id", None) or "")
    ok({"id": service_id, "sped_placement_id": sped_placement_id, "service_type": service_type,
        "message": "SPED service added"})


def update_sped_service(conn, args):
    service_id = getattr(args, "service_id", None)
    if not service_id:
        err("--service-id is required")

    row = conn.execute("SELECT id FROM sr_sped_service WHERE id = ?", (service_id,)).fetchone()
    if not row:
        err(f"SPED service {service_id} not found")

    updates = {}
    for field in ["service_type", "provider_type", "minutes_per_week", "start_date", "end_date"]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    if not updates:
        err("No fields to update")

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE sr_sped_service SET {set_clause} WHERE id = ?",
        list(updates.values()) + [service_id]
    )
    conn.commit()
    audit(conn, "sr_sped_service", service_id, "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": service_id, "message": "SPED service updated"})


def list_sped_services(conn, args):
    sped_placement_id = getattr(args, "sped_placement_id", None)
    student_id = getattr(args, "student_id", None)
    company_id = getattr(args, "company_id", None)

    if sped_placement_id:
        rows = conn.execute(
            "SELECT * FROM sr_sped_service WHERE sped_placement_id = ? ORDER BY created_at",
            (sped_placement_id,)
        ).fetchall()
    elif student_id:
        rows = conn.execute(
            "SELECT * FROM sr_sped_service WHERE student_id = ? ORDER BY created_at",
            (student_id,)
        ).fetchall()
    elif company_id:
        service_type = getattr(args, "service_type", None)
        if service_type:
            rows = conn.execute(
                "SELECT * FROM sr_sped_service WHERE company_id = ? AND service_type = ? ORDER BY created_at",
                (company_id, service_type)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM sr_sped_service WHERE company_id = ? ORDER BY created_at",
                (company_id,)
            ).fetchall()
    else:
        err("--sped-placement-id, --student-id, or --company-id is required")

    ok({"services": [dict(r) for r in rows], "count": len(rows)})


def delete_sped_service(conn, args):
    service_id = getattr(args, "service_id", None)
    if not service_id:
        err("--service-id is required")

    row = conn.execute("SELECT id FROM sr_sped_service WHERE id = ?", (service_id,)).fetchone()
    if not row:
        err(f"SPED service {service_id} not found")

    # Check not part of a snapshot
    # (sr_snapshot_record stores JSON blobs; we can't easily check FK, so we allow deletion)
    conn.execute("DELETE FROM sr_sped_service WHERE id = ?", (service_id,))
    conn.commit()
    audit(conn, "sr_sped_service", service_id, "DELETE", getattr(args, "user_id", None) or "")
    ok({"id": service_id, "message": "SPED service deleted"})


# ─────────────────────────────────────────────────────────────────────────────
# EL PROGRAM
# ─────────────────────────────────────────────────────────────────────────────

def add_el_program(conn, args):
    student_id = getattr(args, "student_id", None)
    school_year = getattr(args, "school_year", None)
    program_type = getattr(args, "program_type", None)
    entry_date = getattr(args, "entry_date", None)
    company_id = getattr(args, "company_id", None)

    if not student_id:
        err("--student-id is required")
    if not school_year:
        err("--school-year is required")
    if not program_type:
        err("--program-type is required")
    if program_type not in VALID_EL_PROGRAM_TYPES:
        err(f"--program-type must be one of: {', '.join(VALID_EL_PROGRAM_TYPES)}")
    if not company_id:
        err("--company-id is required")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        err(f"Student {student_id} not found")
    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    proficiency_instrument = getattr(args, "proficiency_instrument", None) or ""
    if proficiency_instrument and proficiency_instrument not in VALID_PROFICIENCY_INSTRUMENTS:
        err(f"--proficiency-instrument must be one of: {', '.join(VALID_PROFICIENCY_INSTRUMENTS)}")

    exit_reason = getattr(args, "exit_reason", None) or ""
    if exit_reason and exit_reason not in VALID_EL_EXIT_REASONS:
        err(f"--exit-reason must be one of: {', '.join(VALID_EL_EXIT_REASONS)}")

    prog_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO sr_el_program
               (id, student_id, school_year, program_type, entry_date, exit_date,
                exit_reason, english_proficiency_assessed_date, proficiency_level,
                proficiency_instrument, is_parent_waived, waiver_date,
                company_id, created_at, updated_at, created_by)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (prog_id, student_id, int(school_year), program_type,
             entry_date or "",
             getattr(args, "exit_date", None) or "",
             exit_reason,
             getattr(args, "english_proficiency_assessed_date", None) or "",
             getattr(args, "proficiency_level", None) or "",
             proficiency_instrument,
             int(getattr(args, "is_parent_waived", None) or 0),
             getattr(args, "waiver_date", None) or "",
             company_id, now, now, getattr(args, "user_id", None) or "")
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        err(f"Cannot create EL program: {e}")

    audit(conn, "sr_el_program", prog_id, "INSERT", getattr(args, "user_id", None) or "")
    ok({"id": prog_id, "student_id": student_id, "school_year": int(school_year),
        "message": "EL program enrollment added"})


def update_el_program(conn, args):
    el_program_id = getattr(args, "el_program_id", None)
    if not el_program_id:
        err("--el-program-id is required")

    row = conn.execute("SELECT id FROM sr_el_program WHERE id = ?", (el_program_id,)).fetchone()
    if not row:
        err(f"EL program {el_program_id} not found")

    updates = {}
    for field in [
        "program_type", "entry_date", "exit_date", "exit_reason",
        "english_proficiency_assessed_date", "proficiency_level",
        "proficiency_instrument", "is_parent_waived", "waiver_date"
    ]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    if not updates:
        err("No fields to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE sr_el_program SET {set_clause} WHERE id = ?",
        list(updates.values()) + [el_program_id]
    )
    conn.commit()
    audit(conn, "sr_el_program", el_program_id, "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": el_program_id, "message": "EL program updated"})


def get_el_program(conn, args):
    el_program_id = getattr(args, "el_program_id", None)
    student_id = getattr(args, "student_id", None)
    school_year = getattr(args, "school_year", None)

    if el_program_id:
        row = conn.execute("SELECT * FROM sr_el_program WHERE id = ?", (el_program_id,)).fetchone()
    elif student_id and school_year:
        row = conn.execute(
            "SELECT * FROM sr_el_program WHERE student_id = ? AND school_year = ?",
            (student_id, int(school_year))
        ).fetchone()
    elif student_id:
        row = conn.execute(
            "SELECT * FROM sr_el_program WHERE student_id = ? ORDER BY school_year DESC LIMIT 1",
            (student_id,)
        ).fetchone()
    else:
        err("--el-program-id or --student-id required")

    if not row:
        err("EL program record not found")

    ok(dict(row))


def list_el_programs(conn, args):
    company_id = getattr(args, "company_id", None)
    if not company_id:
        err("--company-id is required")

    conditions = ["company_id = ?"]
    params = [company_id]

    school_year = getattr(args, "school_year", None)
    if school_year:
        conditions.append("school_year = ?")
        params.append(int(school_year))

    program_type = getattr(args, "program_type", None)
    if program_type:
        conditions.append("program_type = ?")
        params.append(program_type)

    active_only = getattr(args, "active_only", None)
    if active_only and str(active_only).lower() in ("1", "true", "yes"):
        conditions.append("exit_date = ''")

    where = " AND ".join(conditions)
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)

    rows = conn.execute(
        f"SELECT * FROM sr_el_program WHERE {where} ORDER BY school_year DESC, entry_date LIMIT ? OFFSET ?",
        params + [limit, offset]
    ).fetchall()

    ok({"programs": [dict(r) for r in rows], "count": len(rows)})


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────
ACTIONS = {
    "add-student-supplement": add_student_supplement,
    "update-student-supplement": update_student_supplement,
    "get-student-supplement": get_student_supplement,
    "list-student-supplements": list_student_supplements,
    "assign-ssid": assign_ssid,
    "update-student-race": set_student_race,
    "update-el-status": update_el_status,
    "update-sped-status": update_sped_status,
    "update-economic-status": update_economic_status,
    "add-sped-placement": add_sped_placement,
    "update-sped-placement": update_sped_placement,
    "get-sped-placement": get_sped_placement,
    "list-sped-placements": list_sped_placements,
    "add-sped-service": add_sped_service,
    "update-sped-service": update_sped_service,
    "list-sped-services": list_sped_services,
    "delete-sped-service": delete_sped_service,
    "add-el-program": add_el_program,
    "update-el-program": update_el_program,
    "get-el-program": get_el_program,
    "list-el-programs": list_el_programs,
}
