#!/usr/bin/env python3
"""Gusto CLI — Gusto payroll & HR — manage employees, payroll, benefits, and tax forms via REST API

Zero dependencies beyond Python stdlib.
Built by M. Abidi | agxntsix.ai
"""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

API_BASE = "https://api.gusto.com/v1"

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
    token = get_env("GUSTO_ACCESS_TOKEN")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}



def get_api_base():
    base = API_BASE
    base = base; company_id = get_env("GUSTO_COMPANY_ID")
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


def cmd_company(args):
    """Get company info."""
    path = "/companies/{company_id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_locations(args):
    """List locations."""
    path = "/companies/{company_id}/locations"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_employees(args):
    """List employees."""
    path = "/companies/{company_id}/employees"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_employee_get(args):
    """Get employee."""
    path = f"/employees/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_employee_create(args):
    """Create employee."""
    path = "/companies/{company_id}/employees"
    body = {}
    if getattr(args, "first_name", None): body["first_name"] = try_json(args.first_name)
    if getattr(args, "last_name", None): body["last_name"] = try_json(args.last_name)
    if getattr(args, "email", None): body["email"] = try_json(args.email)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_payrolls(args):
    """List payrolls."""
    path = "/companies/{company_id}/payrolls"
    params = {}
    if getattr(args, "start_date", None): params["start_date"] = args.start_date
    if getattr(args, "end_date", None): params["end_date"] = args.end_date
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_payroll_get(args):
    """Get payroll."""
    path = f"/companies/{company_id}/payrolls/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_pay_schedules(args):
    """List pay schedules."""
    path = "/companies/{company_id}/pay_schedules"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_compensations(args):
    """List compensations."""
    path = f"/employees/{args.id}/compensations"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_benefits(args):
    """List benefits."""
    path = "/companies/{company_id}/company_benefits"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_employee_benefits(args):
    """List employee benefits."""
    path = f"/employees/{args.id}/employee_benefits"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_contractors(args):
    """List contractors."""
    path = "/companies/{company_id}/contractors"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_contractor_payments(args):
    """List contractor payments."""
    path = "/companies/{company_id}/contractor_payments"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_tax_forms(args):
    """List tax forms."""
    path = "/companies/{company_id}/tax_forms"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_garnishments(args):
    """List garnishments."""
    path = f"/employees/{args.id}/garnishments"
    data = req("GET", path)
    out(data, getattr(args, "human", False))



def main():
    parser = argparse.ArgumentParser(description="Gusto CLI")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    sub = parser.add_subparsers(dest="command")

    company_p = sub.add_parser("company", help="Get company info")
    company_p.set_defaults(func=cmd_company)

    locations_p = sub.add_parser("locations", help="List locations")
    locations_p.set_defaults(func=cmd_locations)

    employees_p = sub.add_parser("employees", help="List employees")
    employees_p.set_defaults(func=cmd_employees)

    employee_get_p = sub.add_parser("employee-get", help="Get employee")
    employee_get_p.add_argument("id", help="Employee ID")
    employee_get_p.set_defaults(func=cmd_employee_get)

    employee_create_p = sub.add_parser("employee-create", help="Create employee")
    employee_create_p.add_argument("--first_name", help="First name", default=None)
    employee_create_p.add_argument("--last_name", help="Last name", default=None)
    employee_create_p.add_argument("--email", help="Email", default=None)
    employee_create_p.set_defaults(func=cmd_employee_create)

    payrolls_p = sub.add_parser("payrolls", help="List payrolls")
    payrolls_p.add_argument("--start_date", help="Start", default=None)
    payrolls_p.add_argument("--end_date", help="End", default=None)
    payrolls_p.set_defaults(func=cmd_payrolls)

    payroll_get_p = sub.add_parser("payroll-get", help="Get payroll")
    payroll_get_p.add_argument("id", help="Payroll ID")
    payroll_get_p.set_defaults(func=cmd_payroll_get)

    pay_schedules_p = sub.add_parser("pay-schedules", help="List pay schedules")
    pay_schedules_p.set_defaults(func=cmd_pay_schedules)

    compensations_p = sub.add_parser("compensations", help="List compensations")
    compensations_p.add_argument("id", help="Employee ID")
    compensations_p.set_defaults(func=cmd_compensations)

    benefits_p = sub.add_parser("benefits", help="List benefits")
    benefits_p.set_defaults(func=cmd_benefits)

    employee_benefits_p = sub.add_parser("employee-benefits", help="List employee benefits")
    employee_benefits_p.add_argument("id", help="Employee ID")
    employee_benefits_p.set_defaults(func=cmd_employee_benefits)

    contractors_p = sub.add_parser("contractors", help="List contractors")
    contractors_p.set_defaults(func=cmd_contractors)

    contractor_payments_p = sub.add_parser("contractor-payments", help="List contractor payments")
    contractor_payments_p.set_defaults(func=cmd_contractor_payments)

    tax_forms_p = sub.add_parser("tax-forms", help="List tax forms")
    tax_forms_p.set_defaults(func=cmd_tax_forms)

    garnishments_p = sub.add_parser("garnishments", help="List garnishments")
    garnishments_p.add_argument("id", help="Employee ID")
    garnishments_p.set_defaults(func=cmd_garnishments)


    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
