"""Shared utility functions for VEXT Shield.

Provides file hashing, SKILL.md parsing, OpenClaw path discovery,
encoded content detection, and common helpers.
"""

from __future__ import annotations

import base64
import codecs
import hashlib
import json
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SEVERITY_SCORES: dict[str, int] = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
    "INFO": 0,
}

# OpenClaw stores skills in these subdirectories
SKILL_SUBDIRS = ("skills", "custom_skills", "workspace_skills")

# Sensitive files that skills should never read
SENSITIVE_FILES = {
    "openclaw.json",
    ".env",
    "SOUL.md",
    "MEMORY.md",
    "AGENTS.md",
    ".ssh",
    "id_rsa",
    "id_ed25519",
    "known_hosts",
    "authorized_keys",
    "cookies",
    "keychain",
    "Cookies",
    "Login Data",
    "credentials.json",
    "token.json",
}

# Text file extensions we'll scan
SCANNABLE_EXTENSIONS = {
    ".md", ".txt", ".py", ".sh", ".bash", ".zsh", ".js", ".ts",
    ".json", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".conf",
    ".xml", ".html", ".css", ".rb", ".pl", ".lua", ".r", ".go",
    ".rs", ".java", ".kt", ".swift", ".c", ".cpp", ".h", ".hpp",
}

# Unicode homoglyph map: visually similar characters that differ from ASCII
# Maps suspicious codepoints to the ASCII char they impersonate
HOMOGLYPH_MAP: dict[str, str] = {
    "\u0410": "A",  # Cyrillic А
    "\u0412": "B",  # Cyrillic В
    "\u0421": "C",  # Cyrillic С
    "\u0415": "E",  # Cyrillic Е
    "\u041d": "H",  # Cyrillic Н
    "\u041a": "K",  # Cyrillic К
    "\u041c": "M",  # Cyrillic М
    "\u041e": "O",  # Cyrillic О
    "\u0420": "P",  # Cyrillic Р
    "\u0422": "T",  # Cyrillic Т
    "\u0425": "X",  # Cyrillic Х
    "\u0430": "a",  # Cyrillic а
    "\u0435": "e",  # Cyrillic е
    "\u043e": "o",  # Cyrillic о
    "\u0440": "p",  # Cyrillic р
    "\u0441": "c",  # Cyrillic с
    "\u0443": "y",  # Cyrillic у
    "\u0445": "x",  # Cyrillic х
    "\u0456": "i",  # Cyrillic і
    "\u0458": "j",  # Cyrillic ј
    "\u0455": "s",  # Cyrillic ѕ
    "\u04bb": "h",  # Cyrillic һ
    "\u0501": "d",  # Cyrillic ԁ
    "\u051b": "q",  # Cyrillic ԛ
    "\u200b": "",   # Zero-width space
    "\u200c": "",   # Zero-width non-joiner
    "\u200d": "",   # Zero-width joiner
    "\u2060": "",   # Word joiner
    "\ufeff": "",   # Zero-width no-break space (BOM)
    "\u00a0": " ",  # Non-breaking space
    "\u2000": " ",  # En quad
    "\u2001": " ",  # Em quad
    "\u2002": " ",  # En space
    "\u2003": " ",  # Em space
    "\u2004": " ",  # Three-per-em space
    "\u2005": " ",  # Four-per-em space
    "\u2006": " ",  # Six-per-em space
    "\u2007": " ",  # Figure space
    "\u2008": " ",  # Punctuation space
    "\u2009": " ",  # Thin space
    "\u200a": " ",  # Hair space
    "\u202f": " ",  # Narrow no-break space
    "\u205f": " ",  # Medium mathematical space
    "\u3000": " ",  # Ideographic space
    "\uff21": "A",  # Fullwidth A
    "\uff22": "B",  # Fullwidth B
    "\uff23": "C",  # Fullwidth C
    "\uff41": "a",  # Fullwidth a
    "\uff42": "b",  # Fullwidth b
    "\uff43": "c",  # Fullwidth c
}

# Pre-compiled regex for base64 detection
# Matches strings that look like base64 (min 20 chars, proper charset, padding)
_BASE64_PATTERN = re.compile(
    r'[A-Za-z0-9+/]{20,}={0,2}'
)

# Pre-compiled regex for ROT13 detection keywords after decoding
_ROT13_SUSPICIOUS_KEYWORDS = [
    "ignore", "override", "system", "execute", "eval", "exec",
    "import", "subprocess", "password", "secret", "token", "api_key",
    "curl", "wget", "fetch", "request", "socket", "connect",
]


# ---------------------------------------------------------------------------
# File hashing
# ---------------------------------------------------------------------------

def hash_file(path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def hash_content(content: str) -> str:
    """Compute SHA-256 hash of a string."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# SKILL.md parsing
# ---------------------------------------------------------------------------

def parse_skill_md(path: Path) -> tuple[dict[str, Any], str]:
    """Parse a SKILL.md file into (frontmatter_dict, markdown_body).

    The frontmatter is delimited by ``---`` lines at the top of the file.
    Uses a minimal YAML-subset parser (no PyYAML dependency).

    Returns ``({}, full_text)`` if no valid frontmatter is found.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")

    if not lines or lines[0].strip() != "---":
        return {}, text

    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        return {}, text

    frontmatter_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1:]).strip()

    frontmatter = _parse_yaml_subset(frontmatter_lines)
    return frontmatter, body


def _parse_yaml_subset(lines: list[str]) -> dict[str, Any]:
    """Minimal YAML parser for SKILL.md frontmatter.

    Handles flat key-value pairs and simple nested mappings.
    Does NOT handle the full YAML spec — just enough for OpenClaw metadata.
    """
    result: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, result)]

    for line in lines:
        stripped = line.rstrip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        # Pop stack to find parent at lower indent
        while len(stack) > 1 and stack[-1][0] >= indent:
            stack.pop()

        parent = stack[-1][1]

        if ":" not in stripped:
            continue

        key, _, value = stripped.partition(":")
        key = key.strip().strip('"').strip("'")
        value = value.strip()

        if not value:
            # Nested mapping
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        elif value.startswith("[") and value.endswith("]"):
            # Inline list: [item1, item2]
            items = value[1:-1].split(",")
            parent[key] = [i.strip().strip('"').strip("'") for i in items if i.strip()]
        elif value.startswith('"') and value.endswith('"'):
            parent[key] = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            parent[key] = value[1:-1]
        elif value.lower() in ("true", "yes"):
            parent[key] = True
        elif value.lower() in ("false", "no"):
            parent[key] = False
        elif value.isdigit():
            parent[key] = int(value)
        else:
            parent[key] = value

    return result


# ---------------------------------------------------------------------------
# OpenClaw path discovery
# ---------------------------------------------------------------------------

def find_openclaw_dir() -> Path | None:
    """Locate the OpenClaw configuration directory.

    Checks in order:
    1. $OPENCLAW_HOME environment variable
    2. ~/.openclaw/
    3. ~/.config/openclaw/
    """
    env_home = os.environ.get("OPENCLAW_HOME")
    if env_home:
        p = Path(env_home)
        if p.is_dir():
            return p

    home = Path.home()
    for candidate in [home / ".openclaw", home / ".config" / "openclaw"]:
        if candidate.is_dir():
            return candidate

    return None


def find_vext_shield_dir() -> Path:
    """Get or create the VEXT Shield data directory at ~/.openclaw/vext-shield/."""
    oc = find_openclaw_dir()
    base = oc if oc else Path.home() / ".openclaw"
    shield_dir = base / "vext-shield"
    shield_dir.mkdir(parents=True, exist_ok=True)
    return shield_dir


def enumerate_skills(openclaw_dir: Path | None = None) -> list[Path]:
    """Find all installed skill directories.

    Searches bundled skills, managed skills, and workspace skills.
    Each skill directory must contain a SKILL.md file.
    """
    if openclaw_dir is None:
        openclaw_dir = find_openclaw_dir()
    if openclaw_dir is None:
        return []

    skill_dirs: list[Path] = []

    # Check standard subdirectories
    for subdir_name in SKILL_SUBDIRS:
        subdir = openclaw_dir / subdir_name
        if not subdir.is_dir():
            continue
        # Skills can be nested: skills/author/skill-name/SKILL.md
        for skill_md in subdir.rglob("SKILL.md"):
            skill_dirs.append(skill_md.parent)

    # Also check workspace-level skills (current directory)
    cwd = Path.cwd()
    for skill_md in cwd.rglob("SKILL.md"):
        # Avoid scanning ourselves
        if "vext-shield" in str(skill_md):
            continue
        if skill_md.parent not in skill_dirs:
            skill_dirs.append(skill_md.parent)

    return sorted(set(skill_dirs))


# ---------------------------------------------------------------------------
# Encoded content detection
# ---------------------------------------------------------------------------

def decode_base64_strings(text: str) -> list[dict[str, str]]:
    """Extract and decode base64-encoded strings from text.

    Returns list of dicts with 'encoded' and 'decoded' keys.
    Only returns strings that decode to printable text.
    """
    results: list[dict[str, str]] = []
    seen: set[str] = set()

    for match in _BASE64_PATTERN.finditer(text):
        candidate = match.group()
        if candidate in seen:
            continue
        seen.add(candidate)

        # Skip things that are obviously not base64 (all same char, common words)
        if len(set(candidate)) < 4:
            continue

        try:
            decoded_bytes = base64.b64decode(candidate, validate=True)
            decoded = decoded_bytes.decode("utf-8", errors="strict")
            # Only keep if mostly printable
            printable_ratio = sum(1 for c in decoded if c.isprintable() or c in "\n\r\t") / len(decoded)
            if printable_ratio > 0.8 and len(decoded) >= 4:
                results.append({"encoded": candidate, "decoded": decoded})
        except Exception:
            continue

    return results


def detect_rot13(text: str) -> list[dict[str, str]]:
    """Detect potential ROT13-encoded suspicious content.

    Applies ROT13 to each line and checks if the result contains
    security-relevant keywords.
    """
    results: list[dict[str, str]] = []

    for line in text.split("\n"):
        line = line.strip()
        if not line or len(line) < 10:
            continue

        decoded = codecs.decode(line, "rot_13")
        decoded_lower = decoded.lower()

        for keyword in _ROT13_SUSPICIOUS_KEYWORDS:
            if keyword in decoded_lower and keyword not in line.lower():
                results.append({"encoded": line, "decoded": decoded, "keyword": keyword})
                break

    return results


def detect_unicode_homoglyphs(text: str) -> list[tuple[int, str, str, str]]:
    """Detect unicode homoglyphs that could hide malicious content.

    Returns list of (line_number, char, lookalike, context) tuples.
    """
    findings: list[tuple[int, str, str, str]] = []

    for line_num, line in enumerate(text.split("\n"), 1):
        for i, char in enumerate(line):
            if char in HOMOGLYPH_MAP:
                lookalike = HOMOGLYPH_MAP[char]
                start = max(0, i - 15)
                end = min(len(line), i + 15)
                context = line[start:end]
                findings.append((line_num, char, lookalike, context))

    return findings


def detect_zero_width_chars(text: str) -> list[tuple[int, int, str]]:
    """Detect zero-width characters that could hide content.

    Returns list of (line_number, position, char_name) tuples.
    """
    zero_width_chars = {
        "\u200b": "ZERO WIDTH SPACE",
        "\u200c": "ZERO WIDTH NON-JOINER",
        "\u200d": "ZERO WIDTH JOINER",
        "\u2060": "WORD JOINER",
        "\ufeff": "ZERO WIDTH NO-BREAK SPACE",
        "\u200e": "LEFT-TO-RIGHT MARK",
        "\u200f": "RIGHT-TO-LEFT MARK",
        "\u202a": "LEFT-TO-RIGHT EMBEDDING",
        "\u202b": "RIGHT-TO-LEFT EMBEDDING",
        "\u202c": "POP DIRECTIONAL FORMATTING",
        "\u202d": "LEFT-TO-RIGHT OVERRIDE",
        "\u202e": "RIGHT-TO-LEFT OVERRIDE",
    }

    findings: list[tuple[int, int, str]] = []
    for line_num, line in enumerate(text.split("\n"), 1):
        for i, char in enumerate(line):
            if char in zero_width_chars:
                findings.append((line_num, i, zero_width_chars[char]))

    return findings


# ---------------------------------------------------------------------------
# Severity helpers
# ---------------------------------------------------------------------------

def severity_to_score(severity: str) -> int:
    """Map severity string to numeric score."""
    return SEVERITY_SCORES.get(severity.upper(), 0)


def score_to_grade(score: float) -> str:
    """Map a normalized 0-100 security score to a letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


# ---------------------------------------------------------------------------
# File permission checks
# ---------------------------------------------------------------------------

def check_file_permissions(path: Path) -> dict[str, Any]:
    """Check file permissions and return a security assessment."""
    if not path.exists():
        return {"exists": False, "path": str(path)}

    st = path.stat()
    mode = st.st_mode
    is_world_readable = bool(mode & stat.S_IROTH)
    is_world_writable = bool(mode & stat.S_IWOTH)
    is_group_writable = bool(mode & stat.S_IWGRP)
    octal_mode = oct(mode)[-3:]

    issues: list[str] = []
    if is_world_readable:
        issues.append("World-readable")
    if is_world_writable:
        issues.append("World-writable (CRITICAL)")
    if is_group_writable:
        issues.append("Group-writable")

    return {
        "exists": True,
        "path": str(path),
        "mode": octal_mode,
        "world_readable": is_world_readable,
        "world_writable": is_world_writable,
        "group_writable": is_group_writable,
        "issues": issues,
        "secure": len(issues) == 0,
    }


# ---------------------------------------------------------------------------
# Miscellaneous helpers
# ---------------------------------------------------------------------------

def is_scannable_file(path: Path) -> bool:
    """Check if a file should be scanned based on extension."""
    return path.suffix.lower() in SCANNABLE_EXTENSIONS


def read_file_safe(path: Path, max_size: int = 5 * 1024 * 1024) -> str | None:
    """Read a file safely with size limit (default 5MB).

    Returns None if file is too large or unreadable.
    """
    try:
        if path.stat().st_size > max_size:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError):
        return None


def get_skill_name(skill_dir: Path) -> str:
    """Extract the skill name from a skill directory.

    Tries SKILL.md frontmatter first, falls back to directory name.
    """
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        frontmatter, _ = parse_skill_md(skill_md)
        name = frontmatter.get("name")
        if name:
            return str(name)
    return skill_dir.name


def load_json_safe(path: Path) -> dict[str, Any] | None:
    """Load a JSON file, returning None on failure.

    Handles JSON5-style comments by stripping // comments.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        # Strip single-line comments (JSON5 compat)
        lines = []
        for line in text.split("\n"):
            stripped = line.lstrip()
            if stripped.startswith("//"):
                continue
            # Remove inline comments (naive — doesn't handle strings)
            comment_idx = line.find("//")
            if comment_idx > 0:
                # Simple heuristic: only strip if not inside a string
                before = line[:comment_idx]
                if before.count('"') % 2 == 0:
                    line = before
            lines.append(line)
        # Remove trailing commas before } or ]
        cleaned = "\n".join(lines)
        cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)
        return json.loads(cleaned)
    except (OSError, json.JSONDecodeError):
        return None


def timestamp_str() -> str:
    """Get current timestamp as a filename-safe string."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
