"""
LinkedIn Adapter
================
Publishes posts and articles to LinkedIn via the Community Management API
using OAuth 2.0 Bearer tokens.

Required environment variables
------------------------------
- ``LINKEDIN_ACCESS_TOKEN``  – OAuth 2.0 access token with ``w_member_social`` scope
- ``LINKEDIN_PERSON_URN``    – (Optional) Author URN, e.g. ``urn:li:person:abc123``.
                               If omitted the adapter fetches it via ``/v2/userinfo``.

References
----------
- Posts API: https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api
- Images API: https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/images-api
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests

from .base_adapter import BaseAdapter


class LinkedInAdapter(BaseAdapter):
    """Adapter for LinkedIn using OAuth 2.0."""

    DISPLAY_NAME = "LinkedIn"
    AUTH_METHOD = "OAuth 2.0"
    FEATURES = ["article", "post", "image_upload"]
    MAX_TEXT_LENGTH = 3000
    MAX_IMAGES = 9

    BASE_URL = "https://api.linkedin.com"
    POSTS_URL = f"{BASE_URL}/rest/posts"
    IMAGES_URL = f"{BASE_URL}/rest/images"
    USERINFO_URL = f"{BASE_URL}/v2/userinfo"

    def __init__(self, config: dict | None = None):
        super().__init__(config or {})
        self.access_token = self.config.get("access_token") or os.environ.get(
            "LINKEDIN_ACCESS_TOKEN", ""
        )
        self.person_urn = self.config.get("person_urn") or os.environ.get(
            "LINKEDIN_PERSON_URN", ""
        )

        if not self.access_token:
            raise ValueError(
                "LinkedIn credentials incomplete. Set LINKEDIN_ACCESS_TOKEN."
            )

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------
    def _headers(self, extra: dict | None = None) -> dict:
        h = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202402",
            "Content-Type": "application/json",
        }
        if extra:
            h.update(extra)
        return h

    def _get_person_urn(self) -> str:
        """Fetch the authenticated user's person URN if not configured."""
        if self.person_urn:
            return self.person_urn
        resp = requests.get(self.USERINFO_URL, headers=self._headers(), timeout=30)
        resp.raise_for_status()
        sub = resp.json().get("sub", "")
        self.person_urn = f"urn:li:person:{sub}"
        return self.person_urn

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------
    def publish(self, content: Any, images: list[str] | None = None) -> dict:
        """Publish a post (or article) to LinkedIn.

        *content* is expected to be a ``str`` – the adapted post body.
        """
        author = self._get_person_urn()

        # Upload images if provided
        image_urns: list[str] = []
        if images:
            for img in images[: self.MAX_IMAGES]:
                urn = self.upload_image(img)
                if urn:
                    image_urns.append(urn)

        payload: dict[str, Any] = {
            "author": author,
            "commentary": content[: self.MAX_TEXT_LENGTH],
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
        }

        # Attach images
        if image_urns:
            payload["content"] = {
                "multiImage": {
                    "images": [{"id": urn, "altText": ""} for urn in image_urns],
                }
            }

        resp = requests.post(
            self.POSTS_URL,
            headers=self._headers(),
            data=json.dumps(payload),
            timeout=60,
        )

        if resp.status_code in (200, 201):
            post_id = resp.headers.get("x-restli-id", "")
            return {
                "success": True,
                "message": "LinkedIn post published successfully.",
                "url": f"https://www.linkedin.com/feed/update/{post_id}/" if post_id else None,
                "post_id": post_id,
            }
        return {
            "success": False,
            "error": f"LinkedIn API error {resp.status_code}: {resp.text}",
        }

    def validate(self) -> bool:
        resp = requests.get(self.USERINFO_URL, headers=self._headers(), timeout=30)
        return resp.status_code == 200

    def upload_image(self, image_path: str) -> str | None:
        """Upload an image to LinkedIn and return the image URN.

        The flow is:
        1. ``POST /rest/images?action=initializeUpload`` → get upload URL + image URN.
        2. ``PUT <uploadUrl>`` with binary data.
        """
        path = Path(image_path)
        if not path.exists():
            return None

        author = self._get_person_urn()

        # Step 1 – initialise upload
        init_payload = {
            "initializeUploadRequest": {
                "owner": author,
            }
        }
        resp = requests.post(
            f"{self.IMAGES_URL}?action=initializeUpload",
            headers=self._headers(),
            data=json.dumps(init_payload),
            timeout=30,
        )
        if resp.status_code not in (200, 201):
            return None

        data = resp.json().get("value", {})
        upload_url = data.get("uploadUrl", "")
        image_urn = data.get("image", "")

        if not upload_url or not image_urn:
            return None

        # Step 2 – upload binary
        with open(path, "rb") as f:
            put_resp = requests.put(
                upload_url,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/octet-stream",
                },
                data=f,
                timeout=120,
            )
        if put_resp.status_code in (200, 201):
            return image_urn
        return None
