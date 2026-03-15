#!/usr/bin/env python3
"""ERPClaw Quality Skill -- db_query.py

Quality inspection templates, quality inspections, non-conformance tracking,
and quality goals.  All 14 actions are routed through this single entry point.

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout, exit 0 on success, exit 1 on error.
"""
import argparse
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

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
    from erpclaw_lib.query import Q, P, Table, Field, fn, Order, Criterion, insert_row
    from erpclaw_lib.vendor.pypika.terms import ValueWrapper
except ImportError:
    import json as _json
    print(_json.dumps({"status": "error", "error": "ERPClaw foundation not installed. Install erpclaw first: clawhub install erpclaw", "suggestion": "clawhub install erpclaw"}))
    sys.exit(1)

REQUIRED_TABLES = ["company"]

VALID_INSPECTION_TYPES = ("incoming", "outgoing", "in_process")
VALID_PARAMETER_TYPES = ("numeric", "non_numeric", "formula")
VALID_INSPECTION_STATUSES = ("accepted", "rejected", "partially_accepted")
VALID_READING_STATUSES = ("accepted", "rejected")
VALID_REFERENCE_TYPES = ("purchase_receipt", "delivery_note", "stock_entry")
VALID_NC_SEVERITIES = ("minor", "major", "critical")
VALID_NC_STATUSES = ("open", "investigating", "resolved", "closed")
VALID_GOAL_FREQUENCIES = ("daily", "weekly", "monthly")
VALID_GOAL_STATUSES = ("on_track", "at_risk", "behind")

# ---------------------------------------------------------------------------
# PyPika table references
# ---------------------------------------------------------------------------
T_item = Table("item")
T_batch = Table("batch")
T_qit = Table("quality_inspection_template")
T_qip = Table("quality_inspection_parameter")
T_qi = Table("quality_inspection")
T_qir = Table("quality_inspection_reading")
T_nc = Table("non_conformance")
T_qg = Table("quality_goal")


def _parse_json_arg(value, name):
    if value is None:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        err(f"Invalid JSON for --{name}: {value}")


def _validate_item_exists(conn, item_id: str, label: str = "Item"):
    """Validate that an item exists and return the row, or error."""
    q = Q.from_(T_item).select(T_item.star).where(T_item.id == P())
    item = conn.execute(q.get_sql(), (item_id,)).fetchone()
    if not item:
        err(f"{label} {item_id} not found",
             suggestion="Use 'list items' to see available items.")
    return item


def _validate_template_exists(conn, template_id: str):
    """Validate that an inspection template exists and return the row, or error."""
    q = Q.from_(T_qit).select(T_qit.star).where(T_qit.id == P())
    tmpl = conn.execute(q.get_sql(), (template_id,)).fetchone()
    if not tmpl:
        err(f"Inspection template {template_id} not found")
    return tmpl


def _validate_inspection_exists(conn, inspection_id: str):
    """Validate that a quality inspection exists and return the row, or error."""
    q = Q.from_(T_qi).select(T_qi.star).where(T_qi.id == P())
    qi = conn.execute(q.get_sql(), (inspection_id,)).fetchone()
    if not qi:
        err(f"Quality inspection {inspection_id} not found")
    return qi


def _validate_nc_exists(conn, nc_id: str):
    """Validate that a non-conformance record exists and return the row, or error."""
    q = Q.from_(T_nc).select(T_nc.star).where(T_nc.id == P())
    nc = conn.execute(q.get_sql(), (nc_id,)).fetchone()
    if not nc:
        err(f"Non-conformance {nc_id} not found")
    return nc


def _validate_goal_exists(conn, goal_id: str):
    """Validate that a quality goal exists and return the row, or error."""
    q = Q.from_(T_qg).select(T_qg.star).where(T_qg.id == P())
    goal = conn.execute(q.get_sql(), (goal_id,)).fetchone()
    if not goal:
        err(f"Quality goal {goal_id} not found")
    return goal


# ---------------------------------------------------------------------------
# 1. add-inspection-template
# ---------------------------------------------------------------------------

def add_inspection_template(conn, args):
    """Create an inspection template with optional parameters.

    Required: --name, --inspection-type
    Optional: --item-id, --description, --parameters (JSON array)
    """
    if not args.name:
        err("--name is required")
    if not args.inspection_type:
        err("--inspection-type is required")
    if args.inspection_type not in VALID_INSPECTION_TYPES:
        err(f"--inspection-type must be one of {VALID_INSPECTION_TYPES}")

    # Validate optional item reference
    if args.item_id:
        _validate_item_exists(conn, args.item_id)

    # Parse parameters JSON
    parameters = _parse_json_arg(args.parameters, "parameters") if args.parameters else None

    template_id = str(uuid.uuid4())

    sql, _ = insert_row("quality_inspection_template", {
        "id": P(), "name": P(), "item_id": P(),
        "inspection_type": P(), "description": P(),
    })
    conn.execute(sql, (template_id, args.name, args.item_id,
                        args.inspection_type, args.description))

    # Insert parameter rows
    param_rows = []
    if parameters:
        if not isinstance(parameters, list):
            err("--parameters must be a JSON array")

        for i, p in enumerate(parameters):
            p_name = p.get("parameter_name")
            if not p_name:
                err(f"Parameter {i}: parameter_name is required")

            p_type = p.get("parameter_type")
            if not p_type:
                err(f"Parameter {i}: parameter_type is required")
            if p_type not in VALID_PARAMETER_TYPES:
                err(f"Parameter {i}: parameter_type must be one of {VALID_PARAMETER_TYPES}")

            p_id = str(uuid.uuid4())
            sort_order = p.get("sort_order", i)

            p_sql, _ = insert_row("quality_inspection_parameter", {
                "id": P(), "template_id": P(), "parameter_name": P(),
                "parameter_type": P(), "min_value": P(), "max_value": P(),
                "acceptance_value": P(), "formula": P(), "uom": P(),
                "sort_order": P(),
            })
            conn.execute(p_sql, (p_id, template_id, p_name, p_type,
                                  p.get("min_value"), p.get("max_value"),
                                  p.get("acceptance_value"), p.get("formula"),
                                  p.get("uom"), sort_order))
            param_rows.append({
                "id": p_id,
                "parameter_name": p_name,
                "parameter_type": p_type,
                "min_value": p.get("min_value"),
                "max_value": p.get("max_value"),
                "acceptance_value": p.get("acceptance_value"),
                "formula": p.get("formula"),
                "uom": p.get("uom"),
                "sort_order": sort_order,
            })

    audit(conn, "erpclaw-quality", "add-inspection-template", "quality_inspection_template",
           template_id, description=f"Created template '{args.name}'")
    conn.commit()

    ok({
        "template": {
            "id": template_id,
            "name": args.name,
            "item_id": args.item_id,
            "inspection_type": args.inspection_type,
            "description": args.description,
            "parameters": param_rows,
        },
        "message": f"Inspection template '{args.name}' created with {len(param_rows)} parameter(s)",
    })


# ---------------------------------------------------------------------------
# 2. get-inspection-template
# ---------------------------------------------------------------------------

def get_inspection_template(conn, args):
    """Return an inspection template with all its parameters.

    Required: --template-id
    """
    if not args.template_id:
        err("--template-id is required")

    tmpl = _validate_template_exists(conn, args.template_id)
    tmpl_dict = row_to_dict(tmpl)

    # Fetch parameters
    q = (Q.from_(T_qip).select(T_qip.star)
         .where(T_qip.template_id == P())
         .orderby(T_qip.sort_order))
    params = conn.execute(q.get_sql(), (args.template_id,)).fetchall()
    tmpl_dict["parameters"] = [row_to_dict(p) for p in params]

    ok({"template": tmpl_dict})


# ---------------------------------------------------------------------------
# 3. list-inspection-templates
# ---------------------------------------------------------------------------

def list_inspection_templates(conn, args):
    """List inspection templates with optional filters.

    Optional: --inspection-type, --item-id, --search, --limit, --offset
    """
    q = Q.from_(T_qit).select(T_qit.star)
    params = []

    if args.inspection_type:
        if args.inspection_type not in VALID_INSPECTION_TYPES:
            err(f"--inspection-type must be one of {VALID_INSPECTION_TYPES}")
        q = q.where(T_qit.inspection_type == P())
        params.append(args.inspection_type)

    if args.item_id:
        q = q.where(T_qit.item_id == P())
        params.append(args.item_id)

    if args.search:
        q = q.where(T_qit.name.like(P()))
        params.append(f"%{args.search}%")

    # Count
    cq = Q.from_(T_qit).select(fn.Count("*").as_("cnt"))
    # Replay same WHERE filters
    cq_params = list(params)
    if args.inspection_type:
        cq = cq.where(T_qit.inspection_type == P())
    if args.item_id:
        cq = cq.where(T_qit.item_id == P())
    if args.search:
        cq = cq.where(T_qit.name.like(P()))
    total = conn.execute(cq.get_sql(), cq_params).fetchone()["cnt"]

    # Paginate
    limit = int(args.limit or 20)
    offset = int(args.offset or 0)
    q = q.orderby(T_qit.created_at, order=Order.desc).limit(P()).offset(P())
    params.extend([limit, offset])

    rows = conn.execute(q.get_sql(), params).fetchall()
    templates = [row_to_dict(r) for r in rows]

    ok({
        "templates": templates,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total,
    })


# ---------------------------------------------------------------------------
# 4. add-quality-inspection
# ---------------------------------------------------------------------------

def add_quality_inspection(conn, args):
    """Create a quality inspection record.

    Required: --item-id, --inspection-type, --inspection-date
    Optional: --batch-id, --reference-type, --reference-id, --template-id,
              --inspected-by, --sample-size, --remarks
    """
    if not args.item_id:
        err("--item-id is required")
    if not args.inspection_type:
        err("--inspection-type is required")
    if not args.inspection_date:
        err("--inspection-date is required")
    if args.inspection_type not in VALID_INSPECTION_TYPES:
        err(f"--inspection-type must be one of {VALID_INSPECTION_TYPES}")

    # Validate item exists
    _validate_item_exists(conn, args.item_id)

    # Validate batch if provided
    if args.batch_id:
        bq = Q.from_(T_batch).select(T_batch.id).where(T_batch.id == P())
        batch = conn.execute(bq.get_sql(), (args.batch_id,)).fetchone()
        if not batch:
            err(f"Batch {args.batch_id} not found")

    # Validate reference type
    if args.reference_type:
        if args.reference_type not in VALID_REFERENCE_TYPES:
            err(f"--reference-type must be one of {VALID_REFERENCE_TYPES}")

    # Validate template if provided
    template_params = []
    if args.template_id:
        _validate_template_exists(conn, args.template_id)
        tpq = (Q.from_(T_qip).select(T_qip.star)
               .where(T_qip.template_id == P())
               .orderby(T_qip.sort_order))
        template_params = conn.execute(tpq.get_sql(), (args.template_id,)).fetchall()

    inspection_id = str(uuid.uuid4())
    naming = get_next_name(conn, "quality_inspection", company_id=args.company_id)
    sample_size = int(args.sample_size) if args.sample_size else 1

    qi_sql, _ = insert_row("quality_inspection", {
        "id": P(), "naming_series": P(), "inspection_type": P(),
        "item_id": P(), "batch_id": P(), "reference_type": P(),
        "reference_id": P(), "template_id": P(), "inspection_date": P(),
        "inspected_by": P(), "sample_size": P(), "status": P(), "remarks": P(),
    })
    conn.execute(qi_sql, (inspection_id, naming, args.inspection_type,
                           args.item_id, args.batch_id, args.reference_type,
                           args.reference_id, args.template_id,
                           args.inspection_date, args.inspected_by,
                           sample_size, "accepted", args.remarks))

    # Auto-create reading rows from template parameters
    reading_rows = []
    rd_sql, _ = insert_row("quality_inspection_reading", {
        "id": P(), "quality_inspection_id": P(), "parameter_id": P(),
        "reading_value": P(), "status": P(),
    })
    for param in template_params:
        reading_id = str(uuid.uuid4())
        conn.execute(rd_sql, (reading_id, inspection_id, param["id"],
                               None, "accepted"))
        reading_rows.append({
            "id": reading_id,
            "parameter_id": param["id"],
            "parameter_name": param["parameter_name"],
            "reading_value": None,
            "status": "accepted",
        })

    audit(conn, "erpclaw-quality", "add-quality-inspection", "quality_inspection",
           inspection_id, description=f"Created inspection {naming}")
    conn.commit()

    ok({
        "inspection": {
            "id": inspection_id,
            "naming_series": naming,
            "inspection_type": args.inspection_type,
            "item_id": args.item_id,
            "batch_id": args.batch_id,
            "reference_type": args.reference_type,
            "reference_id": args.reference_id,
            "template_id": args.template_id,
            "inspection_date": args.inspection_date,
            "inspected_by": args.inspected_by,
            "sample_size": sample_size,
            "status": "accepted",
            "remarks": args.remarks,
            "readings": reading_rows,
        },
        "message": f"Quality inspection {naming} created"
                   + (f" with {len(reading_rows)} reading(s)" if reading_rows else ""),
    })


# ---------------------------------------------------------------------------
# 5. record-inspection-readings
# ---------------------------------------------------------------------------

def record_inspection_readings(conn, args):
    """Record reading values for a quality inspection.

    Required: --quality-inspection-id, --readings (JSON array)

    Each reading: {parameter_id, reading_value, remarks?}
    For numeric parameters: checks reading_value between min_value and max_value.
    For non_numeric parameters: checks reading_value == acceptance_value.
    """
    if not args.quality_inspection_id:
        err("--quality-inspection-id is required")
    if not args.readings:
        err("--readings is required (JSON array)")

    _validate_inspection_exists(conn, args.quality_inspection_id)

    readings = _parse_json_arg(args.readings, "readings")
    if not readings or not isinstance(readings, list):
        err("--readings must be a non-empty JSON array")

    updated_readings = []

    for i, r in enumerate(readings):
        param_id = r.get("parameter_id")
        if not param_id:
            err(f"Reading {i}: parameter_id is required")

        reading_value = r.get("reading_value")
        remarks = r.get("remarks")

        # Validate reading row exists for this inspection
        eq = (Q.from_(T_qir)
              .select(T_qir.id, T_qir.quality_inspection_id)
              .where(T_qir.quality_inspection_id == P())
              .where(T_qir.parameter_id == P()))
        existing = conn.execute(eq.get_sql(),
                                (args.quality_inspection_id, param_id)).fetchone()

        # Get parameter definition for validation
        pq = Q.from_(T_qip).select(T_qip.star).where(T_qip.id == P())
        param = conn.execute(pq.get_sql(), (param_id,)).fetchone()
        if not param:
            err(f"Reading {i}: parameter {param_id} not found")

        # Determine reading status based on parameter type
        reading_status = "accepted"

        if reading_value is not None and reading_value != "":
            if param["parameter_type"] == "numeric":
                try:
                    val = to_decimal(str(reading_value))
                except (InvalidOperation, TypeError, ValueError):
                    err(f"Reading {i}: reading_value '{reading_value}' is not a valid number")

                # Check min_value
                if param["min_value"] is not None and param["min_value"] != "":
                    min_val = to_decimal(param["min_value"])
                    if val < min_val:
                        reading_status = "rejected"

                # Check max_value
                if param["max_value"] is not None and param["max_value"] != "":
                    max_val = to_decimal(param["max_value"])
                    if val > max_val:
                        reading_status = "rejected"

            elif param["parameter_type"] == "non_numeric":
                if param["acceptance_value"] is not None and param["acceptance_value"] != "":
                    if str(reading_value).strip() != str(param["acceptance_value"]).strip():
                        reading_status = "rejected"

        if existing:
            # Update existing reading row
            uq = (Q.update(T_qir)
                  .set(T_qir.reading_value, P())
                  .set(T_qir.status, P())
                  .set(T_qir.remarks, P())
                  .where(T_qir.quality_inspection_id == P())
                  .where(T_qir.parameter_id == P()))
            conn.execute(uq.get_sql(),
                         (str(reading_value) if reading_value is not None else None,
                          reading_status, remarks,
                          args.quality_inspection_id, param_id))
            updated_readings.append({
                "id": existing["id"],
                "parameter_id": param_id,
                "reading_value": reading_value,
                "status": reading_status,
                "remarks": remarks,
            })
        else:
            # Insert new reading row
            reading_id = str(uuid.uuid4())
            nr_sql, _ = insert_row("quality_inspection_reading", {
                "id": P(), "quality_inspection_id": P(), "parameter_id": P(),
                "reading_value": P(), "status": P(), "remarks": P(),
            })
            conn.execute(nr_sql,
                         (reading_id, args.quality_inspection_id, param_id,
                          str(reading_value) if reading_value is not None else None,
                          reading_status, remarks))
            updated_readings.append({
                "id": reading_id,
                "parameter_id": param_id,
                "reading_value": reading_value,
                "status": reading_status,
                "remarks": remarks,
            })

    audit(conn, "erpclaw-quality", "record-inspection-readings", "quality_inspection",
           args.quality_inspection_id,
           description=f"Recorded {len(updated_readings)} reading(s)")
    conn.commit()

    ok({
        "readings": updated_readings,
        "message": f"Recorded {len(updated_readings)} reading(s) for inspection {args.quality_inspection_id}",
    })


# ---------------------------------------------------------------------------
# 6. evaluate-inspection
# ---------------------------------------------------------------------------

def evaluate_inspection(conn, args):
    """Evaluate a quality inspection based on its readings.

    Required: --quality-inspection-id

    Logic:
    - All readings accepted -> inspection status = 'accepted'
    - All readings rejected -> inspection status = 'rejected'
    - Mixed -> inspection status = 'partially_accepted'
    """
    if not args.quality_inspection_id:
        err("--quality-inspection-id is required")

    qi = _validate_inspection_exists(conn, args.quality_inspection_id)

    # Get all readings
    rq = (Q.from_(T_qir).select(T_qir.id, T_qir.status)
          .where(T_qir.quality_inspection_id == P()))
    readings = conn.execute(rq.get_sql(), (args.quality_inspection_id,)).fetchall()

    if not readings:
        err(f"No readings found for inspection {args.quality_inspection_id}")

    accepted_count = sum(1 for r in readings if r["status"] == "accepted")
    rejected_count = sum(1 for r in readings if r["status"] == "rejected")
    total_count = len(readings)

    old_status = qi["status"]

    if accepted_count == total_count:
        new_status = "accepted"
    elif rejected_count == total_count:
        new_status = "rejected"
    else:
        new_status = "partially_accepted"

    uq = (Q.update(T_qi).set(T_qi.status, P()).where(T_qi.id == P()))
    conn.execute(uq.get_sql(), (new_status, args.quality_inspection_id))

    audit(conn, "erpclaw-quality", "evaluate-inspection", "quality_inspection",
           args.quality_inspection_id,
           old_values={"status": old_status},
           new_values={"status": new_status},
           description=f"Evaluated: {accepted_count}/{total_count} accepted")
    conn.commit()

    ok({
        "inspection_id": args.quality_inspection_id,
        "old_status": old_status,
        "new_status": new_status,
        "total_readings": total_count,
        "accepted_count": accepted_count,
        "rejected_count": rejected_count,
        "message": f"Inspection evaluated: {new_status} ({accepted_count}/{total_count} accepted)",
    })


# ---------------------------------------------------------------------------
# 7. list-quality-inspections
# ---------------------------------------------------------------------------

def list_quality_inspections(conn, args):
    """List quality inspections with optional filters.

    Optional: --item-id, --inspection-type, --reference-type, --reference-id,
              --status, --from-date, --to-date, --limit, --offset
    """
    q = Q.from_(T_qi).select(T_qi.star)
    cq = Q.from_(T_qi).select(fn.Count("*").as_("cnt"))
    params = []

    if args.item_id:
        q = q.where(T_qi.item_id == P())
        cq = cq.where(T_qi.item_id == P())
        params.append(args.item_id)

    if args.inspection_type:
        if args.inspection_type not in VALID_INSPECTION_TYPES:
            err(f"--inspection-type must be one of {VALID_INSPECTION_TYPES}")
        q = q.where(T_qi.inspection_type == P())
        cq = cq.where(T_qi.inspection_type == P())
        params.append(args.inspection_type)

    if args.reference_type:
        if args.reference_type not in VALID_REFERENCE_TYPES:
            err(f"--reference-type must be one of {VALID_REFERENCE_TYPES}")
        q = q.where(T_qi.reference_type == P())
        cq = cq.where(T_qi.reference_type == P())
        params.append(args.reference_type)

    if args.reference_id:
        q = q.where(T_qi.reference_id == P())
        cq = cq.where(T_qi.reference_id == P())
        params.append(args.reference_id)

    if args.status:
        if args.status not in VALID_INSPECTION_STATUSES:
            err(f"--status must be one of {VALID_INSPECTION_STATUSES}")
        q = q.where(T_qi.status == P())
        cq = cq.where(T_qi.status == P())
        params.append(args.status)

    if args.from_date:
        q = q.where(T_qi.inspection_date >= P())
        cq = cq.where(T_qi.inspection_date >= P())
        params.append(args.from_date)

    if args.to_date:
        q = q.where(T_qi.inspection_date <= P())
        cq = cq.where(T_qi.inspection_date <= P())
        params.append(args.to_date)

    # Count
    total = conn.execute(cq.get_sql(), params).fetchone()["cnt"]

    # Paginate
    limit = int(args.limit or 20)
    offset = int(args.offset or 0)
    q = q.orderby(T_qi.created_at, order=Order.desc).limit(P()).offset(P())
    page_params = list(params) + [limit, offset]

    rows = conn.execute(q.get_sql(), page_params).fetchall()
    inspections = [row_to_dict(r) for r in rows]

    ok({
        "inspections": inspections,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total,
    })


# ---------------------------------------------------------------------------
# 8. add-non-conformance
# ---------------------------------------------------------------------------

def add_non_conformance(conn, args):
    """Create a non-conformance report (NCR).

    Required: --description
    Optional: --quality-inspection-id, --item-id, --batch-id, --severity,
              --root-cause, --corrective-action, --preventive-action,
              --responsible-employee-id
    """
    if not args.description:
        err("--description is required")

    # Validate optional references
    if args.quality_inspection_id:
        _validate_inspection_exists(conn, args.quality_inspection_id)

    if args.item_id:
        _validate_item_exists(conn, args.item_id)

    severity = args.severity or "minor"
    if severity not in VALID_NC_SEVERITIES:
        err(f"--severity must be one of {VALID_NC_SEVERITIES}")

    nc_id = str(uuid.uuid4())
    naming = get_next_name(conn, "non_conformance", company_id=args.company_id)

    nc_sql, _ = insert_row("non_conformance", {
        "id": P(), "naming_series": P(), "quality_inspection_id": P(),
        "item_id": P(), "batch_id": P(), "description": P(),
        "severity": P(), "root_cause": P(), "corrective_action": P(),
        "preventive_action": P(), "responsible_employee_id": P(), "status": P(),
    })
    conn.execute(nc_sql, (nc_id, naming, args.quality_inspection_id,
                           args.item_id, args.batch_id, args.description,
                           severity, args.root_cause, args.corrective_action,
                           args.preventive_action,
                           args.responsible_employee_id, "open"))

    audit(conn, "erpclaw-quality", "add-non-conformance", "non_conformance",
           nc_id, description=f"Created NCR {naming}")
    conn.commit()

    ok({
        "non_conformance": {
            "id": nc_id,
            "naming_series": naming,
            "quality_inspection_id": args.quality_inspection_id,
            "item_id": args.item_id,
            "batch_id": args.batch_id,
            "description": args.description,
            "severity": severity,
            "root_cause": args.root_cause,
            "corrective_action": args.corrective_action,
            "preventive_action": args.preventive_action,
            "responsible_employee_id": args.responsible_employee_id,
            "status": "open",
        },
        "message": f"Non-conformance report {naming} created",
    })


# ---------------------------------------------------------------------------
# 9. update-non-conformance
# ---------------------------------------------------------------------------

def update_non_conformance(conn, args):
    """Update a non-conformance report.

    Required: --non-conformance-id
    Optional: --severity, --root-cause, --corrective-action, --preventive-action,
              --responsible-employee-id, --status, --resolution-date, --description
    """
    if not args.non_conformance_id:
        err("--non-conformance-id is required")

    nc = _validate_nc_exists(conn, args.non_conformance_id)
    old_values = row_to_dict(nc)

    # Build dynamic update
    updates = []
    values = []

    if args.description is not None:
        updates.append("description = ?")
        values.append(args.description)

    if args.severity is not None:
        if args.severity not in VALID_NC_SEVERITIES:
            err(f"--severity must be one of {VALID_NC_SEVERITIES}")
        updates.append("severity = ?")
        values.append(args.severity)

    if args.root_cause is not None:
        updates.append("root_cause = ?")
        values.append(args.root_cause)

    if args.corrective_action is not None:
        updates.append("corrective_action = ?")
        values.append(args.corrective_action)

    if args.preventive_action is not None:
        updates.append("preventive_action = ?")
        values.append(args.preventive_action)

    if args.responsible_employee_id is not None:
        updates.append("responsible_employee_id = ?")
        values.append(args.responsible_employee_id)

    if args.resolution_date is not None:
        updates.append("resolution_date = ?")
        values.append(args.resolution_date)

    if args.status is not None:
        if args.status not in VALID_NC_STATUSES:
            err(f"--status must be one of {VALID_NC_STATUSES}")

        # If setting to 'closed' or 'resolved', require resolution_date
        if args.status in ("closed", "resolved"):
            resolution_date = args.resolution_date or nc["resolution_date"]
            if not resolution_date:
                err(f"--resolution-date is required when setting status to '{args.status}'")

        updates.append("status = ?")
        values.append(args.status)

    if not updates:
        err("No fields to update. Provide at least one optional flag.")

    updates.append("updated_at = datetime('now')")

    values.append(args.non_conformance_id)
    sql = f"UPDATE non_conformance SET {', '.join(updates)} WHERE id = ?"
    conn.execute(sql, values)

    # Re-fetch updated row
    rfq = Q.from_(T_nc).select(T_nc.star).where(T_nc.id == P())
    updated = conn.execute(rfq.get_sql(), (args.non_conformance_id,)).fetchone()
    new_values = row_to_dict(updated)

    audit(conn, "erpclaw-quality", "update-non-conformance", "non_conformance",
           args.non_conformance_id,
           old_values=old_values, new_values=new_values,
           description="Updated non-conformance report")
    conn.commit()

    ok({
        "non_conformance": new_values,
        "message": f"Non-conformance {args.non_conformance_id} updated",
    })


# ---------------------------------------------------------------------------
# 10. list-non-conformances
# ---------------------------------------------------------------------------

def list_non_conformances(conn, args):
    """List non-conformance reports with optional filters.

    Optional: --status, --severity, --item-id, --from-date, --to-date,
              --limit, --offset
    """
    q = Q.from_(T_nc).select(T_nc.star)
    cq = Q.from_(T_nc).select(fn.Count("*").as_("cnt"))
    params = []

    if args.status:
        if args.status not in VALID_NC_STATUSES:
            err(f"--status must be one of {VALID_NC_STATUSES}")
        q = q.where(T_nc.status == P())
        cq = cq.where(T_nc.status == P())
        params.append(args.status)

    if args.severity:
        if args.severity not in VALID_NC_SEVERITIES:
            err(f"--severity must be one of {VALID_NC_SEVERITIES}")
        q = q.where(T_nc.severity == P())
        cq = cq.where(T_nc.severity == P())
        params.append(args.severity)

    if args.item_id:
        q = q.where(T_nc.item_id == P())
        cq = cq.where(T_nc.item_id == P())
        params.append(args.item_id)

    if args.from_date:
        q = q.where(T_nc.created_at >= P())
        cq = cq.where(T_nc.created_at >= P())
        params.append(args.from_date)

    if args.to_date:
        q = q.where(T_nc.created_at <= P())
        cq = cq.where(T_nc.created_at <= P())
        params.append(args.to_date)

    # Count
    total = conn.execute(cq.get_sql(), params).fetchone()["cnt"]

    # Paginate
    limit = int(args.limit or 20)
    offset = int(args.offset or 0)
    q = q.orderby(T_nc.created_at, order=Order.desc).limit(P()).offset(P())
    page_params = list(params) + [limit, offset]

    rows = conn.execute(q.get_sql(), page_params).fetchall()
    non_conformances = [row_to_dict(r) for r in rows]

    ok({
        "non_conformances": non_conformances,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total,
    })


# ---------------------------------------------------------------------------
# 11. add-quality-goal
# ---------------------------------------------------------------------------

def add_quality_goal(conn, args):
    """Create a quality goal.

    Required: --name, --target-value
    Optional: --measurable, --monitoring-frequency, --review-date
    """
    if not args.name:
        err("--name is required")
    if not args.target_value:
        err("--target-value is required")

    monitoring_frequency = args.monitoring_frequency or "monthly"
    if monitoring_frequency not in VALID_GOAL_FREQUENCIES:
        err(f"--monitoring-frequency must be one of {VALID_GOAL_FREQUENCIES}")

    goal_id = str(uuid.uuid4())

    qg_sql, _ = insert_row("quality_goal", {
        "id": P(), "name": P(), "measurable": P(),
        "current_value": P(), "target_value": P(),
        "monitoring_frequency": P(), "status": P(), "review_date": P(),
    })
    conn.execute(qg_sql, (goal_id, args.name, args.measurable,
                           "0", args.target_value, monitoring_frequency,
                           "on_track", args.review_date))

    audit(conn, "erpclaw-quality", "add-quality-goal", "quality_goal",
           goal_id, description=f"Created quality goal '{args.name}'")
    conn.commit()

    ok({
        "quality_goal": {
            "id": goal_id,
            "name": args.name,
            "measurable": args.measurable,
            "current_value": "0",
            "target_value": args.target_value,
            "monitoring_frequency": monitoring_frequency,
            "status": "on_track",
            "review_date": args.review_date,
        },
        "message": f"Quality goal '{args.name}' created",
    })


# ---------------------------------------------------------------------------
# 12. update-quality-goal
# ---------------------------------------------------------------------------

def update_quality_goal(conn, args):
    """Update a quality goal.

    Required: --quality-goal-id
    Optional: --name, --current-value, --target-value, --status,
              --review-date, --measurable, --monitoring-frequency
    """
    if not args.quality_goal_id:
        err("--quality-goal-id is required")

    goal = _validate_goal_exists(conn, args.quality_goal_id)
    old_values = row_to_dict(goal)

    # Build dynamic update
    updates = []
    values = []

    if args.name is not None:
        updates.append("name = ?")
        values.append(args.name)

    if args.measurable is not None:
        updates.append("measurable = ?")
        values.append(args.measurable)

    if args.current_value is not None:
        updates.append("current_value = ?")
        values.append(args.current_value)

    if args.target_value is not None:
        updates.append("target_value = ?")
        values.append(args.target_value)

    if args.status is not None:
        if args.status not in VALID_GOAL_STATUSES:
            err(f"--status must be one of {VALID_GOAL_STATUSES}")
        updates.append("status = ?")
        values.append(args.status)

    if args.review_date is not None:
        updates.append("review_date = ?")
        values.append(args.review_date)

    if args.monitoring_frequency is not None:
        if args.monitoring_frequency not in VALID_GOAL_FREQUENCIES:
            err(f"--monitoring-frequency must be one of {VALID_GOAL_FREQUENCIES}")
        updates.append("monitoring_frequency = ?")
        values.append(args.monitoring_frequency)

    if not updates:
        err("No fields to update. Provide at least one optional flag.")

    updates.append("updated_at = datetime('now')")

    values.append(args.quality_goal_id)
    sql = f"UPDATE quality_goal SET {', '.join(updates)} WHERE id = ?"
    conn.execute(sql, values)

    # Re-fetch updated row
    rfq = Q.from_(T_qg).select(T_qg.star).where(T_qg.id == P())
    updated = conn.execute(rfq.get_sql(), (args.quality_goal_id,)).fetchone()
    new_values = row_to_dict(updated)

    audit(conn, "erpclaw-quality", "update-quality-goal", "quality_goal",
           args.quality_goal_id,
           old_values=old_values, new_values=new_values,
           description="Updated quality goal")
    conn.commit()

    ok({
        "quality_goal": new_values,
        "message": f"Quality goal {args.quality_goal_id} updated",
    })


# ---------------------------------------------------------------------------
# 13. quality-dashboard
# ---------------------------------------------------------------------------

def quality_dashboard(conn, args):
    """Return a quality dashboard summary.

    Returns: total inspections by status, pass rate %, open NCRs by severity,
    quality goals summary.
    """
    # --- Inspections by status ---
    iq = (Q.from_(T_qi)
          .select(T_qi.status, fn.Count("*").as_("cnt"))
          .groupby(T_qi.status))
    inspection_rows = conn.execute(iq.get_sql()).fetchall()
    inspections_by_status = {r["status"]: r["cnt"] for r in inspection_rows}
    total_inspections = sum(inspections_by_status.values())

    # Pass rate: accepted / total * 100
    accepted_count = inspections_by_status.get("accepted", 0)
    pass_rate = "0.00"
    if total_inspections > 0:
        rate = (Decimal(str(accepted_count)) / Decimal(str(total_inspections))) * Decimal("100")
        pass_rate = str(round_currency(rate))

    # --- Open NCRs by severity ---
    nq = (Q.from_(T_nc)
          .select(T_nc.severity, fn.Count("*").as_("cnt"))
          .where(T_nc.status.isin([P(), P()]))
          .groupby(T_nc.severity))
    ncr_rows = conn.execute(nq.get_sql(), ("open", "investigating")).fetchall()
    open_ncrs_by_severity = {r["severity"]: r["cnt"] for r in ncr_rows}
    total_open_ncrs = sum(open_ncrs_by_severity.values())

    # --- Quality goals summary ---
    gq = (Q.from_(T_qg)
          .select(T_qg.status, fn.Count("*").as_("cnt"))
          .groupby(T_qg.status))
    goal_rows = conn.execute(gq.get_sql()).fetchall()
    goals_by_status = {r["status"]: r["cnt"] for r in goal_rows}
    total_goals = sum(goals_by_status.values())

    ok({
        "dashboard": {
            "inspections": {
                "total": total_inspections,
                "by_status": inspections_by_status,
                "pass_rate_pct": pass_rate,
            },
            "non_conformances": {
                "total_open": total_open_ncrs,
                "by_severity": open_ncrs_by_severity,
            },
            "quality_goals": {
                "total": total_goals,
                "by_status": goals_by_status,
            },
        },
    })


# ---------------------------------------------------------------------------
# 14. status (alias for quality-dashboard)
# ---------------------------------------------------------------------------

def status_action(conn, args):
    """Alias for quality-dashboard."""
    quality_dashboard(conn, args)


# ---------------------------------------------------------------------------
# ACTIONS registry
# ---------------------------------------------------------------------------

ACTIONS = {
    "add-inspection-template": add_inspection_template,
    "get-inspection-template": get_inspection_template,
    "list-inspection-templates": list_inspection_templates,
    "add-quality-inspection": add_quality_inspection,
    "record-inspection-readings": record_inspection_readings,
    "evaluate-inspection": evaluate_inspection,
    "list-quality-inspections": list_quality_inspections,
    "add-non-conformance": add_non_conformance,
    "update-non-conformance": update_non_conformance,
    "list-non-conformances": list_non_conformances,
    "add-quality-goal": add_quality_goal,
    "update-quality-goal": update_quality_goal,
    "quality-dashboard": quality_dashboard,
    "status": status_action,
}


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ERPClaw Quality Skill")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # Entity IDs
    parser.add_argument("--company-id")
    parser.add_argument("--template-id")
    parser.add_argument("--quality-inspection-id")
    parser.add_argument("--non-conformance-id")
    parser.add_argument("--quality-goal-id")
    parser.add_argument("--item-id")
    parser.add_argument("--batch-id")

    # Template fields
    parser.add_argument("--name")
    parser.add_argument("--description")
    parser.add_argument("--inspection-type")
    parser.add_argument("--parameters")  # JSON array

    # Inspection fields
    parser.add_argument("--inspection-date")
    parser.add_argument("--inspected-by")
    parser.add_argument("--sample-size")
    parser.add_argument("--reference-type")
    parser.add_argument("--reference-id")
    parser.add_argument("--remarks")

    # Readings JSON
    parser.add_argument("--readings")  # JSON array

    # Non-conformance fields
    parser.add_argument("--severity")
    parser.add_argument("--root-cause")
    parser.add_argument("--corrective-action")
    parser.add_argument("--preventive-action")
    parser.add_argument("--responsible-employee-id")
    parser.add_argument("--resolution-date")

    # Quality goal fields
    parser.add_argument("--measurable")
    parser.add_argument("--current-value")
    parser.add_argument("--target-value")
    parser.add_argument("--monitoring-frequency")
    parser.add_argument("--review-date")

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
        sys.stderr.write(f"[erpclaw-quality] {e}\n")
        err("An unexpected error occurred")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
