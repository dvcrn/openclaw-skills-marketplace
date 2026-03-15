#!/usr/bin/env python3
"""Hunter.io CLI — Hunter.io — email finder, email verifier, domain search, author finder, and lead management.

Zero dependencies beyond Python stdlib.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "https://api.hunter.io/v2"


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
    api_key = get_env("HUNTER_API_KEY")
    if not api_key:
        print("Error: HUNTER_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    headers = {}
    if params is None:
        params = {}
    params["api_key"] = api_key
    url = f"{base}{path}"
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v}, doseq=True)
        url = f"{url}{'&' if '?' in url else '?'}{qs}"
    return req(method, url, data=data, headers=headers)


def out(data):
    print(json.dumps(data, indent=2, default=str))


def cmd_domain_search(args):
    """Find emails for a domain"""
    path = "/domain-search?domain={domain}&api_key={api_key}"
    path = path.replace("{domain}", str(args.domain or ""))
    params = {}
    if args.limit:
        params["limit"] = args.limit
    if args.type:
        params["type"] = args.type
    result = api("GET", path, params=params)
    out(result)

def cmd_email_finder(args):
    """Find specific person's email"""
    path = "/email-finder?domain={domain}&first_name={first_name}&last_name={last_name}&api_key={api_key}"
    path = path.replace("{domain}", str(args.domain or ""))
    path = path.replace("{first-name}", str(args.first_name or ""))
    path = path.replace("{last-name}", str(args.last_name or ""))
    params = {}
    if args.first_name:
        params["first-name"] = args.first_name
    if args.last_name:
        params["last-name"] = args.last_name
    result = api("GET", path, params=params)
    out(result)

def cmd_email_verifier(args):
    """Verify an email address"""
    path = "/email-verifier?email={email}&api_key={api_key}"
    path = path.replace("{email}", str(args.email or ""))
    result = api("GET", path)
    out(result)

def cmd_email_count(args):
    """Count emails for domain"""
    path = "/email-count?domain={domain}"
    path = path.replace("{domain}", str(args.domain or ""))
    result = api("GET", path)
    out(result)

def cmd_list_leads(args):
    """List saved leads"""
    path = "/leads?api_key={api_key}&limit={limit}&offset={offset}"
    path = path.replace("{limit}", str(args.limit or ""))
    path = path.replace("{offset}", str(args.offset or ""))
    result = api("GET", path)
    out(result)

def cmd_create_lead(args):
    """Create a lead"""
    path = "/leads?api_key={api_key}"
    data = {}
    if args.email:
        data["email"] = args.email
    if args.first_name:
        data["first-name"] = args.first_name
    if args.last_name:
        data["last-name"] = args.last_name
    if args.company:
        data["company"] = args.company
    result = api("POST", path, data=data)
    out(result)

def cmd_update_lead(args):
    """Update a lead"""
    path = "/leads/{id}?api_key={api_key}"
    path = path.replace("{id}", str(args.id))
    data = {}
    if args.email:
        data["email"] = args.email
    if args.first_name:
        data["first-name"] = args.first_name
    if args.last_name:
        data["last-name"] = args.last_name
    result = api("PUT", path, data=data)
    out(result)

def cmd_delete_lead(args):
    """Delete a lead"""
    path = "/leads/{id}?api_key={api_key}"
    path = path.replace("{id}", str(args.id))
    result = api("DELETE", path)
    out(result)

def cmd_list_leads_lists(args):
    """List lead lists"""
    path = "/leads_lists?api_key={api_key}"
    result = api("GET", path)
    out(result)

def cmd_get_account(args):
    """Get account info & usage"""
    path = "/account?api_key={api_key}"
    result = api("GET", path)
    out(result)

def cmd_author_finder(args):
    """Find author of article"""
    path = "/author-finder?url={url}&api_key={api_key}"
    path = path.replace("{url}", str(args.url or ""))
    result = api("GET", path)
    out(result)


def main():
    parser = argparse.ArgumentParser(description="Hunter.io CLI")
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    p_domain_search = sub.add_parser("domain-search", help="Find emails for a domain")
    p_domain_search.add_argument("--domain", required=True)
    p_domain_search.add_argument("--limit", default="10")
    p_domain_search.add_argument("--type", required=True)
    p_domain_search.set_defaults(func=cmd_domain_search)

    p_email_finder = sub.add_parser("email-finder", help="Find specific person's email")
    p_email_finder.add_argument("--domain", required=True)
    p_email_finder.add_argument("--first-name", required=True)
    p_email_finder.add_argument("--last-name", required=True)
    p_email_finder.set_defaults(func=cmd_email_finder)

    p_email_verifier = sub.add_parser("email-verifier", help="Verify an email address")
    p_email_verifier.add_argument("--email", required=True)
    p_email_verifier.set_defaults(func=cmd_email_verifier)

    p_email_count = sub.add_parser("email-count", help="Count emails for domain")
    p_email_count.add_argument("--domain", required=True)
    p_email_count.set_defaults(func=cmd_email_count)

    p_list_leads = sub.add_parser("list-leads", help="List saved leads")
    p_list_leads.add_argument("--limit", default="20")
    p_list_leads.add_argument("--offset", default="0")
    p_list_leads.set_defaults(func=cmd_list_leads)

    p_create_lead = sub.add_parser("create-lead", help="Create a lead")
    p_create_lead.add_argument("--email", required=True)
    p_create_lead.add_argument("--first-name", required=True)
    p_create_lead.add_argument("--last-name", required=True)
    p_create_lead.add_argument("--company", required=True)
    p_create_lead.set_defaults(func=cmd_create_lead)

    p_update_lead = sub.add_parser("update-lead", help="Update a lead")
    p_update_lead.add_argument("id")
    p_update_lead.add_argument("--email", required=True)
    p_update_lead.add_argument("--first-name", required=True)
    p_update_lead.add_argument("--last-name", required=True)
    p_update_lead.set_defaults(func=cmd_update_lead)

    p_delete_lead = sub.add_parser("delete-lead", help="Delete a lead")
    p_delete_lead.add_argument("id")
    p_delete_lead.set_defaults(func=cmd_delete_lead)

    p_list_leads_lists = sub.add_parser("list-leads-lists", help="List lead lists")
    p_list_leads_lists.set_defaults(func=cmd_list_leads_lists)

    p_get_account = sub.add_parser("get-account", help="Get account info & usage")
    p_get_account.set_defaults(func=cmd_get_account)

    p_author_finder = sub.add_parser("author-finder", help="Find author of article")
    p_author_finder.add_argument("--url", required=True)
    p_author_finder.set_defaults(func=cmd_author_finder)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
