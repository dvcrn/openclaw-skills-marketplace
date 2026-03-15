"""HealthClaw Mental — schema initialization.

Creates 4 mental-health-specific tables in the shared ERPClaw database.
Requires healthclaw core tables to exist (patient FK references).
"""
import os
import sqlite3
import sys

DB_PATH = os.environ.get("ERPCLAW_DB_PATH", os.path.expanduser("~/.openclaw/erpclaw/data.sqlite"))


def init_mental_schema(db_path: str = DB_PATH) -> dict:
    """Create mental health expansion tables and indexes."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")

    tables_created = 0
    indexes_created = 0

    # -----------------------------------------------------------------------
    # 1. healthclaw_therapy_session — individual/couples/family/group sessions
    # -----------------------------------------------------------------------
    conn.execute("""
        CREATE TABLE IF NOT EXISTS healthclaw_therapy_session (
            id                  TEXT PRIMARY KEY,
            company_id          TEXT NOT NULL REFERENCES company(id),
            encounter_id        TEXT NOT NULL REFERENCES healthclaw_encounter(id),
            patient_id          TEXT NOT NULL REFERENCES healthclaw_patient(id),
            provider_id         TEXT NOT NULL REFERENCES employee(id),
            session_type        TEXT NOT NULL
                                CHECK(session_type IN ('individual','couples','family','group')),
            modality            TEXT
                                CHECK(modality IN ('cbt','dbt','emdr','psychodynamic','supportive','motivational_interviewing','other')),
            duration_minutes    INTEGER,
            session_number      INTEGER,
            notes               TEXT,
            status              TEXT NOT NULL DEFAULT 'completed'
                                CHECK(status IN ('scheduled','in_progress','completed','cancelled','no_show')),
            created_at          TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    tables_created += 1

    conn.execute("CREATE INDEX IF NOT EXISTS idx_therapy_session_company ON healthclaw_therapy_session(company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_therapy_session_patient ON healthclaw_therapy_session(patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_therapy_session_provider ON healthclaw_therapy_session(provider_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_therapy_session_encounter ON healthclaw_therapy_session(encounter_id)")
    indexes_created += 4

    # -----------------------------------------------------------------------
    # 2. healthclaw_assessment — standardized mental health instruments
    # -----------------------------------------------------------------------
    conn.execute("""
        CREATE TABLE IF NOT EXISTS healthclaw_assessment (
            id                  TEXT PRIMARY KEY,
            company_id          TEXT NOT NULL REFERENCES company(id),
            patient_id          TEXT NOT NULL REFERENCES healthclaw_patient(id),
            administered_by_id  TEXT REFERENCES employee(id),
            instrument          TEXT NOT NULL
                                CHECK(instrument IN ('PHQ-9','GAD-7','AUDIT','PCL-5','CSSRS','PHQ-2','GAD-2','DAST-10','MDQ','CAGE')),
            responses           TEXT,
            score               INTEGER,
            severity            TEXT,
            administered_date   TEXT NOT NULL,
            notes               TEXT,
            created_at          TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    tables_created += 1

    conn.execute("CREATE INDEX IF NOT EXISTS idx_assessment_company ON healthclaw_assessment(company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_assessment_patient ON healthclaw_assessment(patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_assessment_instrument ON healthclaw_assessment(patient_id, instrument)")
    indexes_created += 3

    # -----------------------------------------------------------------------
    # 3. healthclaw_treatment_goal — patient treatment goals with tracking
    # -----------------------------------------------------------------------
    conn.execute("""
        CREATE TABLE IF NOT EXISTS healthclaw_treatment_goal (
            id                  TEXT PRIMARY KEY,
            company_id          TEXT NOT NULL REFERENCES company(id),
            patient_id          TEXT NOT NULL REFERENCES healthclaw_patient(id),
            provider_id         TEXT REFERENCES employee(id),
            goal_description    TEXT NOT NULL,
            target_date         TEXT,
            baseline_measure    TEXT,
            current_measure     TEXT,
            goal_status         TEXT NOT NULL DEFAULT 'active'
                                CHECK(goal_status IN ('active','achieved','modified','discontinued')),
            notes               TEXT,
            created_at          TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    tables_created += 1

    conn.execute("CREATE INDEX IF NOT EXISTS idx_treatment_goal_company ON healthclaw_treatment_goal(company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_treatment_goal_patient ON healthclaw_treatment_goal(patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_treatment_goal_status ON healthclaw_treatment_goal(goal_status)")
    indexes_created += 3

    # -----------------------------------------------------------------------
    # 4. healthclaw_group_session — group therapy sessions
    # -----------------------------------------------------------------------
    conn.execute("""
        CREATE TABLE IF NOT EXISTS healthclaw_group_session (
            id                  TEXT PRIMARY KEY,
            company_id          TEXT NOT NULL REFERENCES company(id),
            provider_id         TEXT NOT NULL REFERENCES employee(id),
            session_date        TEXT NOT NULL,
            group_name          TEXT NOT NULL,
            group_type          TEXT
                                CHECK(group_type IN ('process','psychoeducation','support','skills_training')),
            topic               TEXT,
            max_participants    INTEGER DEFAULT 12,
            participant_ids     TEXT,
            duration_minutes    INTEGER,
            notes               TEXT,
            status              TEXT NOT NULL DEFAULT 'completed'
                                CHECK(status IN ('scheduled','completed','cancelled')),
            created_at          TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    tables_created += 1

    conn.execute("CREATE INDEX IF NOT EXISTS idx_group_session_company ON healthclaw_group_session(company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_group_session_provider ON healthclaw_group_session(provider_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_group_session_date ON healthclaw_group_session(session_date)")
    indexes_created += 3

    conn.commit()
    conn.close()

    return {
        "database": db_path,
        "tables": tables_created,
        "indexes": indexes_created,
    }


if __name__ == "__main__":
    result = init_mental_schema()
    print(f"HealthClaw Mental schema created in {result['database']}", file=sys.stderr)
    print(f"  Tables: {result['tables']}", file=sys.stderr)
    print(f"  Indexes: {result['indexes']}", file=sys.stderr)
