#!/usr/bin/env python3
"""Initialize (or validate) the rides SQLite database.

Creates the DB file if missing and applies the schema.

Schema is treated as the source of truth; do not modify it here.
"""

import argparse
import sqlite3
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--schema", required=True)
    args = ap.parse_args()

    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    schema_sql = Path(args.schema).read_text(encoding="utf-8")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()

    print(f"DB ready: {db_path}")


if __name__ == "__main__":
    main()
