#!/usr/bin/env python3
"""Loom CLI — Loom — manage video recordings, transcripts, and folders via Developer API

Zero dependencies beyond Python stdlib.
Built by M. Abidi | agxntsix.ai
"""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

API_BASE = "https://developer.loom.com/v1"

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
    token = get_env("LOOM_ACCESS_TOKEN")
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


def cmd_videos(args):
    """List videos."""
    path = "/videos"
    params = {}
    if getattr(args, "per_page", None): params["per_page"] = args.per_page
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_video_get(args):
    """Get video."""
    path = f"/videos/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_video_update(args):
    """Update video."""
    path = f"/videos/{args.id}"
    body = {}
    if getattr(args, "title", None): body["title"] = try_json(args.title)
    if getattr(args, "description", None): body["description"] = try_json(args.description)
    data = req("PATCH", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_video_delete(args):
    """Delete video."""
    path = f"/videos/{args.id}"
    data = req("DELETE", path)
    out(data, getattr(args, "human", False))

def cmd_video_transcript(args):
    """Get transcript."""
    path = f"/videos/{args.id}/transcript"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_video_comments(args):
    """List comments."""
    path = f"/videos/{args.id}/comments"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_folders(args):
    """List folders."""
    path = "/folders"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_folder_get(args):
    """Get folder."""
    path = f"/folders/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_folder_videos(args):
    """List folder videos."""
    path = f"/folders/{args.id}/videos"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_user(args):
    """Get current user."""
    path = "/me"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_members(args):
    """List workspace members."""
    path = "/members"
    data = req("GET", path)
    out(data, getattr(args, "human", False))



def main():
    parser = argparse.ArgumentParser(description="Loom CLI")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    sub = parser.add_subparsers(dest="command")

    videos_p = sub.add_parser("videos", help="List videos")
    videos_p.add_argument("--per_page", help="Per page", default=None)
    videos_p.set_defaults(func=cmd_videos)

    video_get_p = sub.add_parser("video-get", help="Get video")
    video_get_p.add_argument("id", help="Video ID")
    video_get_p.set_defaults(func=cmd_video_get)

    video_update_p = sub.add_parser("video-update", help="Update video")
    video_update_p.add_argument("id", help="ID")
    video_update_p.add_argument("--title", help="Title", default=None)
    video_update_p.add_argument("--description", help="Description", default=None)
    video_update_p.set_defaults(func=cmd_video_update)

    video_delete_p = sub.add_parser("video-delete", help="Delete video")
    video_delete_p.add_argument("id", help="Video ID")
    video_delete_p.set_defaults(func=cmd_video_delete)

    video_transcript_p = sub.add_parser("video-transcript", help="Get transcript")
    video_transcript_p.add_argument("id", help="Video ID")
    video_transcript_p.set_defaults(func=cmd_video_transcript)

    video_comments_p = sub.add_parser("video-comments", help="List comments")
    video_comments_p.add_argument("id", help="Video ID")
    video_comments_p.set_defaults(func=cmd_video_comments)

    folders_p = sub.add_parser("folders", help="List folders")
    folders_p.set_defaults(func=cmd_folders)

    folder_get_p = sub.add_parser("folder-get", help="Get folder")
    folder_get_p.add_argument("id", help="Folder ID")
    folder_get_p.set_defaults(func=cmd_folder_get)

    folder_videos_p = sub.add_parser("folder-videos", help="List folder videos")
    folder_videos_p.add_argument("id", help="Folder ID")
    folder_videos_p.set_defaults(func=cmd_folder_videos)

    user_p = sub.add_parser("user", help="Get current user")
    user_p.set_defaults(func=cmd_user)

    members_p = sub.add_parser("members", help="List workspace members")
    members_p.set_defaults(func=cmd_members)


    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
