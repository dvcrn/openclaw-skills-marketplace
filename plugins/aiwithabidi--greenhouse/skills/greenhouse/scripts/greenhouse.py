#!/usr/bin/env python3
"""Greenhouse CLI — Greenhouse ATS — manage candidates, jobs, applications, offers, and interviews via Harvest API

Zero dependencies beyond Python stdlib.
Built by M. Abidi | agxntsix.ai
"""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

API_BASE = "https://harvest.greenhouse.io/v1"

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
    if not val:
        print(f"Error: {name} not set", file=sys.stderr)
        sys.exit(1)
    return val


def get_headers():
    import base64
    key = get_env("GREENHOUSE_API_KEY")
    secret = get_env("") if "" else ""
    creds = base64.b64encode(f"{key}:{secret}".encode()).decode()
    return {"Authorization": f"Basic {creds}", "Content-Type": "application/json", "Accept": "application/json"}



def get_api_base():
    base = API_BASE
    pass
    return base

def req(method, path, data=None, params=None):
    headers = get_headers()
    if path.startswith("http"):
        url = path
    else:
        url = get_api_base() + path
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        if qs:
            url = f"{url}?{qs}" if "?" not in url else f"{url}&{qs}"
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, method=method)
    for k, v in headers.items():
        r.add_header(k, v)
    try:
        resp = urllib.request.urlopen(r, timeout=30)
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {"ok": True}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(json.dumps({"error": True, "code": e.code, "message": err_body}), file=sys.stderr)
        sys.exit(1)


def try_json(val):
    if val is None:
        return None
    try:
        return json.loads(val)
    except (json.JSONDecodeError, ValueError):
        return val


def out(data, human=False):
    if human and isinstance(data, dict):
        for k, v in data.items():
            print(f"  {k}: {v}")
    elif human and isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for k, v in item.items():
                    print(f"  {k}: {v}")
                print()
            else:
                print(item)
    else:
        print(json.dumps(data, indent=2, default=str))


def cmd_candidates(args):
    """List candidates."""
    path = "/candidates"
    params = {}
    if getattr(args, "per_page", None): params["per_page"] = args.per_page
    if getattr(args, "job_id", None): params["job_id"] = args.job_id
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_candidate_get(args):
    """Get candidate."""
    path = f"/candidates/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_candidate_create(args):
    """Create candidate."""
    path = "/candidates"
    body = {}
    if getattr(args, "first_name", None): body["first_name"] = try_json(args.first_name)
    if getattr(args, "last_name", None): body["last_name"] = try_json(args.last_name)
    if getattr(args, "email_addresses", None): body["email_addresses"] = try_json(args.email_addresses)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_applications(args):
    """List applications."""
    path = "/applications"
    params = {}
    if getattr(args, "status", None): params["status"] = args.status
    if getattr(args, "job_id", None): params["job_id"] = args.job_id
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_application_get(args):
    """Get application."""
    path = f"/applications/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_application_advance(args):
    """Advance application."""
    path = f"/applications/{args.id}/advance"
    data = req("POST", path)
    out(data, getattr(args, "human", False))

def cmd_application_reject(args):
    """Reject application."""
    path = f"/applications/{args.id}/reject"
    body = {}
    if getattr(args, "rejection_reason_id", None): body["rejection_reason_id"] = try_json(args.rejection_reason_id)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_jobs(args):
    """List jobs."""
    path = "/jobs"
    params = {}
    if getattr(args, "status", None): params["status"] = args.status
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_job_get(args):
    """Get job."""
    path = f"/jobs/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_job_stages(args):
    """List job stages."""
    path = f"/jobs/{args.id}/stages"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_offers(args):
    """List offers."""
    path = "/offers"
    params = {}
    if getattr(args, "status", None): params["status"] = args.status
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_interviews(args):
    """List interviews."""
    path = "/scheduled_interviews"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_scorecards(args):
    """List scorecards."""
    path = "/scorecards"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_departments(args):
    """List departments."""
    path = "/departments"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_offices(args):
    """List offices."""
    path = "/offices"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_users(args):
    """List users."""
    path = "/users"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_sources(args):
    """List sources."""
    path = "/sources"
    data = req("GET", path)
    out(data, getattr(args, "human", False))



def main():
    parser = argparse.ArgumentParser(description="Greenhouse CLI")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    sub = parser.add_subparsers(dest="command")

    candidates_p = sub.add_parser("candidates", help="List candidates")
    candidates_p.add_argument("--per_page", help="Per page", default=None)
    candidates_p.add_argument("--job_id", help="Job ID", default=None)
    candidates_p.set_defaults(func=cmd_candidates)

    candidate_get_p = sub.add_parser("candidate-get", help="Get candidate")
    candidate_get_p.add_argument("id", help="Candidate ID")
    candidate_get_p.set_defaults(func=cmd_candidate_get)

    candidate_create_p = sub.add_parser("candidate-create", help="Create candidate")
    candidate_create_p.add_argument("--first_name", help="First name", default=None)
    candidate_create_p.add_argument("--last_name", help="Last name", default=None)
    candidate_create_p.add_argument("--email_addresses", help="JSON emails", default=None)
    candidate_create_p.set_defaults(func=cmd_candidate_create)

    applications_p = sub.add_parser("applications", help="List applications")
    applications_p.add_argument("--status", help="active/rejected/hired", default=None)
    applications_p.add_argument("--job_id", help="Job ID", default=None)
    applications_p.set_defaults(func=cmd_applications)

    application_get_p = sub.add_parser("application-get", help="Get application")
    application_get_p.add_argument("id", help="Application ID")
    application_get_p.set_defaults(func=cmd_application_get)

    application_advance_p = sub.add_parser("application-advance", help="Advance application")
    application_advance_p.add_argument("id", help="Application ID")
    application_advance_p.set_defaults(func=cmd_application_advance)

    application_reject_p = sub.add_parser("application-reject", help="Reject application")
    application_reject_p.add_argument("id", help="ID")
    application_reject_p.add_argument("--rejection_reason_id", help="Reason ID", default=None)
    application_reject_p.set_defaults(func=cmd_application_reject)

    jobs_p = sub.add_parser("jobs", help="List jobs")
    jobs_p.add_argument("--status", help="open/closed/draft", default=None)
    jobs_p.set_defaults(func=cmd_jobs)

    job_get_p = sub.add_parser("job-get", help="Get job")
    job_get_p.add_argument("id", help="Job ID")
    job_get_p.set_defaults(func=cmd_job_get)

    job_stages_p = sub.add_parser("job-stages", help="List job stages")
    job_stages_p.add_argument("id", help="Job ID")
    job_stages_p.set_defaults(func=cmd_job_stages)

    offers_p = sub.add_parser("offers", help="List offers")
    offers_p.add_argument("--status", help="unresolved/accepted/rejected", default=None)
    offers_p.set_defaults(func=cmd_offers)

    interviews_p = sub.add_parser("interviews", help="List interviews")
    interviews_p.set_defaults(func=cmd_interviews)

    scorecards_p = sub.add_parser("scorecards", help="List scorecards")
    scorecards_p.set_defaults(func=cmd_scorecards)

    departments_p = sub.add_parser("departments", help="List departments")
    departments_p.set_defaults(func=cmd_departments)

    offices_p = sub.add_parser("offices", help="List offices")
    offices_p.set_defaults(func=cmd_offices)

    users_p = sub.add_parser("users", help="List users")
    users_p.set_defaults(func=cmd_users)

    sources_p = sub.add_parser("sources", help="List sources")
    sources_p.set_defaults(func=cmd_sources)


    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
