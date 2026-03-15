#!/usr/bin/env python3
"""Inventory Source CLI — Inventory Source — dropship automation, supplier management, product feeds, inventory sync, and order routing.

Zero dependencies beyond Python stdlib.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "https://api.inventorysource.com/v1"


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
    token = get_env("INVENTORYSOURCE_API_KEY")
    if not token:
        print("Error: INVENTORYSOURCE_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{base}{path}"
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v}, doseq=True)
        url = f"{url}{'&' if '?' in url else '?'}{qs}"
    return req(method, url, data=data, headers=headers)


def out(data):
    print(json.dumps(data, indent=2, default=str))


def cmd_list_suppliers(args):
    """List connected suppliers"""
    path = "/suppliers"
    result = api("GET", path)
    out(result)

def cmd_get_supplier(args):
    """Get supplier details"""
    path = "/suppliers/{id}"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_list_products(args):
    """List products"""
    path = "/products"
    params = {}
    if args.page:
        params["page"] = args.page
    if args.per_page:
        params["per-page"] = args.per_page
    result = api("GET", path, params=params)
    out(result)

def cmd_get_product(args):
    """Get product details"""
    path = "/products/{id}"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_sync_inventory(args):
    """Trigger inventory sync"""
    path = "/inventory/sync"
    data = {}
    result = api("POST", path, data=data)
    out(result)

def cmd_list_orders(args):
    """List orders"""
    path = "/orders"
    params = {}
    if args.page:
        params["page"] = args.page
    if args.status:
        params["status"] = args.status
    result = api("GET", path, params=params)
    out(result)

def cmd_get_order(args):
    """Get order details"""
    path = "/orders/{id}"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_route_order(args):
    """Route order to supplier"""
    path = "/orders/{id}/route"
    path = path.replace("{id}", str(args.id))
    data = {}
    result = api("POST", path, data=data)
    out(result)

def cmd_list_integrations(args):
    """List connected stores"""
    path = "/integrations"
    result = api("GET", path)
    out(result)

def cmd_get_feed(args):
    """Get product feed"""
    path = "/feeds/{id}"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)


def main():
    parser = argparse.ArgumentParser(description="Inventory Source CLI")
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    p_list_suppliers = sub.add_parser("list-suppliers", help="List connected suppliers")
    p_list_suppliers.set_defaults(func=cmd_list_suppliers)

    p_get_supplier = sub.add_parser("get-supplier", help="Get supplier details")
    p_get_supplier.add_argument("id")
    p_get_supplier.set_defaults(func=cmd_get_supplier)

    p_list_products = sub.add_parser("list-products", help="List products")
    p_list_products.add_argument("--page", default="1")
    p_list_products.add_argument("--per-page", default="50")
    p_list_products.set_defaults(func=cmd_list_products)

    p_get_product = sub.add_parser("get-product", help="Get product details")
    p_get_product.add_argument("id")
    p_get_product.set_defaults(func=cmd_get_product)

    p_sync_inventory = sub.add_parser("sync-inventory", help="Trigger inventory sync")
    p_sync_inventory.set_defaults(func=cmd_sync_inventory)

    p_list_orders = sub.add_parser("list-orders", help="List orders")
    p_list_orders.add_argument("--page", default="1")
    p_list_orders.add_argument("--status", required=True)
    p_list_orders.set_defaults(func=cmd_list_orders)

    p_get_order = sub.add_parser("get-order", help="Get order details")
    p_get_order.add_argument("id")
    p_get_order.set_defaults(func=cmd_get_order)

    p_route_order = sub.add_parser("route-order", help="Route order to supplier")
    p_route_order.add_argument("id")
    p_route_order.set_defaults(func=cmd_route_order)

    p_list_integrations = sub.add_parser("list-integrations", help="List connected stores")
    p_list_integrations.set_defaults(func=cmd_list_integrations)

    p_get_feed = sub.add_parser("get-feed", help="Get product feed")
    p_get_feed.add_argument("id")
    p_get_feed.set_defaults(func=cmd_get_feed)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
