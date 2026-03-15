#!/usr/bin/env python3
"""Replicate API CLI. Zero dependencies beyond Python stdlib."""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse


def get_token():
    token = os.environ.get("REPLICATE_API_TOKEN", "")
    if not token:
        env_path = os.path.join(os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("REPLICATE_API_TOKEN="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not token:
        print("Error: REPLICATE_API_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    return token


def api(method, path, data=None, params=None):
    url = "https://api.replicate.com/v1" + path
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {get_token()}")
    req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        raw = resp.read().decode()
        return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        print(f"API Error {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


def cmd_models(a):
    d = api("GET", "/models")
    for m in d.get("results",[]): print(json.dumps({"owner":m.get("owner"),"name":m.get("name"),"description":m.get("description","")[:100]}))

def cmd_model_get(a): print(json.dumps(api("GET", f"/models/{a.owner}/{a.name}"), indent=2))

def cmd_predictions(a):
    d = api("GET", "/predictions")
    for p in d.get("results",[]): print(json.dumps({"id":p["id"],"status":p["status"],"model":p.get("model"),"created_at":p.get("created_at")}))

def cmd_prediction_get(a): print(json.dumps(api("GET", f"/predictions/{a.id}"), indent=2))

def cmd_run(a):
    d = {"version": a.version, "input": json.loads(a.input)}
    if a.webhook: d["webhook"] = a.webhook
    r = api("POST", "/predictions", d)
    print(json.dumps({"id":r["id"],"status":r["status"],"urls":r.get("urls",{})}, indent=2))

def cmd_cancel(a):
    api("POST", f"/predictions/{a.id}/cancel"); print(json.dumps({"ok":True}))

def cmd_collections(a):
    d = api("GET", "/collections")
    for c in d.get("results",[]): print(json.dumps({"slug":c.get("slug"),"name":c.get("name")}))

def cmd_search(a):
    d = api("GET", "/models", params={"query": a.query})
    for m in d.get("results",[]): print(json.dumps({"owner":m.get("owner"),"name":m.get("name"),"run_count":m.get("run_count")}))

def cmd_hardware(a):
    d = api("GET", "/hardware")
    for h in (d if isinstance(d,list) else []): print(json.dumps(h))

def cmd_me(a): print(json.dumps(api("GET", "/account"), indent=2))

def main():
    p = argparse.ArgumentParser(description="Replicate ML Platform CLI")
    s = p.add_subparsers(dest="command")
    s.add_parser("models")
    x = s.add_parser("model"); x.add_argument("owner"); x.add_argument("name")
    s.add_parser("predictions")
    x = s.add_parser("prediction"); x.add_argument("id")
    x = s.add_parser("run"); x.add_argument("version"); x.add_argument("input"); x.add_argument("--webhook")
    x = s.add_parser("cancel"); x.add_argument("id")
    s.add_parser("collections")
    x = s.add_parser("search"); x.add_argument("query")
    s.add_parser("hardware"); s.add_parser("me")
    a = p.parse_args()
    c = {"models":cmd_models,"model":cmd_model_get,"predictions":cmd_predictions,"prediction":cmd_prediction_get,"run":cmd_run,"cancel":cmd_cancel,"collections":cmd_collections,"search":cmd_search,"hardware":cmd_hardware,"me":cmd_me}
    if a.command in c: c[a.command](a)
    else: p.print_help()

if __name__ == "__main__": main()
