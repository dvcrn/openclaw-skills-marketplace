"""Tests for shared/threat_signatures.json integrity."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

SIGNATURES_PATH = _PROJECT_ROOT / "shared" / "threat_signatures.json"


@pytest.fixture(scope="module")
def signatures() -> dict:
    """Load the threat signatures file."""
    with open(SIGNATURES_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_signatures_file_exists():
    """Signatures file exists and is valid JSON."""
    assert SIGNATURES_PATH.exists()
    with open(SIGNATURES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict)


def test_has_version(signatures: dict):
    """Signatures file has a version string."""
    assert "version" in signatures
    assert isinstance(signatures["version"], str)


def test_has_categories(signatures: dict):
    """Signatures file has categories."""
    assert "categories" in signatures
    cats = signatures["categories"]
    assert len(cats) >= 6, f"Expected at least 6 categories, got {len(cats)}"


def test_expected_categories_present(signatures: dict):
    """All expected categories are present."""
    expected = {
        "prompt_injection",
        "data_exfiltration",
        "persistence",
        "privilege_escalation",
        "supply_chain",
        "semantic_worm",
    }
    actual = set(signatures["categories"].keys())
    missing = expected - actual
    assert not missing, f"Missing categories: {missing}"


def test_pattern_count_minimum(signatures: dict):
    """At least 200 patterns total."""
    count = 0
    for cat in signatures["categories"].values():
        for sub in cat.get("subcategories", {}).values():
            count += len(sub.get("patterns", []))
    assert count >= 200, f"Expected >= 200 patterns, got {count}"


def test_all_patterns_valid_regex(signatures: dict):
    """Every pattern compiles as valid regex."""
    errors: list[str] = []
    for cat_key, cat in signatures["categories"].items():
        for sub_key, sub in cat.get("subcategories", {}).items():
            for pat in sub.get("patterns", []):
                pattern = pat.get("pattern", "")
                pat_id = pat.get("id", "unknown")
                try:
                    re.compile(pattern)
                except re.error as e:
                    errors.append(f"{pat_id} ({cat_key}/{sub_key}): {e}")
    assert not errors, f"Invalid regex patterns:\n" + "\n".join(errors)


def test_all_pattern_ids_unique(signatures: dict):
    """All pattern IDs are unique across the entire file."""
    ids: list[str] = []
    for cat in signatures["categories"].values():
        for sub in cat.get("subcategories", {}).values():
            for pat in sub.get("patterns", []):
                ids.append(pat.get("id", ""))

    duplicates = [pid for pid in ids if ids.count(pid) > 1]
    unique_duplicates = list(set(duplicates))
    assert not unique_duplicates, f"Duplicate pattern IDs: {unique_duplicates}"


def test_each_category_has_patterns(signatures: dict):
    """Every category has at least one pattern."""
    for cat_key, cat in signatures["categories"].items():
        count = 0
        for sub in cat.get("subcategories", {}).values():
            count += len(sub.get("patterns", []))
        assert count > 0, f"Category '{cat_key}' has no patterns"


def test_each_pattern_has_required_fields(signatures: dict):
    """Every pattern has id, name, pattern, pattern_type, description."""
    required = {"id", "name", "pattern", "pattern_type", "description"}
    missing: list[str] = []
    for cat_key, cat in signatures["categories"].items():
        for sub_key, sub in cat.get("subcategories", {}).items():
            for pat in sub.get("patterns", []):
                pat_fields = set(pat.keys())
                diff = required - pat_fields
                if diff:
                    missing.append(f"{pat.get('id', '?')} missing: {diff}")
    assert not missing, f"Patterns with missing fields:\n" + "\n".join(missing)


def test_pattern_types_valid(signatures: dict):
    """All pattern_type values are 'regex' or 'literal'."""
    invalid: list[str] = []
    for cat in signatures["categories"].values():
        for sub in cat.get("subcategories", {}).values():
            for pat in sub.get("patterns", []):
                pt = pat.get("pattern_type", "")
                if pt not in ("regex", "literal"):
                    invalid.append(f"{pat.get('id', '?')}: {pt}")
    assert not invalid, f"Invalid pattern_types:\n" + "\n".join(invalid)


def test_category_has_severity_default(signatures: dict):
    """Each category has a severity_default."""
    valid_severities = {"critical", "high", "medium", "low", "info"}
    for cat_key, cat in signatures["categories"].items():
        sev = cat.get("severity_default", "")
        assert sev in valid_severities, (
            f"Category '{cat_key}' has invalid severity_default: '{sev}'"
        )
