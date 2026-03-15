"""HealthClaw Home Health — schema initialization.

Creates 4 home-health-specific tables in the shared ERPClaw database.
Requires healthclaw core tables to exist (patient FK references).
"""
import os
import sqlite3
import sys

DB_PATH = os.environ.get("ERPCLAW_DB_PATH", os.path.expanduser("~/.openclaw/erpclaw/data.sqlite"))


def init_homehealth_schema(db_path: str = DB_PATH) -> dict:
    """Create home health expansion tables and indexes."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")

    tables_created = 0
    indexes_created = 0

    # -----------------------------------------------------------------------
    # 1. healthclaw_home_visit — scheduled/completed home health visits
    # -----------------------------------------------------------------------
    conn.execute("""
        CREATE TABLE IF NOT EXISTS healthclaw_home_visit (
            id                  TEXT PRIMARY KEY,
            company_id          TEXT NOT NULL REFERENCES company(id),
            patient_id          TEXT NOT NULL REFERENCES healthclaw_patient(id),
            clinician_id        TEXT NOT NULL REFERENCES employee(id),
            visit_date          TEXT NOT NULL,
            visit_type          TEXT NOT NULL
                                CHECK(visit_type IN ('skilled_nursing','pt','ot','st','aide','msw')),
            start_time          TEXT,
            end_time            TEXT,
            travel_time_minutes INTEGER,
            mileage             TEXT,
            visit_status        TEXT NOT NULL DEFAULT 'scheduled'
                                CHECK(visit_status IN ('scheduled','in_progress','completed','missed','cancelled')),
            notes               TEXT,
            created_at          TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    tables_created += 1

    conn.execute("CREATE INDEX IF NOT EXISTS idx_home_visit_patient ON healthclaw_home_visit(patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_home_visit_company ON healthclaw_home_visit(company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_home_visit_clinician ON healthclaw_home_visit(clinician_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_home_visit_date ON healthclaw_home_visit(patient_id, visit_date)")
    indexes_created += 4

    # -----------------------------------------------------------------------
    # 2. healthclaw_care_plan — 485 care plans with certification periods
    # -----------------------------------------------------------------------
    conn.execute("""
        CREATE TABLE IF NOT EXISTS healthclaw_care_plan (
            id                          TEXT PRIMARY KEY,
            company_id                  TEXT NOT NULL REFERENCES company(id),
            patient_id                  TEXT NOT NULL REFERENCES healthclaw_patient(id),
            certifying_physician_id     TEXT REFERENCES employee(id),
            start_of_care               TEXT NOT NULL,
            certification_period_start  TEXT NOT NULL,
            certification_period_end    TEXT NOT NULL,
            frequency                   TEXT,
            goals                       TEXT,
            plan_status                 TEXT NOT NULL DEFAULT 'active'
                                        CHECK(plan_status IN ('active','on_hold','discharged','expired','recertified')),
            notes                       TEXT,
            created_at                  TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at                  TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    tables_created += 1

    conn.execute("CREATE INDEX IF NOT EXISTS idx_care_plan_patient ON healthclaw_care_plan(patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_care_plan_company ON healthclaw_care_plan(company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_care_plan_status ON healthclaw_care_plan(plan_status)")
    indexes_created += 3

    # -----------------------------------------------------------------------
    # 3. healthclaw_oasis_assessment — OASIS clinical assessments
    # -----------------------------------------------------------------------
    conn.execute("""
        CREATE TABLE IF NOT EXISTS healthclaw_oasis_assessment (
            id                  TEXT PRIMARY KEY,
            company_id          TEXT NOT NULL REFERENCES company(id),
            patient_id          TEXT NOT NULL REFERENCES healthclaw_patient(id),
            clinician_id        TEXT NOT NULL REFERENCES employee(id),
            assessment_type     TEXT NOT NULL
                                CHECK(assessment_type IN ('soc','roc','recert','transfer','discharge','followup')),
            assessment_date     TEXT NOT NULL,
            m_items             TEXT,
            notes               TEXT,
            created_at          TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    tables_created += 1

    conn.execute("CREATE INDEX IF NOT EXISTS idx_oasis_patient ON healthclaw_oasis_assessment(patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_oasis_company ON healthclaw_oasis_assessment(company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_oasis_type ON healthclaw_oasis_assessment(assessment_type)")
    indexes_created += 3

    # -----------------------------------------------------------------------
    # 4. healthclaw_aide_assignment — home health aide scheduling
    # -----------------------------------------------------------------------
    conn.execute("""
        CREATE TABLE IF NOT EXISTS healthclaw_aide_assignment (
            id                  TEXT PRIMARY KEY,
            company_id          TEXT NOT NULL REFERENCES company(id),
            patient_id          TEXT NOT NULL REFERENCES healthclaw_patient(id),
            aide_id             TEXT NOT NULL REFERENCES employee(id),
            assignment_start    TEXT NOT NULL,
            assignment_end      TEXT,
            days_of_week        TEXT,
            visit_time          TEXT,
            tasks               TEXT,
            supervisor_id       TEXT REFERENCES employee(id),
            supervision_due_date TEXT,
            status              TEXT NOT NULL DEFAULT 'active'
                                CHECK(status IN ('active','on_hold','completed','cancelled')),
            notes               TEXT,
            created_at          TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    tables_created += 1

    conn.execute("CREATE INDEX IF NOT EXISTS idx_aide_assign_patient ON healthclaw_aide_assignment(patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_aide_assign_company ON healthclaw_aide_assignment(company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_aide_assign_aide ON healthclaw_aide_assignment(aide_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_aide_assign_status ON healthclaw_aide_assignment(status)")
    indexes_created += 4

    conn.commit()
    conn.close()

    return {
        "database": db_path,
        "tables": tables_created,
        "indexes": indexes_created,
    }


if __name__ == "__main__":
    result = init_homehealth_schema()
    print(f"HealthClaw Home Health schema created in {result['database']}", file=sys.stderr)
    print(f"  Tables: {result['tables']}", file=sys.stderr)
    print(f"  Indexes: {result['indexes']}", file=sys.stderr)
