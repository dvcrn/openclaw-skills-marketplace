#!/usr/bin/env python3
"""Terraform Cloud CLI — Terraform Cloud — manage workspaces, runs, plans, state, and variables via REST API

Zero dependencies beyond Python stdlib.
Built by M. Abidi | agxntsix.ai
"""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

API_BASE = "https://app.terraform.io/api/v2"

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
    token = get_env("TFC_TOKEN")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}



def get_api_base():
    base = API_BASE
    base = base; org = get_env("TFC_ORG"); base = base
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


def cmd_orgs(args):
    """List organizations."""
    path = "/organizations"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_workspaces(args):
    """List workspaces."""
    path = "/organizations/{org}/workspaces"
    params = {}
    if getattr(args, "search[name]", None): params["search[name]"] = args.search[name]
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_workspace_get(args):
    """Get workspace."""
    path = f"/workspaces/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_workspace_create(args):
    """Create workspace."""
    path = "/organizations/{org}/workspaces"
    body = {}
    if getattr(args, "name", None): body["name"] = try_json(args.name)
    if getattr(args, "auto_apply", None): body["auto-apply"] = try_json(args.auto_apply)
    if getattr(args, "terraform_version", None): body["terraform-version"] = try_json(args.terraform_version)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_workspace_delete(args):
    """Delete workspace."""
    path = f"/workspaces/{args.id}"
    data = req("DELETE", path)
    out(data, getattr(args, "human", False))

def cmd_workspace_lock(args):
    """Lock workspace."""
    path = f"/workspaces/{args.id}/actions/lock"
    body = {}
    if getattr(args, "reason", None): body["reason"] = try_json(args.reason)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_workspace_unlock(args):
    """Unlock workspace."""
    path = f"/workspaces/{args.id}/actions/unlock"
    data = req("POST", path)
    out(data, getattr(args, "human", False))

def cmd_runs(args):
    """List runs."""
    path = f"/workspaces/{args.id}/runs"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_run_get(args):
    """Get run."""
    path = f"/runs/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_run_create(args):
    """Create run."""
    path = "/runs"
    body = {}
    if getattr(args, "workspace_id", None): body["workspace_id"] = try_json(args.workspace_id)
    if getattr(args, "message", None): body["message"] = try_json(args.message)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_run_apply(args):
    """Apply run."""
    path = f"/runs/{args.id}/actions/apply"
    body = {}
    if getattr(args, "comment", None): body["comment"] = try_json(args.comment)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_run_discard(args):
    """Discard run."""
    path = f"/runs/{args.id}/actions/discard"
    data = req("POST", path)
    out(data, getattr(args, "human", False))

def cmd_run_cancel(args):
    """Cancel run."""
    path = f"/runs/{args.id}/actions/cancel"
    data = req("POST", path)
    out(data, getattr(args, "human", False))

def cmd_plan_get(args):
    """Get plan."""
    path = f"/plans/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_state_version(args):
    """Get current state."""
    path = f"/workspaces/{args.id}/current-state-version"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_variables(args):
    """List variables."""
    path = f"/workspaces/{args.id}/vars"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_variable_create(args):
    """Create variable."""
    path = f"/workspaces/{args.id}/vars"
    body = {}
    if getattr(args, "key", None): body["key"] = try_json(args.key)
    if getattr(args, "value", None): body["value"] = try_json(args.value)
    if getattr(args, "category", None): body["category"] = try_json(args.category)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_variable_delete(args):
    """Delete variable."""
    path = f"/vars/{args.id}"
    data = req("DELETE", path)
    out(data, getattr(args, "human", False))

def cmd_teams(args):
    """List teams."""
    path = "/organizations/{org}/teams"
    data = req("GET", path)
    out(data, getattr(args, "human", False))



def main():
    parser = argparse.ArgumentParser(description="Terraform Cloud CLI")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    sub = parser.add_subparsers(dest="command")

    orgs_p = sub.add_parser("orgs", help="List organizations")
    orgs_p.set_defaults(func=cmd_orgs)

    workspaces_p = sub.add_parser("workspaces", help="List workspaces")
    workspaces_p.add_argument("--search[name]", help="Search by name", default=None)
    workspaces_p.set_defaults(func=cmd_workspaces)

    workspace_get_p = sub.add_parser("workspace-get", help="Get workspace")
    workspace_get_p.add_argument("id", help="Workspace ID")
    workspace_get_p.set_defaults(func=cmd_workspace_get)

    workspace_create_p = sub.add_parser("workspace-create", help="Create workspace")
    workspace_create_p.add_argument("--name", help="Name", default=None)
    workspace_create_p.add_argument("--auto-apply", help="Auto apply", default=None)
    workspace_create_p.add_argument("--terraform-version", help="TF version", default=None)
    workspace_create_p.set_defaults(func=cmd_workspace_create)

    workspace_delete_p = sub.add_parser("workspace-delete", help="Delete workspace")
    workspace_delete_p.add_argument("id", help="Workspace ID")
    workspace_delete_p.set_defaults(func=cmd_workspace_delete)

    workspace_lock_p = sub.add_parser("workspace-lock", help="Lock workspace")
    workspace_lock_p.add_argument("id", help="ID")
    workspace_lock_p.add_argument("--reason", help="Reason", default=None)
    workspace_lock_p.set_defaults(func=cmd_workspace_lock)

    workspace_unlock_p = sub.add_parser("workspace-unlock", help="Unlock workspace")
    workspace_unlock_p.add_argument("id", help="ID")
    workspace_unlock_p.set_defaults(func=cmd_workspace_unlock)

    runs_p = sub.add_parser("runs", help="List runs")
    runs_p.add_argument("id", help="Workspace ID")
    runs_p.set_defaults(func=cmd_runs)

    run_get_p = sub.add_parser("run-get", help="Get run")
    run_get_p.add_argument("id", help="Run ID")
    run_get_p.set_defaults(func=cmd_run_get)

    run_create_p = sub.add_parser("run-create", help="Create run")
    run_create_p.add_argument("--workspace_id", help="Workspace ID", default=None)
    run_create_p.add_argument("--message", help="Message", default=None)
    run_create_p.set_defaults(func=cmd_run_create)

    run_apply_p = sub.add_parser("run-apply", help="Apply run")
    run_apply_p.add_argument("id", help="Run ID")
    run_apply_p.add_argument("--comment", help="Comment", default=None)
    run_apply_p.set_defaults(func=cmd_run_apply)

    run_discard_p = sub.add_parser("run-discard", help="Discard run")
    run_discard_p.add_argument("id", help="Run ID")
    run_discard_p.set_defaults(func=cmd_run_discard)

    run_cancel_p = sub.add_parser("run-cancel", help="Cancel run")
    run_cancel_p.add_argument("id", help="Run ID")
    run_cancel_p.set_defaults(func=cmd_run_cancel)

    plan_get_p = sub.add_parser("plan-get", help="Get plan")
    plan_get_p.add_argument("id", help="Plan ID")
    plan_get_p.set_defaults(func=cmd_plan_get)

    state_version_p = sub.add_parser("state-version", help="Get current state")
    state_version_p.add_argument("id", help="Workspace ID")
    state_version_p.set_defaults(func=cmd_state_version)

    variables_p = sub.add_parser("variables", help="List variables")
    variables_p.add_argument("id", help="Workspace ID")
    variables_p.set_defaults(func=cmd_variables)

    variable_create_p = sub.add_parser("variable-create", help="Create variable")
    variable_create_p.add_argument("id", help="Workspace ID")
    variable_create_p.add_argument("--key", help="Key", default=None)
    variable_create_p.add_argument("--value", help="Value", default=None)
    variable_create_p.add_argument("--category", help="terraform/env", default=None)
    variable_create_p.set_defaults(func=cmd_variable_create)

    variable_delete_p = sub.add_parser("variable-delete", help="Delete variable")
    variable_delete_p.add_argument("id", help="Variable ID")
    variable_delete_p.set_defaults(func=cmd_variable_delete)

    teams_p = sub.add_parser("teams", help="List teams")
    teams_p.set_defaults(func=cmd_teams)


    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
