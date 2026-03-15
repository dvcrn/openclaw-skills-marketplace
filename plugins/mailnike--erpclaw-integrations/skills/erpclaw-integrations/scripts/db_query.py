#!/usr/bin/env python3
"""ERPClaw Integrations Skill -- db_query.py

Unified external integrations: Plaid bank sync, Stripe payments, S3 cloud backups.
All external API calls are mocked -- no real network requests are made.

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout, exit 0 on success, exit 1 on error.
"""
import argparse
import hashlib
import json
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

# ---------------------------------------------------------------------------
# Shared library
# ---------------------------------------------------------------------------
try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection, ensure_db_exists, DEFAULT_DB_PATH
    from erpclaw_lib.decimal_utils import to_decimal, round_currency
    from erpclaw_lib.validation import check_input_lengths
    from erpclaw_lib.response import ok, err, row_to_dict, rows_to_list
    from erpclaw_lib.audit import audit
    from erpclaw_lib.dependencies import check_required_tables
    from erpclaw_lib.query import Q, P, Table, Field, fn, Case, Order, Criterion, insert_row, update_row
    from erpclaw_lib.vendor.pypika.terms import LiteralValue, ValueWrapper
except ImportError:
    import json as _json
    print(_json.dumps({"status": "error", "error": "ERPClaw foundation not installed. Install erpclaw first: clawhub install erpclaw", "suggestion": "clawhub install erpclaw"}))
    sys.exit(1)

REQUIRED_TABLES = ["company"]

SKILL_NAME = "erpclaw-integrations"


# ===========================================================================
#
#  PLAID — Bank Account Integration (mock)
#
# ===========================================================================

# ---------------------------------------------------------------------------
# Mock bank transaction data
# ---------------------------------------------------------------------------
MOCK_TRANSACTIONS = [
    {
        "name": "Starbucks Store #12345",
        "amount": "-4.85",
        "category": "Food and Drink",
        "merchant_name": "Starbucks",
    },
    {
        "name": "Amazon Prime Membership",
        "amount": "-14.99",
        "category": "Service",
        "merchant_name": "Amazon",
    },
    {
        "name": "Whole Foods Market #10234",
        "amount": "-87.32",
        "category": "Shops",
        "merchant_name": "Whole Foods",
    },
    {
        "name": "Comcast Internet Bill",
        "amount": "-125.00",
        "category": "Service",
        "merchant_name": "Comcast",
    },
    {
        "name": "Wire Transfer from Acme Corp",
        "amount": "2500.00",
        "category": "Transfer",
        "merchant_name": "Acme Corp",
    },
]


# ---------------------------------------------------------------------------
# Plaid helpers
# ---------------------------------------------------------------------------

def _plaid_get_config_or_err(conn, company_id: str) -> dict:
    """Fetch Plaid config for a company. Calls err() if not found."""
    pc = Table("plaid_config")
    q = Q.from_(pc).select(pc.star).where(pc.company_id == P())
    row = conn.execute(q.get_sql(), (company_id,)).fetchone()
    if not row:
        err(f"Plaid config not found for company {company_id}",
            suggestion="Run 'configure-plaid' first to set up Plaid credentials.")
    return row_to_dict(row)


def _plaid_get_linked_account_or_err(conn, linked_account_id: str) -> dict:
    """Fetch a linked account by ID. Calls err() if not found."""
    pla = Table("plaid_linked_account")
    q = Q.from_(pla).select(pla.star).where(pla.id == P())
    row = conn.execute(q.get_sql(), (linked_account_id,)).fetchone()
    if not row:
        err(f"Linked account {linked_account_id} not found",
            suggestion="Use 'list-transactions' or check the linked account ID.")
    return row_to_dict(row)


# ---------------------------------------------------------------------------
# Plaid actions
# ---------------------------------------------------------------------------

def configure_plaid(conn, args):
    """Save Plaid configuration (client_id, secret, environment) for a company.

    Each company can have exactly one Plaid config (UNIQUE constraint on company_id).
    """
    company_id = args.company_id
    if not company_id:
        err("--company-id is required")

    client_id = args.client_id
    if not client_id:
        err("--client-id is required")

    secret = args.secret
    if not secret:
        err("--secret is required")

    environment = args.environment or "sandbox"
    if environment not in ("sandbox", "development", "production"):
        err(f"Invalid environment '{environment}'. Must be: sandbox, development, production")

    # Validate company exists
    co = Table("company")
    q = Q.from_(co).select(co.id).where(co.id == P())
    if not conn.execute(q.get_sql(), (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    # Check for existing config
    pc = Table("plaid_config")
    q = Q.from_(pc).select(pc.id).where(pc.company_id == P())
    existing = conn.execute(q.get_sql(), (company_id,)).fetchone()
    if existing:
        err(f"Config already exists for this company",
            suggestion="Each company can only have one Plaid configuration.")

    # Encrypt sensitive credentials before storing
    from erpclaw_lib.crypto import encrypt_field, derive_key
    from erpclaw_lib.db import DEFAULT_DB_PATH
    _fk = derive_key(os.environ.get("ERPCLAW_DB_PATH", DEFAULT_DB_PATH),
                      b"erpclaw-field-key")
    enc_client_id = encrypt_field(client_id, _fk)
    enc_secret = encrypt_field(secret, _fk)

    config_id = str(uuid.uuid4())
    sql, _ = insert_row("plaid_config", {
        "id": P(), "company_id": P(), "client_id": P(),
        "secret": P(), "environment": P(),
    })
    conn.execute(sql, (config_id, company_id, enc_client_id, enc_secret, environment))

    audit(conn, SKILL_NAME, "configure-plaid", "plaid_config", config_id,
          new_values={"company_id": company_id, "environment": environment})
    conn.commit()

    ok({"config_id": config_id, "company_id": company_id,
        "environment": environment, "message": "Plaid configured successfully"})


def link_account(conn, args):
    """Mock-link a bank account via Plaid.

    Generates a fake access token and creates a plaid_linked_account record.
    In production, this would involve the Plaid Link flow and token exchange.
    """
    company_id = args.company_id
    if not company_id:
        err("--company-id is required")

    institution_name = args.institution_name
    if not institution_name:
        err("--institution-name is required")

    account_name = args.account_name
    if not account_name:
        err("--account-name is required")

    account_type = args.account_type
    if not account_type:
        err("--account-type is required")

    account_mask = args.account_mask
    if not account_mask:
        err("--account-mask is required")

    # Validate company exists
    co = Table("company")
    q = Q.from_(co).select(co.id).where(co.id == P())
    if not conn.execute(q.get_sql(), (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    # Validate Plaid config exists for this company
    _plaid_get_config_or_err(conn, company_id)

    # Validate ERP account if provided
    erp_account_id = args.erp_account_id
    if erp_account_id:
        acc = Table("account")
        q = Q.from_(acc).select(acc.id).where(acc.id == P())
        if not conn.execute(q.get_sql(), (erp_account_id,)).fetchone():
            err(f"ERP account {erp_account_id} not found")

    # Generate mock access token
    access_token = f"mock-access-{uuid.uuid4()}"

    linked_id = str(uuid.uuid4())
    sql, _ = insert_row("plaid_linked_account", {
        "id": P(), "company_id": P(), "access_token": P(),
        "institution_name": P(), "account_name": P(),
        "account_type": P(), "account_mask": P(), "erp_account_id": P(),
    })
    conn.execute(sql, (linked_id, company_id, access_token, institution_name,
         account_name, account_type, account_mask, erp_account_id))

    audit(conn, SKILL_NAME, "link-account", "plaid_linked_account", linked_id,
          new_values={"institution_name": institution_name,
                      "account_name": account_name,
                      "account_type": account_type})
    conn.commit()

    ok({"linked_account_id": linked_id,
        "institution_name": institution_name,
        "account_name": account_name,
        "account_type": account_type,
        "account_mask": account_mask,
        "access_token": access_token,
        "message": "Bank account linked successfully (mock)"})


def sync_transactions(conn, args):
    """Mock-sync bank transactions from Plaid.

    Generates 5 sample transactions with realistic merchant names and amounts.
    Uses a deterministic seed based on the linked account ID so repeated syncs
    with the same date range produce the same transaction IDs (idempotent).
    """
    linked_account_id = args.linked_account_id
    if not linked_account_id:
        err("--linked-account-id is required")

    linked = _plaid_get_linked_account_or_err(conn, linked_account_id)

    # Determine date range for mock transactions
    to_date = args.to_date or datetime.now().strftime("%Y-%m-%d")
    from_date = args.from_date or (
        datetime.strptime(to_date, "%Y-%m-%d") - timedelta(days=30)
    ).strftime("%Y-%m-%d")

    # Generate mock transactions with deterministic IDs based on linked account
    # This ensures idempotency: same linked account + same data = same txn IDs
    base_date = datetime.strptime(from_date, "%Y-%m-%d")
    created_count = 0
    skipped_count = 0
    transactions = []

    for i, mock in enumerate(MOCK_TRANSACTIONS):
        # Deterministic transaction ID: based on linked account + index
        txn_id = f"mock-txn-{linked_account_id[:8]}-{i:04d}"
        txn_date = (base_date + timedelta(days=i * 5 + 1)).strftime("%Y-%m-%d")

        # Check if already synced (idempotent)
        pt = Table("plaid_transaction")
        q = (Q.from_(pt).select(pt.id)
             .where(pt.plaid_linked_account_id == P())
             .where(pt.plaid_transaction_id == P()))
        existing = conn.execute(q.get_sql(), (linked_account_id, txn_id)).fetchone()

        if existing:
            skipped_count += 1
            continue

        row_id = str(uuid.uuid4())
        sql, _ = insert_row("plaid_transaction", {
            "id": P(), "plaid_linked_account_id": P(),
            "plaid_transaction_id": P(), "date": P(),
            "amount": P(), "name": P(), "category": P(),
            "merchant_name": P(),
        })
        conn.execute(sql, (row_id, linked_account_id, txn_id, txn_date,
             mock["amount"], mock["name"], mock["category"],
             mock["merchant_name"]))
        created_count += 1
        transactions.append({
            "id": row_id,
            "plaid_transaction_id": txn_id,
            "date": txn_date,
            "amount": mock["amount"],
            "name": mock["name"],
            "merchant_name": mock["merchant_name"],
            "match_status": "unmatched",
        })

    # Update last_synced_at
    pla = Table("plaid_linked_account")
    now_fn = LiteralValue("datetime('now')")
    q = (Q.update(pla)
         .set(pla.last_synced_at, now_fn)
         .set(pla.updated_at, now_fn)
         .where(pla.id == P()))
    conn.execute(q.get_sql(), (linked_account_id,))

    audit(conn, SKILL_NAME, "sync-transactions", "plaid_linked_account",
          linked_account_id,
          new_values={"created": created_count, "skipped": skipped_count})
    conn.commit()

    ok({"linked_account_id": linked_account_id,
        "created": created_count,
        "skipped": skipped_count,
        "transactions": transactions,
        "message": f"Synced {created_count} new transactions ({skipped_count} already existed)"})


def match_transactions(conn, args):
    """Auto-match unmatched plaid_transactions to gl_entries.

    Matching criteria:
    - ABS(plaid_transaction.amount) == ABS(gl_entry.debit - gl_entry.credit)
    - gl_entry.posting_date within +/- 3 days of plaid_transaction.date
    - gl_entry.is_cancelled = 0
    - gl_entry.account_id matches the linked account's erp_account_id (if set)
    """
    linked_account_id = args.linked_account_id
    if not linked_account_id:
        err("--linked-account-id is required")

    linked = _plaid_get_linked_account_or_err(conn, linked_account_id)
    erp_account_id = linked.get("erp_account_id")

    # Get all unmatched transactions for this linked account
    pt = Table("plaid_transaction")
    q = (Q.from_(pt)
         .select(pt.id, pt.plaid_transaction_id, pt.date, pt.amount, pt.name)
         .where(pt.plaid_linked_account_id == P())
         .where(pt.match_status == ValueWrapper("unmatched"))
         .orderby(pt.date))
    unmatched = conn.execute(q.get_sql(), (linked_account_id,)).fetchall()

    matched_count = 0
    unmatched_count = 0
    matches = []

    for txn in unmatched:
        txn_dict = row_to_dict(txn)
        txn_amount = abs(to_decimal(txn_dict["amount"]))
        txn_date = txn_dict["date"]

        # Calculate date window: +/- 3 days
        dt = datetime.strptime(txn_date, "%Y-%m-%d")
        date_from = (dt - timedelta(days=3)).strftime("%Y-%m-%d")
        date_to = (dt + timedelta(days=3)).strftime("%Y-%m-%d")

        # Build GL query
        if erp_account_id:
            gl_row = conn.execute(
                """SELECT id, posting_date, debit, credit
                   FROM gl_entry
                   WHERE account_id = ?
                     AND posting_date >= ? AND posting_date <= ?
                     AND is_cancelled = 0
                     AND id NOT IN (
                         SELECT matched_gl_entry_id FROM plaid_transaction
                         WHERE matched_gl_entry_id IS NOT NULL
                     )
                   ORDER BY posting_date
                   LIMIT 50""",
                (erp_account_id, date_from, date_to),
            ).fetchall()
        else:
            gl_row = conn.execute(
                """SELECT id, posting_date, debit, credit
                   FROM gl_entry
                   WHERE posting_date >= ? AND posting_date <= ?
                     AND is_cancelled = 0
                     AND id NOT IN (
                         SELECT matched_gl_entry_id FROM plaid_transaction
                         WHERE matched_gl_entry_id IS NOT NULL
                     )
                   ORDER BY posting_date
                   LIMIT 50""",
                (date_from, date_to),
            ).fetchall()

        # Find a GL entry with matching amount
        found_match = False
        for gl in gl_row:
            gl_dict = row_to_dict(gl)
            gl_debit = to_decimal(gl_dict["debit"] or "0")
            gl_credit = to_decimal(gl_dict["credit"] or "0")
            gl_net = abs(gl_debit - gl_credit)

            if gl_net == txn_amount:
                # Match found
                pt_upd = Table("plaid_transaction")
                q_upd = (Q.update(pt_upd)
                         .set(pt_upd.matched_gl_entry_id, P())
                         .set(pt_upd.match_status, ValueWrapper("auto_matched"))
                         .where(pt_upd.id == P()))
                conn.execute(q_upd.get_sql(), (gl_dict["id"], txn_dict["id"]))
                matched_count += 1
                matches.append({
                    "transaction_id": txn_dict["id"],
                    "transaction_name": txn_dict["name"],
                    "transaction_amount": txn_dict["amount"],
                    "gl_entry_id": gl_dict["id"],
                    "gl_posting_date": gl_dict["posting_date"],
                })
                found_match = True
                break

        if not found_match:
            unmatched_count += 1

    audit(conn, SKILL_NAME, "match-transactions", "plaid_linked_account",
          linked_account_id,
          new_values={"matched": matched_count, "unmatched": unmatched_count})
    conn.commit()

    ok({"linked_account_id": linked_account_id,
        "matched": matched_count,
        "unmatched": unmatched_count,
        "matches": matches,
        "message": f"Matched {matched_count} transactions, {unmatched_count} remain unmatched"})


def list_transactions(conn, args):
    """List synced transactions for a linked account with optional filters."""
    linked_account_id = args.linked_account_id
    if not linked_account_id:
        err("--linked-account-id is required")

    # Verify linked account exists
    _plaid_get_linked_account_or_err(conn, linked_account_id)

    pt = Table("plaid_transaction")
    params = [linked_account_id]

    # Build base WHERE
    q_base = Q.from_(pt).where(pt.plaid_linked_account_id == P())
    if args.match_status:
        q_base = q_base.where(pt.match_status == P())
        params.append(args.match_status)
    if args.from_date:
        q_base = q_base.where(pt.date >= P())
        params.append(args.from_date)
    if args.to_date:
        q_base = q_base.where(pt.date <= P())
        params.append(args.to_date)

    # Count query
    q_count = q_base.select(fn.Count("*"))
    count_row = conn.execute(q_count.get_sql(), params).fetchone()
    total_count = count_row[0]

    limit = int(args.limit) if args.limit else 20
    offset = int(args.offset) if args.offset else 0

    # Data query
    q_data = (q_base
              .select(pt.id, pt.plaid_transaction_id, pt.date, pt.amount,
                      pt.name, pt.category, pt.merchant_name,
                      pt.matched_gl_entry_id, pt.match_status)
              .orderby(pt.date, order=Order.desc)
              .limit(P()).offset(P()))
    rows = conn.execute(q_data.get_sql(), params + [limit, offset]).fetchall()

    ok({"transactions": [row_to_dict(r) for r in rows],
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total_count})


def plaid_status(conn, args):
    """Show Plaid integration status: config count, linked accounts, transactions."""
    company_id = args.company_id
    if not company_id:
        co = Table("company")
        q = Q.from_(co).select(co.id).limit(1)
        row = conn.execute(q.get_sql()).fetchone()
        if not row:
            err("No company found. Create one with erpclaw first.",
                suggestion="Run 'tutorial' to create a demo company, or 'setup company' to create your own.")
        company_id = row["id"]

    # Config status
    pc = Table("plaid_config")
    q = (Q.from_(pc).select(pc.id, pc.environment, pc.status)
         .where(pc.company_id == P()))
    config = conn.execute(q.get_sql(), (company_id,)).fetchone()

    config_info = None
    if config:
        config_dict = row_to_dict(config)
        config_info = {
            "config_id": config_dict["id"],
            "environment": config_dict["environment"],
            "status": config_dict["status"],
        }

    # Linked accounts
    pla = Table("plaid_linked_account")
    q = (Q.from_(pla)
         .select(
             fn.Count("*").as_("total"),
             fn.Sum(Case().when(pla.status == ValueWrapper("active"), 1).else_(0)).as_("active"),
         )
         .where(pla.company_id == P()))
    accounts = conn.execute(q.get_sql(), (company_id,)).fetchone()

    # Transaction counts by match status
    pt = Table("plaid_transaction")
    pla2 = Table("plaid_linked_account")
    q = (Q.from_(pt)
         .join(pla2).on(pt.plaid_linked_account_id == pla2.id)
         .select(pt.match_status, fn.Count("*").as_("cnt"))
         .where(pla2.company_id == P())
         .groupby(pt.match_status))
    txn_counts = conn.execute(q.get_sql(), (company_id,)).fetchall()

    txn_summary = {}
    total_txns = 0
    for row in txn_counts:
        d = row_to_dict(row)
        txn_summary[d["match_status"]] = d["cnt"]
        total_txns += d["cnt"]

    return {
        "config": config_info,
        "linked_accounts": {
            "total": accounts["total"] or 0,
            "active": accounts["active"] or 0,
        },
        "transactions": {
            "total": total_txns,
            **txn_summary,
        },
    }


# ===========================================================================
#
#  STRIPE -- Payment Gateway Integration (mock)
#
# ===========================================================================

# ---------------------------------------------------------------------------
# Stripe helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _mock_stripe_id(prefix: str) -> str:
    """Generate a realistic-looking mock Stripe ID."""
    short = uuid.uuid4().hex[:24]
    return f"{prefix}_mock_{short}"


def _stripe_get_config(conn, company_id: str):
    """Fetch stripe config for a company. Returns dict or calls err()."""
    sc = Table("stripe_config")
    q = (Q.from_(sc).select(sc.star)
         .where(sc.company_id == P())
         .where(sc.status == ValueWrapper("active")))
    row = conn.execute(q.get_sql(), (company_id,)).fetchone()
    if not row:
        err(f"Stripe not configured for company {company_id}",
            suggestion="Use 'configure-stripe' action to set up Stripe credentials first.")
    return row_to_dict(row)


# ---------------------------------------------------------------------------
# Stripe actions
# ---------------------------------------------------------------------------

def configure_stripe(conn, args):
    """Save Stripe API credentials for a company."""
    if not args.company_id:
        err("--company-id is required")
    if not args.publishable_key:
        err("--publishable-key is required")
    if not args.secret_key:
        err("--secret-key is required")

    # Validate company exists
    co = Table("company")
    q = Q.from_(co).select(co.id, co.name).where(co.id == P())
    company = conn.execute(q.get_sql(), (args.company_id,)).fetchone()
    if not company:
        err(f"Company not found: {args.company_id}")

    # Check for existing config
    sc = Table("stripe_config")
    q = Q.from_(sc).select(sc.id).where(sc.company_id == P())
    existing = conn.execute(q.get_sql(), (args.company_id,)).fetchone()
    if existing:
        err(f"Stripe already configured for company {args.company_id}. "
            "Only one configuration per company is allowed.",
            suggestion="Update the existing config or delete it first.")

    mode = args.mode or "test"
    if mode not in ("test", "live"):
        err(f"Invalid mode: {mode}. Must be 'test' or 'live'")

    # Encrypt sensitive credentials before storing
    from erpclaw_lib.crypto import encrypt_field, derive_key
    from erpclaw_lib.db import DEFAULT_DB_PATH
    _fk = derive_key(os.environ.get("ERPCLAW_DB_PATH", DEFAULT_DB_PATH),
                      b"erpclaw-field-key")
    enc_publishable = encrypt_field(args.publishable_key, _fk)
    enc_secret = encrypt_field(args.secret_key, _fk)
    enc_webhook = encrypt_field(args.webhook_secret, _fk) if args.webhook_secret else None

    config_id = str(uuid.uuid4())
    now_ts = _now()
    sql, _ = insert_row("stripe_config", {
        "id": P(), "company_id": P(), "publishable_key": P(),
        "secret_key": P(), "webhook_secret": P(),
        "mode": P(), "status": P(), "created_at": P(), "updated_at": P(),
    })
    conn.execute(sql, (config_id, args.company_id, enc_publishable, enc_secret,
         enc_webhook, mode, "active", now_ts, now_ts))
    conn.commit()
    audit(conn, SKILL_NAME, "configure-stripe", "stripe_config", config_id,
          new_values={"company_id": args.company_id, "mode": mode})

    sc2 = Table("stripe_config")
    q = (Q.from_(sc2).select(sc2.id, sc2.company_id, sc2.mode, sc2.status, sc2.created_at)
         .where(sc2.id == P()))
    config = row_to_dict(conn.execute(q.get_sql(), (config_id,)).fetchone())
    ok({"stripe_config": config,
        "message": f"Stripe configured for company {company['name']} in {mode} mode"})


def create_payment_intent(conn, args):
    """Create a mock Stripe payment intent linked to a sales invoice."""
    if not args.invoice_id:
        err("--invoice-id is required")
    if not args.amount:
        err("--amount is required")

    # Validate amount
    amount = to_decimal(args.amount)
    if amount <= Decimal("0"):
        err("Amount must be greater than zero")

    # Look up the sales invoice
    si = Table("sales_invoice")
    q = (Q.from_(si).select(si.id, si.customer_id, si.grand_total, si.currency, si.status)
         .where(si.id == P()))
    invoice = conn.execute(q.get_sql(), (args.invoice_id,)).fetchone()
    if not invoice:
        err(f"Sales invoice not found: {args.invoice_id}",
            suggestion="Use erpclaw-selling 'list-sales-invoices' to find valid invoice IDs.")

    # Resolve company from customer
    cust = Table("customer")
    q = Q.from_(cust).select(cust.company_id).where(cust.id == P())
    customer = conn.execute(q.get_sql(), (invoice["customer_id"],)).fetchone()
    if not customer:
        err(f"Customer not found for invoice {args.invoice_id}")

    company_id = customer["company_id"]

    # Ensure Stripe is configured for this company
    _stripe_get_config(conn, company_id)

    currency = args.currency or invoice["currency"] or "USD"
    stripe_id = _mock_stripe_id("pi")
    metadata = args.metadata or None

    intent_id = str(uuid.uuid4())
    now_ts = _now()
    sql, _ = insert_row("stripe_payment_intent", {
        "id": P(), "company_id": P(), "stripe_id": P(),
        "amount": P(), "currency": P(), "customer_id": P(),
        "sales_invoice_id": P(), "status": P(), "payment_entry_id": P(),
        "metadata": P(), "created_at": P(), "updated_at": P(),
    })
    conn.execute(sql, (intent_id, company_id, stripe_id, str(round_currency(amount)),
         currency, invoice["customer_id"], args.invoice_id,
         "created", None, metadata, now_ts, now_ts))
    conn.commit()
    audit(conn, SKILL_NAME, "create-payment-intent",
          "stripe_payment_intent", intent_id,
          new_values={"stripe_id": stripe_id, "amount": str(amount),
                      "invoice_id": args.invoice_id})

    spi = Table("stripe_payment_intent")
    q = Q.from_(spi).select(spi.star).where(spi.id == P())
    intent = row_to_dict(conn.execute(q.get_sql(), (intent_id,)).fetchone())
    ok({"payment_intent": intent})


def sync_payments(conn, args):
    """Check all pending payment intents and update status.

    In mock mode, all 'created' intents are moved to 'succeeded'.
    In a real integration, this would poll the Stripe API.
    """
    if not args.company_id:
        err("--company-id is required")

    # Verify config exists
    _stripe_get_config(conn, args.company_id)

    # Find all created/processing intents for this company
    spi = Table("stripe_payment_intent")
    q = (Q.from_(spi).select(spi.star)
         .where(spi.company_id == P())
         .where(spi.status.isin([ValueWrapper("created"), ValueWrapper("processing")])))
    pending = conn.execute(q.get_sql(), (args.company_id,)).fetchall()

    synced = []
    for pi in pending:
        pi_dict = row_to_dict(pi)
        # Mock: all pending intents succeed
        q_upd = (Q.update(spi)
                 .set(spi.status, ValueWrapper("succeeded"))
                 .set(spi.updated_at, P())
                 .where(spi.id == P()))
        conn.execute(q_upd.get_sql(), (_now(), pi_dict["id"]))
        synced.append({
            "id": pi_dict["id"],
            "stripe_id": pi_dict["stripe_id"],
            "amount": pi_dict["amount"],
            "previous_status": pi_dict["status"],
            "new_status": "succeeded",
            "sales_invoice_id": pi_dict["sales_invoice_id"],
        })

    conn.commit()

    if synced:
        audit(conn, SKILL_NAME, "sync-payments",
              "stripe_payment_intent", ",".join(s["id"] for s in synced),
              new_values={"synced_count": len(synced)})

    ok({
        "synced_count": len(synced),
        "synced": synced,
        "message": f"Synced {len(synced)} payment(s) for company {args.company_id}",
    })


def handle_webhook(conn, args):
    """Process a mock Stripe webhook event.

    For payment_intent.succeeded events, updates the payment intent status
    and records the webhook event. Duplicate events are safely ignored
    (idempotent via stripe_event_id UNIQUE constraint).
    """
    if not args.event_id:
        err("--event-id is required (Stripe event ID, e.g. evt_mock_xxx)")
    if not args.event_type:
        err("--event-type is required (e.g. payment_intent.succeeded)")
    if not args.payload:
        err("--payload is required (JSON string)")

    # Validate payload is valid JSON
    try:
        payload_data = json.loads(args.payload)
    except (json.JSONDecodeError, TypeError):
        err("--payload must be valid JSON")

    # Check for duplicate event (idempotency)
    swe = Table("stripe_webhook_event")
    q = (Q.from_(swe).select(swe.id, swe.processed)
         .where(swe.stripe_event_id == P()))
    existing = conn.execute(q.get_sql(), (args.event_id,)).fetchone()
    if existing:
        q2 = Q.from_(swe).select(swe.star).where(swe.id == P())
        evt = row_to_dict(conn.execute(q2.get_sql(), (existing["id"],)).fetchone())
        ok({"webhook_event": evt, "deduplicated": True,
            "message": "Duplicate webhook event -- already processed"})

    # Insert webhook event record
    webhook_id = str(uuid.uuid4())
    error_message = None
    processed = 0
    processed_at = None

    # Process based on event type
    spi = Table("stripe_payment_intent")
    if args.event_type == "payment_intent.succeeded":
        stripe_pi_id = payload_data.get("payment_intent_id") or payload_data.get("stripe_id")
        if stripe_pi_id:
            q = (Q.from_(spi).select(spi.id, spi.status)
                 .where(spi.stripe_id == P()))
            pi = conn.execute(q.get_sql(), (stripe_pi_id,)).fetchone()
            if pi:
                q_upd = (Q.update(spi)
                         .set(spi.status, ValueWrapper("succeeded"))
                         .set(spi.updated_at, P())
                         .where(spi.id == P()))
                conn.execute(q_upd.get_sql(), (_now(), pi["id"]))
                processed = 1
                processed_at = _now()
            else:
                error_message = f"Payment intent not found for stripe_id: {stripe_pi_id}"
        else:
            error_message = "No payment_intent_id or stripe_id in payload"

    elif args.event_type == "payment_intent.payment_failed":
        stripe_pi_id = payload_data.get("payment_intent_id") or payload_data.get("stripe_id")
        if stripe_pi_id:
            q = Q.from_(spi).select(spi.id).where(spi.stripe_id == P())
            pi = conn.execute(q.get_sql(), (stripe_pi_id,)).fetchone()
            if pi:
                q_upd = (Q.update(spi)
                         .set(spi.status, ValueWrapper("failed"))
                         .set(spi.updated_at, P())
                         .where(spi.id == P()))
                conn.execute(q_upd.get_sql(), (_now(), pi["id"]))
                processed = 1
                processed_at = _now()
            else:
                error_message = f"Payment intent not found for stripe_id: {stripe_pi_id}"
        else:
            error_message = "No payment_intent_id or stripe_id in payload"

    else:
        # Unknown event type -- store but mark as unprocessed
        error_message = f"Unhandled event type: {args.event_type}"

    sql, _ = insert_row("stripe_webhook_event", {
        "id": P(), "stripe_event_id": P(), "event_type": P(),
        "payload": P(), "processed": P(),
        "processed_at": P(), "error_message": P(), "created_at": P(),
    })
    conn.execute(sql, (webhook_id, args.event_id, args.event_type, args.payload,
         processed, processed_at, error_message, _now()))
    conn.commit()
    audit(conn, SKILL_NAME, "handle-webhook",
          "stripe_webhook_event", webhook_id,
          new_values={"event_type": args.event_type,
                      "stripe_event_id": args.event_id,
                      "processed": processed})

    q = Q.from_(swe).select(swe.star).where(swe.id == P())
    evt = row_to_dict(conn.execute(q.get_sql(), (webhook_id,)).fetchone())
    ok({"webhook_event": evt, "deduplicated": False})


def list_stripe_payments(conn, args):
    """List payment intents with optional filters."""
    spi = Table("stripe_payment_intent")
    c = Table("customer")
    params = []

    if args.status:
        if args.status not in ("created", "processing", "succeeded", "failed", "cancelled"):
            err(f"Invalid status: {args.status}. "
                "Must be one of: created, processing, succeeded, failed, cancelled")

    # Build base query with optional filters
    q_base = Q.from_(spi)
    if args.company_id:
        q_base = q_base.where(spi.company_id == P())
        params.append(args.company_id)
    if args.status:
        q_base = q_base.where(spi.status == P())
        params.append(args.status)
    if args.invoice_id:
        q_base = q_base.where(spi.sales_invoice_id == P())
        params.append(args.invoice_id)

    limit = int(args.limit or 20)
    offset = int(args.offset or 0)

    # Count query
    q_count = q_base.select(fn.Count("*").as_("cnt"))
    total_count = conn.execute(q_count.get_sql(), params).fetchone()["cnt"]

    # Data query with LEFT JOIN for customer name
    q_data = (q_base
              .left_join(c).on(spi.customer_id == c.id)
              .select(spi.star, c.name.as_("customer_name"))
              .orderby(spi.created_at, order=Order.desc)
              .limit(P()).offset(P()))
    rows = conn.execute(q_data.get_sql(), params + [limit, offset]).fetchall()

    ok({
        "payment_intents": [dict(r) for r in rows],
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total_count,
    })


def stripe_status(conn, args):
    """Stripe integration summary."""
    if args.company_id:
        co = Table("company")
        q = Q.from_(co).select(co.id).where(co.id == P())
        company = conn.execute(q.get_sql(), (args.company_id,)).fetchone()
        if not company:
            err(f"Company not found: {args.company_id}")

    # Config count
    sc = Table("stripe_config")
    q_cfg = Q.from_(sc).select(fn.Count("*").as_("cnt"))
    if args.company_id:
        q_cfg = q_cfg.where(sc.company_id == P())
        config_count = conn.execute(q_cfg.get_sql(), (args.company_id,)).fetchone()["cnt"]
    else:
        config_count = conn.execute(q_cfg.get_sql()).fetchone()["cnt"]

    # Payment intent counts by status
    spi = Table("stripe_payment_intent")
    q_pi = Q.from_(spi).select(spi.status, fn.Count("*").as_("cnt")).groupby(spi.status)
    params_pi = []
    if args.company_id:
        q_pi = q_pi.where(spi.company_id == P())
        params_pi = [args.company_id]
    pi_counts = {}
    for row in conn.execute(q_pi.get_sql(), params_pi).fetchall():
        pi_counts[row["status"]] = row["cnt"]

    pi_total = sum(pi_counts.values())

    # Webhook event counts
    swe_t = Table("stripe_webhook_event")
    q_wh = Q.from_(swe_t).select(fn.Count("*").as_("cnt"))
    wh_total = conn.execute(q_wh.get_sql()).fetchone()["cnt"]
    q_wh_proc = Q.from_(swe_t).select(fn.Count("*").as_("cnt")).where(swe_t.processed == 1)
    wh_processed = conn.execute(q_wh_proc.get_sql()).fetchone()["cnt"]
    wh_unprocessed = wh_total - wh_processed

    return {
        "configured_companies": config_count,
        "payment_intents": pi_counts,
        "payment_intents_total": pi_total,
        "webhook_events_total": wh_total,
        "webhook_events_processed": wh_processed,
        "webhook_events_unprocessed": wh_unprocessed,
    }


# ===========================================================================
#
#  S3 -- Cloud Backup (mock)
#
# ===========================================================================

# ---------------------------------------------------------------------------
# S3 helpers
# ---------------------------------------------------------------------------

def _s3_get_db_path_for_conn(conn):
    """Resolve the file path of the database associated with a connection."""
    row = conn.execute("PRAGMA database_list").fetchone()
    if row:
        return row[2] or DEFAULT_DB_PATH
    return DEFAULT_DB_PATH


def _s3_compute_file_checksum(file_path):
    """Compute SHA-256 checksum of a file.  Returns hex digest string."""
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            sha.update(chunk)
    return sha.hexdigest()


def _s3_get_file_size(file_path):
    """Return file size in bytes."""
    return os.path.getsize(file_path)


def _s3_generate_s3_key(prefix):
    """Generate a mock S3 object key with a timestamp."""
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H-%M-%S")
    prefix = prefix or "erpclaw-backups/"
    if not prefix.endswith("/"):
        prefix += "/"
    return f"{prefix}{timestamp}.sqlite"


def _s3_validate_company_exists(conn, company_id):
    """Validate that a company exists, or error."""
    co = Table("company")
    q = Q.from_(co).select(co.id, co.name).where(co.id == P())
    row = conn.execute(q.get_sql(), (company_id,)).fetchone()
    if not row:
        err(f"Company not found: {company_id}")
    return row


def _s3_get_config(conn, company_id):
    """Fetch the active S3 config for a company, or None."""
    s3c = Table("s3_config")
    q = (Q.from_(s3c).select(s3c.star)
         .where(s3c.company_id == P())
         .where(s3c.status == ValueWrapper("active")))
    return conn.execute(q.get_sql(), (company_id,)).fetchone()


def _s3_validate_backup_exists(conn, backup_id):
    """Fetch a backup record by ID, or error if not found."""
    s3b = Table("s3_backup_record")
    q = Q.from_(s3b).select(s3b.star).where(s3b.id == P())
    row = conn.execute(q.get_sql(), (backup_id,)).fetchone()
    if not row:
        err(f"Backup record not found: {backup_id}")
    return row


# ---------------------------------------------------------------------------
# S3 actions
# ---------------------------------------------------------------------------

def configure_s3(conn, args):
    """Save S3 configuration for a company.

    Required: --company-id, --bucket-name, --access-key-id, --secret-access-key
    Optional: --region (us-east-1), --prefix (erpclaw-backups/)
    """
    if not args.company_id:
        err("--company-id is required")
    if not args.bucket_name:
        err("--bucket-name is required")
    if not args.access_key_id:
        err("--access-key-id is required")
    if not args.secret_access_key:
        err("--secret-access-key is required")

    _s3_validate_company_exists(conn, args.company_id)

    # Check for existing config
    s3c = Table("s3_config")
    q = Q.from_(s3c).select(s3c.id).where(s3c.company_id == P())
    existing = conn.execute(q.get_sql(), (args.company_id,)).fetchone()
    if existing:
        err("S3 configuration already exists for this company. "
            "Delete the existing config before reconfiguring.")

    region = args.region or "us-east-1"
    prefix = args.prefix or "erpclaw-backups/"

    # Encrypt sensitive credentials before storing
    from erpclaw_lib.crypto import encrypt_field, derive_key
    from erpclaw_lib.db import DEFAULT_DB_PATH
    _fk = derive_key(os.environ.get("ERPCLAW_DB_PATH", DEFAULT_DB_PATH),
                      b"erpclaw-field-key")
    enc_access_key = encrypt_field(args.access_key_id, _fk)
    enc_secret_key = encrypt_field(args.secret_access_key, _fk)

    config_id = str(uuid.uuid4())
    sql, _ = insert_row("s3_config", {
        "id": P(), "company_id": P(), "bucket_name": P(),
        "region": P(), "access_key_id": P(),
        "secret_access_key": P(), "prefix": P(), "status": P(),
    })
    conn.execute(sql, (config_id, args.company_id, args.bucket_name, region,
         enc_access_key, enc_secret_key, prefix, "active"))

    audit(conn, SKILL_NAME, "configure-s3", "s3_config", config_id,
          new_values={"bucket_name": args.bucket_name, "region": region},
          description=f"Configured S3 backup for bucket '{args.bucket_name}'")
    conn.commit()

    ok({
        "config": {
            "id": config_id,
            "company_id": args.company_id,
            "bucket_name": args.bucket_name,
            "region": region,
            "prefix": prefix,
            "status": "active",
        },
        "message": f"S3 backup configured for bucket '{args.bucket_name}' in {region}",
    })


def upload_backup(conn, args):
    """Mock-upload a database backup to S3.

    Required: --company-id
    Optional: --encrypted (0), --backup-type (full)

    Reads the actual database file to compute real file size and SHA-256
    checksum, then generates a mock S3 key and inserts a completed record.
    """
    if not args.company_id:
        err("--company-id is required")

    _s3_validate_company_exists(conn, args.company_id)

    config = _s3_get_config(conn, args.company_id)
    if not config:
        err("No S3 configuration found for this company. Run 'configure-s3' first.")

    # Resolve the database file path
    db_file = _s3_get_db_path_for_conn(conn)
    if not os.path.exists(db_file):
        err(f"Database file not found: {db_file}")

    # Compute real file metrics
    file_size = _s3_get_file_size(db_file)
    checksum = _s3_compute_file_checksum(db_file)

    # Generate mock S3 key
    s3_key = _s3_generate_s3_key(config["prefix"])

    encrypted = int(args.encrypted or 0)
    backup_type = args.backup_type or "full"
    if backup_type not in ("full", "incremental"):
        err("--backup-type must be 'full' or 'incremental'")

    record_id = str(uuid.uuid4())
    sql, _ = insert_row("s3_backup_record", {
        "id": P(), "company_id": P(), "s3_key": P(),
        "file_size_bytes": P(), "backup_type": P(),
        "encrypted": P(), "checksum": P(), "status": P(),
    })
    conn.execute(sql, (record_id, args.company_id, s3_key, file_size,
         backup_type, encrypted, checksum, "completed"))

    audit(conn, SKILL_NAME, "upload-backup", "s3_backup_record", record_id,
          new_values={"s3_key": s3_key, "file_size_bytes": file_size,
                      "checksum": checksum[:12]},
          description=f"Mock-uploaded backup to {s3_key}")
    conn.commit()

    ok({
        "backup": {
            "id": record_id,
            "company_id": args.company_id,
            "s3_key": s3_key,
            "bucket_name": config["bucket_name"],
            "file_size_bytes": file_size,
            "backup_type": backup_type,
            "encrypted": encrypted,
            "checksum": checksum,
            "status": "completed",
        },
        "message": f"Backup uploaded to s3://{config['bucket_name']}/{s3_key} "
                   f"({file_size:,} bytes, SHA-256: {checksum[:12]}...)",
    })


def list_remote_backups(conn, args):
    """List backup records for a company.

    Required: --company-id
    Optional: --status, --limit (20), --offset (0)
    """
    if not args.company_id:
        err("--company-id is required")

    _s3_validate_company_exists(conn, args.company_id)

    s3b = Table("s3_backup_record")
    params = [args.company_id]

    q_base = Q.from_(s3b).where(s3b.company_id == P())

    if args.status:
        if args.status not in ("uploading", "completed", "failed", "deleted"):
            err("--status must be one of: uploading, completed, failed, deleted")
        q_base = q_base.where(s3b.status == P())
        params.append(args.status)
    else:
        # By default, exclude deleted backups
        q_base = q_base.where(s3b.status != ValueWrapper("deleted"))

    # Count
    q_count = q_base.select(fn.Count("*").as_("cnt"))
    total = conn.execute(q_count.get_sql(), params).fetchone()["cnt"]

    # Paginate
    limit = int(args.limit or 20)
    offset = int(args.offset or 0)
    q_data = (q_base.select(s3b.star)
              .orderby(s3b.created_at, order=Order.desc)
              .limit(P()).offset(P()))
    rows = conn.execute(q_data.get_sql(), params + [limit, offset]).fetchall()
    backups = rows_to_list(rows)

    ok({
        "backups": backups,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total,
    })


def restore_from_s3(conn, args):
    """Mock-restore a database backup from S3.

    Required: --backup-id

    Does not actually download anything.  Marks the record as "restore
    requested" and returns a mock restore command the user would run.
    """
    if not args.backup_id:
        err("--backup-id is required")

    backup = _s3_validate_backup_exists(conn, args.backup_id)

    if backup["status"] == "deleted":
        err("Cannot restore a deleted backup")
    if backup["status"] != "completed":
        err(f"Backup is not in 'completed' status (current: {backup['status']})")

    # Fetch the S3 config for context
    config = _s3_get_config(conn, backup["company_id"])
    bucket_name = config["bucket_name"] if config else "unknown-bucket"

    # Generate a mock restore command
    restore_path = os.path.expanduser("~/.openclaw/erpclaw/data.sqlite")
    restore_cmd = (
        f"aws s3 cp s3://{bucket_name}/{backup['s3_key']} {restore_path} "
        f"&& echo 'Restore complete. Verify with: sqlite3 {restore_path} "
        f"\".tables\"'"
    )

    audit(conn, SKILL_NAME, "restore-from-s3", "s3_backup_record",
          args.backup_id,
          description=f"Restore requested for {backup['s3_key']}")
    conn.commit()

    ok({
        "backup_id": args.backup_id,
        "s3_key": backup["s3_key"],
        "bucket_name": bucket_name,
        "file_size_bytes": backup["file_size_bytes"],
        "checksum": backup["checksum"],
        "restore_command": restore_cmd,
        "message": (
            f"Restore prepared for s3://{bucket_name}/{backup['s3_key']}. "
            f"Run the restore_command to replace the current database. "
            f"Verify checksum: {backup['checksum'][:12]}..."
        ),
    })


def delete_remote_backup(conn, args):
    """Soft-delete a remote backup record.

    Required: --backup-id

    Sets the record status to 'deleted'.  It will no longer appear in
    default list-remote-backups results.
    """
    if not args.backup_id:
        err("--backup-id is required")

    backup = _s3_validate_backup_exists(conn, args.backup_id)

    if backup["status"] == "deleted":
        err("Backup is already deleted")

    old_status = backup["status"]
    s3b = Table("s3_backup_record")
    q = (Q.update(s3b)
         .set(s3b.status, ValueWrapper("deleted"))
         .where(s3b.id == P()))
    conn.execute(q.get_sql(), (args.backup_id,))

    audit(conn, SKILL_NAME, "delete-remote-backup", "s3_backup_record",
          args.backup_id,
          old_values={"status": old_status},
          new_values={"status": "deleted"},
          description=f"Soft-deleted backup {backup['s3_key']}")
    conn.commit()

    ok({
        "backup_id": args.backup_id,
        "s3_key": backup["s3_key"],
        "old_status": old_status,
        "new_status": "deleted",
        "message": f"Backup {backup['s3_key']} marked as deleted",
    })


def s3_status(conn, args):
    """Return S3 backup status summary."""
    s3c = Table("s3_config")
    q = (Q.from_(s3c).select(fn.Count("*").as_("cnt"))
         .where(s3c.status == ValueWrapper("active")))
    config_count = conn.execute(q.get_sql()).fetchone()["cnt"]

    s3b = Table("s3_backup_record")
    q = (Q.from_(s3b)
         .select(s3b.status, fn.Count("*").as_("cnt"))
         .groupby(s3b.status))
    backup_rows = conn.execute(q.get_sql()).fetchall()
    backups_by_status = {r["status"]: r["cnt"] for r in backup_rows}
    total_backups = sum(backups_by_status.values())

    # Total size of completed backups
    q = (Q.from_(s3b)
         .select(fn.Coalesce(fn.Sum(s3b.file_size_bytes), 0).as_("total_bytes"))
         .where(s3b.status == ValueWrapper("completed")))
    size_row = conn.execute(q.get_sql()).fetchone()
    total_size_bytes = size_row["total_bytes"]

    return {
        "configured_companies": config_count,
        "total_backups": total_backups,
        "backups_by_status": backups_by_status,
        "total_size_bytes": total_size_bytes,
    }


# ===========================================================================
#
#  UNIFIED STATUS -- all 3 integrations
#
# ===========================================================================

def status(conn, args):
    """Unified status for all 3 integrations: Plaid, Stripe, S3."""
    result = {}

    # Plaid status
    try:
        result["plaid"] = plaid_status(conn, args)
    except SystemExit:
        raise
    except Exception:
        result["plaid"] = {"error": "Could not fetch Plaid status"}

    # Stripe status
    try:
        result["stripe"] = stripe_status(conn, args)
    except SystemExit:
        raise
    except Exception:
        result["stripe"] = {"error": "Could not fetch Stripe status"}

    # S3 status
    try:
        result["s3"] = s3_status(conn, args)
    except SystemExit:
        raise
    except Exception:
        result["s3"] = {"error": "Could not fetch S3 status"}

    ok(result)


# ===========================================================================
# Action dispatch
# ===========================================================================

ACTIONS = {
    # Plaid (5 actions)
    "configure-plaid": configure_plaid,
    "link-account": link_account,
    "sync-transactions": sync_transactions,
    "match-transactions": match_transactions,
    "list-transactions": list_transactions,
    # Stripe (5 actions)
    "configure-stripe": configure_stripe,
    "create-payment-intent": create_payment_intent,
    "sync-payments": sync_payments,
    "handle-webhook": handle_webhook,
    "list-stripe-payments": list_stripe_payments,
    # S3 (5 actions)
    "configure-s3": configure_s3,
    "upload-backup": upload_backup,
    "list-remote-backups": list_remote_backups,
    "restore-from-s3": restore_from_s3,
    "delete-remote-backup": delete_remote_backup,
    # Unified
    "status": status,
}


def main():
    parser = argparse.ArgumentParser(description="ERPClaw Integrations (Plaid + Stripe + S3)")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # -- Shared entity IDs ------------------------------------------------
    parser.add_argument("--company-id")
    parser.add_argument("--invoice-id")
    parser.add_argument("--backup-id")

    # -- Plaid configure --------------------------------------------------
    parser.add_argument("--client-id")
    parser.add_argument("--secret")
    parser.add_argument("--environment", default="sandbox")

    # -- Plaid link-account -----------------------------------------------
    parser.add_argument("--institution-name")
    parser.add_argument("--account-name")
    parser.add_argument("--account-type")
    parser.add_argument("--account-mask")
    parser.add_argument("--erp-account-id")

    # -- Plaid transactions -----------------------------------------------
    parser.add_argument("--linked-account-id")
    parser.add_argument("--from-date")
    parser.add_argument("--to-date")
    parser.add_argument("--match-status")

    # -- Stripe configure -------------------------------------------------
    parser.add_argument("--publishable-key")
    parser.add_argument("--secret-key")
    parser.add_argument("--webhook-secret")
    parser.add_argument("--mode")

    # -- Stripe payment intent --------------------------------------------
    parser.add_argument("--amount")
    parser.add_argument("--currency")
    parser.add_argument("--metadata")

    # -- Stripe webhook ---------------------------------------------------
    parser.add_argument("--event-id")
    parser.add_argument("--event-type")
    parser.add_argument("--payload")

    # -- S3 configure -----------------------------------------------------
    parser.add_argument("--bucket-name")
    parser.add_argument("--region")
    parser.add_argument("--access-key-id")
    parser.add_argument("--secret-access-key")
    parser.add_argument("--prefix")

    # -- S3 upload --------------------------------------------------------
    parser.add_argument("--encrypted", default="0")
    parser.add_argument("--backup-type", default="full")

    # -- Shared filters ---------------------------------------------------
    parser.add_argument("--status")
    parser.add_argument("--limit", default="20")
    parser.add_argument("--offset", default="0")

    args, _unknown = parser.parse_known_args()
    check_input_lengths(args)
    action_fn = ACTIONS[args.action]

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
        action_fn(conn, args)
    except SystemExit:
        raise
    except Exception as e:
        conn.rollback()
        sys.stderr.write(f"[{SKILL_NAME}] {e}\n")
        err("An unexpected error occurred")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
