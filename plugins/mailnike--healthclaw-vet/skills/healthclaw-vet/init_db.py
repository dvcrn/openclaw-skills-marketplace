"""HealthClaw Vet — schema initialization.

Creates 4 vet-specific tables in the shared ERPClaw database.
Requires healthclaw core tables to exist (patient FK references).
"""
import os
import sqlite3
import sys

DB_PATH = os.environ.get("ERPCLAW_DB_PATH", os.path.expanduser("~/.openclaw/erpclaw/data.sqlite"))


def init_vet_schema(db_path: str = DB_PATH) -> dict:
    """Create vet expansion tables and indexes."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")

    tables_created = 0
    indexes_created = 0

    # -----------------------------------------------------------------------
    # 1. healthclaw_animal_patient — vet-specific patient extension
    # -----------------------------------------------------------------------
    conn.execute("""
        CREATE TABLE IF NOT EXISTS healthclaw_animal_patient (
            id                  TEXT PRIMARY KEY,
            company_id          TEXT NOT NULL REFERENCES company(id),
            patient_id          TEXT NOT NULL REFERENCES healthclaw_patient(id),
            species             TEXT NOT NULL
                                CHECK(species IN ('canine','feline','equine','avian','reptile','small_mammal','other')),
            breed               TEXT,
            color               TEXT,
            weight_kg           TEXT,
            microchip_id        TEXT,
            spay_neuter_status  TEXT DEFAULT 'unknown'
                                CHECK(spay_neuter_status IN ('intact','spayed','neutered','unknown')),
            reproductive_status TEXT,
            created_at          TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    tables_created += 1

    conn.execute("CREATE INDEX IF NOT EXISTS idx_animal_patient_company ON healthclaw_animal_patient(company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_animal_patient_patient ON healthclaw_animal_patient(patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_animal_patient_species ON healthclaw_animal_patient(species)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_animal_patient_microchip ON healthclaw_animal_patient(microchip_id)")
    indexes_created += 4

    # -----------------------------------------------------------------------
    # 2. healthclaw_boarding — boarding/kennel management
    # -----------------------------------------------------------------------
    conn.execute("""
        CREATE TABLE IF NOT EXISTS healthclaw_boarding (
            id                      TEXT PRIMARY KEY,
            company_id              TEXT NOT NULL REFERENCES company(id),
            animal_patient_id       TEXT NOT NULL REFERENCES healthclaw_animal_patient(id),
            check_in_date           TEXT NOT NULL,
            check_out_date          TEXT,
            kennel_number           TEXT,
            feeding_instructions    TEXT,
            medication_schedule     TEXT,
            special_needs           TEXT,
            daily_rate              TEXT,
            status                  TEXT NOT NULL DEFAULT 'checked_in'
                                    CHECK(status IN ('reserved','checked_in','checked_out','cancelled')),
            notes                   TEXT,
            created_at              TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at              TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    tables_created += 1

    conn.execute("CREATE INDEX IF NOT EXISTS idx_boarding_company ON healthclaw_boarding(company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_boarding_animal ON healthclaw_boarding(animal_patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_boarding_status ON healthclaw_boarding(status)")
    indexes_created += 3

    # -----------------------------------------------------------------------
    # 3. healthclaw_weight_dosing — weight-based medication dosing records
    # -----------------------------------------------------------------------
    conn.execute("""
        CREATE TABLE IF NOT EXISTS healthclaw_weight_dosing (
            id                  TEXT PRIMARY KEY,
            company_id          TEXT NOT NULL REFERENCES company(id),
            animal_patient_id   TEXT NOT NULL REFERENCES healthclaw_animal_patient(id),
            weight_date         TEXT NOT NULL,
            weight_kg           TEXT NOT NULL,
            medication_name     TEXT NOT NULL,
            dose_per_kg         TEXT NOT NULL,
            calculated_dose     TEXT NOT NULL,
            dose_unit           TEXT DEFAULT 'mg',
            route               TEXT CHECK(route IN ('oral','injectable','topical','ophthalmic','otic','other')),
            frequency           TEXT,
            notes               TEXT,
            created_at          TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    tables_created += 1

    conn.execute("CREATE INDEX IF NOT EXISTS idx_weight_dosing_company ON healthclaw_weight_dosing(company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_weight_dosing_animal ON healthclaw_weight_dosing(animal_patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_weight_dosing_medication ON healthclaw_weight_dosing(medication_name)")
    indexes_created += 3

    # -----------------------------------------------------------------------
    # 4. healthclaw_owner_link — animal-to-owner relationship records
    # -----------------------------------------------------------------------
    conn.execute("""
        CREATE TABLE IF NOT EXISTS healthclaw_owner_link (
            id                          TEXT PRIMARY KEY,
            company_id                  TEXT NOT NULL REFERENCES company(id),
            animal_patient_id           TEXT NOT NULL REFERENCES healthclaw_animal_patient(id),
            owner_name                  TEXT NOT NULL,
            owner_phone                 TEXT,
            owner_email                 TEXT,
            relationship                TEXT NOT NULL DEFAULT 'owner'
                                        CHECK(relationship IN ('owner','co_owner','caretaker','breeder','foster')),
            is_primary                  INTEGER NOT NULL DEFAULT 0,
            financial_responsibility    INTEGER NOT NULL DEFAULT 1,
            notes                       TEXT,
            created_at                  TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at                  TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    tables_created += 1

    conn.execute("CREATE INDEX IF NOT EXISTS idx_owner_link_company ON healthclaw_owner_link(company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_owner_link_animal ON healthclaw_owner_link(animal_patient_id)")
    indexes_created += 2

    conn.commit()
    conn.close()

    return {
        "database": db_path,
        "tables": tables_created,
        "indexes": indexes_created,
    }


if __name__ == "__main__":
    result = init_vet_schema()
    print(f"HealthClaw Vet schema created in {result['database']}", file=sys.stderr)
    print(f"  Tables: {result['tables']}", file=sys.stderr)
    print(f"  Indexes: {result['indexes']}", file=sys.stderr)
