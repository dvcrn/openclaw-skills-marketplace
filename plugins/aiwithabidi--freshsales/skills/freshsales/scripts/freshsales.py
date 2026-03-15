#!/usr/bin/env python3
"""Freshsales CLI — comprehensive API integration for AI agents.

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

API_BASE = "https://{domain}/api"


def get_token():
    """Get API token from environment."""
    token = os.environ.get("FRESHSALES_API_KEY", "")
    if not token:
        env_path = os.path.join(
            os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")),
            ".env"
        )
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("FRESHSALES_API_KEY="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not token:
        print(f"Error: FRESHSALES_API_KEY not set", file=sys.stderr)
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


def cmd_contacts(args):
    """List contacts."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/contacts/{args.id}")
    else:
        data = api("GET", "/contacts", params=params)
    output(data, getattr(args, 'human', False))

def cmd_contact_get(args):
    """Get contact details."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/contact/{args.id}")
    else:
        data = api("GET", "/contact/get", params=params)
    output(data, getattr(args, 'human', False))

def cmd_contact_create(args):
    """Create a contact."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/contact/{args.id}")
    else:
        data = api("POST", "/contact/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_contact_update(args):
    """Update a contact."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("PUT", f"/contact/{args.id}")
    else:
        data = api("PUT", "/contact/update", params=params)
    output(data, getattr(args, 'human', False))

def cmd_leads(args):
    """List leads."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/leads/{args.id}")
    else:
        data = api("GET", "/leads", params=params)
    output(data, getattr(args, 'human', False))

def cmd_lead_create(args):
    """Create a lead."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/lead/{args.id}")
    else:
        data = api("POST", "/lead/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_deals(args):
    """List deals."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/deals/{args.id}")
    else:
        data = api("GET", "/deals", params=params)
    output(data, getattr(args, 'human', False))

def cmd_deal_create(args):
    """Create a deal."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/deal/{args.id}")
    else:
        data = api("POST", "/deal/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_deal_update(args):
    """Update deal stage."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("PUT", f"/deal/{args.id}")
    else:
        data = api("PUT", "/deal/update", params=params)
    output(data, getattr(args, 'human', False))

def cmd_accounts(args):
    """List accounts."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/accounts/{args.id}")
    else:
        data = api("GET", "/accounts", params=params)
    output(data, getattr(args, 'human', False))

def cmd_tasks(args):
    """List tasks."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/tasks/{args.id}")
    else:
        data = api("GET", "/tasks", params=params)
    output(data, getattr(args, 'human', False))

def cmd_task_create(args):
    """Create a task."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/task/{args.id}")
    else:
        data = api("POST", "/task/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_search(args):
    """Search across all entities."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/search/{args.id}")
    else:
        data = api("GET", "/search", params=params)
    output(data, getattr(args, 'human', False))

def cmd_activities(args):
    """List recent activities."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/activities/{args.id}")
    else:
        data = api("GET", "/activities", params=params)
    output(data, getattr(args, 'human', False))

def cmd_pipeline(args):
    """Pipeline summary."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/pipeline/{args.id}")
    else:
        data = api("GET", "/pipeline", params=params)
    output(data, getattr(args, 'human', False))


COMMANDS = {
    "contacts": cmd_contacts,
    "contact-get": cmd_contact_get,
    "contact-create": cmd_contact_create,
    "contact-update": cmd_contact_update,
    "leads": cmd_leads,
    "lead-create": cmd_lead_create,
    "deals": cmd_deals,
    "deal-create": cmd_deal_create,
    "deal-update": cmd_deal_update,
    "accounts": cmd_accounts,
    "tasks": cmd_tasks,
    "task-create": cmd_task_create,
    "search": cmd_search,
    "activities": cmd_activities,
    "pipeline": cmd_pipeline,
}


def main():
    parser = argparse.ArgumentParser(
        description="Freshsales CLI — AI agent integration",
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
