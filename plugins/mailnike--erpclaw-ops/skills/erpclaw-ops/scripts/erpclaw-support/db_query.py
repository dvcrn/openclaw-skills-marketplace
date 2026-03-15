#!/usr/bin/env python3
"""ERPClaw Support Skill -- db_query.py

Issue tracking, SLA management, warranty claims, maintenance scheduling,
and support reports. All 18 actions are routed through this single entry point.

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout, exit 0 on success, exit 1 on error.
"""
import argparse
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

# Add shared lib to path
try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection, ensure_db_exists, DEFAULT_DB_PATH
    from erpclaw_lib.decimal_utils import to_decimal, round_currency
    from erpclaw_lib.naming import get_next_name
    from erpclaw_lib.validation import check_input_lengths
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
    from erpclaw_lib.dependencies import check_required_tables
    from erpclaw_lib.query import (
        Q, P, Table, Field, fn, Case, Order, Criterion, Not, NULL,
        DecimalSum, DecimalAbs, insert_row, update_row,
    )
    from erpclaw_lib.vendor.pypika.terms import LiteralValue, ValueWrapper
except ImportError:
    import json as _json
    print(_json.dumps({"status": "error", "error": "ERPClaw foundation not installed. Install erpclaw first: clawhub install erpclaw", "suggestion": "clawhub install erpclaw"}))
    sys.exit(1)

REQUIRED_TABLES = ["company"]

VALID_PRIORITIES = ("low", "medium", "high", "critical")
VALID_ISSUE_TYPES = ("bug", "feature_request", "question", "complaint", "return")
VALID_ISSUE_STATUSES = ("open", "in_progress", "waiting_on_customer", "resolved", "closed")
VALID_WARRANTY_STATUSES = ("open", "in_progress", "resolved", "closed")
VALID_WARRANTY_RESOLUTIONS = ("repair", "replace", "refund", "rejected")
VALID_SCHEDULE_FREQUENCIES = ("monthly", "quarterly", "semi_annual", "annual")
VALID_SCHEDULE_STATUSES = ("active", "expired", "cancelled")
VALID_VISIT_STATUSES = ("scheduled", "completed", "cancelled")
VALID_COMMENT_BY = ("employee", "customer")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_json_arg(value, name):
    if value is None:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        err(f"Invalid JSON for --{name}: {value}")


# ---------------------------------------------------------------------------
# Company resolution
# ---------------------------------------------------------------------------

def _resolve_company_id(conn, args):
    """Resolve company_id from args or conn, set on conn for get_next_name()."""
    company_id = getattr(args, "company_id", None) or getattr(conn, "company_id", None)
    if not company_id:
        err("--company-id is required")
    # Validate company exists
    t = Table("company")
    q = Q.from_(t).select(t.id).where(t.id == P())
    comp = conn.execute(q.get_sql(), (company_id,)).fetchone()
    if not comp:
        err(f"Company {company_id} not found")
    # Set on conn so get_next_name() can find it
    conn.company_id = company_id
    return company_id


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _validate_issue_exists(conn, issue_id: str):
    t = Table("issue")
    q = Q.from_(t).select(t.star).where(t.id == P())
    issue = conn.execute(q.get_sql(), (issue_id,)).fetchone()
    if not issue:
        err(f"Issue {issue_id} not found",
             suggestion="Use 'list issues' to see available issues.")
    return issue


def _validate_sla_exists(conn, sla_id: str):
    t = Table("service_level_agreement")
    q = Q.from_(t).select(t.star).where(t.id == P())
    sla = conn.execute(q.get_sql(), (sla_id,)).fetchone()
    if not sla:
        err(f"SLA {sla_id} not found")
    return sla


def _validate_customer_exists(conn, customer_id: str):
    t = Table("customer")
    q = Q.from_(t).select(t.star).where(t.id == P())
    cust = conn.execute(q.get_sql(), (customer_id,)).fetchone()
    if not cust:
        err(f"Customer {customer_id} not found")
    return cust


# ---------------------------------------------------------------------------
# SLA calculation helpers
# ---------------------------------------------------------------------------

def _calc_sla_due_dates(conn, sla_id, priority, created_at):
    """Calculate response_due and resolution_due from SLA + priority.

    Returns (response_due_str, resolution_due_str) as ISO datetime strings,
    or (None, None) if the priority has no configured hours.
    """
    t = Table("service_level_agreement")
    q = Q.from_(t).select(t.star).where(t.id == P())
    sla = conn.execute(q.get_sql(), (sla_id,)).fetchone()
    if not sla:
        return (None, None)

    # Parse the JSON columns
    response_times = {}
    resolution_times = {}
    try:
        if sla["priority_response_times"]:
            response_times = json.loads(sla["priority_response_times"])
    except (json.JSONDecodeError, TypeError):
        pass
    try:
        if sla["priority_resolution_times"]:
            resolution_times = json.loads(sla["priority_resolution_times"])
    except (json.JSONDecodeError, TypeError):
        pass

    response_hours = response_times.get(priority)
    resolution_hours = resolution_times.get(priority)

    if response_hours is None and resolution_hours is None:
        return (None, None)

    # Parse created_at
    try:
        base_dt = datetime.fromisoformat(created_at)
    except (ValueError, TypeError):
        base_dt = datetime.now(timezone.utc)

    response_due = None
    resolution_due = None

    if response_hours is not None:
        response_due = (base_dt + timedelta(hours=float(response_hours))).isoformat(
            sep=" ", timespec="seconds"
        )

    if resolution_hours is not None:
        resolution_due = (base_dt + timedelta(hours=float(resolution_hours))).isoformat(
            sep=" ", timespec="seconds"
        )

    return (response_due, resolution_due)


def _calc_next_due_date(visit_date_str, frequency):
    """Calculate the next due date from a visit date and frequency.

    Returns ISO date string (YYYY-MM-DD).
    """
    try:
        base = datetime.fromisoformat(visit_date_str).date()
    except (ValueError, TypeError):
        from datetime import date
        base = date.today()

    freq_days = {
        "monthly": 30,
        "quarterly": 90,
        "semi_annual": 180,
        "annual": 365,
    }
    days = freq_days.get(frequency, 90)
    return (base + timedelta(days=days)).isoformat()


# ---------------------------------------------------------------------------
# 1. add-issue
# ---------------------------------------------------------------------------

def add_issue(conn, args):
    """Add a new support issue.

    Required: --subject
    Optional: --customer-id, --item-id, --serial-number-id, --priority,
              --issue-type, --description, --assigned-to, --sla-id, --company-id
    """
    if not args.subject:
        err("--subject is required")

    priority = args.priority or "medium"
    if priority not in VALID_PRIORITIES:
        err(f"--priority must be one of {VALID_PRIORITIES}")

    if args.issue_type and args.issue_type not in VALID_ISSUE_TYPES:
        err(f"--issue-type must be one of {VALID_ISSUE_TYPES}")

    # Validate foreign keys
    if args.customer_id:
        _validate_customer_exists(conn, args.customer_id)

    if args.item_id:
        it = Table("item")
        q = Q.from_(it).select(it.id).where(it.id == P())
        item = conn.execute(q.get_sql(), (args.item_id,)).fetchone()
        if not item:
            err(f"Item {args.item_id} not found")

    # Resolve company_id for naming series
    # If customer_id provided, derive company from customer; otherwise require --company-id
    company_id = None
    if args.customer_id:
        ct = Table("customer")
        cq = Q.from_(ct).select(ct.id, ct.company_id).where(
            (ct.id == P()) | (ct.name == P())
        )
        cust_row = conn.execute(cq.get_sql(), (args.customer_id, args.customer_id)).fetchone()
        if cust_row and cust_row["company_id"]:
            company_id = cust_row["company_id"]
            conn.company_id = company_id
            args.customer_id = cust_row["id"]

    if not company_id:
        company_id = _resolve_company_id(conn, args)

    # SLA: use provided or find default
    sla_id = args.sla_id
    if not sla_id:
        st = Table("service_level_agreement")
        sq = Q.from_(st).select(st.id).where(st.is_default == 1)
        default_sla = conn.execute(sq.get_sql()).fetchone()
        if default_sla:
            sla_id = default_sla["id"]

    # Calculate SLA due dates
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    response_due = None
    resolution_due = None
    if sla_id:
        response_due, resolution_due = _calc_sla_due_dates(conn, sla_id, priority, now_str)

    issue_id = str(uuid.uuid4())
    naming = get_next_name(conn, "issue")

    ins_sql, _ = insert_row("issue", {
        "id": P(), "naming_series": P(), "subject": P(), "description": P(),
        "customer_id": P(), "item_id": P(), "serial_number_id": P(),
        "priority": P(), "issue_type": P(), "status": P(),
        "assigned_to": P(), "sla_id": P(), "response_due": P(),
        "resolution_due": P(),
    })
    conn.execute(ins_sql, (
        issue_id, naming, args.subject, args.description,
        args.customer_id, args.item_id, args.serial_number_id,
        priority, args.issue_type, "open",
        args.assigned_to, sla_id, response_due, resolution_due,
    ))

    audit(conn, "erpclaw-support", "add-issue", "issue", issue_id,
           new_values={"subject": args.subject, "priority": priority},
           description=f"Created issue: {args.subject}")
    conn.commit()

    ok({
        "issue": {
            "id": issue_id,
            "naming_series": naming,
            "subject": args.subject,
            "priority": priority,
            "issue_type": args.issue_type,
            "status": "open",
            "customer_id": args.customer_id,
            "sla_id": sla_id,
            "response_due": response_due,
            "resolution_due": resolution_due,
            "assigned_to": args.assigned_to,
        },
        "message": f"Issue '{args.subject}' created ({naming})",
    })


# ---------------------------------------------------------------------------
# 2. update-issue
# ---------------------------------------------------------------------------

def update_issue(conn, args):
    """Update an existing issue.

    Required: --issue-id
    Optional: --status, --priority, --assigned-to, --issue-type, --description
    """
    if not args.issue_id:
        err("--issue-id is required")

    issue = _validate_issue_exists(conn, args.issue_id)
    old_values = row_to_dict(issue)

    if issue["status"] == "closed":
        err("Cannot update a closed issue. Reopen it first.",
             suggestion="Use 'update issue' with --status open to reopen.")

    if args.priority and args.priority not in VALID_PRIORITIES:
        err(f"--priority must be one of {VALID_PRIORITIES}")
    if args.issue_type and args.issue_type not in VALID_ISSUE_TYPES:
        err(f"--issue-type must be one of {VALID_ISSUE_TYPES}")
    if args.status and args.status not in VALID_ISSUE_STATUSES:
        err(f"--status must be one of {VALID_ISSUE_STATUSES}")

    data = {}
    values = []

    field_map = {
        "status": args.status,
        "priority": args.priority,
        "assigned_to": args.assigned_to,
        "issue_type": args.issue_type,
        "description": args.description,
    }

    for col, val in field_map.items():
        if val is not None:
            data[col] = P()
            values.append(val)

    if not data:
        err("No fields to update. Provide at least one optional flag.")

    data["updated_at"] = LiteralValue("datetime('now')")
    values.append(args.issue_id)

    upd_sql = update_row("issue", data, where={"id": P()})
    conn.execute(upd_sql, values)

    audit(conn, "erpclaw-support", "update-issue", "issue", args.issue_id,
           old_values=old_values,
           description="Updated issue")
    conn.commit()

    it = Table("issue")
    rq = Q.from_(it).select(it.star).where(it.id == P())
    updated = conn.execute(rq.get_sql(), (args.issue_id,)).fetchone()

    ok({
        "issue": row_to_dict(updated),
        "message": f"Issue {updated['naming_series']} updated",
    })


# ---------------------------------------------------------------------------
# 3. get-issue
# ---------------------------------------------------------------------------

def get_issue(conn, args):
    """Get issue details with comments, customer, SLA info, and SLA status.

    Required: --issue-id
    """
    if not args.issue_id:
        err("--issue-id is required")

    issue = _validate_issue_exists(conn, args.issue_id)
    issue_dict = row_to_dict(issue)

    # Customer info
    if issue["customer_id"]:
        ct = Table("customer")
        cq = Q.from_(ct).select(
            ct.id, ct.name, ct.customer_type, ct.territory, ct.status
        ).where(ct.id == P())
        customer = conn.execute(cq.get_sql(), (issue["customer_id"],)).fetchone()
        issue_dict["customer"] = row_to_dict(customer) if customer else None
    else:
        issue_dict["customer"] = None

    # SLA info
    if issue["sla_id"]:
        st = Table("service_level_agreement")
        sq = Q.from_(st).select(st.star).where(st.id == P())
        sla = conn.execute(sq.get_sql(), (issue["sla_id"],)).fetchone()
        issue_dict["sla"] = row_to_dict(sla) if sla else None
    else:
        issue_dict["sla"] = None

    # Comments
    ic = Table("issue_comment")
    icq = Q.from_(ic).select(ic.star).where(ic.issue_id == P()).orderby(ic.created_at)
    comments = conn.execute(icq.get_sql(), (args.issue_id,)).fetchall()
    issue_dict["comments"] = [row_to_dict(c) for c in comments]

    # SLA status check
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    is_response_overdue = False
    is_resolution_overdue = False

    if issue["response_due"] and issue["status"] not in ("resolved", "closed"):
        # Overdue if no first response yet and past due
        if not issue["first_response_at"] and now_str > issue["response_due"]:
            is_response_overdue = True

    if issue["resolution_due"] and issue["status"] not in ("resolved", "closed"):
        if now_str > issue["resolution_due"]:
            is_resolution_overdue = True

    issue_dict["sla_status"] = {
        "is_response_overdue": is_response_overdue,
        "is_resolution_overdue": is_resolution_overdue,
        "sla_breached": bool(issue["sla_breached"]),
    }

    ok({"issue": issue_dict})


# ---------------------------------------------------------------------------
# 4. list-issues
# ---------------------------------------------------------------------------

def list_issues(conn, args):
    """List issues with optional filters.

    Optional: --status, --priority, --customer-id, --assigned-to,
              --company-id, --limit, --offset
    """
    it = Table("issue")
    params = []

    q = Q.from_(it).select(it.star)
    q_cnt = Q.from_(it).select(fn.Count("*").as_("cnt"))

    if args.company_id:
        ct = Table("customer")
        q = q.join(ct).on(it.customer_id == ct.id)
        q_cnt = q_cnt.join(ct).on(it.customer_id == ct.id)
        q = q.where(ct.company_id == P())
        q_cnt = q_cnt.where(ct.company_id == P())
        params.append(args.company_id)

    if args.status:
        q = q.where(it.status == P())
        q_cnt = q_cnt.where(it.status == P())
        params.append(args.status)
    if args.priority:
        q = q.where(it.priority == P())
        q_cnt = q_cnt.where(it.priority == P())
        params.append(args.priority)
    if args.customer_id:
        q = q.where(it.customer_id == P())
        q_cnt = q_cnt.where(it.customer_id == P())
        params.append(args.customer_id)
    if args.assigned_to:
        q = q.where(it.assigned_to == P())
        q_cnt = q_cnt.where(it.assigned_to == P())
        params.append(args.assigned_to)

    limit = int(args.limit or 20)
    offset = int(args.offset or 0)

    q = q.orderby(it.created_at, order=Order.desc).limit(P()).offset(P())
    rows = conn.execute(q.get_sql(), params + [limit, offset]).fetchall()

    total = conn.execute(q_cnt.get_sql(), params).fetchone()["cnt"]

    ok({
        "issues": [row_to_dict(r) for r in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total,
    })


# ---------------------------------------------------------------------------
# 5. add-issue-comment
# ---------------------------------------------------------------------------

def add_issue_comment(conn, args):
    """Add a comment to an issue.

    Required: --issue-id, --comment
    Optional: --comment-by (default 'employee'), --is-internal (default '0')
    """
    if not args.issue_id:
        err("--issue-id is required")
    if not args.comment:
        err("--comment is required")

    issue = _validate_issue_exists(conn, args.issue_id)

    if issue["status"] == "closed":
        err("Cannot add comment to a closed issue. Reopen it first.")

    comment_by = args.comment_by or "employee"
    if comment_by not in VALID_COMMENT_BY:
        err(f"--comment-by must be one of {VALID_COMMENT_BY}")

    is_internal = args.is_internal or "0"

    comment_id = str(uuid.uuid4())

    ins_sql, _ = insert_row("issue_comment", {
        "id": P(), "issue_id": P(), "comment_by": P(),
        "comment_text": P(), "is_internal": P(),
    })
    conn.execute(ins_sql, (
        comment_id, args.issue_id, comment_by, args.comment, int(is_internal),
    ))

    # Track first employee response for SLA
    if comment_by == "employee" and not issue["first_response_at"]:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        sla_breached = issue["sla_breached"]

        # Check if response is overdue
        if issue["response_due"] and now_str > issue["response_due"]:
            sla_breached = 1

        upd_sql = update_row("issue", {
            "first_response_at": P(),
            "sla_breached": P(),
            "updated_at": LiteralValue("datetime('now')"),
        }, where={"id": P()})
        conn.execute(upd_sql, (now_str, sla_breached, args.issue_id))

    audit(conn, "erpclaw-support", "add-issue-comment", "issue_comment", comment_id,
           new_values={"issue_id": args.issue_id, "comment_by": comment_by},
           description=f"Comment added to issue by {comment_by}")
    conn.commit()

    ok({
        "comment": {
            "id": comment_id,
            "issue_id": args.issue_id,
            "comment_by": comment_by,
            "comment_text": args.comment,
            "is_internal": int(is_internal),
        },
        "message": f"Comment added to issue {issue['naming_series']}",
    })


# ---------------------------------------------------------------------------
# 6. resolve-issue
# ---------------------------------------------------------------------------

def resolve_issue(conn, args):
    """Resolve an issue.

    Required: --issue-id
    Optional: --resolution-notes
    """
    if not args.issue_id:
        err("--issue-id is required")

    issue = _validate_issue_exists(conn, args.issue_id)

    if issue["status"] in ("closed", "resolved"):
        err(f"Issue is already {issue['status']}.")

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    sla_breached = issue["sla_breached"]

    # Check if resolution is overdue
    if issue["resolution_due"] and now_str > issue["resolution_due"]:
        sla_breached = 1

    upd_sql = update_row("issue", {
        "status": P(),
        "resolved_at": P(),
        "resolution_notes": P(),
        "sla_breached": P(),
        "updated_at": LiteralValue("datetime('now')"),
    }, where={"id": P()})
    conn.execute(upd_sql, ("resolved", now_str, args.resolution_notes,
                           sla_breached, args.issue_id))

    audit(conn, "erpclaw-support", "resolve-issue", "issue", args.issue_id,
           old_values={"status": issue["status"]},
           new_values={"status": "resolved", "resolved_at": now_str},
           description=f"Issue resolved")
    conn.commit()

    it = Table("issue")
    rq = Q.from_(it).select(it.star).where(it.id == P())
    updated = conn.execute(rq.get_sql(), (args.issue_id,)).fetchone()

    ok({
        "issue": row_to_dict(updated),
        "message": f"Issue {updated['naming_series']} resolved",
    })


# ---------------------------------------------------------------------------
# 7. reopen-issue
# ---------------------------------------------------------------------------

def reopen_issue(conn, args):
    """Reopen a resolved or closed issue.

    Required: --issue-id
    Optional: --reason (for audit trail only, not stored in DB)
    """
    if not args.issue_id:
        err("--issue-id is required")

    issue = _validate_issue_exists(conn, args.issue_id)

    if issue["status"] not in ("resolved", "closed"):
        err(f"Cannot reopen issue with status '{issue['status']}'. "
             "Only resolved or closed issues can be reopened.")

    # Reopen: set status to open, clear resolved_at and resolution_notes
    # Do NOT reset sla_breached (once breached, stays breached)
    upd_sql = update_row("issue", {
        "status": P(),
        "resolved_at": P(),
        "resolution_notes": P(),
        "updated_at": LiteralValue("datetime('now')"),
    }, where={"id": P()})
    conn.execute(upd_sql, ("open", None, None, args.issue_id))

    reason = getattr(args, "reason", None) or "No reason provided"
    audit(conn, "erpclaw-support", "reopen-issue", "issue", args.issue_id,
           old_values={"status": issue["status"]},
           new_values={"status": "open"},
           description=f"Issue reopened: {reason}")
    conn.commit()

    it = Table("issue")
    rq = Q.from_(it).select(it.star).where(it.id == P())
    updated = conn.execute(rq.get_sql(), (args.issue_id,)).fetchone()

    ok({
        "issue": row_to_dict(updated),
        "message": f"Issue {updated['naming_series']} reopened",
    })


# ---------------------------------------------------------------------------
# 8. add-sla
# ---------------------------------------------------------------------------

def add_sla(conn, args):
    """Add a new Service Level Agreement.

    Required: --name, --priorities (JSON string)
    Optional: --working-hours, --is-default
    """
    if not args.name:
        err("--name is required")
    if not args.priorities:
        err("--priorities is required (JSON with response_times and resolution_times)")

    priorities = _parse_json_arg(args.priorities, "priorities")
    if not isinstance(priorities, dict):
        err("--priorities must be a JSON object")

    response_times = priorities.get("response_times")
    resolution_times = priorities.get("resolution_times")

    if not isinstance(response_times, dict):
        err("priorities.response_times must be a JSON object (e.g. {\"low\": 24, \"high\": 4})")
    if not isinstance(resolution_times, dict):
        err("priorities.resolution_times must be a JSON object (e.g. {\"low\": 72, \"high\": 12})")

    is_default = args.is_default or "0"

    # If setting as default, clear existing defaults
    if is_default == "1":
        clear_sql = update_row("service_level_agreement",
                               data={"is_default": P()},
                               where={"is_default": P()})
        conn.execute(clear_sql, (0, 1))

    sla_id = str(uuid.uuid4())

    ins_sql, _ = insert_row("service_level_agreement", {
        "id": P(), "name": P(), "priority_response_times": P(),
        "priority_resolution_times": P(), "working_hours": P(), "is_default": P(),
    })
    conn.execute(ins_sql, (
        sla_id, args.name, json.dumps(response_times),
        json.dumps(resolution_times), args.working_hours, int(is_default),
    ))

    audit(conn, "erpclaw-support", "add-sla", "service_level_agreement", sla_id,
           new_values={"name": args.name, "is_default": is_default},
           description=f"Created SLA: {args.name}")
    conn.commit()

    ok({
        "sla": {
            "id": sla_id,
            "name": args.name,
            "priority_response_times": response_times,
            "priority_resolution_times": resolution_times,
            "working_hours": args.working_hours,
            "is_default": int(is_default),
        },
        "message": f"SLA '{args.name}' created",
    })


# ---------------------------------------------------------------------------
# 9. list-slas
# ---------------------------------------------------------------------------

def list_slas(conn, args):
    """List all Service Level Agreements.

    Optional: --limit, --offset
    """
    limit = int(args.limit or 20)
    offset = int(args.offset or 0)

    st = Table("service_level_agreement")
    q = (Q.from_(st).select(st.star)
         .orderby(st.name).limit(P()).offset(P()))
    rows = conn.execute(q.get_sql(), (limit, offset)).fetchall()

    q_cnt = Q.from_(st).select(fn.Count("*").as_("cnt"))
    total = conn.execute(q_cnt.get_sql()).fetchone()["cnt"]

    slas = []
    for r in rows:
        d = row_to_dict(r)
        # Parse JSON fields for readability
        try:
            if d.get("priority_response_times"):
                d["priority_response_times"] = json.loads(d["priority_response_times"])
        except (json.JSONDecodeError, TypeError):
            pass
        try:
            if d.get("priority_resolution_times"):
                d["priority_resolution_times"] = json.loads(d["priority_resolution_times"])
        except (json.JSONDecodeError, TypeError):
            pass
        slas.append(d)

    ok({
        "slas": slas,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total,
    })


# ---------------------------------------------------------------------------
# 10. add-warranty-claim
# ---------------------------------------------------------------------------

def add_warranty_claim(conn, args):
    """Create a new warranty claim.

    Required: --customer-id, --complaint-description
    Optional: --item-id, --serial-number-id, --warranty-expiry-date
    """
    if not args.customer_id:
        err("--customer-id is required")
    if not args.complaint_description:
        err("--complaint-description is required")

    # Validate customer exists and resolve company_id for naming
    ct = Table("customer")
    cq = Q.from_(ct).select(ct.id, ct.company_id, ct.name).where(ct.id == P())
    cust = conn.execute(cq.get_sql(), (args.customer_id,)).fetchone()
    if not cust:
        err(f"Customer {args.customer_id} not found")

    company_id = cust["company_id"]
    conn.company_id = company_id

    claim_id = str(uuid.uuid4())
    naming = get_next_name(conn, "warranty_claim")

    ins_sql, _ = insert_row("warranty_claim", {
        "id": P(), "naming_series": P(), "customer_id": P(),
        "item_id": P(), "serial_number_id": P(),
        "warranty_expiry_date": P(), "complaint_description": P(),
    })
    conn.execute(ins_sql, (
        claim_id, naming, args.customer_id, args.item_id,
        args.serial_number_id, args.warranty_expiry_date,
        args.complaint_description,
    ))

    audit(conn, "erpclaw-support", "add-warranty-claim", "warranty_claim", claim_id,
           new_values={"customer_id": args.customer_id,
                       "complaint_description": args.complaint_description},
           description=f"Created warranty claim {naming}")
    conn.commit()

    wt = Table("warranty_claim")
    rq = Q.from_(wt).select(wt.star).where(wt.id == P())
    claim = conn.execute(rq.get_sql(), (claim_id,)).fetchone()

    ok({
        "warranty_claim": row_to_dict(claim),
        "message": f"Warranty claim {naming} created",
    })


# ---------------------------------------------------------------------------
# 11. update-warranty-claim
# ---------------------------------------------------------------------------

def update_warranty_claim(conn, args):
    """Update a warranty claim.

    Required: --warranty-claim-id
    Optional: --status, --resolution, --resolution-date, --cost
    """
    if not args.warranty_claim_id:
        err("--warranty-claim-id is required")

    wt = Table("warranty_claim")
    wq = Q.from_(wt).select(wt.star).where(wt.id == P())
    claim = conn.execute(wq.get_sql(), (args.warranty_claim_id,)).fetchone()
    if not claim:
        err(f"Warranty claim {args.warranty_claim_id} not found")

    if claim["status"] == "closed":
        err("Cannot update a closed warranty claim",
             suggestion="Reopen the warranty claim first, then make changes.")

    old_values = row_to_dict(claim)

    data = {}
    values = []

    if args.status is not None:
        if args.status not in VALID_WARRANTY_STATUSES:
            err(f"--status must be one of {VALID_WARRANTY_STATUSES}")
        data["status"] = P()
        values.append(args.status)

    if args.resolution is not None:
        if args.resolution not in VALID_WARRANTY_RESOLUTIONS:
            err(f"--resolution must be one of {VALID_WARRANTY_RESOLUTIONS}")
        data["resolution"] = P()
        values.append(args.resolution)

    if args.resolution_date is not None:
        data["resolution_date"] = P()
        values.append(args.resolution_date)

    if args.cost is not None:
        try:
            to_decimal(args.cost)
        except Exception:
            err(f"--cost must be a valid decimal value, got: {args.cost}")
        data["cost"] = P()
        values.append(args.cost)

    if not data:
        err("No fields to update. Provide at least one optional flag.")

    data["updated_at"] = LiteralValue("datetime('now')")
    values.append(args.warranty_claim_id)
    upd_sql = update_row("warranty_claim", data, where={"id": P()})
    conn.execute(upd_sql, values)

    audit(conn, "erpclaw-support", "update-warranty-claim", "warranty_claim",
           args.warranty_claim_id,
           old_values=old_values,
           description="Updated warranty claim")
    conn.commit()

    wt2 = Table("warranty_claim")
    rq = Q.from_(wt2).select(wt2.star).where(wt2.id == P())
    updated = conn.execute(rq.get_sql(), (args.warranty_claim_id,)).fetchone()

    ok({
        "warranty_claim": row_to_dict(updated),
        "message": f"Warranty claim {updated['naming_series']} updated",
    })


# ---------------------------------------------------------------------------
# 12. list-warranty-claims
# ---------------------------------------------------------------------------

def list_warranty_claims(conn, args):
    """List warranty claims with optional filters.

    Optional: --customer-id, --status, --limit, --offset
    """
    wc = Table("warranty_claim")
    ct = Table("customer")
    params = []

    q = (Q.from_(wc)
         .left_join(ct).on(ct.id == wc.customer_id)
         .select(wc.star, ct.name.as_("customer_name")))
    q_cnt = Q.from_(wc).select(fn.Count("*").as_("cnt"))

    if args.customer_id:
        q = q.where(wc.customer_id == P())
        q_cnt = q_cnt.where(wc.customer_id == P())
        params.append(args.customer_id)
    if args.status:
        q = q.where(wc.status == P())
        q_cnt = q_cnt.where(wc.status == P())
        params.append(args.status)

    limit = int(args.limit or 20)
    offset = int(args.offset or 0)

    q = q.orderby(wc.created_at, order=Order.desc).limit(P()).offset(P())
    rows = conn.execute(q.get_sql(), params + [limit, offset]).fetchall()

    total = conn.execute(q_cnt.get_sql(), params).fetchone()["cnt"]

    ok({
        "warranty_claims": [row_to_dict(r) for r in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total,
    })


# ---------------------------------------------------------------------------
# 13. add-maintenance-schedule
# ---------------------------------------------------------------------------

def add_maintenance_schedule(conn, args):
    """Create a new maintenance schedule.

    Required: --customer-id, --start-date, --end-date
    Optional: --item-id, --serial-number-id, --schedule-frequency (default quarterly),
              --assigned-to
    """
    if not args.customer_id:
        err("--customer-id is required")
    if not args.start_date:
        err("--start-date is required")
    if not args.end_date:
        err("--end-date is required")

    frequency = args.schedule_frequency or "quarterly"
    if frequency not in VALID_SCHEDULE_FREQUENCIES:
        err(f"--schedule-frequency must be one of {VALID_SCHEDULE_FREQUENCIES}")

    # Validate customer exists and resolve company_id for naming
    ct = Table("customer")
    cq = Q.from_(ct).select(ct.id, ct.company_id, ct.name).where(ct.id == P())
    cust = conn.execute(cq.get_sql(), (args.customer_id,)).fetchone()
    if not cust:
        err(f"Customer {args.customer_id} not found")

    conn.company_id = cust["company_id"]

    schedule_id = str(uuid.uuid4())
    naming = get_next_name(conn, "maintenance_schedule")
    next_due = _calc_next_due_date(args.start_date, frequency)

    ins_sql, _ = insert_row("maintenance_schedule", {
        "id": P(), "naming_series": P(), "customer_id": P(),
        "item_id": P(), "serial_number_id": P(),
        "schedule_frequency": P(), "start_date": P(), "end_date": P(),
        "next_due_date": P(), "status": P(), "assigned_to": P(),
    })
    conn.execute(ins_sql, (
        schedule_id, naming, args.customer_id, args.item_id,
        args.serial_number_id, frequency, args.start_date, args.end_date,
        next_due, "active", args.assigned_to,
    ))

    audit(conn, "erpclaw-support", "add-maintenance-schedule", "maintenance_schedule", schedule_id,
           new_values={"customer_id": args.customer_id,
                       "frequency": frequency,
                       "start_date": args.start_date,
                       "end_date": args.end_date},
           description=f"Created maintenance schedule {naming}")
    conn.commit()

    ms = Table("maintenance_schedule")
    rq = Q.from_(ms).select(ms.star).where(ms.id == P())
    sched = conn.execute(rq.get_sql(), (schedule_id,)).fetchone()

    ok({
        "maintenance_schedule": row_to_dict(sched),
        "message": f"Maintenance schedule {naming} created (next due: {next_due})",
    })


# ---------------------------------------------------------------------------
# 14. list-maintenance-schedules
# ---------------------------------------------------------------------------

def list_maintenance_schedules(conn, args):
    """List maintenance schedules with optional filters.

    Optional: --customer-id, --item-id, --status, --limit, --offset
    """
    ms = Table("maintenance_schedule")
    ct = Table("customer")
    params = []

    q = (Q.from_(ms)
         .left_join(ct).on(ct.id == ms.customer_id)
         .select(ms.star, ct.name.as_("customer_name")))
    q_cnt = Q.from_(ms).select(fn.Count("*").as_("cnt"))

    if args.customer_id:
        q = q.where(ms.customer_id == P())
        q_cnt = q_cnt.where(ms.customer_id == P())
        params.append(args.customer_id)
    if args.item_id:
        q = q.where(ms.item_id == P())
        q_cnt = q_cnt.where(ms.item_id == P())
        params.append(args.item_id)
    if args.status:
        q = q.where(ms.status == P())
        q_cnt = q_cnt.where(ms.status == P())
        params.append(args.status)

    limit = int(args.limit or 20)
    offset = int(args.offset or 0)

    q = q.orderby(ms.created_at, order=Order.desc).limit(P()).offset(P())
    rows = conn.execute(q.get_sql(), params + [limit, offset]).fetchall()

    total = conn.execute(q_cnt.get_sql(), params).fetchone()["cnt"]

    ok({
        "maintenance_schedules": [row_to_dict(r) for r in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total,
    })


# ---------------------------------------------------------------------------
# 15. record-maintenance-visit
# ---------------------------------------------------------------------------

def record_maintenance_visit(conn, args):
    """Record a maintenance visit against a schedule.

    Required: --schedule-id, --visit-date
    Optional: --completed-by, --observations, --work-done,
              --status (default 'scheduled')
    """
    if not args.schedule_id:
        err("--schedule-id is required")
    if not args.visit_date:
        err("--visit-date is required")

    visit_status = args.status or "scheduled"
    if visit_status not in VALID_VISIT_STATUSES:
        err(f"--status must be one of {VALID_VISIT_STATUSES}")

    # Validate schedule exists
    mst = Table("maintenance_schedule")
    sq = Q.from_(mst).select(mst.star).where(mst.id == P())
    sched = conn.execute(sq.get_sql(), (args.schedule_id,)).fetchone()
    if not sched:
        err(f"Maintenance schedule {args.schedule_id} not found")

    # Resolve company_id from schedule's customer for naming
    ct = Table("customer")
    cq = Q.from_(ct).select(ct.company_id).where(ct.id == P())
    cust = conn.execute(cq.get_sql(), (sched["customer_id"],)).fetchone()
    if cust:
        conn.company_id = cust["company_id"]

    visit_id = str(uuid.uuid4())
    naming = get_next_name(conn, "maintenance_visit")

    ins_sql, _ = insert_row("maintenance_visit", {
        "id": P(), "naming_series": P(), "maintenance_schedule_id": P(),
        "customer_id": P(), "visit_date": P(), "completed_by": P(),
        "observations": P(), "work_done": P(), "status": P(),
    })
    conn.execute(ins_sql, (
        visit_id, naming, args.schedule_id, sched["customer_id"],
        args.visit_date, args.completed_by, args.observations,
        args.work_done, visit_status,
    ))

    schedule_updated = False

    # If visit is completed, update the schedule
    if visit_status == "completed":
        new_next_due = _calc_next_due_date(
            args.visit_date, sched["schedule_frequency"],
        )

        if new_next_due > sched["end_date"]:
            upd_sql = update_row("maintenance_schedule", {
                "last_completed_date": P(),
                "next_due_date": P(),
                "status": P(),
                "updated_at": LiteralValue("datetime('now')"),
            }, where={"id": P()})
            conn.execute(upd_sql, (args.visit_date, new_next_due, "expired",
                                   args.schedule_id))
        else:
            upd_sql = update_row("maintenance_schedule", {
                "last_completed_date": P(),
                "next_due_date": P(),
                "updated_at": LiteralValue("datetime('now')"),
            }, where={"id": P()})
            conn.execute(upd_sql, (args.visit_date, new_next_due,
                                   args.schedule_id))
        schedule_updated = True

    audit(conn, "erpclaw-support", "record-maintenance-visit", "maintenance_visit", visit_id,
           new_values={"schedule_id": args.schedule_id,
                       "visit_date": args.visit_date,
                       "status": visit_status},
           description=f"Recorded maintenance visit {naming}")
    conn.commit()

    mvt = Table("maintenance_visit")
    vq = Q.from_(mvt).select(mvt.star).where(mvt.id == P())
    visit = conn.execute(vq.get_sql(), (visit_id,)).fetchone()

    resp = {
        "visit": row_to_dict(visit),
        "schedule_updated": schedule_updated,
        "message": f"Maintenance visit {naming} recorded",
    }

    if schedule_updated:
        mst2 = Table("maintenance_schedule")
        sq2 = Q.from_(mst2).select(mst2.star).where(mst2.id == P())
        updated_sched = conn.execute(sq2.get_sql(), (args.schedule_id,)).fetchone()
        resp["schedule"] = row_to_dict(updated_sched)

    ok(resp)


# ---------------------------------------------------------------------------
# 16. sla-compliance-report
# ---------------------------------------------------------------------------

def sla_compliance_report(conn, args):
    """SLA compliance report.

    Optional: --company-id, --from-date, --to-date
    """
    i = Table("issue")
    params = []

    breached_case = Case().when(i.sla_breached == 1, 1).else_(0)
    compliant_case = (Case()
                      .when((i.sla_breached == 0) & i.status.isin(["resolved", "closed"]), 1)
                      .else_(0))
    in_progress_case = (Case()
                        .when(Not(i.status.isin(["resolved", "closed"])), 1)
                        .else_(0))

    q = (Q.from_(i)
         .select(
             fn.Count("*").as_("total_with_sla"),
             fn.Sum(breached_case).as_("breached"),
             fn.Sum(compliant_case).as_("compliant"),
             fn.Sum(in_progress_case).as_("in_progress"),
         )
         .where(i.sla_id.isnotnull()))

    if args.company_id:
        ct = Table("customer")
        sub = Q.from_(ct).select(ct.id).where(ct.company_id == P())
        q = q.where(i.customer_id.isin(sub))
        params.append(args.company_id)
    if args.from_date:
        q = q.where(i.created_at >= P())
        params.append(args.from_date)
    if args.to_date:
        q = q.where(i.created_at <= P())
        params.append(args.to_date + " 23:59:59")

    row = conn.execute(q.get_sql(), params).fetchone()

    total_with_sla = row["total_with_sla"] or 0
    breached = row["breached"] or 0
    compliant = row["compliant"] or 0
    in_progress = row["in_progress"] or 0

    denominator = compliant + breached
    if denominator > 0:
        rate = (Decimal(str(compliant)) / Decimal(str(denominator)) * Decimal("100")
                ).quantize(Decimal("0.01"))
        compliance_rate_pct = str(rate)
    else:
        compliance_rate_pct = "0.00"

    ok({
        "report": {
            "total_with_sla": total_with_sla,
            "breached": breached,
            "compliant": compliant,
            "in_progress": in_progress,
            "compliance_rate_pct": compliance_rate_pct,
        },
        "filters": {
            k: v for k, v in {
                "company_id": args.company_id,
                "from_date": args.from_date,
                "to_date": args.to_date,
            }.items() if v
        },
        "message": f"SLA compliance: {compliance_rate_pct}% ({compliant}/{denominator})",
    })


# ---------------------------------------------------------------------------
# 17. overdue-issues-report
# ---------------------------------------------------------------------------

def overdue_issues_report(conn, args):
    """Report on overdue issues (past SLA response or resolution due).

    Optional: --company-id
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    it = Table("issue")
    ct = Table("customer")
    params = [now, now]

    response_overdue = (it.response_due.isnotnull()
                        & (it.response_due < P())
                        & it.first_response_at.isnull())
    resolution_overdue = it.resolution_due.isnotnull() & (it.resolution_due < P())

    q = (Q.from_(it)
         .left_join(ct).on(ct.id == it.customer_id)
         .select(it.star, ct.name.as_("customer_name"))
         .where(Not(it.status.isin(["resolved", "closed"])))
         .where(response_overdue | resolution_overdue)
         .orderby(it.created_at))

    if args.company_id:
        cust_t = Table("customer")
        sub = Q.from_(cust_t).select(cust_t.id).where(cust_t.company_id == P())
        q = q.where(it.customer_id.isin(sub))
        params.append(args.company_id)

    rows = conn.execute(q.get_sql(), params).fetchall()

    overdue_list = []
    for r in rows:
        entry = row_to_dict(r)
        overdue_response = False
        overdue_resolution = False

        if (r["response_due"] and r["response_due"] < now
                and r["first_response_at"] is None):
            overdue_response = True

        if r["resolution_due"] and r["resolution_due"] < now:
            overdue_resolution = True

        entry["overdue_response"] = overdue_response
        entry["overdue_resolution"] = overdue_resolution
        overdue_list.append(entry)

    ok({
        "overdue_issues": overdue_list,
        "total": len(overdue_list),
        "as_of": now,
        "message": f"{len(overdue_list)} overdue issue(s) found",
    })


# ---------------------------------------------------------------------------
# 18. status
# ---------------------------------------------------------------------------

def status_action(conn, args):
    """Support module status summary.

    Optional: --company-id
    """
    # Build optional company subquery filter
    company_sub = None
    company_params = []
    if args.company_id:
        cust_t = Table("customer")
        company_sub = Q.from_(cust_t).select(cust_t.id).where(cust_t.company_id == P())
        company_params = [args.company_id]

    def _count(table_name, extra_where=None):
        """Count rows with optional company filter and extra condition."""
        t = Table(table_name)
        q = Q.from_(t).select(fn.Count("*").as_("cnt"))
        if extra_where is not None:
            q = q.where(extra_where(t))
        p = list(company_params)
        if company_sub is not None:
            q = q.where(t.customer_id.isin(company_sub))
        return conn.execute(q.get_sql(), p).fetchone()["cnt"]

    # Issues
    issue_total = _count("issue")
    issue_open = _count("issue", lambda t: t.status == "open")
    issue_in_progress = _count("issue", lambda t: t.status == "in_progress")
    issue_resolved = _count("issue", lambda t: t.status == "resolved")
    issue_closed = _count("issue", lambda t: t.status == "closed")
    issue_breached = _count("issue", lambda t: t.sla_breached == 1)

    # Warranty claims
    wc_total = _count("warranty_claim")
    wc_open = _count("warranty_claim", lambda t: t.status == "open")
    wc_in_progress = _count("warranty_claim", lambda t: t.status == "in_progress")
    wc_resolved = _count("warranty_claim", lambda t: t.status == "resolved")

    # Maintenance schedules
    ms_total = _count("maintenance_schedule")
    ms_active = _count("maintenance_schedule", lambda t: t.status == "active")
    ms_expired = _count("maintenance_schedule", lambda t: t.status == "expired")

    # Maintenance visits (filter via schedule → customer)
    mvt = Table("maintenance_visit")
    mv_params = []

    def _mv_count(extra_where=None):
        q = Q.from_(mvt).select(fn.Count("*").as_("cnt"))
        if extra_where is not None:
            q = q.where(extra_where(mvt))
        p = list(mv_params)
        if args.company_id:
            mst = Table("maintenance_schedule")
            cust_t2 = Table("customer")
            inner_sub = Q.from_(cust_t2).select(cust_t2.id).where(cust_t2.company_id == P())
            sched_sub = Q.from_(mst).select(mst.id).where(mst.customer_id.isin(inner_sub))
            q = q.where(mvt.maintenance_schedule_id.isin(sched_sub))
            p.append(args.company_id)
        return conn.execute(q.get_sql(), p).fetchone()["cnt"]

    mv_total = _mv_count()
    mv_scheduled = _mv_count(lambda t: t.status == "scheduled")
    mv_completed = _mv_count(lambda t: t.status == "completed")

    # Overdue issues count
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    it = Table("issue")
    overdue_params = [now, now]

    response_overdue = (it.response_due.isnotnull()
                        & (it.response_due < P())
                        & it.first_response_at.isnull())
    resolution_overdue = it.resolution_due.isnotnull() & (it.resolution_due < P())

    oq = (Q.from_(it).select(fn.Count("*").as_("cnt"))
           .where(Not(it.status.isin(["resolved", "closed"])))
           .where(response_overdue | resolution_overdue))

    if args.company_id:
        cust_t3 = Table("customer")
        co_sub = Q.from_(cust_t3).select(cust_t3.id).where(cust_t3.company_id == P())
        oq = oq.where(it.customer_id.isin(co_sub))
        overdue_params.append(args.company_id)

    overdue_count = conn.execute(oq.get_sql(), overdue_params).fetchone()["cnt"]

    ok({
        "support_status": {
            "issues": {
                "total": issue_total,
                "open": issue_open,
                "in_progress": issue_in_progress,
                "resolved": issue_resolved,
                "closed": issue_closed,
                "breached": issue_breached,
            },
            "warranty_claims": {
                "total": wc_total,
                "open": wc_open,
                "in_progress": wc_in_progress,
                "resolved": wc_resolved,
            },
            "maintenance_schedules": {
                "total": ms_total,
                "active": ms_active,
                "expired": ms_expired,
            },
            "maintenance_visits": {
                "total": mv_total,
                "scheduled": mv_scheduled,
                "completed": mv_completed,
            },
            "overdue_issues": overdue_count,
        },
        "message": (
            f"Support: {issue_open} open issues, {wc_open} open claims, "
            f"{ms_active} active schedules, {overdue_count} overdue"
        ),
    })


# ---------------------------------------------------------------------------
# Action registry
# ---------------------------------------------------------------------------

ACTIONS = {
    "add-issue": add_issue,
    "update-issue": update_issue,
    "get-issue": get_issue,
    "list-issues": list_issues,
    "add-issue-comment": add_issue_comment,
    "resolve-issue": resolve_issue,
    "reopen-issue": reopen_issue,
    "add-sla": add_sla,
    "list-slas": list_slas,
    "add-warranty-claim": add_warranty_claim,
    "update-warranty-claim": update_warranty_claim,
    "list-warranty-claims": list_warranty_claims,
    "add-maintenance-schedule": add_maintenance_schedule,
    "list-maintenance-schedules": list_maintenance_schedules,
    "record-maintenance-visit": record_maintenance_visit,
    "sla-compliance-report": sla_compliance_report,
    "overdue-issues-report": overdue_issues_report,
    "status": status_action,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ERPClaw Support Skill")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)
    parser.add_argument("--company-id")

    # Issue fields
    parser.add_argument("--issue-id")
    parser.add_argument("--subject")
    parser.add_argument("--description")
    parser.add_argument("--priority")
    parser.add_argument("--issue-type")
    parser.add_argument("--assigned-to")
    parser.add_argument("--resolution-notes")
    parser.add_argument("--reason")

    # SLA fields
    parser.add_argument("--sla-id")
    parser.add_argument("--name")
    parser.add_argument("--priorities")
    parser.add_argument("--working-hours")
    parser.add_argument("--is-default")

    # Comment fields
    parser.add_argument("--comment")
    parser.add_argument("--comment-by")
    parser.add_argument("--is-internal")

    # Customer / item / serial
    parser.add_argument("--customer-id")
    parser.add_argument("--item-id")
    parser.add_argument("--serial-number-id")

    # Warranty fields
    parser.add_argument("--warranty-claim-id")
    parser.add_argument("--warranty-expiry-date")
    parser.add_argument("--complaint-description")
    parser.add_argument("--resolution")
    parser.add_argument("--resolution-date")
    parser.add_argument("--cost")

    # Maintenance fields
    parser.add_argument("--schedule-id")
    parser.add_argument("--schedule-frequency")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--visit-date")
    parser.add_argument("--completed-by")
    parser.add_argument("--observations")
    parser.add_argument("--work-done")

    # Filters
    parser.add_argument("--status")
    parser.add_argument("--from-date")
    parser.add_argument("--to-date")
    parser.add_argument("--limit", default="20")
    parser.add_argument("--offset", default="0")

    args, _unknown = parser.parse_known_args()
    check_input_lengths(args)

    db_path = args.db_path or DEFAULT_DB_PATH
    ensure_db_exists(db_path)
    conn = get_connection(db_path)

    # Dependency check
    _dep = check_required_tables(conn, REQUIRED_TABLES)
    if _dep:
        _dep["suggestion"] = "clawhub install " + " ".join(_dep.get("missing_skills", []))
        print(json.dumps(_dep, indent=2))
        conn.close()
        sys.exit(1)

    try:
        ACTIONS[args.action](conn, args)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
