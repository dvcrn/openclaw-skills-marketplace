#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared utilities for gitcode-issue-reply scripts."""

import sys
import re
import json
import os
import subprocess
import time

from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

GITCODE_API_BASE = "https://api.gitcode.com/api/v5"
API_RETRY_TIMES = 2
API_RETRY_INTERVAL = 2


def init_windows_encoding():
    """Reconfigure stdout/stderr to UTF-8 on Windows."""
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass


def print_json(data):
    """UTF-8 safe JSON output, bypassing Windows stdout encoding issues."""
    text = json.dumps(data, ensure_ascii=False, indent=2)
    try:
        sys.stdout.buffer.write(text.encode("utf-8"))
        sys.stdout.buffer.write(b"\n")
        sys.stdout.buffer.flush()
    except (AttributeError, OSError):
        print(text)


def get_token():
    """Read GITCODE_TOKEN: process env -> Windows User -> Windows Machine."""
    token = os.environ.get("GITCODE_TOKEN")
    if token:
        return token.strip()
    if sys.platform == "win32":
        for scope in ("User", "Machine"):
            try:
                out = subprocess.check_output(
                    ["powershell", "-NoProfile", "-Command",
                     "[Environment]::GetEnvironmentVariable('GITCODE_TOKEN','%s')" % scope],
                    creationflags=0x08000000,
                    timeout=5,
                    stderr=subprocess.DEVNULL,
                )
                if out:
                    val = out.decode("utf-8", errors="replace").strip()
                    if val:
                        return val
            except Exception:
                pass
    return None


def parse_issue_url(url):
    """Extract (owner, repo, number) from a GitCode issue URL."""
    m = re.search(r"gitcode\.com[/:]([^/]+)/([^/]+)/issues/(\d+)", url)
    if m:
        return m.group(1), m.group(2), int(m.group(3))
    raise ValueError("Cannot parse owner/repo/number from URL: " + str(url))


def api_get(token, path, retry_times=API_RETRY_TIMES, retry_interval=API_RETRY_INTERVAL):
    """GET request to GitCode API with retry and rate-limit handling."""
    url = (GITCODE_API_BASE.rstrip("/") + "/" + path.lstrip("/")).replace(" ", "%20")
    req = Request(url, headers={"PRIVATE-TOKEN": token})
    last_err = None
    for attempt in range(retry_times + 1):
        try:
            with urlopen(req, timeout=30) as f:
                return json.loads(f.read().decode("utf-8"))
        except HTTPError as e:
            last_err = e
            if e.code == 429:
                wait = 60
                try:
                    wait = int(e.headers.get("Retry-After", 60))
                except (TypeError, ValueError):
                    pass
                time.sleep(wait)
            elif attempt < retry_times:
                time.sleep(retry_interval)
            else:
                raise
        except (URLError, OSError) as e:
            last_err = e
            if attempt < retry_times:
                time.sleep(retry_interval)
            else:
                raise
    raise last_err


def api_post(token, path, data, retry_times=API_RETRY_TIMES, retry_interval=API_RETRY_INTERVAL):
    """POST request to GitCode API with retry and rate-limit handling."""
    url = (GITCODE_API_BASE.rstrip("/") + "/" + path.lstrip("/")).replace(" ", "%20")
    body = json.dumps(data).encode("utf-8")
    last_err = None
    for attempt in range(retry_times + 1):
        req = Request(url, data=body, method="POST", headers={
            "PRIVATE-TOKEN": token,
            "Content-Type": "application/json",
        })
        try:
            with urlopen(req, timeout=30) as f:
                return json.loads(f.read().decode("utf-8"))
        except HTTPError as e:
            last_err = e
            if e.code == 429:
                wait = 60
                try:
                    wait = int(e.headers.get("Retry-After", 60))
                except (TypeError, ValueError):
                    pass
                time.sleep(wait)
            elif attempt < retry_times:
                time.sleep(retry_interval)
            else:
                raise
        except (URLError, OSError) as e:
            last_err = e
            if attempt < retry_times:
                time.sleep(retry_interval)
            else:
                raise
    raise last_err
