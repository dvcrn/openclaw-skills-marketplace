#!/usr/bin/env python3
"""AuraShot Aesthetics API skill client."""
import argparse
import json
import mimetypes
import os
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Optional
from urllib import error, parse, request

DEFAULT_BASE_URL = "https://www.aurashot.art"
SIGNUP_URL = "https://www.aurashot.art/login"
KEYS_URL = "https://www.aurashot.art/studio?tab=keys"

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def resolve_key() -> str:
    for name in ("AURASHOT_API_KEY", "AURASHOT_STUDIO_KEY"):
        value = os.environ.get(name, "").strip()
        if value:
            return value

    print(
        json.dumps(
            {
                "error": "Missing AuraShot API key.",
                "message": "Set AURASHOT_API_KEY or AURASHOT_STUDIO_KEY before running this skill.",
                "signupUrl": SIGNUP_URL,
                "keysUrl": KEYS_URL,
            },
            ensure_ascii=False,
            indent=2,
        ),
        file=sys.stderr,
    )
    raise SystemExit(2)


def base_url_from_args(args: argparse.Namespace) -> str:
    return (args.base_url or os.environ.get("AURASHOT_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")


# ---------------------------------------------------------------------------
# File upload
# ---------------------------------------------------------------------------

def is_remote_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def to_local_path(value: str) -> Path:
    if value.startswith("file://"):
        return Path(parse.unquote(parse.urlparse(value).path)).expanduser()
    return Path(value).expanduser()


def encode_multipart(field_name: str, file_path: Path) -> tuple:
    boundary = f"----AuraShot{uuid.uuid4().hex}"
    filename = file_path.name
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    body = b"".join([
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'.encode(),
        f"Content-Type: {content_type}\r\n\r\n".encode(),
        file_path.read_bytes(),
        b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ])
    return body, boundary


def upload_to_weshop(file_path: Path, api_key: str) -> str:
    """Upload a local image via AuraShot and return the public URL."""
    body, boundary = encode_multipart("image", file_path)
    req = request.Request(
        f"{DEFAULT_BASE_URL}/api/uploads",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "ignore")
        raise SystemExit(json.dumps(
            {"error": "Image upload failed.", "status": exc.code, "detail": detail, "path": str(file_path)},
            ensure_ascii=False, indent=2,
        ))
    except error.URLError as exc:
        raise SystemExit(json.dumps(
            {"error": "Image upload failed.", "detail": str(exc.reason), "path": str(file_path)},
            ensure_ascii=False, indent=2,
        ))

    result = json.loads(raw)
    url = result.get("url")
    if not isinstance(url, str) or not url.strip():
        raise SystemExit(json.dumps(
            {"error": "Image upload failed.", "detail": "No URL in response.", "raw": result},
            ensure_ascii=False, indent=2,
        ))
    return url


def resolve_image(value: Optional[str], api_key: str, field: str) -> Optional[str]:
    if not value:
        return None
    v = value.strip()
    if is_remote_url(v):
        return v
    p = to_local_path(v)
    if p.exists() and p.is_file():
        print(f"[aurashot] Uploading local file for {field}: {p}", file=sys.stderr)
        return upload_to_weshop(p, api_key)
    raise SystemExit(json.dumps(
        {"error": f"Invalid {field}.", "message": "Use a public URL or an existing local file path.", "value": v},
        ensure_ascii=False, indent=2,
    ))


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def make_request(method: str, url: str, api_key: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = request.Request(
        url,
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method=method,
    )
    try:
        with request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "ignore")
        raise SystemExit(json.dumps({"error": "AuraShot request failed.", "status": exc.code, "detail": detail}, ensure_ascii=False, indent=2))
    except error.URLError as exc:
        raise SystemExit(json.dumps({"error": "AuraShot request failed.", "detail": str(exc.reason)}, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_generate(args: argparse.Namespace) -> None:
    api_key = resolve_key()
    base_url = base_url_from_args(args)

    if args.workflow == "virtual_try_on":
        for flag, name in [("--product-image", "product_image"), ("--model-image", "model_image"), ("--scene-image", "scene_image")]:
            if not getattr(args, name, None):
                raise SystemExit(json.dumps({"error": f"virtual_try_on requires {flag}."}, ensure_ascii=False, indent=2))

        description_type = "custom" if args.description else "auto"
        payload: Dict[str, Any] = {
            "workflow": "virtual_try_on",
            "waitForResult": args.wait,
            "input": {
                "productImage": resolve_image(args.product_image, api_key, "productImage"),
                "modelImage": resolve_image(args.model_image, api_key, "modelImage"),
                "sceneImage": resolve_image(args.scene_image, api_key, "sceneImage"),
                "generateVersion": args.version or "weshopFlash",
                "descriptionType": description_type,
                **({"textDescription": args.description} if args.description else {}),
            },
        }

    else:  # pose_change
        if not args.original_image:
            raise SystemExit(json.dumps({"error": "pose_change requires --original-image."}, ensure_ascii=False, indent=2))
        if not args.description:
            raise SystemExit(json.dumps({"error": "pose_change requires --description."}, ensure_ascii=False, indent=2))

        payload = {
            "workflow": "pose_change",
            "waitForResult": args.wait,
            "input": {
                "originalImage": resolve_image(args.original_image, api_key, "originalImage"),
                "generateVersion": args.version or "lite",
                "textDescription": args.description,
            },
        }

    result = make_request("POST", f"{base_url}/api/aesthetic/generate", api_key, payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_query(args: argparse.Namespace) -> None:
    api_key = resolve_key()
    base_url = base_url_from_args(args)

    if not args.execution_id and not args.task_id:
        raise SystemExit(json.dumps({"error": "query requires --execution-id or --task-id."}, ensure_ascii=False, indent=2))

    payload = {
        "workflow": args.workflow,
        **({"executionId": args.execution_id} if args.execution_id else {}),
        **({"taskId": args.task_id} if args.task_id else {}),
    }
    result = make_request("POST", f"{base_url}/api/aesthetic/query", api_key, payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AuraShot Aesthetics API skill client")
    parser.add_argument("--base-url", dest="base_url", default=None)
    subs = parser.add_subparsers(dest="command", required=True)

    gen = subs.add_parser("generate", help="Submit a workflow job")
    gen.add_argument("--workflow", choices=["virtual_try_on", "pose_change"], required=True)
    gen.add_argument("--product-image", dest="product_image")
    gen.add_argument("--model-image", dest="model_image")
    gen.add_argument("--scene-image", dest="scene_image")
    gen.add_argument("--original-image", dest="original_image")
    gen.add_argument("--description", dest="description")
    gen.add_argument("--version", dest="version")
    gen.add_argument("--wait", action="store_true", help="Block until job completes")
    gen.set_defaults(func=cmd_generate)

    qry = subs.add_parser("query", help="Poll a submitted job")
    qry.add_argument("--workflow", choices=["virtual_try_on", "pose_change"], required=True)
    qry.add_argument("--execution-id", dest="execution_id")
    qry.add_argument("--task-id", dest="task_id")
    qry.set_defaults(func=cmd_query)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
