#!/usr/bin/env python3
"""1Password CLI — 1Password Connect — vaults, items, secrets management for server-side applications.

Zero dependencies beyond Python stdlib.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "{connect_host}/v1"


def get_env(name):
    val = os.environ.get(name, "")
    if not val:
        env_path = os.path.join(os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(name + "="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    return val


def req(method, url, data=None, headers=None, timeout=30):
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, method=method)
    r.add_header("Content-Type", "application/json")
    if headers:
        for k, v in headers.items():
            r.add_header(k, v)
    try:
        resp = urllib.request.urlopen(r, timeout=timeout)
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(json.dumps({"error": True, "code": e.code, "message": err}), file=sys.stderr)
        sys.exit(1)


def api(method, path, data=None, params=None):
    """Make authenticated API request."""
    base = API_BASE
    token = get_env("OP_CONNECT_TOKEN")
    host = get_env("OP_CONNECT_HOST")
    if not token or not host:
        print("Error: OP_CONNECT_TOKEN and OP_CONNECT_HOST required", file=sys.stderr)
        sys.exit(1)
    base = f"{host}/v1"
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{base}{path}"
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v}, doseq=True)
        url = f"{url}{'&' if '?' in url else '?'}{qs}"
    return req(method, url, data=data, headers=headers)


def out(data):
    print(json.dumps(data, indent=2, default=str))


def cmd_list_vaults(args):
    """List all vaults"""
    path = "/vaults"
    result = api("GET", path)
    out(result)

def cmd_get_vault(args):
    """Get vault details"""
    path = "/vaults/{id}"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_list_items(args):
    """List items in vault"""
    path = "/vaults/{vault_id}/items"
    path = path.replace("{vault-id}", str(args.vault_id or ""))
    params = {}
    if args.vault_id:
        params["vault-id"] = args.vault_id
    result = api("GET", path, params=params)
    out(result)

def cmd_get_item(args):
    """Get item with fields"""
    path = "/vaults/{vault_id}/items/{id}"
    path = path.replace("{id}", str(args.id))
    path = path.replace("{vault-id}", str(args.vault_id or ""))
    params = {}
    if args.vault_id:
        params["vault-id"] = args.vault_id
    result = api("GET", path, params=params)
    out(result)

def cmd_create_item(args):
    """Create item"""
    path = "/vaults/{vault_id}/items"
    path = path.replace("{vault-id}", str(args.vault_id or ""))
    data = {}
    if args.vault_id:
        data["vault-id"] = args.vault_id
    if args.category:
        data["category"] = args.category
    if args.title:
        data["title"] = args.title
    if args.fields:
        data["fields"] = args.fields
    result = api("POST", path, data=data)
    out(result)

def cmd_update_item(args):
    """Update item"""
    path = "/vaults/{vault_id}/items/{id}"
    path = path.replace("{id}", str(args.id))
    path = path.replace("{vault-id}", str(args.vault_id or ""))
    data = {}
    if args.vault_id:
        data["vault-id"] = args.vault_id
    if args.fields:
        data["fields"] = args.fields
    result = api("PUT", path, data=data)
    out(result)

def cmd_delete_item(args):
    """Delete item"""
    path = "/vaults/{vault_id}/items/{id}"
    path = path.replace("{id}", str(args.id))
    path = path.replace("{vault-id}", str(args.vault_id or ""))
    params = {}
    if args.vault_id:
        params["vault-id"] = args.vault_id
    result = api("DELETE", path, params=params)
    out(result)

def cmd_get_health(args):
    """Check Connect server health"""
    path = "/health"
    result = api("GET", path)
    out(result)

def cmd_get_heartbeat(args):
    """Simple heartbeat check"""
    path = "/heartbeat"
    result = api("GET", path)
    out(result)


def main():
    parser = argparse.ArgumentParser(description="1Password CLI")
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    p_list_vaults = sub.add_parser("list-vaults", help="List all vaults")
    p_list_vaults.set_defaults(func=cmd_list_vaults)

    p_get_vault = sub.add_parser("get-vault", help="Get vault details")
    p_get_vault.add_argument("id")
    p_get_vault.set_defaults(func=cmd_get_vault)

    p_list_items = sub.add_parser("list-items", help="List items in vault")
    p_list_items.add_argument("--vault-id", required=True)
    p_list_items.set_defaults(func=cmd_list_items)

    p_get_item = sub.add_parser("get-item", help="Get item with fields")
    p_get_item.add_argument("--vault-id", required=True)
    p_get_item.add_argument("id")
    p_get_item.set_defaults(func=cmd_get_item)

    p_create_item = sub.add_parser("create-item", help="Create item")
    p_create_item.add_argument("--vault-id", required=True)
    p_create_item.add_argument("--category", default="LOGIN")
    p_create_item.add_argument("--title", required=True)
    p_create_item.add_argument("--fields", default="JSON")
    p_create_item.set_defaults(func=cmd_create_item)

    p_update_item = sub.add_parser("update-item", help="Update item")
    p_update_item.add_argument("--vault-id", required=True)
    p_update_item.add_argument("id")
    p_update_item.add_argument("--fields", default="JSON")
    p_update_item.set_defaults(func=cmd_update_item)

    p_delete_item = sub.add_parser("delete-item", help="Delete item")
    p_delete_item.add_argument("--vault-id", required=True)
    p_delete_item.add_argument("id")
    p_delete_item.set_defaults(func=cmd_delete_item)

    p_get_health = sub.add_parser("get-health", help="Check Connect server health")
    p_get_health.set_defaults(func=cmd_get_health)

    p_get_heartbeat = sub.add_parser("get-heartbeat", help="Simple heartbeat check")
    p_get_heartbeat.set_defaults(func=cmd_get_heartbeat)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
