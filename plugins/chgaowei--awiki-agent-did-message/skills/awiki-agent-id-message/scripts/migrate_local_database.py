"""Migrate the local SQLite database to the owner_did-aware schema.

Usage:
    uv run python scripts/migrate_local_database.py

[INPUT]: database_migration
[OUTPUT]: JSON migration summary
[POS]: Standalone local database migration CLI

[PROTOCOL]:
1. Update this header when logic changes
2. Check the folder's CLAUDE.md after updating
"""

from __future__ import annotations

import argparse
import json
import logging

from database_migration import migrate_local_database
from utils.logging_config import configure_logging

logger = logging.getLogger(__name__)


def main() -> None:
    """CLI entry point."""
    configure_logging(console_level=None, mirror_stdio=True)

    parser = argparse.ArgumentParser(
        description="Migrate the local SQLite database to the latest schema",
    )
    parser.parse_args()

    logger.info("migrate_local_database CLI started")
    result = migrate_local_database()
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
