"""HealthClaw Dental — schema initialization.

Creates 4 dental-specific tables in the shared ERPClaw database.
Requires healthclaw core tables to exist (patient FK references).
"""
import os
import sqlite3
import sys

DB_PATH = os.environ.get("ERPCLAW_DB_PATH", os.path.expanduser("~/.openclaw/erpclaw/data.sqlite"))


def init_dental_schema(db_path: str = DB_PATH) -> dict:
    """Create dental expansion tables and indexes."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")

    tables_created = 0
    indexes_created = 0

    # -----------------------------------------------------------------------
    # 1. healthclaw_tooth_chart — per-tooth condition records
    # -----------------------------------------------------------------------
    conn.execute("""
        CREATE TABLE IF NOT EXISTS healthclaw_tooth_chart (
            id                  TEXT PRIMARY KEY,
            patient_id          TEXT NOT NULL REFERENCES healthclaw_patient(id),
            company_id          TEXT NOT NULL REFERENCES company(id),
            tooth_number        TEXT NOT NULL,
            tooth_system        TEXT NOT NULL DEFAULT 'universal'
                                CHECK(tooth_system IN ('universal','palmer','fdi')),
            surface             TEXT,
            condition           TEXT NOT NULL,
            condition_detail    TEXT,
            noted_date          TEXT NOT NULL,
            noted_by_id         TEXT,
            status              TEXT NOT NULL DEFAULT 'active'
                                CHECK(status IN ('active','resolved','monitoring')),
            notes               TEXT,
            created_at          TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    tables_created += 1

    conn.execute("CREATE INDEX IF NOT EXISTS idx_tooth_chart_patient ON healthclaw_tooth_chart(patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tooth_chart_company ON healthclaw_tooth_chart(company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tooth_chart_tooth ON healthclaw_tooth_chart(patient_id, tooth_number)")
    indexes_created += 3

    # -----------------------------------------------------------------------
    # 2. healthclaw_dental_procedure — CDT-coded dental procedures
    # -----------------------------------------------------------------------
    conn.execute("""
        CREATE TABLE IF NOT EXISTS healthclaw_dental_procedure (
            id                  TEXT PRIMARY KEY,
            encounter_id        TEXT NOT NULL REFERENCES healthclaw_encounter(id),
            patient_id          TEXT NOT NULL REFERENCES healthclaw_patient(id),
            company_id          TEXT NOT NULL REFERENCES company(id),
            provider_id         TEXT NOT NULL,
            cdt_code            TEXT NOT NULL,
            cdt_description     TEXT,
            tooth_number        TEXT,
            surface             TEXT,
            quadrant            TEXT CHECK(quadrant IN ('UR','UL','LR','LL', NULL)),
            procedure_date      TEXT NOT NULL,
            fee                 TEXT NOT NULL DEFAULT '0.00',
            status              TEXT NOT NULL DEFAULT 'planned'
                                CHECK(status IN ('planned','in_progress','completed','cancelled')),
            notes               TEXT,
            created_at          TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    tables_created += 1

    conn.execute("CREATE INDEX IF NOT EXISTS idx_dental_proc_encounter ON healthclaw_dental_procedure(encounter_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_dental_proc_patient ON healthclaw_dental_procedure(patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_dental_proc_company ON healthclaw_dental_procedure(company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_dental_proc_cdt ON healthclaw_dental_procedure(cdt_code)")
    indexes_created += 4

    # -----------------------------------------------------------------------
    # 3. healthclaw_treatment_plan — multi-phase dental treatment plans
    # -----------------------------------------------------------------------
    conn.execute("""
        CREATE TABLE IF NOT EXISTS healthclaw_treatment_plan (
            id                  TEXT PRIMARY KEY,
            patient_id          TEXT NOT NULL REFERENCES healthclaw_patient(id),
            company_id          TEXT NOT NULL REFERENCES company(id),
            provider_id         TEXT NOT NULL,
            plan_name           TEXT NOT NULL,
            plan_date           TEXT NOT NULL,
            phases              TEXT NOT NULL DEFAULT '[]',
            estimated_total     TEXT NOT NULL DEFAULT '0.00',
            insurance_estimate  TEXT NOT NULL DEFAULT '0.00',
            patient_estimate    TEXT NOT NULL DEFAULT '0.00',
            status              TEXT NOT NULL DEFAULT 'proposed'
                                CHECK(status IN ('proposed','accepted','in_progress','completed','cancelled')),
            notes               TEXT,
            created_at          TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    tables_created += 1

    conn.execute("CREATE INDEX IF NOT EXISTS idx_treatment_plan_patient ON healthclaw_treatment_plan(patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_treatment_plan_company ON healthclaw_treatment_plan(company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_treatment_plan_status ON healthclaw_treatment_plan(status)")
    indexes_created += 3

    # -----------------------------------------------------------------------
    # 4. healthclaw_perio_exam — 6-point periodontal probing data
    # -----------------------------------------------------------------------
    conn.execute("""
        CREATE TABLE IF NOT EXISTS healthclaw_perio_exam (
            id                  TEXT PRIMARY KEY,
            patient_id          TEXT NOT NULL REFERENCES healthclaw_patient(id),
            company_id          TEXT NOT NULL REFERENCES company(id),
            provider_id         TEXT NOT NULL,
            exam_date           TEXT NOT NULL,
            measurements        TEXT NOT NULL DEFAULT '{}',
            bleeding_sites      TEXT NOT NULL DEFAULT '[]',
            furcation_data      TEXT NOT NULL DEFAULT '{}',
            mobility_data       TEXT NOT NULL DEFAULT '{}',
            recession_data      TEXT NOT NULL DEFAULT '{}',
            plaque_score        TEXT,
            notes               TEXT,
            status              TEXT NOT NULL DEFAULT 'complete'
                                CHECK(status IN ('in_progress','complete')),
            created_at          TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    tables_created += 1

    conn.execute("CREATE INDEX IF NOT EXISTS idx_perio_exam_patient ON healthclaw_perio_exam(patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_perio_exam_company ON healthclaw_perio_exam(company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_perio_exam_date ON healthclaw_perio_exam(patient_id, exam_date)")
    indexes_created += 3

    conn.commit()
    conn.close()

    return {
        "database": db_path,
        "tables": tables_created,
        "indexes": indexes_created,
    }


if __name__ == "__main__":
    result = init_dental_schema()
    print(f"HealthClaw Dental schema created in {result['database']}", file=sys.stderr)
    print(f"  Tables: {result['tables']}", file=sys.stderr)
    print(f"  Indexes: {result['indexes']}", file=sys.stderr)
