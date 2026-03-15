"""EduClaw State Reporting — submission_tracking domain module

Submission history, certification workflow, amendment tracking,
submission audit trail, and export package generation.

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
    from erpclaw_lib.naming import get_next_name
    import erpclaw_lib.naming as _naming_lib
    # Register educlaw-statereport submission naming series
    _naming_lib.ENTITY_PREFIXES.setdefault("SUB", "SUB-")
except ImportError:
    pass

SKILL = "educlaw-statereport"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

VALID_SUBMISSION_TYPES = ("initial", "amendment", "correction")
VALID_SUBMISSION_METHODS = ("edfi_api", "flat_file", "manual_portal")
VALID_SUBMISSION_STATUSES = ("pending", "in_progress", "completed", "failed", "certified")


# ─────────────────────────────────────────────────────────────────────────────
# SUBMISSION CRUD
# ─────────────────────────────────────────────────────────────────────────────

def add_submission(conn, args):
    window_id = getattr(args, "window_id", None)
    company_id = getattr(args, "company_id", None)
    submission_type = getattr(args, "submission_type", None) or "initial"
    submission_method = getattr(args, "submission_method", None)

    if not window_id:
        err("--window-id is required")
    if not company_id:
        err("--company-id is required")
    if submission_type not in VALID_SUBMISSION_TYPES:
        err(f"--submission-type must be one of: {', '.join(VALID_SUBMISSION_TYPES)}")
    if submission_method and submission_method not in VALID_SUBMISSION_METHODS:
        err(f"--submission-method must be one of: {', '.join(VALID_SUBMISSION_METHODS)}")

    window = conn.execute("SELECT * FROM sr_collection_window WHERE id = ?", (window_id,)).fetchone()
    if not window:
        err(f"Collection window {window_id} not found")

    # Validate snapshot_id if provided
    snapshot_id = getattr(args, "snapshot_id", None)
    if snapshot_id:
        if not conn.execute("SELECT id FROM sr_snapshot WHERE id = ?", (snapshot_id,)).fetchone():
            err(f"Snapshot {snapshot_id} not found")

    # Validate linked_submission_id for amendments
    linked_submission_id = getattr(args, "linked_submission_id", None)
    if linked_submission_id:
        if not conn.execute("SELECT id FROM sr_submission WHERE id = ?", (linked_submission_id,)).fetchone():
            err(f"Linked submission {linked_submission_id} not found")

    school_year = window["school_year"]
    naming_series = get_next_name(conn, "SUB", school_year, company_id)
    submission_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO sr_submission
               (id, naming_series, collection_window_id, snapshot_id,
                submission_type, submission_method, submitted_at, submitted_by,
                records_submitted, records_accepted, records_rejected,
                submission_status, state_confirmation_id, state_confirmed_at,
                amendment_reason, linked_submission_id,
                company_id, created_at, updated_at, created_by)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (submission_id, naming_series, window_id, snapshot_id,
             submission_type, submission_method or "",
             getattr(args, "submitted_at", None) or now,
             getattr(args, "submitted_by", None) or getattr(args, "user_id", None) or "",
             int(getattr(args, "records_submitted", None) or 0),
             int(getattr(args, "records_accepted", None) or 0),
             int(getattr(args, "records_rejected", None) or 0),
             "pending",
             getattr(args, "state_confirmation_id", None) or "",
             getattr(args, "state_confirmed_at", None) or "",
             getattr(args, "amendment_reason", None) or "",
             linked_submission_id,
             company_id, now, now, getattr(args, "user_id", None) or "")
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        err(f"Cannot create submission: {e}")

    audit(conn, "sr_submission", submission_id, "INSERT", getattr(args, "user_id", None) or "")
    ok({"id": submission_id, "naming_series": naming_series,
        "submission_type": submission_type, "submission_status": "pending",
        "message": "Submission record created"})


def update_submission_status(conn, args):
    submission_id = getattr(args, "submission_id", None)
    submission_status = getattr(args, "submission_status", None)

    if not submission_id:
        err("--submission-id is required")
    if not submission_status:
        err("--submission-status is required")
    if submission_status not in VALID_SUBMISSION_STATUSES:
        err(f"--submission-status must be one of: {', '.join(VALID_SUBMISSION_STATUSES)}")

    row = conn.execute("SELECT id FROM sr_submission WHERE id = ?", (submission_id,)).fetchone()
    if not row:
        err(f"Submission {submission_id} not found")

    updates = {"submission_status": submission_status, "updated_at": _now_iso()}

    for field in ["records_accepted", "records_rejected", "records_submitted",
                  "state_confirmation_id", "state_confirmed_at"]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE sr_submission SET {set_clause} WHERE id = ?",
        list(updates.values()) + [submission_id]
    )
    conn.commit()
    audit(conn, "sr_submission", submission_id, "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": submission_id, "submission_status": submission_status,
        "message": "Submission status updated"})


def get_submission(conn, args):
    submission_id = getattr(args, "submission_id", None)
    if not submission_id:
        err("--submission-id is required")

    row = conn.execute("SELECT * FROM sr_submission WHERE id = ?", (submission_id,)).fetchone()
    if not row:
        err(f"Submission {submission_id} not found")

    submission = dict(row)

    # Attach snapshot if linked
    if submission.get("snapshot_id"):
        snap = conn.execute(
            "SELECT * FROM sr_snapshot WHERE id = ?", (submission["snapshot_id"],)
        ).fetchone()
        submission["snapshot"] = dict(snap) if snap else None

    # Error count for this submission
    error_count = conn.execute(
        "SELECT COUNT(*) FROM sr_submission_error WHERE collection_window_id = ? AND resolution_status = 'open'",
        (submission["collection_window_id"],)
    ).fetchone()[0]
    submission["open_error_count"] = error_count

    ok(submission)


def list_submissions(conn, args):
    company_id = getattr(args, "company_id", None)
    if not company_id:
        err("--company-id is required")

    conditions = ["company_id = ?"]
    params = [company_id]

    window_id = getattr(args, "window_id", None)
    if window_id:
        conditions.append("collection_window_id = ?")
        params.append(window_id)

    submission_status = getattr(args, "submission_status", None)
    if submission_status:
        conditions.append("submission_status = ?")
        params.append(submission_status)

    submission_type = getattr(args, "submission_type", None)
    if submission_type:
        conditions.append("submission_type = ?")
        params.append(submission_type)

    where = " AND ".join(conditions)
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)

    rows = conn.execute(
        f"SELECT * FROM sr_submission WHERE {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [limit, offset]
    ).fetchall()

    ok({"submissions": [dict(r) for r in rows], "count": len(rows)})


# ─────────────────────────────────────────────────────────────────────────────
# CERTIFICATION WORKFLOW
# ─────────────────────────────────────────────────────────────────────────────

def certify_submission(conn, args):
    """Certify a submission — atomically updates submission, snapshot, and window."""
    submission_id = getattr(args, "submission_id", None)
    certified_by = getattr(args, "certified_by", None) or getattr(args, "user_id", None) or ""
    certification_notes = getattr(args, "certification_notes", None) or ""

    if not submission_id:
        err("--submission-id is required")
    if not certified_by:
        err("--certified-by is required")

    sub = conn.execute("SELECT * FROM sr_submission WHERE id = ?", (submission_id,)).fetchone()
    if not sub:
        err(f"Submission {submission_id} not found")

    if sub["submission_status"] == "certified":
        err("Submission is already certified")

    now = _now_iso()
    window_id = sub["collection_window_id"]
    snapshot_id = sub["snapshot_id"]

    # Atomic transaction: update submission + snapshot + window
    try:
        conn.execute("BEGIN")

        # Update submission
        conn.execute(
            """UPDATE sr_submission
               SET submission_status = 'certified', updated_at = ?
               WHERE id = ?""",
            (now, submission_id)
        )

        # Update snapshot if linked
        if snapshot_id:
            conn.execute(
                """UPDATE sr_snapshot
                   SET snapshot_status = 'certified', certified_by = ?,
                       certified_at = ?, certification_notes = ?, updated_at = ?
                   WHERE id = ?""",
                (certified_by, now, certification_notes, now, snapshot_id)
            )

        # Update collection window
        conn.execute(
            "UPDATE sr_collection_window SET status = 'certified', updated_at = ? WHERE id = ?",
            (now, window_id)
        )

        conn.execute("COMMIT")
    except Exception as e:
        conn.execute("ROLLBACK")
        err(f"Certification failed: {e}")

    audit(conn, "sr_submission", submission_id, "UPDATE", certified_by)
    ok({"id": submission_id, "submission_status": "certified",
        "certified_by": certified_by, "certified_at": now,
        "message": "Submission certified successfully"})


def create_amendment(conn, args):
    """Create an amendment submission linked to the original."""
    original_submission_id = getattr(args, "original_submission_id", None)
    amendment_reason = getattr(args, "amendment_reason", None)
    company_id = getattr(args, "company_id", None)

    if not original_submission_id:
        err("--original-submission-id is required")
    if not amendment_reason:
        err("--amendment-reason is required")
    if not company_id:
        err("--company-id is required")

    orig = conn.execute(
        "SELECT * FROM sr_submission WHERE id = ?", (original_submission_id,)
    ).fetchone()
    if not orig:
        err(f"Original submission {original_submission_id} not found")

    window_id = orig["collection_window_id"]
    window = conn.execute("SELECT * FROM sr_collection_window WHERE id = ?", (window_id,)).fetchone()
    if not window:
        err(f"Collection window {window_id} not found")

    school_year = window["school_year"]
    naming_series = get_next_name(conn, "SUB", school_year, company_id)
    amendment_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute("BEGIN")

        # Insert amendment submission
        conn.execute(
            """INSERT INTO sr_submission
               (id, naming_series, collection_window_id, snapshot_id,
                submission_type, submission_method, submitted_at, submitted_by,
                records_submitted, records_accepted, records_rejected,
                submission_status, state_confirmation_id, state_confirmed_at,
                amendment_reason, linked_submission_id,
                company_id, created_at, updated_at, created_by)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (amendment_id, naming_series, window_id, None,
             "amendment",
             getattr(args, "submission_method", None) or orig["submission_method"],
             now,
             getattr(args, "user_id", None) or "",
             0, 0, 0,
             "pending", "", "",
             amendment_reason, original_submission_id,
             company_id, now, now, getattr(args, "user_id", None) or "")
        )

        # Re-open the collection window for corrections
        conn.execute(
            "UPDATE sr_collection_window SET status = 'data_entry', updated_at = ? WHERE id = ?",
            (now, window_id)
        )

        conn.execute("COMMIT")
    except Exception as e:
        conn.execute("ROLLBACK")
        err(f"Cannot create amendment: {e}")

    audit(conn, "sr_submission", amendment_id, "INSERT", getattr(args, "user_id", None) or "")
    ok({"id": amendment_id, "naming_series": naming_series,
        "submission_type": "amendment",
        "linked_submission_id": original_submission_id,
        "window_status": "data_entry",
        "message": "Amendment submission created; window re-opened for corrections"})


# ─────────────────────────────────────────────────────────────────────────────
# HISTORY / REPORTS
# ─────────────────────────────────────────────────────────────────────────────

def get_submission_history(conn, args):
    """Full chronological submission history for a collection window."""
    window_id = getattr(args, "window_id", None)
    if not window_id:
        err("--window-id is required")

    window = conn.execute("SELECT * FROM sr_collection_window WHERE id = ?", (window_id,)).fetchone()
    if not window:
        err(f"Collection window {window_id} not found")

    submissions = conn.execute(
        "SELECT * FROM sr_submission WHERE collection_window_id = ? ORDER BY created_at ASC",
        (window_id,)
    ).fetchall()

    snapshots = conn.execute(
        "SELECT * FROM sr_snapshot WHERE collection_window_id = ?",
        (window_id,)
    ).fetchall()

    ok({
        "window_id": window_id,
        "window_name": window["name"],
        "window_type": window["window_type"],
        "school_year": window["school_year"],
        "current_window_status": window["status"],
        "submission_count": len(submissions),
        "submissions": [dict(s) for s in submissions],
        "snapshots": [dict(s) for s in snapshots],
    })


def export_submission_package(conn, args):
    """Build export package: snapshot summary + all snapshot records as JSON."""
    submission_id = getattr(args, "submission_id", None)
    if not submission_id:
        err("--submission-id is required")

    sub = conn.execute("SELECT * FROM sr_submission WHERE id = ?", (submission_id,)).fetchone()
    if not sub:
        err(f"Submission {submission_id} not found")

    snapshot_id = sub["snapshot_id"]
    if not snapshot_id:
        err("Submission has no linked snapshot. Cannot export without a snapshot.")

    snapshot = conn.execute("SELECT * FROM sr_snapshot WHERE id = ?", (snapshot_id,)).fetchone()
    if not snapshot:
        err(f"Snapshot {snapshot_id} not found")

    window = conn.execute(
        "SELECT * FROM sr_collection_window WHERE id = ?", (sub["collection_window_id"],)
    ).fetchone()

    # Get all snapshot records
    records = conn.execute(
        "SELECT * FROM sr_snapshot_record WHERE snapshot_id = ? ORDER BY record_type, created_at",
        (snapshot_id,)
    ).fetchall()

    parsed_records = []
    for r in records:
        rec = dict(r)
        try:
            rec["data_json"] = json.loads(rec["data_json"])
        except (json.JSONDecodeError, TypeError):
            rec["data_json"] = {}
        parsed_records.append(rec)

    ok({
        "submission": dict(sub),
        "snapshot": dict(snapshot),
        "collection_window": {
            "id": window["id"],
            "name": window["name"],
            "window_type": window["window_type"],
            "school_year": window["school_year"],
            "state_code": window["state_code"],
        } if window else None,
        "record_count": len(parsed_records),
        "records": parsed_records,
        "exported_at": _now_iso(),
    })


def get_submission_audit_trail(conn, args):
    """Complete audit trail: status transitions, snapshots, submissions, certifications."""
    window_id = getattr(args, "window_id", None)
    if not window_id:
        err("--window-id is required")

    window = conn.execute("SELECT * FROM sr_collection_window WHERE id = ?", (window_id,)).fetchone()
    if not window:
        err(f"Collection window {window_id} not found")

    submissions = conn.execute(
        """SELECT id, naming_series, submission_type, submission_status,
               submitted_at, submitted_by, records_submitted, records_accepted,
               records_rejected, amendment_reason, linked_submission_id, created_at
           FROM sr_submission WHERE collection_window_id = ? ORDER BY created_at ASC""",
        (window_id,)
    ).fetchall()

    snapshots = conn.execute(
        """SELECT id, snapshot_taken_at, snapshot_taken_by, total_students,
               total_enrollment, snapshot_status, certified_by, certified_at, created_at
           FROM sr_snapshot WHERE collection_window_id = ?""",
        (window_id,)
    ).fetchall()

    error_summary = conn.execute(
        """SELECT severity, resolution_status, COUNT(*) as count
           FROM sr_submission_error WHERE collection_window_id = ?
           GROUP BY severity, resolution_status""",
        (window_id,)
    ).fetchall()

    ok({
        "window_id": window_id,
        "window_name": window["name"],
        "window_type": window["window_type"],
        "school_year": window["school_year"],
        "state_code": window["state_code"],
        "current_status": window["status"],
        "created_at": window["created_at"],
        "updated_at": window["updated_at"],
        "snapshots": [dict(s) for s in snapshots],
        "submissions": [dict(s) for s in submissions],
        "error_summary": [dict(r) for r in error_summary],
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────
ACTIONS = {
    "add-submission": add_submission,
    "update-submission-status": update_submission_status,
    "get-submission": get_submission,
    "list-submissions": list_submissions,
    "approve-submission": certify_submission,
    "create-amendment": create_amendment,
    "get-submission-history": get_submission_history,
    "generate-submission-package": export_submission_package,
    "get-submission-audit-trail": get_submission_audit_trail,
}
