#!/usr/bin/env python3
"""Neon CLI — comprehensive API integration for AI agents.

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

API_BASE = "https://console.neon.tech/api/v2"


def get_token():
    """Get API token from environment."""
    token = os.environ.get("NEON_API_KEY", "")
    if not token:
        env_path = os.path.join(
            os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")),
            ".env"
        )
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("NEON_API_KEY="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not token:
        print(f"Error: NEON_API_KEY not set", file=sys.stderr)
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


def cmd_projects(args):
    """List projects."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/projects/{args.id}")
    else:
        data = api("GET", "/projects", params=params)
    output(data, getattr(args, 'human', False))

def cmd_project_get(args):
    """Get project details."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/project/{args.id}")
    else:
        data = api("GET", "/project/get", params=params)
    output(data, getattr(args, 'human', False))

def cmd_project_create(args):
    """Create a project."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/project/{args.id}")
    else:
        data = api("POST", "/project/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_project_delete(args):
    """Delete a project."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("DELETE", f"/project/{args.id}")
    else:
        data = api("DELETE", "/project/delete", params=params)
    output(data, getattr(args, 'human', False))

def cmd_branches(args):
    """List branches."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/branches/{args.id}")
    else:
        data = api("GET", "/branches", params=params)
    output(data, getattr(args, 'human', False))

def cmd_branch_create(args):
    """Create a branch."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/branch/{args.id}")
    else:
        data = api("POST", "/branch/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_branch_delete(args):
    """Delete a branch."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("DELETE", f"/branch/{args.id}")
    else:
        data = api("DELETE", "/branch/delete", params=params)
    output(data, getattr(args, 'human', False))

def cmd_branch_restore(args):
    """Restore branch to point in time."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/branch/{args.id}")
    else:
        data = api("GET", "/branch/restore", params=params)
    output(data, getattr(args, 'human', False))

def cmd_databases(args):
    """List databases."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/databases/{args.id}")
    else:
        data = api("GET", "/databases", params=params)
    output(data, getattr(args, 'human', False))

def cmd_database_create(args):
    """Create database."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/database/{args.id}")
    else:
        data = api("POST", "/database/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_roles(args):
    """List roles."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/roles/{args.id}")
    else:
        data = api("GET", "/roles", params=params)
    output(data, getattr(args, 'human', False))

def cmd_endpoints(args):
    """List endpoints."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/endpoints/{args.id}")
    else:
        data = api("GET", "/endpoints", params=params)
    output(data, getattr(args, 'human', False))

def cmd_connection_string(args):
    """Get connection string."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/connection/{args.id}")
    else:
        data = api("GET", "/connection/string", params=params)
    output(data, getattr(args, 'human', False))

def cmd_consumption(args):
    """Get consumption metrics."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/consumption/{args.id}")
    else:
        data = api("GET", "/consumption", params=params)
    output(data, getattr(args, 'human', False))

def cmd_operations(args):
    """List operations."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/operations/{args.id}")
    else:
        data = api("GET", "/operations", params=params)
    output(data, getattr(args, 'human', False))


COMMANDS = {
    "projects": cmd_projects,
    "project-get": cmd_project_get,
    "project-create": cmd_project_create,
    "project-delete": cmd_project_delete,
    "branches": cmd_branches,
    "branch-create": cmd_branch_create,
    "branch-delete": cmd_branch_delete,
    "branch-restore": cmd_branch_restore,
    "databases": cmd_databases,
    "database-create": cmd_database_create,
    "roles": cmd_roles,
    "endpoints": cmd_endpoints,
    "connection-string": cmd_connection_string,
    "consumption": cmd_consumption,
    "operations": cmd_operations,
}


def main():
    parser = argparse.ArgumentParser(
        description="Neon CLI — AI agent integration",
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
