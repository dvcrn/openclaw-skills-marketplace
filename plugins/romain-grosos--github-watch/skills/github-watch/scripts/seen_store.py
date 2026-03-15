"""
Gestion des repos deja vus pour GitHub Watch.
Stocke dans ~/.openclaw/data/github-watch/seen.json

Atomic writes to prevent corruption on concurrent access.
"""

import json
import os
import tempfile
from pathlib import Path
from datetime import datetime

DEFAULT_PATH = os.path.expanduser("~/.openclaw/data/github-watch/seen.json")
_ALLOWED_BASE = os.path.expanduser("~/.openclaw/data/")


class GitHubStore:
    def __init__(self, filepath=DEFAULT_PATH):
        self.filepath = Path(filepath).resolve()
        # Validate path stays within allowed directory
        if not str(self.filepath).startswith(str(Path(_ALLOWED_BASE).resolve())):
            raise ValueError(f"Path {self.filepath} outside allowed directory {_ALLOWED_BASE}")
        self.data = {}
        self.load()

    def load(self):
        if self.filepath.exists():
            try:
                with open(self.filepath, encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}
        else:
            self.data = {}

    def save(self):
        """Atomic write: write to temp file then rename."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(self.data, indent=2, ensure_ascii=False, sort_keys=True)
        fd, tmp = tempfile.mkstemp(dir=str(self.filepath.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp, str(self.filepath))
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    def mark_seen(self, repo_name):
        """Mark a repo as seen. Call AFTER agent selection, not during filtering."""
        self.data[repo_name] = datetime.utcnow().isoformat()
        self.save()

    def is_seen(self, repo_name):
        return repo_name in self.data

    def filter_unseen(self, repos, key_fn=None):
        """
        Return (repos_unseen, nb_skipped).
        Does NOT mark repos as seen - call mark_seen() explicitly after agent selection.
        key_fn: extract key from repo dict (default: repo["name"])
        """
        if key_fn is None:
            key_fn = lambda r: r

        unseen = []
        skipped = 0
        for repo in repos:
            key = key_fn(repo)
            if self.is_seen(key):
                skipped += 1
            else:
                unseen.append(repo)

        return unseen, skipped


# Singleton global
github_store = GitHubStore()
