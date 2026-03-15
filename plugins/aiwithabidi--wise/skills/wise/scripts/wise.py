#!/usr/bin/env python3
"""Wise CLI — Wise (TransferWise) — international transfers, multi-currency balances, recipients, exchange rates, and statements.

Zero dependencies beyond Python stdlib.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "https://api.transferwise.com"


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
    token = get_env("WISE_API_TOKEN")
    if not token:
        print("Error: WISE_API_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    headers = {"Authorization": f"Bearer {token}"}
    base = API_BASE
    url = f"{base}{path}"
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v}, doseq=True)
        url = f"{url}{'&' if '?' in url else '?'}{qs}"
    return req(method, url, data=data, headers=headers)


def out(data):
    print(json.dumps(data, indent=2, default=str))


def cmd_get_profiles(args):
    """List profiles (personal/business)"""
    path = "/v2/profiles"
    result = api("GET", path)
    out(result)

def cmd_get_balances(args):
    """Get multi-currency balances"""
    path = "/v4/profiles/{profile_id}/balances?types=STANDARD"
    path = path.replace("{profile-id}", str(args.profile_id or ""))
    params = {}
    if args.profile_id:
        params["profile-id"] = args.profile_id
    result = api("GET", path, params=params)
    out(result)

def cmd_list_recipients(args):
    """List recipients"""
    path = "/v1/accounts?profile={profile_id}"
    path = path.replace("{profile-id}", str(args.profile_id or ""))
    params = {}
    if args.profile_id:
        params["profile-id"] = args.profile_id
    result = api("GET", path, params=params)
    out(result)

def cmd_create_recipient(args):
    """Create recipient"""
    path = "/v1/accounts"
    data = {}
    if args.profile_id:
        data["profile-id"] = args.profile_id
    if args.currency:
        data["currency"] = args.currency
    if args.type:
        data["type"] = args.type
    if args.details:
        data["details"] = args.details
    result = api("POST", path, data=data)
    out(result)

def cmd_create_quote(args):
    """Create transfer quote"""
    path = "/v3/profiles/{profile_id}/quotes"
    path = path.replace("{profile-id}", str(args.profile_id or ""))
    data = {}
    if args.profile_id:
        data["profile-id"] = args.profile_id
    if args.source:
        data["source"] = args.source
    if args.target:
        data["target"] = args.target
    if args.amount:
        data["amount"] = args.amount
    result = api("POST", path, data=data)
    out(result)

def cmd_create_transfer(args):
    """Create transfer"""
    path = "/v1/transfers"
    data = {}
    if args.quote_id:
        data["quote-id"] = args.quote_id
    if args.recipient_id:
        data["recipient-id"] = args.recipient_id
    if args.reference:
        data["reference"] = args.reference
    result = api("POST", path, data=data)
    out(result)

def cmd_fund_transfer(args):
    """Fund a transfer"""
    path = "/v3/profiles/{profile_id}/transfers/{transfer_id}/payments"
    path = path.replace("{profile-id}", str(args.profile_id or ""))
    path = path.replace("{transfer-id}", str(args.transfer_id or ""))
    data = {}
    if args.profile_id:
        data["profile-id"] = args.profile_id
    if args.transfer_id:
        data["transfer-id"] = args.transfer_id
    result = api("POST", path, data=data)
    out(result)

def cmd_get_transfer(args):
    """Get transfer status"""
    path = "/v1/transfers/{id}"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_list_transfers(args):
    """List transfers"""
    path = "/v1/transfers?profile={profile_id}&limit={limit}"
    path = path.replace("{profile-id}", str(args.profile_id or ""))
    path = path.replace("{limit}", str(args.limit or ""))
    params = {}
    if args.profile_id:
        params["profile-id"] = args.profile_id
    result = api("GET", path, params=params)
    out(result)

def cmd_get_rate(args):
    """Get exchange rate"""
    path = "/v1/rates?source={source}&target={target}"
    path = path.replace("{source}", str(args.source or ""))
    path = path.replace("{target}", str(args.target or ""))
    result = api("GET", path)
    out(result)

def cmd_get_statement(args):
    """Get statement"""
    path = "/v1/profiles/{profile_id}/balance-statements/{balance_id}/statement"
    path = path.replace("{profile-id}", str(args.profile_id or ""))
    path = path.replace("{balance-id}", str(args.balance_id or ""))
    params = {}
    if args.profile_id:
        params["profile-id"] = args.profile_id
    if args.balance_id:
        params["balance-id"] = args.balance_id
    result = api("GET", path, params=params)
    out(result)


def main():
    parser = argparse.ArgumentParser(description="Wise CLI")
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    p_get_profiles = sub.add_parser("get-profiles", help="List profiles (personal/business)")
    p_get_profiles.set_defaults(func=cmd_get_profiles)

    p_get_balances = sub.add_parser("get-balances", help="Get multi-currency balances")
    p_get_balances.add_argument("--profile-id", required=True)
    p_get_balances.set_defaults(func=cmd_get_balances)

    p_list_recipients = sub.add_parser("list-recipients", help="List recipients")
    p_list_recipients.add_argument("--profile-id", required=True)
    p_list_recipients.set_defaults(func=cmd_list_recipients)

    p_create_recipient = sub.add_parser("create-recipient", help="Create recipient")
    p_create_recipient.add_argument("--profile-id", required=True)
    p_create_recipient.add_argument("--currency", required=True)
    p_create_recipient.add_argument("--type", required=True)
    p_create_recipient.add_argument("--details", default="JSON")
    p_create_recipient.set_defaults(func=cmd_create_recipient)

    p_create_quote = sub.add_parser("create-quote", help="Create transfer quote")
    p_create_quote.add_argument("--profile-id", required=True)
    p_create_quote.add_argument("--source", required=True)
    p_create_quote.add_argument("--target", required=True)
    p_create_quote.add_argument("--amount", required=True)
    p_create_quote.set_defaults(func=cmd_create_quote)

    p_create_transfer = sub.add_parser("create-transfer", help="Create transfer")
    p_create_transfer.add_argument("--quote-id", required=True)
    p_create_transfer.add_argument("--recipient-id", required=True)
    p_create_transfer.add_argument("--reference", required=True)
    p_create_transfer.set_defaults(func=cmd_create_transfer)

    p_fund_transfer = sub.add_parser("fund-transfer", help="Fund a transfer")
    p_fund_transfer.add_argument("--profile-id", required=True)
    p_fund_transfer.add_argument("--transfer-id", required=True)
    p_fund_transfer.set_defaults(func=cmd_fund_transfer)

    p_get_transfer = sub.add_parser("get-transfer", help="Get transfer status")
    p_get_transfer.add_argument("id")
    p_get_transfer.set_defaults(func=cmd_get_transfer)

    p_list_transfers = sub.add_parser("list-transfers", help="List transfers")
    p_list_transfers.add_argument("--profile-id", required=True)
    p_list_transfers.add_argument("--limit", default="10")
    p_list_transfers.set_defaults(func=cmd_list_transfers)

    p_get_rate = sub.add_parser("get-rate", help="Get exchange rate")
    p_get_rate.add_argument("--source", required=True)
    p_get_rate.add_argument("--target", required=True)
    p_get_rate.set_defaults(func=cmd_get_rate)

    p_get_statement = sub.add_parser("get-statement", help="Get statement")
    p_get_statement.add_argument("--profile-id", required=True)
    p_get_statement.add_argument("--balance-id", required=True)
    p_get_statement.set_defaults(func=cmd_get_statement)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
