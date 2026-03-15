#!/usr/bin/env python3
"""Lemon Squeezy API CLI. Zero dependencies beyond Python stdlib."""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse


def get_token():
    token = os.environ.get("LEMONSQUEEZY_API_KEY", "")
    if not token:
        env_path = os.path.join(os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("LEMONSQUEEZY_API_KEY="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not token:
        print("Error: LEMONSQUEEZY_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return token


def api(method, path, data=None, params=None):
    url = "https://api.lemonsqueezy.com/v1" + path
    if params: url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {get_token()}")
    req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        raw = resp.read().decode()
        return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        print(f"API Error {e.code}: {e.read().decode()}", file=sys.stderr); sys.exit(1)


def _list(path, a):
    d = api("GET", path, params={"page[size]": str(a.limit)} if hasattr(a,"limit") else {})
    for item in d.get("data",[]): print(json.dumps({"id":item["id"],"type":item["type"],"attributes":item.get("attributes",{})}))

def cmd_stores(a): _list("/stores", a)
def cmd_products(a): _list("/products", a)
def cmd_variants(a): _list("/variants", a)
def cmd_orders(a): _list("/orders", a)
def cmd_subscriptions(a): _list("/subscriptions", a)
def cmd_customers(a): _list("/customers", a)
def cmd_checkouts(a): _list("/checkouts", a)
def cmd_license_keys(a): _list("/license-keys", a)
def cmd_discounts(a): _list("/discounts", a)

def cmd_product_get(a): print(json.dumps(api("GET", f"/products/{a.id}"), indent=2))
def cmd_order_get(a): print(json.dumps(api("GET", f"/orders/{a.id}"), indent=2))
def cmd_subscription_get(a): print(json.dumps(api("GET", f"/subscriptions/{a.id}"), indent=2))

def cmd_subscription_cancel(a):
    print(json.dumps(api("DELETE", f"/subscriptions/{a.id}"), indent=2))

def cmd_checkout_create(a):
    d = {"data":{"type":"checkouts","attributes":{"checkout_data":json.loads(a.data) if a.data else {}},"relationships":{"store":{"data":{"type":"stores","id":a.store_id}},"variant":{"data":{"type":"variants","id":a.variant_id}}}}}
    print(json.dumps(api("POST", "/checkouts", d), indent=2))

def cmd_license_activate(a):
    body = json.dumps({"license_key": a.key, "instance_name": a.instance}).encode()
    req = urllib.request.Request("https://api.lemonsqueezy.com/v1/licenses/activate", data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        print(json.dumps(json.loads(resp.read().decode()), indent=2))
    except urllib.error.HTTPError as e:
        print(f"Error: {e.read().decode()}", file=sys.stderr); sys.exit(1)

def cmd_license_validate(a):
    body = json.dumps({"license_key": a.key}).encode()
    req = urllib.request.Request("https://api.lemonsqueezy.com/v1/licenses/validate", data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        print(json.dumps(json.loads(resp.read().decode()), indent=2))
    except urllib.error.HTTPError as e:
        print(f"Error: {e.read().decode()}", file=sys.stderr); sys.exit(1)

def cmd_me(a): print(json.dumps(api("GET", "/users/me"), indent=2))

def main():
    p = argparse.ArgumentParser(description="Lemon Squeezy CLI — digital products & subscriptions")
    s = p.add_subparsers(dest="command")
    s.add_parser("stores")
    x = s.add_parser("products"); x.add_argument("--limit", type=int, default=50)
    x = s.add_parser("product"); x.add_argument("id")
    x = s.add_parser("variants"); x.add_argument("--limit", type=int, default=50)
    x = s.add_parser("orders"); x.add_argument("--limit", type=int, default=50)
    x = s.add_parser("order"); x.add_argument("id")
    x = s.add_parser("subscriptions"); x.add_argument("--limit", type=int, default=50)
    x = s.add_parser("subscription"); x.add_argument("id")
    x = s.add_parser("subscription-cancel"); x.add_argument("id")
    x = s.add_parser("customers"); x.add_argument("--limit", type=int, default=50)
    x = s.add_parser("checkouts"); x.add_argument("--limit", type=int, default=50)
    x = s.add_parser("checkout-create"); x.add_argument("store_id"); x.add_argument("variant_id"); x.add_argument("--data")
    x = s.add_parser("license-keys"); x.add_argument("--limit", type=int, default=50)
    x = s.add_parser("license-activate"); x.add_argument("key"); x.add_argument("instance")
    x = s.add_parser("license-validate"); x.add_argument("key")
    x = s.add_parser("discounts"); x.add_argument("--limit", type=int, default=50)
    s.add_parser("me")
    a = p.parse_args()
    c = {"stores":cmd_stores,"products":cmd_products,"product":cmd_product_get,"variants":cmd_variants,"orders":cmd_orders,"order":cmd_order_get,"subscriptions":cmd_subscriptions,"subscription":cmd_subscription_get,"subscription-cancel":cmd_subscription_cancel,"customers":cmd_customers,"checkouts":cmd_checkouts,"checkout-create":cmd_checkout_create,"license-keys":cmd_license_keys,"license-activate":cmd_license_activate,"license-validate":cmd_license_validate,"discounts":cmd_discounts,"me":cmd_me}
    if a.command in c: c[a.command](a)
    else: p.print_help()

if __name__ == "__main__": main()
