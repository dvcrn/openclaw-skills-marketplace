#!/usr/bin/env python3
"""
DeepEvidence Chat — Medical Q&A via OpenAI-compatible API.

Usage:
    python chat.py "What are the symptoms of diabetes?"
    python chat.py "What are the symptoms of diabetes?" --user external-user-123
    python chat.py "What are follow-up treatment options?" --conversation-id abc123
    python chat.py "What are the CKD staging criteria?" --locale en

Environment:
    DEEPEVIDENCE_API_KEY    Required. API key for authentication.
    DEEPEVIDENCE_BASE_URL   Optional. Default: https://deepevidence.cn/api/v1
    DEEPEVIDENCE_USER_ID    Optional. Default external user ID (only sent if explicitly provided via --user).
"""

import os
import sys
import argparse
from typing import Optional

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    sys.exit(1)

DEFAULT_TEMP_UNAVAILABLE_MSG = (
    "Temporarily unable to retrieve evidence-based results. "
    "Please try again later or consult a licensed clinician."
)


def _debug_enabled() -> bool:
    return os.environ.get("DEEPEVIDENCE_DEBUG", "").strip().lower() in ("1", "true", "yes", "on")


def _print_error(msg: str, *, debug_exc: Optional[Exception] = None) -> None:
    print(msg)
    if debug_exc is not None and _debug_enabled():
        # Avoid printing full request/response; only include minimal exception string.
        print(f"(debug) {type(debug_exc).__name__}: {debug_exc}", file=sys.stderr)


def _status_code_from_exc(exc: Exception) -> Optional[int]:
    for attr in ("status_code", "http_status"):
        v = getattr(exc, attr, None)
        if isinstance(v, int):
            return v
    resp = getattr(exc, "response", None)
    if resp is not None:
        v = getattr(resp, "status_code", None)
        if isinstance(v, int):
            return v
    return None


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


def _handle_api_exception(exc: Exception) -> None:
    status = _status_code_from_exc(exc)
    if status == 401:
        _print_error("Authentication failed: please check DEEPEVIDENCE_API_KEY.", debug_exc=exc)
        sys.exit(1)
    if status == 429:
        _print_error("Rate limit exceeded or quota exhausted: please retry later or contact your administrator.", debug_exc=exc)
        sys.exit(1)
    if status is not None and status >= 500:
        _print_error("Service temporarily unavailable: please retry later.", debug_exc=exc)
        sys.exit(1)
    if _is_timeout_exc(exc):
        _print_error(DEFAULT_TEMP_UNAVAILABLE_MSG, debug_exc=exc)
        sys.exit(1)
    if _is_connection_exc(exc):
        _print_error(DEFAULT_TEMP_UNAVAILABLE_MSG, debug_exc=exc)
        sys.exit(1)
    _print_error(DEFAULT_TEMP_UNAVAILABLE_MSG, debug_exc=exc)
    sys.exit(1)


def get_client():
    api_key = os.environ.get("DEEPEVIDENCE_API_KEY")
    if not api_key:
        _print_error("Missing configuration: DEEPEVIDENCE_API_KEY is not set. Please configure it and retry.")
        sys.exit(1)
    base_url = os.environ.get("DEEPEVIDENCE_BASE_URL", "https://deepevidence.cn/api/v1")
    return OpenAI(api_key=api_key, base_url=base_url)


def chat(query, user=None, conversation_id=None, locale=None, user_name=None, user_email=None):
    """Send a medical question to DeepEvidence and print the response."""
    client = get_client()

    kwargs = {"model": "deepevidence-agent-v1", "messages": [{"role": "user", "content": query}], "stream": False}

    # Do not auto-read/upload OS usernames. Only send an external user ID if explicitly provided.
    if user:
        if not user.startswith("skill_"):
            user = f"skill_{user}"
        kwargs["user"] = user

    metadata = {}
    if conversation_id:
        metadata["conversation_id"] = conversation_id
    if locale:
        metadata["locale"] = locale
    if user_name:
        metadata["user_name"] = user_name
    if user_email:
        metadata["user_email"] = user_email
    if metadata:
        kwargs["extra_body"] = {"metadata": metadata}

    try:
        response = client.chat.completions.create(**kwargs)
    except Exception as e:
        _handle_api_exception(e)

    if not response or not getattr(response, "choices", None) or not response.choices:
        _print_error(DEFAULT_TEMP_UNAVAILABLE_MSG)
        sys.exit(1)
    if not getattr(response.choices[0], "message", None) or not getattr(response.choices[0].message, "content", None):
        _print_error(DEFAULT_TEMP_UNAVAILABLE_MSG)
        sys.exit(1)

    # Print answer
    print(response.choices[0].message.content)

    # Print metadata if available
    resp_dict = response.model_dump() if hasattr(response, "model_dump") else {}
    conv_id = resp_dict.get("metadata", {}).get("conversation_id")
    if conv_id:
        print(f"\n--- conversation_id: {conv_id} ---")

    # Print usage
    if response.usage:
        print(f"[tokens: prompt={response.usage.prompt_tokens}, completion={response.usage.completion_tokens}, total={response.usage.total_tokens}]")

    return response


def main():
    parser = argparse.ArgumentParser(description="DeepEvidence Medical Q&A")
    parser.add_argument("query", help="Medical question to ask")
    parser.add_argument("--user", default=None, help="External user ID for multi-tenant isolation (OPTIONAL). Not sent unless provided.")
    parser.add_argument("--conversation-id", help="Continue an existing conversation by ID")
    parser.add_argument("--locale", help="Language preference, e.g. 'en', 'zh-CN'")
    parser.add_argument("--user-name", help="User display name (optional, used with --user)")
    parser.add_argument("--user-email", help="User email (optional, used with --user)")
    args = parser.parse_args()

    chat(args.query, user=args.user, conversation_id=args.conversation_id, locale=args.locale, user_name=args.user_name, user_email=args.user_email)


if __name__ == "__main__":
    main()
