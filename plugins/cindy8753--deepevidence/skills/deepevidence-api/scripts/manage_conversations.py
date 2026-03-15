#!/usr/bin/env python3
"""
DeepEvidence Conversation Manager — List, view, search, and delete conversations.

These are DeepEvidence extension APIs (not part of OpenAI standard).

Usage:
    python manage_conversations.py list
    python manage_conversations.py list --query "diabetes" --limit 5
    python manage_conversations.py get <conversation_id>
    python manage_conversations.py messages <conversation_id>
    python manage_conversations.py delete <conversation_id>
    python manage_conversations.py delete <conversation_id> --yes   # skip confirmation (dangerous)

Environment:
    DEEPEVIDENCE_API_KEY    Required. API key for authentication.
    DEEPEVIDENCE_BASE_URL   Optional. Default: https://deepevidence.cn/api/v1
    DEEPEVIDENCE_USER_ID    Optional. Default external user ID.
"""

import os
import sys
import json
import argparse

try:
    import httpx as _httpx
    _HTTP_CLIENT = "httpx"
except ImportError:
    try:
        import requests as _requests
        _HTTP_CLIENT = "requests"
    except ImportError:
        print("Error: httpx or requests package not installed. Run: pip install httpx")
        sys.exit(1)

DEFAULT_TIMEOUT_S = float(os.environ.get("DEEPEVIDENCE_TIMEOUT", "20"))


def _is_timeout_exc(exc: Exception) -> bool:
    name = type(exc).__name__.lower()
    if "timeout" in name:
        return True
    cause = getattr(exc, "__cause__", None)
    if cause is not None and "timeout" in type(cause).__name__.lower():
        return True
    return False


def _is_connection_exc(exc: Exception) -> bool:
    name = type(exc).__name__.lower()
    if "connection" in name:
        return True
    cause = getattr(exc, "__cause__", None)
    if cause is not None and "connection" in type(cause).__name__.lower():
        return True
    return False


def _request(method: str, url: str, *, headers=None, params=None, json_body=None, timeout_s: float = DEFAULT_TIMEOUT_S):
    """
    Unified request wrapper with:
    - timeout
    - network exception handling
    - status code handling
    - JSON decode protection
    Returns: (resp, data) where data is parsed JSON dict/list, or None if JSON parse failed.
    """
    try:
        if _HTTP_CLIENT == "httpx":
            resp = _httpx.request(method, url, headers=headers, params=params, json=json_body, timeout=timeout_s)
        else:
            resp = _requests.request(method, url, headers=headers, params=params, json=json_body, timeout=timeout_s)
    except Exception as e:
        if _is_timeout_exc(e):
            print(f"Error: Request timed out after {timeout_s:.0f}s.")
        elif _is_connection_exc(e):
            print("Error: Network connection failed. Please check connectivity and try again.")
        else:
            print(f"Error: Network request failed: {type(e).__name__}")
        sys.exit(1)

    # Status code handling (prefer explicit + show server message if available)
    status = getattr(resp, "status_code", None)
    data = None
    try:
        data = resp.json()
    except Exception:
        data = None

    if isinstance(status, int) and not (200 <= status < 300):
        msg = None
        if isinstance(data, dict) and "error" in data:
            msg = data["error"].get("message")
        if not msg:
            msg = f"HTTP {status}"
        print(f"Error: {msg}")
        sys.exit(1)

    if data is None:
        print("Error: Failed to decode JSON response from server.")
        sys.exit(1)

    return resp, data


def get_config():
    api_key = os.environ.get("DEEPEVIDENCE_API_KEY")
    if not api_key:
        print("Error: DEEPEVIDENCE_API_KEY environment variable is not set.")
        sys.exit(1)
    base_url = os.environ.get("DEEPEVIDENCE_BASE_URL", "https://deepevidence.cn/api/v1")
    user_id = os.environ.get("DEEPEVIDENCE_USER_ID")
    return api_key, base_url, user_id


def make_headers(api_key, user_id=None):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    if user_id:
        headers["X-User-ID"] = user_id
    return headers


def pp(data):
    """Pretty-print JSON data."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def list_conversations(args):
    api_key, base_url, user_id = get_config()
    user_id = args.user or user_id
    params = {"limit": args.limit, "offset": args.offset}
    if args.query:
        params["q"] = args.query
    _, data = _request(
        "GET",
        f"{base_url}/conversations",
        headers=make_headers(api_key, user_id),
        params=params,
    )
    if "error" in data:
        print(f"Error: {data['error'].get('message', 'Unknown error')}")
        sys.exit(1)
    conversations = data.get("data", [])
    if not conversations:
        print("No conversations found.")
        return
    print(f"Found {len(conversations)} conversation(s) (has_more={data.get('has_more', False)}):\n")
    for c in conversations:
        fav = " ⭐" if c.get("is_favorited") else ""
        print(f"  [{c['id']}] {c.get('title', 'Untitled')}{fav}")
    print()


def get_conversation(args):
    api_key, base_url, user_id = get_config()
    user_id = args.user or user_id
    _, data = _request(
        "GET",
        f"{base_url}/conversations/{args.id}",
        headers=make_headers(api_key, user_id),
    )
    if "error" in data:
        print(f"Error: {data['error'].get('message', 'Unknown error')}")
        sys.exit(1)
    pp(data)


def get_messages(args):
    api_key, base_url, user_id = get_config()
    user_id = args.user or user_id
    _, data = _request(
        "GET",
        f"{base_url}/conversations/{args.id}/messages",
        headers=make_headers(api_key, user_id),
    )
    if "error" in data:
        print(f"Error: {data['error'].get('message', 'Unknown error')}")
        sys.exit(1)
    messages = data.get("data", [])
    for msg in messages:
        role = msg.get("role", "unknown").upper()
        content = msg.get("content", "")
        print(f"[{role}] {content[:200]}{'...' if len(content) > 200 else ''}\n")


def delete_conversation(args):
    api_key, base_url, user_id = get_config()
    user_id = args.user or user_id

    if not args.yes:
        convo_title = None
        convo_created_at = None
        try:
            _, data_get = _request(
                "GET",
                f"{base_url}/conversations/{args.id}",
                headers=make_headers(api_key, user_id),
            )
            if isinstance(data_get, dict) and "error" not in data_get:
                convo_title = data_get.get("title")
                convo_created_at = data_get.get("created_at")
        except Exception:
            # Best-effort metadata fetch; deletion still requires explicit confirmation below.
            pass

        print("About to delete conversation:")
        print(f"  id: {args.id}")
        if convo_title is not None:
            print(f"  title: {convo_title}")
        if convo_created_at is not None:
            print(f"  created_at: {convo_created_at}")
        if not sys.stdin.isatty():
            print("Refusing to delete without confirmation in non-interactive mode. Re-run with --yes to proceed.")
            sys.exit(2)
        ans = input("Are you sure you want to delete this conversation? [y/N] ").strip().lower()
        if ans not in ("y", "yes"):
            print("Aborted.")
            return

    _, data = _request(
        "DELETE",
        f"{base_url}/conversations/{args.id}",
        headers=make_headers(api_key, user_id),
    )
    if data.get("deleted"):
        print(f"✅ Conversation {args.id} deleted.")
    else:
        print(f"Error: {data.get('error', {}).get('message', 'Delete failed')}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="DeepEvidence Conversation Manager")
    parser.add_argument("--user", default=None, help="External user ID")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = sub.add_parser("list", help="List conversations")
    p_list.add_argument("--limit", type=int, default=20, help="Max results (default 20, max 100)")
    p_list.add_argument("--offset", type=int, default=0, help="Offset for pagination")
    p_list.add_argument("--query", "-q", help="Search keyword")
    p_list.set_defaults(func=list_conversations)

    # get
    p_get = sub.add_parser("get", help="Get conversation detail with messages")
    p_get.add_argument("id", help="Conversation ID")
    p_get.set_defaults(func=get_conversation)

    # messages
    p_msg = sub.add_parser("messages", help="Get conversation messages")
    p_msg.add_argument("id", help="Conversation ID")
    p_msg.set_defaults(func=get_messages)

    # delete
    p_del = sub.add_parser("delete", help="Delete a conversation")
    p_del.add_argument("id", help="Conversation ID")
    p_del.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip interactive confirmation (DANGEROUS).",
    )
    p_del.set_defaults(func=delete_conversation)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
