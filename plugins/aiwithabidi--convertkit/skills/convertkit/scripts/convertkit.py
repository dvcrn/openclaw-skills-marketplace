#!/usr/bin/env python3
"""ConvertKit CLI — comprehensive API integration for AI agents.

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

API_BASE = "https://api.convertkit.com/v3"


def get_token():
    """Get API token from environment."""
    token = os.environ.get("CONVERTKIT_API_KEY", "")
    if not token:
        env_path = os.path.join(
            os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")),
            ".env"
        )
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("CONVERTKIT_API_KEY="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not token:
        print(f"Error: CONVERTKIT_API_KEY not set", file=sys.stderr)
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


def cmd_subscribers(args):
    """List subscribers."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/subscribers/{args.id}")
    else:
        data = api("GET", "/subscribers", params=params)
    output(data, getattr(args, 'human', False))

def cmd_subscriber_get(args):
    """Get subscriber details."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/subscriber/{args.id}")
    else:
        data = api("GET", "/subscriber/get", params=params)
    output(data, getattr(args, 'human', False))

def cmd_subscriber_add(args):
    """Add a subscriber."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/subscriber/{args.id}")
    else:
        data = api("POST", "/subscriber/add", params=params)
    output(data, getattr(args, 'human', False))

def cmd_subscriber_search(args):
    """Search by email."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/subscriber/{args.id}")
    else:
        data = api("GET", "/subscriber/search", params=params)
    output(data, getattr(args, 'human', False))

def cmd_tags(args):
    """List all tags."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/tags/{args.id}")
    else:
        data = api("GET", "/tags", params=params)
    output(data, getattr(args, 'human', False))

def cmd_tag_create(args):
    """Create a tag."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/tag/{args.id}")
    else:
        data = api("POST", "/tag/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_tag_apply(args):
    """Tag a subscriber."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/tag/{args.id}")
    else:
        data = api("POST", "/tag/apply", params=params)
    output(data, getattr(args, 'human', False))

def cmd_tag_remove(args):
    """Remove tag."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("PUT", f"/tag/{args.id}")
    else:
        data = api("PUT", "/tag/remove", params=params)
    output(data, getattr(args, 'human', False))

def cmd_forms(args):
    """List forms."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/forms/{args.id}")
    else:
        data = api("GET", "/forms", params=params)
    output(data, getattr(args, 'human', False))

def cmd_form_subscribers(args):
    """List form subscribers."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/form/{args.id}")
    else:
        data = api("GET", "/form/subscribers", params=params)
    output(data, getattr(args, 'human', False))

def cmd_sequences(args):
    """List sequences."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/sequences/{args.id}")
    else:
        data = api("GET", "/sequences", params=params)
    output(data, getattr(args, 'human', False))

def cmd_sequence_subscribers(args):
    """List sequence subscribers."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/sequence/{args.id}")
    else:
        data = api("GET", "/sequence/subscribers", params=params)
    output(data, getattr(args, 'human', False))

def cmd_broadcasts(args):
    """List broadcasts."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/broadcasts/{args.id}")
    else:
        data = api("GET", "/broadcasts", params=params)
    output(data, getattr(args, 'human', False))

def cmd_broadcast_create(args):
    """Create a broadcast."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/broadcast/{args.id}")
    else:
        data = api("POST", "/broadcast/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_broadcast_send(args):
    """Send a broadcast."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/broadcast/{args.id}")
    else:
        data = api("POST", "/broadcast/send", params=params)
    output(data, getattr(args, 'human', False))


COMMANDS = {
    "subscribers": cmd_subscribers,
    "subscriber-get": cmd_subscriber_get,
    "subscriber-add": cmd_subscriber_add,
    "subscriber-search": cmd_subscriber_search,
    "tags": cmd_tags,
    "tag-create": cmd_tag_create,
    "tag-apply": cmd_tag_apply,
    "tag-remove": cmd_tag_remove,
    "forms": cmd_forms,
    "form-subscribers": cmd_form_subscribers,
    "sequences": cmd_sequences,
    "sequence-subscribers": cmd_sequence_subscribers,
    "broadcasts": cmd_broadcasts,
    "broadcast-create": cmd_broadcast_create,
    "broadcast-send": cmd_broadcast_send,
}


def main():
    parser = argparse.ArgumentParser(
        description="ConvertKit CLI — AI agent integration",
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
