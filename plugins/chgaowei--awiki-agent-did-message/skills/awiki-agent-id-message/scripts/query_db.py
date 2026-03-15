"""Read-only SQL query CLI against local SQLite database.

Usage:
    python scripts/query_db.py "SELECT * FROM threads LIMIT 10"
    python scripts/query_db.py "SELECT * FROM messages WHERE credential_name='alice' LIMIT 10"
    python scripts/query_db.py "SELECT * FROM groups ORDER BY last_message_at DESC LIMIT 10"
    python scripts/query_db.py "SELECT * FROM group_members WHERE group_id='grp_xxx' LIMIT 20"
    python scripts/query_db.py "SELECT * FROM relationship_events WHERE status='pending' ORDER BY created_at DESC LIMIT 20"

[INPUT]: local_store (SQLite connection + execute_sql), logging_config
[OUTPUT]: JSON query results to stdout
[POS]: CLI entry point for ad-hoc local database queries

[PROTOCOL]:
1. Update this header when logic changes
2. Check the folder's CLAUDE.md after updating
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

import local_store
from utils.logging_config import configure_logging

logger = logging.getLogger(__name__)


def main() -> None:
    configure_logging(console_level=None, mirror_stdio=True)

    parser = argparse.ArgumentParser(description="Query local SQLite database")
    parser.add_argument("sql", type=str, help="SQL statement to execute")
    parser.add_argument(
        "--credential",
        type=str,
        default=None,
        help="Legacy option; prefer explicit owner_did / credential_name filters in SQL",
    )

    args = parser.parse_args()
    logger.info("query_db CLI started sql=%s", args.sql)

    conn = local_store.get_connection()
    local_store.ensure_schema(conn)

    try:
        result = local_store.execute_sql(conn, args.sql)
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        logger.info("query_db completed rows=%d", len(result) if isinstance(result, list) else 1)
    except ValueError as exc:
        logger.warning("query_db rejected sql: %s", exc)
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
