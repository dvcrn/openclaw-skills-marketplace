#!/usr/bin/env python3
import fcntl
import json
import os
from pathlib import Path
from typing import Any


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def write_json_atomic(path: Path, payload: Any, indent: int = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=indent), encoding="utf-8")
    tmp.replace(path)


def append_jsonl_locked(path: Path, row: dict[str, Any], fsync: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        f.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
        f.write("\n")
        f.flush()
        if fsync:
            os.fsync(f.fileno())
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
