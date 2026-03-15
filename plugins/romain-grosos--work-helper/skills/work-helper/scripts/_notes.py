"""Notes libres -- stockage JSON local.

Chaque note :
  {id, timestamp, text, project}

Fichier : ~/.openclaw/data/work-helper/notes.json
"""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

_DATA_DIR = Path(os.path.expanduser("~/.openclaw/data/work-helper"))
_NOTES_PATH = _DATA_DIR / "notes.json"


def _ensure_dir() -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load() -> List[dict]:
    if not _NOTES_PATH.exists():
        return []
    try:
        return json.loads(_NOTES_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save(notes: List[dict]) -> None:
    _ensure_dir()
    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=str(_DATA_DIR), suffix=".tmp"
    )
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, str(_NOTES_PATH))
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def add(text: str, *, project: str = "") -> dict:
    """Ajoute une note. Retourne la note creee."""
    note = {
        "id": uuid.uuid4().hex[:12],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "text": text,
        "project": project,
    }
    notes = _load()
    notes.append(note)
    _save(notes)
    return note


def list_notes(*, project: str = "") -> List[dict]:
    """Liste les notes, filtre optionnel par projet."""
    notes = _load()
    if project:
        return [n for n in notes if n.get("project", "").lower() == project.lower()]
    return notes


def search(term: str) -> List[dict]:
    """Recherche dans le texte et le projet."""
    notes = _load()
    term_lower = term.lower()
    return [
        n for n in notes
        if term_lower in n.get("text", "").lower()
        or term_lower in n.get("project", "").lower()
    ]


def delete(note_id: str) -> bool:
    """Supprime une note par ID."""
    notes = _load()
    new = [n for n in notes if n["id"] != note_id]
    if len(new) == len(notes):
        return False
    _save(new)
    return True
