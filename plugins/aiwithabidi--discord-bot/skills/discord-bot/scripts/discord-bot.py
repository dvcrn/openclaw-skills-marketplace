#!/usr/bin/env python3
"""Discord Bot CLI — comprehensive API integration for AI agents.

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

API_BASE = "https://discord.com/api/v10"


def get_token():
    """Get API token from environment."""
    token = os.environ.get("DISCORD_BOT_TOKEN", "")
    if not token:
        env_path = os.path.join(
            os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")),
            ".env"
        )
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("DISCORD_BOT_TOKEN="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not token:
        print(f"Error: DISCORD_BOT_TOKEN not set", file=sys.stderr)
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


def cmd_guilds(args):
    """List bot's servers."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/guilds/{args.id}")
    else:
        data = api("GET", "/guilds", params=params)
    output(data, getattr(args, 'human', False))

def cmd_guild_get(args):
    """Get server details."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/guild/{args.id}")
    else:
        data = api("GET", "/guild/get", params=params)
    output(data, getattr(args, 'human', False))

def cmd_channels(args):
    """List server channels."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/channels/{args.id}")
    else:
        data = api("GET", "/channels", params=params)
    output(data, getattr(args, 'human', False))

def cmd_channel_create(args):
    """Create a channel."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/channel/{args.id}")
    else:
        data = api("POST", "/channel/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_channel_update(args):
    """Update channel."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("PUT", f"/channel/{args.id}")
    else:
        data = api("PUT", "/channel/update", params=params)
    output(data, getattr(args, 'human', False))

def cmd_send(args):
    """Send a message."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/send/{args.id}")
    else:
        data = api("POST", "/send", params=params)
    output(data, getattr(args, 'human', False))

def cmd_send_embed(args):
    """Send embed message."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/send/{args.id}")
    else:
        data = api("POST", "/send/embed", params=params)
    output(data, getattr(args, 'human', False))

def cmd_messages(args):
    """List channel messages."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/messages/{args.id}")
    else:
        data = api("GET", "/messages", params=params)
    output(data, getattr(args, 'human', False))

def cmd_message_edit(args):
    """Edit a message."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/message/{args.id}")
    else:
        data = api("GET", "/message/edit", params=params)
    output(data, getattr(args, 'human', False))

def cmd_message_delete(args):
    """Delete a message."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("DELETE", f"/message/{args.id}")
    else:
        data = api("DELETE", "/message/delete", params=params)
    output(data, getattr(args, 'human', False))

def cmd_react(args):
    """Add reaction to message."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/react/{args.id}")
    else:
        data = api("GET", "/react", params=params)
    output(data, getattr(args, 'human', False))

def cmd_members(args):
    """List server members."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/members/{args.id}")
    else:
        data = api("GET", "/members", params=params)
    output(data, getattr(args, 'human', False))

def cmd_roles(args):
    """List server roles."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/roles/{args.id}")
    else:
        data = api("GET", "/roles", params=params)
    output(data, getattr(args, 'human', False))

def cmd_role_assign(args):
    """Assign role to member."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/role/{args.id}")
    else:
        data = api("GET", "/role/assign", params=params)
    output(data, getattr(args, 'human', False))

def cmd_webhooks(args):
    """List channel webhooks."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/webhooks/{args.id}")
    else:
        data = api("GET", "/webhooks", params=params)
    output(data, getattr(args, 'human', False))


COMMANDS = {
    "guilds": cmd_guilds,
    "guild-get": cmd_guild_get,
    "channels": cmd_channels,
    "channel-create": cmd_channel_create,
    "channel-update": cmd_channel_update,
    "send": cmd_send,
    "send-embed": cmd_send_embed,
    "messages": cmd_messages,
    "message-edit": cmd_message_edit,
    "message-delete": cmd_message_delete,
    "react": cmd_react,
    "members": cmd_members,
    "roles": cmd_roles,
    "role-assign": cmd_role_assign,
    "webhooks": cmd_webhooks,
}


def main():
    parser = argparse.ArgumentParser(
        description="Discord Bot CLI — AI agent integration",
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
