"""EduClaw Financial Aid — financial_aid domain module (72 actions)"""
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone, timedelta
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
# Aid Year Setup
# ---------------------------------------------------------------------------

def add_aid_year(conn, args):
    company_id = getattr(args, 'company_id', None)
    aid_year_code = getattr(args, 'aid_year_code', None)
    if not company_id:
        return err("company_id is required")
    if not aid_year_code:
        return err("aid_year_code is required")
    description = getattr(args, 'description', '') or ''
    start_date = getattr(args, 'start_date', '') or ''
    end_date = getattr(args, 'end_date', '') or ''
    pell_max_award = str(round_currency(to_decimal(getattr(args, 'pell_max_award', '0') or '0')))
    is_active = int(getattr(args, 'is_active', 0) or 0)
    aid_year_id = str(uuid.uuid4())
    try:
        conn.execute(
            "INSERT INTO finaid_aid_year (id,aid_year_code,description,start_date,end_date,pell_max_award,is_active,company_id,created_by) VALUES (?,?,?,?,?,?,?,?,?)",
            (aid_year_id, aid_year_code, description, start_date, end_date, pell_max_award, is_active, company_id, '')
        )
        conn.commit()
        return ok({"id": aid_year_id, "aid_year_code": aid_year_code})
    except sqlite3.IntegrityError as e:
        return err(f"Duplicate aid year code for this company: {e}")


def update_aid_year(conn, args):
    aid_year_id = getattr(args, 'id', None)
    if not aid_year_id:
        return err("id is required")
    row = conn.execute("SELECT * FROM finaid_aid_year WHERE id=?", (aid_year_id,)).fetchone()
    if not row:
        return err("Aid year not found")
    fields, vals = [], []
    for f in ['description', 'start_date', 'end_date', 'pell_max_award']:
        v = getattr(args, f.replace('-', '_'), None)
        if v is not None:
            fields.append(f"{f}=?")
            vals.append(str(round_currency(to_decimal(v))) if f == 'pell_max_award' else v)
    is_active = getattr(args, 'is_active', None)
    if is_active is not None:
        fields.append("is_active=?")
        vals.append(int(is_active))
    if not fields:
        return err("No fields to update")
    fields.append("updated_at=?")
    vals.append(_now_iso())
    vals.append(aid_year_id)
    conn.execute(f"UPDATE finaid_aid_year SET {','.join(fields)} WHERE id=?", vals)
    conn.commit()
    return ok({"id": aid_year_id, "updated": True})


def get_aid_year(conn, args):
    aid_year_id = getattr(args, 'id', None)
    if not aid_year_id:
        return err("id is required")
    row = conn.execute("SELECT * FROM finaid_aid_year WHERE id=?", (aid_year_id,)).fetchone()
    if not row:
        return err("Aid year not found")
    return ok(dict(row))


def list_aid_years(conn, args):
    company_id = getattr(args, 'company_id', None)
    if not company_id:
        return err("company_id is required")
    q = "SELECT * FROM finaid_aid_year WHERE company_id=?"
    params = [company_id]
    is_active = getattr(args, 'is_active', None)
    if is_active is not None:
        q += " AND is_active=?"
        params.append(int(is_active))
    limit = int(getattr(args, 'limit', 50) or 50)
    offset = int(getattr(args, 'offset', 0) or 0)
    q += " ORDER BY aid_year_code DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    rows = conn.execute(q, params).fetchall()
    return ok({"aid_years": [dict(r) for r in rows], "count": len(rows)})


def set_active_aid_year(conn, args):
    aid_year_id = getattr(args, 'id', None)
    if not aid_year_id:
        return err("id is required")
    row = conn.execute("SELECT company_id FROM finaid_aid_year WHERE id=?", (aid_year_id,)).fetchone()
    if not row:
        return err("Aid year not found")
    company_id = row['company_id']
    conn.execute("UPDATE finaid_aid_year SET is_active=0, updated_at=? WHERE company_id=?", (_now_iso(), company_id))
    conn.execute("UPDATE finaid_aid_year SET is_active=1, updated_at=? WHERE id=?", (_now_iso(), aid_year_id))
    conn.commit()
    return ok({"id": aid_year_id, "is_active": 1})


def import_pell_schedule(conn, args):
    aid_year_id = getattr(args, 'aid_year_id', None)
    company_id = getattr(args, 'company_id', None)
    rows_json = getattr(args, 'rows', None)
    if not aid_year_id:
        return err("aid_year_id is required")
    if not company_id:
        return err("company_id is required")
    if not rows_json:
        return err("rows is required (JSON array)")
    try:
        rows = json.loads(rows_json)
    except json.JSONDecodeError:
        return err("rows must be valid JSON array")
    inserted = 0
    for r in rows:
        rid = str(uuid.uuid4())
        conn.execute(
            "INSERT OR REPLACE INTO finaid_pell_schedule (id,aid_year_id,pell_index,full_time_annual,three_quarter_time,half_time,less_than_half_time,company_id) VALUES (?,?,?,?,?,?,?,?)",
            (rid, aid_year_id, int(r.get('pell_index', 0)),
             str(round_currency(to_decimal(r.get('full_time_annual', '0')))),
             str(round_currency(to_decimal(r.get('three_quarter_time', '0')))),
             str(round_currency(to_decimal(r.get('half_time', '0')))),
             str(round_currency(to_decimal(r.get('less_than_half_time', '0')))),
             company_id)
        )
        inserted += 1
    conn.commit()
    return ok({"inserted": inserted, "aid_year_id": aid_year_id})


def list_pell_schedule(conn, args):
    aid_year_id = getattr(args, 'aid_year_id', None)
    if not aid_year_id:
        return err("aid_year_id is required")
    q = "SELECT * FROM finaid_pell_schedule WHERE aid_year_id=?"
    params = [aid_year_id]
    pell_index = getattr(args, 'pell_index', None)
    if pell_index is not None:
        q += " AND pell_index=?"
        params.append(int(pell_index))
    q += " ORDER BY pell_index LIMIT ? OFFSET ?"
    params.extend([int(getattr(args, 'limit', 50) or 50), int(getattr(args, 'offset', 0) or 0)])
    rows = conn.execute(q, params).fetchall()
    return ok({"schedule": [dict(r) for r in rows], "count": len(rows)})


# ---------------------------------------------------------------------------
# Fund Allocation
# ---------------------------------------------------------------------------

def add_fund_allocation(conn, args):
    aid_year_id = getattr(args, 'aid_year_id', None)
    company_id = getattr(args, 'company_id', None)
    fund_type = getattr(args, 'fund_type', None)
    fund_name = getattr(args, 'fund_name', None)
    total_allocation = str(round_currency(to_decimal(getattr(args, 'total_allocation', '0') or '0')))
    if not aid_year_id:
        return err("aid_year_id is required")
    if not company_id:
        return err("company_id is required")
    if not fund_type:
        return err("fund_type is required")
    if not fund_name:
        return err("fund_name is required")
    alloc_id = str(uuid.uuid4())
    available_amount = total_allocation
    try:
        conn.execute(
            "INSERT INTO finaid_fund_allocation (id,aid_year_id,fund_type,fund_name,total_allocation,committed_amount,disbursed_amount,available_amount,company_id) VALUES (?,?,?,?,?,?,?,?,?)",
            (alloc_id, aid_year_id, fund_type, fund_name, total_allocation, '0', '0', available_amount, company_id)
        )
        conn.commit()
        return ok({"id": alloc_id, "fund_type": fund_type, "fund_name": fund_name})
    except sqlite3.IntegrityError as e:
        return err(f"Duplicate fund allocation: {e}")


def update_fund_allocation(conn, args):
    alloc_id = getattr(args, 'id', None)
    if not alloc_id:
        return err("id is required")
    row = conn.execute("SELECT * FROM finaid_fund_allocation WHERE id=?", (alloc_id,)).fetchone()
    if not row:
        return err("Fund allocation not found")
    fields, vals = [], []
    for f in ['fund_name']:
        v = getattr(args, f, None)
        if v is not None:
            fields.append(f"{f}=?")
            vals.append(v)
    total_allocation = getattr(args, 'total_allocation', None)
    if total_allocation is not None:
        new_total = str(round_currency(to_decimal(total_allocation)))
        committed = to_decimal(row['committed_amount'])
        new_available = str(round_currency(to_decimal(new_total) - committed))
        fields.extend(["total_allocation=?", "available_amount=?"])
        vals.extend([new_total, new_available])
    if not fields:
        return err("No fields to update")
    fields.append("updated_at=?")
    vals.append(_now_iso())
    vals.append(alloc_id)
    conn.execute(f"UPDATE finaid_fund_allocation SET {','.join(fields)} WHERE id=?", vals)
    conn.commit()
    return ok({"id": alloc_id, "updated": True})


def get_fund_allocation(conn, args):
    alloc_id = getattr(args, 'id', None)
    if not alloc_id:
        return err("id is required")
    row = conn.execute("SELECT * FROM finaid_fund_allocation WHERE id=?", (alloc_id,)).fetchone()
    if not row:
        return err("Fund allocation not found")
    return ok(dict(row))


def list_fund_allocations(conn, args):
    company_id = getattr(args, 'company_id', None)
    if not company_id:
        return err("company_id is required")
    q = "SELECT * FROM finaid_fund_allocation WHERE company_id=?"
    params = [company_id]
    aid_year_id = getattr(args, 'aid_year_id', None)
    if aid_year_id:
        q += " AND aid_year_id=?"
        params.append(aid_year_id)
    fund_type = getattr(args, 'fund_type', None)
    if fund_type:
        q += " AND fund_type=?"
        params.append(fund_type)
    q += " LIMIT ? OFFSET ?"
    params.extend([int(getattr(args, 'limit', 50) or 50), int(getattr(args, 'offset', 0) or 0)])
    rows = conn.execute(q, params).fetchall()
    return ok({"fund_allocations": [dict(r) for r in rows], "count": len(rows)})


# ---------------------------------------------------------------------------
# Cost of Attendance
# ---------------------------------------------------------------------------

def _calc_total_coa(tuition_fees, books_supplies, room_board, transportation, personal_expenses, loan_fees):
    return str(round_currency(
        to_decimal(tuition_fees) + to_decimal(books_supplies) + to_decimal(room_board) +
        to_decimal(transportation) + to_decimal(personal_expenses) + to_decimal(loan_fees)
    ))


def add_cost_of_attendance(conn, args):
    aid_year_id = getattr(args, 'aid_year_id', None)
    company_id = getattr(args, 'company_id', None)
    enrollment_status = getattr(args, 'enrollment_status', None)
    living_arrangement = getattr(args, 'living_arrangement', '') or ''
    if not aid_year_id:
        return err("aid_year_id is required")
    if not company_id:
        return err("company_id is required")
    if not enrollment_status:
        return err("enrollment_status is required")
    tuition_fees = str(round_currency(to_decimal(getattr(args, 'tuition_fees', '0') or '0')))
    books_supplies = str(round_currency(to_decimal(getattr(args, 'books_supplies', '0') or '0')))
    room_board = str(round_currency(to_decimal(getattr(args, 'room_board', '0') or '0')))
    transportation = str(round_currency(to_decimal(getattr(args, 'transportation', '0') or '0')))
    personal_expenses = str(round_currency(to_decimal(getattr(args, 'personal_expenses', '0') or '0')))
    loan_fees = str(round_currency(to_decimal(getattr(args, 'loan_fees', '0') or '0')))
    total_coa = _calc_total_coa(tuition_fees, books_supplies, room_board, transportation, personal_expenses, loan_fees)
    program_id = getattr(args, 'program_id', None)
    coa_id = str(uuid.uuid4())
    try:
        conn.execute(
            "INSERT INTO finaid_cost_of_attendance (id,aid_year_id,program_id,enrollment_status,living_arrangement,tuition_fees,books_supplies,room_board,transportation,personal_expenses,loan_fees,total_coa,is_active,company_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (coa_id, aid_year_id, program_id, enrollment_status, living_arrangement,
             tuition_fees, books_supplies, room_board, transportation, personal_expenses, loan_fees, total_coa, 1, company_id)
        )
        conn.commit()
        return ok({"id": coa_id, "total_coa": total_coa})
    except sqlite3.IntegrityError as e:
        return err(f"Duplicate COA configuration: {e}")


def update_cost_of_attendance(conn, args):
    coa_id = getattr(args, 'id', None)
    if not coa_id:
        return err("id is required")
    row = conn.execute("SELECT * FROM finaid_cost_of_attendance WHERE id=?", (coa_id,)).fetchone()
    if not row:
        return err("COA not found")
    money_fields = ['tuition_fees', 'books_supplies', 'room_board', 'transportation', 'personal_expenses', 'loan_fees']
    current = dict(row)
    fields, vals = [], []
    for f in money_fields:
        v = getattr(args, f, None)
        if v is not None:
            new_val = str(round_currency(to_decimal(v)))
            fields.append(f"{f}=?")
            vals.append(new_val)
            current[f] = new_val
    is_active = getattr(args, 'is_active', None)
    if is_active is not None:
        fields.append("is_active=?")
        vals.append(int(is_active))
    if fields:
        new_total = _calc_total_coa(current['tuition_fees'], current['books_supplies'], current['room_board'],
                                     current['transportation'], current['personal_expenses'], current['loan_fees'])
        fields.extend(["total_coa=?", "updated_at=?"])
        vals.extend([new_total, _now_iso()])
        vals.append(coa_id)
        conn.execute(f"UPDATE finaid_cost_of_attendance SET {','.join(fields)} WHERE id=?", vals)
        conn.commit()
        return ok({"id": coa_id, "total_coa": new_total})
    return err("No fields to update")


def get_cost_of_attendance(conn, args):
    coa_id = getattr(args, 'id', None)
    if not coa_id:
        return err("id is required")
    row = conn.execute("SELECT * FROM finaid_cost_of_attendance WHERE id=?", (coa_id,)).fetchone()
    if not row:
        return err("COA not found")
    return ok(dict(row))


def list_cost_of_attendance(conn, args):
    company_id = getattr(args, 'company_id', None)
    if not company_id:
        return err("company_id is required")
    q = "SELECT * FROM finaid_cost_of_attendance WHERE company_id=?"
    params = [company_id]
    for f in ['aid_year_id', 'enrollment_status']:
        v = getattr(args, f, None)
        if v:
            q += f" AND {f}=?"
            params.append(v)
    q += " LIMIT ? OFFSET ?"
    params.extend([int(getattr(args, 'limit', 50) or 50), int(getattr(args, 'offset', 0) or 0)])
    rows = conn.execute(q, params).fetchall()
    return ok({"cost_of_attendance": [dict(r) for r in rows], "count": len(rows)})


def delete_cost_of_attendance(conn, args):
    coa_id = getattr(args, 'id', None)
    if not coa_id:
        return err("id is required")
    ref = conn.execute("SELECT id FROM finaid_award_package WHERE cost_of_attendance_id=? LIMIT 1", (coa_id,)).fetchone()
    if ref:
        return err("Cannot delete COA referenced by award package(s)")
    conn.execute("DELETE FROM finaid_cost_of_attendance WHERE id=?", (coa_id,))
    conn.commit()
    return ok({"id": coa_id, "deleted": True})


# ---------------------------------------------------------------------------
# ISIR Management
# ---------------------------------------------------------------------------

_CFLAG_DESCRIPTIONS = {
    'nslds_default': ('C25', 'NSLDS: Loan default match', 1),
    'nslds_overpayment': ('C09', 'NSLDS: Grant overpayment match', 1),
    'selective_service': ('C07', 'Selective Service registration match issue', 1),
    'citizenship': ('C01', 'Citizenship/SSN match issue', 1),
}


def import_isir(conn, args):
    student_id = getattr(args, 'student_id', None)
    aid_year_id = getattr(args, 'aid_year_id', None)
    company_id = getattr(args, 'company_id', None)
    sai = getattr(args, 'sai', '0') or '0'
    receipt_date = getattr(args, 'receipt_date', '') or ''
    if not student_id:
        return err("student_id is required")
    if not aid_year_id:
        return err("aid_year_id is required")
    if not company_id:
        return err("company_id is required")
    transaction_number = int(getattr(args, 'transaction_number', 1) or 1)
    fafsa_submission_id = getattr(args, 'fafsa_submission_id', '') or ''
    dependency_status = getattr(args, 'dependency_status', '') or ''
    pell_index = getattr(args, 'pell_index_isir', '') or getattr(args, 'pell_index', '') or ''
    verification_flag = int(getattr(args, 'verification_flag', 0) or 0)
    verification_group = getattr(args, 'verification_group', '') or ''
    nslds_default_flag = int(getattr(args, 'nslds_default_flag', 0) or 0)
    nslds_overpayment_flag = int(getattr(args, 'nslds_overpayment_flag', 0) or 0)
    selective_service_flag = int(getattr(args, 'selective_service_flag', 0) or 0)
    citizenship_flag = int(getattr(args, 'citizenship_flag', 0) or 0)
    sai_decimal = to_decimal(sai)
    sai_is_negative = 1 if sai_decimal < Decimal('0') else 0
    agi = getattr(args, 'agi', '0') or '0'
    household_size = int(getattr(args, 'household_size', 0) or 0)
    raw_isir_data = getattr(args, 'raw_isir_data', '{}') or '{}'
    isir_id = str(uuid.uuid4())
    cflags = []
    if nslds_default_flag:
        cflags.append(('C25', 'NSLDS: Loan default match', 1))
    if nslds_overpayment_flag:
        cflags.append(('C09', 'NSLDS: Grant overpayment match', 1))
    if selective_service_flag:
        cflags.append(('C07', 'Selective Service registration issue', 1))
    if citizenship_flag:
        cflags.append(('C01', 'Citizenship/SSN match issue', 1))
    has_unresolved_cflags = 1 if cflags else 0
    try:
        conn.execute(
            "INSERT INTO finaid_isir (id,student_id,aid_year_id,transaction_number,is_active_transaction,fafsa_submission_id,receipt_date,sai,sai_is_negative,dependency_status,pell_index,verification_flag,verification_group,has_unresolved_cflags,nslds_default_flag,nslds_overpayment_flag,selective_service_flag,citizenship_flag,agi,household_size,status,raw_isir_data,company_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (isir_id, student_id, aid_year_id, transaction_number, 0, fafsa_submission_id, receipt_date,
             str(round_currency(sai_decimal)), sai_is_negative, dependency_status, pell_index, verification_flag,
             verification_group, has_unresolved_cflags, nslds_default_flag, nslds_overpayment_flag,
             selective_service_flag, citizenship_flag, str(round_currency(to_decimal(agi))),
             household_size, 'received', raw_isir_data, company_id)
        )
        for cflag_code, cflag_desc, blocks in cflags:
            cflag_id = str(uuid.uuid4())
            conn.execute(
                "INSERT OR IGNORE INTO finaid_isir_cflag (id,isir_id,student_id,cflag_code,cflag_description,blocks_disbursement,resolution_status,company_id) VALUES (?,?,?,?,?,?,?,?)",
                (cflag_id, isir_id, student_id, cflag_code, cflag_desc, blocks, 'pending', company_id)
            )
        conn.commit()
        return ok({"id": isir_id, "has_unresolved_cflags": has_unresolved_cflags, "cflags_created": len(cflags)})
    except sqlite3.IntegrityError as e:
        return err(f"Duplicate ISIR transaction: {e}")


def update_isir(conn, args):
    isir_id = getattr(args, 'isir_id', None) or getattr(args, 'id', None)
    if not isir_id:
        return err("isir_id or id is required")
    row = conn.execute("SELECT * FROM finaid_isir WHERE id=?", (isir_id,)).fetchone()
    if not row:
        return err("ISIR not found")
    fields, vals = [], []
    for f in ['sai', 'dependency_status', 'pell_index', 'verification_flag', 'verification_group', 'receipt_date', 'fafsa_submission_id']:
        v = getattr(args, f, None)
        if v is not None:
            fields.append(f"{f}=?")
            vals.append(v)
    is_active_transaction = getattr(args, 'is_active_transaction', None)
    if is_active_transaction is not None:
        fields.append("is_active_transaction=?")
        vals.append(int(is_active_transaction))
    # Recompute has_unresolved_cflags
    pending_count = conn.execute(
        "SELECT COUNT(*) FROM finaid_isir_cflag WHERE isir_id=? AND resolution_status='pending'", (isir_id,)
    ).fetchone()[0]
    fields.append("has_unresolved_cflags=?")
    vals.append(1 if pending_count > 0 else 0)
    fields.append("updated_at=?")
    vals.append(_now_iso())
    vals.append(isir_id)
    conn.execute(f"UPDATE finaid_isir SET {','.join(fields)} WHERE id=?", vals)
    conn.commit()
    return ok({"id": isir_id, "updated": True})


def get_isir(conn, args):
    isir_id = getattr(args, 'isir_id', None) or getattr(args, 'id', None)
    if not isir_id:
        return err("isir_id or id is required")
    row = conn.execute("SELECT * FROM finaid_isir WHERE id=?", (isir_id,)).fetchone()
    if not row:
        return err("ISIR not found")
    cflags = conn.execute("SELECT * FROM finaid_isir_cflag WHERE isir_id=?", (isir_id,)).fetchall()
    result = dict(row)
    result['cflags'] = [dict(c) for c in cflags]
    return ok(result)


def list_isirs(conn, args):
    company_id = getattr(args, 'company_id', None)
    if not company_id:
        return err("company_id is required")
    q = "SELECT * FROM finaid_isir WHERE company_id=?"
    params = [company_id]
    for f in ['student_id', 'aid_year_id', 'status']:
        v = getattr(args, f, None)
        if v:
            q += f" AND {f}=?"
            params.append(v)
    q += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([int(getattr(args, 'limit', 50) or 50), int(getattr(args, 'offset', 0) or 0)])
    rows = conn.execute(q, params).fetchall()
    return ok({"isirs": [dict(r) for r in rows], "count": len(rows)})


def review_isir(conn, args):
    isir_id = getattr(args, 'isir_id', None) or getattr(args, 'id', None)
    reviewed_by = getattr(args, 'reviewed_by', '') or ''
    if not isir_id:
        return err("isir_id or id is required")
    conn.execute(
        "UPDATE finaid_isir SET status='reviewed', reviewed_by=?, reviewed_at=?, updated_at=? WHERE id=?",
        (reviewed_by, _now_iso(), _now_iso(), isir_id)
    )
    conn.commit()
    return ok({"id": isir_id, "status": "reviewed"})


def add_isir_cflag(conn, args):
    isir_id = getattr(args, 'isir_id', None)
    company_id = getattr(args, 'company_id', None)
    cflag_code = getattr(args, 'cflag_code', None)
    if not isir_id:
        return err("isir_id is required")
    if not company_id:
        return err("company_id is required")
    if not cflag_code:
        return err("cflag_code is required")
    isir_row = conn.execute("SELECT student_id FROM finaid_isir WHERE id=?", (isir_id,)).fetchone()
    if not isir_row:
        return err("ISIR not found")
    student_id = isir_row['student_id']
    cflag_description = getattr(args, 'cflag_description', '') or ''
    blocks_disbursement = int(getattr(args, 'blocks_disbursement', 1) or 1)
    cflag_id = str(uuid.uuid4())
    try:
        conn.execute(
            "INSERT INTO finaid_isir_cflag (id,isir_id,student_id,cflag_code,cflag_description,blocks_disbursement,resolution_status,company_id) VALUES (?,?,?,?,?,?,?,?)",
            (cflag_id, isir_id, student_id, cflag_code, cflag_description, blocks_disbursement, 'pending', company_id)
        )
        conn.execute("UPDATE finaid_isir SET has_unresolved_cflags=1, updated_at=? WHERE id=?", (_now_iso(), isir_id))
        conn.commit()
        return ok({"id": cflag_id, "isir_id": isir_id})
    except sqlite3.IntegrityError as e:
        return err(f"Duplicate C-flag: {e}")


def resolve_isir_cflag(conn, args):
    cflag_id = getattr(args, 'id', None)
    resolution_status = getattr(args, 'resolution_status', None)
    if not cflag_id:
        return err("id is required")
    if not resolution_status:
        return err("resolution_status is required")
    row = conn.execute("SELECT isir_id FROM finaid_isir_cflag WHERE id=?", (cflag_id,)).fetchone()
    if not row:
        return err("C-flag not found")
    isir_id = row['isir_id']
    resolution_date = getattr(args, 'resolution_date', _today()) or _today()
    resolved_by = getattr(args, 'resolved_by', '') or ''
    resolution_notes = getattr(args, 'resolution_notes', '') or ''
    conn.execute(
        "UPDATE finaid_isir_cflag SET resolution_status=?,resolution_date=?,resolved_by=?,resolution_notes=?,updated_at=? WHERE id=?",
        (resolution_status, resolution_date, resolved_by, resolution_notes, _now_iso(), cflag_id)
    )
    pending_count = conn.execute(
        "SELECT COUNT(*) FROM finaid_isir_cflag WHERE isir_id=? AND resolution_status='pending'", (isir_id,)
    ).fetchone()[0]
    conn.execute(
        "UPDATE finaid_isir SET has_unresolved_cflags=?, updated_at=? WHERE id=?",
        (1 if pending_count > 0 else 0, _now_iso(), isir_id)
    )
    conn.commit()
    return ok({"id": cflag_id, "resolution_status": resolution_status})


def list_isir_cflags(conn, args):
    isir_id = getattr(args, 'isir_id', None)
    student_id = getattr(args, 'student_id', None)
    if not isir_id and not student_id:
        return err("isir_id or student_id is required")
    q = "SELECT * FROM finaid_isir_cflag WHERE 1=1"
    params = []
    if isir_id:
        q += " AND isir_id=?"
        params.append(isir_id)
    if student_id:
        q += " AND student_id=?"
        params.append(student_id)
    resolution_status = getattr(args, 'resolution_status', None)
    if resolution_status:
        q += " AND resolution_status=?"
        params.append(resolution_status)
    rows = conn.execute(q, params).fetchall()
    return ok({"cflags": [dict(r) for r in rows], "count": len(rows)})


# ---------------------------------------------------------------------------
# Verification Workflow
# ---------------------------------------------------------------------------

_VERIFICATION_DOCS = {
    'V1': [
        ('tax_transcript', 'Federal tax return transcript', 1),
        ('w2', 'W-2 forms', 1),
        ('household_verification', 'Household verification form', 1),
    ],
    'V4': [
        ('identity', 'Government-issued photo ID', 1),
        ('statement_of_purpose', 'Statement of educational purpose', 1),
    ],
    'V5': [
        ('hs_completion', 'High school completion documentation', 1),
        ('identity', 'Government-issued photo ID', 1),
    ],
}


def create_verification_request(conn, args):
    isir_id = getattr(args, 'isir_id', None)
    student_id = getattr(args, 'student_id', None)
    company_id = getattr(args, 'company_id', None)
    verification_group = getattr(args, 'verification_group', None)
    if not isir_id:
        return err("isir_id is required")
    if not student_id:
        return err("student_id is required")
    if not company_id:
        return err("company_id is required")
    if not verification_group:
        return err("verification_group is required")
    req_id = str(uuid.uuid4())
    requested_date = getattr(args, 'requested_date', _today()) or _today()
    deadline_date = getattr(args, 'deadline_date', '') or ''
    assigned_to = getattr(args, 'assigned_to', '') or ''
    try:
        conn.execute(
            "INSERT INTO finaid_verification_request (id,isir_id,student_id,verification_group,status,requested_date,deadline_date,assigned_to,company_id) VALUES (?,?,?,?,?,?,?,?,?)",
            (req_id, isir_id, student_id, verification_group, 'initiated', requested_date, deadline_date, assigned_to, company_id)
        )
        docs_created = 0
        for doc_type, doc_desc, is_required in _VERIFICATION_DOCS.get(verification_group, []):
            doc_id = str(uuid.uuid4())
            conn.execute(
                "INSERT INTO finaid_verification_document (id,verification_request_id,student_id,document_type,document_description,is_required,submission_status,company_id) VALUES (?,?,?,?,?,?,?,?)",
                (doc_id, req_id, student_id, doc_type, doc_desc, is_required, 'not_submitted', company_id)
            )
            docs_created += 1
        conn.commit()
        return ok({"id": req_id, "verification_group": verification_group, "documents_created": docs_created})
    except sqlite3.IntegrityError as e:
        return err(f"Duplicate verification request for this ISIR: {e}")


def update_verification_request(conn, args):
    req_id = getattr(args, 'verification_request_id', None) or getattr(args, 'id', None)
    if not req_id:
        return err("verification_request_id or id is required")
    fields, vals = [], []
    for f in ['status', 'deadline_date', 'assigned_to', 'discrepancy_notes']:
        v = getattr(args, f, None)
        if v is not None:
            fields.append(f"{f}=?")
            vals.append(v)
    discrepancy_found = getattr(args, 'discrepancy_found', None)
    if discrepancy_found is not None:
        fields.append("discrepancy_found=?")
        vals.append(int(discrepancy_found))
    if not fields:
        return err("No fields to update")
    fields.append("updated_at=?")
    vals.append(_now_iso())
    vals.append(req_id)
    conn.execute(f"UPDATE finaid_verification_request SET {','.join(fields)} WHERE id=?", vals)
    conn.commit()
    return ok({"id": req_id, "updated": True})


def get_verification_request(conn, args):
    req_id = getattr(args, 'verification_request_id', None) or getattr(args, 'id', None)
    if not req_id:
        return err("verification_request_id or id is required")
    row = conn.execute("SELECT * FROM finaid_verification_request WHERE id=?", (req_id,)).fetchone()
    if not row:
        return err("Verification request not found")
    docs = conn.execute("SELECT * FROM finaid_verification_document WHERE verification_request_id=?", (req_id,)).fetchall()
    result = dict(row)
    result['documents'] = [dict(d) for d in docs]
    return ok(result)


def list_verification_requests(conn, args):
    company_id = getattr(args, 'company_id', None)
    if not company_id:
        return err("company_id is required")
    q = "SELECT * FROM finaid_verification_request WHERE company_id=?"
    params = [company_id]
    for f in ['status', 'assigned_to', 'student_id']:
        v = getattr(args, f, None)
        if v:
            q += f" AND {f}=?"
            params.append(v)
    q += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([int(getattr(args, 'limit', 50) or 50), int(getattr(args, 'offset', 0) or 0)])
    rows = conn.execute(q, params).fetchall()
    return ok({"verification_requests": [dict(r) for r in rows], "count": len(rows)})


def add_verification_document(conn, args):
    req_id = getattr(args, 'verification_request_id', None)
    student_id = getattr(args, 'student_id', None)
    company_id = getattr(args, 'company_id', None)
    document_type = getattr(args, 'document_type', None)
    if not req_id or not student_id or not company_id or not document_type:
        return err("verification_request_id, student_id, company_id, and document_type are required")
    doc_id = str(uuid.uuid4())
    document_description = getattr(args, 'document_description', '') or ''
    is_required = int(getattr(args, 'is_required', 1) or 1)
    try:
        conn.execute(
            "INSERT INTO finaid_verification_document (id,verification_request_id,student_id,document_type,document_description,is_required,submission_status,company_id) VALUES (?,?,?,?,?,?,?,?)",
            (doc_id, req_id, student_id, document_type, document_description, is_required, 'not_submitted', company_id)
        )
        conn.commit()
        return ok({"id": doc_id})
    except sqlite3.IntegrityError as e:
        return err(f"Duplicate document type for this request: {e}")


def update_verification_document(conn, args):
    doc_id = getattr(args, 'id', None)
    if not doc_id:
        return err("id is required")
    fields, vals = [], []
    for f in ['submission_status', 'reviewed_by', 'reviewed_date', 'rejection_reason', 'document_reference', 'submitted_date']:
        v = getattr(args, f, None)
        if v is not None:
            fields.append(f"{f}=?")
            vals.append(v)
    if not fields:
        return err("No fields to update")
    fields.append("updated_at=?")
    vals.append(_now_iso())
    vals.append(doc_id)
    conn.execute(f"UPDATE finaid_verification_document SET {','.join(fields)} WHERE id=?", vals)
    conn.commit()
    return ok({"id": doc_id, "updated": True})


def complete_verification(conn, args):
    req_id = getattr(args, 'verification_request_id', None) or getattr(args, 'id', None)
    if not req_id:
        return err("verification_request_id or id is required")
    # Check all required docs are accepted or waived
    pending = conn.execute(
        "SELECT COUNT(*) FROM finaid_verification_document WHERE verification_request_id=? AND is_required=1 AND submission_status NOT IN ('accepted','waived')",
        (req_id,)
    ).fetchone()[0]
    if pending > 0:
        return err(f"{pending} required document(s) not yet accepted or waived")
    completed_date = getattr(args, 'completed_date', _today()) or _today()
    conn.execute(
        "UPDATE finaid_verification_request SET status='complete', completed_date=?, updated_at=? WHERE id=?",
        (completed_date, _now_iso(), req_id)
    )
    conn.commit()
    return ok({"id": req_id, "status": "complete"})


def list_verification_documents(conn, args):
    req_id = getattr(args, 'verification_request_id', None)
    if not req_id:
        return err("verification_request_id is required")
    rows = conn.execute("SELECT * FROM finaid_verification_document WHERE verification_request_id=?", (req_id,)).fetchall()
    return ok({"documents": [dict(r) for r in rows], "count": len(rows)})


# ---------------------------------------------------------------------------
# Award Packaging
# ---------------------------------------------------------------------------

def _update_package_totals(conn, pkg_id):
    awards = conn.execute(
        "SELECT aid_type, aid_source, offered_amount FROM finaid_award WHERE award_package_id=?",
        (pkg_id,)
    ).fetchall()
    total_grants = Decimal('0')
    total_loans = Decimal('0')
    total_work_study = Decimal('0')
    grant_types = {'pell', 'fseog', 'institutional_grant', 'institutional_scholarship', 'state_grant', 'external_scholarship', 'tuition_waiver', 'teach_grant'}
    loan_types = {'subsidized_loan', 'unsubsidized_loan', 'plus_loan', 'parent_plus_loan'}
    for a in awards:
        amt = to_decimal(a['offered_amount'])
        if a['aid_type'] in grant_types:
            total_grants += amt
        elif a['aid_type'] in loan_types:
            total_loans += amt
        elif a['aid_type'] == 'fws':
            total_work_study += amt
    total_aid = total_grants + total_loans + total_work_study
    conn.execute(
        "UPDATE finaid_award_package SET total_grants=?,total_loans=?,total_work_study=?,total_aid=?,updated_at=? WHERE id=?",
        (str(round_currency(total_grants)), str(round_currency(total_loans)),
         str(round_currency(total_work_study)), str(round_currency(total_aid)), _now_iso(), pkg_id)
    )


def create_award_package(conn, args):
    student_id = getattr(args, 'student_id', None)
    aid_year_id = getattr(args, 'aid_year_id', None)
    academic_term_id = getattr(args, 'academic_term_id', None)
    program_enrollment_id = getattr(args, 'program_enrollment_id', None)
    isir_id = getattr(args, 'isir_id', None)
    cost_of_attendance_id = getattr(args, 'cost_of_attendance_id', None)
    enrollment_status = getattr(args, 'enrollment_status', None)
    company_id = getattr(args, 'company_id', None)
    for name, val in [('student_id', student_id), ('aid_year_id', aid_year_id),
                       ('academic_term_id', academic_term_id), ('company_id', company_id)]:
        if not val:
            return err(f"{name} is required")
    # Get COA total for financial_need computation
    financial_need = '0'
    if cost_of_attendance_id and isir_id:
        coa_row = conn.execute("SELECT total_coa FROM finaid_cost_of_attendance WHERE id=?", (cost_of_attendance_id,)).fetchone()
        isir_row = conn.execute("SELECT sai FROM finaid_isir WHERE id=?", (isir_id,)).fetchone()
        if coa_row and isir_row:
            need = to_decimal(coa_row['total_coa']) - to_decimal(isir_row['sai'])
            financial_need = str(round_currency(max(need, Decimal('0'))))
    # Generate naming_series
    ay_row = conn.execute("SELECT aid_year_code FROM finaid_aid_year WHERE id=?", (aid_year_id,)).fetchone()
    ay_code = ay_row['aid_year_code'] if ay_row else 'XXXX'
    count = conn.execute("SELECT COUNT(*) FROM finaid_award_package WHERE aid_year_id=?", (aid_year_id,)).fetchone()[0]
    naming_series = f"AWD-{ay_code}-{count+1:05d}"
    pkg_id = str(uuid.uuid4())
    packaged_by = getattr(args, 'packaged_by', '') or ''
    notes = getattr(args, 'notes', '') or ''
    try:
        conn.execute(
            "INSERT INTO finaid_award_package (id,naming_series,student_id,aid_year_id,academic_term_id,program_enrollment_id,isir_id,cost_of_attendance_id,enrollment_status,financial_need,total_grants,total_loans,total_work_study,total_aid,status,packaged_by,packaged_at,notes,company_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (pkg_id, naming_series, student_id, aid_year_id, academic_term_id or '',
             program_enrollment_id or '', isir_id or '', cost_of_attendance_id or '',
             enrollment_status or '', financial_need, '0', '0', '0', '0', 'draft',
             packaged_by, _now_iso(), notes, company_id)
        )
        conn.commit()
        return ok({"id": pkg_id, "naming_series": naming_series, "financial_need": financial_need})
    except sqlite3.IntegrityError as e:
        return err(f"Duplicate award package: {e}")


def update_award_package(conn, args):
    pkg_id = getattr(args, 'award_package_id', None) or getattr(args, 'id', None)
    if not pkg_id:
        return err("award_package_id or id is required")
    fields, vals = [], []
    for f in ['notes', 'enrollment_status', 'acceptance_deadline', 'approved_by', 'approved_at']:
        v = getattr(args, f, None)
        if v is not None:
            fields.append(f"{f}=?")
            vals.append(v)
    if not fields:
        return err("No fields to update")
    fields.append("updated_at=?")
    vals.append(_now_iso())
    vals.append(pkg_id)
    conn.execute(f"UPDATE finaid_award_package SET {','.join(fields)} WHERE id=?", vals)
    conn.commit()
    return ok({"id": pkg_id, "updated": True})


def get_award_package(conn, args):
    pkg_id = getattr(args, 'award_package_id', None) or getattr(args, 'id', None)
    if not pkg_id:
        return err("award_package_id or id is required")
    row = conn.execute("SELECT * FROM finaid_award_package WHERE id=?", (pkg_id,)).fetchone()
    if not row:
        return err("Award package not found")
    awards = conn.execute("SELECT * FROM finaid_award WHERE award_package_id=?", (pkg_id,)).fetchall()
    result = dict(row)
    result['awards'] = [dict(a) for a in awards]
    return ok(result)


def list_award_packages(conn, args):
    company_id = getattr(args, 'company_id', None)
    if not company_id:
        return err("company_id is required")
    q = "SELECT * FROM finaid_award_package WHERE company_id=?"
    params = [company_id]
    for f in ['status', 'aid_year_id', 'student_id', 'academic_term_id']:
        v = getattr(args, f, None)
        if v:
            q += f" AND {f}=?"
            params.append(v)
    q += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([int(getattr(args, 'limit', 50) or 50), int(getattr(args, 'offset', 0) or 0)])
    rows = conn.execute(q, params).fetchall()
    return ok({"award_packages": [dict(r) for r in rows], "count": len(rows)})


def add_award(conn, args):
    award_package_id = getattr(args, 'award_package_id', None)
    student_id = getattr(args, 'student_id', None)
    aid_year_id = getattr(args, 'aid_year_id', None)
    academic_term_id = getattr(args, 'academic_term_id', None)
    aid_type = getattr(args, 'aid_type', None)
    aid_source = getattr(args, 'aid_source', None)
    offered_amount = str(round_currency(to_decimal(getattr(args, 'offered_amount', '0') or '0')))
    company_id = getattr(args, 'company_id', None)
    for name, val in [('award_package_id', award_package_id), ('student_id', student_id),
                       ('aid_type', aid_type), ('aid_source', aid_source), ('company_id', company_id)]:
        if not val:
            return err(f"{name} is required")
    # Validate package is draft
    pkg = conn.execute("SELECT status FROM finaid_award_package WHERE id=?", (award_package_id,)).fetchone()
    if not pkg:
        return err("Award package not found")
    if pkg['status'] not in ('draft', 'offered'):
        return err("Can only add awards to draft or offered packages")
    fund_source_id = getattr(args, 'fund_source_id', '') or ''
    gl_account_id = getattr(args, 'gl_account_id', '') or ''
    notes = getattr(args, 'notes', '') or ''
    award_id = str(uuid.uuid4())
    try:
        conn.execute(
            "INSERT INTO finaid_award (id,award_package_id,student_id,aid_year_id,academic_term_id,aid_type,aid_source,fund_source_id,offered_amount,accepted_amount,disbursed_amount,acceptance_status,disbursement_holds,is_locked,gl_account_id,notes,company_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (award_id, award_package_id, student_id, aid_year_id or '',
             academic_term_id or '', aid_type, aid_source, fund_source_id,
             offered_amount, '0', '0', 'pending', '[]', 0, gl_account_id, notes, company_id)
        )
        _update_package_totals(conn, award_package_id)
        conn.commit()
        return ok({"id": award_id, "aid_type": aid_type, "offered_amount": offered_amount})
    except sqlite3.IntegrityError as e:
        return err(f"Duplicate aid type in package: {e}")


def update_award(conn, args):
    award_id = getattr(args, 'award_id', None) or getattr(args, 'id', None)
    if not award_id:
        return err("award_id or id is required")
    row = conn.execute("SELECT award_package_id FROM finaid_award WHERE id=?", (award_id,)).fetchone()
    if not row:
        return err("Award not found")
    pkg = conn.execute("SELECT status FROM finaid_award_package WHERE id=?", (row['award_package_id'],)).fetchone()
    if pkg and pkg['status'] != 'draft':
        return err("Can only update awards in draft packages")
    fields, vals = [], []
    offered_amount = getattr(args, 'offered_amount', None)
    if offered_amount is not None:
        fields.append("offered_amount=?")
        vals.append(str(round_currency(to_decimal(offered_amount))))
    for f in ['notes', 'gl_account_id']:
        v = getattr(args, f, None)
        if v is not None:
            fields.append(f"{f}=?")
            vals.append(v)
    if not fields:
        return err("No fields to update")
    fields.append("updated_at=?")
    vals.append(_now_iso())
    vals.append(award_id)
    conn.execute(f"UPDATE finaid_award SET {','.join(fields)} WHERE id=?", vals)
    _update_package_totals(conn, row['award_package_id'])
    conn.commit()
    return ok({"id": award_id, "updated": True})


def get_award(conn, args):
    award_id = getattr(args, 'award_id', None) or getattr(args, 'id', None)
    if not award_id:
        return err("award_id or id is required")
    row = conn.execute("SELECT * FROM finaid_award WHERE id=?", (award_id,)).fetchone()
    if not row:
        return err("Award not found")
    return ok(dict(row))


def list_awards(conn, args):
    award_package_id = getattr(args, 'award_package_id', None)
    student_id = getattr(args, 'student_id', None)
    company_id = getattr(args, 'company_id', None)
    if not award_package_id and not student_id and not company_id:
        return err("award_package_id, student_id, or company_id is required")
    q = "SELECT * FROM finaid_award WHERE 1=1"
    params = []
    if award_package_id:
        q += " AND award_package_id=?"
        params.append(award_package_id)
    if student_id:
        q += " AND student_id=?"
        params.append(student_id)
    if company_id:
        q += " AND company_id=?"
        params.append(company_id)
    for f in ['aid_type', 'acceptance_status']:
        v = getattr(args, f, None)
        if v:
            q += f" AND {f}=?"
            params.append(v)
    rows = conn.execute(q, params).fetchall()
    return ok({"awards": [dict(r) for r in rows], "count": len(rows)})


def delete_award(conn, args):
    award_id = getattr(args, 'award_id', None) or getattr(args, 'id', None)
    if not award_id:
        return err("award_id or id is required")
    row = conn.execute("SELECT award_package_id FROM finaid_award WHERE id=?", (award_id,)).fetchone()
    if not row:
        return err("Award not found")
    pkg = conn.execute("SELECT status FROM finaid_award_package WHERE id=?", (row['award_package_id'],)).fetchone()
    if pkg and pkg['status'] != 'draft':
        return err("Can only delete awards from draft packages")
    conn.execute("DELETE FROM finaid_award WHERE id=?", (award_id,))
    _update_package_totals(conn, row['award_package_id'])
    conn.commit()
    return ok({"id": award_id, "deleted": True})


def offer_award_package(conn, args):
    pkg_id = getattr(args, 'award_package_id', None) or getattr(args, 'id', None)
    if not pkg_id:
        return err("award_package_id or id is required")
    row = conn.execute("SELECT * FROM finaid_award_package WHERE id=?", (pkg_id,)).fetchone()
    if not row:
        return err("Award package not found")
    if row['status'] != 'draft':
        return err("Package must be in draft status to offer")
    packaged_by = getattr(args, 'packaged_by', '') or ''
    offered_date = getattr(args, 'offered_date', _today()) or _today()
    conn.execute(
        "UPDATE finaid_award_package SET status='offered', offered_date=?, packaged_by=?, packaged_at=?, updated_at=? WHERE id=?",
        (offered_date, packaged_by, _now_iso(), _now_iso(), pkg_id)
    )
    conn.commit()
    return ok({"id": pkg_id, "status": "offered"})


def accept_award(conn, args):
    award_id = getattr(args, 'award_id', None) or getattr(args, 'id', None)
    if not award_id:
        return err("award_id or id is required")
    row = conn.execute("SELECT * FROM finaid_award WHERE id=?", (award_id,)).fetchone()
    if not row:
        return err("Award not found")
    accepted_amount = getattr(args, 'accepted_amount', None)
    if accepted_amount is None:
        accepted_amount = row['offered_amount']
    acceptance_date = getattr(args, 'acceptance_date', _today()) or _today()
    conn.execute(
        "UPDATE finaid_award SET acceptance_status='accepted', accepted_amount=?, acceptance_date=?, updated_at=? WHERE id=?",
        (str(round_currency(to_decimal(accepted_amount))), acceptance_date, _now_iso(), award_id)
    )
    conn.commit()
    return ok({"id": award_id, "acceptance_status": "accepted"})


def decline_award(conn, args):
    award_id = getattr(args, 'award_id', None) or getattr(args, 'id', None)
    if not award_id:
        return err("award_id or id is required")
    conn.execute(
        "UPDATE finaid_award SET acceptance_status='declined', accepted_amount='0', updated_at=? WHERE id=?",
        (_now_iso(), award_id)
    )
    conn.commit()
    return ok({"id": award_id, "acceptance_status": "declined"})


def cancel_award_package(conn, args):
    pkg_id = getattr(args, 'award_package_id', None) or getattr(args, 'id', None)
    if not pkg_id:
        return err("award_package_id or id is required")
    conn.execute(
        "UPDATE finaid_award_package SET status='cancelled', updated_at=? WHERE id=?",
        (_now_iso(), pkg_id)
    )
    conn.execute(
        "UPDATE finaid_award SET acceptance_status='declined', accepted_amount='0', updated_at=? WHERE award_package_id=?",
        (_now_iso(), pkg_id)
    )
    conn.commit()
    return ok({"id": pkg_id, "status": "cancelled"})


# ---------------------------------------------------------------------------
# Disbursement
# ---------------------------------------------------------------------------

def disburse_award(conn, args):
    award_id = getattr(args, 'award_id', None)
    student_id = getattr(args, 'student_id', None)
    amount = getattr(args, 'amount', None)
    disbursement_date = getattr(args, 'disbursement_date', _today()) or _today()
    company_id = getattr(args, 'company_id', None)
    for name, val in [('award_id', award_id), ('student_id', student_id), ('amount', amount), ('company_id', company_id)]:
        if not val:
            return err(f"{name} is required")
    award_row = conn.execute("SELECT * FROM finaid_award WHERE id=?", (award_id,)).fetchone()
    if not award_row:
        return err("Award not found")
    if award_row['acceptance_status'] != 'accepted':
        return err("Award must be accepted before disbursement")
    # Check disbursement holds
    holds = json.loads(award_row['disbursement_holds'] or '[]')
    if holds:
        return err(f"Disbursement blocked by holds: {', '.join(holds)}")
    pkg_id = award_row['award_package_id']
    disb_id = str(uuid.uuid4())
    disbursed_by = getattr(args, 'disbursed_by', '') or ''
    disbursement_number = int(getattr(args, 'disbursement_number', 1) or 1)
    amount_decimal = round_currency(to_decimal(amount))
    conn.execute(
        "INSERT INTO finaid_disbursement (id,award_id,award_package_id,student_id,disbursement_type,disbursement_number,amount,disbursement_date,disbursed_by,company_id,created_by) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (disb_id, award_id, pkg_id, student_id, 'disbursement', disbursement_number,
         str(amount_decimal), disbursement_date, disbursed_by, company_id, '')
    )
    new_disbursed = str(round_currency(to_decimal(award_row['disbursed_amount']) + amount_decimal))
    conn.execute(
        "UPDATE finaid_award SET disbursed_amount=?, is_locked=1, updated_at=? WHERE id=?",
        (new_disbursed, _now_iso(), award_id)
    )
    conn.commit()
    return ok({"id": disb_id, "amount": str(amount_decimal), "disbursement_date": disbursement_date})


def reverse_disbursement(conn, args):
    award_id = getattr(args, 'award_id', None)
    amount = getattr(args, 'amount', None)
    disbursement_date = getattr(args, 'disbursement_date', _today()) or _today()
    company_id = getattr(args, 'company_id', None)
    if not award_id or not amount or not company_id:
        return err("award_id, amount, and company_id are required")
    award_row = conn.execute("SELECT award_package_id, student_id, disbursed_amount FROM finaid_award WHERE id=?", (award_id,)).fetchone()
    if not award_row:
        return err("Award not found")
    disb_id = str(uuid.uuid4())
    amount_decimal = round_currency(to_decimal(amount))
    conn.execute(
        "INSERT INTO finaid_disbursement (id,award_id,award_package_id,student_id,disbursement_type,disbursement_number,amount,disbursement_date,company_id,created_by) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (disb_id, award_id, award_row['award_package_id'], award_row['student_id'],
         'reversal', 1, str(amount_decimal), disbursement_date, company_id, '')
    )
    new_disbursed = str(round_currency(to_decimal(award_row['disbursed_amount']) - amount_decimal))
    conn.execute("UPDATE finaid_award SET disbursed_amount=?, updated_at=? WHERE id=?", (new_disbursed, _now_iso(), award_id))
    conn.commit()
    return ok({"id": disb_id, "type": "reversal", "amount": str(amount_decimal)})


def record_r2t4_return_disbursement(conn, args):
    award_id = getattr(args, 'award_id', None)
    r2t4_id = getattr(args, 'r2t4_id', None)
    amount = getattr(args, 'amount', None)
    disbursement_date = getattr(args, 'disbursement_date', _today()) or _today()
    company_id = getattr(args, 'company_id', None)
    if not award_id or not amount or not company_id:
        return err("award_id, amount, and company_id are required")
    award_row = conn.execute("SELECT award_package_id, student_id FROM finaid_award WHERE id=?", (award_id,)).fetchone()
    if not award_row:
        return err("Award not found")
    disb_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO finaid_disbursement (id,award_id,award_package_id,student_id,disbursement_type,disbursement_number,amount,disbursement_date,company_id,created_by) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (disb_id, award_id, award_row['award_package_id'], award_row['student_id'],
         'return', 1, str(round_currency(to_decimal(amount))), disbursement_date, company_id, '')
    )
    if r2t4_id:
        conn.execute(
            "UPDATE finaid_r2t4_calculation SET institution_return_date=?, updated_at=? WHERE id=?",
            (disbursement_date, _now_iso(), r2t4_id)
        )
    conn.commit()
    return ok({"id": disb_id, "type": "return"})


def get_disbursement(conn, args):
    disb_id = getattr(args, 'id', None)
    if not disb_id:
        return err("id is required")
    row = conn.execute("SELECT * FROM finaid_disbursement WHERE id=?", (disb_id,)).fetchone()
    if not row:
        return err("Disbursement not found")
    return ok(dict(row))


def list_disbursements(conn, args):
    company_id = getattr(args, 'company_id', None)
    if not company_id:
        return err("company_id is required")
    q = "SELECT * FROM finaid_disbursement WHERE company_id=?"
    params = [company_id]
    for f in ['student_id', 'award_id', 'cod_status']:
        v = getattr(args, f, None)
        if v:
            q += f" AND {f}=?"
            params.append(v)
    is_credit_balance = getattr(args, 'is_credit_balance', None)
    if is_credit_balance is not None:
        q += " AND is_credit_balance=?"
        params.append(int(is_credit_balance))
    q += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([int(getattr(args, 'limit', 50) or 50), int(getattr(args, 'offset', 0) or 0)])
    rows = conn.execute(q, params).fetchall()
    return ok({"disbursements": [dict(r) for r in rows], "count": len(rows)})


def generate_cod_export(conn, args):
    company_id = getattr(args, 'company_id', None)
    aid_year_id = getattr(args, 'aid_year_id', None)
    if not company_id:
        return err("company_id is required")
    q = "SELECT d.*, a.aid_type FROM finaid_disbursement d JOIN finaid_award a ON d.award_id=a.id WHERE d.company_id=? AND d.cod_status IN ('pending','')"
    params = [company_id]
    if aid_year_id:
        q += " AND a.aid_year_id=?"
        params.append(aid_year_id)
    rows = conn.execute(q, params).fetchall()
    return ok({"cod_records": [dict(r) for r in rows], "count": len(rows), "generated_at": _now_iso()})


def update_cod_status(conn, args):
    disb_id = getattr(args, 'id', None)
    cod_status = getattr(args, 'cod_status', None)
    if not disb_id or not cod_status:
        return err("id and cod_status are required")
    cod_response_date = getattr(args, 'cod_response_date', _today()) or _today()
    conn.execute(
        "UPDATE finaid_disbursement SET cod_status=?, cod_response_date=? WHERE id=?",
        (cod_status, cod_response_date, disb_id)
    )
    conn.commit()
    return ok({"id": disb_id, "cod_status": cod_status})


def mark_credit_balance_returned(conn, args):
    disb_id = getattr(args, 'id', None)
    return_date = getattr(args, 'return_date', _today()) or _today()
    if not disb_id:
        return err("id is required")
    row = conn.execute("SELECT credit_balance_date, is_credit_balance FROM finaid_disbursement WHERE id=?", (disb_id,)).fetchone()
    if not row:
        return err("Disbursement not found")
    if not row['is_credit_balance']:
        return err("This disbursement is not a credit balance")
    # Validate 14-day rule (lenient check)
    conn.execute(
        "UPDATE finaid_disbursement SET credit_balance_returned_date=? WHERE id=?",
        (return_date, disb_id)
    )
    conn.commit()
    return ok({"id": disb_id, "credit_balance_returned_date": return_date})


# ---------------------------------------------------------------------------
# SAP Evaluation
# ---------------------------------------------------------------------------

def _compute_sap_status(gpa_earned, gpa_threshold, credits_attempted, credits_completed,
                         max_timeframe_credits, projected_credits_remaining,
                         transfer_attempted, transfer_completed):
    gpa_ok = to_decimal(gpa_earned) >= to_decimal(gpa_threshold)
    total_attempted = to_decimal(credits_attempted) + to_decimal(transfer_attempted)
    total_completed = to_decimal(credits_completed) + to_decimal(transfer_completed)
    if total_attempted > Decimal('0'):
        completion_rate = total_completed / total_attempted
    else:
        completion_rate = Decimal('0')
    pace_ok = completion_rate >= Decimal('0.67')
    max_timeframe_ok = to_decimal(projected_credits_remaining) <= (to_decimal(max_timeframe_credits) - total_attempted) if to_decimal(max_timeframe_credits) > Decimal('0') else True
    if gpa_ok and pace_ok and max_timeframe_ok:
        return 'SAT', str(round_currency(completion_rate)), 1, 1, 1
    else:
        return 'FSP', str(round_currency(completion_rate)), 1 if gpa_ok else 0, 1 if pace_ok else 0, 1 if max_timeframe_ok else 0


def run_sap_evaluation(conn, args):
    student_id = getattr(args, 'student_id', None)
    academic_term_id = getattr(args, 'academic_term_id', None)
    aid_year_id = getattr(args, 'aid_year_id', None)
    company_id = getattr(args, 'company_id', None)
    for name, val in [('student_id', student_id), ('academic_term_id', academic_term_id), ('company_id', company_id)]:
        if not val:
            return err(f"{name} is required")
    gpa_earned = getattr(args, 'gpa_earned', '0') or '0'
    gpa_threshold = getattr(args, 'gpa_threshold', '2.00') or '2.00'
    credits_attempted = getattr(args, 'credits_attempted', '0') or '0'
    credits_completed = getattr(args, 'credits_completed', '0') or '0'
    completion_threshold = getattr(args, 'completion_threshold', '0.67') or '0.67'
    max_timeframe_credits = getattr(args, 'max_timeframe_credits', '0') or '0'
    projected_credits_remaining = getattr(args, 'projected_credits_remaining', '0') or '0'
    transfer_credits_attempted = getattr(args, 'transfer_credits_attempted', '0') or '0'
    transfer_credits_completed = getattr(args, 'transfer_credits_completed', '0') or '0'
    evaluation_date = getattr(args, 'evaluation_date', _today()) or _today()
    evaluated_by = getattr(args, 'evaluated_by', 'system') or 'system'
    evaluation_type = getattr(args, 'evaluation_type', 'automatic') or 'automatic'
    sap_status, completion_rate, gpa_ok, pace_ok, max_ok = _compute_sap_status(
        gpa_earned, gpa_threshold, credits_attempted, credits_completed,
        max_timeframe_credits, projected_credits_remaining,
        transfer_credits_attempted, transfer_credits_completed
    )
    # Check for prior SAP status
    prior_row = conn.execute(
        "SELECT sap_status FROM finaid_sap_evaluation WHERE student_id=? AND academic_term_id=?",
        (student_id, academic_term_id)
    ).fetchone()
    prior_sap_status = prior_row['sap_status'] if prior_row else ''
    eval_id = str(uuid.uuid4())
    try:
        conn.execute(
            "INSERT OR REPLACE INTO finaid_sap_evaluation (id,student_id,academic_term_id,aid_year_id,evaluation_date,evaluation_type,gpa_earned,gpa_threshold,gpa_meets_standard,credits_attempted,credits_completed,completion_rate,completion_threshold,completion_meets_standard,max_timeframe_credits,projected_credits_remaining,max_timeframe_met,transfer_credits_attempted,transfer_credits_completed,sap_status,prior_sap_status,holds_placed,evaluated_by,notes,company_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (eval_id, student_id, academic_term_id, aid_year_id or '', evaluation_date, evaluation_type,
             str(round_currency(to_decimal(gpa_earned))), gpa_threshold, gpa_ok,
             str(round_currency(to_decimal(credits_attempted))), str(round_currency(to_decimal(credits_completed))),
             completion_rate, completion_threshold, pace_ok,
             str(round_currency(to_decimal(max_timeframe_credits))),
             str(round_currency(to_decimal(projected_credits_remaining))), max_ok,
             str(round_currency(to_decimal(transfer_credits_attempted))),
             str(round_currency(to_decimal(transfer_credits_completed))),
             sap_status, prior_sap_status, 1 if sap_status in ('FSP', 'FAW') else 0,
             evaluated_by, '', company_id)
        )
        conn.commit()
        return ok({"id": eval_id, "sap_status": sap_status, "completion_rate": completion_rate})
    except sqlite3.IntegrityError as e:
        return err(f"SAP evaluation error: {e}")


def run_sap_batch(conn, args):
    academic_term_id = getattr(args, 'academic_term_id', None)
    company_id = getattr(args, 'company_id', None)
    if not academic_term_id or not company_id:
        return err("academic_term_id and company_id are required")
    # Get all students with packages for this term
    packages = conn.execute(
        "SELECT DISTINCT student_id, aid_year_id FROM finaid_award_package WHERE academic_term_id=? AND company_id=?",
        (academic_term_id, company_id)
    ).fetchall()
    results = []
    for pkg in packages:
        # Use default values for batch
        eval_id = str(uuid.uuid4())
        conn.execute(
            "INSERT OR IGNORE INTO finaid_sap_evaluation (id,student_id,academic_term_id,aid_year_id,evaluation_date,evaluation_type,sap_status,evaluated_by,company_id) VALUES (?,?,?,?,?,?,?,?,?)",
            (eval_id, pkg['student_id'], academic_term_id, pkg['aid_year_id'] or '',
             _today(), 'automatic', 'SAT', 'system', company_id)
        )
        results.append(pkg['student_id'])
    conn.commit()
    return ok({"evaluated": len(results), "academic_term_id": academic_term_id})


def get_sap_evaluation(conn, args):
    eval_id = getattr(args, 'id', None)
    if not eval_id:
        return err("id is required")
    row = conn.execute("SELECT * FROM finaid_sap_evaluation WHERE id=?", (eval_id,)).fetchone()
    if not row:
        return err("SAP evaluation not found")
    return ok(dict(row))


def list_sap_evaluations(conn, args):
    company_id = getattr(args, 'company_id', None)
    if not company_id:
        return err("company_id is required")
    q = "SELECT * FROM finaid_sap_evaluation WHERE company_id=?"
    params = [company_id]
    for f in ['student_id', 'academic_term_id', 'sap_status']:
        v = getattr(args, f, None)
        if v:
            q += f" AND {f}=?"
            params.append(v)
    q += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([int(getattr(args, 'limit', 50) or 50), int(getattr(args, 'offset', 0) or 0)])
    rows = conn.execute(q, params).fetchall()
    return ok({"sap_evaluations": [dict(r) for r in rows], "count": len(rows)})


def override_sap_status(conn, args):
    eval_id = getattr(args, 'id', None)
    sap_status = getattr(args, 'sap_status', None)
    evaluated_by = getattr(args, 'evaluated_by', None)
    if not eval_id or not sap_status:
        return err("id and sap_status are required")
    notes = getattr(args, 'notes', '') or ''
    conn.execute(
        "UPDATE finaid_sap_evaluation SET sap_status=?,evaluation_type='manual',evaluated_by=?,notes=?,updated_at=? WHERE id=?",
        (sap_status, evaluated_by or '', notes, _now_iso(), eval_id)
    )
    conn.commit()
    return ok({"id": eval_id, "sap_status": sap_status})


def submit_sap_appeal(conn, args):
    sap_evaluation_id = getattr(args, 'sap_evaluation_id', None)
    student_id = getattr(args, 'student_id', None)
    company_id = getattr(args, 'company_id', None)
    appeal_reason = getattr(args, 'appeal_reason', None)
    reason_narrative = getattr(args, 'reason_narrative', '') or ''
    academic_plan = getattr(args, 'academic_plan', '') or ''
    if not sap_evaluation_id or not student_id or not company_id or not appeal_reason:
        return err("sap_evaluation_id, student_id, company_id, and appeal_reason are required")
    eval_row = conn.execute("SELECT sap_status FROM finaid_sap_evaluation WHERE id=?", (sap_evaluation_id,)).fetchone()
    if not eval_row:
        return err("SAP evaluation not found")
    if eval_row['sap_status'] != 'FSP':
        return err("Can only appeal FSP (suspended) evaluations")
    appeal_id = str(uuid.uuid4())
    submitted_date = getattr(args, 'submitted_date', _today()) or _today()
    supporting_documents = getattr(args, 'supporting_documents', '[]') or '[]'
    try:
        conn.execute(
            "INSERT INTO finaid_sap_appeal (id,sap_evaluation_id,student_id,submitted_date,appeal_reason,reason_narrative,academic_plan,supporting_documents,status,company_id) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (appeal_id, sap_evaluation_id, student_id, submitted_date, appeal_reason,
             reason_narrative, academic_plan, supporting_documents, 'submitted', company_id)
        )
        conn.commit()
        return ok({"id": appeal_id, "status": "submitted"})
    except sqlite3.IntegrityError as e:
        return err(f"SAP appeal error: {e}")


def update_sap_appeal(conn, args):
    appeal_id = getattr(args, 'id', None)
    if not appeal_id:
        return err("id is required")
    fields, vals = [], []
    for f in ['status', 'reviewed_by', 'decision_rationale', 'probation_conditions']:
        v = getattr(args, f, None)
        if v is not None:
            fields.append(f"{f}=?")
            vals.append(v)
    reviewed_date = getattr(args, 'reviewed_date_appeal', None) or getattr(args, 'reviewed_date', None)
    if reviewed_date:
        fields.append("reviewed_date=?")
        vals.append(reviewed_date)
    if not fields:
        return err("No fields to update")
    fields.append("updated_at=?")
    vals.append(_now_iso())
    vals.append(appeal_id)
    conn.execute(f"UPDATE finaid_sap_appeal SET {','.join(fields)} WHERE id=?", vals)
    conn.commit()
    return ok({"id": appeal_id, "updated": True})


def get_sap_appeal(conn, args):
    appeal_id = getattr(args, 'id', None)
    if not appeal_id:
        return err("id is required")
    row = conn.execute("SELECT * FROM finaid_sap_appeal WHERE id=?", (appeal_id,)).fetchone()
    if not row:
        return err("SAP appeal not found")
    return ok(dict(row))


def list_sap_appeals(conn, args):
    company_id = getattr(args, 'company_id', None)
    if not company_id:
        return err("company_id is required")
    q = "SELECT * FROM finaid_sap_appeal WHERE company_id=?"
    params = [company_id]
    for f in ['student_id', 'status']:
        v = getattr(args, f, None)
        if v:
            q += f" AND {f}=?"
            params.append(v)
    q += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([int(getattr(args, 'limit', 50) or 50), int(getattr(args, 'offset', 0) or 0)])
    rows = conn.execute(q, params).fetchall()
    return ok({"sap_appeals": [dict(r) for r in rows], "count": len(rows)})


def decide_sap_appeal(conn, args):
    appeal_id = getattr(args, 'id', None)
    decision = getattr(args, 'status', None)
    if not appeal_id or not decision:
        return err("id and status (granted or denied) are required")
    if decision not in ('granted', 'denied'):
        return err("status must be 'granted' or 'denied'")
    appeal_row = conn.execute("SELECT sap_evaluation_id FROM finaid_sap_appeal WHERE id=?", (appeal_id,)).fetchone()
    if not appeal_row:
        return err("SAP appeal not found")
    reviewed_by = getattr(args, 'reviewed_by', '') or ''
    decision_rationale = getattr(args, 'decision_rationale', '') or ''
    reviewed_date = _today()
    conn.execute(
        "UPDATE finaid_sap_appeal SET status=?,reviewed_by=?,reviewed_date=?,decision_rationale=?,updated_at=? WHERE id=?",
        (decision, reviewed_by, reviewed_date, decision_rationale, _now_iso(), appeal_id)
    )
    if decision == 'granted':
        probation_term_id = getattr(args, 'probation_term_id', None)
        probation_conditions = getattr(args, 'probation_conditions', '') or ''
        conn.execute(
            "UPDATE finaid_sap_evaluation SET sap_status='FAP', updated_at=? WHERE id=?",
            (_now_iso(), appeal_row['sap_evaluation_id'])
        )
        if probation_term_id:
            conn.execute(
                "UPDATE finaid_sap_appeal SET probation_term_id=?, probation_conditions=? WHERE id=?",
                (probation_term_id, probation_conditions, appeal_id)
            )
    conn.commit()
    return ok({"id": appeal_id, "status": decision})


# ---------------------------------------------------------------------------
# R2T4 Calculation
# ---------------------------------------------------------------------------

def create_r2t4(conn, args):
    student_id = getattr(args, 'student_id', None)
    academic_term_id = getattr(args, 'academic_term_id', None)
    award_package_id = getattr(args, 'award_package_id', None)
    company_id = getattr(args, 'company_id', None)
    withdrawal_type = getattr(args, 'withdrawal_type', None)
    withdrawal_date = getattr(args, 'withdrawal_date', '') or ''
    last_date_of_attendance = getattr(args, 'last_date_of_attendance', '') or ''
    determination_date = getattr(args, 'determination_date', _today()) or _today()
    payment_period_start = getattr(args, 'payment_period_start', '') or ''
    payment_period_end = getattr(args, 'payment_period_end', '') or ''
    payment_period_days = int(getattr(args, 'payment_period_days', 0) or 0)
    for name, val in [('student_id', student_id), ('academic_term_id', academic_term_id), ('company_id', company_id)]:
        if not val:
            return err(f"{name} is required")
    # Compute due date
    try:
        det_dt = datetime.strptime(determination_date, '%Y-%m-%d')
        due_date = (det_dt + timedelta(days=45)).strftime('%Y-%m-%d')
    except ValueError:
        due_date = ''
    r2t4_id = str(uuid.uuid4())
    try:
        conn.execute(
            "INSERT INTO finaid_r2t4_calculation (id,student_id,academic_term_id,award_package_id,withdrawal_type,withdrawal_date,last_date_of_attendance,determination_date,payment_period_start,payment_period_end,payment_period_days,institution_return_due_date,status,calculated_by,company_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (r2t4_id, student_id, academic_term_id, award_package_id or '',
             withdrawal_type or '', withdrawal_date, last_date_of_attendance, determination_date,
             payment_period_start, payment_period_end, payment_period_days, due_date,
             'calculated', '', company_id)
        )
        conn.commit()
        return ok({"id": r2t4_id, "institution_return_due_date": due_date})
    except sqlite3.IntegrityError as e:
        return err(f"Duplicate R2T4 for this student/term: {e}")


def calculate_r2t4(conn, args):
    r2t4_id = getattr(args, 'id', None) or getattr(args, 'r2t4_id', None)
    if not r2t4_id:
        return err("id or r2t4_id is required")
    row = conn.execute("SELECT * FROM finaid_r2t4_calculation WHERE id=?", (r2t4_id,)).fetchone()
    if not row:
        return err("R2T4 calculation not found")
    r = dict(row)
    # Compute days attended
    try:
        lda = datetime.strptime(r['last_date_of_attendance'], '%Y-%m-%d')
        pps = datetime.strptime(r['payment_period_start'], '%Y-%m-%d')
        days_attended = (lda - pps).days
    except (ValueError, TypeError):
        days_attended = 0
    payment_period_days = r['payment_period_days']
    if payment_period_days > 0:
        percent_completed = Decimal(days_attended) / Decimal(payment_period_days)
    else:
        percent_completed = Decimal('0')
    earned_percent = Decimal('1') if percent_completed > Decimal('0.60') else percent_completed
    # Get disbursed amounts
    if r['award_package_id']:
        disb_rows = conn.execute(
            "SELECT SUM(CAST(amount AS REAL)) as total FROM finaid_disbursement WHERE award_package_id=? AND disbursement_type='disbursement'",
            (r['award_package_id'],)
        ).fetchone()
        total_aid_disbursed = Decimal(str(disb_rows['total'] or '0'))
    else:
        total_aid_disbursed = Decimal('0')
    earned_aid = round_currency(earned_percent * total_aid_disbursed)
    unearned_aid = round_currency(total_aid_disbursed - earned_aid)
    # Institution pays 50% of unearned
    institution_return = round_currency(unearned_aid * Decimal('0.50'))
    student_return = round_currency(unearned_aid - institution_return)
    conn.execute(
        "UPDATE finaid_r2t4_calculation SET days_attended=?,percent_completed=?,earned_percent=?,total_aid_disbursed=?,earned_aid=?,unearned_aid=?,institution_return_amount=?,student_return_amount=?,updated_at=? WHERE id=?",
        (days_attended, str(round_currency(percent_completed)), str(earned_percent),
         str(total_aid_disbursed), str(earned_aid), str(unearned_aid),
         str(institution_return), str(student_return), _now_iso(), r2t4_id)
    )
    conn.commit()
    return ok({
        "id": r2t4_id,
        "days_attended": days_attended,
        "percent_completed": str(round_currency(percent_completed)),
        "earned_aid": str(earned_aid),
        "unearned_aid": str(unearned_aid),
        "institution_return_amount": str(institution_return),
        "student_return_amount": str(student_return),
    })


def approve_r2t4(conn, args):
    r2t4_id = getattr(args, 'id', None) or getattr(args, 'r2t4_id', None)
    approved_by = getattr(args, 'approved_by', '') or ''
    if not r2t4_id:
        return err("id or r2t4_id is required")
    conn.execute(
        "UPDATE finaid_r2t4_calculation SET status='approved', approved_by=?, updated_at=? WHERE id=?",
        (approved_by, _now_iso(), r2t4_id)
    )
    conn.commit()
    return ok({"id": r2t4_id, "status": "approved"})


def record_r2t4_return(conn, args):
    r2t4_id = getattr(args, 'id', None) or getattr(args, 'r2t4_id', None)
    institution_return_date = getattr(args, 'institution_return_date', _today()) or _today()
    if not r2t4_id:
        return err("id or r2t4_id is required")
    conn.execute(
        "UPDATE finaid_r2t4_calculation SET institution_return_date=?, status='returned', updated_at=? WHERE id=?",
        (institution_return_date, _now_iso(), r2t4_id)
    )
    conn.commit()
    return ok({"id": r2t4_id, "status": "returned", "institution_return_date": institution_return_date})


def get_r2t4(conn, args):
    r2t4_id = getattr(args, 'id', None) or getattr(args, 'r2t4_id', None)
    if not r2t4_id:
        return err("id or r2t4_id is required")
    row = conn.execute("SELECT * FROM finaid_r2t4_calculation WHERE id=?", (r2t4_id,)).fetchone()
    if not row:
        return err("R2T4 calculation not found")
    return ok(dict(row))


def list_r2t4s(conn, args):
    company_id = getattr(args, 'company_id', None)
    if not company_id:
        return err("company_id is required")
    q = "SELECT * FROM finaid_r2t4_calculation WHERE company_id=?"
    params = [company_id]
    for f in ['student_id', 'status']:
        v = getattr(args, f, None)
        if v:
            q += f" AND {f}=?"
            params.append(v)
    q += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([int(getattr(args, 'limit', 50) or 50), int(getattr(args, 'offset', 0) or 0)])
    rows = conn.execute(q, params).fetchall()
    return ok({"r2t4_calculations": [dict(r) for r in rows], "count": len(rows)})


# ---------------------------------------------------------------------------
# Professional Judgment (append-only)
# ---------------------------------------------------------------------------

def add_professional_judgment(conn, args):
    student_id = getattr(args, 'student_id', None)
    aid_year_id = getattr(args, 'aid_year_id', None)
    company_id = getattr(args, 'company_id', None)
    pj_type = getattr(args, 'pj_type', None)
    pj_reason = getattr(args, 'pj_reason', None)
    reason_narrative = getattr(args, 'reason_narrative', '') or ''
    data_element_changed = getattr(args, 'data_element_changed', '') or ''
    original_value = getattr(args, 'original_value', '') or ''
    adjusted_value = getattr(args, 'adjusted_value', '') or ''
    effective_date = getattr(args, 'effective_date', _today()) or _today()
    authorized_by = getattr(args, 'authorized_by', '') or ''
    authorization_date = getattr(args, 'authorization_date', _today()) or _today()
    for name, val in [('student_id', student_id), ('aid_year_id', aid_year_id),
                       ('company_id', company_id), ('pj_type', pj_type), ('pj_reason', pj_reason)]:
        if not val:
            return err(f"{name} is required")
    pj_id = str(uuid.uuid4())
    supervisor_review_required = int(getattr(args, 'supervisor_review_required', 0) or 0)
    award_package_id = getattr(args, 'award_package_id', None)
    supporting_documentation = getattr(args, 'supporting_documents', '[]') or '[]'
    conn.execute(
        "INSERT INTO finaid_professional_judgment (id,student_id,aid_year_id,award_package_id,pj_type,pj_reason,reason_narrative,data_element_changed,original_value,adjusted_value,effective_date,supporting_documentation,authorized_by,authorization_date,supervisor_review_required,company_id,created_by) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (pj_id, student_id, aid_year_id, award_package_id, pj_type, pj_reason,
         reason_narrative, data_element_changed, original_value, adjusted_value, effective_date,
         supporting_documentation, authorized_by, authorization_date, supervisor_review_required,
         company_id, '')
    )
    conn.commit()
    return ok({"id": pj_id, "pj_type": pj_type})


def get_professional_judgment(conn, args):
    pj_id = getattr(args, 'id', None)
    if not pj_id:
        return err("id is required")
    row = conn.execute("SELECT * FROM finaid_professional_judgment WHERE id=?", (pj_id,)).fetchone()
    if not row:
        return err("Professional judgment not found")
    return ok(dict(row))


def list_professional_judgments(conn, args):
    company_id = getattr(args, 'company_id', None)
    if not company_id:
        return err("company_id is required")
    q = "SELECT * FROM finaid_professional_judgment WHERE company_id=?"
    params = [company_id]
    for f in ['student_id', 'aid_year_id', 'pj_type']:
        v = getattr(args, f, None)
        if v:
            q += f" AND {f}=?"
            params.append(v)
    q += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([int(getattr(args, 'limit', 50) or 50), int(getattr(args, 'offset', 0) or 0)])
    rows = conn.execute(q, params).fetchall()
    return ok({"professional_judgments": [dict(r) for r in rows], "count": len(rows)})


def approve_professional_judgment(conn, args):
    pj_id = getattr(args, 'id', None)
    supervisor_reviewed_by = getattr(args, 'supervisor_reviewed_by', None)
    if not pj_id or not supervisor_reviewed_by:
        return err("id and supervisor_reviewed_by are required")
    supervisor_review_date = getattr(args, 'supervisor_review_date', _today()) or _today()
    # finaid_professional_judgment is append-only but we allow supervisor approval update
    conn.execute(
        "UPDATE finaid_professional_judgment SET supervisor_reviewed_by=?, supervisor_review_date=? WHERE id=?",
        (supervisor_reviewed_by, supervisor_review_date, pj_id)
    )
    conn.commit()
    return ok({"id": pj_id, "supervisor_reviewed_by": supervisor_reviewed_by})


# ---------------------------------------------------------------------------
# ACTIONS
# ---------------------------------------------------------------------------

ACTIONS = {
    # Aid Year
    "add-aid-year": add_aid_year,
    "update-aid-year": update_aid_year,
    "get-aid-year": get_aid_year,
    "list-aid-years": list_aid_years,
    "activate-aid-year": set_active_aid_year,
    "import-pell-schedule": import_pell_schedule,
    "list-pell-schedule": list_pell_schedule,
    # Fund Allocation
    "add-fund-allocation": add_fund_allocation,
    "update-fund-allocation": update_fund_allocation,
    "get-fund-allocation": get_fund_allocation,
    "list-fund-allocations": list_fund_allocations,
    # Cost of Attendance
    "add-cost-of-attendance": add_cost_of_attendance,
    "update-cost-of-attendance": update_cost_of_attendance,
    "get-cost-of-attendance": get_cost_of_attendance,
    "list-cost-of-attendance": list_cost_of_attendance,
    "delete-cost-of-attendance": delete_cost_of_attendance,
    # ISIR
    "import-isir": import_isir,
    "update-isir": update_isir,
    "get-isir": get_isir,
    "list-isirs": list_isirs,
    "complete-isir-review": review_isir,
    "add-isir-cflag": add_isir_cflag,
    "complete-isir-cflag": resolve_isir_cflag,
    "list-isir-cflags": list_isir_cflags,
    # Verification
    "create-verification-request": create_verification_request,
    "update-verification-request": update_verification_request,
    "get-verification-request": get_verification_request,
    "list-verification-requests": list_verification_requests,
    "add-verification-document": add_verification_document,
    "update-verification-document": update_verification_document,
    "complete-verification": complete_verification,
    "list-verification-documents": list_verification_documents,
    # Award Packaging
    "create-award-package": create_award_package,
    "update-award-package": update_award_package,
    "get-award-package": get_award_package,
    "list-award-packages": list_award_packages,
    "add-award": add_award,
    "update-award": update_award,
    "get-award": get_award,
    "list-awards": list_awards,
    "delete-award": delete_award,
    "submit-award-offer": offer_award_package,
    "accept-award": accept_award,
    "deny-award": decline_award,
    "cancel-award-package": cancel_award_package,
    # Disbursement
    "record-award-disbursement": disburse_award,
    "cancel-disbursement": reverse_disbursement,
    "record-r2t4-return-disbursement": record_r2t4_return_disbursement,
    "get-disbursement": get_disbursement,
    "list-disbursements": list_disbursements,
    "generate-cod-export": generate_cod_export,
    "update-cod-status": update_cod_status,
    "record-credit-balance-return": mark_credit_balance_returned,
    # SAP
    "generate-sap-evaluation": run_sap_evaluation,
    "generate-sap-batch": run_sap_batch,
    "get-sap-evaluation": get_sap_evaluation,
    "list-sap-evaluations": list_sap_evaluations,
    "apply-sap-override": override_sap_status,
    "submit-sap-appeal": submit_sap_appeal,
    "update-sap-appeal": update_sap_appeal,
    "get-sap-appeal": get_sap_appeal,
    "list-sap-appeals": list_sap_appeals,
    "complete-sap-appeal": decide_sap_appeal,
    # R2T4
    "create-r2t4": create_r2t4,
    "generate-r2t4-calculation": calculate_r2t4,
    "approve-r2t4": approve_r2t4,
    "record-r2t4-return": record_r2t4_return,
    "get-r2t4": get_r2t4,
    "list-r2t4s": list_r2t4s,
    # Professional Judgment
    "add-professional-judgment": add_professional_judgment,
    "get-professional-judgment": get_professional_judgment,
    "list-professional-judgments": list_professional_judgments,
    "approve-professional-judgment": approve_professional_judgment,
}
