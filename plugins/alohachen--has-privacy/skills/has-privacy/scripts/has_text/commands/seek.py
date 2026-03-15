#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""seek command — Restore anonymized text (Phase 3 of HaS workflow).

Internal workflow:
    Check for tags → Language detection → Tool-Seek or Model-Seek
    → Self-check → Model-Seek fallback
"""

from __future__ import annotations

import sys
from typing import Any, Dict, List, Optional

from ..client import HaSClient
from ..prompts import build_seek_messages
from ..mapping import has_tags
from ..lang import is_same_language


# ======================================================================
# Tool-Seek: deterministic string replacement
# ======================================================================

def _tool_seek(text: str, mapping: Dict[str, List[str]]) -> str:
    """Restore text by replacing tags with original values.

    Uses the first value in each tag's value array.
    """
    restored = text
    for tag, values in mapping.items():
        if values:
            restored = restored.replace(tag, str(values[0]))
    return restored


# ======================================================================
# Seek self-check
# ======================================================================

def _seek_self_check(restored_text: str) -> bool:
    """Check if the restored text still contains unreplaced tags.

    Returns True if no tags remain (success).
    """
    return not has_tags(restored_text)


# ======================================================================
# Public entry point
# ======================================================================

def run_seek(
    client: HaSClient,
    text: str,
    mapping: Dict[str, List[str]],
    original_text: Optional[str] = None,
) -> Dict[str, Any]:
    """Restore anonymized text to its original form.

    Implements the Phase 3 workflow:
    1. Check if text contains tags
    2. If same language → Tool-Seek (deterministic) → self-check
    3. If different language or self-check fails → Model-Seek (model-based)

    Language detection is automatic: compares the language of the input text
    against the language of the mapping values (which represent the original
    entities). If they differ (e.g., text was translated), Model-Seek is used.

    Args:
        client: HaSClient connected to llama-server.
        text: Text containing anonymized tags to restore.
        mapping: Mapping dictionary {tag: [original_values]}.
        original_text: Optional original text for language comparison.
                       If not provided, uses mapping values for detection.

    Returns:
        {"text": "restored original text..."}
    """
    # Quick check: no tags → return as-is
    if not has_tags(text):
        return {"text": text}

    # Determine if same language
    use_tool_seek = True
    if original_text:
        use_tool_seek = is_same_language(original_text, text)
    else:
        # Auto-detect: compare mapping values' language vs text language
        # Collect a sample of original entity values from the mapping
        entity_sample = " ".join(
            val for vals in mapping.values() for val in vals[:2]
        )
        if entity_sample.strip():
            use_tool_seek = is_same_language(entity_sample, text)

    if use_tool_seek:
        # Try Tool-Seek first (deterministic, fast)
        restored = _tool_seek(text, mapping)

        # Self-check
        if _seek_self_check(restored):
            return {"text": restored}

        # Self-check failed: some tags weren't replaced
        # Fall through to Model-Seek
        print(
            "Tool-Seek self-check failed, falling back to Model-Seek...",
            file=sys.stderr,
        )

    # Model-Seek (handles cross-language or unreplaceable tags)
    messages = build_seek_messages(mapping, text)
    model_restored = client.chat(messages)

    return {"text": model_restored}
