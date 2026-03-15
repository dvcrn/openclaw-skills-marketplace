#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hide command — Anonymize text (Phase 1 of HaS workflow).

Internal workflow per chunk:
    NER → Hide (with or without mapping) → Tool-Pair → composite check
    → Model-Split if needed → mapping self-check → Model-Pair fallback
"""

from __future__ import annotations

import sys
from typing import Any, Dict, List, Optional, Tuple

from ..client import HaSClient
from ..pair import compute_pair_mapping
from ..prompts import (
    build_ner_messages,
    build_hide_with_messages,
    build_hide_without_messages,
    build_pair_messages,
    build_split_messages,
)
from ..mapping import (
    TAG_PATTERN,
    find_tags,
    has_tags,
    is_composite_tag,
    find_composite_entries,
    merge_mappings,
    parse_json_tolerant,
)
from ..chunker import chunk_text, DEFAULT_MAX_CHUNK_TOKENS


# ======================================================================
# Tool-Pair: algorithmic pair extraction
# ======================================================================

def _tool_pair(original: str, anonymized: str) -> Dict[str, List[str]]:
    """Algorithmic pair extraction using diff-based matching.

    Uses the self-contained pair.py module (copied from pair_core.py).
    """
    try:
        result = compute_pair_mapping(original, anonymized)
        return result.normalized_mapping
    except Exception:
        return {}


# ======================================================================
# Mapping self-check
# ======================================================================

def _mapping_self_check(
    anonymized_text: str,
    mapping: Dict[str, List[str]],
) -> bool:
    """Check if the mapping covers all tags in the anonymized text.

    Returns True if all tags in the text have corresponding mapping entries.
    """
    text_tags = set(find_tags(anonymized_text))
    if not text_tags:
        return True

    # Expand composite keys to individual tags
    mapped_tags = set()
    for key in mapping:
        for m in TAG_PATTERN.finditer(key):
            mapped_tags.add(m.group(0))

    # Check that all text tags are covered
    missing = text_tags - mapped_tags
    if missing:
        return False

    # Check all values are non-empty
    for key, values in mapping.items():
        if not values:
            return False

    return True


# ======================================================================
# Composite tag handling
# ======================================================================

def _handle_composite_tags(
    client: HaSClient,
    mapping: Dict[str, List[str]],
) -> Dict[str, List[str]]:
    """If mapping has composite keys, split them using Model-Split.

    Returns mapping with composite keys replaced by atomic keys.
    """
    atomic, composite = find_composite_entries(mapping)

    if not composite:
        return mapping

    # Build input for Model-Split
    composite_list = [{k: v} for k, v in composite.items()]

    messages = build_split_messages(composite_list)
    raw_output = client.chat(messages)
    split_result = parse_json_tolerant(raw_output)

    if isinstance(split_result, dict):
        # Merge split results with atomic entries
        for key, values in split_result.items():
            if isinstance(values, list):
                atomic[key] = values
            elif isinstance(values, str):
                atomic[key] = [values]
    elif isinstance(split_result, list):
        # List of dicts
        for item in split_result:
            if isinstance(item, dict):
                for key, values in item.items():
                    if isinstance(values, list):
                        atomic[key] = values
                    elif isinstance(values, str):
                        atomic[key] = [values]

    return atomic


# ======================================================================
# Single-chunk hide
# ======================================================================

def _hide_single_chunk(
    client: HaSClient,
    text: str,
    types: List[str],
    existing_mapping: Optional[Dict[str, List[str]]] = None,
) -> Tuple[str, Dict[str, List[str]]]:
    """Anonymize a single text chunk.

    Returns:
        (anonymized_text, mapping)
    """
    # Step 1: NER
    ner_messages = build_ner_messages(text, types)
    ner_output = client.chat(ner_messages)
    ner_result = parse_json_tolerant(ner_output)

    # Check if any entities were found
    if isinstance(ner_result, dict):
        has_entities = any(
            isinstance(v, list) and len(v) > 0
            for v in ner_result.values()
        )
    else:
        has_entities = False

    if not has_entities:
        # No entities found, return original text unchanged
        return text, existing_mapping or {}

    # Step 2: Hide
    # Use ner_output as-is (the raw model output string) for the assistant turn
    if existing_mapping:
        # Subsequent chunk: use hide_with
        messages = build_hide_with_messages(text, types, ner_output, existing_mapping)
    else:
        # First chunk: use hide_without
        messages = build_hide_without_messages(text, types, ner_output)

    anonymized_text = client.chat(messages)

    # Step 3: Tool-Pair — extract mapping
    tool_mapping = _tool_pair(text, anonymized_text)

    # Step 4: Handle composite tags
    if tool_mapping:
        tool_mapping = _handle_composite_tags(client, tool_mapping)

    # Step 5: Mapping self-check
    if _mapping_self_check(anonymized_text, tool_mapping):
        # Tool-Pair succeeded
        chunk_mapping = tool_mapping
    else:
        # Fallback: Model-Pair
        pair_messages = build_pair_messages(text, anonymized_text)
        pair_output = client.chat(pair_messages)
        model_mapping = parse_json_tolerant(pair_output)

        if isinstance(model_mapping, dict):
            # Normalize model output to Dict[str, List[str]]
            normalized = {}
            for k, v in model_mapping.items():
                if isinstance(v, list):
                    normalized[k] = [str(x) for x in v]
                elif isinstance(v, str):
                    normalized[k] = [v]
            chunk_mapping = _handle_composite_tags(client, normalized)
        else:
            # Both failed; use whatever Tool-Pair got
            chunk_mapping = tool_mapping

    # Merge with existing mapping
    if existing_mapping:
        merged = merge_mappings(existing_mapping, chunk_mapping)
    else:
        merged = chunk_mapping

    return anonymized_text, merged


# ======================================================================
# Public entry point
# ======================================================================

def run_hide(
    client: HaSClient,
    text: str,
    types: List[str],
    existing_mapping: Optional[Dict[str, List[str]]] = None,
    max_chunk_tokens: int = DEFAULT_MAX_CHUNK_TOKENS,
) -> Dict[str, Any]:
    """Anonymize text with automatic chunking and mapping accumulation.

    This is the main entry point for the hide command.
    Implements the full Phase 1 workflow from the HaS flowchart.

    Args:
        client: HaSClient connected to llama-server.
        text: Text to anonymize.
        types: Entity types to anonymize, e.g. ["人名", "地址"].
        existing_mapping: Optional pre-existing mapping for cross-document consistency.
        max_chunk_tokens: Maximum tokens per chunk.

    Returns:
        {
            "text": "anonymized text...",
            "mapping": {"<tag>": ["original_value"], ...},
            "chunks": N  # number of chunks processed (if > 1)
        }
    """
    chunks = chunk_text(text, client.count_tokens, max_chunk_tokens)

    if not chunks:
        return {"text": "", "mapping": existing_mapping or {}}

    accumulated_mapping = dict(existing_mapping) if existing_mapping else {}
    anonymized_parts: List[str] = []

    for i, chunk in enumerate(chunks):
        if len(chunks) > 1:
            print(
                f"Processing chunk {i + 1}/{len(chunks)} "
                f"({chunk.token_count} tokens, {len(chunk.text)} chars)...",
                file=sys.stderr,
            )

        anonymized_text, accumulated_mapping = _hide_single_chunk(
            client,
            chunk.text,
            types,
            existing_mapping=accumulated_mapping if accumulated_mapping else None,
        )
        anonymized_parts.append(anonymized_text)

    result = {
        "text": "".join(anonymized_parts),
        "mapping": accumulated_mapping,
    }

    if len(chunks) > 1:
        result["chunks"] = len(chunks)

    return result
