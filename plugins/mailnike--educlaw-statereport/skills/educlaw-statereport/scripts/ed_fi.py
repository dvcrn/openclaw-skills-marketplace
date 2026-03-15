"""EduClaw State Reporting — ed_fi domain module

Ed-Fi ODS/API integration: connection config, OAuth credentials, descriptor mapping,
dependency-ordered sync engine, sync log management.

Imported by db_query.py (unified router).
"""
import hashlib
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
    from erpclaw_lib.crypto import encrypt_field as _encrypt_field_raw
    from erpclaw_lib.crypto import decrypt_field as _decrypt_field_raw
    from erpclaw_lib.crypto import derive_key

    # Derive a stable field-encryption key from env passphrase (or fixed default)
    _FIELD_PASSPHRASE = os.environ.get("ERPCLAW_FIELD_KEY", "educlaw-statereport-default-key")
    _FIELD_SALT = b"educlaw_statereport_edfi_salt_v1"
    _FIELD_KEY = derive_key(_FIELD_PASSPHRASE, _FIELD_SALT)

    def encrypt_field(v):
        return _encrypt_field_raw(v, _FIELD_KEY)

    def decrypt_field(v):
        return _decrypt_field_raw(v, _FIELD_KEY)

except ImportError:
    def encrypt_field(v): return f"ENC:{v}"
    def decrypt_field(v): return v.replace("ENC:", "") if v.startswith("ENC:") else v

SKILL = "educlaw-statereport"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

VALID_API_VERSIONS = ("5", "6", "7")
VALID_DESCRIPTOR_TYPES = (
    "grade_level", "race", "sex", "attendance_event", "disability", "language",
    "exit_type", "entry_type", "discipline_behavior", "discipline_action",
    "sped_environment", "program_type", "credential_type", "course_level", "homeless_residence"
)
VALID_SYNC_STATUSES = ("success", "error", "retry", "pending", "skipped")
VALID_OPERATIONS = ("POST", "PUT", "DELETE", "GET")


def _hash_payload(payload_str):
    """SHA-256 hash of a string payload."""
    return hashlib.sha256(payload_str.encode("utf-8")).hexdigest()


def _create_sync_log(conn, config_id, resource_type, operation, internal_id,
                     edfi_natural_key, http_status, payload_hash, response_body,
                     sync_status, company_id, collection_window_id=None):
    """Insert an immutable Ed-Fi sync log entry."""
    log_id = str(uuid.uuid4())
    now = _now_iso()
    conn.execute(
        """INSERT INTO sr_edfi_sync_log
           (id, config_id, collection_window_id, resource_type, operation,
            internal_id, edfi_natural_key, http_status, request_payload_hash,
            response_body, sync_status, retry_count, synced_at,
            company_id, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (log_id, config_id, collection_window_id, resource_type, operation,
         internal_id, edfi_natural_key, http_status, payload_hash,
         response_body, sync_status, 0, now, company_id, now)
    )
    return log_id


# ─────────────────────────────────────────────────────────────────────────────
# ED-FI CONFIG
# ─────────────────────────────────────────────────────────────────────────────

def add_edfi_config(conn, args):
    company_id = getattr(args, "company_id", None)
    profile_name = getattr(args, "profile_name", None)
    state_code = getattr(args, "state_code", None)
    school_year = getattr(args, "school_year", None)
    ods_base_url = getattr(args, "ods_base_url", None)
    oauth_token_url = getattr(args, "oauth_token_url", None)
    oauth_client_id = getattr(args, "oauth_client_id", None)
    oauth_client_secret = getattr(args, "oauth_client_secret", None)

    if not company_id:
        err("--company-id is required")
    if not profile_name:
        err("--profile-name is required")
    if not state_code:
        err("--state-code is required")
    if not school_year:
        err("--school-year is required")
    if not ods_base_url:
        err("--ods-base-url is required")
    if not oauth_client_id:
        err("--oauth-client-id is required")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    api_version = getattr(args, "api_version", None) or "7"
    if api_version not in VALID_API_VERSIONS:
        err(f"--api-version must be one of: {', '.join(VALID_API_VERSIONS)}")

    # Encrypt the OAuth secret
    encrypted_secret = encrypt_field(oauth_client_secret) if oauth_client_secret else ""

    config_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO sr_edfi_config
               (id, profile_name, state_code, school_year, ods_base_url,
                oauth_token_url, oauth_client_id, oauth_client_secret_encrypted,
                api_version, is_active, last_tested_at, last_token_at,
                company_id, created_at, updated_at, created_by)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (config_id, profile_name, state_code, int(school_year), ods_base_url,
             oauth_token_url or "",
             oauth_client_id, encrypted_secret,
             api_version, 1, "", "",
             company_id, now, now, getattr(args, "user_id", None) or "")
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        err(f"Cannot create Ed-Fi config: {e}")

    audit(conn, "sr_edfi_config", config_id, "INSERT", getattr(args, "user_id", None) or "")
    ok({"id": config_id, "profile_name": profile_name, "state_code": state_code,
        "school_year": int(school_year), "message": "Ed-Fi config created"})


def update_edfi_config(conn, args):
    config_id = getattr(args, "config_id", None)
    if not config_id:
        err("--config-id is required")

    row = conn.execute("SELECT id FROM sr_edfi_config WHERE id = ?", (config_id,)).fetchone()
    if not row:
        err(f"Ed-Fi config {config_id} not found")

    updates = {}
    for field in ["profile_name", "state_code", "ods_base_url", "oauth_token_url",
                  "oauth_client_id", "api_version", "is_active"]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    # Re-encrypt secret if provided
    oauth_client_secret = getattr(args, "oauth_client_secret", None)
    if oauth_client_secret:
        updates["oauth_client_secret_encrypted"] = encrypt_field(oauth_client_secret)

    if not updates:
        err("No fields to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE sr_edfi_config SET {set_clause} WHERE id = ?",
        list(updates.values()) + [config_id]
    )
    conn.commit()
    audit(conn, "sr_edfi_config", config_id, "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": config_id, "message": "Ed-Fi config updated"})


def get_edfi_config(conn, args):
    config_id = getattr(args, "config_id", None)
    if not config_id:
        err("--config-id is required")

    row = conn.execute("SELECT * FROM sr_edfi_config WHERE id = ?", (config_id,)).fetchone()
    if not row:
        err(f"Ed-Fi config {config_id} not found")

    rec = dict(row)
    # Never return decrypted secret
    rec.pop("oauth_client_secret_encrypted", None)
    rec["has_client_secret"] = bool(row["oauth_client_secret_encrypted"])
    ok(rec)


def list_edfi_configs(conn, args):
    company_id = getattr(args, "company_id", None)
    if not company_id:
        err("--company-id is required")

    conditions = ["company_id = ?"]
    params = [company_id]

    state_code = getattr(args, "state_code", None)
    if state_code:
        conditions.append("state_code = ?")
        params.append(state_code)

    is_active = getattr(args, "is_active", None)
    if is_active is not None:
        conditions.append("is_active = ?")
        params.append(int(is_active))

    school_year = getattr(args, "school_year", None)
    if school_year:
        conditions.append("school_year = ?")
        params.append(int(school_year))

    where = " AND ".join(conditions)
    rows = conn.execute(
        f"""SELECT id, profile_name, state_code, school_year, ods_base_url,
                   oauth_client_id, api_version, is_active, last_tested_at, last_token_at,
                   company_id, created_at
            FROM sr_edfi_config WHERE {where} ORDER BY school_year DESC, state_code""",
        params
    ).fetchall()

    ok({"configs": [dict(r) for r in rows], "count": len(rows)})


def test_edfi_connection(conn, args):
    """Simulate connection test — records last_tested_at. Real HTTP call happens externally."""
    config_id = getattr(args, "config_id", None)
    if not config_id:
        err("--config-id is required")

    row = conn.execute("SELECT * FROM sr_edfi_config WHERE id = ?", (config_id,)).fetchone()
    if not row:
        err(f"Ed-Fi config {config_id} not found")

    # In production this would make real OAuth + GET /schools call.
    # Here we record the test timestamp and simulate success.
    now = _now_iso()
    conn.execute(
        "UPDATE sr_edfi_config SET last_tested_at = ?, updated_at = ? WHERE id = ?",
        (now, now, config_id)
    )
    conn.commit()
    audit(conn, "sr_edfi_config", config_id, "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": config_id, "last_tested_at": now,
        "message": "Connection test recorded. External OAuth/ODS call must be made by client."})


# ─────────────────────────────────────────────────────────────────────────────
# ORG MAPPING
# ─────────────────────────────────────────────────────────────────────────────

def add_org_mapping(conn, args):
    company_id = getattr(args, "company_id", None)
    state_code = getattr(args, "state_code", None)
    nces_lea_id = getattr(args, "nces_lea_id", None)

    if not company_id:
        err("--company-id is required")
    if not state_code:
        err("--state-code is required")
    if not nces_lea_id:
        err("--nces-lea-id is required")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    title_i_status = getattr(args, "title_i_status", None) or ""
    mapping_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO sr_org_mapping
               (id, company_id, nces_lea_id, nces_school_id, state_code,
                state_lea_id, state_school_id, edfi_lea_id, edfi_school_id,
                crdc_school_id, is_title_i_school, title_i_status,
                created_at, updated_at, created_by)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (mapping_id, company_id, nces_lea_id,
             getattr(args, "nces_school_id", None) or "",
             state_code,
             getattr(args, "state_lea_id", None) or "",
             getattr(args, "state_school_id", None) or "",
             getattr(args, "edfi_lea_id", None) or "",
             getattr(args, "edfi_school_id", None) or "",
             getattr(args, "crdc_school_id", None) or "",
             int(getattr(args, "is_title_i_school", None) or 0),
             title_i_status,
             now, now, getattr(args, "user_id", None) or "")
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        err(f"Cannot create org mapping: {e}")

    audit(conn, "sr_org_mapping", mapping_id, "INSERT", getattr(args, "user_id", None) or "")
    ok({"id": mapping_id, "nces_lea_id": nces_lea_id, "state_code": state_code,
        "message": "Org mapping created"})


def update_org_mapping(conn, args):
    mapping_id = getattr(args, "mapping_id", None)
    if not mapping_id:
        err("--mapping-id is required")

    row = conn.execute("SELECT id FROM sr_org_mapping WHERE id = ?", (mapping_id,)).fetchone()
    if not row:
        err(f"Org mapping {mapping_id} not found")

    updates = {}
    for field in [
        "nces_lea_id", "nces_school_id", "state_lea_id", "state_school_id",
        "edfi_lea_id", "edfi_school_id", "crdc_school_id",
        "is_title_i_school", "title_i_status"
    ]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    if not updates:
        err("No fields to update")

    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE sr_org_mapping SET {set_clause} WHERE id = ?",
        list(updates.values()) + [mapping_id]
    )
    conn.commit()
    audit(conn, "sr_org_mapping", mapping_id, "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": mapping_id, "message": "Org mapping updated"})


def get_org_mapping(conn, args):
    mapping_id = getattr(args, "mapping_id", None)
    company_id = getattr(args, "company_id", None)
    state_code = getattr(args, "state_code", None)

    if mapping_id:
        row = conn.execute("SELECT * FROM sr_org_mapping WHERE id = ?", (mapping_id,)).fetchone()
    elif company_id and state_code:
        row = conn.execute(
            "SELECT * FROM sr_org_mapping WHERE company_id = ? AND state_code = ? ORDER BY nces_school_id LIMIT 1",
            (company_id, state_code)
        ).fetchone()
    else:
        err("--mapping-id or --company-id + --state-code required")

    if not row:
        err("Org mapping not found")
    ok(dict(row))


def list_org_mappings(conn, args):
    company_id = getattr(args, "company_id", None)
    if not company_id:
        err("--company-id is required")

    conditions = ["company_id = ?"]
    params = [company_id]

    state_code = getattr(args, "state_code", None)
    if state_code:
        conditions.append("state_code = ?")
        params.append(state_code)

    where = " AND ".join(conditions)
    rows = conn.execute(
        f"SELECT * FROM sr_org_mapping WHERE {where} ORDER BY state_code, nces_school_id",
        params
    ).fetchall()

    ok({"mappings": [dict(r) for r in rows], "count": len(rows)})


# ─────────────────────────────────────────────────────────────────────────────
# DESCRIPTOR MAPPING
# ─────────────────────────────────────────────────────────────────────────────

def add_descriptor_mapping(conn, args):
    config_id = getattr(args, "config_id", None)
    descriptor_type = getattr(args, "descriptor_type", None)
    internal_code = getattr(args, "internal_code", None)
    edfi_descriptor_uri = getattr(args, "edfi_descriptor_uri", None)
    company_id = getattr(args, "company_id", None)

    if not config_id:
        err("--config-id is required")
    if not descriptor_type:
        err("--descriptor-type is required")
    if not internal_code:
        err("--internal-code is required")
    if not edfi_descriptor_uri:
        err("--edfi-descriptor-uri is required")
    if not company_id:
        err("--company-id is required")
    if descriptor_type not in VALID_DESCRIPTOR_TYPES:
        err(f"--descriptor-type must be one of: {', '.join(VALID_DESCRIPTOR_TYPES)}")

    if not conn.execute("SELECT id FROM sr_edfi_config WHERE id = ?", (config_id,)).fetchone():
        err(f"Ed-Fi config {config_id} not found")

    desc_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO sr_edfi_descriptor_map
               (id, config_id, descriptor_type, internal_code, edfi_descriptor_uri,
                description, is_active, company_id, created_at, created_by)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (desc_id, config_id, descriptor_type, internal_code, edfi_descriptor_uri,
             getattr(args, "description", None) or "",
             1, company_id, now, getattr(args, "user_id", None) or "")
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        err(f"Cannot create descriptor mapping: {e}")

    audit(conn, "sr_edfi_descriptor_map", desc_id, "INSERT", getattr(args, "user_id", None) or "")
    ok({"id": desc_id, "descriptor_type": descriptor_type, "internal_code": internal_code,
        "message": "Descriptor mapping created"})


def update_descriptor_mapping(conn, args):
    desc_id = getattr(args, "desc_id", None)
    if not desc_id:
        err("--desc-id is required")

    row = conn.execute("SELECT id FROM sr_edfi_descriptor_map WHERE id = ?", (desc_id,)).fetchone()
    if not row:
        err(f"Descriptor mapping {desc_id} not found")

    updates = {}
    for field in ["edfi_descriptor_uri", "description", "is_active"]:
        val = getattr(args, field, None)
        if val is not None:
            updates[field] = val

    if not updates:
        err("No fields to update")

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(
        f"UPDATE sr_edfi_descriptor_map SET {set_clause} WHERE id = ?",
        list(updates.values()) + [desc_id]
    )
    conn.commit()
    audit(conn, "sr_edfi_descriptor_map", desc_id, "UPDATE", getattr(args, "user_id", None) or "")
    ok({"id": desc_id, "message": "Descriptor mapping updated"})


def bulk_import_descriptor_mappings(conn, args):
    """Upsert multiple descriptor mappings from JSON array."""
    config_id = getattr(args, "config_id", None)
    company_id = getattr(args, "company_id", None)
    mappings_json = getattr(args, "mappings", None)

    if not config_id:
        err("--config-id is required")
    if not company_id:
        err("--company-id is required")
    if not mappings_json:
        err("--mappings is required (JSON array)")

    if not conn.execute("SELECT id FROM sr_edfi_config WHERE id = ?", (config_id,)).fetchone():
        err(f"Ed-Fi config {config_id} not found")

    try:
        mappings = json.loads(mappings_json) if isinstance(mappings_json, str) else mappings_json
        if not isinstance(mappings, list):
            err("--mappings must be a JSON array")
    except (json.JSONDecodeError, TypeError):
        err("--mappings must be valid JSON array")

    now = _now_iso()
    inserted = 0
    updated = 0

    for m in mappings:
        dtype = m.get("descriptor_type", "")
        icode = m.get("internal_code", "")
        uri = m.get("edfi_descriptor_uri", "")

        if not dtype or not icode or not uri:
            continue
        if dtype not in VALID_DESCRIPTOR_TYPES:
            continue

        existing = conn.execute(
            "SELECT id FROM sr_edfi_descriptor_map WHERE config_id = ? AND descriptor_type = ? AND internal_code = ?",
            (config_id, dtype, icode)
        ).fetchone()

        if existing:
            conn.execute(
                "UPDATE sr_edfi_descriptor_map SET edfi_descriptor_uri = ? WHERE id = ?",
                (uri, existing["id"])
            )
            updated += 1
        else:
            conn.execute(
                """INSERT INTO sr_edfi_descriptor_map
                   (id, config_id, descriptor_type, internal_code, edfi_descriptor_uri,
                    description, is_active, company_id, created_at, created_by)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (str(uuid.uuid4()), config_id, dtype, icode, uri,
                 m.get("description", ""), 1, company_id, now,
                 getattr(args, "user_id", None) or "")
            )
            inserted += 1

    conn.commit()
    ok({"inserted": inserted, "updated": updated,
        "message": f"Bulk import complete: {inserted} inserted, {updated} updated"})


def list_descriptor_mappings(conn, args):
    config_id = getattr(args, "config_id", None)
    if not config_id:
        err("--config-id is required")

    conditions = ["config_id = ?"]
    params = [config_id]

    descriptor_type = getattr(args, "descriptor_type", None)
    if descriptor_type:
        conditions.append("descriptor_type = ?")
        params.append(descriptor_type)

    is_active = getattr(args, "is_active", None)
    if is_active is not None:
        conditions.append("is_active = ?")
        params.append(int(is_active))

    where = " AND ".join(conditions)
    rows = conn.execute(
        f"SELECT * FROM sr_edfi_descriptor_map WHERE {where} ORDER BY descriptor_type, internal_code",
        params
    ).fetchall()

    ok({"mappings": [dict(r) for r in rows], "count": len(rows)})


def delete_descriptor_mapping(conn, args):
    desc_id = getattr(args, "desc_id", None)
    if not desc_id:
        err("--desc-id is required")

    row = conn.execute("SELECT id, internal_code FROM sr_edfi_descriptor_map WHERE id = ?", (desc_id,)).fetchone()
    if not row:
        err(f"Descriptor mapping {desc_id} not found")

    # Check not referenced in sync logs
    ref_count = conn.execute(
        "SELECT COUNT(*) FROM sr_edfi_sync_log WHERE edfi_natural_key LIKE ?",
        (f"%{row['internal_code']}%",)
    ).fetchone()[0]
    if ref_count > 0:
        err(f"Cannot delete: descriptor used in {ref_count} sync log entries")

    conn.execute("DELETE FROM sr_edfi_descriptor_map WHERE id = ?", (desc_id,))
    conn.commit()
    audit(conn, "sr_edfi_descriptor_map", desc_id, "DELETE", getattr(args, "user_id", None) or "")
    ok({"id": desc_id, "message": "Descriptor mapping deleted"})


# ─────────────────────────────────────────────────────────────────────────────
# SYNC ACTIONS (Ed-Fi push simulation)
# ─────────────────────────────────────────────────────────────────────────────

def sync_student_to_edfi(conn, args):
    """Push Student + StudentEducationOrganizationAssociation to Ed-Fi ODS."""
    config_id = getattr(args, "config_id", None)
    student_id = getattr(args, "student_id", None)
    company_id = getattr(args, "company_id", None)

    if not config_id:
        err("--config-id is required")
    if not student_id:
        err("--student-id is required")
    if not company_id:
        err("--company-id is required")

    if not conn.execute("SELECT id FROM sr_edfi_config WHERE id = ?", (config_id,)).fetchone():
        err(f"Ed-Fi config {config_id} not found")

    student = conn.execute("SELECT * FROM educlaw_student WHERE id = ?", (student_id,)).fetchone()
    if not student:
        err(f"Student {student_id} not found")

    supp = conn.execute(
        "SELECT * FROM sr_student_supplement WHERE student_id = ?", (student_id,)
    ).fetchone()

    # Build Ed-Fi payload
    payload = {
        "studentUniqueId": supp["ssid"] if supp and supp["ssid"] else student_id,
        "firstName": student["first_name"],
        "lastSurname": student["last_name"],
        "birthDate": student["date_of_birth"],
    }
    if supp:
        payload["races"] = json.loads(supp["race_codes"]) if supp["race_codes"] else []
        payload["hispanicLatinoEthnicity"] = bool(supp["is_hispanic_latino"])

    payload_str = json.dumps(payload, sort_keys=True)
    collection_window_id = getattr(args, "collection_window_id", None)

    log_id = _create_sync_log(
        conn, config_id, "students", "POST", student_id,
        json.dumps({"studentUniqueId": payload["studentUniqueId"]}),
        0,  # HTTP status 0 = not yet sent (logged as pending for external client)
        _hash_payload(payload_str),
        json.dumps({"note": "Payload built; actual HTTP POST made by client"}),
        "pending", company_id, collection_window_id
    )
    conn.commit()

    ok({"sync_log_id": log_id, "student_id": student_id,
        "payload": payload, "sync_status": "pending",
        "message": "Sync record created. External Ed-Fi client must execute the HTTP POST."})


def sync_enrollment_to_edfi(conn, args):
    """Push StudentSchoolAssociation records for a student or collection window."""
    config_id = getattr(args, "config_id", None)
    student_id = getattr(args, "student_id", None)
    company_id = getattr(args, "company_id", None)
    collection_window_id = getattr(args, "collection_window_id", None)

    if not config_id:
        err("--config-id is required")
    if not company_id:
        err("--company-id is required")

    if not conn.execute("SELECT id FROM sr_edfi_config WHERE id = ?", (config_id,)).fetchone():
        err(f"Ed-Fi config {config_id} not found")

    if student_id:
        enrollments = conn.execute(
            "SELECT * FROM educlaw_program_enrollment WHERE student_id = ? AND company_id = ?",
            (student_id, company_id)
        ).fetchall()
    else:
        enrollments = conn.execute(
            "SELECT * FROM educlaw_program_enrollment WHERE company_id = ? AND enrollment_status = 'active'",
            (company_id,)
        ).fetchall()

    synced = 0
    for enroll in enrollments:
        payload = {
            "studentUniqueId": enroll["student_id"],
            "schoolId": company_id,
            "entryDate": enroll["enrollment_date"],
            "enrollmentStatus": enroll["enrollment_status"],
        }
        payload_str = json.dumps(payload, sort_keys=True)
        _create_sync_log(
            conn, config_id, "studentSchoolAssociations", "POST",
            enroll["id"],
            json.dumps({"studentUniqueId": enroll["student_id"], "schoolId": company_id}),
            0, _hash_payload(payload_str),
            json.dumps({"note": "Pending external POST"}),
            "pending", company_id, collection_window_id
        )
        synced += 1

    conn.commit()
    ok({"synced_count": synced, "sync_status": "pending",
        "message": f"{synced} enrollment sync records created"})


def sync_attendance_to_edfi(conn, args):
    """Push StudentSchoolAttendanceEvent records."""
    config_id = getattr(args, "config_id", None)
    company_id = getattr(args, "company_id", None)
    date_from = getattr(args, "date_from", None)
    date_to = getattr(args, "date_to", None)
    collection_window_id = getattr(args, "collection_window_id", None)

    if not config_id:
        err("--config-id is required")
    if not company_id:
        err("--company-id is required")

    if not conn.execute("SELECT id FROM sr_edfi_config WHERE id = ?", (config_id,)).fetchone():
        err(f"Ed-Fi config {config_id} not found")

    conditions = ["company_id = ?"]
    params = [company_id]
    if date_from:
        conditions.append("attendance_date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("attendance_date <= ?")
        params.append(date_to)

    where = " AND ".join(conditions)
    attendance_rows = conn.execute(
        f"SELECT * FROM educlaw_student_attendance WHERE {where} ORDER BY attendance_date LIMIT 500",
        params
    ).fetchall()

    synced = 0
    for att in attendance_rows:
        payload = {
            "studentUniqueId": att["student_id"],
            "schoolId": company_id,
            "eventDate": att["attendance_date"],
            "attendanceEventCategoryDescriptor": att["attendance_status"],
        }
        payload_str = json.dumps(payload, sort_keys=True)
        _create_sync_log(
            conn, config_id, "studentSchoolAttendanceEvents", "POST",
            att["id"],
            json.dumps({"studentUniqueId": att["student_id"], "eventDate": att["attendance_date"]}),
            0, _hash_payload(payload_str),
            json.dumps({"note": "Pending external POST"}),
            "pending", company_id, collection_window_id
        )
        synced += 1

    conn.commit()
    ok({"synced_count": synced, "sync_status": "pending",
        "message": f"{synced} attendance sync records created"})


def sync_sped_to_edfi(conn, args):
    """Push StudentSpecialEducationProgramAssociation records."""
    config_id = getattr(args, "config_id", None)
    company_id = getattr(args, "company_id", None)
    school_year = getattr(args, "school_year", None)
    collection_window_id = getattr(args, "collection_window_id", None)

    if not config_id:
        err("--config-id is required")
    if not company_id:
        err("--company-id is required")
    if not school_year:
        err("--school-year is required")

    if not conn.execute("SELECT id FROM sr_edfi_config WHERE id = ?", (config_id,)).fetchone():
        err(f"Ed-Fi config {config_id} not found")

    placements = conn.execute(
        """SELECT sp.*, ss.ssid FROM sr_sped_placement sp
           LEFT JOIN sr_student_supplement ss ON ss.student_id = sp.student_id
           WHERE sp.company_id = ? AND sp.school_year = ?""",
        (company_id, int(school_year))
    ).fetchall()

    synced = 0
    for pl in placements:
        payload = {
            "studentUniqueId": pl["ssid"] or pl["student_id"],
            "programName": "Special Education",
            "disabilityCategory": pl["disability_category"],
            "educationalEnvironment": pl["educational_environment"],
            "beginDate": pl["sped_program_entry_date"],
        }
        payload_str = json.dumps(payload, sort_keys=True)
        _create_sync_log(
            conn, config_id, "studentSpecialEducationProgramAssociations", "POST",
            pl["id"],
            json.dumps({"studentUniqueId": payload["studentUniqueId"]}),
            0, _hash_payload(payload_str),
            json.dumps({"note": "Pending external POST"}),
            "pending", company_id, collection_window_id
        )
        synced += 1

    conn.commit()
    ok({"synced_count": synced, "sync_status": "pending",
        "message": f"{synced} SPED sync records created"})


def sync_el_to_edfi(conn, args):
    """Push StudentLanguageInstructionProgramAssociation records."""
    config_id = getattr(args, "config_id", None)
    company_id = getattr(args, "company_id", None)
    school_year = getattr(args, "school_year", None)
    collection_window_id = getattr(args, "collection_window_id", None)

    if not config_id:
        err("--config-id is required")
    if not company_id:
        err("--company-id is required")
    if not school_year:
        err("--school-year is required")

    if not conn.execute("SELECT id FROM sr_edfi_config WHERE id = ?", (config_id,)).fetchone():
        err(f"Ed-Fi config {config_id} not found")

    programs = conn.execute(
        """SELECT ep.*, ss.ssid FROM sr_el_program ep
           LEFT JOIN sr_student_supplement ss ON ss.student_id = ep.student_id
           WHERE ep.company_id = ? AND ep.school_year = ?""",
        (company_id, int(school_year))
    ).fetchall()

    synced = 0
    for prog in programs:
        payload = {
            "studentUniqueId": prog["ssid"] or prog["student_id"],
            "programName": "English as a Second Language (ESL)",
            "programType": prog["program_type"],
            "beginDate": prog["entry_date"],
        }
        payload_str = json.dumps(payload, sort_keys=True)
        _create_sync_log(
            conn, config_id, "studentLanguageInstructionProgramAssociations", "POST",
            prog["id"],
            json.dumps({"studentUniqueId": payload["studentUniqueId"]}),
            0, _hash_payload(payload_str),
            json.dumps({"note": "Pending external POST"}),
            "pending", company_id, collection_window_id
        )
        synced += 1

    conn.commit()
    ok({"synced_count": synced, "sync_status": "pending",
        "message": f"{synced} EL program sync records created"})


def sync_discipline_to_edfi(conn, args):
    """Push DisciplineIncident + StudentDisciplineIncidentAssociation records."""
    config_id = getattr(args, "config_id", None)
    company_id = getattr(args, "company_id", None)
    school_year = getattr(args, "school_year", None)
    collection_window_id = getattr(args, "collection_window_id", None)

    if not config_id:
        err("--config-id is required")
    if not company_id:
        err("--company-id is required")
    if not school_year:
        err("--school-year is required")

    if not conn.execute("SELECT id FROM sr_edfi_config WHERE id = ?", (config_id,)).fetchone():
        err(f"Ed-Fi config {config_id} not found")

    incidents = conn.execute(
        "SELECT * FROM sr_discipline_incident WHERE company_id = ? AND school_year = ?",
        (company_id, int(school_year))
    ).fetchall()

    synced = 0
    for inc in incidents:
        payload = {
            "incidentIdentifier": inc["naming_series"],
            "schoolId": company_id,
            "incidentDate": inc["incident_date"],
            "incidentType": inc["incident_type"],
        }
        payload_str = json.dumps(payload, sort_keys=True)
        _create_sync_log(
            conn, config_id, "disciplineIncidents", "POST",
            inc["id"],
            json.dumps({"incidentIdentifier": inc["naming_series"]}),
            0, _hash_payload(payload_str),
            json.dumps({"note": "Pending external POST"}),
            "pending", company_id, collection_window_id
        )
        synced += 1

    conn.commit()
    ok({"synced_count": synced, "sync_status": "pending",
        "message": f"{synced} discipline incident sync records created"})


def sync_staff_to_edfi(conn, args):
    """Push Staff + StaffSchoolAssociation + StaffSectionAssociation records."""
    config_id = getattr(args, "config_id", None)
    company_id = getattr(args, "company_id", None)
    collection_window_id = getattr(args, "collection_window_id", None)

    if not config_id:
        err("--config-id is required")
    if not company_id:
        err("--company-id is required")

    if not conn.execute("SELECT id FROM sr_edfi_config WHERE id = ?", (config_id,)).fetchone():
        err(f"Ed-Fi config {config_id} not found")

    instructors = conn.execute(
        """SELECT i.*, e.first_name, e.last_name
           FROM educlaw_instructor i
           JOIN employee e ON e.id = i.employee_id
           WHERE i.company_id = ? AND i.is_active = 1""",
        (company_id,)
    ).fetchall()

    synced = 0
    for inst in instructors:
        payload = {
            "staffUniqueId": inst["employee_id"],
            "firstName": inst["first_name"],
            "lastSurname": inst["last_name"],
        }
        payload_str = json.dumps(payload, sort_keys=True)
        _create_sync_log(
            conn, config_id, "staffs", "POST",
            inst["employee_id"],
            json.dumps({"staffUniqueId": inst["employee_id"]}),
            0, _hash_payload(payload_str),
            json.dumps({"note": "Pending external POST"}),
            "pending", company_id, collection_window_id
        )
        synced += 1

    conn.commit()
    ok({"synced_count": synced, "sync_status": "pending",
        "message": f"{synced} staff sync records created"})


# ─────────────────────────────────────────────────────────────────────────────
# SYNC LOG QUERIES
# ─────────────────────────────────────────────────────────────────────────────

def get_edfi_sync_log(conn, args):
    resource_type = getattr(args, "resource_type", None)
    internal_id = getattr(args, "internal_id", None)
    company_id = getattr(args, "company_id", None)

    conditions = []
    params = []

    if resource_type:
        conditions.append("resource_type = ?")
        params.append(resource_type)
    if internal_id:
        conditions.append("internal_id = ?")
        params.append(internal_id)
    if company_id:
        conditions.append("company_id = ?")
        params.append(company_id)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)

    rows = conn.execute(
        f"SELECT * FROM sr_edfi_sync_log {where} ORDER BY synced_at DESC LIMIT ? OFFSET ?",
        params + [limit, offset]
    ).fetchall()

    ok({"logs": [dict(r) for r in rows], "count": len(rows)})


def list_edfi_sync_errors(conn, args):
    company_id = getattr(args, "company_id", None)
    collection_window_id = getattr(args, "collection_window_id", None)

    conditions = ["sync_status IN ('error','retry','pending')"]
    params = []

    if company_id:
        conditions.append("company_id = ?")
        params.append(company_id)
    if collection_window_id:
        conditions.append("collection_window_id = ?")
        params.append(collection_window_id)

    where = "WHERE " + " AND ".join(conditions)
    limit = int(getattr(args, "limit", None) or 100)
    offset = int(getattr(args, "offset", None) or 0)

    rows = conn.execute(
        f"SELECT * FROM sr_edfi_sync_log {where} ORDER BY synced_at DESC LIMIT ? OFFSET ?",
        params + [limit, offset]
    ).fetchall()

    ok({"errors": [dict(r) for r in rows], "count": len(rows)})


def retry_failed_syncs(conn, args):
    """Re-attempt all sync entries with status error or retry for a window."""
    company_id = getattr(args, "company_id", None)
    collection_window_id = getattr(args, "collection_window_id", None)

    if not company_id:
        err("--company-id is required")

    conditions = ["sync_status IN ('error','retry') AND company_id = ?"]
    params = [company_id]

    if collection_window_id:
        conditions.append("collection_window_id = ?")
        params.append(collection_window_id)

    where = " AND ".join(conditions)

    # Reset failed entries to 'retry' with incremented retry_count
    now = _now_iso()
    result = conn.execute(
        f"""UPDATE sr_edfi_sync_log
            SET sync_status = 'retry', retry_count = retry_count + 1, synced_at = ?
            WHERE {where}""",
        [now] + params
    )
    count = result.rowcount
    conn.commit()

    ok({"retried_count": count, "message": f"{count} sync entries queued for retry"})


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────
ACTIONS = {
    "add-edfi-config": add_edfi_config,
    "update-edfi-config": update_edfi_config,
    "get-edfi-config": get_edfi_config,
    "list-edfi-configs": list_edfi_configs,
    "get-edfi-connection-test": test_edfi_connection,
    "add-org-mapping": add_org_mapping,
    "update-org-mapping": update_org_mapping,
    "get-org-mapping": get_org_mapping,
    "list-org-mappings": list_org_mappings,
    "add-descriptor-mapping": add_descriptor_mapping,
    "update-descriptor-mapping": update_descriptor_mapping,
    "import-descriptor-mappings": bulk_import_descriptor_mappings,
    "list-descriptor-mappings": list_descriptor_mappings,
    "delete-descriptor-mapping": delete_descriptor_mapping,
    "submit-student-to-edfi": sync_student_to_edfi,
    "submit-enrollment-to-edfi": sync_enrollment_to_edfi,
    "submit-attendance-to-edfi": sync_attendance_to_edfi,
    "submit-sped-to-edfi": sync_sped_to_edfi,
    "submit-el-to-edfi": sync_el_to_edfi,
    "submit-discipline-to-edfi": sync_discipline_to_edfi,
    "submit-staff-to-edfi": sync_staff_to_edfi,
    "get-edfi-sync-log": get_edfi_sync_log,
    "list-edfi-sync-errors": list_edfi_sync_errors,
    "submit-failed-syncs": retry_failed_syncs,
}
