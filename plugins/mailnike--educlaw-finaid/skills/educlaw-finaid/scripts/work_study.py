"""EduClaw Financial Aid — work_study domain module

Actions for the work_study domain: job postings, student assignments,
timesheets, payroll export, and earnings summaries.

Imported by db_query.py (unified router).
"""
import csv
import io
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection
    from erpclaw_lib.decimal_utils import to_decimal, round_currency
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
except ImportError:
    pass

SKILL = "educlaw-finaid"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
_today = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# WORK STUDY JOB
# ---------------------------------------------------------------------------

def add_work_study_job(conn, args):
    company_id = getattr(args, "company_id", None)
    aid_year_id = getattr(args, "aid_year_id", None)
    job_title = getattr(args, "job_title", None)
    job_type = getattr(args, "job_type", None)
    pay_rate = getattr(args, "pay_rate", None)
    total_positions = getattr(args, "total_positions", None)

    if not company_id:
        err("--company-id is required")
    if not aid_year_id:
        err("--aid-year-id is required")
    if not job_title:
        err("--job-title is required")
    if not job_type:
        err("--job-type is required")
    if job_type not in ("on_campus", "off_campus_community", "off_campus_other"):
        err("--job-type must be on_campus, off_campus_community, or off_campus_other")
    if not pay_rate:
        err("--pay-rate is required")
    if not total_positions:
        err("--total-positions is required")

    department_id = getattr(args, "department_id", None) or ""
    supervisor_id = getattr(args, "supervisor_id", None) or ""
    description = getattr(args, "description", None) or ""
    hours_per_week = getattr(args, "hours_per_week", None) or "0"

    job_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO finaid_work_study_job
               (id, job_title, department_id, supervisor_id, job_type, description,
                pay_rate, hours_per_week, total_positions, filled_positions,
                aid_year_id, status, company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (job_id, job_title, department_id, supervisor_id, job_type, description,
             str(to_decimal(pay_rate)), str(to_decimal(hours_per_week)),
             int(total_positions), 0,
             aid_year_id, "open", company_id, now, now,
             getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Failed to create work study job: {e}")

    audit(conn, SKILL, "add-work-study-job", "finaid_work_study_job", job_id,
          new_values={"job_title": job_title, "job_type": job_type, "status": "open"})
    conn.commit()
    ok({
        "id": job_id,
        "job_title": job_title,
        "job_type": job_type,
        "pay_rate": str(to_decimal(pay_rate)),
        "total_positions": int(total_positions),
        "status": "open",
        "company_id": company_id,
    })


def update_work_study_job(conn, args):
    job_id = getattr(args, "id", None)
    if not job_id:
        err("--id is required")

    row = conn.execute(
        "SELECT * FROM finaid_work_study_job WHERE id = ?", (job_id,)
    ).fetchone()
    if not row:
        err(f"Work study job {job_id} not found")

    updates, params, changed = [], [], []

    if getattr(args, "job_title", None) is not None:
        updates.append("job_title = ?")
        params.append(args.job_title)
        changed.append("job_title")
    if getattr(args, "description", None) is not None:
        updates.append("description = ?")
        params.append(args.description)
        changed.append("description")
    if getattr(args, "pay_rate", None) is not None:
        updates.append("pay_rate = ?")
        params.append(str(to_decimal(args.pay_rate)))
        changed.append("pay_rate")
    if getattr(args, "hours_per_week", None) is not None:
        updates.append("hours_per_week = ?")
        params.append(str(to_decimal(args.hours_per_week)))
        changed.append("hours_per_week")
    if getattr(args, "total_positions", None) is not None:
        updates.append("total_positions = ?")
        params.append(int(args.total_positions))
        changed.append("total_positions")
    if getattr(args, "department_id", None) is not None:
        updates.append("department_id = ?")
        params.append(args.department_id)
        changed.append("department_id")
    if getattr(args, "supervisor_id", None) is not None:
        updates.append("supervisor_id = ?")
        params.append(args.supervisor_id)
        changed.append("supervisor_id")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = ?")
    params.append(_now_iso())
    params.append(job_id)
    conn.execute(
        f"UPDATE finaid_work_study_job SET {', '.join(updates)} WHERE id = ?", params
    )
    conn.commit()
    ok({"id": job_id, "updated_fields": changed})


def get_work_study_job(conn, args):
    job_id = getattr(args, "id", None)
    if not job_id:
        err("--id is required")

    row = conn.execute(
        "SELECT * FROM finaid_work_study_job WHERE id = ?", (job_id,)
    ).fetchone()
    if not row:
        err(f"Work study job {job_id} not found")

    data = dict(row)

    active_count_row = conn.execute(
        "SELECT COUNT(*) as cnt FROM finaid_work_study_assignment WHERE job_id = ? AND status = 'active'",
        (job_id,)
    ).fetchone()
    data["active_assignment_count"] = active_count_row["cnt"] if active_count_row else 0

    ok(data)


def list_work_study_jobs(conn, args):
    company_id = getattr(args, "company_id", None)
    if not company_id:
        err("--company-id is required")

    query = "SELECT * FROM finaid_work_study_job WHERE company_id = ?"
    params = [company_id]

    if getattr(args, "aid_year_id", None):
        query += " AND aid_year_id = ?"
        params.append(args.aid_year_id)
    if getattr(args, "department_id", None):
        query += " AND department_id = ?"
        params.append(args.department_id)
    if getattr(args, "status", None):
        query += " AND status = ?"
        params.append(args.status)
    if getattr(args, "job_type", None):
        query += " AND job_type = ?"
        params.append(args.job_type)

    query += " ORDER BY created_at DESC"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"jobs": [dict(r) for r in rows], "count": len(rows)})


def close_work_study_job(conn, args):
    job_id = getattr(args, "id", None)
    if not job_id:
        err("--id is required")

    row = conn.execute(
        "SELECT * FROM finaid_work_study_job WHERE id = ?", (job_id,)
    ).fetchone()
    if not row:
        err(f"Work study job {job_id} not found")

    conn.execute(
        "UPDATE finaid_work_study_job SET status = 'closed', updated_at = ? WHERE id = ?",
        (_now_iso(), job_id)
    )
    conn.commit()
    ok({"id": job_id, "status": "closed"})


# ---------------------------------------------------------------------------
# WORK STUDY ASSIGNMENT
# ---------------------------------------------------------------------------

def assign_student_to_job(conn, args):
    student_id = getattr(args, "student_id", None)
    award_id = getattr(args, "award_id", None)
    job_id = getattr(args, "job_id", None)
    aid_year_id = getattr(args, "aid_year_id", None)
    academic_term_id = getattr(args, "academic_term_id", None)
    company_id = getattr(args, "company_id", None)
    start_date = getattr(args, "start_date", None)
    end_date = getattr(args, "end_date", None)
    award_limit = getattr(args, "award_limit", None)

    if not student_id:
        err("--student-id is required")
    if not award_id:
        err("--award-id is required")
    if not job_id:
        err("--job-id is required")
    if not aid_year_id:
        err("--aid-year-id is required")
    if not academic_term_id:
        err("--academic-term-id is required")
    if not company_id:
        err("--company-id is required")
    if not start_date:
        err("--start-date is required")
    if not end_date:
        err("--end-date is required")
    if not award_limit:
        err("--award-limit is required")

    # Validate job exists and is open
    job_row = conn.execute(
        "SELECT * FROM finaid_work_study_job WHERE id = ?", (job_id,)
    ).fetchone()
    if not job_row:
        err(f"Work study job {job_id} not found")
    job = dict(job_row)
    if job["status"] != "open":
        err(f"Job {job_id} is not open (status: {job['status']})")

    # Validate award_id is a valid FWS award
    award_row = conn.execute(
        "SELECT * FROM finaid_award WHERE id = ? AND aid_type = 'fws'", (award_id,)
    ).fetchone()
    if not award_row:
        err(f"Award {award_id} not found or is not a Federal Work Study (fws) award")

    assignment_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO finaid_work_study_assignment
               (id, student_id, award_id, job_id, aid_year_id, academic_term_id,
                start_date, end_date, award_limit, earned_to_date, status,
                company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (assignment_id, student_id, award_id, job_id, aid_year_id, academic_term_id,
             start_date, end_date, str(to_decimal(award_limit)), "0.00", "active",
             company_id, now, now, getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Failed to create assignment: {e}")

    # Increment filled_positions
    new_filled = job["filled_positions"] + 1
    new_status = "filled" if new_filled >= job["total_positions"] else job["status"]
    conn.execute(
        "UPDATE finaid_work_study_job SET filled_positions = ?, status = ?, updated_at = ? WHERE id = ?",
        (new_filled, new_status, now, job_id)
    )

    audit(conn, SKILL, "assign-student-to-job", "finaid_work_study_assignment", assignment_id,
          new_values={"student_id": student_id, "job_id": job_id, "status": "active"})
    conn.commit()
    ok({
        "id": assignment_id,
        "student_id": student_id,
        "job_id": job_id,
        "award_id": award_id,
        "status": "active",
        "job_status": new_status,
    })


def update_work_study_assignment(conn, args):
    assignment_id = getattr(args, "id", None)
    if not assignment_id:
        err("--id is required")

    row = conn.execute(
        "SELECT * FROM finaid_work_study_assignment WHERE id = ?", (assignment_id,)
    ).fetchone()
    if not row:
        err(f"Work study assignment {assignment_id} not found")

    updates, params, changed = [], [], []

    if getattr(args, "start_date", None) is not None:
        updates.append("start_date = ?")
        params.append(args.start_date)
        changed.append("start_date")
    if getattr(args, "end_date", None) is not None:
        updates.append("end_date = ?")
        params.append(args.end_date)
        changed.append("end_date")
    if getattr(args, "award_limit", None) is not None:
        updates.append("award_limit = ?")
        params.append(str(to_decimal(args.award_limit)))
        changed.append("award_limit")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = ?")
    params.append(_now_iso())
    params.append(assignment_id)
    conn.execute(
        f"UPDATE finaid_work_study_assignment SET {', '.join(updates)} WHERE id = ?", params
    )
    conn.commit()
    ok({"id": assignment_id, "updated_fields": changed})


def get_work_study_assignment(conn, args):
    assignment_id = getattr(args, "id", None)
    if not assignment_id:
        err("--id is required")

    row = conn.execute(
        "SELECT * FROM finaid_work_study_assignment WHERE id = ?", (assignment_id,)
    ).fetchone()
    if not row:
        err(f"Work study assignment {assignment_id} not found")

    data = dict(row)

    # Earnings summary: sum of approved timesheet earnings
    earnings_row = conn.execute(
        """SELECT COALESCE(SUM(CAST(earnings AS REAL)), 0) as approved_earnings
           FROM finaid_work_study_timesheet
           WHERE assignment_id = ? AND supervisor_approval_status = 'approved'""",
        (assignment_id,)
    ).fetchone()
    data["approved_earnings_sum"] = str(
        round_currency(to_decimal(earnings_row["approved_earnings"]))
    ) if earnings_row else "0.00"

    ok(data)


def list_work_study_assignments(conn, args):
    company_id = getattr(args, "company_id", None)
    if not company_id:
        err("--company-id is required")

    query = "SELECT * FROM finaid_work_study_assignment WHERE company_id = ?"
    params = [company_id]

    if getattr(args, "student_id", None):
        query += " AND student_id = ?"
        params.append(args.student_id)
    if getattr(args, "job_id", None):
        query += " AND job_id = ?"
        params.append(args.job_id)
    if getattr(args, "academic_term_id", None):
        query += " AND academic_term_id = ?"
        params.append(args.academic_term_id)
    if getattr(args, "status", None):
        query += " AND status = ?"
        params.append(args.status)

    query += " ORDER BY created_at DESC"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"assignments": [dict(r) for r in rows], "count": len(rows)})


def terminate_work_study_assignment(conn, args):
    assignment_id = getattr(args, "id", None)
    if not assignment_id:
        err("--id is required")

    row = conn.execute(
        "SELECT * FROM finaid_work_study_assignment WHERE id = ?", (assignment_id,)
    ).fetchone()
    if not row:
        err(f"Work study assignment {assignment_id} not found")

    assignment = dict(row)
    now = _now_iso()

    conn.execute(
        "UPDATE finaid_work_study_assignment SET status = 'terminated', updated_at = ? WHERE id = ?",
        (now, assignment_id)
    )

    # Decrement job filled_positions; if job was filled, set back to open
    job_row = conn.execute(
        "SELECT * FROM finaid_work_study_job WHERE id = ?", (assignment["job_id"],)
    ).fetchone()
    if job_row:
        job = dict(job_row)
        new_filled = max(0, job["filled_positions"] - 1)
        new_job_status = "open" if job["status"] == "filled" else job["status"]
        conn.execute(
            "UPDATE finaid_work_study_job SET filled_positions = ?, status = ?, updated_at = ? WHERE id = ?",
            (new_filled, new_job_status, now, job["id"])
        )

    audit(conn, SKILL, "terminate-work-study-assignment", "finaid_work_study_assignment",
          assignment_id, new_values={"status": "terminated"})
    conn.commit()
    ok({"id": assignment_id, "status": "terminated"})


# ---------------------------------------------------------------------------
# WORK STUDY TIMESHEET
# ---------------------------------------------------------------------------

def submit_work_study_timesheet(conn, args):
    assignment_id = getattr(args, "assignment_id", None)
    student_id = getattr(args, "student_id", None)
    company_id = getattr(args, "company_id", None)
    pay_period_start = getattr(args, "pay_period_start", None)
    pay_period_end = getattr(args, "pay_period_end", None)
    hours_worked = getattr(args, "hours_worked", None)
    submission_date = getattr(args, "submission_date", None)

    if not assignment_id:
        err("--assignment-id is required")
    if not student_id:
        err("--student-id is required")
    if not company_id:
        err("--company-id is required")
    if not pay_period_start:
        err("--pay-period-start is required")
    if not pay_period_end:
        err("--pay-period-end is required")
    if not hours_worked:
        err("--hours-worked is required")
    if not submission_date:
        err("--submission-date is required")

    # Validate assignment is active
    assignment_row = conn.execute(
        "SELECT * FROM finaid_work_study_assignment WHERE id = ?", (assignment_id,)
    ).fetchone()
    if not assignment_row:
        err(f"Assignment {assignment_id} not found")
    assignment = dict(assignment_row)
    if assignment["status"] != "active":
        err(f"Assignment {assignment_id} is not active (status: {assignment['status']})")

    # Check for duplicate (unique assignment_id + pay_period_start)
    dup = conn.execute(
        "SELECT id FROM finaid_work_study_timesheet WHERE assignment_id = ? AND pay_period_start = ?",
        (assignment_id, pay_period_start)
    ).fetchone()
    if dup:
        err(f"Timesheet already exists for assignment {assignment_id} and pay period starting {pay_period_start}")

    # Get pay_rate from job
    job_row = conn.execute(
        "SELECT * FROM finaid_work_study_job WHERE id = ?", (assignment["job_id"],)
    ).fetchone()
    if not job_row:
        err(f"Job {assignment['job_id']} not found")
    job = dict(job_row)

    hours = to_decimal(hours_worked)
    pay_rate = to_decimal(job["pay_rate"])
    earnings = round_currency(hours * pay_rate)

    earned_to_date = to_decimal(assignment["earned_to_date"])
    award_limit = to_decimal(assignment["award_limit"])
    remaining = award_limit - earned_to_date

    # Cap earnings if they would exceed award_limit
    if earnings > remaining:
        earnings = round_currency(remaining)

    cumulative_earnings = round_currency(earned_to_date + earnings)

    timesheet_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO finaid_work_study_timesheet
               (id, assignment_id, student_id, pay_period_start, pay_period_end,
                hours_worked, earnings, cumulative_earnings, submission_date,
                supervisor_approval_status, supervisor_approved_by,
                supervisor_approved_date, rejection_reason, payroll_exported,
                payroll_export_date, company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (timesheet_id, assignment_id, student_id, pay_period_start, pay_period_end,
             str(hours), str(earnings), str(cumulative_earnings), submission_date,
             "pending", "", "", "", 0, "",
             company_id, now, now, getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Failed to submit timesheet: {e}")

    audit(conn, SKILL, "submit-work-study-timesheet", "finaid_work_study_timesheet",
          timesheet_id,
          new_values={"assignment_id": assignment_id, "hours_worked": str(hours),
                      "earnings": str(earnings)})
    conn.commit()
    ok({
        "id": timesheet_id,
        "assignment_id": assignment_id,
        "student_id": student_id,
        "pay_period_start": pay_period_start,
        "pay_period_end": pay_period_end,
        "hours_worked": str(hours),
        "earnings": str(earnings),
        "cumulative_earnings": str(cumulative_earnings),
        "supervisor_approval_status": "pending",
    })


def update_work_study_timesheet(conn, args):
    timesheet_id = getattr(args, "id", None)
    if not timesheet_id:
        err("--id is required")

    row = conn.execute(
        "SELECT * FROM finaid_work_study_timesheet WHERE id = ?", (timesheet_id,)
    ).fetchone()
    if not row:
        err(f"Timesheet {timesheet_id} not found")

    ts = dict(row)
    if ts["supervisor_approval_status"] != "pending":
        err(f"Timesheet {timesheet_id} cannot be updated: approval status is '{ts['supervisor_approval_status']}' (must be 'pending')")

    updates, params, changed = [], [], []

    hours_worked = getattr(args, "hours_worked", None)
    if hours_worked is not None:
        hours = to_decimal(hours_worked)

        # Recompute earnings based on job pay_rate
        assignment_row = conn.execute(
            "SELECT * FROM finaid_work_study_assignment WHERE id = ?", (ts["assignment_id"],)
        ).fetchone()
        if not assignment_row:
            err(f"Assignment {ts['assignment_id']} not found")
        assignment = dict(assignment_row)

        job_row = conn.execute(
            "SELECT * FROM finaid_work_study_job WHERE id = ?", (assignment["job_id"],)
        ).fetchone()
        if not job_row:
            err(f"Job {assignment['job_id']} not found")
        job = dict(job_row)

        pay_rate = to_decimal(job["pay_rate"])
        earnings = round_currency(hours * pay_rate)

        earned_to_date = to_decimal(assignment["earned_to_date"])
        award_limit = to_decimal(assignment["award_limit"])
        remaining = award_limit - earned_to_date

        if earnings > remaining:
            earnings = round_currency(remaining)

        cumulative_earnings = round_currency(earned_to_date + earnings)

        updates.append("hours_worked = ?")
        params.append(str(hours))
        changed.append("hours_worked")
        updates.append("earnings = ?")
        params.append(str(earnings))
        changed.append("earnings")
        updates.append("cumulative_earnings = ?")
        params.append(str(cumulative_earnings))
        changed.append("cumulative_earnings")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = ?")
    params.append(_now_iso())
    params.append(timesheet_id)
    conn.execute(
        f"UPDATE finaid_work_study_timesheet SET {', '.join(updates)} WHERE id = ?", params
    )
    conn.commit()
    ok({"id": timesheet_id, "updated_fields": changed})


def approve_work_study_timesheet(conn, args):
    timesheet_id = getattr(args, "id", None)
    supervisor_approved_by = getattr(args, "supervisor_approved_by", None)

    if not timesheet_id:
        err("--id is required")
    if not supervisor_approved_by:
        err("--supervisor-approved-by is required")

    row = conn.execute(
        "SELECT * FROM finaid_work_study_timesheet WHERE id = ?", (timesheet_id,)
    ).fetchone()
    if not row:
        err(f"Timesheet {timesheet_id} not found")

    ts = dict(row)
    if ts["supervisor_approval_status"] != "pending":
        err(f"Timesheet {timesheet_id} cannot be approved: status is '{ts['supervisor_approval_status']}'")

    today = _today()
    now = _now_iso()

    conn.execute(
        """UPDATE finaid_work_study_timesheet
           SET supervisor_approval_status = 'approved',
               supervisor_approved_by = ?,
               supervisor_approved_date = ?,
               updated_at = ?
           WHERE id = ?""",
        (supervisor_approved_by, today, now, timesheet_id)
    )

    # Update assignment.earned_to_date += earnings
    earnings = to_decimal(ts["earnings"])
    conn.execute(
        """UPDATE finaid_work_study_assignment
           SET earned_to_date = CAST(ROUND(CAST(earned_to_date AS REAL) + ?, 2) AS TEXT),
               updated_at = ?
           WHERE id = ?""",
        (float(earnings), now, ts["assignment_id"])
    )

    audit(conn, SKILL, "approve-work-study-timesheet", "finaid_work_study_timesheet",
          timesheet_id,
          new_values={"supervisor_approval_status": "approved",
                      "supervisor_approved_by": supervisor_approved_by})
    conn.commit()
    ok({
        "id": timesheet_id,
        "supervisor_approval_status": "approved",
        "supervisor_approved_by": supervisor_approved_by,
        "supervisor_approved_date": today,
    })


def reject_work_study_timesheet(conn, args):
    timesheet_id = getattr(args, "id", None)
    supervisor_approved_by = getattr(args, "supervisor_approved_by", None)

    if not timesheet_id:
        err("--id is required")
    if not supervisor_approved_by:
        err("--supervisor-approved-by is required")

    row = conn.execute(
        "SELECT * FROM finaid_work_study_timesheet WHERE id = ?", (timesheet_id,)
    ).fetchone()
    if not row:
        err(f"Timesheet {timesheet_id} not found")

    ts = dict(row)
    if ts["supervisor_approval_status"] != "pending":
        err(f"Timesheet {timesheet_id} cannot be rejected: status is '{ts['supervisor_approval_status']}'")

    rejection_reason = getattr(args, "rejection_reason", None) or ""
    now = _now_iso()

    conn.execute(
        """UPDATE finaid_work_study_timesheet
           SET supervisor_approval_status = 'rejected',
               supervisor_approved_by = ?,
               rejection_reason = ?,
               updated_at = ?
           WHERE id = ?""",
        (supervisor_approved_by, rejection_reason, now, timesheet_id)
    )

    audit(conn, SKILL, "reject-work-study-timesheet", "finaid_work_study_timesheet",
          timesheet_id,
          new_values={"supervisor_approval_status": "rejected",
                      "supervisor_approved_by": supervisor_approved_by})
    conn.commit()
    ok({
        "id": timesheet_id,
        "supervisor_approval_status": "rejected",
        "supervisor_approved_by": supervisor_approved_by,
        "rejection_reason": rejection_reason,
    })


def get_work_study_timesheet(conn, args):
    timesheet_id = getattr(args, "id", None)
    if not timesheet_id:
        err("--id is required")

    row = conn.execute(
        "SELECT * FROM finaid_work_study_timesheet WHERE id = ?", (timesheet_id,)
    ).fetchone()
    if not row:
        err(f"Timesheet {timesheet_id} not found")

    ok(dict(row))


def list_work_study_timesheets(conn, args):
    company_id = getattr(args, "company_id", None)
    if not company_id:
        err("--company-id is required")

    query = "SELECT * FROM finaid_work_study_timesheet WHERE company_id = ?"
    params = [company_id]

    if getattr(args, "student_id", None):
        query += " AND student_id = ?"
        params.append(args.student_id)
    if getattr(args, "assignment_id", None):
        query += " AND assignment_id = ?"
        params.append(args.assignment_id)
    if getattr(args, "supervisor_approval_status", None):
        query += " AND supervisor_approval_status = ?"
        params.append(args.supervisor_approval_status)
    if getattr(args, "pay_period_start", None):
        query += " AND pay_period_start = ?"
        params.append(args.pay_period_start)

    query += " ORDER BY pay_period_start DESC"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"timesheets": [dict(r) for r in rows], "count": len(rows)})


# ---------------------------------------------------------------------------
# PAYROLL EXPORT
# ---------------------------------------------------------------------------

def export_work_study_payroll(conn, args):
    company_id = getattr(args, "company_id", None)
    if not company_id:
        err("--company-id is required")

    query = """
        SELECT
            t.id as timesheet_id,
            t.student_id,
            t.assignment_id,
            j.job_title,
            t.pay_period_start,
            t.pay_period_end,
            t.hours_worked,
            t.earnings,
            t.supervisor_approved_by
        FROM finaid_work_study_timesheet t
        JOIN finaid_work_study_assignment a ON a.id = t.assignment_id
        JOIN finaid_work_study_job j ON j.id = a.job_id
        WHERE t.company_id = ?
          AND t.supervisor_approval_status = 'approved'
          AND t.payroll_exported = 0
    """
    params = [company_id]

    if getattr(args, "academic_term_id", None):
        query += " AND a.academic_term_id = ?"
        params.append(args.academic_term_id)
    if getattr(args, "pay_period_start", None):
        query += " AND t.pay_period_start = ?"
        params.append(args.pay_period_start)

    rows = conn.execute(query, params).fetchall()
    if not rows:
        ok({"exported_count": 0, "total_amount": "0.00", "csv_data": ""})
        return

    # Generate CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "student_id", "assignment_id", "job_title",
        "pay_period_start", "pay_period_end",
        "hours_worked", "earnings", "supervisor_approved_by"
    ])
    writer.writeheader()

    total_amount = Decimal("0")
    timesheet_ids = []

    for row in rows:
        r = dict(row)
        timesheet_ids.append(r["timesheet_id"])
        total_amount += to_decimal(r["earnings"])
        writer.writerow({
            "student_id": r["student_id"],
            "assignment_id": r["assignment_id"],
            "job_title": r["job_title"],
            "pay_period_start": r["pay_period_start"],
            "pay_period_end": r["pay_period_end"],
            "hours_worked": r["hours_worked"],
            "earnings": r["earnings"],
            "supervisor_approved_by": r["supervisor_approved_by"],
        })

    csv_data = output.getvalue()
    today = _today()
    now = _now_iso()

    # Mark timesheets as exported
    for ts_id in timesheet_ids:
        conn.execute(
            "UPDATE finaid_work_study_timesheet SET payroll_exported = 1, payroll_export_date = ?, updated_at = ? WHERE id = ?",
            (today, now, ts_id)
        )

    conn.commit()
    ok({
        "exported_count": len(timesheet_ids),
        "total_amount": str(round_currency(total_amount)),
        "csv_data": csv_data,
    })


# ---------------------------------------------------------------------------
# EARNINGS SUMMARY
# ---------------------------------------------------------------------------

def get_work_study_earnings_summary(conn, args):
    student_id = getattr(args, "student_id", None)
    aid_year_id = getattr(args, "aid_year_id", None)
    company_id = getattr(args, "company_id", None)

    if not student_id:
        err("--student-id is required")
    if not aid_year_id:
        err("--aid-year-id is required")
    if not company_id:
        err("--company-id is required")

    # Get the active assignment for this student/aid_year/company
    assignment_row = conn.execute(
        """SELECT a.*, j.job_type
           FROM finaid_work_study_assignment a
           JOIN finaid_work_study_job j ON j.id = a.job_id
           WHERE a.student_id = ? AND a.aid_year_id = ? AND a.company_id = ?
             AND a.status = 'active'
           LIMIT 1""",
        (student_id, aid_year_id, company_id)
    ).fetchone()

    award_limit = Decimal("0")
    if assignment_row:
        award_limit = to_decimal(dict(assignment_row)["award_limit"])

    # Sum of approved timesheet earnings for the student/aid_year
    earned_row = conn.execute(
        """SELECT COALESCE(SUM(CAST(t.earnings AS REAL)), 0) as total_earned
           FROM finaid_work_study_timesheet t
           JOIN finaid_work_study_assignment a ON a.id = t.assignment_id
           WHERE a.student_id = ? AND a.aid_year_id = ? AND a.company_id = ?
             AND t.supervisor_approval_status = 'approved'""",
        (student_id, aid_year_id, company_id)
    ).fetchone()

    earned_to_date = to_decimal(earned_row["total_earned"]) if earned_row else Decimal("0")
    remaining_limit = round_currency(max(Decimal("0"), award_limit - earned_to_date))

    # Community service hours: sum of hours from on_campus or off_campus_community jobs
    community_hours_row = conn.execute(
        """SELECT COALESCE(SUM(CAST(t.hours_worked AS REAL)), 0) as community_hours
           FROM finaid_work_study_timesheet t
           JOIN finaid_work_study_assignment a ON a.id = t.assignment_id
           JOIN finaid_work_study_job j ON j.id = a.job_id
           WHERE a.student_id = ? AND a.aid_year_id = ? AND a.company_id = ?
             AND j.job_type IN ('on_campus', 'off_campus_community')
             AND t.supervisor_approval_status = 'approved'""",
        (student_id, aid_year_id, company_id)
    ).fetchone()

    community_service_hours = to_decimal(
        community_hours_row["community_hours"]
    ) if community_hours_row else Decimal("0")

    ok({
        "student_id": student_id,
        "aid_year_id": aid_year_id,
        "company_id": company_id,
        "award_limit": str(round_currency(award_limit)),
        "earned_to_date": str(round_currency(earned_to_date)),
        "remaining_limit": str(remaining_limit),
        "community_service_hours": str(community_service_hours),
    })


# ---------------------------------------------------------------------------
# ACTIONS REGISTRY
# ---------------------------------------------------------------------------

ACTIONS = {
    "add-work-study-job": add_work_study_job,
    "update-work-study-job": update_work_study_job,
    "get-work-study-job": get_work_study_job,
    "list-work-study-jobs": list_work_study_jobs,
    "terminate-work-study-job": close_work_study_job,
    "assign-student-to-job": assign_student_to_job,
    "update-work-study-assignment": update_work_study_assignment,
    "get-work-study-assignment": get_work_study_assignment,
    "list-work-study-assignments": list_work_study_assignments,
    "terminate-work-study-assignment": terminate_work_study_assignment,
    "submit-work-study-timesheet": submit_work_study_timesheet,
    "update-work-study-timesheet": update_work_study_timesheet,
    "approve-work-study-timesheet": approve_work_study_timesheet,
    "deny-work-study-timesheet": reject_work_study_timesheet,
    "get-work-study-timesheet": get_work_study_timesheet,
    "list-work-study-timesheets": list_work_study_timesheets,
    "generate-payroll-export": export_work_study_payroll,
    "get-work-study-earnings-summary": get_work_study_earnings_summary,
}
