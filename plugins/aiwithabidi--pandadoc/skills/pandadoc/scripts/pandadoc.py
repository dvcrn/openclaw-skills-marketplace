#!/usr/bin/env python3
"""PandaDoc CLI — PandaDoc — manage documents, templates, contacts, and e-signatures via REST API

Zero dependencies beyond Python stdlib.
Built by M. Abidi | agxntsix.ai
"""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

API_BASE = "https://api.pandadoc.com/public/v1"

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
    token = get_env("PANDADOC_API_KEY")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}



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


def cmd_documents(args):
    """List documents."""
    path = "/documents"
    params = {}
    if getattr(args, "status", None): params["status"] = args.status
    if getattr(args, "q", None): params["q"] = args.q
    if getattr(args, "tag", None): params["tag"] = args.tag
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_document_get(args):
    """Get document details."""
    path = f"/documents/{args.id}/details"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_document_create(args):
    """Create document."""
    path = "/documents"
    body = {}
    if getattr(args, "name", None): body["name"] = try_json(args.name)
    if getattr(args, "template_uuid", None): body["template_uuid"] = try_json(args.template_uuid)
    if getattr(args, "recipients", None): body["recipients"] = try_json(args.recipients)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_document_send(args):
    """Send document."""
    path = f"/documents/{args.id}/send"
    body = {}
    if getattr(args, "message", None): body["message"] = try_json(args.message)
    if getattr(args, "subject", None): body["subject"] = try_json(args.subject)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_document_status(args):
    """Get status."""
    path = f"/documents/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_document_delete(args):
    """Delete document."""
    path = f"/documents/{args.id}"
    data = req("DELETE", path)
    out(data, getattr(args, "human", False))

def cmd_document_link(args):
    """Create sharing link."""
    path = f"/documents/{args.id}/session"
    body = {}
    if getattr(args, "recipient", None): body["recipient"] = try_json(args.recipient)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_templates(args):
    """List templates."""
    path = "/templates"
    params = {}
    if getattr(args, "q", None): params["q"] = args.q
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_template_get(args):
    """Get template."""
    path = f"/templates/{args.id}/details"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_contacts(args):
    """List contacts."""
    path = "/contacts"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_contact_create(args):
    """Create contact."""
    path = "/contacts"
    body = {}
    if getattr(args, "email", None): body["email"] = try_json(args.email)
    if getattr(args, "first_name", None): body["first_name"] = try_json(args.first_name)
    if getattr(args, "last_name", None): body["last_name"] = try_json(args.last_name)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_folders(args):
    """List folders."""
    path = "/documents/folders"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_webhooks(args):
    """List webhooks."""
    path = "/webhooks"
    data = req("GET", path)
    out(data, getattr(args, "human", False))



def main():
    parser = argparse.ArgumentParser(description="PandaDoc CLI")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    sub = parser.add_subparsers(dest="command")

    documents_p = sub.add_parser("documents", help="List documents")
    documents_p.add_argument("--status", help="Status filter", default=None)
    documents_p.add_argument("--q", help="Search", default=None)
    documents_p.add_argument("--tag", help="Tag filter", default=None)
    documents_p.set_defaults(func=cmd_documents)

    document_get_p = sub.add_parser("document-get", help="Get document details")
    document_get_p.add_argument("id", help="Document ID")
    document_get_p.set_defaults(func=cmd_document_get)

    document_create_p = sub.add_parser("document-create", help="Create document")
    document_create_p.add_argument("--name", help="Name", default=None)
    document_create_p.add_argument("--template_uuid", help="Template UUID", default=None)
    document_create_p.add_argument("--recipients", help="JSON recipients", default=None)
    document_create_p.set_defaults(func=cmd_document_create)

    document_send_p = sub.add_parser("document-send", help="Send document")
    document_send_p.add_argument("id", help="ID")
    document_send_p.add_argument("--message", help="Message", default=None)
    document_send_p.add_argument("--subject", help="Subject", default=None)
    document_send_p.set_defaults(func=cmd_document_send)

    document_status_p = sub.add_parser("document-status", help="Get status")
    document_status_p.add_argument("id", help="ID")
    document_status_p.set_defaults(func=cmd_document_status)

    document_delete_p = sub.add_parser("document-delete", help="Delete document")
    document_delete_p.add_argument("id", help="ID")
    document_delete_p.set_defaults(func=cmd_document_delete)

    document_link_p = sub.add_parser("document-link", help="Create sharing link")
    document_link_p.add_argument("id", help="ID")
    document_link_p.add_argument("--recipient", help="Recipient email", default=None)
    document_link_p.set_defaults(func=cmd_document_link)

    templates_p = sub.add_parser("templates", help="List templates")
    templates_p.add_argument("--q", help="Search", default=None)
    templates_p.set_defaults(func=cmd_templates)

    template_get_p = sub.add_parser("template-get", help="Get template")
    template_get_p.add_argument("id", help="Template ID")
    template_get_p.set_defaults(func=cmd_template_get)

    contacts_p = sub.add_parser("contacts", help="List contacts")
    contacts_p.set_defaults(func=cmd_contacts)

    contact_create_p = sub.add_parser("contact-create", help="Create contact")
    contact_create_p.add_argument("--email", help="Email", default=None)
    contact_create_p.add_argument("--first_name", help="First name", default=None)
    contact_create_p.add_argument("--last_name", help="Last name", default=None)
    contact_create_p.set_defaults(func=cmd_contact_create)

    folders_p = sub.add_parser("folders", help="List folders")
    folders_p.set_defaults(func=cmd_folders)

    webhooks_p = sub.add_parser("webhooks", help="List webhooks")
    webhooks_p.set_defaults(func=cmd_webhooks)


    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
