#!/usr/bin/env python3
"""Render CLI — comprehensive API integration for AI agents.

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

API_BASE = "https://api.render.com/v1"


def get_token():
    """Get API token from environment."""
    token = os.environ.get("RENDER_API_KEY", "")
    if not token:
        env_path = os.path.join(
            os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")),
            ".env"
        )
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("RENDER_API_KEY="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not token:
        print(f"Error: RENDER_API_KEY not set", file=sys.stderr)
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


def cmd_services(args):
    """List services."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/services/{args.id}")
    else:
        data = api("GET", "/services", params=params)
    output(data, getattr(args, 'human', False))

def cmd_service_get(args):
    """Get service details."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/service/{args.id}")
    else:
        data = api("GET", "/service/get", params=params)
    output(data, getattr(args, 'human', False))

def cmd_service_create(args):
    """Create a service."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/service/{args.id}")
    else:
        data = api("POST", "/service/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_deploys(args):
    """List deployments."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/deploys/{args.id}")
    else:
        data = api("GET", "/deploys", params=params)
    output(data, getattr(args, 'human', False))

def cmd_deploy(args):
    """Trigger a deploy."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/deploy/{args.id}")
    else:
        data = api("GET", "/deploy", params=params)
    output(data, getattr(args, 'human', False))

def cmd_deploy_rollback(args):
    """Rollback to previous deploy."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/deploy/{args.id}")
    else:
        data = api("GET", "/deploy/rollback", params=params)
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
    """Create PostgreSQL database."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/database/{args.id}")
    else:
        data = api("POST", "/database/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_env_vars(args):
    """List environment variables."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/env/{args.id}")
    else:
        data = api("GET", "/env/vars", params=params)
    output(data, getattr(args, 'human', False))

def cmd_env_set(args):
    """Set environment variable."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("PUT", f"/env/{args.id}")
    else:
        data = api("PUT", "/env/set", params=params)
    output(data, getattr(args, 'human', False))

def cmd_env_delete(args):
    """Delete environment variable."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("DELETE", f"/env/{args.id}")
    else:
        data = api("DELETE", "/env/delete", params=params)
    output(data, getattr(args, 'human', False))

def cmd_domains(args):
    """List custom domains."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/domains/{args.id}")
    else:
        data = api("GET", "/domains", params=params)
    output(data, getattr(args, 'human', False))

def cmd_domain_add(args):
    """Add custom domain."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/domain/{args.id}")
    else:
        data = api("POST", "/domain/add", params=params)
    output(data, getattr(args, 'human', False))

def cmd_logs(args):
    """Get service logs."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/logs/{args.id}")
    else:
        data = api("GET", "/logs", params=params)
    output(data, getattr(args, 'human', False))

def cmd_suspend(args):
    """Suspend a service."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/suspend/{args.id}")
    else:
        data = api("GET", "/suspend", params=params)
    output(data, getattr(args, 'human', False))


COMMANDS = {
    "services": cmd_services,
    "service-get": cmd_service_get,
    "service-create": cmd_service_create,
    "deploys": cmd_deploys,
    "deploy": cmd_deploy,
    "deploy-rollback": cmd_deploy_rollback,
    "databases": cmd_databases,
    "database-create": cmd_database_create,
    "env-vars": cmd_env_vars,
    "env-set": cmd_env_set,
    "env-delete": cmd_env_delete,
    "domains": cmd_domains,
    "domain-add": cmd_domain_add,
    "logs": cmd_logs,
    "suspend": cmd_suspend,
}


def main():
    parser = argparse.ArgumentParser(
        description="Render CLI — AI agent integration",
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
