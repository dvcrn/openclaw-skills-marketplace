#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTTP client for llama-server (OpenAI-compatible API)."""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

import requests

DEFAULT_SERVER = "http://127.0.0.1:8080"


class HaSClient:
    """Thin wrapper around llama-server's OpenAI-compatible API."""

    def __init__(self, server_url: str = DEFAULT_SERVER):
        self.base_url = server_url.rstrip("/")
        self._session = requests.Session()

    # ------------------------------------------------------------------
    # Chat completions
    # ------------------------------------------------------------------

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send a chat completion request and return the assistant reply.

        Args:
            messages: List of {"role": "user"|"assistant", "content": "..."}

        Returns:
            The model's response text.
        """
        url = f"{self.base_url}/v1/chat/completions"
        payload = {"messages": messages}
        try:
            resp = self._session.post(url, json=payload, timeout=120)
            resp.raise_for_status()
        except requests.ConnectionError:
            print(
                f"Error: Cannot connect to llama-server at {self.base_url}\n"
                f"Please start llama-server first:\n"
                f"  llama-server -m has_text_model.gguf -ngl 999 -c 8192 -np 1 -fa on -ctk q8_0 -ctv q8_0 --port 8080",
                file=sys.stderr,
            )
            sys.exit(1)
        except requests.HTTPError as e:
            print(f"Error: llama-server returned {e.response.status_code}: {e.response.text}", file=sys.stderr)
            sys.exit(1)

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
        except requests.ConnectionError:
            # Fallback: estimate tokens from character count
            # Qwen3 Chinese ratio: ~0.54 tokens/char
            return [0] * int(len(text) * 0.54)
        except requests.HTTPError:
            return [0] * int(len(text) * 0.54)

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
