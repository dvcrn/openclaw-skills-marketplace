#!/usr/bin/env python3
"""Vonage CLI — Vonage — SMS messaging, voice calls, verify API, number management, and application management.

Zero dependencies beyond Python stdlib.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "https://api.nexmo.com"


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
    api_key = get_env("VONAGE_API_KEY")
    api_secret = get_env("VONAGE_API_SECRET")
    if not api_key:
        print("Error: VONAGE_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    headers = {}
    if params is None:
        params = {}
    params["api_key"] = api_key
    params["api_secret"] = api_secret
    url = f"{base}{path}"
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v}, doseq=True)
        url = f"{url}{'&' if '?' in url else '?'}{qs}"
    return req(method, url, data=data, headers=headers)


def out(data):
    print(json.dumps(data, indent=2, default=str))


def cmd_send_sms(args):
    """Send SMS"""
    path = "/sms/json"
    data = {}
    if getattr(args, 'from'):
        data["from"] = getattr(args, 'from')
    if args.to:
        data["to"] = args.to
    if args.text:
        data["text"] = args.text
    result = api("POST", path, data=data)
    out(result)

def cmd_list_messages(args):
    """Search messages"""
    path = "/search/messages?api_key={api_key}&api_secret={secret}"
    params = {}
    if args.date:
        params["date"] = args.date
    if args.to:
        params["to"] = args.to
    result = api("GET", path, params=params)
    out(result)

def cmd_create_call(args):
    """Create voice call"""
    path = "/v1/calls"
    data = {}
    if args.to:
        data["to"] = args.to
    if getattr(args, 'from'):
        data["from"] = getattr(args, 'from')
    if args.ncco:
        data["ncco"] = args.ncco
    result = api("POST", path, data=data)
    out(result)

def cmd_list_calls(args):
    """List calls"""
    path = "/v1/calls"
    result = api("GET", path)
    out(result)

def cmd_get_call(args):
    """Get call details"""
    path = "/v1/calls/{id}"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_send_verify(args):
    """Send verification code"""
    path = "/verify/json"
    data = {}
    if args.number:
        data["number"] = args.number
    if args.brand:
        data["brand"] = args.brand
    result = api("POST", path, data=data)
    out(result)

def cmd_check_verify(args):
    """Check verification code"""
    path = "/verify/check/json"
    data = {}
    if args.request_id:
        data["request-id"] = args.request_id
    if args.code:
        data["code"] = args.code
    result = api("POST", path, data=data)
    out(result)

def cmd_list_numbers(args):
    """List your numbers"""
    path = "/account/numbers"
    result = api("GET", path)
    out(result)

def cmd_search_numbers(args):
    """Search available numbers"""
    path = "/number/search"
    params = {}
    if args.country:
        params["country"] = args.country
    if args.type:
        params["type"] = args.type
    result = api("GET", path, params=params)
    out(result)

def cmd_buy_number(args):
    """Buy a number"""
    path = "/number/buy"
    data = {}
    if args.country:
        data["country"] = args.country
    if args.msisdn:
        data["msisdn"] = args.msisdn
    result = api("POST", path, data=data)
    out(result)

def cmd_list_applications(args):
    """List applications"""
    path = "/v2/applications"
    result = api("GET", path)
    out(result)

def cmd_create_application(args):
    """Create application"""
    path = "/v2/applications"
    data = {}
    if args.name:
        data["name"] = args.name
    result = api("POST", path, data=data)
    out(result)

def cmd_get_balance(args):
    """Get account balance"""
    path = "/account/get-balance"
    result = api("GET", path)
    out(result)


def main():
    parser = argparse.ArgumentParser(description="Vonage CLI")
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    p_send_sms = sub.add_parser("send-sms", help="Send SMS")
    p_send_sms.add_argument("--from", dest="from_addr", required=True)
    p_send_sms.add_argument("--to", required=True)
    p_send_sms.add_argument("--text", required=True)
    p_send_sms.set_defaults(func=cmd_send_sms)

    p_list_messages = sub.add_parser("list-messages", help="Search messages")
    p_list_messages.add_argument("--date", required=True)
    p_list_messages.add_argument("--to", required=True)
    p_list_messages.set_defaults(func=cmd_list_messages)

    p_create_call = sub.add_parser("create-call", help="Create voice call")
    p_create_call.add_argument("--to", required=True)
    p_create_call.add_argument("--from", dest="from_addr", required=True)
    p_create_call.add_argument("--ncco", default="JSON")
    p_create_call.set_defaults(func=cmd_create_call)

    p_list_calls = sub.add_parser("list-calls", help="List calls")
    p_list_calls.set_defaults(func=cmd_list_calls)

    p_get_call = sub.add_parser("get-call", help="Get call details")
    p_get_call.add_argument("id")
    p_get_call.set_defaults(func=cmd_get_call)

    p_send_verify = sub.add_parser("send-verify", help="Send verification code")
    p_send_verify.add_argument("--number", required=True)
    p_send_verify.add_argument("--brand", required=True)
    p_send_verify.set_defaults(func=cmd_send_verify)

    p_check_verify = sub.add_parser("check-verify", help="Check verification code")
    p_check_verify.add_argument("--request-id", required=True)
    p_check_verify.add_argument("--code", required=True)
    p_check_verify.set_defaults(func=cmd_check_verify)

    p_list_numbers = sub.add_parser("list-numbers", help="List your numbers")
    p_list_numbers.set_defaults(func=cmd_list_numbers)

    p_search_numbers = sub.add_parser("search-numbers", help="Search available numbers")
    p_search_numbers.add_argument("--country", default="US")
    p_search_numbers.add_argument("--type", default="mobile-lvn")
    p_search_numbers.set_defaults(func=cmd_search_numbers)

    p_buy_number = sub.add_parser("buy-number", help="Buy a number")
    p_buy_number.add_argument("--country", required=True)
    p_buy_number.add_argument("--msisdn", required=True)
    p_buy_number.set_defaults(func=cmd_buy_number)

    p_list_applications = sub.add_parser("list-applications", help="List applications")
    p_list_applications.set_defaults(func=cmd_list_applications)

    p_create_application = sub.add_parser("create-application", help="Create application")
    p_create_application.add_argument("--name", required=True)
    p_create_application.set_defaults(func=cmd_create_application)

    p_get_balance = sub.add_parser("get-balance", help="Get account balance")
    p_get_balance.set_defaults(func=cmd_get_balance)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
