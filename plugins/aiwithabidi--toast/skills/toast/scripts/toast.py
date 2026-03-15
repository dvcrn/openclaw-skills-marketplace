#!/usr/bin/env python3
"""Toast CLI — Toast — restaurant POS, orders, menus, employees, revenue centers, and reporting.

Zero dependencies beyond Python stdlib.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "https://api.toasttab.com"


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
    token = get_env("TOAST_API_KEY")
    if not token:
        print("Error: TOAST_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    headers = {"Authorization": f"Bearer {token}"}
    guid = get_env("TOAST_RESTAURANT_GUID")
    headers["Toast-Restaurant-External-ID"] = guid
    url = f"{base}{path}"
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v}, doseq=True)
        url = f"{url}{'&' if '?' in url else '?'}{qs}"
    return req(method, url, data=data, headers=headers)


def out(data):
    print(json.dumps(data, indent=2, default=str))


def cmd_list_orders(args):
    """List orders"""
    path = "/orders/v2/orders"
    params = {}
    if args.start_date:
        params["start-date"] = args.start_date
    if args.end_date:
        params["end-date"] = args.end_date
    if args.page_size:
        params["page-size"] = args.page_size
    result = api("GET", path, params=params)
    out(result)

def cmd_get_order(args):
    """Get order details"""
    path = "/orders/v2/orders/{id}"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_list_menus(args):
    """List menus"""
    path = "/menus/v2/menus"
    result = api("GET", path)
    out(result)

def cmd_get_menu(args):
    """Get menu details"""
    path = "/menus/v2/menus/{id}"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_list_menu_items(args):
    """List menu items"""
    path = "/menus/v2/menuItems"
    params = {}
    if args.page_size:
        params["page-size"] = args.page_size
    result = api("GET", path, params=params)
    out(result)

def cmd_list_employees(args):
    """List employees"""
    path = "/labor/v1/employees"
    result = api("GET", path)
    out(result)

def cmd_get_employee(args):
    """Get employee details"""
    path = "/labor/v1/employees/{id}"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_list_revenue_centers(args):
    """List revenue centers"""
    path = "/config/v2/revenueCenters"
    result = api("GET", path)
    out(result)

def cmd_list_tables(args):
    """List tables"""
    path = "/config/v2/tables"
    result = api("GET", path)
    out(result)

def cmd_list_dining_options(args):
    """List dining options"""
    path = "/config/v2/diningOptions"
    result = api("GET", path)
    out(result)

def cmd_get_restaurant(args):
    """Get restaurant info"""
    path = "/restaurants/v1/restaurants/{guid}"
    path = path.replace("{guid}", str(args.guid or ""))
    result = api("GET", path)
    out(result)


def main():
    parser = argparse.ArgumentParser(description="Toast CLI")
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    p_list_orders = sub.add_parser("list-orders", help="List orders")
    p_list_orders.add_argument("--start-date", required=True)
    p_list_orders.add_argument("--end-date", required=True)
    p_list_orders.add_argument("--page-size", default="25")
    p_list_orders.set_defaults(func=cmd_list_orders)

    p_get_order = sub.add_parser("get-order", help="Get order details")
    p_get_order.add_argument("id")
    p_get_order.set_defaults(func=cmd_get_order)

    p_list_menus = sub.add_parser("list-menus", help="List menus")
    p_list_menus.set_defaults(func=cmd_list_menus)

    p_get_menu = sub.add_parser("get-menu", help="Get menu details")
    p_get_menu.add_argument("id")
    p_get_menu.set_defaults(func=cmd_get_menu)

    p_list_menu_items = sub.add_parser("list-menu-items", help="List menu items")
    p_list_menu_items.add_argument("--page-size", default="100")
    p_list_menu_items.set_defaults(func=cmd_list_menu_items)

    p_list_employees = sub.add_parser("list-employees", help="List employees")
    p_list_employees.set_defaults(func=cmd_list_employees)

    p_get_employee = sub.add_parser("get-employee", help="Get employee details")
    p_get_employee.add_argument("id")
    p_get_employee.set_defaults(func=cmd_get_employee)

    p_list_revenue_centers = sub.add_parser("list-revenue-centers", help="List revenue centers")
    p_list_revenue_centers.set_defaults(func=cmd_list_revenue_centers)

    p_list_tables = sub.add_parser("list-tables", help="List tables")
    p_list_tables.set_defaults(func=cmd_list_tables)

    p_list_dining_options = sub.add_parser("list-dining-options", help="List dining options")
    p_list_dining_options.set_defaults(func=cmd_list_dining_options)

    p_get_restaurant = sub.add_parser("get-restaurant", help="Get restaurant info")
    p_get_restaurant.add_argument("--guid", required=True)
    p_get_restaurant.set_defaults(func=cmd_get_restaurant)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
