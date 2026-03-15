"""Local database migration helpers for owner_did-aware multi-identity storage.

[INPUT]: local_store (SQLite schema management), SDKConfig (data_dir)
[OUTPUT]: detect_local_database_layout(), migrate_local_database(),
          ensure_local_database_ready()
[POS]: Shared migration module used by check_status.py and the standalone
       migrate_local_database.py CLI, with idempotent self-healing for
       already-ready databases

[PROTOCOL]:
1. Update this header when logic changes
2. Check the folder's CLAUDE.md after updating
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import local_store
from utils.config import SDKConfig

logger = logging.getLogger(__name__)


def _database_path(config: SDKConfig | None = None) -> Path:
    """Return the local SQLite database path."""
    resolved_config = config or SDKConfig()
    return resolved_config.data_dir / "database" / "awiki.db"


def _backup_root(config: SDKConfig | None = None) -> Path:
    """Return the database migration backup directory."""
    resolved_config = config or SDKConfig()
    backup_dir = resolved_config.data_dir / "database" / ".migration-backup"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def detect_local_database_layout(config: SDKConfig | None = None) -> dict[str, Any]:
    """Detect whether the local database requires migration."""
    db_path = _database_path(config)
    if not db_path.exists():
        return {
            "status": "not_found",
            "db_path": str(db_path),
            "before_version": None,
        }

    conn = local_store.get_connection()
    try:
        version = conn.execute("PRAGMA user_version").fetchone()[0]
    finally:
        conn.close()

    return {
        "status": "legacy" if version < local_store._SCHEMA_VERSION else "ready",
        "db_path": str(db_path),
        "before_version": version,
    }


def _backup_database(config: SDKConfig | None = None) -> Path:
    """Create a SQLite backup before migration."""
    db_path = _database_path(config)
    backup_path = _backup_root(config) / (
        f"awiki-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.db"
    )
    source = sqlite3.connect(str(db_path))
    try:
        destination = sqlite3.connect(str(backup_path))
        try:
            source.backup(destination)
        finally:
            destination.close()
    finally:
        source.close()
    logger.info("Created local database backup path=%s", backup_path)
    return backup_path


def _ensure_database_schema(
    *,
    db_path: str,
    status: str,
    backup_path: str | None,
) -> dict[str, Any]:
    """Run idempotent schema repair and return the migration summary."""
    conn = local_store.get_connection()
    try:
        before_version = conn.execute("PRAGMA user_version").fetchone()[0]
        local_store.ensure_schema(conn)
        after_version = conn.execute("PRAGMA user_version").fetchone()[0]
    finally:
        conn.close()

    return {
        "status": status,
        "db_path": db_path,
        "before_version": before_version,
        "after_version": after_version,
        "backup_path": backup_path,
    }


def migrate_local_database(config: SDKConfig | None = None) -> dict[str, Any]:
    """Migrate the local SQLite database to the latest schema."""
    detection = detect_local_database_layout(config)
    if detection["status"] == "not_found":
        return {
            "status": "not_needed",
            "db_path": detection["db_path"],
            "before_version": None,
            "after_version": None,
            "backup_path": None,
        }
    if detection["status"] == "ready":
        return _ensure_database_schema(
            db_path=detection["db_path"],
            status="ready",
            backup_path=None,
        )

    backup_path = _backup_database(config)
    return _ensure_database_schema(
        db_path=detection["db_path"],
        status="migrated",
        backup_path=str(backup_path),
    )


def ensure_local_database_ready(config: SDKConfig | None = None) -> dict[str, Any]:
    """Ensure the local database is ready for multi-identity use."""
    detection = detect_local_database_layout(config)
    if detection["status"] == "not_found":
        return detection
    return migrate_local_database(config)


__all__ = [
    "detect_local_database_layout",
    "ensure_local_database_ready",
    "migrate_local_database",
]
