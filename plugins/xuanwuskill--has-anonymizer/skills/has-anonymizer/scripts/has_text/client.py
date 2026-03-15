#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTTP client for llama-server (OpenAI-compatible API)."""

from __future__ import annotations

from typing import Dict, List

DEFAULT_SERVER = "http://127.0.0.1:8080"

# Per-script tokens-per-character ratios, measured against the HaS 0.6B Q8
# model tokenizer on representative text blocks:
#
#   Chinese (CJK Unified):  0.56  (540 chars → 302 tokens)
#   Japanese (hiragana/katakana + CJK): 0.74 measured, padded to 0.95
#   Korean (hangul):        0.67  (121 chars → 81 tokens)
#   Latin letters (English prose): 0.20  (1693 chars → 341 tokens)
#   Digits / ASCII punct:   ~0.55  (individual tokens in most contexts)
#   Fallback:               0.56  (conservative, avoids under-estimation)
#
# The Latin letter ratio (0.20) reflects subword merging in continuous English
# text. Digits and punctuation are usually emitted as individual tokens, so
# they get a higher ratio. We pad the letter ratio from 0.20 → 0.25 for safety.
_RATIO_CJK = 0.56
_RATIO_KANA = 0.95
_RATIO_HANGUL = 0.67
_RATIO_LATIN_LETTER = 0.25
_RATIO_DIGIT_PUNCT = 0.55
_RATIO_FALLBACK = 0.56


def _char_ratio(code: int) -> float:
    """Return the per-character token ratio for a Unicode code point."""
    # ASCII letters benefit from subword merging
    if 65 <= code <= 90 or 97 <= code <= 122:
        return _RATIO_LATIN_LETTER
    # ASCII digits and punctuation are mostly individual tokens
    if code < 0x0100:
        return _RATIO_DIGIT_PUNCT
    # CJK Unified Ideographs (shared by Chinese and Japanese kanji)
    if 0x4E00 <= code <= 0x9FFF:
        return _RATIO_CJK
    # Hiragana / Katakana
    if 0x3040 <= code <= 0x30FF:
        return _RATIO_KANA
    # Hangul Syllables
    if 0xAC00 <= code <= 0xD7AF:
        return _RATIO_HANGUL
    # CJK Extension A/B, Compatibility Ideographs, etc.
    if 0x3400 <= code <= 0x4DBF or 0x20000 <= code <= 0x2A6DF:
        return _RATIO_CJK
    # CJK punctuation, symbols, fullwidth forms
    if 0x3000 <= code <= 0x303F or 0xFF00 <= code <= 0xFFEF:
        return _RATIO_CJK
    return _RATIO_FALLBACK


def estimate_token_count(text: str) -> int:
    """Cheap local token estimate used when llama-server is unavailable.

    Uses per-script ratios calibrated against the HaS 0.6B model tokenizer
    so that CJK-heavy text is not under-estimated (which would produce
    chunks that exceed the model's context window).
    """
    if not text:
        return 0
    total = sum(_char_ratio(ord(ch)) for ch in text)
    return max(1, int(total))


def _load_requests():
    """Import requests lazily so tests can import command modules without it."""
    try:
        import requests
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The 'requests' package is required to talk to llama-server. "
            "Run via has-text/has_text_entry.py or install requests first."
        ) from exc
    return requests


class HaSClient:
    """Thin wrapper around llama-server's OpenAI-compatible API."""

    def __init__(self, server_url: str = DEFAULT_SERVER):
        self.base_url = server_url.rstrip("/")
        self._requests = _load_requests()
        self._session = self._requests.Session()

    # ------------------------------------------------------------------
    # Chat completions
    # ------------------------------------------------------------------

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send a chat completion request and return the assistant reply.

        Args:
            messages: List of {"role": "user"|"assistant", "content": "..."}

        Returns:
            The model's response text.

        Raises:
            RuntimeError: If the server is unreachable or returns an error.
        """
        url = f"{self.base_url}/v1/chat/completions"
        payload = {"messages": messages}
        try:
            resp = self._session.post(url, json=payload, timeout=120)
            resp.raise_for_status()
        except self._requests.ConnectionError:
            raise RuntimeError(
                f"Cannot connect to llama-server at {self.base_url}\n"
                f"Please start llama-server first:\n"
                f"  llama-server -m has_text_model.gguf -ngl 999 -c 8192 -fa on -ctk q8_0 -ctv q8_0 --port 8080\n"
                f"For parallel scan/seek, add --parallel N (or -np N) and scale -c to 8192 * N "
                f"so each slot keeps the full 8K context budget."
            )
        except self._requests.HTTPError as e:
            raise RuntimeError(
                f"llama-server returned {e.response.status_code}: {e.response.text}"
            ) from e

        data = resp.json()
        return data["choices"][0]["message"]["content"]

    # ------------------------------------------------------------------
    # Tokenize (for chunking)
    # ------------------------------------------------------------------

    def tokenize(self, text: str) -> List[int]:
        """Tokenize text using llama-server's /tokenize endpoint.

        Args:
            text: Text to tokenize.

        Returns:
            List of token IDs.
        """
        url = f"{self.base_url}/tokenize"
        try:
            resp = self._session.post(url, json={"content": text}, timeout=30)
            resp.raise_for_status()
        except self._requests.ConnectionError:
            return [0] * estimate_token_count(text)
        except self._requests.HTTPError:
            return [0] * estimate_token_count(text)

        data = resp.json()
        return data.get("tokens", [])

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string.

        Args:
            text: Text to count tokens for.

        Returns:
            Number of tokens.
        """
        return len(self.tokenize(text))

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    def health(self) -> bool:
        """Check if llama-server is reachable."""
        try:
            resp = self._session.get(f"{self.base_url}/health", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
