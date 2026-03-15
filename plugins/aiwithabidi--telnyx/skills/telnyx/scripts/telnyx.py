#!/usr/bin/env python3
"""Telnyx CLI — Telnyx — voice, SMS/MMS messaging, SIP trunking, number management, and fax.

Zero dependencies beyond Python stdlib.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "https://api.telnyx.com/v2"


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
    token = get_env("TELNYX_API_KEY")
    if not token:
        print("Error: TELNYX_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{base}{path}"
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v}, doseq=True)
        url = f"{url}{'&' if '?' in url else '?'}{qs}"
    return req(method, url, data=data, headers=headers)


def out(data):
    print(json.dumps(data, indent=2, default=str))


def cmd_send_message(args):
    """Send SMS/MMS"""
    path = "/messages"
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
    """List messages"""
    path = "/messages"
    params = {}
    if args.page_size:
        params["page-size"] = args.page_size
    result = api("GET", path, params=params)
    out(result)

def cmd_create_call(args):
    """Create outbound call"""
    path = "/calls"
    data = {}
    if getattr(args, 'from'):
        data["from"] = getattr(args, 'from')
    if args.to:
        data["to"] = args.to
    if args.connection_id:
        data["connection-id"] = args.connection_id
    result = api("POST", path, data=data)
    out(result)

def cmd_list_calls(args):
    """List active calls"""
    path = "/calls"
    result = api("GET", path)
    out(result)

def cmd_get_call(args):
    """Get call details"""
    path = "/calls/{id}"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_hangup_call(args):
    """Hang up call"""
    path = "/calls/{id}/actions/hangup"
    path = path.replace("{id}", str(args.id))
    data = {}
    result = api("POST", path, data=data)
    out(result)

def cmd_list_numbers(args):
    """List phone numbers"""
    path = "/phone_numbers"
    params = {}
    if args.page_size:
        params["page-size"] = args.page_size
    result = api("GET", path, params=params)
    out(result)

def cmd_search_numbers(args):
    """Search available numbers"""
    path = "/available_phone_numbers"
    params = {}
    if args.country_code:
        params["country-code"] = args.country_code
    if args.limit:
        params["limit"] = args.limit
    result = api("GET", path, params=params)
    out(result)

def cmd_order_number(args):
    """Order phone number"""
    path = "/number_orders"
    data = {}
    if args.phone_numbers:
        data["phone-numbers"] = args.phone_numbers
    result = api("POST", path, data=data)
    out(result)

def cmd_list_connections(args):
    """List SIP connections"""
    path = "/connections"
    result = api("GET", path)
    out(result)

def cmd_create_connection(args):
    """Create SIP connection"""
    path = "/connections"
    data = {}
    if args.name:
        data["name"] = args.name
    if args.connection_type:
        data["connection-type"] = args.connection_type
    result = api("POST", path, data=data)
    out(result)

def cmd_send_fax(args):
    """Send a fax"""
    path = "/faxes"
    data = {}
    if getattr(args, 'from'):
        data["from"] = getattr(args, 'from')
    if args.to:
        data["to"] = args.to
    if args.media_url:
        data["media-url"] = args.media_url
    result = api("POST", path, data=data)
    out(result)

def cmd_list_faxes(args):
    """List faxes"""
    path = "/faxes"
    result = api("GET", path)
    out(result)

def cmd_get_balance(args):
    """Get account balance"""
    path = "/balance"
    result = api("GET", path)
    out(result)


def main():
    parser = argparse.ArgumentParser(description="Telnyx CLI")
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    p_send_message = sub.add_parser("send-message", help="Send SMS/MMS")
    p_send_message.add_argument("--from", dest="from_addr", required=True)
    p_send_message.add_argument("--to", required=True)
    p_send_message.add_argument("--text", required=True)
    p_send_message.set_defaults(func=cmd_send_message)

    p_list_messages = sub.add_parser("list-messages", help="List messages")
    p_list_messages.add_argument("--page-size", default="25")
    p_list_messages.set_defaults(func=cmd_list_messages)

    p_create_call = sub.add_parser("create-call", help="Create outbound call")
    p_create_call.add_argument("--from", dest="from_addr", required=True)
    p_create_call.add_argument("--to", required=True)
    p_create_call.add_argument("--connection-id", required=True)
    p_create_call.set_defaults(func=cmd_create_call)

    p_list_calls = sub.add_parser("list-calls", help="List active calls")
    p_list_calls.set_defaults(func=cmd_list_calls)

    p_get_call = sub.add_parser("get-call", help="Get call details")
    p_get_call.add_argument("id")
    p_get_call.set_defaults(func=cmd_get_call)

    p_hangup_call = sub.add_parser("hangup-call", help="Hang up call")
    p_hangup_call.add_argument("id")
    p_hangup_call.set_defaults(func=cmd_hangup_call)

    p_list_numbers = sub.add_parser("list-numbers", help="List phone numbers")
    p_list_numbers.add_argument("--page-size", default="25")
    p_list_numbers.set_defaults(func=cmd_list_numbers)

    p_search_numbers = sub.add_parser("search-numbers", help="Search available numbers")
    p_search_numbers.add_argument("--country-code", default="US")
    p_search_numbers.add_argument("--limit", default="10")
    p_search_numbers.set_defaults(func=cmd_search_numbers)

    p_order_number = sub.add_parser("order-number", help="Order phone number")
    p_order_number.add_argument("--phone-numbers", default="JSON array")
    p_order_number.set_defaults(func=cmd_order_number)

    p_list_connections = sub.add_parser("list-connections", help="List SIP connections")
    p_list_connections.set_defaults(func=cmd_list_connections)

    p_create_connection = sub.add_parser("create-connection", help="Create SIP connection")
    p_create_connection.add_argument("--name", required=True)
    p_create_connection.add_argument("--connection-type", default="ip")
    p_create_connection.set_defaults(func=cmd_create_connection)

    p_send_fax = sub.add_parser("send-fax", help="Send a fax")
    p_send_fax.add_argument("--from", dest="from_addr", required=True)
    p_send_fax.add_argument("--to", required=True)
    p_send_fax.add_argument("--media-url", required=True)
    p_send_fax.set_defaults(func=cmd_send_fax)

    p_list_faxes = sub.add_parser("list-faxes", help="List faxes")
    p_list_faxes.set_defaults(func=cmd_list_faxes)

    p_get_balance = sub.add_parser("get-balance", help="Get account balance")
    p_get_balance.set_defaults(func=cmd_get_balance)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
