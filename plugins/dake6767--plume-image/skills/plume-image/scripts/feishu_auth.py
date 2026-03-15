#!/usr/bin/env python3
"""
Feishu authentication shared module
Provides Feishu config reading and tenant_access_token retrieval
"""

import json
import ssl
import urllib.request
from pathlib import Path

# OpenClaw config file path
OPENCLAW_CONFIG = Path.home() / ".openclaw" / "openclaw.json"

# Feishu API
FEISHU_API_BASE = "https://open.feishu.cn/open-apis"

# SSL context
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

# Token cache
_token_cache: dict = {}


def load_feishu_config(account: str = "main") -> dict | None:
    """Read Feishu config (appId, appSecret) from openclaw.json"""
    if not OPENCLAW_CONFIG.exists():
        return None
    try:
        with open(OPENCLAW_CONFIG) as f:
            config = json.load(f)
        feishu = config.get("channels", {}).get("feishu", {})
        # Prefer reading from accounts sub-structure, fallback to top-level appId/appSecret
        accounts = feishu.get("accounts", {})
        if account in accounts:
            acc = accounts[account]
            return {"app_id": acc.get("appId"), "app_secret": acc.get("appSecret")}
        # Top-level config (single account mode)
        if feishu.get("appId"):
            return {"app_id": feishu["appId"], "app_secret": feishu.get("appSecret")}
        return None
    except (json.JSONDecodeError, IOError):
        return None


def get_feishu_tenant_token(app_id: str, app_secret: str) -> str | None:
    """Get Feishu tenant_access_token"""
    url = f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
    data = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json; charset=utf-8",
    })
    try:
        with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXT) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        if result.get("code") != 0:
            return None
        return result.get("tenant_access_token")
    except Exception:
        return None


def get_token(account: str = "main") -> str | None:
    """Cached convenience function to get Feishu tenant_access_token"""
    if account in _token_cache:
        return _token_cache[account]

    config = load_feishu_config(account)
    if not config or not config.get("app_id"):
        return None

    token = get_feishu_tenant_token(config["app_id"], config["app_secret"])
    if token:
        _token_cache[account] = token
    return token
