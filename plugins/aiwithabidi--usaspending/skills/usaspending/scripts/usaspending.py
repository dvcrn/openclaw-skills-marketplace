#!/usr/bin/env python3
"""USAspending CLI — USAspending.gov — federal spending data, contracts, grants, awards, agencies, and recipient search. No API key required.

Zero dependencies beyond Python stdlib.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "https://api.usaspending.gov/api/v2"


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
    headers = {}
    url = f"{base}{path}"
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v}, doseq=True)
        url = f"{url}{'&' if '?' in url else '?'}{qs}"
    return req(method, url, data=data, headers=headers)


def out(data):
    print(json.dumps(data, indent=2, default=str))


def cmd_search_awards(args):
    """Search federal awards"""
    path = "/search/spending_by_award/"
    data = {}
    if args.keywords:
        data["keywords"] = args.keywords
    if args.award_type:
        data["award-type"] = args.award_type
    if args.limit:
        data["limit"] = args.limit
    if args.page:
        data["page"] = args.page
    result = api("POST", path, data=data)
    out(result)

def cmd_get_award(args):
    """Get award details"""
    path = "/awards/{id}/"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_search_recipients(args):
    """Search recipients"""
    path = "/recipient/"
    data = {}
    if args.keyword:
        data["keyword"] = args.keyword
    if args.limit:
        data["limit"] = args.limit
    result = api("POST", path, data=data)
    out(result)

def cmd_get_recipient(args):
    """Get recipient details"""
    path = "/recipient/{id}/"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_list_agencies(args):
    """List top-tier agencies"""
    path = "/references/toptier_agencies/"
    result = api("GET", path)
    out(result)

def cmd_get_agency(args):
    """Get agency details"""
    path = "/agency/{code}/"
    path = path.replace("{code}", str(args.code or ""))
    result = api("GET", path)
    out(result)

def cmd_spending_by_category(args):
    """Spending by category"""
    path = "/search/spending_by_category/"
    data = {}
    if args.category:
        data["category"] = args.category
    if args.filters:
        data["filters"] = args.filters
    result = api("POST", path, data=data)
    out(result)

def cmd_spending_over_time(args):
    """Spending over time"""
    path = "/search/spending_over_time/"
    data = {}
    if args.group:
        data["group"] = args.group
    if args.filters:
        data["filters"] = args.filters
    result = api("POST", path, data=data)
    out(result)

def cmd_list_cfda(args):
    """List CFDA programs"""
    path = "/references/cfda/totals/"
    result = api("GET", path)
    out(result)

def cmd_autocomplete(args):
    """Autocomplete search"""
    path = "/autocomplete/awarding_agency/"
    data = {}
    if args.search_text:
        data["search-text"] = args.search_text
    result = api("POST", path, data=data)
    out(result)


def main():
    parser = argparse.ArgumentParser(description="USAspending CLI")
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    p_search_awards = sub.add_parser("search-awards", help="Search federal awards")
    p_search_awards.add_argument("--keywords", required=True)
    p_search_awards.add_argument("--award-type", default="contracts")
    p_search_awards.add_argument("--limit", default="25")
    p_search_awards.add_argument("--page", default="1")
    p_search_awards.set_defaults(func=cmd_search_awards)

    p_get_award = sub.add_parser("get-award", help="Get award details")
    p_get_award.add_argument("id")
    p_get_award.set_defaults(func=cmd_get_award)

    p_search_recipients = sub.add_parser("search-recipients", help="Search recipients")
    p_search_recipients.add_argument("--keyword", required=True)
    p_search_recipients.add_argument("--limit", default="25")
    p_search_recipients.set_defaults(func=cmd_search_recipients)

    p_get_recipient = sub.add_parser("get-recipient", help="Get recipient details")
    p_get_recipient.add_argument("id")
    p_get_recipient.set_defaults(func=cmd_get_recipient)

    p_list_agencies = sub.add_parser("list-agencies", help="List top-tier agencies")
    p_list_agencies.set_defaults(func=cmd_list_agencies)

    p_get_agency = sub.add_parser("get-agency", help="Get agency details")
    p_get_agency.add_argument("--code", required=True)
    p_get_agency.set_defaults(func=cmd_get_agency)

    p_spending_by_category = sub.add_parser("spending-by-category", help="Spending by category")
    p_spending_by_category.add_argument("--category", default="awarding_agency")
    p_spending_by_category.add_argument("--filters", default="JSON")
    p_spending_by_category.set_defaults(func=cmd_spending_by_category)

    p_spending_over_time = sub.add_parser("spending-over-time", help="Spending over time")
    p_spending_over_time.add_argument("--group", default="fiscal_year")
    p_spending_over_time.add_argument("--filters", default="JSON")
    p_spending_over_time.set_defaults(func=cmd_spending_over_time)

    p_list_cfda = sub.add_parser("list-cfda", help="List CFDA programs")
    p_list_cfda.set_defaults(func=cmd_list_cfda)

    p_autocomplete = sub.add_parser("autocomplete", help="Autocomplete search")
    p_autocomplete.add_argument("--search-text", required=True)
    p_autocomplete.set_defaults(func=cmd_autocomplete)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
