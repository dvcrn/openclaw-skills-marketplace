#!/usr/bin/env python3
"""Printful CLI — Printful — print-on-demand products, orders, shipping rates, mockup generation, and store management.

Zero dependencies beyond Python stdlib.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "https://api.printful.com"


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
    token = get_env("PRINTFUL_API_KEY")
    if not token:
        print("Error: PRINTFUL_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{base}{path}"
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v}, doseq=True)
        url = f"{url}{'&' if '?' in url else '?'}{qs}"
    return req(method, url, data=data, headers=headers)


def out(data):
    print(json.dumps(data, indent=2, default=str))


def cmd_list_products(args):
    """List sync products"""
    path = "/store/products"
    params = {}
    if args.limit:
        params["limit"] = args.limit
    if args.offset:
        params["offset"] = args.offset
    result = api("GET", path, params=params)
    out(result)

def cmd_get_product(args):
    """Get product details"""
    path = "/store/products/{id}"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_create_order(args):
    """Create an order"""
    path = "/orders"
    data = {}
    if args.recipient:
        data["recipient"] = args.recipient
    if args.items:
        data["items"] = args.items
    result = api("POST", path, data=data)
    out(result)

def cmd_list_orders(args):
    """List orders"""
    path = "/orders"
    params = {}
    if args.limit:
        params["limit"] = args.limit
    if args.offset:
        params["offset"] = args.offset
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

def cmd_cancel_order(args):
    """Cancel an order"""
    path = "/orders/{id}"
    path = path.replace("{id}", str(args.id))
    result = api("DELETE", path)
    out(result)

def cmd_estimate_costs(args):
    """Estimate order costs"""
    path = "/orders/estimate-costs"
    data = {}
    if args.recipient:
        data["recipient"] = args.recipient
    if args.items:
        data["items"] = args.items
    result = api("POST", path, data=data)
    out(result)

def cmd_get_shipping_rates(args):
    """Calculate shipping rates"""
    path = "/shipping/rates"
    data = {}
    if args.recipient:
        data["recipient"] = args.recipient
    if args.items:
        data["items"] = args.items
    result = api("POST", path, data=data)
    out(result)

def cmd_list_catalog(args):
    """Browse product catalog"""
    path = "/products"
    params = {}
    if args.category:
        params["category"] = args.category
    result = api("GET", path, params=params)
    out(result)

def cmd_get_catalog_product(args):
    """Get catalog product details"""
    path = "/products/{id}"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_list_mockup_templates(args):
    """List mockup templates"""
    path = "/mockup-generator/templates/{product_id}"
    path = path.replace("{product-id}", str(args.product_id or ""))
    params = {}
    if args.product_id:
        params["product-id"] = args.product_id
    result = api("GET", path, params=params)
    out(result)

def cmd_create_mockup(args):
    """Generate mockup"""
    path = "/mockup-generator/create-task/{product_id}"
    path = path.replace("{product-id}", str(args.product_id or ""))
    data = {}
    if args.product_id:
        data["product-id"] = args.product_id
    if args.files:
        data["files"] = args.files
    result = api("POST", path, data=data)
    out(result)

def cmd_list_warehouses(args):
    """List warehouses"""
    path = "/warehouses"
    result = api("GET", path)
    out(result)

def cmd_list_countries(args):
    """List supported countries"""
    path = "/countries"
    result = api("GET", path)
    out(result)

def cmd_get_store_info(args):
    """Get store info"""
    path = "/stores"
    result = api("GET", path)
    out(result)


def main():
    parser = argparse.ArgumentParser(description="Printful CLI")
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    p_list_products = sub.add_parser("list-products", help="List sync products")
    p_list_products.add_argument("--limit", default="20")
    p_list_products.add_argument("--offset", default="0")
    p_list_products.set_defaults(func=cmd_list_products)

    p_get_product = sub.add_parser("get-product", help="Get product details")
    p_get_product.add_argument("id")
    p_get_product.set_defaults(func=cmd_get_product)

    p_create_order = sub.add_parser("create-order", help="Create an order")
    p_create_order.add_argument("--recipient", default="JSON")
    p_create_order.add_argument("--items", default="JSON array")
    p_create_order.set_defaults(func=cmd_create_order)

    p_list_orders = sub.add_parser("list-orders", help="List orders")
    p_list_orders.add_argument("--limit", default="20")
    p_list_orders.add_argument("--offset", default="0")
    p_list_orders.add_argument("--status", required=True)
    p_list_orders.set_defaults(func=cmd_list_orders)

    p_get_order = sub.add_parser("get-order", help="Get order details")
    p_get_order.add_argument("id")
    p_get_order.set_defaults(func=cmd_get_order)

    p_cancel_order = sub.add_parser("cancel-order", help="Cancel an order")
    p_cancel_order.add_argument("id")
    p_cancel_order.set_defaults(func=cmd_cancel_order)

    p_estimate_costs = sub.add_parser("estimate-costs", help="Estimate order costs")
    p_estimate_costs.add_argument("--recipient", default="JSON")
    p_estimate_costs.add_argument("--items", default="JSON array")
    p_estimate_costs.set_defaults(func=cmd_estimate_costs)

    p_get_shipping_rates = sub.add_parser("get-shipping-rates", help="Calculate shipping rates")
    p_get_shipping_rates.add_argument("--recipient", default="JSON")
    p_get_shipping_rates.add_argument("--items", default="JSON array")
    p_get_shipping_rates.set_defaults(func=cmd_get_shipping_rates)

    p_list_catalog = sub.add_parser("list-catalog", help="Browse product catalog")
    p_list_catalog.add_argument("--category", required=True)
    p_list_catalog.set_defaults(func=cmd_list_catalog)

    p_get_catalog_product = sub.add_parser("get-catalog-product", help="Get catalog product details")
    p_get_catalog_product.add_argument("id")
    p_get_catalog_product.set_defaults(func=cmd_get_catalog_product)

    p_list_mockup_templates = sub.add_parser("list-mockup-templates", help="List mockup templates")
    p_list_mockup_templates.add_argument("--product-id", required=True)
    p_list_mockup_templates.set_defaults(func=cmd_list_mockup_templates)

    p_create_mockup = sub.add_parser("create-mockup", help="Generate mockup")
    p_create_mockup.add_argument("--product-id", required=True)
    p_create_mockup.add_argument("--files", default="JSON")
    p_create_mockup.set_defaults(func=cmd_create_mockup)

    p_list_warehouses = sub.add_parser("list-warehouses", help="List warehouses")
    p_list_warehouses.set_defaults(func=cmd_list_warehouses)

    p_list_countries = sub.add_parser("list-countries", help="List supported countries")
    p_list_countries.set_defaults(func=cmd_list_countries)

    p_get_store_info = sub.add_parser("get-store-info", help="Get store info")
    p_get_store_info.set_defaults(func=cmd_get_store_info)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
