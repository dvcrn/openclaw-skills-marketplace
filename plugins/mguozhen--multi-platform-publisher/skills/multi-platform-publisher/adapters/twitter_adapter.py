"""
Twitter / X Adapter
===================
Publishes tweets and threads via the X API v2 using OAuth 1.0a
authentication (User Context).

Required environment variables
------------------------------
- ``TWITTER_API_KEY``              – Consumer / API key
- ``TWITTER_API_SECRET``           – Consumer / API secret
- ``TWITTER_ACCESS_TOKEN``         – User access token
- ``TWITTER_ACCESS_TOKEN_SECRET``  – User access-token secret

References
----------
- X API v2 Tweets endpoint: https://developer.x.com/en/docs/x-api/tweets/manage-tweets/api-reference/post-tweets
- Media Upload v1.1:        https://developer.x.com/en/docs/x-api/media/upload-media/api-reference/post-media-upload
"""

from __future__ import annotations

import os
import time
import json
import hashlib
import hmac
import base64
import urllib.parse
from pathlib import Path
from typing import Any

import requests

from .base_adapter import BaseAdapter


class TwitterAdapter(BaseAdapter):
    """Adapter for X / Twitter using OAuth 1.0a."""

    DISPLAY_NAME = "X / Twitter"
    AUTH_METHOD = "OAuth 1.0a"
    FEATURES = ["tweet", "thread", "image_upload"]
    MAX_TEXT_LENGTH = 280
    MAX_IMAGES = 4

    # API endpoints
    TWEET_URL = "https://api.x.com/2/tweets"
    MEDIA_UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"
    VERIFY_URL = "https://api.x.com/2/users/me"

    def __init__(self, config: dict | None = None):
        super().__init__(config or {})
        self.api_key = self.config.get("api_key") or os.environ.get("TWITTER_API_KEY", "")
        self.api_secret = self.config.get("api_secret") or os.environ.get("TWITTER_API_SECRET", "")
        self.access_token = self.config.get("access_token") or os.environ.get("TWITTER_ACCESS_TOKEN", "")
        self.access_token_secret = self.config.get("access_token_secret") or os.environ.get(
            "TWITTER_ACCESS_TOKEN_SECRET", ""
        )

        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            raise ValueError(
                "Twitter credentials incomplete. "
                "Set TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, "
                "and TWITTER_ACCESS_TOKEN_SECRET."
            )

    # ------------------------------------------------------------------
    # OAuth 1.0a signing
    # ------------------------------------------------------------------
    def _oauth_signature(
        self,
        method: str,
        url: str,
        params: dict,
    ) -> str:
        """Generate an OAuth 1.0a signature."""
        sorted_params = "&".join(
            f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(str(v), safe='')}"
            for k, v in sorted(params.items())
        )
        base_string = (
            f"{method.upper()}&"
            f"{urllib.parse.quote(url, safe='')}&"
            f"{urllib.parse.quote(sorted_params, safe='')}"
        )
        signing_key = (
            f"{urllib.parse.quote(self.api_secret, safe='')}&"
            f"{urllib.parse.quote(self.access_token_secret, safe='')}"
        )
        signature = hmac.new(
            signing_key.encode("utf-8"),
            base_string.encode("utf-8"),
            hashlib.sha1,
        ).digest()
        return base64.b64encode(signature).decode("utf-8")

    def _oauth_header(self, method: str, url: str, extra_params: dict | None = None) -> str:
        """Build the ``Authorization: OAuth …`` header value."""
        oauth_params = {
            "oauth_consumer_key": self.api_key,
            "oauth_nonce": base64.b64encode(os.urandom(32)).decode("utf-8").rstrip("="),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_token": self.access_token,
            "oauth_version": "1.0",
        }
        all_params = {**oauth_params, **(extra_params or {})}
        oauth_params["oauth_signature"] = self._oauth_signature(method, url, all_params)

        header_parts = ", ".join(
            f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"'
            for k, v in sorted(oauth_params.items())
        )
        return f"OAuth {header_parts}"

    def _request(
        self,
        method: str,
        url: str,
        json_body: dict | None = None,
        data: dict | None = None,
        files: dict | None = None,
    ) -> requests.Response:
        """Send an OAuth 1.0a-signed request."""
        extra = {}
        if data:
            extra = dict(data)
        headers = {"Authorization": self._oauth_header(method, url, extra)}
        kwargs: dict[str, Any] = {"headers": headers, "timeout": 60}
        if json_body is not None:
            headers["Content-Type"] = "application/json"
            kwargs["data"] = json.dumps(json_body)
        elif data is not None:
            kwargs["data"] = data
        if files is not None:
            kwargs["files"] = files
            # Remove Content-Type so requests can set multipart boundary
            headers.pop("Content-Type", None)
        return requests.request(method, url, **kwargs)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------
    def publish(self, content: Any, images: list[str] | None = None) -> dict:
        """Publish a tweet or thread.

        *content* may be a ``str`` (single tweet) or ``list[str]`` (thread).
        """
        media_ids = []
        if images:
            for img in images[: self.MAX_IMAGES]:
                mid = self.upload_image(img)
                if mid:
                    media_ids.append(mid)

        if isinstance(content, list):
            return self._publish_thread(content, media_ids)
        return self._publish_single(content, media_ids)

    def validate(self) -> bool:
        resp = self._request("GET", self.VERIFY_URL)
        return resp.status_code == 200

    def upload_image(self, image_path: str) -> str | None:
        path = Path(image_path)
        if not path.exists():
            return None
        with open(path, "rb") as f:
            resp = self._request(
                "POST",
                self.MEDIA_UPLOAD_URL,
                files={"media": (path.name, f, "application/octet-stream")},
            )
        if resp.status_code in (200, 201):
            return resp.json().get("media_id_string")
        return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _publish_single(self, text: str, media_ids: list[str]) -> dict:
        payload: dict[str, Any] = {"text": text}
        if media_ids:
            payload["media"] = {"media_ids": media_ids}
        resp = self._request("POST", self.TWEET_URL, json_body=payload)
        if resp.status_code in (200, 201):
            data = resp.json().get("data", {})
            tweet_id = data.get("id", "")
            return {
                "success": True,
                "message": "Tweet published successfully.",
                "url": f"https://x.com/i/status/{tweet_id}",
                "tweet_id": tweet_id,
            }
        return {
            "success": False,
            "error": f"Twitter API error {resp.status_code}: {resp.text}",
        }

    def _publish_thread(self, tweets: list[str], media_ids: list[str]) -> dict:
        """Post a thread by chaining ``reply_to`` tweet IDs."""
        published: list[dict] = []
        previous_id: str | None = None

        for idx, text in enumerate(tweets):
            payload: dict[str, Any] = {"text": text}
            # Attach images only to the first tweet of the thread
            if idx == 0 and media_ids:
                payload["media"] = {"media_ids": media_ids}
            if previous_id:
                payload["reply"] = {"in_reply_to_tweet_id": previous_id}

            resp = self._request("POST", self.TWEET_URL, json_body=payload)
            if resp.status_code not in (200, 201):
                return {
                    "success": False,
                    "error": (
                        f"Thread failed at tweet #{idx + 1}: "
                        f"API {resp.status_code} – {resp.text}"
                    ),
                    "published_tweets": published,
                }
            data = resp.json().get("data", {})
            tweet_id = data.get("id", "")
            previous_id = tweet_id
            published.append({"index": idx, "tweet_id": tweet_id})

        first_id = published[0]["tweet_id"] if published else ""
        return {
            "success": True,
            "message": f"Thread published ({len(published)} tweets).",
            "url": f"https://x.com/i/status/{first_id}",
            "tweets": published,
        }
