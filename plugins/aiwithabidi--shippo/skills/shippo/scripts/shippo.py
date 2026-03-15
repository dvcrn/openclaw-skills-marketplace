#!/usr/bin/env python3
"""Shippo CLI — Shippo — shipping labels, rates comparison, package tracking, address validation, and returns.

Zero dependencies beyond Python stdlib.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "https://api.goshippo.com"


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
    token = get_env("SHIPPO_API_TOKEN")
    if not token:
        print("Error: SHIPPO_API_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{base}{path}"
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v}, doseq=True)
        url = f"{url}{'&' if '?' in url else '?'}{qs}"
    return req(method, url, data=data, headers=headers)


def out(data):
    print(json.dumps(data, indent=2, default=str))


def cmd_create_shipment(args):
    """Create shipment & get rates"""
    path = "/shipments"
    data = {}
    if getattr(args, 'from'):
        data["from"] = getattr(args, 'from')
    if args.to:
        data["to"] = args.to
    if args.parcel:
        data["parcel"] = args.parcel
    result = api("POST", path, data=data)
    out(result)

def cmd_list_shipments(args):
    """List shipments"""
    path = "/shipments"
    params = {}
    if args.results:
        params["results"] = args.results
    if args.page:
        params["page"] = args.page
    result = api("GET", path, params=params)
    out(result)

def cmd_get_shipment(args):
    """Get shipment details"""
    path = "/shipments/{id}"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_get_rates(args):
    """Get rates for shipment"""
    path = "/shipments/{id}/rates"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_purchase_label(args):
    """Purchase shipping label"""
    path = "/transactions"
    data = {}
    if args.rate:
        data["rate"] = args.rate
    result = api("POST", path, data=data)
    out(result)

def cmd_list_transactions(args):
    """List label transactions"""
    path = "/transactions"
    params = {}
    if args.results:
        params["results"] = args.results
    result = api("GET", path, params=params)
    out(result)

def cmd_get_transaction(args):
    """Get label/transaction details"""
    path = "/transactions/{id}"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_track_package(args):
    """Track a package"""
    path = "/tracks/{carrier}/{tracking_number}"
    path = path.replace("{carrier}", str(args.carrier or ""))
    path = path.replace("{tracking-number}", str(args.tracking_number or ""))
    params = {}
    if args.tracking_number:
        params["tracking-number"] = args.tracking_number
    result = api("GET", path, params=params)
    out(result)

def cmd_validate_address(args):
    """Validate an address"""
    path = "/addresses"
    data = {}
    if args.name:
        data["name"] = args.name
    if args.street1:
        data["street1"] = args.street1
    if args.city:
        data["city"] = args.city
    if args.state:
        data["state"] = args.state
    if args.zip:
        data["zip"] = args.zip
    if args.country:
        data["country"] = args.country
    result = api("POST", path, data=data)
    out(result)

def cmd_list_parcels(args):
    """List saved parcels"""
    path = "/parcels"
    result = api("GET", path)
    out(result)

def cmd_create_parcel(args):
    """Create a parcel template"""
    path = "/parcels"
    data = {}
    if args.length:
        data["length"] = args.length
    if args.width:
        data["width"] = args.width
    if args.height:
        data["height"] = args.height
    if args.weight:
        data["weight"] = args.weight
    result = api("POST", path, data=data)
    out(result)

def cmd_create_return(args):
    """Create return shipment"""
    path = "/shipments"
    data = {}
    if getattr(args, 'from'):
        data["from"] = getattr(args, 'from')
    if args.to:
        data["to"] = args.to
    if args.parcel:
        data["parcel"] = args.parcel
    if args.is_return:
        data["is-return"] = args.is_return
    result = api("POST", path, data=data)
    out(result)

def cmd_list_carriers(args):
    """List carrier accounts"""
    path = "/carrier_accounts"
    result = api("GET", path)
    out(result)


def main():
    parser = argparse.ArgumentParser(description="Shippo CLI")
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    p_create_shipment = sub.add_parser("create-shipment", help="Create shipment & get rates")
    p_create_shipment.add_argument("--from", dest="from_addr", default="JSON address")
    p_create_shipment.add_argument("--to", default="JSON address")
    p_create_shipment.add_argument("--parcel", default="JSON")
    p_create_shipment.set_defaults(func=cmd_create_shipment)

    p_list_shipments = sub.add_parser("list-shipments", help="List shipments")
    p_list_shipments.add_argument("--results", default="25")
    p_list_shipments.add_argument("--page", default="1")
    p_list_shipments.set_defaults(func=cmd_list_shipments)

    p_get_shipment = sub.add_parser("get-shipment", help="Get shipment details")
    p_get_shipment.add_argument("id")
    p_get_shipment.set_defaults(func=cmd_get_shipment)

    p_get_rates = sub.add_parser("get-rates", help="Get rates for shipment")
    p_get_rates.add_argument("id")
    p_get_rates.set_defaults(func=cmd_get_rates)

    p_purchase_label = sub.add_parser("purchase-label", help="Purchase shipping label")
    p_purchase_label.add_argument("--rate", required=True)
    p_purchase_label.set_defaults(func=cmd_purchase_label)

    p_list_transactions = sub.add_parser("list-transactions", help="List label transactions")
    p_list_transactions.add_argument("--results", default="25")
    p_list_transactions.set_defaults(func=cmd_list_transactions)

    p_get_transaction = sub.add_parser("get-transaction", help="Get label/transaction details")
    p_get_transaction.add_argument("id")
    p_get_transaction.set_defaults(func=cmd_get_transaction)

    p_track_package = sub.add_parser("track-package", help="Track a package")
    p_track_package.add_argument("--carrier", required=True)
    p_track_package.add_argument("--tracking-number", required=True)
    p_track_package.set_defaults(func=cmd_track_package)

    p_validate_address = sub.add_parser("validate-address", help="Validate an address")
    p_validate_address.add_argument("--name", required=True)
    p_validate_address.add_argument("--street1", required=True)
    p_validate_address.add_argument("--city", required=True)
    p_validate_address.add_argument("--state", required=True)
    p_validate_address.add_argument("--zip", required=True)
    p_validate_address.add_argument("--country", default="US")
    p_validate_address.set_defaults(func=cmd_validate_address)

    p_list_parcels = sub.add_parser("list-parcels", help="List saved parcels")
    p_list_parcels.set_defaults(func=cmd_list_parcels)

    p_create_parcel = sub.add_parser("create-parcel", help="Create a parcel template")
    p_create_parcel.add_argument("--length", required=True)
    p_create_parcel.add_argument("--width", required=True)
    p_create_parcel.add_argument("--height", required=True)
    p_create_parcel.add_argument("--weight", required=True)
    p_create_parcel.set_defaults(func=cmd_create_parcel)

    p_create_return = sub.add_parser("create-return", help="Create return shipment")
    p_create_return.add_argument("--from", dest="from_addr", default="JSON")
    p_create_return.add_argument("--to", default="JSON")
    p_create_return.add_argument("--parcel", default="JSON")
    p_create_return.add_argument("--is-return", default="true")
    p_create_return.set_defaults(func=cmd_create_return)

    p_list_carriers = sub.add_parser("list-carriers", help="List carrier accounts")
    p_list_carriers.set_defaults(func=cmd_list_carriers)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
