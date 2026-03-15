"""EduClaw K-12 — grade_promotion domain module

Actions: create-promotion-review, update-promotion-review, list-promotion-reviews,
submit-promotion-decision, get-promotion-decision, add-promotion-notification,
apply-grade-promotion, create-intervention-plan, update-intervention-plan,
list-intervention-plans, list-at-risk-students, generate-promotion-report

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

# Grade level progression map
GRADE_PROGRESSION = {
    "K": "1", "KINDERGARTEN": "1",
    "1": "2", "2": "3", "3": "4", "4": "5", "5": "6",
    "6": "7", "7": "8", "8": "9", "9": "10",
    "10": "11", "11": "12",
    "12": None,  # 12th grade → graduated
}



def _parse_json(value, default=None):
    if value is None:
        return default if default is not None else []
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return default if default is not None else []


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: create-promotion-review
# ─────────────────────────────────────────────────────────────────────────────

def create_promotion_review(conn, args):
    """Create end-of-year promotion review; pre-populate with GPA/attendance/discipline."""
    student_id = getattr(args, "student_id", None) or None
    academic_year_id = getattr(args, "academic_year_id", None) or None
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    created_by = getattr(args, "user_id", None) or ""

    if not student_id:
        return err("--student-id is required")
    if not academic_year_id:
        return err("--academic-year-id is required")

    student = conn.execute(
        "SELECT id, grade_level, cumulative_gpa, company_id FROM educlaw_student WHERE id = ?",
        (student_id,)
    ).fetchone()
    if not student:
        return err(f"Student {student_id} not found")

    if not conn.execute(
        "SELECT id FROM educlaw_academic_year WHERE id = ?", (academic_year_id,)
    ).fetchone():
        return err(f"Academic year {academic_year_id} not found")

    # Check uniqueness: one review per student per year
    existing = conn.execute(
        """SELECT id FROM educlaw_k12_promotion_review
           WHERE student_id = ? AND academic_year_id = ?""",
        (student_id, academic_year_id)
    ).fetchone()
    if existing:
        return err(
            f"Promotion review already exists for student {student_id} "
            f"in academic year {academic_year_id}"
        )

    grade_level = getattr(args, "grade_level", None) or student["grade_level"] or ""
    review_date = getattr(args, "review_date", None) or datetime.now().strftime("%Y-%m-%d")

    # Pre-populate GPA from student record (or args override)
    gpa_ytd = getattr(args, "gpa_ytd", None) or student["cumulative_gpa"] or ""
    attendance_rate_ytd = getattr(args, "attendance_rate_ytd", None) or ""
    failing_subjects = getattr(args, "failing_subjects", None) or "[]"

    # Auto-populate discipline incident count from discipline_student records
    discipline_count_arg = getattr(args, "discipline_incident_count", None)
    if discipline_count_arg is not None:
        discipline_incident_count = int(discipline_count_arg)
    else:
        # Count discipline incidents where student is offender in this academic year
        count_row = conn.execute(
            """SELECT COUNT(DISTINCT di.id) as cnt
               FROM educlaw_k12_discipline_student ds
               JOIN educlaw_k12_discipline_incident di ON ds.incident_id = di.id
               WHERE ds.student_id = ?
                 AND di.academic_year_id = ?
                 AND ds.role = 'offender'""",
            (student_id, academic_year_id)
        ).fetchone()
        discipline_incident_count = count_row["cnt"] if count_row else 0

    # Check if student has active IEP
    active_iep = conn.execute(
        "SELECT id FROM educlaw_k12_iep WHERE student_id = ? AND iep_status = 'active'",
        (student_id,)
    ).fetchone()
    is_idea_eligible = 1 if active_iep else 0

    prior_retention_count = int(getattr(args, "prior_retention_count", None) or 0)
    interventions_tried = getattr(args, "interventions_tried", None) or "[]"
    teacher_recommendation = getattr(args, "teacher_recommendation", None) or "pending"
    teacher_rationale = getattr(args, "teacher_rationale", None) or ""
    counselor_recommendation = getattr(args, "counselor_recommendation", None) or "pending"
    counselor_notes = getattr(args, "counselor_notes", None) or ""

    now = _now_iso()
    review_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_promotion_review
           (id, student_id, academic_year_id, grade_level, review_date,
            gpa_ytd, attendance_rate_ytd, failing_subjects, discipline_incident_count,
            teacher_recommendation, teacher_rationale, counselor_recommendation,
            counselor_notes, is_idea_eligible, prior_retention_count,
            interventions_tried, review_status, company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?)""",
        (review_id, student_id, academic_year_id, grade_level, review_date,
         gpa_ytd, attendance_rate_ytd, failing_subjects, discipline_incident_count,
         teacher_recommendation, teacher_rationale, counselor_recommendation,
         counselor_notes, is_idea_eligible, prior_retention_count,
         interventions_tried, company_id, now, now, created_by)
    )
    conn.commit()
    audit(conn, SKILL, "create-promotion-review", "educlaw_k12_promotion_review", review_id)
    return ok({
        "id": review_id,
        "student_id": student_id,
        "grade_level": grade_level,
        "review_status": "pending",
        "discipline_incident_count": discipline_incident_count,
        "is_idea_eligible": bool(is_idea_eligible),
        "message": "Promotion review created",
    })



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: update-promotion-review
# ─────────────────────────────────────────────────────────────────────────────

def update_promotion_review(conn, args):
    """Update teacher/counselor recommendations, failing subjects, interventions tried."""
    review_id = getattr(args, "review_id", None) or None
    if not review_id:
        return err("--review-id is required")

    if not conn.execute(
        "SELECT id FROM educlaw_k12_promotion_review WHERE id = ?", (review_id,)
    ).fetchone():
        return err(f"Promotion review {review_id} not found")

    updates = {}
    str_fields = [
        "grade_level", "review_date", "gpa_ytd", "attendance_rate_ytd",
        "failing_subjects", "teacher_recommendation", "teacher_rationale",
        "counselor_recommendation", "counselor_notes", "interventions_tried",
        "review_status",
    ]
    for field in str_fields:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    for int_field in ["discipline_incident_count", "is_idea_eligible", "prior_retention_count"]:
        val = getattr(args, int_field, None)
        if val is not None:
            updates[int_field] = int(val)

    if not updates:
        return err("No fields provided to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE educlaw_k12_promotion_review SET {set_clause} WHERE id = ?",
        list(updates.values()) + [review_id]
    )
    conn.commit()
    audit(conn, SKILL, "update-promotion-review", "educlaw_k12_promotion_review", review_id)
    return ok({"id": review_id, "message": "Promotion review updated"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-promotion-reviews
# ─────────────────────────────────────────────────────────────────────────────

def list_promotion_reviews(conn, args):
    """List all promotion reviews for an academic year, filterable by grade level and status."""
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    academic_year_id = getattr(args, "academic_year_id", None) or None
    grade_level = getattr(args, "grade_level", None) or None
    review_status = getattr(args, "review_status", None) or None
    limit = getattr(args, "limit", None) or 100
    offset = getattr(args, "offset", None) or 0

    query = """SELECT pr.*, s.full_name, s.first_name, s.last_name
               FROM educlaw_k12_promotion_review pr
               JOIN educlaw_student s ON pr.student_id = s.id
               WHERE pr.company_id = ?"""
    params = [company_id]

    if academic_year_id:
        query += " AND pr.academic_year_id = ?"
        params.append(academic_year_id)
    if grade_level:
        query += " AND pr.grade_level = ?"
        params.append(grade_level)
    if review_status:
        query += " AND pr.review_status = ?"
        params.append(review_status)

    query += " ORDER BY pr.grade_level, s.last_name, s.first_name LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()
    return ok({"reviews": rows_to_list(rows), "count": len(rows)})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: submit-promotion-decision
# ─────────────────────────────────────────────────────────────────────────────

def submit_promotion_decision(conn, args):
    """Create immutable promotion decision; update promotion_review status to decided."""
    promotion_review_id = getattr(args, "promotion_review_id", None) or None
    decision = getattr(args, "decision", None) or None
    decided_by = getattr(args, "decided_by", None) or ""
    rationale = getattr(args, "rationale", None) or ""
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    created_by = getattr(args, "user_id", None) or ""

    if not promotion_review_id:
        return err("--promotion-review-id is required")
    if not decision:
        return err("--decision is required (promote/retain/conditional_promote)")

    review = conn.execute(
        "SELECT * FROM educlaw_k12_promotion_review WHERE id = ?",
        (promotion_review_id,)
    ).fetchone()
    if not review:
        return err(f"Promotion review {promotion_review_id} not found")

    # Check for existing decision (one per review)
    existing = conn.execute(
        "SELECT id FROM educlaw_k12_promotion_decision WHERE promotion_review_id = ?",
        (promotion_review_id,)
    ).fetchone()
    if existing:
        return err(f"Promotion decision already exists for review {promotion_review_id}")

    student_id = review["student_id"]
    academic_year_id = review["academic_year_id"]

    decision_date = getattr(args, "decision_date", None) or datetime.now().strftime("%Y-%m-%d")
    team_members = getattr(args, "team_members_json", None) or "[]"
    conditions = getattr(args, "conditions", None) or ""
    parent_notified_date = getattr(args, "parent_notified_date", None) or ""
    parent_notified_by = getattr(args, "parent_notified_by", None) or ""
    notification_method = getattr(args, "notification_method", None) or "letter"
    appeal_deadline = getattr(args, "appeal_deadline", None) or ""
    next_grade_level = getattr(args, "next_grade_level", None) or ""

    # Auto-calculate next_grade_level for promote decisions
    if decision == "promote" and not next_grade_level:
        current_grade = review["grade_level"] or ""
        next_grade_level = GRADE_PROGRESSION.get(current_grade.upper(), "") or ""

    now = _now_iso()
    decision_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_promotion_decision
           (id, promotion_review_id, student_id, academic_year_id, decision,
            decision_date, decided_by, rationale, team_members, conditions,
            parent_notified_date, parent_notified_by, notification_method,
            appeal_deadline, is_appealed, appeal_filed_date,
            appeal_outcome, appeal_decision_date, next_grade_level,
            company_id, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, '', 'not_applicable', '',
                   ?, ?, ?, ?)""",
        (decision_id, promotion_review_id, student_id, academic_year_id, decision,
         decision_date, decided_by, rationale, team_members, conditions,
         parent_notified_date, parent_notified_by, notification_method,
         appeal_deadline, next_grade_level, company_id, now, created_by)
    )

    # Update review status to decided
    conn.execute(
        "UPDATE educlaw_k12_promotion_review SET review_status = 'decided', updated_at = ? "
        "WHERE id = ?",
        (now, promotion_review_id)
    )
    conn.commit()
    audit(conn, SKILL, "submit-promotion-decision", "educlaw_k12_promotion_decision",
          decision_id, description=f"Decision: {decision} for student {student_id}")
    return ok({
        "id": decision_id,
        "decision": decision,
        "decision_date": decision_date,
        "next_grade_level": next_grade_level,
        "message": "Promotion decision recorded",
    })



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: get-promotion-decision
# ─────────────────────────────────────────────────────────────────────────────

def get_promotion_decision(conn, args):
    """Get promotion decision for a student in a given academic year."""
    student_id = getattr(args, "student_id", None) or None
    academic_year_id = getattr(args, "academic_year_id", None) or None
    decision_id = getattr(args, "decision_id", None) or None

    if decision_id:
        row = conn.execute(
            "SELECT * FROM educlaw_k12_promotion_decision WHERE id = ?",
            (decision_id,)
        ).fetchone()
    elif student_id and academic_year_id:
        row = conn.execute(
            """SELECT pd.* FROM educlaw_k12_promotion_decision pd
               WHERE pd.student_id = ? AND pd.academic_year_id = ?
               ORDER BY pd.created_at DESC LIMIT 1""",
            (student_id, academic_year_id)
        ).fetchone()
    elif student_id:
        row = conn.execute(
            "SELECT * FROM educlaw_k12_promotion_decision WHERE student_id = ? "
            "ORDER BY created_at DESC LIMIT 1",
            (student_id,)
        ).fetchone()
    else:
        return err("--decision-id or --student-id is required")

    if not row:
        return err("Promotion decision not found")

    data = row_to_dict(row)
    data["team_members"] = _parse_json(data.get("team_members"), [])

    # Include the linked review
    review = conn.execute(
        "SELECT * FROM educlaw_k12_promotion_review WHERE id = ?",
        (data["promotion_review_id"],)
    ).fetchone()
    data["review"] = row_to_dict(review) if review else None
    return ok(data)



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-promotion-notification
# ─────────────────────────────────────────────────────────────────────────────

def notify_promotion_decision(conn, args):
    """Create educlaw_notification records for guardians; update parent_notified_date."""
    decision_id = getattr(args, "decision_id", None) or None
    user_id = getattr(args, "user_id", None) or ""

    if not decision_id:
        return err("--decision-id is required")

    decision = conn.execute(
        "SELECT * FROM educlaw_k12_promotion_decision WHERE id = ?",
        (decision_id,)
    ).fetchone()
    if not decision:
        return err(f"Promotion decision {decision_id} not found")

    d = row_to_dict(decision)
    student_id = d["student_id"]
    company_id = d["company_id"]
    decision_value = d["decision"]
    next_grade = d["next_grade_level"]

    # Get student name
    student = conn.execute(
        "SELECT full_name FROM educlaw_student WHERE id = ?", (student_id,)
    ).fetchone()
    student_name = student["full_name"] if student else ""

    # Get guardians
    guardians = conn.execute(
        """SELECT sg.guardian_id FROM educlaw_student_guardian sg
           WHERE sg.student_id = ? AND sg.receives_communications = 1""",
        (student_id,)
    ).fetchall()

    now = _now_iso()
    today = datetime.now().strftime("%Y-%m-%d")
    notifications_created = 0

    decision_labels = {
        "promote": "Promoted to next grade",
        "retain": "Retained in current grade",
        "conditional_promote": "Conditionally promoted",
    }
    label = decision_labels.get(decision_value, decision_value)
    title = f"Grade Promotion Decision — {student_name}"
    message_text = getattr(args, "message", None) or (
        f"The promotion decision for {student_name} has been finalized: {label}. "
        + (f"Next grade level: {next_grade}. " if next_grade else "")
        + "Please contact the school with any questions."
    )

    for g_row in guardians:
        notif_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO educlaw_notification
               (id, recipient_type, recipient_id, notification_type, title, message,
                reference_type, reference_id, is_read, sent_via, sent_at,
                company_id, created_at, created_by)
               VALUES (?, 'guardian', ?, 'announcement', ?, ?,
                       'promotion_decision', ?, 0, 'system', ?, ?, ?, ?)""",
            (notif_id, g_row["guardian_id"], title, message_text,
             decision_id, now, company_id, now, user_id)
        )
        notifications_created += 1

    # Update parent_notified_date on decision
    notified_date = getattr(args, "parent_notified_date", None) or today
    notified_by = getattr(args, "parent_notified_by", None) or user_id
    conn.execute(
        """UPDATE educlaw_k12_promotion_decision
           SET parent_notified_date = ?, parent_notified_by = ?
           WHERE id = ?""",
        (notified_date, notified_by, decision_id)
    )

    # Update review status to notified
    conn.execute(
        "UPDATE educlaw_k12_promotion_review SET review_status = 'notified', updated_at = ? "
        "WHERE id = ?",
        (now, d["promotion_review_id"])
    )

    conn.commit()
    return ok({
        "decision_id": decision_id,
        "notifications_created": notifications_created,
        "parent_notified_date": notified_date,
        "message": f"Created {notifications_created} guardian notification(s)",
    })



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: apply-grade-promotion
# ─────────────────────────────────────────────────────────────────────────────

def batch_promote_grade(conn, args):
    """Advance all students with decision='promote' in an academic year.

    Idempotent: checks current grade_level before incrementing.
    12th graders with promote decision → status='graduated'.
    """
    academic_year_id = getattr(args, "academic_year_id", None) or None
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    dry_run = getattr(args, "dry_run", None) or False

    if not academic_year_id:
        return err("--academic-year-id is required")

    # Get all promote decisions for this academic year
    decisions = conn.execute(
        """SELECT pd.student_id, pd.next_grade_level, pd.id AS decision_id,
                  s.grade_level AS current_grade, s.status AS current_status
           FROM educlaw_k12_promotion_decision pd
           JOIN educlaw_student s ON pd.student_id = s.id
           WHERE pd.academic_year_id = ?
             AND pd.decision = 'promote'
             AND pd.company_id = ?""",
        (academic_year_id, company_id)
    ).fetchall()

    promoted_count = 0
    graduated_count = 0
    skipped_count = 0
    results = []

    now = _now_iso()
    for row in decisions:
        student_id = row["student_id"]
        current_grade = (row["current_grade"] or "").upper().strip()
        next_grade = row["next_grade_level"] or ""
        current_status = row["current_status"] or ""

        # 12th grade promotion → graduated
        if current_grade == "12":
            if current_status == "graduated":
                skipped_count += 1
                results.append({
                    "student_id": student_id,
                    "action": "skipped",
                    "reason": "already_graduated",
                })
                continue
            if not dry_run:
                conn.execute(
                    """UPDATE educlaw_student
                       SET status = 'graduated', grade_level = '12', updated_at = ?
                       WHERE id = ?""",
                    (now, student_id)
                )
            graduated_count += 1
            results.append({
                "student_id": student_id,
                "action": "graduated",
                "from_grade": "12",
                "to_status": "graduated",
            })
        else:
            # Advance grade level
            expected_next = GRADE_PROGRESSION.get(current_grade, "")
            if not next_grade:
                next_grade = expected_next or ""

            if not next_grade:
                skipped_count += 1
                results.append({
                    "student_id": student_id,
                    "action": "skipped",
                    "reason": "no_next_grade_defined",
                })
                continue

            # Idempotency check: if student is already at next_grade, skip
            if current_grade == next_grade:
                skipped_count += 1
                results.append({
                    "student_id": student_id,
                    "action": "skipped",
                    "reason": "already_at_target_grade",
                })
                continue

            if not dry_run:
                conn.execute(
                    "UPDATE educlaw_student SET grade_level = ?, updated_at = ? WHERE id = ?",
                    (next_grade, now, student_id)
                )
            promoted_count += 1
            results.append({
                "student_id": student_id,
                "action": "promoted",
                "from_grade": current_grade,
                "to_grade": next_grade,
            })

    if not dry_run:
        conn.commit()

    return ok({
        "academic_year_id": academic_year_id,
        "dry_run": bool(dry_run),
        "promoted_count": promoted_count,
        "graduated_count": graduated_count,
        "skipped_count": skipped_count,
        "total_processed": len(decisions),
        "details": results,
        "message": (
            f"{'[DRY RUN] ' if dry_run else ''}"
            f"Processed {len(decisions)} students: "
            f"{promoted_count} promoted, {graduated_count} graduated, {skipped_count} skipped"
        ),
    })



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: create-intervention-plan
# ─────────────────────────────────────────────────────────────────────────────

def create_intervention_plan(conn, args):
    """Create at-risk intervention plan for a student."""
    student_id = getattr(args, "student_id", None) or None
    academic_year_id = getattr(args, "academic_year_id", None) or None
    trigger = getattr(args, "trigger", None) or None
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    created_by = getattr(args, "user_id", None) or ""

    if not student_id:
        return err("--student-id is required")
    if not academic_year_id:
        return err("--academic-year-id is required")
    if not trigger:
        return err("--trigger is required (at_risk_mid_year/retention_decision/other)")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        return err(f"Student {student_id} not found")

    if not conn.execute(
        "SELECT id FROM educlaw_academic_year WHERE id = ?", (academic_year_id,)
    ).fetchone():
        return err(f"Academic year {academic_year_id} not found")

    promotion_review_id = getattr(args, "promotion_review_id", None) or None
    if promotion_review_id:
        if not conn.execute(
            "SELECT id FROM educlaw_k12_promotion_review WHERE id = ?",
            (promotion_review_id,)
        ).fetchone():
            return err(f"Promotion review {promotion_review_id} not found")

    intervention_types = getattr(args, "intervention_types", None) or "[]"
    academic_targets = getattr(args, "academic_targets", None) or ""
    attendance_target = getattr(args, "attendance_target", None) or ""
    assigned_staff = getattr(args, "assigned_staff", None) or ""
    start_date = getattr(args, "start_date", None) or ""
    review_date = getattr(args, "review_date", None) or ""
    parent_notification_date = getattr(args, "parent_notification_date", None) or ""
    outcome_notes = getattr(args, "outcome_notes", None) or ""

    now = _now_iso()
    plan_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_k12_intervention_plan
           (id, student_id, academic_year_id, promotion_review_id, trigger,
            intervention_types, academic_targets, attendance_target, assigned_staff,
            start_date, review_date, parent_notification_date, plan_status,
            outcome_notes, company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, ?, ?)""",
        (plan_id, student_id, academic_year_id, promotion_review_id, trigger,
         intervention_types, academic_targets, attendance_target, assigned_staff,
         start_date, review_date, parent_notification_date, outcome_notes,
         company_id, now, now, created_by)
    )
    conn.commit()
    audit(conn, SKILL, "create-intervention-plan", "educlaw_k12_intervention_plan", plan_id)
    return ok({"id": plan_id, "trigger": trigger, "plan_status": "active",
               "message": "Intervention plan created"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: update-intervention-plan
# ─────────────────────────────────────────────────────────────────────────────

def update_intervention_plan(conn, args):
    """Update intervention plan status, outcome notes, review date."""
    plan_id = getattr(args, "intervention_plan_id", None) or None
    if not plan_id:
        return err("--intervention-plan-id is required")

    if not conn.execute(
        "SELECT id FROM educlaw_k12_intervention_plan WHERE id = ?", (plan_id,)
    ).fetchone():
        return err(f"Intervention plan {plan_id} not found")

    updates = {}
    for field in ["intervention_types", "academic_targets", "attendance_target",
                  "assigned_staff", "start_date", "review_date",
                  "parent_notification_date", "plan_status", "outcome_notes"]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    if not updates:
        return err("No fields provided to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE educlaw_k12_intervention_plan SET {set_clause} WHERE id = ?",
        list(updates.values()) + [plan_id]
    )
    conn.commit()
    audit(conn, SKILL, "update-intervention-plan", "educlaw_k12_intervention_plan", plan_id)
    return ok({"id": plan_id, "message": "Intervention plan updated"})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-intervention-plans
# ─────────────────────────────────────────────────────────────────────────────

def list_intervention_plans(conn, args):
    """List intervention plans by academic year, status, or student."""
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    student_id = getattr(args, "student_id", None) or None
    academic_year_id = getattr(args, "academic_year_id", None) or None
    plan_status = getattr(args, "plan_status", None) or None
    limit = getattr(args, "limit", None) or 100
    offset = getattr(args, "offset", None) or 0

    query = "SELECT * FROM educlaw_k12_intervention_plan WHERE company_id = ?"
    params = [company_id]

    if student_id:
        query += " AND student_id = ?"
        params.append(student_id)
    if academic_year_id:
        query += " AND academic_year_id = ?"
        params.append(academic_year_id)
    if plan_status:
        query += " AND plan_status = ?"
        params.append(plan_status)

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()
    result = rows_to_list(rows)
    for r in result:
        r["intervention_types"] = _parse_json(r.get("intervention_types"), [])
    return ok({"plans": result, "count": len(result)})



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-at-risk-students
# ─────────────────────────────────────────────────────────────────────────────

def identify_at_risk_students(conn, args):
    """Flag students below GPA/attendance thresholds or failing required subjects."""
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    academic_year_id = getattr(args, "academic_year_id", None) or None
    gpa_threshold = getattr(args, "gpa_threshold", None) or "2.0"
    attendance_threshold = getattr(args, "attendance_threshold", None) or "90.0"
    grade_level = getattr(args, "grade_level", None) or None

    try:
        gpa_thresh = to_decimal(gpa_threshold)
    except Exception:
        gpa_thresh = to_decimal("2.0")

    try:
        att_thresh = to_decimal(attendance_threshold)
    except Exception:
        att_thresh = to_decimal("90.0")

    # Get all active students for this company
    query = "SELECT * FROM educlaw_student WHERE company_id = ? AND status = 'active'"
    params = [company_id]
    if grade_level:
        query += " AND grade_level = ?"
        params.append(grade_level)

    students = conn.execute(query, params).fetchall()

    at_risk = []
    for student in students:
        sid = student["id"]
        flags = []

        # Check GPA
        gpa_str = student["cumulative_gpa"] or ""
        if gpa_str:
            try:
                gpa = to_decimal(gpa_str)
                if gpa < gpa_thresh:
                    flags.append({"type": "low_gpa", "value": str(gpa),
                                  "threshold": str(gpa_thresh)})
            except Exception:
                pass

        # Check attendance (from promotion_review if available)
        review = None
        if academic_year_id:
            review = conn.execute(
                """SELECT gpa_ytd, attendance_rate_ytd, failing_subjects
                   FROM educlaw_k12_promotion_review
                   WHERE student_id = ? AND academic_year_id = ?""",
                (sid, academic_year_id)
            ).fetchone()

        if review:
            if review["attendance_rate_ytd"]:
                try:
                    att = to_decimal(review["attendance_rate_ytd"])
                    if att < att_thresh:
                        flags.append({"type": "low_attendance", "value": str(att),
                                      "threshold": str(att_thresh)})
                except Exception:
                    pass

            failing = _parse_json(review["failing_subjects"], [])
            if failing:
                flags.append({"type": "failing_subjects", "subjects": failing,
                               "count": len(failing)})

            # Use review GPA if available
            if review["gpa_ytd"] and not any(f["type"] == "low_gpa" for f in flags):
                try:
                    gpa = to_decimal(review["gpa_ytd"])
                    if gpa < gpa_thresh:
                        flags.append({"type": "low_gpa", "value": str(gpa),
                                      "threshold": str(gpa_thresh)})
                except Exception:
                    pass

        if flags:
            at_risk.append({
                "student_id": sid,
                "full_name": student["full_name"],
                "grade_level": student["grade_level"],
                "risk_flags": flags,
                "risk_count": len(flags),
            })

    at_risk.sort(key=lambda x: x["risk_count"], reverse=True)

    return ok({
        "company_id": company_id,
        "academic_year_id": academic_year_id,
        "gpa_threshold": str(gpa_thresh),
        "attendance_threshold": str(att_thresh),
        "at_risk_students": at_risk,
        "at_risk_count": len(at_risk),
        "total_students_checked": len(students),
    })



# ─────────────────────────────────────────────────────────────────────────────
# ACTION: generate-promotion-report
# ─────────────────────────────────────────────────────────────────────────────

def generate_promotion_report(conn, args):
    """Summary by grade: count of promote/retain/conditional; intervention plan coverage."""
    company_id = resolve_company_id(conn, getattr(args, "company_id", None) or None)
    academic_year_id = getattr(args, "academic_year_id", None) or None

    if not academic_year_id:
        return err("--academic-year-id is required")

    # Decision breakdown by grade level
    decisions = conn.execute(
        """SELECT pr.grade_level, pd.decision, COUNT(*) as cnt
           FROM educlaw_k12_promotion_decision pd
           JOIN educlaw_k12_promotion_review pr ON pd.promotion_review_id = pr.id
           WHERE pd.company_id = ? AND pd.academic_year_id = ?
           GROUP BY pr.grade_level, pd.decision
           ORDER BY pr.grade_level, pd.decision""",
        (company_id, academic_year_id)
    ).fetchall()

    by_grade = {}
    for row in decisions:
        grade = row["grade_level"] or "unknown"
        if grade not in by_grade:
            by_grade[grade] = {"grade_level": grade, "promote": 0, "retain": 0,
                                "conditional_promote": 0, "total": 0}
        by_grade[grade][row["decision"]] = row["cnt"]
        by_grade[grade]["total"] += row["cnt"]

    # Total reviews
    total_reviews = conn.execute(
        """SELECT COUNT(*) as cnt FROM educlaw_k12_promotion_review
           WHERE company_id = ? AND academic_year_id = ?""",
        (company_id, academic_year_id)
    ).fetchone()["cnt"]

    # Decided reviews
    decided = conn.execute(
        """SELECT COUNT(*) as cnt FROM educlaw_k12_promotion_decision
           WHERE company_id = ? AND academic_year_id = ?""",
        (company_id, academic_year_id)
    ).fetchone()["cnt"]

    # Intervention plan coverage (students with retention decisions that have a plan)
    retain_count = conn.execute(
        """SELECT COUNT(*) as cnt FROM educlaw_k12_promotion_decision
           WHERE company_id = ? AND academic_year_id = ? AND decision = 'retain'""",
        (company_id, academic_year_id)
    ).fetchone()["cnt"]

    retain_with_plan = conn.execute(
        """SELECT COUNT(DISTINCT pd.student_id) as cnt
           FROM educlaw_k12_promotion_decision pd
           JOIN educlaw_k12_intervention_plan ip ON pd.student_id = ip.student_id
             AND ip.academic_year_id = pd.academic_year_id
           WHERE pd.company_id = ? AND pd.academic_year_id = ? AND pd.decision = 'retain'""",
        (company_id, academic_year_id)
    ).fetchone()["cnt"]

    return ok({
        "company_id": company_id,
        "academic_year_id": academic_year_id,
        "total_reviews": total_reviews,
        "total_decided": decided,
        "by_grade_level": list(by_grade.values()),
        "retained_students": retain_count,
        "retained_with_intervention_plan": retain_with_plan,
        "intervention_plan_coverage_rate": (
            f"{retain_with_plan / retain_count * 100:.1f}%"
            if retain_count > 0 else "N/A"
        ),
    })


# ─── ACTIONS registry ────────────────────────────────────────────────────────
ACTIONS = {
    "create-promotion-review": create_promotion_review,
    "update-promotion-review": update_promotion_review,
    "list-promotion-reviews": list_promotion_reviews,
    "submit-promotion-decision": submit_promotion_decision,
    "get-promotion-decision": get_promotion_decision,
    "add-promotion-notification": notify_promotion_decision,
    "apply-grade-promotion": batch_promote_grade,
    "create-intervention-plan": create_intervention_plan,
    "update-intervention-plan": update_intervention_plan,
    "list-intervention-plans": list_intervention_plans,
    "list-at-risk-students": identify_at_risk_students,
    "generate-promotion-report": generate_promotion_report,
}
