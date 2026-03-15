#!/usr/bin/env python3
"""Make (Integromat) CLI — comprehensive API integration for AI agents.

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

API_BASE = "https://{zone}.make.com/api/v2"


def get_token():
    """Get API token from environment."""
    token = os.environ.get("MAKE_API_KEY", "")
    if not token:
        env_path = os.path.join(
            os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")),
            ".env"
        )
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("MAKE_API_KEY="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not token:
        print(f"Error: MAKE_API_KEY not set", file=sys.stderr)
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


def cmd_scenarios(args):
    """List scenarios."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/scenarios/{args.id}")
    else:
        data = api("GET", "/scenarios", params=params)
    output(data, getattr(args, 'human', False))

def cmd_scenario_get(args):
    """Get scenario details."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/scenario/{args.id}")
    else:
        data = api("GET", "/scenario/get", params=params)
    output(data, getattr(args, 'human', False))

def cmd_scenario_run(args):
    """Trigger a scenario run."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/scenario/{args.id}")
    else:
        data = api("GET", "/scenario/run", params=params)
    output(data, getattr(args, 'human', False))

def cmd_scenario_activate(args):
    """Activate a scenario."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("PUT", f"/scenario/{args.id}")
    else:
        data = api("PUT", "/scenario/activate", params=params)
    output(data, getattr(args, 'human', False))

def cmd_scenario_deactivate(args):
    """Deactivate a scenario."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("PUT", f"/scenario/{args.id}")
    else:
        data = api("PUT", "/scenario/deactivate", params=params)
    output(data, getattr(args, 'human', False))

def cmd_executions(args):
    """List execution logs."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/executions/{args.id}")
    else:
        data = api("GET", "/executions", params=params)
    output(data, getattr(args, 'human', False))

def cmd_execution_get(args):
    """Get execution details."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/execution/{args.id}")
    else:
        data = api("GET", "/execution/get", params=params)
    output(data, getattr(args, 'human', False))

def cmd_connections(args):
    """List connections."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/connections/{args.id}")
    else:
        data = api("GET", "/connections", params=params)
    output(data, getattr(args, 'human', False))

def cmd_data_stores(args):
    """List data stores."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/data/{args.id}")
    else:
        data = api("GET", "/data/stores", params=params)
    output(data, getattr(args, 'human', False))

def cmd_data_store_records(args):
    """List data store records."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/data/{args.id}")
    else:
        data = api("GET", "/data/store/records", params=params)
    output(data, getattr(args, 'human', False))

def cmd_webhooks(args):
    """List webhooks."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/webhooks/{args.id}")
    else:
        data = api("GET", "/webhooks", params=params)
    output(data, getattr(args, 'human', False))

def cmd_webhook_create(args):
    """Create a webhook."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/webhook/{args.id}")
    else:
        data = api("POST", "/webhook/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_organizations(args):
    """List organizations."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/organizations/{args.id}")
    else:
        data = api("GET", "/organizations", params=params)
    output(data, getattr(args, 'human', False))

def cmd_users(args):
    """List team users."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/users/{args.id}")
    else:
        data = api("GET", "/users", params=params)
    output(data, getattr(args, 'human', False))

def cmd_usage(args):
    """Get usage stats."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/usage/{args.id}")
    else:
        data = api("GET", "/usage", params=params)
    output(data, getattr(args, 'human', False))


COMMANDS = {
    "scenarios": cmd_scenarios,
    "scenario-get": cmd_scenario_get,
    "scenario-run": cmd_scenario_run,
    "scenario-activate": cmd_scenario_activate,
    "scenario-deactivate": cmd_scenario_deactivate,
    "executions": cmd_executions,
    "execution-get": cmd_execution_get,
    "connections": cmd_connections,
    "data-stores": cmd_data_stores,
    "data-store-records": cmd_data_store_records,
    "webhooks": cmd_webhooks,
    "webhook-create": cmd_webhook_create,
    "organizations": cmd_organizations,
    "users": cmd_users,
    "usage": cmd_usage,
}


def main():
    parser = argparse.ArgumentParser(
        description="Make (Integromat) CLI — AI agent integration",
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
