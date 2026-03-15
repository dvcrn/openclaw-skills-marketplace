#!/usr/bin/env python3
"""ERPClaw CRM Skill -- db_query.py

Lead management, opportunity pipeline, campaigns, and activity tracking.
All 18 actions are routed through this single entry point.

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout, exit 0 on success, exit 1 on error.
"""
import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
import uuid
from datetime import datetime, timezone
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
    from erpclaw_lib.query import Q, P, Table, Field, fn, Case, Order, Criterion, Not, NULL, insert_row, update_row
    from erpclaw_lib.vendor.pypika.terms import LiteralValue, ValueWrapper
except ImportError:
    import json as _json
    print(_json.dumps({"status": "error", "error": "ERPClaw foundation not installed. Install erpclaw first: clawhub install erpclaw", "suggestion": "clawhub install erpclaw"}))
    sys.exit(1)

REQUIRED_TABLES = ["company"]

VALID_LEAD_SOURCES = ("website", "referral", "campaign", "cold_call",
                      "social_media", "trade_show", "other")
VALID_LEAD_STATUSES = ("new", "contacted", "qualified", "converted",
                       "unresponsive", "lost")
VALID_OPP_STAGES = ("new", "contacted", "qualified", "proposal_sent",
                    "negotiation", "won", "lost")
VALID_OPP_TYPES = ("sales", "support", "maintenance")
VALID_CAMPAIGN_TYPES = ("email", "social", "event", "referral", "content")
VALID_CAMPAIGN_STATUSES = ("planned", "active", "completed")
VALID_ACTIVITY_TYPES = ("call", "email", "meeting", "note", "task")

# ---------------------------------------------------------------------------
# PyPika table references
# ---------------------------------------------------------------------------
_t_company = Table("company")
_t_lead = Table("lead")
_t_opportunity = Table("opportunity")
_t_customer = Table("customer")
_t_campaign = Table("campaign")
_t_campaign_lead = Table("campaign_lead")
_t_activity = Table("crm_activity")


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


def _calc_weighted_revenue(expected_revenue: str, probability: str) -> str:
    """Calculate weighted_revenue = expected_revenue * (probability / 100)."""
    rev = to_decimal(expected_revenue or "0")
    prob = to_decimal(probability or "0")
    weighted = (rev * prob / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return str(weighted)


# ---------------------------------------------------------------------------
# Company resolution
# ---------------------------------------------------------------------------

def _resolve_company_id(conn, args):
    """Resolve company_id from args or conn, set on conn for get_next_name()."""
    company_id = getattr(args, "company_id", None) or getattr(conn, "company_id", None)
    if not company_id:
        err("--company-id is required")
    # Validate company exists
    q = Q.from_(_t_company).select(_t_company.id).where(_t_company.id == P())
    comp = conn.execute(q.get_sql(), (company_id,)).fetchone()
    if not comp:
        err(f"Company {company_id} not found")
    # Set on conn so get_next_name() can find it
    conn.company_id = company_id
    return company_id


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _validate_lead_exists(conn, lead_id: str):
    q = Q.from_(_t_lead).select(_t_lead.star).where(_t_lead.id == P())
    lead = conn.execute(q.get_sql(), (lead_id,)).fetchone()
    if not lead:
        err(f"Lead {lead_id} not found",
             suggestion="Use 'list leads' to see available leads.")
    return lead


def _validate_opportunity_exists(conn, opp_id: str):
    q = Q.from_(_t_opportunity).select(_t_opportunity.star).where(_t_opportunity.id == P())
    opp = conn.execute(q.get_sql(), (opp_id,)).fetchone()
    if not opp:
        err(f"Opportunity {opp_id} not found",
             suggestion="Use 'list opportunities' to see available opportunities.")
    return opp


def _validate_customer_exists(conn, customer_id: str):
    q = Q.from_(_t_customer).select(_t_customer.star).where(_t_customer.id == P())
    cust = conn.execute(q.get_sql(), (customer_id,)).fetchone()
    if not cust:
        err(f"Customer {customer_id} not found")
    return cust


def _validate_campaign_exists(conn, campaign_id: str):
    q = Q.from_(_t_campaign).select(_t_campaign.star).where(_t_campaign.id == P())
    camp = conn.execute(q.get_sql(), (campaign_id,)).fetchone()
    if not camp:
        err(f"Campaign {campaign_id} not found")
    return camp


# ---------------------------------------------------------------------------
# 1. add-lead
# ---------------------------------------------------------------------------

def add_lead(conn, args):
    """Add a new lead.

    Required: --lead-name
    Optional: --company-name, --email, --phone, --source, --territory,
              --industry, --assigned-to, --notes
    """
    if not args.lead_name:
        err("--lead-name is required")

    if args.source and args.source not in VALID_LEAD_SOURCES:
        err(f"--source must be one of {VALID_LEAD_SOURCES}")

    # Validate email format if provided
    _EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    if args.email and not _EMAIL_RE.match(args.email):
        err(f"Invalid email format for --email: '{args.email}'")

    company_id = _resolve_company_id(conn, args)
    lead_id = str(uuid.uuid4())
    naming = get_next_name(conn, "lead")

    sql, _ = insert_row("lead", {
        "id": P(), "naming_series": P(), "lead_name": P(), "company_name": P(),
        "email": P(), "phone": P(), "source": P(), "territory": P(),
        "industry": P(), "status": ValueWrapper("new"), "assigned_to": P(),
        "notes": P(), "company_id": P(),
    })
    conn.execute(sql,
        (lead_id, naming, args.lead_name, args.company_name, args.email,
         args.phone, args.source, args.territory, args.industry,
         args.assigned_to, args.notes, company_id),
    )

    audit(conn, "erpclaw-crm", "add-lead", "lead", lead_id,
           new_values={"lead_name": args.lead_name, "source": args.source},
           description=f"Created lead: {args.lead_name}")
    conn.commit()

    ok({
        "lead": {
            "id": lead_id,
            "naming_series": naming,
            "lead_name": args.lead_name,
            "company_name": args.company_name,
            "email": args.email,
            "phone": args.phone,
            "source": args.source,
            "status": "new",
        },
        "message": f"Lead '{args.lead_name}' created ({naming})",
    })


# ---------------------------------------------------------------------------
# 2. update-lead
# ---------------------------------------------------------------------------

def update_lead(conn, args):
    """Update an existing lead.

    Required: --lead-id
    Optional: --lead-name, --company-name, --email, --phone, --source,
              --territory, --industry, --status, --assigned-to, --notes
    """
    if not args.lead_id:
        err("--lead-id is required")

    lead = _validate_lead_exists(conn, args.lead_id)
    old_values = row_to_dict(lead)

    # Frozen after conversion
    if lead["status"] == "converted":
        err("Cannot update a converted lead. Work with the opportunity instead.",
             suggestion="Use 'list opportunities' to find the opportunity created from this lead.")

    if args.source and args.source not in VALID_LEAD_SOURCES:
        err(f"--source must be one of {VALID_LEAD_SOURCES}")
    if args.status and args.status not in VALID_LEAD_STATUSES:
        err(f"--status must be one of {VALID_LEAD_STATUSES}")

    field_map = {
        "lead_name": args.lead_name,
        "company_name": args.company_name,
        "email": args.email,
        "phone": args.phone,
        "source": args.source,
        "territory": args.territory,
        "industry": args.industry,
        "status": args.status,
        "assigned_to": args.assigned_to,
        "notes": args.notes,
    }

    data = {k: P() for k, v in field_map.items() if v is not None}
    values = [v for v in field_map.values() if v is not None]

    if not data:
        err("No fields to update. Provide at least one optional flag.")

    data["updated_at"] = LiteralValue("datetime('now')")
    sql = update_row("lead", data, {"id": P()})
    values.append(args.lead_id)
    conn.execute(sql, values)

    audit(conn, "erpclaw-crm", "update-lead", "lead", args.lead_id,
           old_values=old_values,
           description="Updated lead")
    conn.commit()

    q = Q.from_(_t_lead).select(_t_lead.star).where(_t_lead.id == P())
    updated = conn.execute(q.get_sql(), (args.lead_id,)).fetchone()

    ok({
        "lead": row_to_dict(updated),
        "message": f"Lead {updated['naming_series']} updated",
    })


# ---------------------------------------------------------------------------
# 3. get-lead
# ---------------------------------------------------------------------------

def get_lead(conn, args):
    """Get lead details with activities and campaigns.

    Required: --lead-id
    """
    if not args.lead_id:
        err("--lead-id is required")

    lead = _validate_lead_exists(conn, args.lead_id)
    lead_dict = row_to_dict(lead)

    # Fetch activities for this lead
    q = (Q.from_(_t_activity).select(_t_activity.star)
         .where(_t_activity.lead_id == P())
         .orderby(_t_activity.activity_date, order=Order.desc))
    activities = conn.execute(q.get_sql(), (args.lead_id,)).fetchall()
    lead_dict["activities"] = [row_to_dict(a) for a in activities]

    # Fetch campaigns this lead is linked to
    c = _t_campaign
    cl = _t_campaign_lead
    q = (Q.from_(c).join(cl).on(cl.campaign_id == c.id)
         .select(c.star, cl.added_date, cl.converted)
         .where(cl.lead_id == P())
         .orderby(cl.added_date, order=Order.desc))
    campaigns = conn.execute(q.get_sql(), (args.lead_id,)).fetchall()
    lead_dict["campaigns"] = [row_to_dict(c) for c in campaigns]

    ok({"lead": lead_dict})


# ---------------------------------------------------------------------------
# 4. list-leads
# ---------------------------------------------------------------------------

def list_leads(conn, args):
    """List leads with optional filters.

    Optional: --status, --source, --search, --limit, --offset
    """
    t = _t_lead
    q = Q.from_(t).select(t.star)
    q_cnt = Q.from_(t).select(fn.Count("*").as_("cnt"))
    params = []

    if args.status:
        q = q.where(t.status == P())
        q_cnt = q_cnt.where(t.status == P())
        params.append(args.status)
    if args.source:
        q = q.where(t.source == P())
        q_cnt = q_cnt.where(t.source == P())
        params.append(args.source)
    if args.search:
        search_crit = (
            t.lead_name.like(P()) | t.company_name.like(P()) | t.email.like(P())
        )
        q = q.where(search_crit)
        q_cnt = q_cnt.where(search_crit)
        params.extend([f"%{args.search}%"] * 3)

    limit = int(args.limit or 20)
    offset = int(args.offset or 0)

    q = q.orderby(t.created_at, order=Order.desc).limit(P()).offset(P())

    rows = conn.execute(q.get_sql(), params + [limit, offset]).fetchall()
    total = conn.execute(q_cnt.get_sql(), params).fetchone()["cnt"]

    ok({
        "leads": [row_to_dict(r) for r in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total,
    })


# ---------------------------------------------------------------------------
# 5. convert-lead-to-opportunity
# ---------------------------------------------------------------------------

def convert_lead_to_opportunity(conn, args):
    """Convert a lead to an opportunity (single transaction).

    Required: --lead-id, --opportunity-name
    Optional: --expected-revenue, --probability, --opportunity-type,
              --expected-closing-date
    """
    if not args.lead_id:
        err("--lead-id is required")
    if not args.opportunity_name:
        err("--opportunity-name is required")

    lead = _validate_lead_exists(conn, args.lead_id)

    if lead["status"] == "converted":
        err(f"Lead {lead['naming_series']} is already converted to opportunity {lead['converted_to_opportunity']}")

    opp_type = args.opportunity_type or "sales"
    if opp_type not in VALID_OPP_TYPES:
        err(f"--opportunity-type must be one of {VALID_OPP_TYPES}")

    probability = args.probability or "50"
    expected_revenue = args.expected_revenue or "0"
    weighted = _calc_weighted_revenue(expected_revenue, probability)

    company_id = _resolve_company_id(conn, args)
    opp_id = str(uuid.uuid4())
    opp_naming = get_next_name(conn, "opportunity")

    # Single transaction: create opportunity + update lead
    sql, _ = insert_row("opportunity", {
        "id": P(), "naming_series": P(), "opportunity_name": P(), "lead_id": P(),
        "opportunity_type": P(), "source": P(), "probability": P(),
        "expected_revenue": P(), "weighted_revenue": P(),
        "stage": ValueWrapper("new"), "expected_closing_date": P(), "company_id": P(),
    })
    conn.execute(sql,
        (opp_id, opp_naming, args.opportunity_name, args.lead_id,
         opp_type, lead["source"], probability, expected_revenue, weighted,
         args.expected_closing_date, company_id),
    )

    sql = update_row("lead", {
        "status": ValueWrapper("converted"),
        "converted_to_opportunity": P(),
        "updated_at": LiteralValue("datetime('now')"),
    }, {"id": P()})
    conn.execute(sql, (opp_id, args.lead_id))

    # Mark campaign_lead as converted if applicable
    sql = update_row("campaign_lead", {
        "converted": ValueWrapper(1),
    }, {"lead_id": P()})
    conn.execute(sql, (args.lead_id,))

    audit(conn, "erpclaw-crm", "convert-lead-to-opportunity", "lead", args.lead_id,
           new_values={"opportunity_id": opp_id},
           description=f"Converted lead to opportunity {opp_naming}")
    audit(conn, "erpclaw-crm", "convert-lead-to-opportunity", "opportunity", opp_id,
           new_values={"opportunity_name": args.opportunity_name, "lead_id": args.lead_id},
           description=f"Opportunity created from lead conversion")
    conn.commit()

    ok({
        "opportunity": {
            "id": opp_id,
            "naming_series": opp_naming,
            "opportunity_name": args.opportunity_name,
            "lead_id": args.lead_id,
            "stage": "new",
            "probability": probability,
            "expected_revenue": expected_revenue,
            "weighted_revenue": weighted,
        },
        "lead_status": "converted",
        "message": f"Lead converted to opportunity {opp_naming}",
    })


# ---------------------------------------------------------------------------
# 6. add-opportunity
# ---------------------------------------------------------------------------

def add_opportunity(conn, args):
    """Add a new opportunity.

    Required: --opportunity-name
    Optional: --lead-id, --customer-id, --opportunity-type, --expected-revenue,
              --probability, --expected-closing-date, --assigned-to
    """
    if not args.opportunity_name:
        err("--opportunity-name is required")

    opp_type = args.opportunity_type or "sales"
    if opp_type not in VALID_OPP_TYPES:
        err(f"--opportunity-type must be one of {VALID_OPP_TYPES}")

    if args.lead_id:
        _validate_lead_exists(conn, args.lead_id)
    if args.customer_id:
        _validate_customer_exists(conn, args.customer_id)

    probability = args.probability or "0"
    expected_revenue = args.expected_revenue or "0"
    weighted = _calc_weighted_revenue(expected_revenue, probability)

    company_id = _resolve_company_id(conn, args)
    opp_id = str(uuid.uuid4())
    naming = get_next_name(conn, "opportunity")

    source = None
    if args.lead_id:
        q = Q.from_(_t_lead).select(_t_lead.source).where(_t_lead.id == P())
        lead = conn.execute(q.get_sql(), (args.lead_id,)).fetchone()
        if lead:
            source = lead["source"]

    sql, _ = insert_row("opportunity", {
        "id": P(), "naming_series": P(), "opportunity_name": P(), "lead_id": P(),
        "customer_id": P(), "opportunity_type": P(), "source": P(),
        "probability": P(), "expected_revenue": P(), "weighted_revenue": P(),
        "stage": ValueWrapper("new"), "expected_closing_date": P(),
        "assigned_to": P(), "company_id": P(),
    })
    conn.execute(sql,
        (opp_id, naming, args.opportunity_name, args.lead_id,
         args.customer_id, opp_type, source, probability, expected_revenue,
         weighted, args.expected_closing_date, args.assigned_to, company_id),
    )

    audit(conn, "erpclaw-crm", "add-opportunity", "opportunity", opp_id,
           new_values={"opportunity_name": args.opportunity_name},
           description=f"Created opportunity: {args.opportunity_name}")
    conn.commit()

    ok({
        "opportunity": {
            "id": opp_id,
            "naming_series": naming,
            "opportunity_name": args.opportunity_name,
            "lead_id": args.lead_id,
            "customer_id": args.customer_id,
            "stage": "new",
            "probability": probability,
            "expected_revenue": expected_revenue,
            "weighted_revenue": weighted,
        },
        "message": f"Opportunity '{args.opportunity_name}' created ({naming})",
    })


# ---------------------------------------------------------------------------
# 7. update-opportunity
# ---------------------------------------------------------------------------

def update_opportunity(conn, args):
    """Update an existing opportunity.

    Required: --opportunity-id
    Optional: --opportunity-name, --stage, --probability, --expected-revenue,
              --expected-closing-date, --assigned-to, --next-follow-up-date
    """
    if not args.opportunity_id:
        err("--opportunity-id is required")

    opp = _validate_opportunity_exists(conn, args.opportunity_id)
    old_values = row_to_dict(opp)

    # Terminal states are frozen
    if opp["stage"] in ("won", "lost"):
        err(f"Opportunity is {opp['stage']}. Terminal states cannot be updated.")

    if args.stage and args.stage not in VALID_OPP_STAGES:
        err(f"--stage must be one of {VALID_OPP_STAGES}")

    # Don't allow setting won/lost via update-opportunity; use mark- actions
    if args.stage in ("won", "lost"):
        err(f"Use mark-opportunity-{args.stage} to set terminal state")

    field_map = {
        "opportunity_name": args.opportunity_name,
        "stage": args.stage,
        "probability": args.probability,
        "expected_revenue": args.expected_revenue,
        "expected_closing_date": args.expected_closing_date,
        "assigned_to": args.assigned_to,
        "next_follow_up_date": args.next_follow_up_date,
        "customer_id": getattr(args, "customer_id", None),
    }

    data = {k: P() for k, v in field_map.items() if v is not None}
    values = [v for v in field_map.values() if v is not None]

    if not data:
        err("No fields to update. Provide at least one optional flag.")

    # Recalculate weighted revenue if probability or expected_revenue changed
    new_prob = args.probability or opp["probability"]
    new_rev = args.expected_revenue or opp["expected_revenue"]
    new_weighted = _calc_weighted_revenue(new_rev, new_prob)
    data["weighted_revenue"] = P()
    values.append(new_weighted)

    data["updated_at"] = LiteralValue("datetime('now')")
    sql = update_row("opportunity", data, {"id": P()})
    values.append(args.opportunity_id)
    conn.execute(sql, values)

    audit(conn, "erpclaw-crm", "update-opportunity", "opportunity", args.opportunity_id,
           old_values=old_values,
           description="Updated opportunity")
    conn.commit()

    q = Q.from_(_t_opportunity).select(_t_opportunity.star).where(_t_opportunity.id == P())
    updated = conn.execute(q.get_sql(), (args.opportunity_id,)).fetchone()

    ok({
        "opportunity": row_to_dict(updated),
        "message": f"Opportunity {updated['naming_series']} updated",
    })


# ---------------------------------------------------------------------------
# 8. get-opportunity
# ---------------------------------------------------------------------------

def get_opportunity(conn, args):
    """Get opportunity details with activities, lead, and customer info.

    Required: --opportunity-id
    """
    if not args.opportunity_id:
        err("--opportunity-id is required")

    opp = _validate_opportunity_exists(conn, args.opportunity_id)
    opp_dict = row_to_dict(opp)

    # Fetch activities
    q = (Q.from_(_t_activity).select(_t_activity.star)
         .where(_t_activity.opportunity_id == P())
         .orderby(_t_activity.activity_date, order=Order.desc))
    activities = conn.execute(q.get_sql(), (args.opportunity_id,)).fetchall()
    opp_dict["activities"] = [row_to_dict(a) for a in activities]

    # Fetch lead info if linked
    if opp["lead_id"]:
        t = _t_lead
        q = (Q.from_(t).select(
            t.id, t.naming_series, t.lead_name, t.company_name,
            t.email, t.phone, t.source, t.status)
            .where(t.id == P()))
        lead = conn.execute(q.get_sql(), (opp["lead_id"],)).fetchone()
        opp_dict["lead"] = row_to_dict(lead) if lead else None

    # Fetch customer info if linked
    if opp["customer_id"]:
        t = _t_customer
        q = (Q.from_(t).select(
            t.id, t.name, t.customer_type, t.territory, t.status)
            .where(t.id == P()))
        customer = conn.execute(q.get_sql(), (opp["customer_id"],)).fetchone()
        opp_dict["customer"] = row_to_dict(customer) if customer else None

    ok({"opportunity": opp_dict})


# ---------------------------------------------------------------------------
# 9. list-opportunities
# ---------------------------------------------------------------------------

def list_opportunities(conn, args):
    """List opportunities with optional filters.

    Optional: --stage, --search, --limit, --offset
    """
    t = _t_opportunity
    q = Q.from_(t).select(t.star)
    q_cnt = Q.from_(t).select(fn.Count("*").as_("cnt"))
    params = []

    if args.stage:
        q = q.where(t.stage == P())
        q_cnt = q_cnt.where(t.stage == P())
        params.append(args.stage)
    if args.search:
        search_crit = t.opportunity_name.like(P()) | t.source.like(P())
        q = q.where(search_crit)
        q_cnt = q_cnt.where(search_crit)
        params.extend([f"%{args.search}%"] * 2)

    limit = int(args.limit or 20)
    offset = int(args.offset or 0)

    q = q.orderby(t.created_at, order=Order.desc).limit(P()).offset(P())

    rows = conn.execute(q.get_sql(), params + [limit, offset]).fetchall()
    total = conn.execute(q_cnt.get_sql(), params).fetchone()["cnt"]

    ok({
        "opportunities": [row_to_dict(r) for r in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total,
    })


# ---------------------------------------------------------------------------
# 10. convert-opportunity-to-quotation (cross-skill subprocess)
# ---------------------------------------------------------------------------

def convert_opportunity_to_quotation(conn, args):
    """Convert a won opportunity to a quotation via erpclaw-selling subprocess.

    Required: --opportunity-id, --items (JSON array)
    """
    if not args.opportunity_id:
        err("--opportunity-id is required")
    if not args.items:
        err("--items is required (JSON array of {item_id, qty, rate})")

    opp = _validate_opportunity_exists(conn, args.opportunity_id)

    items_data = _parse_json_arg(args.items, "items")
    if not items_data or not isinstance(items_data, list):
        err("--items must be a non-empty JSON array")

    # Require customer_id for quotation
    if not opp["customer_id"]:
        err("Opportunity must have a customer_id to create a quotation. "
             "Update the opportunity with --customer-id first.")

    # Pre-flight: check erpclaw base package (contains selling domain) is installed
    from erpclaw_lib.dependencies import check_subprocess_target, resolve_skill_script
    dep_err = check_subprocess_target(conn, "erpclaw", "quotation")
    if dep_err:
        err(dep_err["error"])
    selling_script = resolve_skill_script("erpclaw")

    # Build subprocess command
    cmd = [
        "python3", selling_script,
        "--action", "add-quotation",
        "--customer-id", opp["customer_id"],
        "--posting-date", datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "--items", json.dumps(items_data),
    ]

    # Pass db-path if using non-default
    db_path = getattr(args, "db_path", None)
    if db_path:
        cmd.extend(["--db-path", db_path])

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30,
        )
    except subprocess.TimeoutExpired:
        err("Quotation creation timed out (30s)")

    if result.returncode != 0:
        err_msg = result.stdout.strip() or result.stderr.strip()
        err(f"Failed to create quotation: {err_msg}")

    try:
        qtn_result = json.loads(result.stdout)
    except json.JSONDecodeError:
        err(f"Invalid response from selling skill: {result.stdout[:200]}")

    if qtn_result.get("status") != "ok":
        err(f"Quotation creation failed: {qtn_result.get('message', 'unknown error')}")

    # Extract quotation ID from response
    quotation_id = None
    if "quotation" in qtn_result:
        quotation_id = qtn_result["quotation"].get("id")

    # Update opportunity with quotation reference
    if quotation_id:
        sql = update_row("opportunity", {
            "quotation_id": P(),
            "updated_at": LiteralValue("datetime('now')"),
        }, {"id": P()})
        conn.execute(sql, (quotation_id, args.opportunity_id))
        audit(conn, "erpclaw-crm", "convert-opportunity-to-quotation", "opportunity", args.opportunity_id,
               new_values={"quotation_id": quotation_id},
               description=f"Created quotation from opportunity")
        conn.commit()

    ok({
        "quotation": qtn_result.get("quotation", {}),
        "opportunity_id": args.opportunity_id,
        "message": f"Quotation created from opportunity {opp['naming_series']}",
    })


# ---------------------------------------------------------------------------
# 11. mark-opportunity-won
# ---------------------------------------------------------------------------

def mark_opportunity_won(conn, args):
    """Mark an opportunity as won (terminal state).

    Required: --opportunity-id
    Sets probability to 100, weighted_revenue = expected_revenue.
    """
    if not args.opportunity_id:
        err("--opportunity-id is required")

    opp = _validate_opportunity_exists(conn, args.opportunity_id)

    if opp["stage"] in ("won", "lost"):
        err(f"Opportunity is already {opp['stage']}. Terminal states cannot be changed.")

    new_weighted = opp["expected_revenue"]  # 100% probability

    sql = update_row("opportunity", {
        "stage": ValueWrapper("won"),
        "probability": ValueWrapper("100"),
        "weighted_revenue": P(),
        "updated_at": LiteralValue("datetime('now')"),
    }, {"id": P()})
    conn.execute(sql, (new_weighted, args.opportunity_id))

    audit(conn, "erpclaw-crm", "mark-opportunity-won", "opportunity", args.opportunity_id,
           old_values={"stage": opp["stage"], "probability": opp["probability"]},
           new_values={"stage": "won", "probability": "100"},
           description=f"Opportunity marked as won")
    conn.commit()

    ok({
        "opportunity": {
            "id": args.opportunity_id,
            "naming_series": opp["naming_series"],
            "stage": "won",
            "probability": "100",
            "expected_revenue": opp["expected_revenue"],
            "weighted_revenue": new_weighted,
        },
        "message": f"Opportunity {opp['naming_series']} marked as WON",
    })


# ---------------------------------------------------------------------------
# 12. mark-opportunity-lost
# ---------------------------------------------------------------------------

def mark_opportunity_lost(conn, args):
    """Mark an opportunity as lost (terminal state).

    Required: --opportunity-id, --lost-reason
    Sets probability to 0, weighted_revenue = 0.
    """
    if not args.opportunity_id:
        err("--opportunity-id is required")
    if not args.lost_reason:
        err("--lost-reason is required when marking as lost")

    opp = _validate_opportunity_exists(conn, args.opportunity_id)

    if opp["stage"] in ("won", "lost"):
        err(f"Opportunity is already {opp['stage']}. Terminal states cannot be changed.")

    sql = update_row("opportunity", {
        "stage": ValueWrapper("lost"),
        "probability": ValueWrapper("0"),
        "weighted_revenue": ValueWrapper("0"),
        "lost_reason": P(),
        "updated_at": LiteralValue("datetime('now')"),
    }, {"id": P()})
    conn.execute(sql, (args.lost_reason, args.opportunity_id))

    audit(conn, "erpclaw-crm", "mark-opportunity-lost", "opportunity", args.opportunity_id,
           old_values={"stage": opp["stage"]},
           new_values={"stage": "lost", "lost_reason": args.lost_reason},
           description=f"Opportunity marked as lost: {args.lost_reason}")
    conn.commit()

    ok({
        "opportunity": {
            "id": args.opportunity_id,
            "naming_series": opp["naming_series"],
            "stage": "lost",
            "probability": "0",
            "expected_revenue": opp["expected_revenue"],
            "weighted_revenue": "0",
            "lost_reason": args.lost_reason,
        },
        "message": f"Opportunity {opp['naming_series']} marked as LOST",
    })


# ---------------------------------------------------------------------------
# 13. add-campaign
# ---------------------------------------------------------------------------

def add_campaign(conn, args):
    """Add a new campaign.

    Required: --name
    Optional: --campaign-type, --budget, --start-date, --end-date,
              --description, --lead-id (auto-links lead)
    """
    if not args.name:
        err("--name is required")

    if args.campaign_type and args.campaign_type not in VALID_CAMPAIGN_TYPES:
        err(f"--campaign-type must be one of {VALID_CAMPAIGN_TYPES}")

    campaign_id = str(uuid.uuid4())
    budget = args.budget or "0"

    sql, _ = insert_row("campaign", {
        "id": P(), "name": P(), "campaign_type": P(), "start_date": P(),
        "end_date": P(), "budget": P(), "status": ValueWrapper("planned"),
        "description": P(),
    })
    conn.execute(sql,
        (campaign_id, args.name, args.campaign_type, args.start_date,
         args.end_date, budget, args.description),
    )

    # Auto-link lead if provided
    lead_linked = False
    if args.lead_id:
        _validate_lead_exists(conn, args.lead_id)
        cl_id = str(uuid.uuid4())
        sql, _ = insert_row("campaign_lead", {
            "id": P(), "campaign_id": P(), "lead_id": P(),
        })
        conn.execute(sql, (cl_id, campaign_id, args.lead_id))
        lead_linked = True

    audit(conn, "erpclaw-crm", "add-campaign", "campaign", campaign_id,
           new_values={"name": args.name, "campaign_type": args.campaign_type},
           description=f"Created campaign: {args.name}")
    conn.commit()

    resp = {
        "campaign": {
            "id": campaign_id,
            "name": args.name,
            "campaign_type": args.campaign_type,
            "budget": budget,
            "status": "planned",
            "start_date": args.start_date,
            "end_date": args.end_date,
        },
        "message": f"Campaign '{args.name}' created",
    }
    if lead_linked:
        resp["lead_linked"] = args.lead_id

    ok(resp)


# ---------------------------------------------------------------------------
# 14. list-campaigns
# ---------------------------------------------------------------------------

def list_campaigns(conn, args):
    """List campaigns with lead counts.

    Optional: --status, --limit, --offset
    """
    conditions = ["1=1"]
    params = []

    if args.status:
        conditions.append("c.status = ?")
        params.append(args.status)

    where = " AND ".join(conditions)
    limit = int(args.limit or 20)
    offset = int(args.offset or 0)

    rows = conn.execute(
        f"""SELECT c.*,
               COUNT(cl.id) AS total_leads,
               SUM(CASE WHEN cl.converted = 1 THEN 1 ELSE 0 END) AS converted_leads
           FROM campaign c
           LEFT JOIN campaign_lead cl ON cl.campaign_id = c.id
           WHERE {where}
           GROUP BY c.id
           ORDER BY c.created_at DESC
           LIMIT ? OFFSET ?""",
        params + [limit, offset],
    ).fetchall()

    total = conn.execute(
        f"SELECT COUNT(*) AS cnt FROM campaign c WHERE {where}", params,
    ).fetchone()["cnt"]

    ok({
        "campaigns": [row_to_dict(r) for r in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total,
    })


# ---------------------------------------------------------------------------
# 15. add-activity
# ---------------------------------------------------------------------------

def add_activity(conn, args):
    """Add a CRM activity.

    Required: --activity-type, --subject, --activity-date
    Optional: --lead-id, --opportunity-id, --customer-id, --description,
              --created-by, --next-action-date
    """
    if not args.activity_type:
        err("--activity-type is required")
    if not args.subject:
        err("--subject is required")
    if not args.activity_date:
        err("--activity-date is required")

    if args.activity_type not in VALID_ACTIVITY_TYPES:
        err(f"--activity-type must be one of {VALID_ACTIVITY_TYPES}")

    # At least one reference should be provided
    if not any([args.lead_id, args.opportunity_id, args.customer_id]):
        err("At least one of --lead-id, --opportunity-id, or --customer-id is required")

    if args.lead_id:
        _validate_lead_exists(conn, args.lead_id)
    if args.opportunity_id:
        _validate_opportunity_exists(conn, args.opportunity_id)
    if args.customer_id:
        _validate_customer_exists(conn, args.customer_id)

    activity_id = str(uuid.uuid4())

    sql, _ = insert_row("crm_activity", {
        "id": P(), "activity_type": P(), "subject": P(), "description": P(),
        "activity_date": P(), "lead_id": P(), "opportunity_id": P(),
        "customer_id": P(), "created_by": P(), "next_action_date": P(),
    })
    conn.execute(sql,
        (activity_id, args.activity_type, args.subject, args.description,
         args.activity_date, args.lead_id, args.opportunity_id,
         args.customer_id, args.created_by, args.next_action_date),
    )

    audit(conn, "erpclaw-crm", "add-activity", "crm_activity", activity_id,
           new_values={"activity_type": args.activity_type, "subject": args.subject},
           description=f"Logged {args.activity_type}: {args.subject}")
    conn.commit()

    ok({
        "activity": {
            "id": activity_id,
            "activity_type": args.activity_type,
            "subject": args.subject,
            "activity_date": args.activity_date,
            "lead_id": args.lead_id,
            "opportunity_id": args.opportunity_id,
            "customer_id": args.customer_id,
        },
        "message": f"Activity '{args.subject}' logged",
    })


# ---------------------------------------------------------------------------
# 16. list-activities
# ---------------------------------------------------------------------------

def list_activities(conn, args):
    """List CRM activities with optional filters.

    Optional: --lead-id, --opportunity-id, --activity-type, --limit, --offset
    """
    t = _t_activity
    q = Q.from_(t).select(t.star)
    q_cnt = Q.from_(t).select(fn.Count("*").as_("cnt"))
    params = []

    if args.lead_id:
        q = q.where(t.lead_id == P())
        q_cnt = q_cnt.where(t.lead_id == P())
        params.append(args.lead_id)
    if args.opportunity_id:
        q = q.where(t.opportunity_id == P())
        q_cnt = q_cnt.where(t.opportunity_id == P())
        params.append(args.opportunity_id)
    if args.activity_type:
        q = q.where(t.activity_type == P())
        q_cnt = q_cnt.where(t.activity_type == P())
        params.append(args.activity_type)

    limit = int(args.limit or 20)
    offset = int(args.offset or 0)

    q = q.orderby(t.activity_date, order=Order.desc).limit(P()).offset(P())

    rows = conn.execute(q.get_sql(), params + [limit, offset]).fetchall()
    total = conn.execute(q_cnt.get_sql(), params).fetchone()["cnt"]

    ok({
        "activities": [row_to_dict(r) for r in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total,
    })


# ---------------------------------------------------------------------------
# 17. pipeline-report
# ---------------------------------------------------------------------------

def pipeline_report(conn, args):
    """Pipeline report with stage-wise aggregation.

    Optional: --stage, --from-date, --to-date
    """
    conditions = ["1=1"]
    params = []

    if args.stage:
        conditions.append("stage = ?")
        params.append(args.stage)
    if args.from_date:
        conditions.append("created_at >= ?")
        params.append(args.from_date)
    if args.to_date:
        conditions.append("created_at <= ?")
        params.append(args.to_date + " 23:59:59")

    where = " AND ".join(conditions)

    # Stage-wise aggregation
    stage_rows = conn.execute(
        f"""SELECT stage,
               COUNT(*) AS count,
               COALESCE(decimal_sum(expected_revenue), '0') AS total_expected_revenue,
               COALESCE(decimal_sum(weighted_revenue), '0') AS total_weighted_revenue
           FROM opportunity
           WHERE {where}
           GROUP BY stage
           ORDER BY CASE stage
               WHEN 'new' THEN 1
               WHEN 'contacted' THEN 2
               WHEN 'qualified' THEN 3
               WHEN 'proposal_sent' THEN 4
               WHEN 'negotiation' THEN 5
               WHEN 'won' THEN 6
               WHEN 'lost' THEN 7
           END""",
        params,
    ).fetchall()

    stages = []
    for row in stage_rows:
        stages.append({
            "stage": row["stage"],
            "count": row["count"],
            "total_expected_revenue": str(Decimal(str(row["total_expected_revenue"])).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "total_weighted_revenue": str(Decimal(str(row["total_weighted_revenue"])).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP)),
        })

    # Conversion rate: won / (won + lost)
    total_won = 0
    total_lost = 0
    total_all = 0
    for s in stages:
        total_all += s["count"]
        if s["stage"] == "won":
            total_won = s["count"]
        elif s["stage"] == "lost":
            total_lost = s["count"]

    total_closed = total_won + total_lost
    conversion_rate = "0.00"
    if total_closed > 0:
        rate = (Decimal(str(total_won)) / Decimal(str(total_closed))) * Decimal("100")
        conversion_rate = str(rate.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    ok({
        "pipeline": {
            "stages": stages,
            "total_opportunities": total_all,
            "total_won": total_won,
            "total_lost": total_lost,
            "conversion_rate_pct": conversion_rate,
        },
    })


# ---------------------------------------------------------------------------
# 18. status
# ---------------------------------------------------------------------------

def status_action(conn, args):
    """CRM status summary."""
    q = Q.from_(_t_lead).select(fn.Count("*").as_("cnt"))
    lead_count = conn.execute(q.get_sql()).fetchone()["cnt"]

    q = (Q.from_(_t_lead).select(fn.Count("*").as_("cnt"))
         .where(_t_lead.status.notin([ValueWrapper("converted"), ValueWrapper("lost")])))
    active_leads = conn.execute(q.get_sql()).fetchone()["cnt"]

    q = Q.from_(_t_opportunity).select(fn.Count("*").as_("cnt"))
    opp_count = conn.execute(q.get_sql()).fetchone()["cnt"]

    q = (Q.from_(_t_opportunity).select(fn.Count("*").as_("cnt"))
         .where(_t_opportunity.stage.notin([ValueWrapper("won"), ValueWrapper("lost")])))
    open_opps = conn.execute(q.get_sql()).fetchone()["cnt"]

    q = Q.from_(_t_campaign).select(fn.Count("*").as_("cnt"))
    campaign_count = conn.execute(q.get_sql()).fetchone()["cnt"]

    q = Q.from_(_t_activity).select(fn.Count("*").as_("cnt"))
    activity_count = conn.execute(q.get_sql()).fetchone()["cnt"]

    ok({
        "crm_status": {
            "leads": {"total": lead_count, "active": active_leads},
            "opportunities": {"total": opp_count, "open": open_opps},
            "campaigns": {"total": campaign_count},
            "activities": {"total": activity_count},
        },
        "message": f"CRM: {active_leads} active leads, {open_opps} open opportunities",
    })


# ---------------------------------------------------------------------------
# ACTIONS registry
# ---------------------------------------------------------------------------

ACTIONS = {
    "add-lead": add_lead,
    "update-lead": update_lead,
    "get-lead": get_lead,
    "list-leads": list_leads,
    "convert-lead-to-opportunity": convert_lead_to_opportunity,
    "add-opportunity": add_opportunity,
    "update-opportunity": update_opportunity,
    "get-opportunity": get_opportunity,
    "list-opportunities": list_opportunities,
    "convert-opportunity-to-quotation": convert_opportunity_to_quotation,
    "mark-opportunity-won": mark_opportunity_won,
    "mark-opportunity-lost": mark_opportunity_lost,
    "add-campaign": add_campaign,
    "list-campaigns": list_campaigns,
    "add-activity": add_activity,
    "list-activities": list_activities,
    "pipeline-report": pipeline_report,
    "status": status_action,
}


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ERPClaw CRM Skill")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)
    parser.add_argument("--company-id")

    # Entity IDs
    parser.add_argument("--lead-id")
    parser.add_argument("--opportunity-id")
    parser.add_argument("--campaign-id")
    parser.add_argument("--activity-id")
    parser.add_argument("--customer-id")

    # Lead fields
    parser.add_argument("--lead-name")
    parser.add_argument("--company-name")
    parser.add_argument("--email")
    parser.add_argument("--phone")
    parser.add_argument("--source")
    parser.add_argument("--territory")
    parser.add_argument("--industry")
    parser.add_argument("--assigned-to")
    parser.add_argument("--notes")

    # Opportunity fields
    parser.add_argument("--opportunity-name")
    parser.add_argument("--opportunity-type")
    parser.add_argument("--expected-closing-date")
    parser.add_argument("--probability")
    parser.add_argument("--expected-revenue")
    parser.add_argument("--stage")
    parser.add_argument("--lost-reason")
    parser.add_argument("--next-follow-up-date")

    # Campaign fields
    parser.add_argument("--name")
    parser.add_argument("--campaign-type")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--budget")
    parser.add_argument("--actual-spend")
    parser.add_argument("--description")

    # Activity fields
    parser.add_argument("--activity-type")
    parser.add_argument("--subject")
    parser.add_argument("--activity-date")
    parser.add_argument("--created-by")
    parser.add_argument("--next-action-date")

    # Cross-skill
    parser.add_argument("--items")  # JSON array for quotation conversion

    # Filters
    parser.add_argument("--status")
    parser.add_argument("--from-date")
    parser.add_argument("--to-date")
    parser.add_argument("--limit", default="20")
    parser.add_argument("--offset", default="0")
    parser.add_argument("--search")

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
    except Exception as e:
        conn.rollback()
        sys.stderr.write(f"[erpclaw-crm] {e}\n")
        err("An unexpected error occurred")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
