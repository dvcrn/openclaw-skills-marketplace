"""
Logger
======
Lightweight logger for multi-platform-publisher.  Writes to stderr so
that JSON output on stdout remains clean.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone


class Logger:
    """Simple levelled logger that writes to stderr."""

    LEVELS = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}

    def __init__(self, name: str, level: str = "INFO"):
        self.name = name
        self.level = self.LEVELS.get(level.upper(), 1)

    def _log(self, level: str, message: str) -> None:
        if self.LEVELS.get(level, 0) >= self.level:
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            print(f"[{ts}] [{level}] {self.name}: {message}", file=sys.stderr)

    def debug(self, msg: str) -> None:
        self._log("DEBUG", msg)

    def info(self, msg: str) -> None:
        self._log("INFO", msg)

    def warning(self, msg: str) -> None:
        self._log("WARNING", msg)

    def error(self, msg: str) -> None:
        self._log("ERROR", msg)
