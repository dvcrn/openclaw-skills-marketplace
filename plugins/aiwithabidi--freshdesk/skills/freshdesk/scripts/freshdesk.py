#!/usr/bin/env python3
"""Freshdesk CLI — Freshdesk helpdesk — manage tickets, contacts, companies, and agents via REST API

Zero dependencies beyond Python stdlib.
Built by M. Abidi | agxntsix.ai
"""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

API_BASE = "https://{domain}/api/v2"

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
    key = get_env("FRESHDESK_API_KEY")
    secret = get_env("FRESHDESK_DOMAIN") if "FRESHDESK_DOMAIN" else ""
    creds = base64.b64encode(f"{key}:{secret}".encode()).decode()
    return {"Authorization": f"Basic {creds}", "Content-Type": "application/json", "Accept": "application/json"}



def get_api_base():
    base = API_BASE
    base = base.replace("{domain}", get_env("FRESHDESK_DOMAIN"))
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


def cmd_tickets(args):
    """List tickets."""
    path = "/tickets"
    params = {}
    if getattr(args, "filter", None): params["filter"] = args.filter
    if getattr(args, "email", None): params["email"] = args.email
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_ticket_get(args):
    """Get ticket."""
    path = f"/tickets/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_ticket_create(args):
    """Create ticket."""
    path = "/tickets"
    body = {}
    if getattr(args, "subject", None): body["subject"] = try_json(args.subject)
    if getattr(args, "description", None): body["description"] = try_json(args.description)
    if getattr(args, "email", None): body["email"] = try_json(args.email)
    if getattr(args, "priority", None): body["priority"] = try_json(args.priority)
    if getattr(args, "status", None): body["status"] = try_json(args.status)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_ticket_update(args):
    """Update ticket."""
    path = f"/tickets/{args.id}"
    body = {}
    if getattr(args, "status", None): body["status"] = try_json(args.status)
    if getattr(args, "priority", None): body["priority"] = try_json(args.priority)
    data = req("PUT", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_ticket_delete(args):
    """Delete ticket."""
    path = f"/tickets/{args.id}"
    data = req("DELETE", path)
    out(data, getattr(args, "human", False))

def cmd_ticket_reply(args):
    """Reply to ticket."""
    path = f"/tickets/{args.id}/reply"
    body = {}
    if getattr(args, "body", None): body["body"] = try_json(args.body)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_ticket_note(args):
    """Add note."""
    path = f"/tickets/{args.id}/notes"
    body = {}
    if getattr(args, "body", None): body["body"] = try_json(args.body)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_conversations(args):
    """List conversations."""
    path = f"/tickets/{args.id}/conversations"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_contacts(args):
    """List contacts."""
    path = "/contacts"
    params = {}
    if getattr(args, "email", None): params["email"] = args.email
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_contact_get(args):
    """Get contact."""
    path = f"/contacts/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_contact_create(args):
    """Create contact."""
    path = "/contacts"
    body = {}
    if getattr(args, "name", None): body["name"] = try_json(args.name)
    if getattr(args, "email", None): body["email"] = try_json(args.email)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_companies(args):
    """List companies."""
    path = "/companies"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_agents(args):
    """List agents."""
    path = "/agents"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_groups(args):
    """List groups."""
    path = "/groups"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_roles(args):
    """List roles."""
    path = "/roles"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_products(args):
    """List products."""
    path = "/products"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_satisfaction_ratings(args):
    """List CSAT."""
    path = "/surveys/satisfaction_ratings"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_time_entries(args):
    """Ticket time entries."""
    path = f"/tickets/{args.id}/time_entries"
    data = req("GET", path)
    out(data, getattr(args, "human", False))



def main():
    parser = argparse.ArgumentParser(description="Freshdesk CLI")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    sub = parser.add_subparsers(dest="command")

    tickets_p = sub.add_parser("tickets", help="List tickets")
    tickets_p.add_argument("--filter", help="Filter", default=None)
    tickets_p.add_argument("--email", help="Requester email", default=None)
    tickets_p.set_defaults(func=cmd_tickets)

    ticket_get_p = sub.add_parser("ticket-get", help="Get ticket")
    ticket_get_p.add_argument("id", help="Ticket ID")
    ticket_get_p.set_defaults(func=cmd_ticket_get)

    ticket_create_p = sub.add_parser("ticket-create", help="Create ticket")
    ticket_create_p.add_argument("--subject", help="Subject", default=None)
    ticket_create_p.add_argument("--description", help="Description", default=None)
    ticket_create_p.add_argument("--email", help="Email", default=None)
    ticket_create_p.add_argument("--priority", help="1-4", default=None)
    ticket_create_p.add_argument("--status", help="2-5", default=None)
    ticket_create_p.set_defaults(func=cmd_ticket_create)

    ticket_update_p = sub.add_parser("ticket-update", help="Update ticket")
    ticket_update_p.add_argument("id", help="ID")
    ticket_update_p.add_argument("--status", help="Status", default=None)
    ticket_update_p.add_argument("--priority", help="Priority", default=None)
    ticket_update_p.set_defaults(func=cmd_ticket_update)

    ticket_delete_p = sub.add_parser("ticket-delete", help="Delete ticket")
    ticket_delete_p.add_argument("id", help="ID")
    ticket_delete_p.set_defaults(func=cmd_ticket_delete)

    ticket_reply_p = sub.add_parser("ticket-reply", help="Reply to ticket")
    ticket_reply_p.add_argument("id", help="ID")
    ticket_reply_p.add_argument("--body", help="Reply body", default=None)
    ticket_reply_p.set_defaults(func=cmd_ticket_reply)

    ticket_note_p = sub.add_parser("ticket-note", help="Add note")
    ticket_note_p.add_argument("id", help="ID")
    ticket_note_p.add_argument("--body", help="Note body", default=None)
    ticket_note_p.set_defaults(func=cmd_ticket_note)

    conversations_p = sub.add_parser("conversations", help="List conversations")
    conversations_p.add_argument("id", help="Ticket ID")
    conversations_p.set_defaults(func=cmd_conversations)

    contacts_p = sub.add_parser("contacts", help="List contacts")
    contacts_p.add_argument("--email", help="Email", default=None)
    contacts_p.set_defaults(func=cmd_contacts)

    contact_get_p = sub.add_parser("contact-get", help="Get contact")
    contact_get_p.add_argument("id", help="Contact ID")
    contact_get_p.set_defaults(func=cmd_contact_get)

    contact_create_p = sub.add_parser("contact-create", help="Create contact")
    contact_create_p.add_argument("--name", help="Name", default=None)
    contact_create_p.add_argument("--email", help="Email", default=None)
    contact_create_p.set_defaults(func=cmd_contact_create)

    companies_p = sub.add_parser("companies", help="List companies")
    companies_p.set_defaults(func=cmd_companies)

    agents_p = sub.add_parser("agents", help="List agents")
    agents_p.set_defaults(func=cmd_agents)

    groups_p = sub.add_parser("groups", help="List groups")
    groups_p.set_defaults(func=cmd_groups)

    roles_p = sub.add_parser("roles", help="List roles")
    roles_p.set_defaults(func=cmd_roles)

    products_p = sub.add_parser("products", help="List products")
    products_p.set_defaults(func=cmd_products)

    satisfaction_ratings_p = sub.add_parser("satisfaction-ratings", help="List CSAT")
    satisfaction_ratings_p.set_defaults(func=cmd_satisfaction_ratings)

    time_entries_p = sub.add_parser("time-entries", help="Ticket time entries")
    time_entries_p.add_argument("id", help="Ticket ID")
    time_entries_p.set_defaults(func=cmd_time_entries)


    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
