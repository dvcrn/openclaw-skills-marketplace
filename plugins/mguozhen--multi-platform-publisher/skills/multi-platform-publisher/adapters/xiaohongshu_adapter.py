"""
Xiaohongshu (小红书) Adapter
=============================
Publishes notes to Xiaohongshu via the MCP (Model Context Protocol)
bridge or direct web API.

Required environment variables
------------------------------
- ``XHS_COOKIE``          – Browser cookie string for authentication
- ``XHS_MCP_ENDPOINT``    – (Optional) MCP server endpoint for Xiaohongshu
                            Defaults to ``http://localhost:3001``

Notes
-----
Xiaohongshu does not offer an official public API.  This adapter
supports two strategies:

1. **MCP mode** (preferred) – delegates to a running MCP server that
   wraps Xiaohongshu's internal endpoints.  The MCP server handles
   signing, anti-bot headers, and cookie refresh.
2. **Direct mode** – calls Xiaohongshu's web API directly using the
   cookie.  This is more fragile and may break when XHS updates its
   anti-bot measures.

The adapter tries MCP first and falls back to direct mode.
"""

from __future__ import annotations

import json
import os
import time
import hashlib
from pathlib import Path
from typing import Any

import requests

from .base_adapter import BaseAdapter


class XiaohongshuAdapter(BaseAdapter):
    """Adapter for Xiaohongshu (小红书)."""

    DISPLAY_NAME = "Xiaohongshu (小红书)"
    AUTH_METHOD = "MCP / Cookie"
    FEATURES = ["note", "image_upload"]
    MAX_TEXT_LENGTH = 1000
    MAX_IMAGES = 18

    # XHS web-API base
    WEB_BASE = "https://edith.xiaohongshu.com"
    # Default MCP endpoint
    DEFAULT_MCP_ENDPOINT = "http://localhost:3001"

    def __init__(self, config: dict | None = None):
        super().__init__(config or {})
        self.cookie = self.config.get("cookie") or os.environ.get("XHS_COOKIE", "")
        self.mcp_endpoint = (
            self.config.get("mcp_endpoint")
            or os.environ.get("XHS_MCP_ENDPOINT", self.DEFAULT_MCP_ENDPOINT)
        )

        if not self.cookie:
            raise ValueError(
                "Xiaohongshu credentials incomplete. Set XHS_COOKIE."
            )

        self._use_mcp: bool | None = None  # determined lazily

    # ------------------------------------------------------------------
    # Strategy detection
    # ------------------------------------------------------------------
    def _mcp_available(self) -> bool:
        """Check whether the MCP server is reachable."""
        if self._use_mcp is not None:
            return self._use_mcp
        try:
            resp = requests.get(f"{self.mcp_endpoint}/health", timeout=5)
            self._use_mcp = resp.status_code == 200
        except Exception:
            self._use_mcp = False
        return self._use_mcp

    # ------------------------------------------------------------------
    # MCP helpers
    # ------------------------------------------------------------------
    def _mcp_call(self, tool: str, arguments: dict) -> dict:
        """Invoke a tool on the MCP server."""
        payload = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": "tools/call",
            "params": {
                "name": tool,
                "arguments": arguments,
            },
        }
        resp = requests.post(
            self.mcp_endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json().get("result", {})

    # ------------------------------------------------------------------
    # Direct-mode helpers
    # ------------------------------------------------------------------
    def _web_headers(self) -> dict:
        """Build headers that mimic the XHS web client."""
        return {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Cookie": self.cookie,
            "Origin": "https://www.xiaohongshu.com",
            "Referer": "https://www.xiaohongshu.com/",
            "Content-Type": "application/json;charset=UTF-8",
        }

    def _generate_xhs_sign(self, api_path: str, payload: str = "") -> dict:
        """Generate a minimal X-S / X-T signing pair.

        .. warning::

           Xiaohongshu's signing algorithm changes frequently.  In
           production, prefer the MCP approach which keeps the signing
           logic up to date.
        """
        timestamp = str(int(time.time() * 1000))
        raw = f"{api_path}{payload}{timestamp}"
        x_s = hashlib.md5(raw.encode()).hexdigest()
        return {"X-S": x_s, "X-T": timestamp}

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------
    def publish(self, content: Any, images: list[str] | None = None) -> dict:
        """Publish a note to Xiaohongshu.

        *content* is expected to be a ``dict`` with keys:
        - ``title`` – note title
        - ``desc``  – note body text

        If *content* is a plain ``str``, it is wrapped automatically.
        """
        if isinstance(content, str):
            # Try to split first line as title
            lines = content.strip().split("\n", 1)
            title = lines[0].strip()[:20]
            desc = content
            content = {"title": title, "desc": desc}

        # Upload images
        image_ids: list[str] = []
        if images:
            for img in images[: self.MAX_IMAGES]:
                iid = self.upload_image(img)
                if iid:
                    image_ids.append(iid)

        if self._mcp_available():
            return self._publish_via_mcp(content, image_ids)
        return self._publish_direct(content, image_ids)

    def validate(self) -> bool:
        if self._mcp_available():
            try:
                result = self._mcp_call("xhs_get_user_info", {})
                return result.get("success", False)
            except Exception:
                return False
        # Direct mode – try fetching user info
        try:
            resp = requests.get(
                f"{self.WEB_BASE}/api/sns/web/v1/user/selfinfo",
                headers=self._web_headers(),
                timeout=15,
            )
            return resp.status_code == 200 and resp.json().get("success", False)
        except Exception:
            return False

    def upload_image(self, image_path: str) -> str | None:
        path = Path(image_path)
        if not path.exists():
            return None

        if self._mcp_available():
            return self._upload_image_mcp(path)
        return self._upload_image_direct(path)

    # ------------------------------------------------------------------
    # MCP publish / upload
    # ------------------------------------------------------------------
    def _publish_via_mcp(self, content: dict, image_ids: list[str]) -> dict:
        try:
            result = self._mcp_call(
                "xhs_create_note",
                {
                    "title": content.get("title", ""),
                    "desc": content.get("desc", ""),
                    "image_ids": image_ids,
                    "post_type": "normal",
                },
            )
            if result.get("success"):
                note_id = result.get("note_id", "")
                return {
                    "success": True,
                    "message": "Xiaohongshu note published via MCP.",
                    "url": f"https://www.xiaohongshu.com/explore/{note_id}" if note_id else None,
                    "note_id": note_id,
                }
            return {
                "success": False,
                "error": result.get("error", "MCP publish failed"),
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def _upload_image_mcp(self, path: Path) -> str | None:
        try:
            import base64

            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            result = self._mcp_call(
                "xhs_upload_image",
                {"image_base64": b64, "filename": path.name},
            )
            return result.get("image_id")
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Direct publish / upload
    # ------------------------------------------------------------------
    def _publish_direct(self, content: dict, image_ids: list[str]) -> dict:
        api_path = "/api/sns/web/v1/feed"
        payload_dict: dict[str, Any] = {
            "title": content.get("title", ""),
            "desc": content.get("desc", ""),
            "note_type": "normal",
            "image_info": {"images": [{"file_id": fid} for fid in image_ids]},
            "post_time": int(time.time()),
        }
        payload_str = json.dumps(payload_dict, ensure_ascii=False)
        headers = {**self._web_headers(), **self._generate_xhs_sign(api_path, payload_str)}

        try:
            resp = requests.post(
                f"{self.WEB_BASE}{api_path}",
                headers=headers,
                data=payload_str.encode("utf-8"),
                timeout=60,
            )
            data = resp.json()
            if data.get("success"):
                note_id = data.get("data", {}).get("note_id", "")
                return {
                    "success": True,
                    "message": "Xiaohongshu note published (direct mode).",
                    "url": f"https://www.xiaohongshu.com/explore/{note_id}" if note_id else None,
                    "note_id": note_id,
                }
            return {
                "success": False,
                "error": f"XHS API: {data.get('msg', 'Unknown error')}",
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def _upload_image_direct(self, path: Path) -> str | None:
        api_path = "/api/sns/web/v1/upload/image"
        headers = {**self._web_headers(), **self._generate_xhs_sign(api_path)}
        # Remove JSON content-type for multipart upload
        headers.pop("Content-Type", None)

        try:
            with open(path, "rb") as f:
                resp = requests.post(
                    f"{self.WEB_BASE}{api_path}",
                    headers=headers,
                    files={"file": (path.name, f, "image/jpeg")},
                    timeout=120,
                )
            data = resp.json()
            if data.get("success"):
                return data.get("data", {}).get("file_id")
            return None
        except Exception:
            return None
