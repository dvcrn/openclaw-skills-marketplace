#!/usr/bin/env python3
"""Railway API CLI. Zero dependencies beyond Python stdlib."""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse


def get_token():
    token = os.environ.get("RAILWAY_API_TOKEN", "")
    if not token:
        env_path = os.path.join(os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("RAILWAY_API_TOKEN="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not token:
        print("Error: RAILWAY_API_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    return token


API_URL = "https://backboard.railway.app/graphql/v2"

def gql(query, variables=None):
    data = {"query": query}
    if variables: data["variables"] = variables
    body = json.dumps(data).encode()
    req = urllib.request.Request(API_URL, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {get_token()}")
    req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read().decode())
        if result.get("errors"): print(f"GQL Error: {result['errors']}", file=sys.stderr); sys.exit(1)
        return result.get("data", {})
    except urllib.error.HTTPError as e:
        print(f"API Error {e.code}: {e.read().decode()}", file=sys.stderr); sys.exit(1)

def cmd_projects(a):
    d = gql("query{projects{edges{node{id name description updatedAt}}}}")
    for e in d.get("projects",{}).get("edges",[]): print(json.dumps(e["node"]))

def cmd_project_get(a):
    print(json.dumps(gql("query($id:String!){project(id:$id){id name environments{edges{node{id name}}}services{edges{node{id name}}}}}", {"id":a.id}).get("project",{}), indent=2))

def cmd_project_create(a):
    print(json.dumps(gql('mutation($i:ProjectCreateInput!){projectCreate(input:$i){id name}}', {"i":{"name":a.name}}), indent=2))

def cmd_services(a):
    d = gql("query($id:String!){project(id:$id){services{edges{node{id name}}}}}", {"id":a.project_id})
    for e in d.get("project",{}).get("services",{}).get("edges",[]): print(json.dumps(e["node"]))

def cmd_deployments(a):
    d = gql("query($f:Int,$i:DeploymentListInput!){deployments(first:$f,input:$i){edges{node{id status createdAt}}}}", {"f":a.limit,"i":{"projectId":a.project_id}})
    for e in d.get("deployments",{}).get("edges",[]): print(json.dumps(e["node"]))

def cmd_variables(a):
    d = gql("query($p:String!,$e:String!,$s:String){variables(projectId:$p,environmentId:$e,serviceId:$s)}", {"p":a.project_id,"e":a.env_id,"s":a.service_id})
    print(json.dumps(d.get("variables",{}), indent=2))

def cmd_me(a):
    print(json.dumps(gql("query{me{id email name}}").get("me",{}), indent=2))

def main():
    p = argparse.ArgumentParser(description="Railway Platform CLI")
    s = p.add_subparsers(dest="command")
    s.add_parser("projects")
    x = s.add_parser("project"); x.add_argument("id")
    x = s.add_parser("project-create"); x.add_argument("name")
    x = s.add_parser("services"); x.add_argument("project_id")
    x = s.add_parser("deployments"); x.add_argument("project_id"); x.add_argument("--limit", type=int, default=20)
    x = s.add_parser("variables"); x.add_argument("project_id"); x.add_argument("env_id"); x.add_argument("--service-id")
    s.add_parser("me")
    a = p.parse_args()
    c = {"projects":cmd_projects,"project":cmd_project_get,"project-create":cmd_project_create,"services":cmd_services,"deployments":cmd_deployments,"variables":cmd_variables,"me":cmd_me}
    if a.command in c: c[a.command](a)
    else: p.print_help()

if __name__ == "__main__": main()
