#!/usr/bin/env python3
"""Thinkific CLI — Thinkific — manage courses, students, enrollments, coupons, and products via REST API

Zero dependencies beyond Python stdlib.
Built by M. Abidi | agxntsix.ai
"""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

API_BASE = "https://api.thinkific.com/api/public/v1"

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
    token = get_env("THINKIFIC_API_KEY")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}


# Thinkific requires subdomain header


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


def cmd_courses(args):
    """List courses."""
    path = "/courses"
    params = {}
    if getattr(args, "page", None): params["page"] = args.page
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_course_get(args):
    """Get course."""
    path = f"/courses/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_course_create(args):
    """Create course."""
    path = "/courses"
    body = {}
    if getattr(args, "name", None): body["name"] = try_json(args.name)
    if getattr(args, "slug", None): body["slug"] = try_json(args.slug)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_course_update(args):
    """Update course."""
    path = f"/courses/{args.id}"
    body = {}
    if getattr(args, "name", None): body["name"] = try_json(args.name)
    data = req("PUT", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_course_delete(args):
    """Delete course."""
    path = f"/courses/{args.id}"
    data = req("DELETE", path)
    out(data, getattr(args, "human", False))

def cmd_chapters(args):
    """List chapters."""
    path = f"/courses/{args.id}/chapters"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_users(args):
    """List users."""
    path = "/users"
    params = {}
    if getattr(args, "page", None): params["page"] = args.page
    if getattr(args, "query", None): params["query"] = args.query
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_user_get(args):
    """Get user."""
    path = f"/users/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_user_create(args):
    """Create user."""
    path = "/users"
    body = {}
    if getattr(args, "email", None): body["email"] = try_json(args.email)
    if getattr(args, "first_name", None): body["first_name"] = try_json(args.first_name)
    if getattr(args, "last_name", None): body["last_name"] = try_json(args.last_name)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_enrollments(args):
    """List enrollments."""
    path = "/enrollments"
    params = {}
    if getattr(args, "course_id", None): params["course_id"] = args.course_id
    if getattr(args, "user_id", None): params["user_id"] = args.user_id
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_enroll(args):
    """Create enrollment."""
    path = "/enrollments"
    body = {}
    if getattr(args, "user_id", None): body["user_id"] = try_json(args.user_id)
    if getattr(args, "course_id", None): body["course_id"] = try_json(args.course_id)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_coupons(args):
    """List coupons."""
    path = "/coupons"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_coupon_create(args):
    """Create coupon."""
    path = "/coupons"
    body = {}
    if getattr(args, "code", None): body["code"] = try_json(args.code)
    if getattr(args, "discount_type", None): body["discount_type"] = try_json(args.discount_type)
    if getattr(args, "discount_amount", None): body["discount_amount"] = try_json(args.discount_amount)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_products(args):
    """List products."""
    path = "/products"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_orders(args):
    """List orders."""
    path = "/orders"
    params = {}
    if getattr(args, "page", None): params["page"] = args.page
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_groups(args):
    """List groups."""
    path = "/groups"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_instructors(args):
    """List instructors."""
    path = "/instructors"
    data = req("GET", path)
    out(data, getattr(args, "human", False))



def main():
    parser = argparse.ArgumentParser(description="Thinkific CLI")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    sub = parser.add_subparsers(dest="command")

    courses_p = sub.add_parser("courses", help="List courses")
    courses_p.add_argument("--page", help="Page", default=None)
    courses_p.set_defaults(func=cmd_courses)

    course_get_p = sub.add_parser("course-get", help="Get course")
    course_get_p.add_argument("id", help="Course ID")
    course_get_p.set_defaults(func=cmd_course_get)

    course_create_p = sub.add_parser("course-create", help="Create course")
    course_create_p.add_argument("--name", help="Name", default=None)
    course_create_p.add_argument("--slug", help="URL slug", default=None)
    course_create_p.set_defaults(func=cmd_course_create)

    course_update_p = sub.add_parser("course-update", help="Update course")
    course_update_p.add_argument("id", help="ID")
    course_update_p.add_argument("--name", help="Name", default=None)
    course_update_p.set_defaults(func=cmd_course_update)

    course_delete_p = sub.add_parser("course-delete", help="Delete course")
    course_delete_p.add_argument("id", help="ID")
    course_delete_p.set_defaults(func=cmd_course_delete)

    chapters_p = sub.add_parser("chapters", help="List chapters")
    chapters_p.add_argument("id", help="Course ID")
    chapters_p.set_defaults(func=cmd_chapters)

    users_p = sub.add_parser("users", help="List users")
    users_p.add_argument("--page", help="Page", default=None)
    users_p.add_argument("--query", help="Search", default=None)
    users_p.set_defaults(func=cmd_users)

    user_get_p = sub.add_parser("user-get", help="Get user")
    user_get_p.add_argument("id", help="User ID")
    user_get_p.set_defaults(func=cmd_user_get)

    user_create_p = sub.add_parser("user-create", help="Create user")
    user_create_p.add_argument("--email", help="Email", default=None)
    user_create_p.add_argument("--first_name", help="First name", default=None)
    user_create_p.add_argument("--last_name", help="Last name", default=None)
    user_create_p.set_defaults(func=cmd_user_create)

    enrollments_p = sub.add_parser("enrollments", help="List enrollments")
    enrollments_p.add_argument("--course_id", help="Course ID", default=None)
    enrollments_p.add_argument("--user_id", help="User ID", default=None)
    enrollments_p.set_defaults(func=cmd_enrollments)

    enroll_p = sub.add_parser("enroll", help="Create enrollment")
    enroll_p.add_argument("--user_id", help="User ID", default=None)
    enroll_p.add_argument("--course_id", help="Course ID", default=None)
    enroll_p.set_defaults(func=cmd_enroll)

    coupons_p = sub.add_parser("coupons", help="List coupons")
    coupons_p.set_defaults(func=cmd_coupons)

    coupon_create_p = sub.add_parser("coupon-create", help="Create coupon")
    coupon_create_p.add_argument("--code", help="Code", default=None)
    coupon_create_p.add_argument("--discount_type", help="Type", default=None)
    coupon_create_p.add_argument("--discount_amount", help="Amount", default=None)
    coupon_create_p.set_defaults(func=cmd_coupon_create)

    products_p = sub.add_parser("products", help="List products")
    products_p.set_defaults(func=cmd_products)

    orders_p = sub.add_parser("orders", help="List orders")
    orders_p.add_argument("--page", help="Page", default=None)
    orders_p.set_defaults(func=cmd_orders)

    groups_p = sub.add_parser("groups", help="List groups")
    groups_p.set_defaults(func=cmd_groups)

    instructors_p = sub.add_parser("instructors", help="List instructors")
    instructors_p.set_defaults(func=cmd_instructors)


    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
