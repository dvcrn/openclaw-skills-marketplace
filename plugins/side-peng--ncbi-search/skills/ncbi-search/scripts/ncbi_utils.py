#!/usr/bin/env python3
"""
NCBI Utility Functions

Shared utilities for NCBI E-Utilities API calls.

Author: 亮子 (OpenClaw Assistant)
"""

import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional

# Rate limiting state
LAST_REQUEST_TIME = 0
MIN_REQUEST_INTERVAL = 0.34  # ~3 requests/second without API key
SESSION = None


def create_session():
    """Create a session with retry logic."""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def get_session():
    """Get or create the global session."""
    global SESSION
    if SESSION is None:
        SESSION = create_session()
    return SESSION


def rate_limit(api_key: Optional[str] = None):
    """Enforce rate limiting."""
    global LAST_REQUEST_TIME
    interval = 0.11 if api_key else MIN_REQUEST_INTERVAL
    elapsed = time.time() - LAST_REQUEST_TIME
    if elapsed < interval:
        time.sleep(interval - elapsed)
    LAST_REQUEST_TIME = time.time()


def clean_xml_tags(text: str) -> str:
    """Remove XML tags and clean whitespace."""
    import re
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()