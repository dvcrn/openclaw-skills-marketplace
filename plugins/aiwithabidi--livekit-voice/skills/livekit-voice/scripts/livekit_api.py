#!/usr/bin/env python3
"""LiveKit real-time voice/video API integration for OpenClaw agents."""

import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def get_config():
    api_key = os.environ.get("LIVEKIT_API_KEY")
    api_secret = os.environ.get("LIVEKIT_API_SECRET")
    url = os.environ.get("LIVEKIT_URL")
    if not all([api_key, api_secret, url]):
        print("Error: LIVEKIT_API_KEY, LIVEKIT_API_SECRET, and LIVEKIT_URL must be set", file=sys.stderr)
        sys.exit(1)
    return api_key, api_secret, url


def b64url_encode(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def generate_jwt(api_key, api_secret, grants, ttl=3600):
    """Generate a LiveKit-compatible JWT access token."""
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        "iss": api_key,
        "nbf": now,
        "exp": now + ttl,
        "sub": grants.get("identity", ""),
        "name": grants.get("name", ""),
        "video": grants.get("video", {}),
    }
    segments = [b64url_encode(json.dumps(header)), b64url_encode(json.dumps(payload))]
    signing_input = ".".join(segments).encode()
    signature = hmac.new(api_secret.encode(), signing_input, hashlib.sha256).digest()
    segments.append(b64url_encode(signature))
    return ".".join(segments)


def twirp_request(url, api_key, api_secret, service, method, body=None):
    """Make a Twirp RPC request to LiveKit server."""
    # Convert wss:// to https:// for API calls
    http_url = url.replace("wss://", "https://").replace("ws://", "http://")
    endpoint = f"{http_url}/twirp/livekit.{service}/{method}"

    token = generate_jwt(api_key, api_secret, {
        "video": {"roomCreate": True, "roomList": True, "roomAdmin": True, "roomRecord": True}
    })

    data = json.dumps(body or {}).encode()
    req = Request(endpoint, data=data, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        body_text = e.read().decode() if e.fp else ""
        print(f"API Error {e.code}: {body_text}", file=sys.stderr)
        sys.exit(1)


def cmd_create_room(args):
    api_key, api_secret, url = get_config()
    body = {"name": args.name}
    if args.max_participants:
        body["maxParticipants"] = args.max_participants
    if args.empty_timeout:
        body["emptyTimeout"] = args.empty_timeout

    result = twirp_request(url, api_key, api_secret, "RoomService", "CreateRoom", body)
    print(f"  Room created: {result.get('name', args.name)}")
    print(f"  SID: {result.get('sid', 'N/A')}")
    print(f"  Max Participants: {result.get('maxParticipants', 'unlimited')}")


def cmd_token(args):
    api_key, api_secret, _ = get_config()
    video_grants = {"room": args.room, "roomJoin": True}
    if args.can_publish:
        video_grants["canPublish"] = True
    if args.can_subscribe:
        video_grants["canSubscribe"] = True

    grants = {
        "identity": args.identity,
        "name": args.name or args.identity,
        "video": video_grants,
    }
    token = generate_jwt(api_key, api_secret, grants, ttl=args.ttl)
    print(f"  Token for '{args.identity}' in room '{args.room}':")
    print(f"  {token}")


def cmd_list_rooms(args):
    api_key, api_secret, url = get_config()
    result = twirp_request(url, api_key, api_secret, "RoomService", "ListRooms", {})
    rooms = result.get("rooms", [])
    if not rooms:
        print("  No active rooms.")
        return
    for r in rooms:
        print(f"  {r.get('name','?')} | SID: {r.get('sid','?')} | Participants: {r.get('numParticipants',0)} | Created: {r.get('creationTime','?')}")


def cmd_participants(args):
    api_key, api_secret, url = get_config()
    result = twirp_request(url, api_key, api_secret, "RoomService", "ListParticipants", {"room": args.room})
    participants = result.get("participants", [])
    if not participants:
        print(f"  No participants in '{args.room}'.")
        return
    for p in participants:
        tracks = len(p.get("tracks", []))
        print(f"  {p.get('identity','?')} ({p.get('name','?')}) | State: {p.get('state','?')} | Tracks: {tracks}")


def cmd_delete_room(args):
    api_key, api_secret, url = get_config()
    twirp_request(url, api_key, api_secret, "RoomService", "DeleteRoom", {"room": args.name})
    print(f"  Room '{args.name}' deleted.")


def cmd_record(args):
    api_key, api_secret, url = get_config()
    body = {
        "roomCompositeRequest": {
            "roomName": args.room,
            "layout": "speaker-dark",
        }
    }
    if args.output:
        if args.output.startswith("s3://"):
            body["roomCompositeRequest"]["fileOutputs"] = [{"s3": {"bucket": args.output.split("/")[2], "prefix": "/".join(args.output.split("/")[3:])}}]
        else:
            body["roomCompositeRequest"]["file"] = {"filepath": args.output}

    result = twirp_request(url, api_key, api_secret, "Egress", "StartRoomCompositeEgress", body)
    print(f"  Recording started: {result.get('egressId', 'N/A')}")
    print(f"  Status: {result.get('status', 'N/A')}")


def main():
    parser = argparse.ArgumentParser(description="LiveKit Voice/Video API")
    sub = parser.add_subparsers(dest="command", required=True)

    p_cr = sub.add_parser("create-room", help="Create a room")
    p_cr.add_argument("name")
    p_cr.add_argument("--max-participants", type=int)
    p_cr.add_argument("--empty-timeout", type=int, default=300)

    p_tok = sub.add_parser("token", help="Generate access token")
    p_tok.add_argument("room")
    p_tok.add_argument("--identity", required=True)
    p_tok.add_argument("--name")
    p_tok.add_argument("--can-publish", action="store_true")
    p_tok.add_argument("--can-subscribe", action="store_true")
    p_tok.add_argument("--ttl", type=int, default=3600)

    sub.add_parser("list-rooms", help="List active rooms")

    p_part = sub.add_parser("participants", help="List participants")
    p_part.add_argument("room")

    p_del = sub.add_parser("delete-room", help="Delete a room")
    p_del.add_argument("name")

    p_rec = sub.add_parser("record", help="Start recording")
    p_rec.add_argument("room")
    p_rec.add_argument("--output")

    args = parser.parse_args()
    cmds = {
        "create-room": cmd_create_room, "token": cmd_token, "list-rooms": cmd_list_rooms,
        "participants": cmd_participants, "delete-room": cmd_delete_room, "record": cmd_record,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
