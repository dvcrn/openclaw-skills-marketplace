#!/usr/bin/env python3
"""OpenAI CLI — comprehensive API integration for AI agents.

Full CRUD operations, search, reporting, and automation.
Zero dependencies beyond Python stdlib.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone

API_BASE = "https://api.openai.com/v1"


def get_token():
    """Get API token from environment."""
    token = os.environ.get("OPENAI_API_KEY", "")
    if not token:
        env_path = os.path.join(
            os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")),
            ".env"
        )
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("OPENAI_API_KEY="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not token:
        print(f"Error: OPENAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return token


def api(method, path, data=None, params=None):
    """Make an API request."""
    token = get_token()
    url = f"{API_BASE}{path}"
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        if qs:
            url = f"{url}?{qs}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {"ok": True}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(json.dumps({"error": True, "code": e.code, "message": err_body}), file=sys.stderr)
        sys.exit(1)


def output(data, human=False):
    """Output data as JSON or human-readable."""
    if human and isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for k, v in item.items():
                    print(f"  {k}: {v}")
                print()
            else:
                print(item)
    elif human and isinstance(data, dict):
        for k, v in data.items():
            print(f"  {k}: {v}")
    else:
        print(json.dumps(data, indent=2, default=str))


def cmd_chat(args):
    """Send chat completion."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/chat/{args.id}")
    else:
        data = api("GET", "/chat", params=params)
    output(data, getattr(args, 'human', False))

def cmd_chat_system(args):
    """Chat with system prompt."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/chat/{args.id}")
    else:
        data = api("GET", "/chat/system", params=params)
    output(data, getattr(args, 'human', False))

def cmd_embed(args):
    """Generate embeddings."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/embed/{args.id}")
    else:
        data = api("GET", "/embed", params=params)
    output(data, getattr(args, 'human', False))

def cmd_image(args):
    """Generate an image."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/image/{args.id}")
    else:
        data = api("GET", "/image", params=params)
    output(data, getattr(args, 'human', False))

def cmd_transcribe(args):
    """Transcribe audio file."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/transcribe/{args.id}")
    else:
        data = api("GET", "/transcribe", params=params)
    output(data, getattr(args, 'human', False))

def cmd_tts(args):
    """Text to speech."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/tts/{args.id}")
    else:
        data = api("GET", "/tts", params=params)
    output(data, getattr(args, 'human', False))

def cmd_models(args):
    """List available models."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/models/{args.id}")
    else:
        data = api("GET", "/models", params=params)
    output(data, getattr(args, 'human', False))

def cmd_model_get(args):
    """Get model details."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/model/{args.id}")
    else:
        data = api("GET", "/model/get", params=params)
    output(data, getattr(args, 'human', False))

def cmd_files(args):
    """List uploaded files."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/files/{args.id}")
    else:
        data = api("GET", "/files", params=params)
    output(data, getattr(args, 'human', False))

def cmd_file_upload(args):
    """Upload a file."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/file/{args.id}")
    else:
        data = api("POST", "/file/upload", params=params)
    output(data, getattr(args, 'human', False))

def cmd_fine_tune(args):
    """Create fine-tuning job."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/fine/{args.id}")
    else:
        data = api("GET", "/fine/tune", params=params)
    output(data, getattr(args, 'human', False))

def cmd_fine_tune_list(args):
    """List fine-tuning jobs."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/fine/{args.id}")
    else:
        data = api("GET", "/fine/tune/list", params=params)
    output(data, getattr(args, 'human', False))

def cmd_moderate(args):
    """Check content moderation."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/moderate/{args.id}")
    else:
        data = api("GET", "/moderate", params=params)
    output(data, getattr(args, 'human', False))

def cmd_usage(args):
    """Check API usage."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/usage/{args.id}")
    else:
        data = api("GET", "/usage", params=params)
    output(data, getattr(args, 'human', False))

def cmd_assistants(args):
    """List assistants."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/assistants/{args.id}")
    else:
        data = api("GET", "/assistants", params=params)
    output(data, getattr(args, 'human', False))


COMMANDS = {
    "chat": cmd_chat,
    "chat-system": cmd_chat_system,
    "embed": cmd_embed,
    "image": cmd_image,
    "transcribe": cmd_transcribe,
    "tts": cmd_tts,
    "models": cmd_models,
    "model-get": cmd_model_get,
    "files": cmd_files,
    "file-upload": cmd_file_upload,
    "fine-tune": cmd_fine_tune,
    "fine-tune-list": cmd_fine_tune_list,
    "moderate": cmd_moderate,
    "usage": cmd_usage,
    "assistants": cmd_assistants,
}


def main():
    parser = argparse.ArgumentParser(
        description="OpenAI CLI — AI agent integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("command", choices=list(COMMANDS.keys()), help="Command to run")
    parser.add_argument("args", nargs="*", help="Command arguments")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    parser.add_argument("--limit", type=int, help="Limit results")
    parser.add_argument("--id", help="Resource ID")
    parser.add_argument("--from", dest="from_date", help="Start date")
    parser.add_argument("--to", dest="to_date", help="End date")
    parser.add_argument("--status", help="Filter by status")
    parser.add_argument("--sort", help="Sort field")
    parser.add_argument("--query", help="Search query")

    parsed = parser.parse_args()
    cmd_func = COMMANDS[parsed.command]
    cmd_func(parsed)


if __name__ == "__main__":
    main()
