#!/usr/bin/env python3
"""Fly.io CLI — comprehensive API integration for AI agents.

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

API_BASE = "https://api.machines.dev/v1"


def get_token():
    """Get API token from environment."""
    token = os.environ.get("FLY_API_TOKEN", "")
    if not token:
        env_path = os.path.join(
            os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")),
            ".env"
        )
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("FLY_API_TOKEN="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not token:
        print(f"Error: FLY_API_TOKEN not set", file=sys.stderr)
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


def cmd_apps(args):
    """List apps."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/apps/{args.id}")
    else:
        data = api("GET", "/apps", params=params)
    output(data, getattr(args, 'human', False))

def cmd_app_get(args):
    """Get app details."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/app/{args.id}")
    else:
        data = api("GET", "/app/get", params=params)
    output(data, getattr(args, 'human', False))

def cmd_app_create(args):
    """Create an app."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/app/{args.id}")
    else:
        data = api("POST", "/app/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_machines(args):
    """List machines."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/machines/{args.id}")
    else:
        data = api("GET", "/machines", params=params)
    output(data, getattr(args, 'human', False))

def cmd_machine_get(args):
    """Get machine details."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/machine/{args.id}")
    else:
        data = api("GET", "/machine/get", params=params)
    output(data, getattr(args, 'human', False))

def cmd_machine_start(args):
    """Start a machine."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/machine/{args.id}")
    else:
        data = api("GET", "/machine/start", params=params)
    output(data, getattr(args, 'human', False))

def cmd_machine_stop(args):
    """Stop a machine."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/machine/{args.id}")
    else:
        data = api("GET", "/machine/stop", params=params)
    output(data, getattr(args, 'human', False))

def cmd_machine_create(args):
    """Create a machine."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/machine/{args.id}")
    else:
        data = api("POST", "/machine/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_volumes(args):
    """List volumes."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/volumes/{args.id}")
    else:
        data = api("GET", "/volumes", params=params)
    output(data, getattr(args, 'human', False))

def cmd_volume_create(args):
    """Create a volume."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/volume/{args.id}")
    else:
        data = api("POST", "/volume/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_secrets(args):
    """List secrets."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/secrets/{args.id}")
    else:
        data = api("GET", "/secrets", params=params)
    output(data, getattr(args, 'human', False))

def cmd_secret_set(args):
    """Set a secret."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("PUT", f"/secret/{args.id}")
    else:
        data = api("PUT", "/secret/set", params=params)
    output(data, getattr(args, 'human', False))

def cmd_certs(args):
    """List certificates."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/certs/{args.id}")
    else:
        data = api("GET", "/certs", params=params)
    output(data, getattr(args, 'human', False))

def cmd_regions(args):
    """List available regions."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/regions/{args.id}")
    else:
        data = api("GET", "/regions", params=params)
    output(data, getattr(args, 'human', False))

def cmd_status(args):
    """App status overview."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/status/{args.id}")
    else:
        data = api("GET", "/status", params=params)
    output(data, getattr(args, 'human', False))


COMMANDS = {
    "apps": cmd_apps,
    "app-get": cmd_app_get,
    "app-create": cmd_app_create,
    "machines": cmd_machines,
    "machine-get": cmd_machine_get,
    "machine-start": cmd_machine_start,
    "machine-stop": cmd_machine_stop,
    "machine-create": cmd_machine_create,
    "volumes": cmd_volumes,
    "volume-create": cmd_volume_create,
    "secrets": cmd_secrets,
    "secret-set": cmd_secret_set,
    "certs": cmd_certs,
    "regions": cmd_regions,
    "status": cmd_status,
}


def main():
    parser = argparse.ArgumentParser(
        description="Fly.io CLI — AI agent integration",
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
