#!/usr/bin/env python3
"""Mux CLI — Mux video — manage assets, live streams, playback IDs, and analytics via REST API

Zero dependencies beyond Python stdlib.
Built by M. Abidi | agxntsix.ai
"""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

API_BASE = "https://api.mux.com"

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
    key = get_env("MUX_TOKEN_ID")
    secret = get_env("MUX_TOKEN_SECRET") if "MUX_TOKEN_SECRET" else ""
    creds = base64.b64encode(f"{key}:{secret}".encode()).decode()
    return {"Authorization": f"Basic {creds}", "Content-Type": "application/json", "Accept": "application/json"}



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


def cmd_assets(args):
    """List assets."""
    path = "/video/v1/assets"
    params = {}
    if getattr(args, "limit", None): params["limit"] = args.limit
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_asset_get(args):
    """Get asset."""
    path = f"/video/v1/assets/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_asset_create(args):
    """Create asset."""
    path = "/video/v1/assets"
    body = {}
    if getattr(args, "url", None): body["url"] = try_json(args.url)
    if getattr(args, "playback_policy", None): body["playback_policy"] = try_json(args.playback_policy)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_asset_delete(args):
    """Delete asset."""
    path = f"/video/v1/assets/{args.id}"
    data = req("DELETE", path)
    out(data, getattr(args, "human", False))

def cmd_asset_input_info(args):
    """Get input info."""
    path = f"/video/v1/assets/{args.id}/input-info"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_asset_playback_ids(args):
    """List playback IDs."""
    path = f"/video/v1/assets/{args.id}/playback-ids"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_live_streams(args):
    """List live streams."""
    path = "/video/v1/live-streams"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_live_stream_get(args):
    """Get live stream."""
    path = f"/video/v1/live-streams/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_live_stream_create(args):
    """Create live stream."""
    path = "/video/v1/live-streams"
    body = {}
    if getattr(args, "playback_policy", None): body["playback_policy"] = try_json(args.playback_policy)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_live_stream_delete(args):
    """Delete live stream."""
    path = f"/video/v1/live-streams/{args.id}"
    data = req("DELETE", path)
    out(data, getattr(args, "human", False))

def cmd_live_stream_reset_key(args):
    """Reset stream key."""
    path = f"/video/v1/live-streams/{args.id}/reset-stream-key"
    data = req("POST", path)
    out(data, getattr(args, "human", False))

def cmd_uploads(args):
    """List uploads."""
    path = "/video/v1/uploads"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_upload_create(args):
    """Create direct upload."""
    path = "/video/v1/uploads"
    body = {}
    if getattr(args, "cors_origin", None): body["cors_origin"] = try_json(args.cors_origin)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_views(args):
    """List video views."""
    path = "/data/v1/video-views"
    params = {}
    if getattr(args, "timeframe[]", None): params["timeframe[]"] = getattr(args, "timeframe_", None)
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_metrics(args):
    """Get metrics."""
    path = "/data/v1/metrics/overall"
    params = {}
    if getattr(args, "timeframe[]", None): params["timeframe[]"] = getattr(args, "timeframe_", None)
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_monitoring(args):
    """Monitoring metrics."""
    path = "/data/v1/monitoring/metrics"
    data = req("GET", path)
    out(data, getattr(args, "human", False))



def main():
    parser = argparse.ArgumentParser(description="Mux CLI")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    sub = parser.add_subparsers(dest="command")

    assets_p = sub.add_parser("assets", help="List assets")
    assets_p.add_argument("--limit", help="Limit", default=None)
    assets_p.set_defaults(func=cmd_assets)

    asset_get_p = sub.add_parser("asset-get", help="Get asset")
    asset_get_p.add_argument("id", help="Asset ID")
    asset_get_p.set_defaults(func=cmd_asset_get)

    asset_create_p = sub.add_parser("asset-create", help="Create asset")
    asset_create_p.add_argument("--url", help="Input URL", default=None)
    asset_create_p.add_argument("--playback_policy", help="public/signed", default=None)
    asset_create_p.set_defaults(func=cmd_asset_create)

    asset_delete_p = sub.add_parser("asset-delete", help="Delete asset")
    asset_delete_p.add_argument("id", help="Asset ID")
    asset_delete_p.set_defaults(func=cmd_asset_delete)

    asset_input_info_p = sub.add_parser("asset-input-info", help="Get input info")
    asset_input_info_p.add_argument("id", help="Asset ID")
    asset_input_info_p.set_defaults(func=cmd_asset_input_info)

    asset_playback_ids_p = sub.add_parser("asset-playback-ids", help="List playback IDs")
    asset_playback_ids_p.add_argument("id", help="Asset ID")
    asset_playback_ids_p.set_defaults(func=cmd_asset_playback_ids)

    live_streams_p = sub.add_parser("live-streams", help="List live streams")
    live_streams_p.set_defaults(func=cmd_live_streams)

    live_stream_get_p = sub.add_parser("live-stream-get", help="Get live stream")
    live_stream_get_p.add_argument("id", help="Stream ID")
    live_stream_get_p.set_defaults(func=cmd_live_stream_get)

    live_stream_create_p = sub.add_parser("live-stream-create", help="Create live stream")
    live_stream_create_p.add_argument("--playback_policy", help="public/signed", default=None)
    live_stream_create_p.set_defaults(func=cmd_live_stream_create)

    live_stream_delete_p = sub.add_parser("live-stream-delete", help="Delete live stream")
    live_stream_delete_p.add_argument("id", help="Stream ID")
    live_stream_delete_p.set_defaults(func=cmd_live_stream_delete)

    live_stream_reset_key_p = sub.add_parser("live-stream-reset-key", help="Reset stream key")
    live_stream_reset_key_p.add_argument("id", help="Stream ID")
    live_stream_reset_key_p.set_defaults(func=cmd_live_stream_reset_key)

    uploads_p = sub.add_parser("uploads", help="List uploads")
    uploads_p.set_defaults(func=cmd_uploads)

    upload_create_p = sub.add_parser("upload-create", help="Create direct upload")
    upload_create_p.add_argument("--cors_origin", help="CORS origin", default=None)
    upload_create_p.set_defaults(func=cmd_upload_create)

    views_p = sub.add_parser("views", help="List video views")
    views_p.add_argument("--timeframe", dest="timeframe_", help="Timeframe", default=None)
    views_p.set_defaults(func=cmd_views)

    metrics_p = sub.add_parser("metrics", help="Get metrics")
    metrics_p.add_argument("--timeframe", dest="timeframe_", help="Timeframe", default=None)
    metrics_p.set_defaults(func=cmd_metrics)

    monitoring_p = sub.add_parser("monitoring", help="Monitoring metrics")
    monitoring_p.set_defaults(func=cmd_monitoring)


    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
