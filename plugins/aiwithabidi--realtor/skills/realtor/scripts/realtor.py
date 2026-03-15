#!/usr/bin/env python3
"""Realtor.com CLI — Realtor.com — search listings, agents, and property details via API

Zero dependencies beyond Python stdlib.
Built by M. Abidi | agxntsix.ai
"""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

API_BASE = "https://realtor16.p.rapidapi.com"

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
    key = get_env("REALTOR_API_KEY")
    return {"X-RapidAPI-Key": key, "Content-Type": "application/json", "Accept": "application/json"}



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


def cmd_search_sale(args):
    """Search for-sale listings."""
    path = "/forsale"
    params = {}
    if getattr(args, "city", None): params["city"] = args.city
    if getattr(args, "state_code", None): params["state_code"] = args.state_code
    if getattr(args, "postal_code", None): params["postal_code"] = args.postal_code
    if getattr(args, "price_min", None): params["price_min"] = args.price_min
    if getattr(args, "price_max", None): params["price_max"] = args.price_max
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_search_rent(args):
    """Search rentals."""
    path = "/forrent"
    params = {}
    if getattr(args, "city", None): params["city"] = args.city
    if getattr(args, "state_code", None): params["state_code"] = args.state_code
    if getattr(args, "postal_code", None): params["postal_code"] = args.postal_code
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_search_sold(args):
    """Search recently sold."""
    path = "/recentlysold"
    params = {}
    if getattr(args, "city", None): params["city"] = args.city
    if getattr(args, "state_code", None): params["state_code"] = args.state_code
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_property(args):
    """Get property details."""
    path = "/property"
    params = {}
    if getattr(args, "property_id", None): params["property_id"] = args.property_id
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_agents(args):
    """Search agents."""
    path = "/agents"
    params = {}
    if getattr(args, "city", None): params["city"] = args.city
    if getattr(args, "state_code", None): params["state_code"] = args.state_code
    if getattr(args, "name", None): params["name"] = args.name
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_agent_get(args):
    """Get agent details."""
    path = "/agent"
    params = {}
    if getattr(args, "nrds_id", None): params["nrds_id"] = args.nrds_id
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_auto_complete(args):
    """Location auto-complete."""
    path = "/autosuggest"
    params = {}
    if getattr(args, "input", None): params["input"] = args.input
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))



def main():
    parser = argparse.ArgumentParser(description="Realtor.com CLI")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    sub = parser.add_subparsers(dest="command")

    search_sale_p = sub.add_parser("search-sale", help="Search for-sale listings")
    search_sale_p.add_argument("--city", help="City", default=None)
    search_sale_p.add_argument("--state_code", help="State code", default=None)
    search_sale_p.add_argument("--postal_code", help="ZIP", default=None)
    search_sale_p.add_argument("--price_min", help="Min price", default=None)
    search_sale_p.add_argument("--price_max", help="Max price", default=None)
    search_sale_p.set_defaults(func=cmd_search_sale)

    search_rent_p = sub.add_parser("search-rent", help="Search rentals")
    search_rent_p.add_argument("--city", help="City", default=None)
    search_rent_p.add_argument("--state_code", help="State", default=None)
    search_rent_p.add_argument("--postal_code", help="ZIP", default=None)
    search_rent_p.set_defaults(func=cmd_search_rent)

    search_sold_p = sub.add_parser("search-sold", help="Search recently sold")
    search_sold_p.add_argument("--city", help="City", default=None)
    search_sold_p.add_argument("--state_code", help="State", default=None)
    search_sold_p.set_defaults(func=cmd_search_sold)

    property_p = sub.add_parser("property", help="Get property details")
    property_p.add_argument("--property_id", help="Property ID", default=None)
    property_p.set_defaults(func=cmd_property)

    agents_p = sub.add_parser("agents", help="Search agents")
    agents_p.add_argument("--city", help="City", default=None)
    agents_p.add_argument("--state_code", help="State", default=None)
    agents_p.add_argument("--name", help="Name", default=None)
    agents_p.set_defaults(func=cmd_agents)

    agent_get_p = sub.add_parser("agent-get", help="Get agent details")
    agent_get_p.add_argument("--nrds_id", help="NRDS ID", default=None)
    agent_get_p.set_defaults(func=cmd_agent_get)

    auto_complete_p = sub.add_parser("auto-complete", help="Location auto-complete")
    auto_complete_p.add_argument("--input", help="Search input", default=None)
    auto_complete_p.set_defaults(func=cmd_auto_complete)


    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
