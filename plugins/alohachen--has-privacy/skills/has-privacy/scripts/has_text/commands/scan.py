#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scan command — Identify sensitive entities in text (NER only, no anonymization)."""

from __future__ import annotations

import json
import sys
from typing import Dict, List, Optional

from ..client import HaSClient
from ..prompts import build_ner_messages
from ..mapping import parse_json_tolerant
from ..chunker import chunk_text, DEFAULT_MAX_CHUNK_TOKENS


def run_scan(
    client: HaSClient,
    text: str,
    types: List[str],
    max_chunk_tokens: int = DEFAULT_MAX_CHUNK_TOKENS,
) -> Dict[str, List[str]]:
    """Scan text for sensitive entities.

    For short text, runs a single NER call.
    For long text, chunks and merges NER results.

    Returns:
        {"entities": {"人名": ["张三", "李四"], "地址": ["北京"], ...}}
    """
    chunks = chunk_text(text, client.count_tokens, max_chunk_tokens)

    merged_entities: Dict[str, List[str]] = {}

    for chunk in chunks:
        messages = build_ner_messages(chunk.text, types)
        raw_output = client.chat(messages)
        ner_result = parse_json_tolerant(raw_output)

        if not isinstance(ner_result, dict):
            print(
                f"Warning: NER output for chunk {chunk.index} is not valid JSON, skipping.",
                file=sys.stderr,
            )
            continue

        # Merge entities
        for entity_type, entities in ner_result.items():
            if not isinstance(entities, list):
                continue
            if entity_type not in merged_entities:
                merged_entities[entity_type] = []
            for entity in entities:
                entity_str = str(entity).strip()
                if entity_str and entity_str not in merged_entities[entity_type]:
                    merged_entities[entity_type].append(entity_str)

    return {"entities": merged_entities}
