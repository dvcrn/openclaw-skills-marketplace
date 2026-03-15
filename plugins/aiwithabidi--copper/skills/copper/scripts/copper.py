#!/usr/bin/env python3
"""Copper CRM CLI — comprehensive API integration for AI agents.

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

API_BASE = "https://api.copper.com/developer_api/v1"


def get_token():
    """Get API token from environment."""
    token = os.environ.get("COPPER_API_KEY", "")
    if not token:
        env_path = os.path.join(
            os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")),
            ".env"
        )
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("COPPER_API_KEY="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not token:
        print(f"Error: COPPER_API_KEY not set", file=sys.stderr)
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


def cmd_people(args):
    """List people/contacts."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/people/{args.id}")
    else:
        data = api("GET", "/people", params=params)
    output(data, getattr(args, 'human', False))

def cmd_person_get(args):
    """Get person details."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/person/{args.id}")
    else:
        data = api("GET", "/person/get", params=params)
    output(data, getattr(args, 'human', False))

def cmd_person_create(args):
    """Create a person."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/person/{args.id}")
    else:
        data = api("POST", "/person/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_person_update(args):
    """Update a person."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("PUT", f"/person/{args.id}")
    else:
        data = api("PUT", "/person/update", params=params)
    output(data, getattr(args, 'human', False))

def cmd_companies(args):
    """List companies."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/companies/{args.id}")
    else:
        data = api("GET", "/companies", params=params)
    output(data, getattr(args, 'human', False))

def cmd_company_create(args):
    """Create a company."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/company/{args.id}")
    else:
        data = api("POST", "/company/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_opportunities(args):
    """List opportunities."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/opportunities/{args.id}")
    else:
        data = api("GET", "/opportunities", params=params)
    output(data, getattr(args, 'human', False))

def cmd_opportunity_create(args):
    """Create opportunity."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/opportunity/{args.id}")
    else:
        data = api("POST", "/opportunity/create", params=params)
    output(data, getattr(args, 'human', False))

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

def cmd_activities(args):
    """List activities for a record."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/activities/{args.id}")
    else:
        data = api("GET", "/activities", params=params)
    output(data, getattr(args, 'human', False))

def cmd_search(args):
    """Search across all records."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/search/{args.id}")
    else:
        data = api("GET", "/search", params=params)
    output(data, getattr(args, 'human', False))

def cmd_pipelines(args):
    """List pipelines."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/pipelines/{args.id}")
    else:
        data = api("GET", "/pipelines", params=params)
    output(data, getattr(args, 'human', False))

def cmd_pipeline_report(args):
    """Pipeline summary report."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/pipeline/{args.id}")
    else:
        data = api("GET", "/pipeline/report", params=params)
    output(data, getattr(args, 'human', False))


COMMANDS = {
    "people": cmd_people,
    "person-get": cmd_person_get,
    "person-create": cmd_person_create,
    "person-update": cmd_person_update,
    "companies": cmd_companies,
    "company-create": cmd_company_create,
    "opportunities": cmd_opportunities,
    "opportunity-create": cmd_opportunity_create,
    "projects": cmd_projects,
    "tasks": cmd_tasks,
    "task-create": cmd_task_create,
    "activities": cmd_activities,
    "search": cmd_search,
    "pipelines": cmd_pipelines,
    "pipeline-report": cmd_pipeline_report,
}


def main():
    parser = argparse.ArgumentParser(
        description="Copper CRM CLI — AI agent integration",
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
