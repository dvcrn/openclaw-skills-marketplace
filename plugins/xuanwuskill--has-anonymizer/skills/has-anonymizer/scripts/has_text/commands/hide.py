#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hide command — Anonymize text (Phase 1 of HaS workflow).

Internal workflow per chunk:
    NER → Hide (with or without mapping) → Model-Pair → composite check
    → Model-Split if needed → mapping self-check
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple

from ..chunker import DEFAULT_MAX_CHUNK_TOKENS, take_chunk
from ..client import HaSClient
from ..mapping import (
    TAG_PATTERN,
    find_composite_entries,
    find_tags,
    merge_mappings,
    normalize_mapping_dict,
    parse_json_tolerant,
)
from ..parallel import DEFAULT_MAX_PARALLEL_REQUESTS, resolve_parallel_workers
from ..prompts import (
    build_hide_with_messages,
    build_hide_without_messages,
    build_ner_messages,
    build_pair_messages,
    build_split_messages,
)
from ..validation import normalize_entity_map


@dataclass(frozen=True)
class HideDocument:
    """Plaintext input for batch anonymization."""

    source: str
    text: str


def estimate_hide_batch_request_count(documents: List[HideDocument]) -> int:
    """Estimate how many hide workers will actually need the model."""
    return sum(1 for document in documents if document.text and document.text.strip())


def _warn(message: str) -> None:
    """Emit a non-fatal warning to stderr."""
    print(f"Warning: {message}", file=sys.stderr)


def _clone_hide_client(client: HaSClient) -> HaSClient:
    """Create a fresh client per worker to avoid sharing HTTP sessions."""
    client_cls = client.__class__
    try:
        return client_cls(client.base_url)
    except TypeError:
        return HaSClient(client.base_url)


def _compute_chunk_budget(
    count_tokens,
    max_chunk_tokens: int,
    mapping: Optional[Dict[str, List[str]]],
) -> int:
    """Shrink the text budget as the carried mapping grows.

    `hide_with` injects the full accumulated mapping into every later chunk.
    Subtracting its tokenized size keeps later requests inside the 8K context
    window instead of chunking solely on the raw source text.
    """
    if not mapping:
        return max_chunk_tokens

    mapping_json = json.dumps(mapping, ensure_ascii=False, separators=(",", ":"))
    mapping_tokens = count_tokens(mapping_json)
    budget = max_chunk_tokens - mapping_tokens
    if budget <= 0:
        raise RuntimeError(
            "Accumulated mapping no longer leaves room for more text chunks "
            f"({len(mapping)} entries, ~{mapping_tokens} mapping tokens). "
            "Split the document or reduce the carried mapping."
        )
    return budget


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

    normalized_split: Dict[str, List[str]] = {}

    try:
        if isinstance(split_result, dict):
            normalized_split = normalize_mapping_dict(split_result)
        elif isinstance(split_result, list):
            merged_split: Dict[str, Any] = {}
            for item in split_result:
                if not isinstance(item, dict):
                    raise ValueError("Model-Split returned a non-object entry")
                merged_split.update(item)
            normalized_split = normalize_mapping_dict(merged_split)
        else:
            raise ValueError("Model-Split did not return valid JSON")
    except ValueError as exc:
        _warn(f"Model-Split failed; keeping composite mapping entries intact ({exc})")
        return mapping

    merged = dict(atomic)
    merged.update(normalized_split)

    for composite_key, values in composite.items():
        component_tags = [m.group(0) for m in TAG_PATTERN.finditer(composite_key)]
        if not component_tags or not all(tag in merged for tag in component_tags):
            merged[composite_key] = values

    return merged


# ======================================================================
# Model-Pair mapping extraction
# ======================================================================

def _model_pair(
    client: HaSClient,
    original_text: str,
    anonymized_text: str,
) -> Dict[str, List[str]]:
    """Extract mapping via the model and reject incomplete results."""
    pair_messages = build_pair_messages(original_text, anonymized_text)
    raw_output = client.chat(pair_messages)
    pair_result = parse_json_tolerant(raw_output)
    if not isinstance(pair_result, dict):
        raise RuntimeError("Model-Pair did not return a JSON object")

    try:
        mapping = normalize_mapping_dict(pair_result)
    except ValueError as exc:
        raise RuntimeError(f"Model-Pair returned invalid mapping ({exc})") from exc

    mapping = _handle_composite_tags(client, mapping)
    if not _mapping_self_check(anonymized_text, mapping):
        raise RuntimeError("Model-Pair mapping did not cover all tags in anonymized text")

    return mapping


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
    ner_result = normalize_entity_map(
        parse_json_tolerant(ner_output),
        context="NER output",
    )
    has_entities = any(ner_result.values())

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

    # Step 3: Model-Pair — extract mapping
    chunk_mapping = _model_pair(client, text, anonymized_text)

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
    progress_label: Optional[str] = None,
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
    if not text or not text.strip():
        return {"text": "", "mapping": existing_mapping or {}}

    accumulated_mapping = dict(existing_mapping) if existing_mapping else {}
    anonymized_parts: List[str] = []
    remaining_text = text
    chunk_count = 0

    while remaining_text:
        chunk_budget = _compute_chunk_budget(
            client.count_tokens,
            max_chunk_tokens,
            accumulated_mapping if accumulated_mapping else None,
        )
        chunk = take_chunk(
            remaining_text,
            client.count_tokens,
            chunk_budget,
            index=chunk_count,
        )
        if chunk is None:
            break

        next_remaining = remaining_text[len(chunk.text):]
        if chunk_count > 0 or next_remaining:
            prefix = f"{progress_label}: " if progress_label else ""
            print(
                f"{prefix}Processing chunk {chunk_count + 1} "
                f"({chunk.token_count} tokens, {len(chunk.text)} chars; "
                f"text budget {chunk_budget})...",
                file=sys.stderr,
            )

        anonymized_text, accumulated_mapping = _hide_single_chunk(
            client,
            chunk.text,
            types,
            existing_mapping=accumulated_mapping if accumulated_mapping else None,
        )
        anonymized_parts.append(anonymized_text)
        remaining_text = next_remaining
        chunk_count += 1

    result = {
        "text": "".join(anonymized_parts),
        "mapping": accumulated_mapping,
    }

    if chunk_count > 1:
        result["chunks"] = chunk_count

    return result


def run_hide_batch(
    client: HaSClient,
    documents: List[HideDocument],
    types: List[str],
    existing_mapping: Optional[Dict[str, List[str]]] = None,
    max_chunk_tokens: int = DEFAULT_MAX_CHUNK_TOKENS,
    max_parallel_requests: int = DEFAULT_MAX_PARALLEL_REQUESTS,
) -> Dict[str, Any]:
    """Anonymize multiple plaintext documents with independent per-file mappings."""
    if max_parallel_requests < 1:
        raise ValueError("max_parallel_requests must be >= 1")

    if not documents:
        return {"results": [], "count": 0}

    results: List[Optional[Dict[str, Any]]] = [None] * len(documents)

    def _process(index: int, document: HideDocument) -> Dict[str, Any]:
        hidden = run_hide(
            _clone_hide_client(client),
            document.text,
            types,
            existing_mapping=existing_mapping,
            max_chunk_tokens=max_chunk_tokens,
            progress_label=Path(document.source).name,
        )
        hidden["file"] = document.source
        return hidden

    if len(documents) == 1 or max_parallel_requests == 1:
        for index, document in enumerate(documents):
            results[index] = _process(index, document)
    else:
        max_workers = resolve_parallel_workers(len(documents), max_parallel_requests)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(_process, index, document): index
                for index, document in enumerate(documents)
            }
            try:
                for future in as_completed(futures):
                    index = futures[future]
                    results[index] = future.result()
            except BaseException:
                for future in futures:
                    future.cancel()
                raise

    materialized = [result for result in results if result is not None]
    return {"results": materialized, "count": len(materialized)}
