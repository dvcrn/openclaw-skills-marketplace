#!/usr/bin/env python3
"""PagerDuty CLI — PagerDuty incident management — manage incidents, services, schedules, escalation policies, and on-call via REST API

Zero dependencies beyond Python stdlib.
Built by M. Abidi | agxntsix.ai
"""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

API_BASE = "https://api.pagerduty.com"

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
    token = get_env("PAGERDUTY_API_KEY")
    return {"Authorization": f"Token token={token}", "Content-Type": "application/json", "Accept": "application/json"}



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


def cmd_incidents(args):
    """List incidents."""
    path = "/incidents"
    params = {}
    if getattr(args, "statuses[]", None): params["statuses[]"] = getattr(args, "statuses_", None)
    if getattr(args, "since", None): params["since"] = args.since
    if getattr(args, "until", None): params["until"] = args.until
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_incident_get(args):
    """Get incident."""
    path = f"/incidents/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_incident_create(args):
    """Create incident."""
    path = "/incidents"
    body = {}
    if getattr(args, "title", None): body["title"] = try_json(args.title)
    if getattr(args, "service_id", None): body["service_id"] = try_json(args.service_id)
    if getattr(args, "urgency", None): body["urgency"] = try_json(args.urgency)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_incident_update(args):
    """Update incident."""
    path = f"/incidents/{args.id}"
    body = {}
    if getattr(args, "status", None): body["status"] = try_json(args.status)
    data = req("PUT", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_incident_notes(args):
    """List incident notes."""
    path = f"/incidents/{args.id}/notes"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_incident_note_add(args):
    """Add note."""
    path = f"/incidents/{args.id}/notes"
    body = {}
    if getattr(args, "content", None): body["content"] = try_json(args.content)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_services(args):
    """List services."""
    path = "/services"
    params = {}
    if getattr(args, "query", None): params["query"] = args.query
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_service_get(args):
    """Get service."""
    path = f"/services/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_service_create(args):
    """Create service."""
    path = "/services"
    body = {}
    if getattr(args, "name", None): body["name"] = try_json(args.name)
    if getattr(args, "escalation_policy_id", None): body["escalation_policy_id"] = try_json(args.escalation_policy_id)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_oncalls(args):
    """List on-calls."""
    path = "/oncalls"
    params = {}
    if getattr(args, "schedule_ids[]", None): params["schedule_ids[]"] = getattr(args, "schedule_ids_", None)
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_schedules(args):
    """List schedules."""
    path = "/schedules"
    params = {}
    if getattr(args, "query", None): params["query"] = args.query
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_schedule_get(args):
    """Get schedule."""
    path = f"/schedules/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_escalation_policies(args):
    """List escalation policies."""
    path = "/escalation_policies"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_users(args):
    """List users."""
    path = "/users"
    params = {}
    if getattr(args, "query", None): params["query"] = args.query
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_user_get(args):
    """Get user."""
    path = f"/users/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_teams(args):
    """List teams."""
    path = "/teams"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_vendors(args):
    """List vendors."""
    path = "/vendors"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_notifications(args):
    """List notifications."""
    path = "/notifications"
    params = {}
    if getattr(args, "since", None): params["since"] = args.since
    if getattr(args, "until", None): params["until"] = args.until
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_abilities(args):
    """List abilities."""
    path = "/abilities"
    data = req("GET", path)
    out(data, getattr(args, "human", False))



def main():
    parser = argparse.ArgumentParser(description="PagerDuty CLI")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    sub = parser.add_subparsers(dest="command")

    incidents_p = sub.add_parser("incidents", help="List incidents")
    incidents_p.add_argument("--statuses", dest="statuses_", help="Status filter", default=None)
    incidents_p.add_argument("--since", help="Since ISO", default=None)
    incidents_p.add_argument("--until", help="Until ISO", default=None)
    incidents_p.set_defaults(func=cmd_incidents)

    incident_get_p = sub.add_parser("incident-get", help="Get incident")
    incident_get_p.add_argument("id", help="Incident ID")
    incident_get_p.set_defaults(func=cmd_incident_get)

    incident_create_p = sub.add_parser("incident-create", help="Create incident")
    incident_create_p.add_argument("--title", help="Title", default=None)
    incident_create_p.add_argument("--service_id", help="Service ID", default=None)
    incident_create_p.add_argument("--urgency", help="high/low", default=None)
    incident_create_p.set_defaults(func=cmd_incident_create)

    incident_update_p = sub.add_parser("incident-update", help="Update incident")
    incident_update_p.add_argument("id", help="ID")
    incident_update_p.add_argument("--status", help="Status", default=None)
    incident_update_p.set_defaults(func=cmd_incident_update)

    incident_notes_p = sub.add_parser("incident-notes", help="List incident notes")
    incident_notes_p.add_argument("id", help="ID")
    incident_notes_p.set_defaults(func=cmd_incident_notes)

    incident_note_add_p = sub.add_parser("incident-note-add", help="Add note")
    incident_note_add_p.add_argument("id", help="ID")
    incident_note_add_p.add_argument("--content", help="Note content", default=None)
    incident_note_add_p.set_defaults(func=cmd_incident_note_add)

    services_p = sub.add_parser("services", help="List services")
    services_p.add_argument("--query", help="Search", default=None)
    services_p.set_defaults(func=cmd_services)

    service_get_p = sub.add_parser("service-get", help="Get service")
    service_get_p.add_argument("id", help="Service ID")
    service_get_p.set_defaults(func=cmd_service_get)

    service_create_p = sub.add_parser("service-create", help="Create service")
    service_create_p.add_argument("--name", help="Name", default=None)
    service_create_p.add_argument("--escalation_policy_id", help="Policy ID", default=None)
    service_create_p.set_defaults(func=cmd_service_create)

    oncalls_p = sub.add_parser("oncalls", help="List on-calls")
    oncalls_p.add_argument("--schedule_ids", dest="schedule_ids_", help="Schedule IDs", default=None)
    oncalls_p.set_defaults(func=cmd_oncalls)

    schedules_p = sub.add_parser("schedules", help="List schedules")
    schedules_p.add_argument("--query", help="Search", default=None)
    schedules_p.set_defaults(func=cmd_schedules)

    schedule_get_p = sub.add_parser("schedule-get", help="Get schedule")
    schedule_get_p.add_argument("id", help="Schedule ID")
    schedule_get_p.set_defaults(func=cmd_schedule_get)

    escalation_policies_p = sub.add_parser("escalation-policies", help="List escalation policies")
    escalation_policies_p.set_defaults(func=cmd_escalation_policies)

    users_p = sub.add_parser("users", help="List users")
    users_p.add_argument("--query", help="Search", default=None)
    users_p.set_defaults(func=cmd_users)

    user_get_p = sub.add_parser("user-get", help="Get user")
    user_get_p.add_argument("id", help="User ID")
    user_get_p.set_defaults(func=cmd_user_get)

    teams_p = sub.add_parser("teams", help="List teams")
    teams_p.set_defaults(func=cmd_teams)

    vendors_p = sub.add_parser("vendors", help="List vendors")
    vendors_p.set_defaults(func=cmd_vendors)

    notifications_p = sub.add_parser("notifications", help="List notifications")
    notifications_p.add_argument("--since", help="Since", default=None)
    notifications_p.add_argument("--until", help="Until", default=None)
    notifications_p.set_defaults(func=cmd_notifications)

    abilities_p = sub.add_parser("abilities", help="List abilities")
    abilities_p.set_defaults(func=cmd_abilities)


    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
