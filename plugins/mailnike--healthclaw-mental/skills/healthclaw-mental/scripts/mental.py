"""HealthClaw Mental — mental health domain module

Actions for the mental health expansion (4 tables, 14 actions).
Imported by db_query.py (unified router).
"""
import json
import os
import sys
import uuid
from decimal import Decimal

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection
    from erpclaw_lib.decimal_utils import to_decimal, round_currency
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
except ImportError:
    pass


# ---- Helpers ----------------------------------------------------------------

def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


VALID_SESSION_TYPES = ("individual", "couples", "family", "group")
VALID_MODALITIES = ("cbt", "dbt", "emdr", "psychodynamic", "supportive", "motivational_interviewing", "other")
VALID_SESSION_STATUSES = ("scheduled", "in_progress", "completed", "cancelled", "no_show")
VALID_INSTRUMENTS = ("PHQ-9", "GAD-7", "AUDIT", "PCL-5", "CSSRS", "PHQ-2", "GAD-2", "DAST-10", "MDQ", "CAGE")
VALID_GOAL_STATUSES = ("active", "achieved", "modified", "discontinued")
VALID_GROUP_TYPES = ("process", "psychoeducation", "support", "skills_training")
VALID_GROUP_STATUSES = ("scheduled", "completed", "cancelled")


def _validate_enum(val, choices, label):
    if val not in choices:
        err(f"Invalid {label}: {val}. Must be one of: {', '.join(choices)}")


def _auto_score_phq9(responses):
    """Auto-score PHQ-9: 9 items, 0-3 each. Returns (score, severity)."""
    if len(responses) != 9:
        return None, None
    for v in responses:
        if not isinstance(v, int) or v < 0 or v > 3:
            return None, None
    score = sum(responses)
    if score <= 4:
        severity = "minimal"
    elif score <= 9:
        severity = "mild"
    elif score <= 14:
        severity = "moderate"
    elif score <= 19:
        severity = "moderately_severe"
    else:
        severity = "severe"
    return score, severity


def _auto_score_gad7(responses):
    """Auto-score GAD-7: 7 items, 0-3 each. Returns (score, severity)."""
    if len(responses) != 7:
        return None, None
    for v in responses:
        if not isinstance(v, int) or v < 0 or v > 3:
            return None, None
    score = sum(responses)
    if score <= 4:
        severity = "minimal"
    elif score <= 9:
        severity = "mild"
    elif score <= 14:
        severity = "moderate"
    else:
        severity = "severe"
    return score, severity


def _auto_score_audit(responses):
    """Auto-score AUDIT: 10 items, score 0-40. Returns (score, severity)."""
    if len(responses) != 10:
        return None, None
    for v in responses:
        if not isinstance(v, int) or v < 0 or v > 4:
            return None, None
    score = sum(responses)
    if score <= 7:
        severity = "low_risk"
    elif score <= 15:
        severity = "hazardous"
    elif score <= 19:
        severity = "harmful"
    else:
        severity = "dependence"
    return score, severity


# ---------------------------------------------------------------------------
# 1. add-therapy-session
# ---------------------------------------------------------------------------
def add_therapy_session(conn, args):
    for req in ("encounter_id", "patient_id", "company_id", "provider_id", "session_type"):
        if not getattr(args, req, None):
            err(f"--{req.replace('_', '-')} is required")

    # Validate encounter exists
    if not conn.execute("SELECT id FROM healthclaw_encounter WHERE id = ?", (args.encounter_id,)).fetchone():
        err(f"Encounter {args.encounter_id} not found")
    # Validate patient exists
    if not conn.execute("SELECT id FROM healthclaw_patient WHERE id = ?", (args.patient_id,)).fetchone():
        err(f"Patient {args.patient_id} not found")
    # Validate provider exists
    if not conn.execute("SELECT id FROM employee WHERE id = ?", (args.provider_id,)).fetchone():
        err(f"Provider {args.provider_id} not found")

    _validate_enum(args.session_type, VALID_SESSION_TYPES, "session-type")

    modality = getattr(args, "modality", None)
    if modality:
        _validate_enum(modality, VALID_MODALITIES, "modality")

    status = getattr(args, "status", None) or "completed"
    _validate_enum(status, VALID_SESSION_STATUSES, "status")

    session_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute(
        """INSERT INTO healthclaw_therapy_session
           (id, company_id, encounter_id, patient_id, provider_id, session_type, modality,
            duration_minutes, session_number, notes, status, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (session_id, args.company_id, args.encounter_id, args.patient_id, args.provider_id,
         args.session_type, modality,
         getattr(args, "duration_minutes", None), getattr(args, "session_number", None),
         getattr(args, "notes", None), status, now, now)
    )
    audit(conn, "healthclaw_therapy_session", session_id, "add-therapy-session", args.company_id)
    conn.commit()
    ok({"id": session_id, "session_type": args.session_type, "session_status": status})


# ---------------------------------------------------------------------------
# 2. update-therapy-session
# ---------------------------------------------------------------------------
def update_therapy_session(conn, args):
    session_id = getattr(args, "therapy_session_id", None)
    if not session_id:
        err("--therapy-session-id is required")
    if not conn.execute("SELECT id FROM healthclaw_therapy_session WHERE id = ?", (session_id,)).fetchone():
        err(f"Therapy session {session_id} not found")

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "notes": "notes",
        "duration_minutes": "duration_minutes",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            updates.append(f"{col_name} = ?"); params.append(val); changed.append(col_name)

    session_type = getattr(args, "session_type", None)
    if session_type:
        _validate_enum(session_type, VALID_SESSION_TYPES, "session-type")
        updates.append("session_type = ?"); params.append(session_type); changed.append("session_type")

    modality = getattr(args, "modality", None)
    if modality:
        _validate_enum(modality, VALID_MODALITIES, "modality")
        updates.append("modality = ?"); params.append(modality); changed.append("modality")

    status = getattr(args, "status", None)
    if status:
        _validate_enum(status, VALID_SESSION_STATUSES, "status")
        updates.append("status = ?"); params.append(status); changed.append("status")

    if not updates:
        err("No fields to update")
    updates.append("updated_at = datetime('now')")
    params.append(session_id)
    conn.execute(f"UPDATE healthclaw_therapy_session SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_therapy_session", session_id, "update-therapy-session", getattr(args, "company_id", None))
    conn.commit()
    ok({"id": session_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 3. list-therapy-sessions
# ---------------------------------------------------------------------------
def list_therapy_sessions(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?"); params.append(args.patient_id)
    if getattr(args, "provider_id", None):
        where.append("provider_id = ?"); params.append(args.provider_id)
    if getattr(args, "status", None):
        where.append("status = ?"); params.append(args.status)
    if getattr(args, "search", None):
        where.append("(notes LIKE ? OR session_type LIKE ? OR modality LIKE ?)")
        s = f"%{args.search}%"
        params.extend([s, s, s])
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_therapy_session WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_therapy_session WHERE {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?", params
    ).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# 4. add-assessment
# ---------------------------------------------------------------------------
def add_assessment(conn, args):
    for req in ("patient_id", "company_id", "instrument", "administered_date"):
        if not getattr(args, req, None):
            err(f"--{req.replace('_', '-')} is required")

    # Validate patient exists
    if not conn.execute("SELECT id FROM healthclaw_patient WHERE id = ?", (args.patient_id,)).fetchone():
        err(f"Patient {args.patient_id} not found")
    # Validate administered_by if provided
    administered_by_id = getattr(args, "administered_by_id", None)
    if administered_by_id:
        if not conn.execute("SELECT id FROM employee WHERE id = ?", (administered_by_id,)).fetchone():
            err(f"Employee {administered_by_id} not found")

    _validate_enum(args.instrument, VALID_INSTRUMENTS, "instrument")

    responses_raw = getattr(args, "responses", None)
    responses_list = None
    if responses_raw:
        try:
            responses_list = json.loads(responses_raw)
        except (json.JSONDecodeError, TypeError):
            err("--responses must be valid JSON array")

    # Auto-scoring
    score = getattr(args, "score", None)
    severity = getattr(args, "severity", None)

    if responses_list is not None and score is None:
        auto_score, auto_severity = None, None
        if args.instrument == "PHQ-9":
            auto_score, auto_severity = _auto_score_phq9(responses_list)
        elif args.instrument == "GAD-7":
            auto_score, auto_severity = _auto_score_gad7(responses_list)
        elif args.instrument == "AUDIT":
            auto_score, auto_severity = _auto_score_audit(responses_list)
        if auto_score is not None:
            score = auto_score
            severity = auto_severity

    # Convert score to int if provided as string
    if score is not None and not isinstance(score, int):
        try:
            score = int(score)
        except (ValueError, TypeError):
            pass

    assessment_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute(
        """INSERT INTO healthclaw_assessment
           (id, company_id, patient_id, administered_by_id, instrument, responses,
            score, severity, administered_date, notes, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (assessment_id, args.company_id, args.patient_id,
         getattr(args, "administered_by_id", None), args.instrument,
         responses_raw, score, severity,
         args.administered_date, getattr(args, "notes", None), now, now)
    )
    audit(conn, "healthclaw_assessment", assessment_id, "add-assessment", args.company_id)
    conn.commit()
    result = {"id": assessment_id, "instrument": args.instrument}
    if score is not None:
        result["score"] = score
    if severity is not None:
        result["severity"] = severity
    ok(result)


# ---------------------------------------------------------------------------
# 5. get-assessment
# ---------------------------------------------------------------------------
def get_assessment(conn, args):
    assessment_id = getattr(args, "assessment_id", None)
    if not assessment_id:
        err("--assessment-id is required")
    row = conn.execute("SELECT * FROM healthclaw_assessment WHERE id = ?", (assessment_id,)).fetchone()
    if not row:
        err(f"Assessment {assessment_id} not found")
    data = row_to_dict(row)
    # Parse JSON fields
    if data.get("responses"):
        try:
            data["responses"] = json.loads(data["responses"])
        except (json.JSONDecodeError, TypeError):
            pass
    ok(data)


# ---------------------------------------------------------------------------
# 6. list-assessments
# ---------------------------------------------------------------------------
def list_assessments(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?"); params.append(args.patient_id)
    if getattr(args, "instrument", None):
        where.append("instrument = ?"); params.append(args.instrument)
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_assessment WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_assessment WHERE {where_sql} ORDER BY administered_date DESC LIMIT ? OFFSET ?", params
    ).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# 7. compare-assessments
# ---------------------------------------------------------------------------
def compare_assessments(conn, args):
    assessment_id_1 = getattr(args, "assessment_id_1", None)
    assessment_id_2 = getattr(args, "assessment_id_2", None)
    if not assessment_id_1 or not assessment_id_2:
        err("--assessment-id-1 and --assessment-id-2 are required")

    row1 = conn.execute("SELECT * FROM healthclaw_assessment WHERE id = ?", (assessment_id_1,)).fetchone()
    row2 = conn.execute("SELECT * FROM healthclaw_assessment WHERE id = ?", (assessment_id_2,)).fetchone()
    if not row1:
        err(f"Assessment {assessment_id_1} not found")
    if not row2:
        err(f"Assessment {assessment_id_2} not found")

    d1, d2 = row_to_dict(row1), row_to_dict(row2)

    # Must be same instrument
    if d1["instrument"] != d2["instrument"]:
        err(f"Cannot compare different instruments: {d1['instrument']} vs {d2['instrument']}")

    # Must be same patient
    if d1["patient_id"] != d2["patient_id"]:
        err(f"Cannot compare assessments for different patients")

    score1 = d1.get("score")
    score2 = d2.get("score")
    score_change = None
    improved = None
    if score1 is not None and score2 is not None:
        score_change = score2 - score1
        # For all these instruments, lower score = improvement
        improved = score_change < 0

    ok({
        "assessment_1": {"id": assessment_id_1, "date": d1.get("administered_date"), "score": score1, "severity": d1.get("severity")},
        "assessment_2": {"id": assessment_id_2, "date": d2.get("administered_date"), "score": score2, "severity": d2.get("severity")},
        "instrument": d1["instrument"],
        "score_change": score_change,
        "severity_change": f"{d1.get('severity')} -> {d2.get('severity')}",
        "improved": improved,
    })


# ---------------------------------------------------------------------------
# 8. add-treatment-goal
# ---------------------------------------------------------------------------
def add_treatment_goal(conn, args):
    for req in ("patient_id", "company_id", "goal_description"):
        if not getattr(args, req, None):
            err(f"--{req.replace('_', '-')} is required")

    # Validate patient exists
    if not conn.execute("SELECT id FROM healthclaw_patient WHERE id = ?", (args.patient_id,)).fetchone():
        err(f"Patient {args.patient_id} not found")
    # Validate provider if provided
    provider_id = getattr(args, "provider_id", None)
    if provider_id:
        if not conn.execute("SELECT id FROM employee WHERE id = ?", (provider_id,)).fetchone():
            err(f"Provider {provider_id} not found")

    goal_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute(
        """INSERT INTO healthclaw_treatment_goal
           (id, company_id, patient_id, provider_id, goal_description, target_date,
            baseline_measure, current_measure, goal_status, notes, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?)""",
        (goal_id, args.company_id, args.patient_id,
         getattr(args, "provider_id", None), args.goal_description,
         getattr(args, "target_date", None), getattr(args, "baseline_measure", None),
         getattr(args, "current_measure", None),
         getattr(args, "notes", None), now, now)
    )
    audit(conn, "healthclaw_treatment_goal", goal_id, "add-treatment-goal", args.company_id)
    conn.commit()
    ok({"id": goal_id, "goal_description": args.goal_description, "goal_status": "active"})


# ---------------------------------------------------------------------------
# 9. update-treatment-goal
# ---------------------------------------------------------------------------
def update_treatment_goal(conn, args):
    goal_id = getattr(args, "treatment_goal_id", None)
    if not goal_id:
        err("--treatment-goal-id is required")
    if not conn.execute("SELECT id FROM healthclaw_treatment_goal WHERE id = ?", (goal_id,)).fetchone():
        err(f"Treatment goal {goal_id} not found")

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "goal_description": "goal_description",
        "target_date": "target_date",
        "current_measure": "current_measure",
        "notes": "notes",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            updates.append(f"{col_name} = ?"); params.append(val); changed.append(col_name)

    goal_status = getattr(args, "goal_status", None)
    if goal_status:
        _validate_enum(goal_status, VALID_GOAL_STATUSES, "goal-status")
        updates.append("goal_status = ?"); params.append(goal_status); changed.append("goal_status")

    if not updates:
        err("No fields to update")
    updates.append("updated_at = datetime('now')")
    params.append(goal_id)
    conn.execute(f"UPDATE healthclaw_treatment_goal SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_treatment_goal", goal_id, "update-treatment-goal", getattr(args, "company_id", None))
    conn.commit()
    ok({"id": goal_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 10. list-treatment-goals
# ---------------------------------------------------------------------------
def list_treatment_goals(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "patient_id", None):
        where.append("patient_id = ?"); params.append(args.patient_id)
    if getattr(args, "goal_status", None):
        where.append("goal_status = ?"); params.append(args.goal_status)
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_treatment_goal WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_treatment_goal WHERE {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?", params
    ).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# 11. add-group-session
# ---------------------------------------------------------------------------
def add_group_session(conn, args):
    for req in ("company_id", "provider_id", "session_date", "group_name"):
        if not getattr(args, req, None):
            err(f"--{req.replace('_', '-')} is required")

    # Validate provider exists
    if not conn.execute("SELECT id FROM employee WHERE id = ?", (args.provider_id,)).fetchone():
        err(f"Provider {args.provider_id} not found")

    group_type = getattr(args, "group_type", None)
    if group_type:
        _validate_enum(group_type, VALID_GROUP_TYPES, "group-type")

    status = getattr(args, "status", None) or "completed"
    _validate_enum(status, VALID_GROUP_STATUSES, "status")

    participant_ids_raw = getattr(args, "participant_ids", None)
    if participant_ids_raw:
        try:
            json.loads(participant_ids_raw)
        except (json.JSONDecodeError, TypeError):
            err("--participant-ids must be valid JSON array")

    session_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute(
        """INSERT INTO healthclaw_group_session
           (id, company_id, provider_id, session_date, group_name, group_type,
            topic, max_participants, participant_ids, duration_minutes, notes, status,
            created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (session_id, args.company_id, args.provider_id, args.session_date, args.group_name,
         group_type, getattr(args, "topic", None),
         getattr(args, "max_participants", 12), participant_ids_raw,
         getattr(args, "duration_minutes", None), getattr(args, "notes", None),
         status, now, now)
    )
    audit(conn, "healthclaw_group_session", session_id, "add-group-session", args.company_id)
    conn.commit()
    ok({"id": session_id, "group_name": args.group_name, "session_status": status})


# ---------------------------------------------------------------------------
# 12. update-group-session
# ---------------------------------------------------------------------------
def update_group_session(conn, args):
    session_id = getattr(args, "group_session_id", None)
    if not session_id:
        err("--group-session-id is required")
    if not conn.execute("SELECT id FROM healthclaw_group_session WHERE id = ?", (session_id,)).fetchone():
        err(f"Group session {session_id} not found")

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "group_name": "group_name",
        "topic": "topic",
        "duration_minutes": "duration_minutes",
        "notes": "notes",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            updates.append(f"{col_name} = ?"); params.append(val); changed.append(col_name)

    group_type = getattr(args, "group_type", None)
    if group_type:
        _validate_enum(group_type, VALID_GROUP_TYPES, "group-type")
        updates.append("group_type = ?"); params.append(group_type); changed.append("group_type")

    status = getattr(args, "status", None)
    if status:
        _validate_enum(status, VALID_GROUP_STATUSES, "status")
        updates.append("status = ?"); params.append(status); changed.append("status")

    participant_ids_raw = getattr(args, "participant_ids", None)
    if participant_ids_raw:
        try:
            json.loads(participant_ids_raw)
        except (json.JSONDecodeError, TypeError):
            err("--participant-ids must be valid JSON array")
        updates.append("participant_ids = ?"); params.append(participant_ids_raw); changed.append("participant_ids")

    max_participants = getattr(args, "max_participants", None)
    if max_participants is not None:
        updates.append("max_participants = ?"); params.append(max_participants); changed.append("max_participants")

    if not updates:
        err("No fields to update")
    updates.append("updated_at = datetime('now')")
    params.append(session_id)
    conn.execute(f"UPDATE healthclaw_group_session SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_group_session", session_id, "update-group-session", getattr(args, "company_id", None))
    conn.commit()
    ok({"id": session_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 13. list-group-sessions
# ---------------------------------------------------------------------------
def list_group_sessions(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "provider_id", None):
        where.append("provider_id = ?"); params.append(args.provider_id)
    if getattr(args, "status", None):
        where.append("status = ?"); params.append(args.status)
    if getattr(args, "search", None):
        where.append("(group_name LIKE ? OR topic LIKE ? OR notes LIKE ?)")
        s = f"%{args.search}%"
        params.extend([s, s, s])
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_group_session WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_group_session WHERE {where_sql} ORDER BY session_date DESC LIMIT ? OFFSET ?", params
    ).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# 14. get-group-session
# ---------------------------------------------------------------------------
def get_group_session(conn, args):
    session_id = getattr(args, "group_session_id", None)
    if not session_id:
        err("--group-session-id is required")
    row = conn.execute("SELECT * FROM healthclaw_group_session WHERE id = ?", (session_id,)).fetchone()
    if not row:
        err(f"Group session {session_id} not found")
    data = row_to_dict(row)
    # Parse JSON fields
    if data.get("participant_ids"):
        try:
            data["participant_ids"] = json.loads(data["participant_ids"])
        except (json.JSONDecodeError, TypeError):
            pass
    ok(data)


# ---------------------------------------------------------------------------
# Action Router
# ---------------------------------------------------------------------------
ACTIONS = {
    "add-therapy-session": add_therapy_session,
    "update-therapy-session": update_therapy_session,
    "list-therapy-sessions": list_therapy_sessions,
    "add-assessment": add_assessment,
    "get-assessment": get_assessment,
    "list-assessments": list_assessments,
    "compare-assessments": compare_assessments,
    "add-treatment-goal": add_treatment_goal,
    "update-treatment-goal": update_treatment_goal,
    "list-treatment-goals": list_treatment_goals,
    "add-group-session": add_group_session,
    "update-group-session": update_group_session,
    "list-group-sessions": list_group_sessions,
    "get-group-session": get_group_session,
}
