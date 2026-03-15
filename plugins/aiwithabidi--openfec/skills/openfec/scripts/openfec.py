#!/usr/bin/env python3
"""OpenFEC CLI — OpenFEC — campaign finance data, candidates, committees, filings, and contribution search.

Zero dependencies beyond Python stdlib.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "https://api.open.fec.gov/v1"


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
    api_key = get_env("FEC_API_KEY") or "DEMO_KEY"
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


def cmd_search_candidates(args):
    """Search candidates"""
    path = "/candidates/search/?api_key={api_key}"
    params = {}
    if args.q:
        params["q"] = args.q
    if args.office:
        params["office"] = args.office
    if args.state:
        params["state"] = args.state
    if args.party:
        params["party"] = args.party
    if args.cycle:
        params["cycle"] = args.cycle
    if args.per_page:
        params["per-page"] = args.per_page
    result = api("GET", path, params=params)
    out(result)

def cmd_get_candidate(args):
    """Get candidate details"""
    path = "/candidate/{id}/?api_key={api_key}"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_candidate_totals(args):
    """Get candidate financial totals"""
    path = "/candidate/{id}/totals/?api_key={api_key}"
    path = path.replace("{id}", str(args.id))
    params = {}
    if args.cycle:
        params["cycle"] = args.cycle
    result = api("GET", path, params=params)
    out(result)

def cmd_search_committees(args):
    """Search committees"""
    path = "/committees/?api_key={api_key}"
    params = {}
    if args.q:
        params["q"] = args.q
    if args.committee_type:
        params["committee-type"] = args.committee_type
    if args.per_page:
        params["per-page"] = args.per_page
    result = api("GET", path, params=params)
    out(result)

def cmd_get_committee(args):
    """Get committee details"""
    path = "/committee/{id}/?api_key={api_key}"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_list_filings(args):
    """List filings"""
    path = "/filings/?api_key={api_key}"
    params = {}
    if args.candidate_id:
        params["candidate-id"] = args.candidate_id
    if args.committee_id:
        params["committee-id"] = args.committee_id
    if args.per_page:
        params["per-page"] = args.per_page
    result = api("GET", path, params=params)
    out(result)

def cmd_search_contributions(args):
    """Search individual contributions"""
    path = "/schedules/schedule_a/?api_key={api_key}"
    params = {}
    if args.contributor_name:
        params["contributor-name"] = args.contributor_name
    if args.contributor_state:
        params["contributor-state"] = args.contributor_state
    if args.min_amount:
        params["min-amount"] = args.min_amount
    if args.max_amount:
        params["max-amount"] = args.max_amount
    if args.per_page:
        params["per-page"] = args.per_page
    result = api("GET", path, params=params)
    out(result)

def cmd_search_disbursements(args):
    """Search disbursements"""
    path = "/schedules/schedule_b/?api_key={api_key}"
    params = {}
    if args.committee_id:
        params["committee-id"] = args.committee_id
    if args.recipient_name:
        params["recipient-name"] = args.recipient_name
    if args.per_page:
        params["per-page"] = args.per_page
    result = api("GET", path, params=params)
    out(result)

def cmd_election_results(args):
    """Get election results"""
    path = "/elections/?api_key={api_key}"
    params = {}
    if args.office:
        params["office"] = args.office
    if args.cycle:
        params["cycle"] = args.cycle
    result = api("GET", path, params=params)
    out(result)

def cmd_get_totals(args):
    """Totals by entity type"""
    path = "/totals/by_entity/?api_key={api_key}"
    params = {}
    if args.cycle:
        params["cycle"] = args.cycle
    result = api("GET", path, params=params)
    out(result)


def main():
    parser = argparse.ArgumentParser(description="OpenFEC CLI")
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    p_search_candidates = sub.add_parser("search-candidates", help="Search candidates")
    p_search_candidates.add_argument("--q", required=True)
    p_search_candidates.add_argument("--office", required=True)
    p_search_candidates.add_argument("--state", required=True)
    p_search_candidates.add_argument("--party", required=True)
    p_search_candidates.add_argument("--cycle", required=True)
    p_search_candidates.add_argument("--per-page", default="20")
    p_search_candidates.set_defaults(func=cmd_search_candidates)

    p_get_candidate = sub.add_parser("get-candidate", help="Get candidate details")
    p_get_candidate.add_argument("id")
    p_get_candidate.set_defaults(func=cmd_get_candidate)

    p_candidate_totals = sub.add_parser("candidate-totals", help="Get candidate financial totals")
    p_candidate_totals.add_argument("id")
    p_candidate_totals.add_argument("--cycle", required=True)
    p_candidate_totals.set_defaults(func=cmd_candidate_totals)

    p_search_committees = sub.add_parser("search-committees", help="Search committees")
    p_search_committees.add_argument("--q", required=True)
    p_search_committees.add_argument("--committee-type", required=True)
    p_search_committees.add_argument("--per-page", default="20")
    p_search_committees.set_defaults(func=cmd_search_committees)

    p_get_committee = sub.add_parser("get-committee", help="Get committee details")
    p_get_committee.add_argument("id")
    p_get_committee.set_defaults(func=cmd_get_committee)

    p_list_filings = sub.add_parser("list-filings", help="List filings")
    p_list_filings.add_argument("--candidate-id", required=True)
    p_list_filings.add_argument("--committee-id", required=True)
    p_list_filings.add_argument("--per-page", default="20")
    p_list_filings.set_defaults(func=cmd_list_filings)

    p_search_contributions = sub.add_parser("search-contributions", help="Search individual contributions")
    p_search_contributions.add_argument("--contributor-name", required=True)
    p_search_contributions.add_argument("--contributor-state", required=True)
    p_search_contributions.add_argument("--min-amount", required=True)
    p_search_contributions.add_argument("--max-amount", required=True)
    p_search_contributions.add_argument("--per-page", default="20")
    p_search_contributions.set_defaults(func=cmd_search_contributions)

    p_search_disbursements = sub.add_parser("search-disbursements", help="Search disbursements")
    p_search_disbursements.add_argument("--committee-id", required=True)
    p_search_disbursements.add_argument("--recipient-name", required=True)
    p_search_disbursements.add_argument("--per-page", default="20")
    p_search_disbursements.set_defaults(func=cmd_search_disbursements)

    p_election_results = sub.add_parser("election-results", help="Get election results")
    p_election_results.add_argument("--office", default="president")
    p_election_results.add_argument("--cycle", required=True)
    p_election_results.set_defaults(func=cmd_election_results)

    p_get_totals = sub.add_parser("get-totals", help="Totals by entity type")
    p_get_totals.add_argument("--cycle", required=True)
    p_get_totals.set_defaults(func=cmd_get_totals)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
