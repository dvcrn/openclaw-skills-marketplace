#!/usr/bin/env python3
"""Segment CLI — Segment — manage sources, destinations, events, and tracking plans via Config & Tracking APIs

Zero dependencies beyond Python stdlib.
Built by M. Abidi | agxntsix.ai
"""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

API_BASE = "https://api.segmentapis.com"

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
    if not val:
        print(f"Error: {name} not set", file=sys.stderr)
        sys.exit(1)
    return val


def get_headers():
    token = get_env("SEGMENT_ACCESS_TOKEN")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}



def get_api_base():
    base = API_BASE
    pass
    return base

def req(method, path, data=None, params=None):
    headers = get_headers()
    if path.startswith("http"):
        url = path
    else:
        url = get_api_base() + path
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        if qs:
            url = f"{url}?{qs}" if "?" not in url else f"{url}&{qs}"
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, method=method)
    for k, v in headers.items():
        r.add_header(k, v)
    try:
        resp = urllib.request.urlopen(r, timeout=30)
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {"ok": True}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(json.dumps({"error": True, "code": e.code, "message": err_body}), file=sys.stderr)
        sys.exit(1)


def try_json(val):
    if val is None:
        return None
    try:
        return json.loads(val)
    except (json.JSONDecodeError, ValueError):
        return val


def out(data, human=False):
    if human and isinstance(data, dict):
        for k, v in data.items():
            print(f"  {k}: {v}")
    elif human and isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for k, v in item.items():
                    print(f"  {k}: {v}")
                print()
            else:
                print(item)
    else:
        print(json.dumps(data, indent=2, default=str))


def cmd_sources(args):
    """List sources."""
    path = "/sources"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_source_get(args):
    """Get source."""
    path = f"/sources/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_source_create(args):
    """Create source."""
    path = "/sources"
    body = {}
    if getattr(args, "name", None): body["name"] = try_json(args.name)
    if getattr(args, "catalog_name", None): body["catalog_name"] = try_json(args.catalog_name)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_source_delete(args):
    """Delete source."""
    path = f"/sources/{args.id}"
    data = req("DELETE", path)
    out(data, getattr(args, "human", False))

def cmd_destinations(args):
    """List destinations."""
    path = "/destinations"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_destination_get(args):
    """Get destination."""
    path = f"/destinations/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_warehouses(args):
    """List warehouses."""
    path = "/warehouses"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_catalog_sources(args):
    """List source catalog."""
    path = "/catalog/sources"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_catalog_destinations(args):
    """List destination catalog."""
    path = "/catalog/destinations"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_tracking_plans(args):
    """List tracking plans."""
    path = "/tracking-plans"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_tracking_plan_get(args):
    """Get tracking plan."""
    path = f"/tracking-plans/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_spaces(args):
    """List spaces."""
    path = "/spaces"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_functions(args):
    """List functions."""
    path = "/functions"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_track(args):
    """Send track event."""
    path = "/track"
    body = {}
    if getattr(args, "event", None): body["event"] = try_json(args.event)
    if getattr(args, "userId", None): body["userId"] = try_json(args.userId)
    if getattr(args, "properties", None): body["properties"] = try_json(args.properties)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_identify(args):
    """Send identify."""
    path = "/identify"
    body = {}
    if getattr(args, "userId", None): body["userId"] = try_json(args.userId)
    if getattr(args, "traits", None): body["traits"] = try_json(args.traits)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))



def main():
    parser = argparse.ArgumentParser(description="Segment CLI")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    sub = parser.add_subparsers(dest="command")

    sources_p = sub.add_parser("sources", help="List sources")
    sources_p.set_defaults(func=cmd_sources)

    source_get_p = sub.add_parser("source-get", help="Get source")
    source_get_p.add_argument("id", help="Source ID")
    source_get_p.set_defaults(func=cmd_source_get)

    source_create_p = sub.add_parser("source-create", help="Create source")
    source_create_p.add_argument("--name", help="Name", default=None)
    source_create_p.add_argument("--catalog_name", help="Catalog name", default=None)
    source_create_p.set_defaults(func=cmd_source_create)

    source_delete_p = sub.add_parser("source-delete", help="Delete source")
    source_delete_p.add_argument("id", help="Source ID")
    source_delete_p.set_defaults(func=cmd_source_delete)

    destinations_p = sub.add_parser("destinations", help="List destinations")
    destinations_p.set_defaults(func=cmd_destinations)

    destination_get_p = sub.add_parser("destination-get", help="Get destination")
    destination_get_p.add_argument("id", help="Destination ID")
    destination_get_p.set_defaults(func=cmd_destination_get)

    warehouses_p = sub.add_parser("warehouses", help="List warehouses")
    warehouses_p.set_defaults(func=cmd_warehouses)

    catalog_sources_p = sub.add_parser("catalog-sources", help="List source catalog")
    catalog_sources_p.set_defaults(func=cmd_catalog_sources)

    catalog_destinations_p = sub.add_parser("catalog-destinations", help="List destination catalog")
    catalog_destinations_p.set_defaults(func=cmd_catalog_destinations)

    tracking_plans_p = sub.add_parser("tracking-plans", help="List tracking plans")
    tracking_plans_p.set_defaults(func=cmd_tracking_plans)

    tracking_plan_get_p = sub.add_parser("tracking-plan-get", help="Get tracking plan")
    tracking_plan_get_p.add_argument("id", help="Plan ID")
    tracking_plan_get_p.set_defaults(func=cmd_tracking_plan_get)

    spaces_p = sub.add_parser("spaces", help="List spaces")
    spaces_p.set_defaults(func=cmd_spaces)

    functions_p = sub.add_parser("functions", help="List functions")
    functions_p.set_defaults(func=cmd_functions)

    track_p = sub.add_parser("track", help="Send track event")
    track_p.add_argument("--event", help="Event name", default=None)
    track_p.add_argument("--userId", help="User ID", default=None)
    track_p.add_argument("--properties", help="JSON properties", default=None)
    track_p.set_defaults(func=cmd_track)

    identify_p = sub.add_parser("identify", help="Send identify")
    identify_p.add_argument("--userId", help="User ID", default=None)
    identify_p.add_argument("--traits", help="JSON traits", default=None)
    identify_p.set_defaults(func=cmd_identify)


    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
