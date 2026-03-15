"""
Config Loader
=============
Loads platform credentials and settings from multiple sources with the
following precedence (highest → lowest):

1. Environment variables
2. ``~/.openclaw/openclaw.json`` (``skills.entries.multi-platform-publisher``)
3. ``config.json`` in the skill directory
4. Built-in defaults
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class ConfigLoader:
    """Load and merge configuration for multi-platform-publisher."""

    SKILL_NAME = "multi-platform-publisher"

    # Mapping: config key → environment variable(s)
    ENV_MAP: dict[str, dict[str, str]] = {
        "twitter": {
            "api_key": "TWITTER_API_KEY",
            "api_secret": "TWITTER_API_SECRET",
            "access_token": "TWITTER_ACCESS_TOKEN",
            "access_token_secret": "TWITTER_ACCESS_TOKEN_SECRET",
        },
        "linkedin": {
            "access_token": "LINKEDIN_ACCESS_TOKEN",
            "person_urn": "LINKEDIN_PERSON_URN",
        },
        "wechat": {
            "appid": "WECHAT_APPID",
            "appsecret": "WECHAT_APPSECRET",
        },
        "xiaohongshu": {
            "cookie": "XHS_COOKIE",
            "mcp_endpoint": "XHS_MCP_ENDPOINT",
        },
    }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @classmethod
    def load(cls) -> dict[str, Any]:
        """Return the merged configuration dictionary."""
        config: dict[str, Any] = {}

        # Layer 1 – built-in defaults
        config = cls._defaults()

        # Layer 2 – skill-local config.json
        cls._merge(config, cls._load_local_config())

        # Layer 3 – OpenClaw global config
        cls._merge(config, cls._load_openclaw_config())

        # Layer 4 – environment variables (highest priority)
        cls._merge(config, cls._load_env())

        return config

    # ------------------------------------------------------------------
    # Loaders
    # ------------------------------------------------------------------
    @staticmethod
    def _defaults() -> dict[str, Any]:
        return {
            "twitter": {},
            "linkedin": {},
            "wechat": {},
            "xiaohongshu": {},
            "settings": {
                "default_platforms": "all",
                "content_adaptation": True,
                "auto_hashtags": True,
                "dry_run": False,
            },
        }

    @classmethod
    def _load_env(cls) -> dict[str, Any]:
        """Read credentials from environment variables."""
        result: dict[str, Any] = {}
        for platform, mapping in cls.ENV_MAP.items():
            section: dict[str, str] = {}
            for key, env_var in mapping.items():
                val = os.environ.get(env_var, "")
                if val:
                    section[key] = val
            if section:
                result[platform] = section
        return result

    @classmethod
    def _load_openclaw_config(cls) -> dict[str, Any]:
        """Read from ``~/.openclaw/openclaw.json``."""
        path = Path.home() / ".openclaw" / "openclaw.json"
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            entry = (
                data.get("skills", {})
                .get("entries", {})
                .get(cls.SKILL_NAME, {})
            )
            env_section = entry.get("env", {})
            config_section = entry.get("config", {})

            result: dict[str, Any] = {}
            # Map env values back to platform sections
            for platform, mapping in cls.ENV_MAP.items():
                section: dict[str, str] = {}
                for key, env_var in mapping.items():
                    if env_var in env_section:
                        section[key] = env_section[env_var]
                if section:
                    result[platform] = section

            if config_section:
                result["settings"] = config_section

            return result
        except (json.JSONDecodeError, KeyError):
            return {}

    @classmethod
    def _load_local_config(cls) -> dict[str, Any]:
        """Read from ``config.json`` next to this file."""
        path = Path(__file__).resolve().parent.parent / "config.json"
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, KeyError):
            return {}

    # ------------------------------------------------------------------
    # Merge helper
    # ------------------------------------------------------------------
    @staticmethod
    def _merge(base: dict, override: dict) -> None:
        """Recursively merge *override* into *base* in place."""
        for key, value in override.items():
            if (
                key in base
                and isinstance(base[key], dict)
                and isinstance(value, dict)
            ):
                ConfigLoader._merge(base[key], value)
            else:
                base[key] = value
