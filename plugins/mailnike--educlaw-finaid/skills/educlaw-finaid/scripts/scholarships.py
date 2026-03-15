"""EduClaw Financial Aid — scholarships domain module

Actions: add-scholarship-program, update-scholarship-program, get-scholarship-program,
list-scholarship-programs, terminate-scholarship-program, generate-scholarship-matches,
submit-scholarship-application, update-scholarship-application, get-scholarship-application,
list-scholarship-applications, complete-scholarship-review, approve-scholarship-application,
deny-scholarship-application, generate-scholarship-renewal, list-scholarship-renewals

Imported by scripts/db_query.py (unified router).
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
    from erpclaw_lib.naming import get_next_name
    from erpclaw_lib.response import ok, err, row_to_dict, rows_to_list
    from erpclaw_lib.audit import audit
except ImportError:
    pass

SKILL = "educlaw-finaid"

_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
_today = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# ACTION: add-scholarship-program
# ---------------------------------------------------------------------------

def add_scholarship_program(conn, args):
    """Insert a new scholarship program definition."""
    company_id        = getattr(args, "company_id", None) or None
    name              = getattr(args, "name", None) or None
    code              = getattr(args, "code", None) or None
    scholarship_type  = getattr(args, "scholarship_type", None) or None
    funding_source    = getattr(args, "funding_source", None) or None
    award_method      = getattr(args, "award_method", None) or None
    award_amount_type = getattr(args, "award_amount_type", None) or None
    award_period      = getattr(args, "award_period", None) or None
    applies_to_aid_type = getattr(args, "applies_to_aid_type", None) or None

    if not company_id:
        return err("--company-id is required")
    if not name:
        return err("--name is required")
    if not code:
        return err("--code is required")
    if not scholarship_type:
        return err("--scholarship-type is required")
    if not funding_source:
        return err("--funding-source is required")
    if not award_method:
        return err("--award-method is required")
    if not award_amount_type:
        return err("--award-amount-type is required")
    if not award_period:
        return err("--award-period is required")
    if not applies_to_aid_type:
        return err("--applies-to-aid-type is required")

    # Optional fields
    description              = getattr(args, "description", None) or ""
    award_amount_raw         = getattr(args, "award_amount", None) or "0"
    min_award_raw            = getattr(args, "min_award", None) or "0"
    max_award_raw            = getattr(args, "max_award", None) or "0"
    annual_budget_raw        = getattr(args, "annual_budget", None) or "0"
    max_recipients           = int(getattr(args, "max_recipients", None) or 0)
    renewal_eligible         = int(bool(getattr(args, "renewal_eligible", None) or 0))
    renewal_gpa_minimum_raw  = getattr(args, "renewal_gpa_minimum", None) or "0"
    renewal_credits_min_raw  = getattr(args, "renewal_credits_minimum", None) or "0"
    eligibility_criteria_raw = getattr(args, "eligibility_criteria", None) or "{}"
    application_deadline     = getattr(args, "application_deadline", None) or ""
    gl_account_id            = getattr(args, "gl_account_id", None) or ""
    created_by               = getattr(args, "user_id", None) or ""

    # Validate / normalise Decimal fields
    try:
        award_amount        = str(round_currency(to_decimal(award_amount_raw)))
        min_award           = str(round_currency(to_decimal(min_award_raw)))
        max_award           = str(round_currency(to_decimal(max_award_raw)))
        annual_budget       = str(round_currency(to_decimal(annual_budget_raw)))
        budget_remaining    = annual_budget
        renewal_gpa_minimum = str(to_decimal(renewal_gpa_minimum_raw))
        renewal_credits_min = str(to_decimal(renewal_credits_min_raw))
    except Exception as exc:
        return err(f"Invalid numeric value: {exc}")

    # Validate eligibility_criteria is valid JSON
    try:
        json.loads(eligibility_criteria_raw)
    except (ValueError, TypeError):
        return err("--eligibility-criteria must be valid JSON")

    now = _now_iso()
    program_id = str(uuid.uuid4())

    try:
        conn.execute(
            """INSERT INTO finaid_scholarship_program
               (id, name, code, description, scholarship_type, funding_source,
                award_method, award_amount_type, award_amount, min_award, max_award,
                annual_budget, budget_remaining, max_recipients, renewal_eligible,
                renewal_gpa_minimum, renewal_credits_minimum, eligibility_criteria,
                application_deadline, award_period, applies_to_aid_type,
                gl_account_id, is_active, company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1,
                       ?, ?, ?, ?)""",
            (program_id, name, code, description, scholarship_type, funding_source,
             award_method, award_amount_type, award_amount, min_award, max_award,
             annual_budget, budget_remaining, max_recipients, renewal_eligible,
             renewal_gpa_minimum, renewal_credits_min, eligibility_criteria_raw,
             application_deadline, award_period, applies_to_aid_type,
             gl_account_id, company_id, now, now, created_by)
        )
    except sqlite3.IntegrityError as exc:
        if "UNIQUE" in str(exc).upper():
            return err(f"Duplicate: scholarship program with code '{code}' already exists for this company")
        return err(str(exc))

    conn.commit()
    audit(conn, SKILL, "add-scholarship-program", "finaid_scholarship_program",
          program_id, description=f"Created scholarship program {name} ({code})")
    return ok({
        "id": program_id,
        "name": name,
        "code": code,
        "award_method": award_method,
        "is_active": 1,
        "message": "Scholarship program created",
    })


ACTIONS = {}
ACTIONS["add-scholarship-program"] = add_scholarship_program


# ---------------------------------------------------------------------------
# ACTION: update-scholarship-program
# ---------------------------------------------------------------------------

def update_scholarship_program(conn, args):
    """Update an existing scholarship program."""
    program_id = getattr(args, "id", None) or None
    if not program_id:
        return err("--id is required")

    row = conn.execute(
        "SELECT * FROM finaid_scholarship_program WHERE id = ?", (program_id,)
    ).fetchone()
    if not row:
        return err(f"Scholarship program {program_id} not found")

    existing = row_to_dict(row)
    updates = {}

    for field in ["name", "description", "min_award", "max_award",
                  "max_recipients", "eligibility_criteria",
                  "application_deadline", "award_period", "gl_account_id"]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    # renewal fields
    for field in ["renewal_eligible"]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = int(bool(val))

    # Decimal fields
    for dec_field in ["award_amount", "renewal_gpa_minimum", "renewal_credits_minimum"]:
        val = getattr(args, dec_field, None)
        if val is not None:
            try:
                updates[dec_field] = str(to_decimal(val))
            except Exception as exc:
                return err(f"Invalid value for {dec_field}: {exc}")

    for curr_field in ["min_award", "max_award"]:
        if curr_field in updates:
            try:
                updates[curr_field] = str(round_currency(to_decimal(updates[curr_field])))
            except Exception as exc:
                return err(f"Invalid value for {curr_field}: {exc}")

    # annual_budget — recompute budget_remaining
    annual_budget_raw = getattr(args, "annual_budget", None)
    if annual_budget_raw is not None:
        try:
            new_budget = round_currency(to_decimal(annual_budget_raw))
            old_budget = round_currency(to_decimal(existing.get("annual_budget", "0")))
            old_remaining = round_currency(to_decimal(existing.get("budget_remaining", "0")))
            # delta already spent = old_budget - old_remaining
            spent = old_budget - old_remaining
            new_remaining = new_budget - spent
            updates["annual_budget"] = str(new_budget)
            updates["budget_remaining"] = str(new_remaining)
        except Exception as exc:
            return err(f"Invalid annual_budget value: {exc}")

    # eligibility_criteria — validate JSON
    if "eligibility_criteria" in updates:
        try:
            json.loads(updates["eligibility_criteria"])
        except (ValueError, TypeError):
            return err("--eligibility-criteria must be valid JSON")

    if not updates:
        return err("No fields provided to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    try:
        conn.execute(
            f"UPDATE finaid_scholarship_program SET {set_clause} WHERE id = ?",
            list(updates.values()) + [program_id]
        )
    except sqlite3.IntegrityError as exc:
        return err(f"Duplicate: {exc}")

    conn.commit()
    audit(conn, SKILL, "update-scholarship-program", "finaid_scholarship_program", program_id)
    return ok({"id": program_id, "message": "Scholarship program updated"})


ACTIONS["update-scholarship-program"] = update_scholarship_program


# ---------------------------------------------------------------------------
# ACTION: get-scholarship-program
# ---------------------------------------------------------------------------

def get_scholarship_program(conn, args):
    """Retrieve a single scholarship program by id."""
    program_id = getattr(args, "id", None) or None
    if not program_id:
        return err("--id is required")

    row = conn.execute(
        "SELECT * FROM finaid_scholarship_program WHERE id = ?", (program_id,)
    ).fetchone()
    if not row:
        return err(f"Scholarship program {program_id} not found")

    return ok(row_to_dict(row))


ACTIONS["get-scholarship-program"] = get_scholarship_program


# ---------------------------------------------------------------------------
# ACTION: list-scholarship-programs
# ---------------------------------------------------------------------------

def list_scholarship_programs(conn, args):
    """List scholarship programs with optional filters."""
    company_id      = getattr(args, "company_id", None) or None
    scholarship_type = getattr(args, "scholarship_type", None) or None
    is_active       = getattr(args, "is_active", None)
    funding_source  = getattr(args, "funding_source", None) or None
    limit           = getattr(args, "limit", None) or 50
    offset          = getattr(args, "offset", None) or 0

    if not company_id:
        return err("--company-id is required")

    query  = "SELECT * FROM finaid_scholarship_program WHERE company_id = ?"
    params = [company_id]

    if scholarship_type:
        query += " AND scholarship_type = ?"
        params.append(scholarship_type)
    if is_active is not None:
        query += " AND is_active = ?"
        params.append(int(bool(is_active)))
    if funding_source:
        query += " AND funding_source = ?"
        params.append(funding_source)

    query += " ORDER BY name ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()
    return ok({"programs": rows_to_list(rows), "count": len(rows)})


ACTIONS["list-scholarship-programs"] = list_scholarship_programs


# ---------------------------------------------------------------------------
# ACTION: deactivate-scholarship-program
# ---------------------------------------------------------------------------

def deactivate_scholarship_program(conn, args):
    """Set is_active=0 on a scholarship program."""
    program_id = getattr(args, "id", None) or None
    if not program_id:
        return err("--id is required")

    row = conn.execute(
        "SELECT id, is_active FROM finaid_scholarship_program WHERE id = ?", (program_id,)
    ).fetchone()
    if not row:
        return err(f"Scholarship program {program_id} not found")

    conn.execute(
        "UPDATE finaid_scholarship_program SET is_active = 0, updated_at = ? WHERE id = ?",
        (_now_iso(), program_id)
    )
    conn.commit()
    audit(conn, SKILL, "deactivate-scholarship-program", "finaid_scholarship_program",
          program_id, description="Program deactivated")
    return ok({"id": program_id, "is_active": 0, "message": "Scholarship program deactivated"})


ACTIONS["deactivate-scholarship-program"] = deactivate_scholarship_program


# ---------------------------------------------------------------------------
# ACTION: auto-match-scholarships
# ---------------------------------------------------------------------------

def auto_match_scholarships(conn, args):
    """Auto-match students to scholarship programs for a given aid year.

    Finds all active auto_match programs for the company, then finds students
    who have an active award package for the aid year and do not already have
    an award from each program.  Creates a finaid_award line for each new match.
    """
    company_id  = getattr(args, "company_id", None) or None
    aid_year_id = getattr(args, "aid_year_id", None) or None
    created_by  = getattr(args, "user_id", None) or ""

    if not company_id:
        return err("--company-id is required")
    if not aid_year_id:
        return err("--aid-year-id is required")

    # Validate aid_year_id
    if not conn.execute(
        "SELECT id FROM finaid_aid_year WHERE id = ?", (aid_year_id,)
    ).fetchone():
        return err(f"Aid year {aid_year_id} not found")

    # Find all auto_match programs that are active
    programs = conn.execute(
        """SELECT * FROM finaid_scholarship_program
           WHERE company_id = ? AND award_method = 'auto_match' AND is_active = 1""",
        (company_id,)
    ).fetchall()

    if not programs:
        return ok({"matches_created": 0, "message": "No active auto-match programs found"})

    # Find all students who have an award package for this aid year
    packages = conn.execute(
        """SELECT id AS award_package_id, student_id, academic_term_id
           FROM finaid_award_package
           WHERE company_id = ? AND aid_year_id = ?""",
        (company_id, aid_year_id)
    ).fetchall()

    if not packages:
        return ok({"matches_created": 0, "message": "No award packages found for this aid year"})

    now = _now_iso()
    matches_created = 0
    match_details = []

    for program in programs:
        prog = row_to_dict(program)
        program_id       = prog["id"]
        applies_to_aid_type = prog["applies_to_aid_type"]
        award_amount     = prog.get("award_amount", "0")

        for pkg in packages:
            pkg_dict     = row_to_dict(pkg)
            student_id   = pkg_dict["student_id"]
            package_id   = pkg_dict["award_package_id"]
            term_id      = pkg_dict.get("academic_term_id", "")

            # Check if student already has an award from this program
            existing_award = conn.execute(
                """SELECT id FROM finaid_award
                   WHERE award_package_id = ? AND fund_source_id = ?""",
                (package_id, program_id)
            ).fetchone()
            if existing_award:
                continue

            # Create a finaid_award line
            award_id = str(uuid.uuid4())
            try:
                conn.execute(
                    """INSERT INTO finaid_award
                       (id, award_package_id, student_id, aid_year_id, academic_term_id,
                        aid_type, aid_source, fund_source_id, offered_amount, accepted_amount,
                        disbursed_amount, acceptance_status, acceptance_date,
                        disbursement_holds, is_locked, gl_account_id, notes,
                        company_id, created_at, updated_at, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, 'institutional', ?, ?, '0', '0',
                               'pending', '', '[]', 0, ?, '', ?, ?, ?, ?)""",
                    (award_id, package_id, student_id, aid_year_id, term_id or "",
                     applies_to_aid_type, program_id, award_amount,
                     prog.get("gl_account_id", ""),
                     company_id, now, now, created_by)
                )
                matches_created += 1
                match_details.append({
                    "award_id": award_id,
                    "student_id": student_id,
                    "scholarship_program_id": program_id,
                    "award_package_id": package_id,
                    "offered_amount": award_amount,
                })
            except sqlite3.IntegrityError:
                # Skip duplicates that slipped through
                continue

    conn.commit()
    if matches_created:
        audit(conn, SKILL, "auto-match-scholarships", "finaid_award",
              company_id, description=f"Auto-matched {matches_created} scholarships for aid year {aid_year_id}")

    return ok({
        "matches_created": matches_created,
        "aid_year_id": aid_year_id,
        "programs_evaluated": len(programs),
        "matches": match_details,
        "message": f"Auto-match complete: {matches_created} award(s) created",
    })


ACTIONS["auto-match-scholarships"] = auto_match_scholarships


# ---------------------------------------------------------------------------
# ACTION: submit-scholarship-application
# ---------------------------------------------------------------------------

def submit_scholarship_application(conn, args):
    """Submit a student application for a scholarship program."""
    scholarship_program_id = getattr(args, "scholarship_program_id", None) or None
    student_id             = getattr(args, "student_id", None) or None
    aid_year_id            = getattr(args, "aid_year_id", None) or None
    company_id             = getattr(args, "company_id", None) or None

    if not scholarship_program_id:
        return err("--scholarship-program-id is required")
    if not student_id:
        return err("--student-id is required")
    if not aid_year_id:
        return err("--aid-year-id is required")
    if not company_id:
        return err("--company-id is required")

    # Validate references
    if not conn.execute(
        "SELECT id FROM finaid_scholarship_program WHERE id = ?", (scholarship_program_id,)
    ).fetchone():
        return err(f"Scholarship program {scholarship_program_id} not found")

    if not conn.execute(
        "SELECT id FROM educlaw_student WHERE id = ?", (student_id,)
    ).fetchone():
        return err(f"Student {student_id} not found")

    if not conn.execute(
        "SELECT id FROM finaid_aid_year WHERE id = ?", (aid_year_id,)
    ).fetchone():
        return err(f"Aid year {aid_year_id} not found")

    # Optional fields
    essay_response      = getattr(args, "essay_response", None) or ""
    gpa_raw             = getattr(args, "gpa_at_application", None) or "0"
    submission_date     = getattr(args, "submission_date", None) or _today()
    created_by          = getattr(args, "user_id", None) or ""

    try:
        gpa_at_application = str(to_decimal(gpa_raw))
    except Exception as exc:
        return err(f"Invalid gpa_at_application value: {exc}")

    now = _now_iso()
    application_id = str(uuid.uuid4())

    try:
        conn.execute(
            """INSERT INTO finaid_scholarship_application
               (id, scholarship_program_id, student_id, aid_year_id, submission_date,
                status, essay_response, gpa_at_application, reviewer_id, review_date,
                review_notes, award_amount, award_term_id, denial_reason,
                company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, 'submitted', ?, ?, '', '', '', '0', NULL, '',
                       ?, ?, ?, ?)""",
            (application_id, scholarship_program_id, student_id, aid_year_id,
             submission_date, essay_response, gpa_at_application,
             company_id, now, now, created_by)
        )
    except sqlite3.IntegrityError as exc:
        if "UNIQUE" in str(exc).upper():
            return err(
                "Duplicate: an application from this student for this program and aid year already exists"
            )
        return err(str(exc))

    conn.commit()
    audit(conn, SKILL, "submit-scholarship-application", "finaid_scholarship_application",
          application_id,
          description=f"Application submitted for program {scholarship_program_id} by student {student_id}")
    return ok({
        "id": application_id,
        "scholarship_program_id": scholarship_program_id,
        "student_id": student_id,
        "aid_year_id": aid_year_id,
        "status": "submitted",
        "submission_date": submission_date,
        "message": "Scholarship application submitted",
    })


ACTIONS["submit-scholarship-application"] = submit_scholarship_application


# ---------------------------------------------------------------------------
# ACTION: update-scholarship-application
# ---------------------------------------------------------------------------

def update_scholarship_application(conn, args):
    """Update essay response or GPA on an existing application."""
    application_id = getattr(args, "id", None) or None
    if not application_id:
        return err("--id is required")

    row = conn.execute(
        "SELECT * FROM finaid_scholarship_application WHERE id = ?", (application_id,)
    ).fetchone()
    if not row:
        return err(f"Scholarship application {application_id} not found")

    updates = {}

    essay_response = getattr(args, "essay_response", None)
    if essay_response is not None:
        updates["essay_response"] = essay_response

    gpa_raw = getattr(args, "gpa_at_application", None)
    if gpa_raw is not None:
        try:
            updates["gpa_at_application"] = str(to_decimal(gpa_raw))
        except Exception as exc:
            return err(f"Invalid gpa_at_application value: {exc}")

    if not updates:
        return err("No fields provided to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE finaid_scholarship_application SET {set_clause} WHERE id = ?",
        list(updates.values()) + [application_id]
    )
    conn.commit()
    audit(conn, SKILL, "update-scholarship-application",
          "finaid_scholarship_application", application_id)
    return ok({"id": application_id, "message": "Scholarship application updated"})


ACTIONS["update-scholarship-application"] = update_scholarship_application


# ---------------------------------------------------------------------------
# ACTION: get-scholarship-application
# ---------------------------------------------------------------------------

def get_scholarship_application(conn, args):
    """Retrieve a single scholarship application by id."""
    application_id = getattr(args, "id", None) or None
    if not application_id:
        return err("--id is required")

    row = conn.execute(
        "SELECT * FROM finaid_scholarship_application WHERE id = ?", (application_id,)
    ).fetchone()
    if not row:
        return err(f"Scholarship application {application_id} not found")

    return ok(row_to_dict(row))


ACTIONS["get-scholarship-application"] = get_scholarship_application


# ---------------------------------------------------------------------------
# ACTION: list-scholarship-applications
# ---------------------------------------------------------------------------

def list_scholarship_applications(conn, args):
    """List scholarship applications with optional filters."""
    company_id             = getattr(args, "company_id", None) or None
    scholarship_program_id = getattr(args, "scholarship_program_id", None) or None
    status                 = getattr(args, "status", None) or None
    aid_year_id            = getattr(args, "aid_year_id", None) or None
    reviewer_id            = getattr(args, "reviewer_id", None) or None
    limit                  = getattr(args, "limit", None) or 50
    offset                 = getattr(args, "offset", None) or 0

    if not company_id:
        return err("--company-id is required")

    query  = "SELECT * FROM finaid_scholarship_application WHERE company_id = ?"
    params = [company_id]

    if scholarship_program_id:
        query += " AND scholarship_program_id = ?"
        params.append(scholarship_program_id)
    if status:
        query += " AND status = ?"
        params.append(status)
    if aid_year_id:
        query += " AND aid_year_id = ?"
        params.append(aid_year_id)
    if reviewer_id:
        query += " AND reviewer_id = ?"
        params.append(reviewer_id)

    query += " ORDER BY submission_date DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()
    return ok({"applications": rows_to_list(rows), "count": len(rows)})


ACTIONS["list-scholarship-applications"] = list_scholarship_applications


# ---------------------------------------------------------------------------
# ACTION: review-scholarship-application
# ---------------------------------------------------------------------------

def review_scholarship_application(conn, args):
    """Assign a reviewer and mark the application as under_review."""
    application_id = getattr(args, "id", None) or None
    reviewer_id    = getattr(args, "reviewer_id", None) or None

    if not application_id:
        return err("--id is required")
    if not reviewer_id:
        return err("--reviewer-id is required")

    row = conn.execute(
        "SELECT * FROM finaid_scholarship_application WHERE id = ?", (application_id,)
    ).fetchone()
    if not row:
        return err(f"Scholarship application {application_id} not found")

    review_notes = getattr(args, "review_notes", None) or ""
    review_date  = _today()
    now          = _now_iso()

    conn.execute(
        """UPDATE finaid_scholarship_application
           SET status = 'under_review', reviewer_id = ?, review_date = ?,
               review_notes = ?, updated_at = ?
           WHERE id = ?""",
        (reviewer_id, review_date, review_notes, now, application_id)
    )
    conn.commit()
    audit(conn, SKILL, "review-scholarship-application",
          "finaid_scholarship_application", application_id,
          description=f"Assigned reviewer {reviewer_id}")
    return ok({
        "id": application_id,
        "status": "under_review",
        "reviewer_id": reviewer_id,
        "review_date": review_date,
        "message": "Application marked as under review",
    })


ACTIONS["review-scholarship-application"] = review_scholarship_application


# ---------------------------------------------------------------------------
# ACTION: award-scholarship-application
# ---------------------------------------------------------------------------

def award_scholarship_application(conn, args):
    """Award a scholarship application and decrement program budget_remaining."""
    application_id = getattr(args, "id", None) or None
    award_amount_raw = getattr(args, "award_amount", None) or None

    if not application_id:
        return err("--id is required")
    if award_amount_raw is None:
        return err("--award-amount is required")

    try:
        award_amount = round_currency(to_decimal(award_amount_raw))
    except Exception as exc:
        return err(f"Invalid award_amount: {exc}")

    row = conn.execute(
        "SELECT * FROM finaid_scholarship_application WHERE id = ?", (application_id,)
    ).fetchone()
    if not row:
        return err(f"Scholarship application {application_id} not found")

    app = row_to_dict(row)
    award_term_id = getattr(args, "award_term_id", None) or None
    now = _now_iso()

    # Update the application
    conn.execute(
        """UPDATE finaid_scholarship_application
           SET status = 'awarded', award_amount = ?, award_term_id = ?, updated_at = ?
           WHERE id = ?""",
        (str(award_amount), award_term_id, now, application_id)
    )

    # Decrement budget_remaining on the scholarship program
    prog_row = conn.execute(
        "SELECT id, budget_remaining FROM finaid_scholarship_program WHERE id = ?",
        (app["scholarship_program_id"],)
    ).fetchone()
    if prog_row:
        try:
            current_remaining = round_currency(to_decimal(prog_row["budget_remaining"] or "0"))
            new_remaining = current_remaining - award_amount
            conn.execute(
                "UPDATE finaid_scholarship_program SET budget_remaining = ?, updated_at = ? WHERE id = ?",
                (str(new_remaining), now, prog_row["id"])
            )
        except Exception:
            # Non-fatal: budget tracking failure should not block award
            pass

    conn.commit()
    audit(conn, SKILL, "award-scholarship-application",
          "finaid_scholarship_application", application_id,
          description=f"Awarded ${award_amount}")
    return ok({
        "id": application_id,
        "status": "awarded",
        "award_amount": str(award_amount),
        "message": "Scholarship application awarded",
    })


ACTIONS["award-scholarship-application"] = award_scholarship_application


# ---------------------------------------------------------------------------
# ACTION: deny-scholarship-application
# ---------------------------------------------------------------------------

def deny_scholarship_application(conn, args):
    """Deny a scholarship application."""
    application_id = getattr(args, "id", None) or None
    if not application_id:
        return err("--id is required")

    row = conn.execute(
        "SELECT id FROM finaid_scholarship_application WHERE id = ?", (application_id,)
    ).fetchone()
    if not row:
        return err(f"Scholarship application {application_id} not found")

    denial_reason = getattr(args, "denial_reason", None) or ""
    now = _now_iso()

    conn.execute(
        """UPDATE finaid_scholarship_application
           SET status = 'denied', denial_reason = ?, updated_at = ?
           WHERE id = ?""",
        (denial_reason, now, application_id)
    )
    conn.commit()
    audit(conn, SKILL, "deny-scholarship-application",
          "finaid_scholarship_application", application_id,
          description="Application denied")
    return ok({
        "id": application_id,
        "status": "denied",
        "denial_reason": denial_reason,
        "message": "Scholarship application denied",
    })


ACTIONS["deny-scholarship-application"] = deny_scholarship_application


# ---------------------------------------------------------------------------
# ACTION: evaluate-scholarship-renewal
# ---------------------------------------------------------------------------

def evaluate_scholarship_renewal(conn, args):
    """Evaluate end-of-term scholarship renewal eligibility for a student.

    Checks GPA and credits against the program's renewal thresholds.
    Inserts a finaid_scholarship_renewal record.
    UNIQUE(scholarship_application_id, academic_term_id).
    """
    scholarship_application_id = getattr(args, "scholarship_application_id", None) or None
    academic_term_id            = getattr(args, "academic_term_id", None) or None
    company_id                  = getattr(args, "company_id", None) or None
    gpa_raw                     = getattr(args, "gpa_at_evaluation", None) or None
    credits_raw                 = getattr(args, "credits_attempted", None) or None

    if not scholarship_application_id:
        return err("--scholarship-application-id is required")
    if not academic_term_id:
        return err("--academic-term-id is required")
    if not company_id:
        return err("--company-id is required")
    if gpa_raw is None:
        return err("--gpa-at-evaluation is required")
    if credits_raw is None:
        return err("--credits-attempted is required")

    # Optional (but "required optional" per spec)
    student_id            = getattr(args, "student_id", None) or ""
    scholarship_program_id = getattr(args, "scholarship_program_id", None) or ""
    evaluated_by          = getattr(args, "evaluated_by", None) or ""

    # Validate references
    app_row = conn.execute(
        "SELECT * FROM finaid_scholarship_application WHERE id = ?",
        (scholarship_application_id,)
    ).fetchone()
    if not app_row:
        return err(f"Scholarship application {scholarship_application_id} not found")

    app = row_to_dict(app_row)

    # Resolve program_id from application if not provided
    resolved_program_id = scholarship_program_id or app.get("scholarship_program_id", "")
    # Resolve student_id from application if not provided
    resolved_student_id = student_id or app.get("student_id", "")

    # Validate academic term
    if not conn.execute(
        "SELECT id FROM educlaw_academic_term WHERE id = ?", (academic_term_id,)
    ).fetchone():
        return err(f"Academic term {academic_term_id} not found")

    # Validate GPA and credits
    try:
        gpa_at_evaluation = to_decimal(gpa_raw)
    except Exception as exc:
        return err(f"Invalid gpa_at_evaluation: {exc}")

    try:
        credits_attempted = int(credits_raw)
    except (ValueError, TypeError):
        return err("--credits-attempted must be an integer")

    # Fetch program renewal thresholds
    prog_row = conn.execute(
        "SELECT renewal_gpa_minimum, renewal_credits_minimum FROM finaid_scholarship_program WHERE id = ?",
        (resolved_program_id,)
    ).fetchone() if resolved_program_id else None

    gpa_minimum     = to_decimal(prog_row["renewal_gpa_minimum"]     or "0") if prog_row else to_decimal("0")
    credits_minimum = to_decimal(prog_row["renewal_credits_minimum"] or "0") if prog_row else to_decimal("0")

    gpa_met     = gpa_at_evaluation >= gpa_minimum
    credits_met = to_decimal(str(credits_attempted)) >= credits_minimum
    meets_criteria = 1 if (gpa_met and credits_met) else 0
    renewal_status = "renewed" if meets_criteria else "suspended"

    # Build reason string
    reasons = []
    if not gpa_met:
        reasons.append(f"GPA {gpa_at_evaluation} below minimum {gpa_minimum}")
    if not credits_met:
        reasons.append(f"Credits {credits_attempted} below minimum {credits_minimum}")
    reason = "; ".join(reasons) if reasons else "All renewal criteria met"

    now = _now_iso()
    renewal_id = str(uuid.uuid4())

    try:
        conn.execute(
            """INSERT INTO finaid_scholarship_renewal
               (id, scholarship_application_id, student_id, scholarship_program_id,
                academic_term_id, renewal_status, gpa_at_evaluation, credits_attempted,
                meets_criteria, reason, evaluated_by, evaluation_date,
                company_id, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (renewal_id, scholarship_application_id, resolved_student_id,
             resolved_program_id, academic_term_id, renewal_status,
             str(gpa_at_evaluation), credits_attempted, meets_criteria,
             reason, evaluated_by, _today(),
             company_id, now, now)
        )
    except sqlite3.IntegrityError as exc:
        if "UNIQUE" in str(exc).upper():
            return err(
                "Duplicate: a renewal evaluation for this application and term already exists"
            )
        return err(str(exc))

    conn.commit()
    audit(conn, SKILL, "evaluate-scholarship-renewal",
          "finaid_scholarship_renewal", renewal_id,
          description=f"Renewal evaluation: {renewal_status} for application {scholarship_application_id}")
    return ok({
        "id": renewal_id,
        "scholarship_application_id": scholarship_application_id,
        "student_id": resolved_student_id,
        "scholarship_program_id": resolved_program_id,
        "academic_term_id": academic_term_id,
        "renewal_status": renewal_status,
        "meets_criteria": meets_criteria,
        "gpa_at_evaluation": str(gpa_at_evaluation),
        "credits_attempted": credits_attempted,
        "reason": reason,
        "message": f"Renewal evaluated: {renewal_status}",
    })


ACTIONS["evaluate-scholarship-renewal"] = evaluate_scholarship_renewal


# ---------------------------------------------------------------------------
# ACTION: list-scholarship-renewals
# ---------------------------------------------------------------------------

def list_scholarship_renewals(conn, args):
    """List scholarship renewal evaluations with optional filters."""
    company_id             = getattr(args, "company_id", None) or None
    scholarship_program_id = getattr(args, "scholarship_program_id", None) or None
    student_id             = getattr(args, "student_id", None) or None
    academic_term_id       = getattr(args, "academic_term_id", None) or None
    renewal_status         = getattr(args, "renewal_status", None) or None
    limit                  = getattr(args, "limit", None) or 50
    offset                 = getattr(args, "offset", None) or 0

    if not company_id:
        return err("--company-id is required")

    query  = "SELECT * FROM finaid_scholarship_renewal WHERE company_id = ?"
    params = [company_id]

    if scholarship_program_id:
        query += " AND scholarship_program_id = ?"
        params.append(scholarship_program_id)
    if student_id:
        query += " AND student_id = ?"
        params.append(student_id)
    if academic_term_id:
        query += " AND academic_term_id = ?"
        params.append(academic_term_id)
    if renewal_status:
        query += " AND renewal_status = ?"
        params.append(renewal_status)

    query += " ORDER BY evaluation_date DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()
    return ok({"renewals": rows_to_list(rows), "count": len(rows)})


# ---------------------------------------------------------------------------
# ACTIONS registry
# ---------------------------------------------------------------------------
ACTIONS = {
    "add-scholarship-program": add_scholarship_program,
    "update-scholarship-program": update_scholarship_program,
    "get-scholarship-program": get_scholarship_program,
    "list-scholarship-programs": list_scholarship_programs,
    "terminate-scholarship-program": deactivate_scholarship_program,
    "generate-scholarship-matches": auto_match_scholarships,
    "submit-scholarship-application": submit_scholarship_application,
    "update-scholarship-application": update_scholarship_application,
    "get-scholarship-application": get_scholarship_application,
    "list-scholarship-applications": list_scholarship_applications,
    "complete-scholarship-review": review_scholarship_application,
    "approve-scholarship-application": award_scholarship_application,
    "deny-scholarship-application": deny_scholarship_application,
    "generate-scholarship-renewal": evaluate_scholarship_renewal,
    "list-scholarship-renewals": list_scholarship_renewals,
}
