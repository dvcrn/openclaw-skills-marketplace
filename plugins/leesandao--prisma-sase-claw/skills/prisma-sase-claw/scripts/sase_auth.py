#!/usr/bin/env python3
"""
Prisma SASE API Authentication Helper

Handles OAuth2 client credentials flow with automatic token caching and renewal.

Usage:
    from sase_auth import SASEAuth

    auth = SASEAuth(
        client_id="your_client_id",
        client_secret="your_client_secret",
        tsg_id="your_tsg_id"
    )

    # Get a valid token (auto-refreshes if expired)
    token = auth.get_token()

    # Get headers ready for API calls
    headers = auth.get_headers()

    # For endpoints requiring regional header
    headers = auth.get_headers(region="americas")
"""

import os
import sys
import time
import base64
import json

try:
    import requests
except ImportError:
    print("Error: 'requests' library is required. Install it with: pip install requests")
    sys.exit(1)


AUTH_URL = "https://auth.apps.paloaltonetworks.com/oauth2/access_token"
API_BASE = "https://api.sase.paloaltonetworks.com"

# Refresh token 60 seconds before actual expiry to avoid edge-case failures
TOKEN_REFRESH_BUFFER_SECONDS = 60


class SASEAuth:
    """Handles OAuth2 authentication for Prisma SASE API."""

    def __init__(self, client_id=None, client_secret=None, tsg_id=None):
        """
        Initialize with credentials. Falls back to environment variables if not provided:
          - PRISMA_CLIENT_ID
          - PRISMA_CLIENT_SECRET
          - PRISMA_TSG_ID
        """
        self.client_id = client_id or os.environ.get("PRISMA_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("PRISMA_CLIENT_SECRET")
        self.tsg_id = tsg_id or os.environ.get("PRISMA_TSG_ID")

        if not all([self.client_id, self.client_secret, self.tsg_id]):
            missing = []
            if not self.client_id:
                missing.append("client_id / PRISMA_CLIENT_ID")
            if not self.client_secret:
                missing.append("client_secret / PRISMA_CLIENT_SECRET")
            if not self.tsg_id:
                missing.append("tsg_id / PRISMA_TSG_ID")
            raise ValueError(f"Missing required credentials: {', '.join(missing)}")

        self._token = None
        self._token_expiry = 0

    def _request_token(self):
        """Request a new access token from the auth endpoint."""
        auth_string = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_string}",
        }

        data = {
            "grant_type": "client_credentials",
            "scope": f"tsg_id:{self.tsg_id}",
        }

        response = requests.post(AUTH_URL, headers=headers, data=data)

        if response.status_code != 200:
            raise RuntimeError(
                f"Authentication failed ({response.status_code}): {response.text}"
            )

        result = response.json()
        self._token = result["access_token"]
        self._token_expiry = time.time() + result.get("expires_in", 899)

        return self._token

    def get_token(self):
        """Get a valid access token. Automatically refreshes if expired or near expiry."""
        if (
            self._token is None
            or time.time() >= self._token_expiry - TOKEN_REFRESH_BUFFER_SECONDS
        ):
            self._request_token()
        return self._token

    def get_headers(self, region=None):
        """
        Get headers dict ready for API calls.

        Args:
            region: Optional region code for endpoints that require x-panw-region.
                    Valid values: americas, au, ca, de, europe, in, jp, sg, uk
        """
        headers = {
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": "application/json",
        }
        if region:
            headers["x-panw-region"] = region
        return headers

    def api_get(self, path, region=None, params=None):
        """Make an authenticated GET request to the SASE API."""
        url = f"{API_BASE}{path}"
        response = requests.get(url, headers=self.get_headers(region), params=params)
        response.raise_for_status()
        return response.json()

    def api_post(self, path, data, region=None, params=None):
        """Make an authenticated POST request to the SASE API."""
        url = f"{API_BASE}{path}"
        response = requests.post(
            url, headers=self.get_headers(region), json=data, params=params
        )
        response.raise_for_status()
        return response.json()

    def api_put(self, path, data, region=None, params=None):
        """Make an authenticated PUT request to the SASE API."""
        url = f"{API_BASE}{path}"
        response = requests.put(
            url, headers=self.get_headers(region), json=data, params=params
        )
        response.raise_for_status()
        return response.json()

    def api_delete(self, path, region=None, params=None):
        """Make an authenticated DELETE request to the SASE API."""
        url = f"{API_BASE}{path}"
        response = requests.delete(
            url, headers=self.get_headers(region), params=params
        )
        response.raise_for_status()
        if response.content:
            return response.json()
        return None


def main():
    """CLI usage: python sase_auth.py — prints a fresh token to stdout."""
    try:
        auth = SASEAuth()
        print(auth.get_token())
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(
            "\nSet environment variables:\n"
            "  export PRISMA_CLIENT_ID=your_client_id\n"
            "  export PRISMA_CLIENT_SECRET=your_client_secret\n"
            "  export PRISMA_TSG_ID=your_tsg_id",
            file=sys.stderr,
        )
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
