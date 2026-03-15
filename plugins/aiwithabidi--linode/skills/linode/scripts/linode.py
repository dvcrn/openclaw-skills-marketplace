#!/usr/bin/env python3
"""Linode/Akamai CLI — Linode (Akamai) — compute instances, volumes, networking, NodeBalancers, domains, and Kubernetes.

Zero dependencies beyond Python stdlib.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "https://api.linode.com/v4"


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
    token = get_env("LINODE_TOKEN")
    if not token:
        print("Error: LINODE_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{base}{path}"
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v}, doseq=True)
        url = f"{url}{'&' if '?' in url else '?'}{qs}"
    return req(method, url, data=data, headers=headers)


def out(data):
    print(json.dumps(data, indent=2, default=str))


def cmd_list_instances(args):
    """List Linode instances"""
    path = "/linode/instances"
    params = {}
    if args.page:
        params["page"] = args.page
    result = api("GET", path, params=params)
    out(result)

def cmd_get_instance(args):
    """Get instance details"""
    path = "/linode/instances/{id}"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_create_instance(args):
    """Create instance"""
    path = "/linode/instances"
    data = {}
    if args.type:
        data["type"] = args.type
    if args.region:
        data["region"] = args.region
    if args.image:
        data["image"] = args.image
    if args.label:
        data["label"] = args.label
    if args.root_pass:
        data["root-pass"] = args.root_pass
    result = api("POST", path, data=data)
    out(result)

def cmd_delete_instance(args):
    """Delete instance"""
    path = "/linode/instances/{id}"
    path = path.replace("{id}", str(args.id))
    result = api("DELETE", path)
    out(result)

def cmd_boot_instance(args):
    """Boot instance"""
    path = "/linode/instances/{id}/boot"
    path = path.replace("{id}", str(args.id))
    data = {}
    result = api("POST", path, data=data)
    out(result)

def cmd_reboot_instance(args):
    """Reboot instance"""
    path = "/linode/instances/{id}/reboot"
    path = path.replace("{id}", str(args.id))
    data = {}
    result = api("POST", path, data=data)
    out(result)

def cmd_shutdown_instance(args):
    """Shut down instance"""
    path = "/linode/instances/{id}/shutdown"
    path = path.replace("{id}", str(args.id))
    data = {}
    result = api("POST", path, data=data)
    out(result)

def cmd_list_volumes(args):
    """List volumes"""
    path = "/volumes"
    result = api("GET", path)
    out(result)

def cmd_create_volume(args):
    """Create volume"""
    path = "/volumes"
    data = {}
    if args.label:
        data["label"] = args.label
    if args.size:
        data["size"] = args.size
    if args.region:
        data["region"] = args.region
    result = api("POST", path, data=data)
    out(result)

def cmd_list_nodebalancers(args):
    """List NodeBalancers"""
    path = "/nodebalancers"
    result = api("GET", path)
    out(result)

def cmd_list_domains(args):
    """List domains"""
    path = "/domains"
    result = api("GET", path)
    out(result)

def cmd_list_domain_records(args):
    """List domain records"""
    path = "/domains/{id}/records"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_list_firewalls(args):
    """List firewalls"""
    path = "/networking/firewalls"
    result = api("GET", path)
    out(result)

def cmd_list_kubernetes(args):
    """List LKE clusters"""
    path = "/lke/clusters"
    result = api("GET", path)
    out(result)

def cmd_list_types(args):
    """List instance types/plans"""
    path = "/linode/types"
    result = api("GET", path)
    out(result)

def cmd_list_regions(args):
    """List regions"""
    path = "/regions"
    result = api("GET", path)
    out(result)

def cmd_list_images(args):
    """List images"""
    path = "/images"
    result = api("GET", path)
    out(result)

def cmd_get_account(args):
    """Get account info"""
    path = "/account"
    result = api("GET", path)
    out(result)


def main():
    parser = argparse.ArgumentParser(description="Linode/Akamai CLI")
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    p_list_instances = sub.add_parser("list-instances", help="List Linode instances")
    p_list_instances.add_argument("--page", default="1")
    p_list_instances.set_defaults(func=cmd_list_instances)

    p_get_instance = sub.add_parser("get-instance", help="Get instance details")
    p_get_instance.add_argument("id")
    p_get_instance.set_defaults(func=cmd_get_instance)

    p_create_instance = sub.add_parser("create-instance", help="Create instance")
    p_create_instance.add_argument("--type", default="g6-nanode-1")
    p_create_instance.add_argument("--region", default="us-east")
    p_create_instance.add_argument("--image", default="linode/ubuntu24.04")
    p_create_instance.add_argument("--label", required=True)
    p_create_instance.add_argument("--root-pass", required=True)
    p_create_instance.set_defaults(func=cmd_create_instance)

    p_delete_instance = sub.add_parser("delete-instance", help="Delete instance")
    p_delete_instance.add_argument("id")
    p_delete_instance.set_defaults(func=cmd_delete_instance)

    p_boot_instance = sub.add_parser("boot-instance", help="Boot instance")
    p_boot_instance.add_argument("id")
    p_boot_instance.set_defaults(func=cmd_boot_instance)

    p_reboot_instance = sub.add_parser("reboot-instance", help="Reboot instance")
    p_reboot_instance.add_argument("id")
    p_reboot_instance.set_defaults(func=cmd_reboot_instance)

    p_shutdown_instance = sub.add_parser("shutdown-instance", help="Shut down instance")
    p_shutdown_instance.add_argument("id")
    p_shutdown_instance.set_defaults(func=cmd_shutdown_instance)

    p_list_volumes = sub.add_parser("list-volumes", help="List volumes")
    p_list_volumes.set_defaults(func=cmd_list_volumes)

    p_create_volume = sub.add_parser("create-volume", help="Create volume")
    p_create_volume.add_argument("--label", required=True)
    p_create_volume.add_argument("--size", default="20")
    p_create_volume.add_argument("--region", default="us-east")
    p_create_volume.set_defaults(func=cmd_create_volume)

    p_list_nodebalancers = sub.add_parser("list-nodebalancers", help="List NodeBalancers")
    p_list_nodebalancers.set_defaults(func=cmd_list_nodebalancers)

    p_list_domains = sub.add_parser("list-domains", help="List domains")
    p_list_domains.set_defaults(func=cmd_list_domains)

    p_list_domain_records = sub.add_parser("list-domain-records", help="List domain records")
    p_list_domain_records.add_argument("id")
    p_list_domain_records.set_defaults(func=cmd_list_domain_records)

    p_list_firewalls = sub.add_parser("list-firewalls", help="List firewalls")
    p_list_firewalls.set_defaults(func=cmd_list_firewalls)

    p_list_kubernetes = sub.add_parser("list-kubernetes", help="List LKE clusters")
    p_list_kubernetes.set_defaults(func=cmd_list_kubernetes)

    p_list_types = sub.add_parser("list-types", help="List instance types/plans")
    p_list_types.set_defaults(func=cmd_list_types)

    p_list_regions = sub.add_parser("list-regions", help="List regions")
    p_list_regions.set_defaults(func=cmd_list_regions)

    p_list_images = sub.add_parser("list-images", help="List images")
    p_list_images.set_defaults(func=cmd_list_images)

    p_get_account = sub.add_parser("get-account", help="Get account info")
    p_get_account.set_defaults(func=cmd_get_account)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
