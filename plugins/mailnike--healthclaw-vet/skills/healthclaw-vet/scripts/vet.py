"""HealthClaw Vet — veterinary domain module

Actions for the vet expansion (4 tables, 12 actions).
Imported by db_query.py (unified router).
"""
import json
import os
import sys
import uuid
from decimal import Decimal

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection
    from erpclaw_lib.decimal_utils import to_decimal, round_currency
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
except ImportError:
    pass


# ---- Helpers ----------------------------------------------------------------

def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


VALID_SPECIES = ("canine", "feline", "equine", "avian", "reptile", "small_mammal", "other")
VALID_SPAY_NEUTER = ("intact", "spayed", "neutered", "unknown")
VALID_BOARDING_STATUSES = ("reserved", "checked_in", "checked_out", "cancelled")
VALID_ROUTES = ("oral", "injectable", "topical", "ophthalmic", "otic", "other")
VALID_RELATIONSHIPS = ("owner", "co_owner", "caretaker", "breeder", "foster")


def _validate_enum(val, choices, label):
    if val not in choices:
        err(f"Invalid {label}: {val}. Must be one of: {', '.join(choices)}")


# ---------------------------------------------------------------------------
# 1. add-animal-patient
# ---------------------------------------------------------------------------
def add_animal_patient(conn, args):
    if not getattr(args, "company_id", None):
        err("--company-id is required")
    if not getattr(args, "patient_id", None):
        err("--patient-id is required")
    if not getattr(args, "species", None):
        err("--species is required")

    # Validate patient exists
    if not conn.execute("SELECT id FROM healthclaw_patient WHERE id = ?", (args.patient_id,)).fetchone():
        err(f"Patient {args.patient_id} not found")

    _validate_enum(args.species, VALID_SPECIES, "species")

    spay_neuter_status = getattr(args, "spay_neuter_status", None) or "unknown"
    _validate_enum(spay_neuter_status, VALID_SPAY_NEUTER, "spay-neuter-status")

    weight_kg = getattr(args, "weight_kg", None)
    if weight_kg is not None:
        weight_kg = str(round_currency(to_decimal(weight_kg)))

    entry_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute(
        """INSERT INTO healthclaw_animal_patient
           (id, company_id, patient_id, species, breed, color, weight_kg, microchip_id,
            spay_neuter_status, reproductive_status, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (entry_id, args.company_id, args.patient_id, args.species,
         getattr(args, "breed", None), getattr(args, "color", None),
         weight_kg, getattr(args, "microchip_id", None),
         spay_neuter_status, getattr(args, "reproductive_status", None),
         now, now)
    )
    audit(conn, "healthclaw_animal_patient", entry_id, "add-animal-patient", args.company_id)
    conn.commit()
    ok({"id": entry_id, "species": args.species, "patient_id": args.patient_id})


# ---------------------------------------------------------------------------
# 2. update-animal-patient
# ---------------------------------------------------------------------------
def update_animal_patient(conn, args):
    entry_id = getattr(args, "animal_patient_id", None)
    if not entry_id:
        err("--animal-patient-id is required")
    if not conn.execute("SELECT id FROM healthclaw_animal_patient WHERE id = ?", (entry_id,)).fetchone():
        err(f"Animal patient {entry_id} not found")

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "breed": "breed", "color": "color",
        "microchip_id": "microchip_id", "reproductive_status": "reproductive_status",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            updates.append(f"{col_name} = ?"); params.append(val); changed.append(col_name)

    species = getattr(args, "species", None)
    if species:
        _validate_enum(species, VALID_SPECIES, "species")
        updates.append("species = ?"); params.append(species); changed.append("species")

    spay_neuter_status = getattr(args, "spay_neuter_status", None)
    if spay_neuter_status:
        _validate_enum(spay_neuter_status, VALID_SPAY_NEUTER, "spay-neuter-status")
        updates.append("spay_neuter_status = ?"); params.append(spay_neuter_status); changed.append("spay_neuter_status")

    weight_kg = getattr(args, "weight_kg", None)
    if weight_kg is not None:
        updates.append("weight_kg = ?")
        params.append(str(round_currency(to_decimal(weight_kg))))
        changed.append("weight_kg")

    if not updates:
        err("No fields to update")
    updates.append("updated_at = datetime('now')")
    params.append(entry_id)
    conn.execute(f"UPDATE healthclaw_animal_patient SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_animal_patient", entry_id, "update-animal-patient", getattr(args, "company_id", None))
    conn.commit()
    ok({"id": entry_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 3. get-animal-patient
# ---------------------------------------------------------------------------
def get_animal_patient(conn, args):
    entry_id = getattr(args, "animal_patient_id", None)
    if not entry_id:
        err("--animal-patient-id is required")
    row = conn.execute("SELECT * FROM healthclaw_animal_patient WHERE id = ?", (entry_id,)).fetchone()
    if not row:
        err(f"Animal patient {entry_id} not found")
    ok(row_to_dict(row))


# ---------------------------------------------------------------------------
# 4. list-animal-patients
# ---------------------------------------------------------------------------
def list_animal_patients(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "company_id", None):
        where.append("company_id = ?"); params.append(args.company_id)
    if getattr(args, "species", None):
        where.append("species = ?"); params.append(args.species)
    if getattr(args, "search", None):
        where.append("(breed LIKE ? OR color LIKE ? OR microchip_id LIKE ?)")
        s = f"%{args.search}%"
        params.extend([s, s, s])
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_animal_patient WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_animal_patient WHERE {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?", params
    ).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# 5. add-boarding
# ---------------------------------------------------------------------------
def add_boarding(conn, args):
    if not getattr(args, "company_id", None):
        err("--company-id is required")
    if not getattr(args, "animal_patient_id", None):
        err("--animal-patient-id is required")
    if not getattr(args, "check_in_date", None):
        err("--check-in-date is required")

    # Validate animal patient exists
    if not conn.execute("SELECT id FROM healthclaw_animal_patient WHERE id = ?", (args.animal_patient_id,)).fetchone():
        err(f"Animal patient {args.animal_patient_id} not found")

    daily_rate = getattr(args, "daily_rate", None)
    if daily_rate is not None:
        daily_rate = str(round_currency(to_decimal(daily_rate)))

    entry_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute(
        """INSERT INTO healthclaw_boarding
           (id, company_id, animal_patient_id, check_in_date, check_out_date, kennel_number,
            feeding_instructions, medication_schedule, special_needs, daily_rate, status, notes,
            created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'checked_in', ?, ?, ?)""",
        (entry_id, args.company_id, args.animal_patient_id, args.check_in_date,
         getattr(args, "check_out_date", None), getattr(args, "kennel_number", None),
         getattr(args, "feeding_instructions", None), getattr(args, "medication_schedule", None),
         getattr(args, "special_needs", None), daily_rate,
         getattr(args, "notes", None), now, now)
    )
    audit(conn, "healthclaw_boarding", entry_id, "add-boarding", args.company_id)
    conn.commit()
    ok({"id": entry_id, "animal_patient_id": args.animal_patient_id, "check_in_date": args.check_in_date})


# ---------------------------------------------------------------------------
# 6. update-boarding
# ---------------------------------------------------------------------------
def update_boarding(conn, args):
    entry_id = getattr(args, "boarding_id", None)
    if not entry_id:
        err("--boarding-id is required")
    if not conn.execute("SELECT id FROM healthclaw_boarding WHERE id = ?", (entry_id,)).fetchone():
        err(f"Boarding {entry_id} not found")

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "check_out_date": "check_out_date", "kennel_number": "kennel_number",
        "feeding_instructions": "feeding_instructions", "medication_schedule": "medication_schedule",
        "special_needs": "special_needs", "notes": "notes",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            updates.append(f"{col_name} = ?"); params.append(val); changed.append(col_name)

    status = getattr(args, "status", None)
    if status:
        _validate_enum(status, VALID_BOARDING_STATUSES, "status")
        updates.append("status = ?"); params.append(status); changed.append("status")

    daily_rate = getattr(args, "daily_rate", None)
    if daily_rate is not None:
        updates.append("daily_rate = ?")
        params.append(str(round_currency(to_decimal(daily_rate))))
        changed.append("daily_rate")

    if not updates:
        err("No fields to update")
    updates.append("updated_at = datetime('now')")
    params.append(entry_id)
    conn.execute(f"UPDATE healthclaw_boarding SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_boarding", entry_id, "update-boarding", getattr(args, "company_id", None))
    conn.commit()
    ok({"id": entry_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 7. list-boardings
# ---------------------------------------------------------------------------
def list_boardings(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "animal_patient_id", None):
        where.append("animal_patient_id = ?"); params.append(args.animal_patient_id)
    if getattr(args, "status", None):
        where.append("status = ?"); params.append(args.status)
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_boarding WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_boarding WHERE {where_sql} ORDER BY check_in_date DESC LIMIT ? OFFSET ?", params
    ).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# 8. calculate-dose
# ---------------------------------------------------------------------------
def calculate_dose(conn, args):
    if not getattr(args, "animal_patient_id", None):
        err("--animal-patient-id is required")
    if not getattr(args, "company_id", None):
        err("--company-id is required")
    if not getattr(args, "medication_name", None):
        err("--medication-name is required")
    if not getattr(args, "dose_per_kg", None):
        err("--dose-per-kg is required")

    # Validate animal patient exists
    row = conn.execute("SELECT * FROM healthclaw_animal_patient WHERE id = ?", (args.animal_patient_id,)).fetchone()
    if not row:
        err(f"Animal patient {args.animal_patient_id} not found")
    animal = row_to_dict(row)

    # Determine weight: use provided weight or latest from animal patient record
    weight_kg_str = getattr(args, "weight_kg", None)
    if not weight_kg_str:
        weight_kg_str = animal.get("weight_kg")
    if not weight_kg_str:
        err("No weight available. Provide --weight-kg or update the animal patient record.")

    weight_kg = to_decimal(weight_kg_str)
    dose_per_kg = to_decimal(args.dose_per_kg)
    calculated_dose = round_currency(weight_kg * dose_per_kg)

    route = getattr(args, "route", None)
    if route:
        _validate_enum(route, VALID_ROUTES, "route")

    from datetime import datetime, timezone
    weight_date = getattr(args, "weight_date", None) or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    entry_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute(
        """INSERT INTO healthclaw_weight_dosing
           (id, company_id, animal_patient_id, weight_date, weight_kg, medication_name,
            dose_per_kg, calculated_dose, dose_unit, route, frequency, notes,
            created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (entry_id, args.company_id, args.animal_patient_id, weight_date,
         str(weight_kg), args.medication_name, str(dose_per_kg), str(calculated_dose),
         getattr(args, "dose_unit", None) or "mg", route,
         getattr(args, "frequency", None), getattr(args, "notes", None),
         now, now)
    )
    audit(conn, "healthclaw_weight_dosing", entry_id, "calculate-dose", args.company_id)
    conn.commit()
    ok({
        "id": entry_id,
        "medication_name": args.medication_name,
        "weight_kg": str(weight_kg),
        "dose_per_kg": str(dose_per_kg),
        "calculated_dose": str(calculated_dose),
        "dose_unit": getattr(args, "dose_unit", None) or "mg",
    })


# ---------------------------------------------------------------------------
# 9. list-dosing-history
# ---------------------------------------------------------------------------
def list_dosing_history(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "animal_patient_id", None):
        where.append("animal_patient_id = ?"); params.append(args.animal_patient_id)
    if getattr(args, "medication_name", None):
        where.append("medication_name = ?"); params.append(args.medication_name)
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_weight_dosing WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_weight_dosing WHERE {where_sql} ORDER BY weight_date DESC LIMIT ? OFFSET ?", params
    ).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# 10. add-owner-link
# ---------------------------------------------------------------------------
def add_owner_link(conn, args):
    if not getattr(args, "company_id", None):
        err("--company-id is required")
    if not getattr(args, "animal_patient_id", None):
        err("--animal-patient-id is required")
    if not getattr(args, "owner_name", None):
        err("--owner-name is required")

    # Validate animal patient exists
    if not conn.execute("SELECT id FROM healthclaw_animal_patient WHERE id = ?", (args.animal_patient_id,)).fetchone():
        err(f"Animal patient {args.animal_patient_id} not found")

    relationship = getattr(args, "relationship", None) or "owner"
    _validate_enum(relationship, VALID_RELATIONSHIPS, "relationship")

    is_primary = int(getattr(args, "is_primary", 0))
    financial_responsibility = int(getattr(args, "financial_responsibility", 1))

    entry_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute(
        """INSERT INTO healthclaw_owner_link
           (id, company_id, animal_patient_id, owner_name, owner_phone, owner_email,
            relationship, is_primary, financial_responsibility, notes,
            created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (entry_id, args.company_id, args.animal_patient_id, args.owner_name,
         getattr(args, "owner_phone", None), getattr(args, "owner_email", None),
         relationship, is_primary, financial_responsibility,
         getattr(args, "notes", None), now, now)
    )
    audit(conn, "healthclaw_owner_link", entry_id, "add-owner-link", args.company_id)
    conn.commit()
    ok({"id": entry_id, "owner_name": args.owner_name, "animal_patient_id": args.animal_patient_id})


# ---------------------------------------------------------------------------
# 11. update-owner-link
# ---------------------------------------------------------------------------
def update_owner_link(conn, args):
    entry_id = getattr(args, "owner_link_id", None)
    if not entry_id:
        err("--owner-link-id is required")
    if not conn.execute("SELECT id FROM healthclaw_owner_link WHERE id = ?", (entry_id,)).fetchone():
        err(f"Owner link {entry_id} not found")

    updates, params, changed = [], [], []
    for arg_name, col_name in {
        "owner_name": "owner_name", "owner_phone": "owner_phone",
        "owner_email": "owner_email", "notes": "notes",
    }.items():
        val = getattr(args, arg_name, None)
        if val is not None:
            updates.append(f"{col_name} = ?"); params.append(val); changed.append(col_name)

    relationship = getattr(args, "relationship", None)
    if relationship:
        _validate_enum(relationship, VALID_RELATIONSHIPS, "relationship")
        updates.append("relationship = ?"); params.append(relationship); changed.append("relationship")

    is_primary = getattr(args, "is_primary", None)
    if is_primary is not None:
        updates.append("is_primary = ?"); params.append(int(is_primary)); changed.append("is_primary")

    financial_responsibility = getattr(args, "financial_responsibility", None)
    if financial_responsibility is not None:
        updates.append("financial_responsibility = ?"); params.append(int(financial_responsibility)); changed.append("financial_responsibility")

    if not updates:
        err("No fields to update")
    updates.append("updated_at = datetime('now')")
    params.append(entry_id)
    conn.execute(f"UPDATE healthclaw_owner_link SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, "healthclaw_owner_link", entry_id, "update-owner-link", getattr(args, "company_id", None))
    conn.commit()
    ok({"id": entry_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# 12. list-owner-links
# ---------------------------------------------------------------------------
def list_owner_links(conn, args):
    where, params = ["1=1"], []
    if getattr(args, "animal_patient_id", None):
        where.append("animal_patient_id = ?"); params.append(args.animal_patient_id)
    where_sql = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM healthclaw_owner_link WHERE {where_sql}", params).fetchone()[0]
    params.extend([args.limit, args.offset])
    rows = conn.execute(
        f"SELECT * FROM healthclaw_owner_link WHERE {where_sql} ORDER BY is_primary DESC, created_at DESC LIMIT ? OFFSET ?", params
    ).fetchall()
    ok({"rows": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": args.limit, "offset": args.offset, "has_more": (args.offset + args.limit) < total})


# ---------------------------------------------------------------------------
# Action Router
# ---------------------------------------------------------------------------
ACTIONS = {
    "add-animal-patient": add_animal_patient,
    "update-animal-patient": update_animal_patient,
    "get-animal-patient": get_animal_patient,
    "list-animal-patients": list_animal_patients,
    "add-boarding": add_boarding,
    "update-boarding": update_boarding,
    "list-boardings": list_boardings,
    "calculate-dose": calculate_dose,
    "list-dosing-history": list_dosing_history,
    "add-owner-link": add_owner_link,
    "update-owner-link": update_owner_link,
    "list-owner-links": list_owner_links,
}
