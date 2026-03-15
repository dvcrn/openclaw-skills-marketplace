"""SQLite database for storing Discord chat messages."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .config import get_db_path

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS messages (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    platform      TEXT    NOT NULL DEFAULT 'discord',
    guild_id      TEXT,
    guild_name    TEXT,
    channel_id    TEXT    NOT NULL,
    channel_name  TEXT,
    msg_id        TEXT    NOT NULL,
    sender_id     TEXT,
    sender_name   TEXT,
    content       TEXT,
    timestamp     TEXT    NOT NULL,
    raw_json      TEXT,
    UNIQUE(platform, channel_id, msg_id)
);
"""

_CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_messages_channel_ts ON messages(channel_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_content ON messages(content);
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_name);
CREATE INDEX IF NOT EXISTS idx_messages_guild ON messages(guild_id);
"""


class MessageDB:
    """SQLite message store with context manager support."""

    def __init__(self, db_path: Path | str | None = None):
        if db_path is None:
            self.db_path = get_db_path()
        else:
            self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript(_CREATE_TABLE + _CREATE_INDEX)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def insert_batch(self, messages: list[dict], platform: str = "discord") -> int:
        """Batch insert messages. Returns rows actually inserted (excluding dupes)."""
        if not messages:
            return 0
        rows = [
            (
                platform,
                m.get("guild_id"),
                m.get("guild_name"),
                m["channel_id"],
                m.get("channel_name"),
                m["msg_id"],
                m.get("sender_id"),
                m.get("sender_name"),
                m.get("content"),
                m["timestamp"].isoformat() if isinstance(m["timestamp"], datetime) else m["timestamp"],
                json.dumps(m["raw_json"], ensure_ascii=False) if m.get("raw_json") else None,
            )
            for m in messages
        ]
        try:
            before = self.conn.total_changes
            self.conn.executemany(
                """INSERT OR IGNORE INTO messages
                   (platform, guild_id, guild_name, channel_id, channel_name,
                    msg_id, sender_id, sender_name, content, timestamp, raw_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                rows,
            )
            self.conn.commit()
            return self.conn.total_changes - before
        except sqlite3.Error:
            return 0

    def resolve_channel_id(self, channel_str: str) -> str | None:
        """Resolve a channel string (name or ID) to a database channel_id.

        Returns None if not found in the database.
        """
        channels = self.get_channels()

        # Try name match first
        for c in channels:
            if c["channel_name"] and channel_str.lower() in c["channel_name"].lower():
                return c["channel_id"]

        # Try raw ID match
        for c in channels:
            if c["channel_id"] == channel_str:
                return c["channel_id"]

        # If input looks like a snowflake ID, pass through
        if channel_str.isdigit() and len(channel_str) > 15:
            return channel_str

        return None

    def search(
        self,
        keyword: str,
        channel_id: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """Search messages by keyword."""
        query = "SELECT * FROM messages WHERE content LIKE ?"
        params: list[Any] = [f"%{keyword}%"]
        if channel_id:
            query += " AND channel_id = ?"
            params.append(channel_id)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        rows = self.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_recent(
        self,
        channel_id: str | None = None,
        hours: int | None = 24,
        limit: int = 500,
    ) -> list[dict]:
        """Get recent messages. If hours is None, return all."""
        if hours is not None:
            cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
            query = "SELECT * FROM messages WHERE timestamp >= ?"
            params: list[Any] = [cutoff]
        else:
            query = "SELECT * FROM messages WHERE 1=1"
            params = []
        if channel_id:
            query += " AND channel_id = ?"
            params.append(channel_id)
        query += " ORDER BY timestamp ASC LIMIT ?"
        params.append(limit)
        rows = self.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_today(
        self,
        channel_id: str | None = None,
        tz_offset_hours: int = 8,
        limit: int = 5000,
    ) -> list[dict]:
        """Get today's messages (in local timezone)."""
        now_utc = datetime.now(timezone.utc)
        local_tz = timezone(timedelta(hours=tz_offset_hours))
        today_local = now_utc.astimezone(local_tz).replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_utc = today_local.astimezone(timezone.utc).isoformat()

        query = "SELECT * FROM messages WHERE timestamp >= ?"
        params: list[Any] = [cutoff_utc]
        if channel_id:
            query += " AND channel_id = ?"
            params.append(channel_id)
        query += " ORDER BY channel_name, timestamp ASC LIMIT ?"
        params.append(limit)
        rows = self.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_channels(self) -> list[dict]:
        """Get all known channels with message counts."""
        rows = self.conn.execute(
            """SELECT channel_id, channel_name, guild_id, guild_name,
                      COUNT(*) as msg_count,
                      MIN(timestamp) as first_msg, MAX(timestamp) as last_msg
               FROM messages
               GROUP BY channel_id
               ORDER BY msg_count DESC"""
        ).fetchall()
        return [dict(r) for r in rows]

    def get_last_msg_id(self, channel_id: str) -> str | None:
        """Get the latest msg_id for a channel, used for incremental sync."""
        row = self.conn.execute(
            "SELECT MAX(msg_id) FROM messages WHERE channel_id = ?", (channel_id,)
        ).fetchone()
        return row[0] if row and row[0] is not None else None

    def count(self, channel_id: str | None = None) -> int:
        if channel_id:
            row = self.conn.execute(
                "SELECT COUNT(*) FROM messages WHERE channel_id = ?", (channel_id,)
            ).fetchone()
        else:
            row = self.conn.execute("SELECT COUNT(*) FROM messages").fetchone()
        return row[0]

    def delete_channel(self, channel_id: str) -> int:
        """Delete all messages for a channel. Returns number of deleted rows."""
        cursor = self.conn.execute(
            "DELETE FROM messages WHERE channel_id = ?", (channel_id,)
        )
        self.conn.commit()
        return cursor.rowcount

    def top_senders(
        self,
        channel_id: str | None = None,
        hours: int | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """Get most active senders."""
        conditions = ["sender_name IS NOT NULL"]
        params: list[Any] = []
        if channel_id:
            conditions.append("channel_id = ?")
            params.append(channel_id)
        if hours:
            cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
            conditions.append("timestamp >= ?")
            params.append(cutoff)

        where = " AND ".join(conditions)
        rows = self.conn.execute(
            f"""SELECT sender_name, sender_id, COUNT(*) as msg_count,
                       MIN(timestamp) as first_msg, MAX(timestamp) as last_msg
                FROM messages WHERE {where}
                GROUP BY sender_name
                ORDER BY msg_count DESC
                LIMIT ?""",
            params + [limit],
        ).fetchall()
        return [dict(r) for r in rows]

    def timeline(
        self,
        channel_id: str | None = None,
        hours: int | None = None,
        granularity: str = "day",
    ) -> list[dict]:
        """Get message count grouped by time period."""
        if granularity == "hour":
            time_expr = "substr(timestamp, 1, 13)"  # YYYY-MM-DDTHH
        else:
            time_expr = "substr(timestamp, 1, 10)"  # YYYY-MM-DD

        conditions = ["1=1"]
        params: list[Any] = []
        if channel_id:
            conditions.append("channel_id = ?")
            params.append(channel_id)
        if hours:
            cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
            conditions.append("timestamp >= ?")
            params.append(cutoff)

        where = " AND ".join(conditions)
        rows = self.conn.execute(
            f"""SELECT {time_expr} as period, COUNT(*) as msg_count
                FROM messages WHERE {where}
                GROUP BY period
                ORDER BY period ASC""",
            params,
        ).fetchall()
        return [dict(r) for r in rows]

    def close(self):
        self.conn.close()
