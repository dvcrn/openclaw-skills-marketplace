#!/usr/bin/env python3
"""DocuSign CLI — DocuSign e-signatures — manage envelopes, templates, recipients, and signing via REST API

Zero dependencies beyond Python stdlib.
Built by M. Abidi | agxntsix.ai
"""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

API_BASE = "https://demo.docusign.net/restapi/v2.1/accounts/{account_id}"

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
    token = get_env("DOCUSIGN_ACCESS_TOKEN")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}



def get_api_base():
    base = API_BASE
    base = base.replace("{account_id}", get_env("DOCUSIGN_ACCOUNT_ID"))
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


def cmd_envelopes(args):
    """List envelopes."""
    path = "/envelopes"
    params = {}
    if getattr(args, "from_date", None): params["from_date"] = args.from_date
    if getattr(args, "status", None): params["status"] = args.status
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_envelope_get(args):
    """Get envelope."""
    path = f"/envelopes/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_envelope_create(args):
    """Create envelope."""
    path = "/envelopes"
    body = {}
    if getattr(args, "subject", None): body["subject"] = try_json(args.subject)
    if getattr(args, "templateId", None): body["templateId"] = try_json(args.templateId)
    if getattr(args, "status", None): body["status"] = try_json(args.status)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_envelope_void(args):
    """Void envelope."""
    path = f"/envelopes/{args.id}"
    body = {}
    if getattr(args, "voidedReason", None): body["voidedReason"] = try_json(args.voidedReason)
    data = req("PUT", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_recipients(args):
    """List recipients."""
    path = f"/envelopes/{args.id}/recipients"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_documents(args):
    """List documents."""
    path = f"/envelopes/{args.id}/documents"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_templates(args):
    """List templates."""
    path = "/templates"
    params = {}
    if getattr(args, "search_text", None): params["search_text"] = args.search_text
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_template_get(args):
    """Get template."""
    path = f"/templates/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_audit_events(args):
    """Get audit events."""
    path = f"/envelopes/{args.id}/audit_events"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_folders(args):
    """List folders."""
    path = "/folders"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_users(args):
    """List users."""
    path = "/users"
    data = req("GET", path)
    out(data, getattr(args, "human", False))



def main():
    parser = argparse.ArgumentParser(description="DocuSign CLI")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    sub = parser.add_subparsers(dest="command")

    envelopes_p = sub.add_parser("envelopes", help="List envelopes")
    envelopes_p.add_argument("--from_date", help="From date ISO", default=None)
    envelopes_p.add_argument("--status", help="Status filter", default=None)
    envelopes_p.set_defaults(func=cmd_envelopes)

    envelope_get_p = sub.add_parser("envelope-get", help="Get envelope")
    envelope_get_p.add_argument("id", help="Envelope ID")
    envelope_get_p.set_defaults(func=cmd_envelope_get)

    envelope_create_p = sub.add_parser("envelope-create", help="Create envelope")
    envelope_create_p.add_argument("--subject", help="Subject", default=None)
    envelope_create_p.add_argument("--templateId", help="Template ID", default=None)
    envelope_create_p.add_argument("--status", help="created/sent", default=None)
    envelope_create_p.set_defaults(func=cmd_envelope_create)

    envelope_void_p = sub.add_parser("envelope-void", help="Void envelope")
    envelope_void_p.add_argument("id", help="ID")
    envelope_void_p.add_argument("--voidedReason", help="Reason", default=None)
    envelope_void_p.set_defaults(func=cmd_envelope_void)

    recipients_p = sub.add_parser("recipients", help="List recipients")
    recipients_p.add_argument("id", help="Envelope ID")
    recipients_p.set_defaults(func=cmd_recipients)

    documents_p = sub.add_parser("documents", help="List documents")
    documents_p.add_argument("id", help="Envelope ID")
    documents_p.set_defaults(func=cmd_documents)

    templates_p = sub.add_parser("templates", help="List templates")
    templates_p.add_argument("--search_text", help="Search", default=None)
    templates_p.set_defaults(func=cmd_templates)

    template_get_p = sub.add_parser("template-get", help="Get template")
    template_get_p.add_argument("id", help="Template ID")
    template_get_p.set_defaults(func=cmd_template_get)

    audit_events_p = sub.add_parser("audit-events", help="Get audit events")
    audit_events_p.add_argument("id", help="Envelope ID")
    audit_events_p.set_defaults(func=cmd_audit_events)

    folders_p = sub.add_parser("folders", help="List folders")
    folders_p.set_defaults(func=cmd_folders)

    users_p = sub.add_parser("users", help="List users")
    users_p.set_defaults(func=cmd_users)


    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
