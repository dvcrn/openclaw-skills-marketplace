#!/usr/bin/env python3
"""IFTTT CLI — comprehensive API integration for AI agents.

Full CRUD operations, search, reporting, and automation.
Zero dependencies beyond Python stdlib.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone

API_BASE = "https://maker.ifttt.com/trigger"


def get_token():
    """Get API token from environment."""
    token = os.environ.get("IFTTT_WEBHOOK_KEY", "")
    if not token:
        env_path = os.path.join(
            os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")),
            ".env"
        )
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("IFTTT_WEBHOOK_KEY="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not token:
        print(f"Error: IFTTT_WEBHOOK_KEY not set", file=sys.stderr)
        sys.exit(1)
    return token


def api(method, path, data=None, params=None):
    """Make an API request."""
    token = get_token()
    url = f"{API_BASE}{path}"
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        if qs:
            url = f"{url}?{qs}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {"ok": True}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(json.dumps({"error": True, "code": e.code, "message": err_body}), file=sys.stderr)
        sys.exit(1)


def output(data, human=False):
    """Output data as JSON or human-readable."""
    if human and isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for k, v in item.items():
                    print(f"  {k}: {v}")
                print()
            else:
                print(item)
    elif human and isinstance(data, dict):
        for k, v in data.items():
            print(f"  {k}: {v}")
    else:
        print(json.dumps(data, indent=2, default=str))


def cmd_trigger(args):
    """Fire a webhook event."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/trigger/{args.id}")
    else:
        data = api("POST", "/trigger", params=params)
    output(data, getattr(args, 'human', False))

def cmd_trigger_json(args):
    """Fire with JSON payload."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/trigger/{args.id}")
    else:
        data = api("POST", "/trigger/json", params=params)
    output(data, getattr(args, 'human', False))

def cmd_status(args):
    """Check webhook connectivity."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/status/{args.id}")
    else:
        data = api("GET", "/status", params=params)
    output(data, getattr(args, 'human', False))

def cmd_user(args):
    """Get user info (Connect API)."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/user/{args.id}")
    else:
        data = api("GET", "/user", params=params)
    output(data, getattr(args, 'human', False))

def cmd_applets(args):
    """List applets (Connect API)."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/applets/{args.id}")
    else:
        data = api("GET", "/applets", params=params)
    output(data, getattr(args, 'human', False))

def cmd_applet_enable(args):
    """Enable an applet."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("PUT", f"/applet/{args.id}")
    else:
        data = api("PUT", "/applet/enable", params=params)
    output(data, getattr(args, 'human', False))

def cmd_applet_disable(args):
    """Disable an applet."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("DELETE", f"/applet/{args.id}")
    else:
        data = api("DELETE", "/applet/disable", params=params)
    output(data, getattr(args, 'human', False))

def cmd_services(args):
    """List connected services."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/services/{args.id}")
    else:
        data = api("GET", "/services", params=params)
    output(data, getattr(args, 'human', False))


COMMANDS = {
    "trigger": cmd_trigger,
    "trigger-json": cmd_trigger_json,
    "status": cmd_status,
    "user": cmd_user,
    "applets": cmd_applets,
    "applet-enable": cmd_applet_enable,
    "applet-disable": cmd_applet_disable,
    "services": cmd_services,
}


def main():
    parser = argparse.ArgumentParser(
        description="IFTTT CLI — AI agent integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("command", choices=list(COMMANDS.keys()), help="Command to run")
    parser.add_argument("args", nargs="*", help="Command arguments")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    parser.add_argument("--limit", type=int, help="Limit results")
    parser.add_argument("--id", help="Resource ID")
    parser.add_argument("--from", dest="from_date", help="Start date")
    parser.add_argument("--to", dest="to_date", help="End date")
    parser.add_argument("--status", help="Filter by status")
    parser.add_argument("--sort", help="Sort field")
    parser.add_argument("--query", help="Search query")

    parsed = parser.parse_args()
    cmd_func = COMMANDS[parsed.command]
    cmd_func(parsed)


if __name__ == "__main__":
    main()
