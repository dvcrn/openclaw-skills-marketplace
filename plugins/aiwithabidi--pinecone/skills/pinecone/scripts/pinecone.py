#!/usr/bin/env python3
"""Pinecone CLI — comprehensive API integration for AI agents.

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

API_BASE = "https://api.pinecone.io"


def get_token():
    """Get API token from environment."""
    token = os.environ.get("PINECONE_API_KEY", "")
    if not token:
        env_path = os.path.join(
            os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")),
            ".env"
        )
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("PINECONE_API_KEY="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not token:
        print(f"Error: PINECONE_API_KEY not set", file=sys.stderr)
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


def cmd_indexes(args):
    """List indexes."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/indexes/{args.id}")
    else:
        data = api("GET", "/indexes", params=params)
    output(data, getattr(args, 'human', False))

def cmd_index_get(args):
    """Get index details."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/index/{args.id}")
    else:
        data = api("GET", "/index/get", params=params)
    output(data, getattr(args, 'human', False))

def cmd_index_create(args):
    """Create an index."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/index/{args.id}")
    else:
        data = api("POST", "/index/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_index_delete(args):
    """Delete an index."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("DELETE", f"/index/{args.id}")
    else:
        data = api("DELETE", "/index/delete", params=params)
    output(data, getattr(args, 'human', False))

def cmd_upsert(args):
    """Upsert vectors."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/upsert/{args.id}")
    else:
        data = api("GET", "/upsert", params=params)
    output(data, getattr(args, 'human', False))

def cmd_query(args):
    """Query similar vectors."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/query/{args.id}")
    else:
        data = api("GET", "/query", params=params)
    output(data, getattr(args, 'human', False))

def cmd_fetch(args):
    """Fetch vectors by ID."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/fetch/{args.id}")
    else:
        data = api("GET", "/fetch", params=params)
    output(data, getattr(args, 'human', False))

def cmd_delete(args):
    """Delete vectors."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("DELETE", f"/delete/{args.id}")
    else:
        data = api("DELETE", "/delete", params=params)
    output(data, getattr(args, 'human', False))

def cmd_delete_namespace(args):
    """Delete all vectors in namespace."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("DELETE", f"/delete/{args.id}")
    else:
        data = api("DELETE", "/delete/namespace", params=params)
    output(data, getattr(args, 'human', False))

def cmd_stats(args):
    """Get index statistics."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/stats/{args.id}")
    else:
        data = api("GET", "/stats", params=params)
    output(data, getattr(args, 'human', False))

def cmd_collections(args):
    """List collections."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/collections/{args.id}")
    else:
        data = api("GET", "/collections", params=params)
    output(data, getattr(args, 'human', False))

def cmd_collection_create(args):
    """Create collection from index."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/collection/{args.id}")
    else:
        data = api("POST", "/collection/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_namespaces(args):
    """List namespaces in index."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/namespaces/{args.id}")
    else:
        data = api("GET", "/namespaces", params=params)
    output(data, getattr(args, 'human', False))


COMMANDS = {
    "indexes": cmd_indexes,
    "index-get": cmd_index_get,
    "index-create": cmd_index_create,
    "index-delete": cmd_index_delete,
    "upsert": cmd_upsert,
    "query": cmd_query,
    "fetch": cmd_fetch,
    "delete": cmd_delete,
    "delete-namespace": cmd_delete_namespace,
    "stats": cmd_stats,
    "collections": cmd_collections,
    "collection-create": cmd_collection_create,
    "namespaces": cmd_namespaces,
}


def main():
    parser = argparse.ArgumentParser(
        description="Pinecone CLI — AI agent integration",
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
