#!/usr/bin/env python3
"""Smoobu API helper script for OpenClaw."""

import argparse
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from datetime import datetime, timedelta

BASE_URL = "https://login.smoobu.com"

def get_api_key():
    """Get API key from environment or secrets files."""
    key = os.environ.get("SMOOBU_API_KEY")
    if not key:
        # Try loading from secrets/smoobu.env first
        secrets_path = os.path.expanduser("~/.openclaw/secrets/smoobu.env")
        if os.path.exists(secrets_path):
            with open(secrets_path) as f:
                for line in f:
                    if line.startswith("SMOOBU_API_KEY="):
                        key = line.split("=", 1)[1].strip()
                        break
    if not key:
        # Fallback to property.env (legacy)
        legacy_path = os.path.expanduser("~/.openclaw/secrets/property.env")
        if os.path.exists(legacy_path):
            with open(legacy_path) as f:
                for line in f:
                    if line.startswith("SMOOBU_API_KEY="):
                        key = line.split("=", 1)[1].strip()
                        break
    if not key:
        print("Error: SMOOBU_API_KEY not set", file=sys.stderr)
        print("Add it to ~/.openclaw/secrets/smoobu.env", file=sys.stderr)
        sys.exit(1)
    return key

def api_request(method, endpoint, data=None):
    """Make API request to Smoobu."""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Api-Key": get_api_key(),
        "Content-Type": "application/json",
    }
    
    body = json.dumps(data).encode() if data else None
    req = Request(url, data=body, headers=headers, method=method)
    
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        error_body = e.read().decode()
        try:
            error = json.loads(error_body)
        except:
            error = {"error": error_body}
        print(f"API Error ({e.code}): {json.dumps(error, indent=2)}", file=sys.stderr)
        sys.exit(1)

def cmd_me(args):
    """Get user profile."""
    result = api_request("GET", "/api/me")
    print(json.dumps(result, indent=2))

def cmd_apartments(args):
    """List all apartments."""
    result = api_request("GET", "/api/apartments")
    print(json.dumps(result, indent=2))

def cmd_bookings(args):
    """List bookings with optional filters."""
    params = []
    if args.from_date:
        params.append(f"from={args.from_date}")
    if args.to_date:
        params.append(f"to={args.to_date}")
    if args.apartment:
        params.append(f"apartmentId={args.apartment}")
    
    endpoint = "/api/reservations"
    if params:
        endpoint += "?" + "&".join(params)
    
    result = api_request("GET", endpoint)
    print(json.dumps(result, indent=2))

def cmd_availability(args):
    """Check availability for date range."""
    # First get apartments if none specified
    if not args.apartments:
        apts = api_request("GET", "/api/apartments")
        apartment_ids = [a["id"] for a in apts.get("apartments", [])]
    else:
        apartment_ids = [int(x) for x in args.apartments.split(",")]
    
    data = {
        "arrivalDate": args.arrival,
        "departureDate": args.departure,
        "apartments": apartment_ids,
    }
    if args.guests:
        data["guests"] = args.guests
    
    result = api_request("POST", "/booking/checkApartmentAvailability", data)
    print(json.dumps(result, indent=2))

def cmd_create(args):
    """Create a booking."""
    data = {
        "arrivalDate": args.arrival,
        "departureDate": args.departure,
        "apartmentId": args.apartment,
        "channelId": args.channel or 70,  # 70 = manual/API
    }
    if args.first_name:
        data["firstName"] = args.first_name
    if args.last_name:
        data["lastName"] = args.last_name
    if args.email:
        data["email"] = args.email
    if args.phone:
        data["phone"] = args.phone
    if args.adults:
        data["adults"] = args.adults
    if args.price:
        data["price"] = args.price
    if args.notice:
        data["notice"] = args.notice
    
    result = api_request("POST", "/api/reservations", data)
    print(json.dumps(result, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Smoobu API helper")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # me
    subparsers.add_parser("me", help="Get user profile")
    
    # apartments
    subparsers.add_parser("apartments", help="List apartments")
    
    # bookings
    p = subparsers.add_parser("bookings", help="List bookings")
    p.add_argument("--from", dest="from_date", help="Start date (YYYY-MM-DD)")
    p.add_argument("--to", dest="to_date", help="End date (YYYY-MM-DD)")
    p.add_argument("--apartment", type=int, help="Filter by apartment ID")
    
    # availability
    p = subparsers.add_parser("availability", help="Check availability")
    p.add_argument("--arrival", required=True, help="Arrival date (YYYY-MM-DD)")
    p.add_argument("--departure", required=True, help="Departure date (YYYY-MM-DD)")
    p.add_argument("--apartments", help="Comma-separated apartment IDs (default: all)")
    p.add_argument("--guests", type=int, help="Number of guests")
    
    # create
    p = subparsers.add_parser("create", help="Create booking")
    p.add_argument("--arrival", required=True, help="Arrival date (YYYY-MM-DD)")
    p.add_argument("--departure", required=True, help="Departure date (YYYY-MM-DD)")
    p.add_argument("--apartment", type=int, required=True, help="Apartment ID")
    p.add_argument("--channel", type=int, help="Channel ID (default: 70)")
    p.add_argument("--first-name", help="Guest first name")
    p.add_argument("--last-name", help="Guest last name")
    p.add_argument("--email", help="Guest email")
    p.add_argument("--phone", help="Guest phone")
    p.add_argument("--adults", type=int, help="Number of adults")
    p.add_argument("--price", type=float, help="Total price")
    p.add_argument("--notice", help="Notes")
    
    args = parser.parse_args()
    
    commands = {
        "me": cmd_me,
        "apartments": cmd_apartments,
        "bookings": cmd_bookings,
        "availability": cmd_availability,
        "create": cmd_create,
    }
    
    commands[args.command](args)

if __name__ == "__main__":
    main()
