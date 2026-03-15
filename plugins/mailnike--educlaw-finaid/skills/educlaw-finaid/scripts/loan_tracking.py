"""EduClaw Financial Aid — loan_tracking domain module

Actions for the loan_tracking domain.
Imported by db_query.py (unified router).
"""
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

_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
_today = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d")

# ---------------------------------------------------------------------------
# Loan-type aid_type values considered valid for loan origination
# ---------------------------------------------------------------------------
LOAN_AID_TYPES = (
    "subsidized_loan",
    "unsubsidized_loan",
    "plus_loan",
    "parent_plus_loan",
    "teach_grant",
)

# ---------------------------------------------------------------------------
# Annual loan limits (upper-division = year 3+)
# ---------------------------------------------------------------------------
ANNUAL_LIMITS = {
    "dependent": {
        1: {"sub": Decimal("3500"), "combined": Decimal("5500")},
        2: {"sub": Decimal("4500"), "combined": Decimal("6500")},
        3: {"sub": Decimal("5500"), "combined": Decimal("7500")},
    },
    "independent": {
        1: {"sub": Decimal("3500"), "combined": Decimal("9500")},
        2: {"sub": Decimal("4500"), "combined": Decimal("10500")},
        3: {"sub": Decimal("5500"), "combined": Decimal("12500")},
    },
}

# ---------------------------------------------------------------------------
# Aggregate loan limits
# ---------------------------------------------------------------------------
AGGREGATE_LIMITS = {
    "dependent": {"sub": Decimal("23000"), "combined": Decimal("31000")},
    "independent": {"sub": Decimal("65500"), "combined": Decimal("57500")},
}


# ---------------------------------------------------------------------------
# Helper: load / save disbursement_holds JSON on finaid_award
# ---------------------------------------------------------------------------
def _load_holds(conn, award_id):
    row = conn.execute(
        "SELECT disbursement_holds FROM finaid_award WHERE id=?", (award_id,)
    ).fetchone()
    if not row:
        return []
    try:
        return json.loads(row[0]) if row[0] else []
    except (ValueError, TypeError):
        return []


def _save_holds(conn, award_id, holds):
    conn.execute(
        "UPDATE finaid_award SET disbursement_holds=?, updated_at=? WHERE id=?",
        (json.dumps(holds), _now_iso(), award_id),
    )


# ---------------------------------------------------------------------------
# 1. add-loan
# ---------------------------------------------------------------------------
def add_loan(conn, args):
    try:
        required = ["student_id", "award_id", "aid_year_id", "loan_type",
                    "loan_period_start", "loan_period_end", "loan_amount",
                    "company_id", "borrower_id"]
        for field in required:
            if not getattr(args, field, None):
                return err(f"Missing required field: {field}")

        # Validate award exists and has a loan aid_type
        award_row = conn.execute(
            "SELECT id, aid_type FROM finaid_award WHERE id=? AND company_id=?",
            (args.award_id, args.company_id),
        ).fetchone()
        if not award_row:
            return err(f"Award not found: {args.award_id}")
        if award_row[1] not in LOAN_AID_TYPES:
            return err(
                f"Award aid_type '{award_row[1]}' is not a loan type. "
                f"Must be one of: {', '.join(LOAN_AID_TYPES)}"
            )

        loan_id = str(uuid.uuid4())
        now = _now_iso()

        loan_amount = str(round_currency(to_decimal(getattr(args, "loan_amount", None) or "0")))
        first_disb = str(round_currency(to_decimal(getattr(args, "first_disbursement_amount", None) or "0")))
        second_disb = str(round_currency(to_decimal(getattr(args, "second_disbursement_amount", None) or "0")))
        orig_fee = str(round_currency(to_decimal(getattr(args, "origination_fee", None) or "0")))
        interest_rate = str(round_currency(to_decimal(getattr(args, "interest_rate", None) or "0")))
        cod_loan_id = getattr(args, "cod_loan_id", None) or ""
        borrower_type = getattr(args, "borrower_type", None) or "student"
        ec_required = int(getattr(args, "entrance_counseling_required", 0) or 0)
        created_by = getattr(args, "created_by", None) or ""

        # All federal loans require MPN
        mpn_required = 1

        conn.execute(
            """INSERT INTO finaid_loan (
                id, student_id, award_id, aid_year_id, loan_type,
                loan_period_start, loan_period_end,
                loan_amount, first_disbursement_amount, second_disbursement_amount,
                origination_fee, interest_rate,
                cod_loan_id, cod_origination_status, cod_origination_date,
                mpn_required, mpn_signed, mpn_signed_date,
                entrance_counseling_required, entrance_counseling_complete, entrance_counseling_date,
                exit_counseling_required, exit_counseling_complete, exit_counseling_date,
                borrower_id, borrower_type, status,
                company_id, created_at, updated_at, created_by
            ) VALUES (
                ?,?,?,?,?,  ?,?,  ?,?,?,  ?,?,  ?,?,?,
                ?,?,?,  ?,?,?,  ?,?,?,  ?,?,?,  ?,?,?,?
            )""",
            (
                loan_id,
                args.student_id,
                args.award_id,
                args.aid_year_id,
                args.loan_type,
                args.loan_period_start,
                args.loan_period_end,
                loan_amount,
                first_disb,
                second_disb,
                orig_fee,
                interest_rate,
                cod_loan_id,
                "",              # cod_origination_status
                "",              # cod_origination_date
                mpn_required,
                0,               # mpn_signed
                "",              # mpn_signed_date
                ec_required,
                0,               # entrance_counseling_complete
                "",              # entrance_counseling_date
                0,               # exit_counseling_required
                0,               # exit_counseling_complete
                "",              # exit_counseling_date
                args.borrower_id,
                borrower_type,
                "originated",
                args.company_id,
                now,
                now,
                created_by,
            ),
        )

        # Add disbursement holds to finaid_award
        holds = _load_holds(conn, args.award_id)
        if mpn_required and "mpn_pending" not in holds:
            holds.append("mpn_pending")
        if ec_required and "ec_pending" not in holds:
            holds.append("ec_pending")
        _save_holds(conn, args.award_id, holds)

        conn.commit()
        return ok({"id": loan_id, "status": "originated"})

    except sqlite3.IntegrityError:
        conn.rollback()
        return err("Duplicate loan record")
    except Exception as e:
        conn.rollback()
        return err(str(e))


# ---------------------------------------------------------------------------
# 2. update-loan
# ---------------------------------------------------------------------------
def update_loan(conn, args):
    try:
        loan_id = getattr(args, "id", None)
        if not loan_id:
            return err("Missing required field: id")

        row = conn.execute("SELECT id FROM finaid_loan WHERE id=?", (loan_id,)).fetchone()
        if not row:
            return err(f"Loan not found: {loan_id}")

        updatable = [
            ("loan_period_start", str),
            ("loan_period_end", str),
            ("first_disbursement_amount", lambda v: str(round_currency(to_decimal(v)))),
            ("second_disbursement_amount", lambda v: str(round_currency(to_decimal(v)))),
            ("origination_fee", lambda v: str(round_currency(to_decimal(v)))),
            ("interest_rate", lambda v: str(round_currency(to_decimal(v)))),
            ("cod_loan_id", str),
            ("loan_amount", lambda v: str(round_currency(to_decimal(v)))),
        ]

        fields = []
        values = []
        for field, coerce in updatable:
            val = getattr(args, field, None)
            if val is not None:
                fields.append(f"{field}=?")
                values.append(coerce(val))

        if not fields:
            return err("No updatable fields provided")

        fields.append("updated_at=?")
        values.append(_now_iso())
        values.append(loan_id)

        conn.execute(
            f"UPDATE finaid_loan SET {', '.join(fields)} WHERE id=?", values
        )
        conn.commit()
        return ok({"id": loan_id, "updated": True})

    except Exception as e:
        conn.rollback()
        return err(str(e))


# ---------------------------------------------------------------------------
# 3. get-loan
# ---------------------------------------------------------------------------
def get_loan(conn, args):
    try:
        loan_id = getattr(args, "id", None)
        if not loan_id:
            return err("Missing required field: id")

        row = conn.execute(
            "SELECT * FROM finaid_loan WHERE id=?", (loan_id,)
        ).fetchone()
        if not row:
            return err(f"Loan not found: {loan_id}")

        return ok(row_to_dict(row))

    except Exception as e:
        return err(str(e))


# ---------------------------------------------------------------------------
# 4. list-loans
# ---------------------------------------------------------------------------
def list_loans(conn, args):
    try:
        company_id = getattr(args, "company_id", None)
        if not company_id:
            return err("Missing required field: company_id")

        clauses = ["company_id=?"]
        params = [company_id]

        student_id = getattr(args, "student_id", None)
        if student_id:
            clauses.append("student_id=?")
            params.append(student_id)

        aid_year_id = getattr(args, "aid_year_id", None)
        if aid_year_id:
            clauses.append("aid_year_id=?")
            params.append(aid_year_id)

        loan_type = getattr(args, "loan_type", None)
        if loan_type:
            clauses.append("loan_type=?")
            params.append(loan_type)

        status = getattr(args, "status", None)
        if status:
            clauses.append("status=?")
            params.append(status)

        cod_origination_status = getattr(args, "cod_origination_status", None)
        if cod_origination_status:
            clauses.append("cod_origination_status=?")
            params.append(cod_origination_status)

        limit = getattr(args, "limit", 50) or 50
        offset = getattr(args, "offset", 0) or 0

        where = " AND ".join(clauses)
        rows = conn.execute(
            f"SELECT * FROM finaid_loan WHERE {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            params + [limit, offset],
        ).fetchall()

        return ok({"loans": [row_to_dict(r) for r in rows], "count": len(rows)})

    except Exception as e:
        return err(str(e))


# ---------------------------------------------------------------------------
# 5. update-mpn-status
# ---------------------------------------------------------------------------
def update_mpn_status(conn, args):
    try:
        loan_id = getattr(args, "id", None)
        mpn_signed_date = getattr(args, "mpn_signed_date", None)
        if not loan_id:
            return err("Missing required field: id")
        if not mpn_signed_date:
            return err("Missing required field: mpn_signed_date")

        row = conn.execute(
            "SELECT id, award_id FROM finaid_loan WHERE id=?", (loan_id,)
        ).fetchone()
        if not row:
            return err(f"Loan not found: {loan_id}")

        award_id = row[1]
        now = _now_iso()

        conn.execute(
            "UPDATE finaid_loan SET mpn_signed=1, mpn_signed_date=?, updated_at=? WHERE id=?",
            (mpn_signed_date, now, loan_id),
        )

        # Remove 'mpn_pending' from finaid_award.disbursement_holds
        holds = _load_holds(conn, award_id)
        holds = [h for h in holds if h != "mpn_pending"]
        _save_holds(conn, award_id, holds)

        conn.commit()
        return ok({"id": loan_id, "mpn_signed": True, "mpn_signed_date": mpn_signed_date})

    except Exception as e:
        conn.rollback()
        return err(str(e))


# ---------------------------------------------------------------------------
# 6. update-entrance-counseling
# ---------------------------------------------------------------------------
def update_entrance_counseling(conn, args):
    try:
        loan_id = getattr(args, "id", None)
        ec_date = getattr(args, "entrance_counseling_date", None)
        if not loan_id:
            return err("Missing required field: id")
        if not ec_date:
            return err("Missing required field: entrance_counseling_date")

        row = conn.execute(
            "SELECT id, award_id FROM finaid_loan WHERE id=?", (loan_id,)
        ).fetchone()
        if not row:
            return err(f"Loan not found: {loan_id}")

        award_id = row[1]
        now = _now_iso()

        conn.execute(
            """UPDATE finaid_loan
               SET entrance_counseling_complete=1, entrance_counseling_date=?, updated_at=?
               WHERE id=?""",
            (ec_date, now, loan_id),
        )

        # Remove 'ec_pending' from finaid_award.disbursement_holds
        holds = _load_holds(conn, award_id)
        holds = [h for h in holds if h != "ec_pending"]
        _save_holds(conn, award_id, holds)

        conn.commit()
        return ok({
            "id": loan_id,
            "entrance_counseling_complete": True,
            "entrance_counseling_date": ec_date,
        })

    except Exception as e:
        conn.rollback()
        return err(str(e))


# ---------------------------------------------------------------------------
# 7. update-exit-counseling
# ---------------------------------------------------------------------------
def update_exit_counseling(conn, args):
    try:
        loan_id = getattr(args, "id", None)
        exit_date = getattr(args, "exit_counseling_date", None)
        if not loan_id:
            return err("Missing required field: id")
        if not exit_date:
            return err("Missing required field: exit_counseling_date")

        row = conn.execute(
            "SELECT id FROM finaid_loan WHERE id=?", (loan_id,)
        ).fetchone()
        if not row:
            return err(f"Loan not found: {loan_id}")

        conn.execute(
            """UPDATE finaid_loan
               SET exit_counseling_complete=1, exit_counseling_date=?, updated_at=?
               WHERE id=?""",
            (exit_date, _now_iso(), loan_id),
        )
        conn.commit()
        return ok({
            "id": loan_id,
            "exit_counseling_complete": True,
            "exit_counseling_date": exit_date,
        })

    except Exception as e:
        conn.rollback()
        return err(str(e))


# ---------------------------------------------------------------------------
# 8. generate-cod-origination
# ---------------------------------------------------------------------------
def generate_cod_origination(conn, args):
    try:
        loan_id = getattr(args, "id", None)
        if not loan_id:
            return err("Missing required field: id")

        loan_row = conn.execute(
            "SELECT * FROM finaid_loan WHERE id=?", (loan_id,)
        ).fetchone()
        if not loan_row:
            return err(f"Loan not found: {loan_id}")

        loan = row_to_dict(loan_row)

        # Fetch award info
        award_row = conn.execute(
            "SELECT id, offered_amount, aid_type, aid_source, student_id, "
            "aid_year_id, award_package_id FROM finaid_award WHERE id=?",
            (loan["award_id"],),
        ).fetchone()

        award = row_to_dict(award_row) if award_row else {}

        cod_payload = {
            # Loan identifiers
            "loan_id": loan["id"],
            "cod_loan_id": loan.get("cod_loan_id", ""),
            "student_id": loan["student_id"],
            "aid_year_id": loan["aid_year_id"],
            "loan_type": loan["loan_type"],
            # Borrower info
            "borrower_id": loan.get("borrower_id", ""),
            "borrower_type": loan.get("borrower_type", "student"),
            # Loan period
            "loan_period_start": loan.get("loan_period_start", ""),
            "loan_period_end": loan.get("loan_period_end", ""),
            # Amounts
            "loan_amount": loan.get("loan_amount", "0"),
            "first_disbursement_amount": loan.get("first_disbursement_amount", "0"),
            "second_disbursement_amount": loan.get("second_disbursement_amount", "0"),
            "origination_fee": loan.get("origination_fee", "0"),
            "interest_rate": loan.get("interest_rate", "0"),
            # Award info
            "award_id": loan.get("award_id", ""),
            "offered_amount": award.get("offered_amount", "0"),
            "aid_type": award.get("aid_type", ""),
            "aid_source": award.get("aid_source", ""),
            "award_package_id": award.get("award_package_id", ""),
            # MPN / counseling status
            "mpn_required": loan.get("mpn_required", 1),
            "mpn_signed": loan.get("mpn_signed", 0),
            "mpn_signed_date": loan.get("mpn_signed_date", ""),
            "entrance_counseling_required": loan.get("entrance_counseling_required", 0),
            "entrance_counseling_complete": loan.get("entrance_counseling_complete", 0),
            "entrance_counseling_date": loan.get("entrance_counseling_date", ""),
            # COD origination
            "cod_origination_status": loan.get("cod_origination_status", ""),
            "cod_origination_date": loan.get("cod_origination_date", ""),
            # Meta
            "loan_status": loan.get("status", ""),
            "company_id": loan.get("company_id", ""),
            "generated_at": _now_iso(),
        }

        return ok(cod_payload)

    except Exception as e:
        return err(str(e))


# ---------------------------------------------------------------------------
# 9. update-cod-origination-status
# ---------------------------------------------------------------------------
def update_cod_origination_status(conn, args):
    try:
        loan_id = getattr(args, "id", None)
        cod_status = getattr(args, "cod_origination_status", None)
        if not loan_id:
            return err("Missing required field: id")
        if not cod_status:
            return err("Missing required field: cod_origination_status")

        valid_statuses = ("pending", "accepted", "rejected", "")
        if cod_status not in valid_statuses:
            return err(
                f"Invalid cod_origination_status '{cod_status}'. "
                f"Must be one of: {', '.join(repr(s) for s in valid_statuses)}"
            )

        row = conn.execute(
            "SELECT id FROM finaid_loan WHERE id=?", (loan_id,)
        ).fetchone()
        if not row:
            return err(f"Loan not found: {loan_id}")

        cod_date = getattr(args, "cod_origination_date", None) or _today()
        now = _now_iso()

        # If accepted, also flip loan.status to 'active'
        if cod_status == "accepted":
            conn.execute(
                """UPDATE finaid_loan
                   SET cod_origination_status=?, cod_origination_date=?,
                       status='active', updated_at=?
                   WHERE id=?""",
                (cod_status, cod_date, now, loan_id),
            )
        else:
            conn.execute(
                """UPDATE finaid_loan
                   SET cod_origination_status=?, cod_origination_date=?, updated_at=?
                   WHERE id=?""",
                (cod_status, cod_date, now, loan_id),
            )

        conn.commit()
        return ok({
            "id": loan_id,
            "cod_origination_status": cod_status,
            "cod_origination_date": cod_date,
            "loan_status": "active" if cod_status == "accepted" else None,
        })

    except Exception as e:
        conn.rollback()
        return err(str(e))


# ---------------------------------------------------------------------------
# 10. get-loan-limits-status
# ---------------------------------------------------------------------------
def get_loan_limits_status(conn, args):
    try:
        student_id = getattr(args, "student_id", None)
        aid_year_id = getattr(args, "aid_year_id", None)
        company_id = getattr(args, "company_id", None)
        if not student_id:
            return err("Missing required field: student_id")
        if not aid_year_id:
            return err("Missing required field: aid_year_id")
        if not company_id:
            return err("Missing required field: company_id")

        # All loans for this student in this aid year (current year)
        year_rows = conn.execute(
            "SELECT * FROM finaid_loan WHERE student_id=? AND aid_year_id=? AND company_id=?",
            (student_id, aid_year_id, company_id),
        ).fetchall()

        current_year_total = Decimal("0")
        current_year_subsidized = Decimal("0")
        for r in year_rows:
            d = row_to_dict(r)
            amt = to_decimal(d.get("loan_amount", "0"))
            current_year_total += amt
            if d.get("loan_type") == "subsidized":
                current_year_subsidized += amt

        # Aggregate across ALL aid years for this student
        all_rows = conn.execute(
            "SELECT * FROM finaid_loan WHERE student_id=? AND company_id=?",
            (student_id, company_id),
        ).fetchall()

        aggregate_total = Decimal("0")
        aggregate_subsidized = Decimal("0")
        for r in all_rows:
            d = row_to_dict(r)
            amt = to_decimal(d.get("loan_amount", "0"))
            aggregate_total += amt
            if d.get("loan_type") == "subsidized":
                aggregate_subsidized += amt

        return ok({
            "student_id": student_id,
            "aid_year_id": aid_year_id,
            "current_year_total": str(round_currency(current_year_total)),
            "current_year_subsidized": str(round_currency(current_year_subsidized)),
            "aggregate_total": str(round_currency(aggregate_total)),
            "aggregate_subsidized": str(round_currency(aggregate_subsidized)),
            # Annual limits (upper-division / year 3+)
            "annual_limit_dependent": "7500.00",
            "annual_limit_independent": "12500.00",
            # Aggregate limits
            "aggregate_limit_dependent": "31000.00",
            "aggregate_limit_independent": "57500.00",
            "loans": [row_to_dict(r) for r in year_rows],
        })

    except Exception as e:
        return err(str(e))


# ---------------------------------------------------------------------------
# ACTIONS registry
# ---------------------------------------------------------------------------
ACTIONS = {
    "add-loan": add_loan,
    "update-loan": update_loan,
    "get-loan": get_loan,
    "list-loans": list_loans,
    "update-mpn-status": update_mpn_status,
    "update-entrance-counseling": update_entrance_counseling,
    "update-exit-counseling": update_exit_counseling,
    "generate-cod-origination": generate_cod_origination,
    "update-cod-origination-status": update_cod_origination_status,
    "get-loan-limits-status": get_loan_limits_status,
}
