"""Journal d'activite -- stockage JSON local.

Chaque entree :
  {id, timestamp, text, project, duration_minutes, tags}

Fichier : ~/.openclaw/data/work-helper/journal.json
"""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

_DATA_DIR = Path(os.path.expanduser("~/.openclaw/data/work-helper"))
_JOURNAL_PATH = _DATA_DIR / "journal.json"


# ── helpers ──────────────────────────────────────────────────────────

def _ensure_dir() -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load() -> List[dict]:
    if not _JOURNAL_PATH.exists():
        return []
    try:
        return json.loads(_JOURNAL_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save(entries: List[dict]) -> None:
    _ensure_dir()
    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=str(_DATA_DIR), suffix=".tmp"
    )
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, str(_JOURNAL_PATH))
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _parse_duration(raw: str) -> Optional[int]:
    """Parse '2h', '30m', '1h30', '1h30m', '90' -> minutes."""
    if not raw:
        return None
    raw = raw.strip().lower()
    hours = 0
    minutes = 0
    if "h" in raw:
        parts = raw.split("h", 1)
        hours = int(parts[0]) if parts[0] else 0
        rest = parts[1].rstrip("m").strip()
        minutes = int(rest) if rest else 0
    elif "m" in raw:
        minutes = int(raw.rstrip("m"))
    else:
        minutes = int(raw)
    return hours * 60 + minutes


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── public API ───────────────────────────────────────────────────────

def add(text: str, *,
        project: str = "",
        duration: str = "",
        tags: str = "") -> dict:
    """Ajoute une entree au journal. Retourne l'entree creee."""
    entry = {
        "id": uuid.uuid4().hex[:12],
        "timestamp": _now_iso(),
        "text": text,
        "project": project,
        "duration_minutes": _parse_duration(duration),
        "tags": [t.strip() for t in tags.split(",") if t.strip()] if tags else [],
    }
    entries = _load()
    entries.append(entry)
    _save(entries)
    return entry


def list_entries(*, period: str = "today",
                 project: str = "",
                 tz_name: str = "Europe/Paris") -> List[dict]:
    """Liste les entrees pour une periode : today, week, month, all."""
    entries = _load()
    now = datetime.now(timezone.utc)

    if period == "today":
        cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        cutoff = now - timedelta(days=now.weekday())
        cutoff = cutoff.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "month":
        cutoff = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        cutoff = None

    result = []
    for e in entries:
        ts = datetime.fromisoformat(e["timestamp"])
        if cutoff and ts < cutoff:
            continue
        if project and e.get("project", "").lower() != project.lower():
            continue
        result.append(e)
    return result


def search(term: str) -> List[dict]:
    """Recherche dans le texte, le projet et les tags."""
    entries = _load()
    term_lower = term.lower()
    return [
        e for e in entries
        if term_lower in e.get("text", "").lower()
        or term_lower in e.get("project", "").lower()
        or any(term_lower in t.lower() for t in e.get("tags", []))
    ]


def get_all() -> List[dict]:
    """Retourne toutes les entrees."""
    return _load()


def delete(entry_id: str) -> bool:
    """Supprime une entree par ID. Retourne True si trouvee."""
    entries = _load()
    new = [e for e in entries if e["id"] != entry_id]
    if len(new) == len(entries):
        return False
    _save(new)
    return True
