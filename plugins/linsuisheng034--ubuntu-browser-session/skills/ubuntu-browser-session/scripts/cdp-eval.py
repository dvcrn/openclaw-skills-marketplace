#!/usr/bin/env python3
"""Minimal CDP evaluation helper using only the Python standard library."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import socket
import struct
import sys
import urllib.error
import urllib.parse
import urllib.request

TIMEOUT_SECONDS = 5
USER_AGENT = "ubuntu-browser-session/cdp-eval"


class CdpError(RuntimeError):
    pass


def http_get_json(url: str) -> object:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def resolve_websocket_url(port: int, target_id: str | None) -> str:
    if target_id:
        targets = http_get_json(f"http://127.0.0.1:{port}/json/list")
        if not isinstance(targets, list):
            raise CdpError("invalid target list response")
        for target in targets:
            if target.get("id") == target_id:
                websocket_url = target.get("webSocketDebuggerUrl")
                if websocket_url:
                    return websocket_url
                break
        raise CdpError("target-id not found")

    version = http_get_json(f"http://127.0.0.1:{port}/json/version")
    websocket_url = version.get("webSocketDebuggerUrl") if isinstance(version, dict) else None
    if not websocket_url:
        raise CdpError("missing webSocketDebuggerUrl")
    return websocket_url


def websocket_key() -> str:
    return base64.b64encode(os.urandom(16)).decode("ascii")


def build_frame(payload: str) -> bytes:
    raw = payload.encode("utf-8")
    mask_key = os.urandom(4)
    length = len(raw)
    header = bytearray([0x81])
    if length < 126:
        header.append(0x80 | length)
    elif length < (1 << 16):
        header.append(0x80 | 126)
        header.extend(struct.pack("!H", length))
    else:
        header.append(0x80 | 127)
        header.extend(struct.pack("!Q", length))
    masked = bytes(byte ^ mask_key[index % 4] for index, byte in enumerate(raw))
    return bytes(header) + mask_key + masked


def recv_exact(sock: socket.socket, size: int) -> bytes:
    chunks = []
    remaining = size
    while remaining > 0:
        chunk = sock.recv(remaining)
        if not chunk:
            raise CdpError("unexpected websocket EOF")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def read_frame(sock: socket.socket) -> str:
    first_two = recv_exact(sock, 2)
    first, second = first_two[0], first_two[1]
    opcode = first & 0x0F
    masked = second & 0x80
    length = second & 0x7F
    if length == 126:
        length = struct.unpack("!H", recv_exact(sock, 2))[0]
    elif length == 127:
        length = struct.unpack("!Q", recv_exact(sock, 8))[0]
    mask_key = recv_exact(sock, 4) if masked else b""
    payload = recv_exact(sock, length)
    if masked:
        payload = bytes(byte ^ mask_key[index % 4] for index, byte in enumerate(payload))
    if opcode == 0x8:
        raise CdpError("websocket closed by peer")
    if opcode == 0x9:
        sock.sendall(bytes([0x8A, 0x00]))
        return read_frame(sock)
    if opcode != 0x1:
        raise CdpError(f"unsupported websocket opcode: {opcode}")
    return payload.decode("utf-8")


def websocket_request(websocket_url: str, message: dict[str, object]) -> dict[str, object]:
    parsed = urllib.parse.urlparse(websocket_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or (443 if parsed.scheme == "wss" else 80)
    if parsed.scheme != "ws":
        raise CdpError("only ws:// CDP endpoints are supported")

    key = websocket_key()
    request_path = parsed.path or "/"
    if parsed.query:
        request_path += f"?{parsed.query}"

    with socket.create_connection((host, port), timeout=TIMEOUT_SECONDS) as sock:
        sock.settimeout(TIMEOUT_SECONDS)
        handshake = (
            f"GET {request_path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        sock.sendall(handshake.encode("utf-8"))
        response = b""
        while b"\r\n\r\n" not in response:
            chunk = sock.recv(4096)
            if not chunk:
                raise CdpError("incomplete websocket handshake")
            response += chunk
        header_blob = response.split(b"\r\n\r\n", 1)[0].decode("utf-8", errors="replace")
        if "101" not in header_blob.splitlines()[0]:
            raise CdpError(f"handshake failed: {header_blob.splitlines()[0]}")
        expected_accept = base64.b64encode(
            hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")).digest()
        ).decode("ascii")
        if f"Sec-WebSocket-Accept: {expected_accept}" not in header_blob:
            raise CdpError("invalid websocket accept header")

        sock.sendall(build_frame(json.dumps(message)))
        while True:
            payload = json.loads(read_frame(sock))
            if payload.get("id") == message["id"]:
                return payload


def evaluate(port: int, target_id: str | None, expression: str) -> dict[str, object]:
    websocket_url = resolve_websocket_url(port, target_id)
    response = websocket_request(
        websocket_url,
        {
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {
                "expression": expression,
                "returnByValue": True,
            },
        },
    )
    if "error" in response:
        raise CdpError(str(response["error"]))
    result = response.get("result", {})
    if "exceptionDetails" in result:
        details = result["exceptionDetails"]
        description = details.get("exception", {}).get("description") or details.get("text") or "evaluation failed"
        raise CdpError(str(description))
    payload = result.get("result", {})
    return payload.get("value") if "value" in payload else payload


def detect_challenge(page_info: dict[str, object]) -> dict[str, object]:
    indicators = []
    haystack = " ".join(
        [
            str(page_info.get("title", "")),
            str(page_info.get("bodySnippet", "")),
            str(page_info.get("htmlSnippet", "")),
        ]
    ).lower()
    for token in [
        "请稍候",
        "just a moment",
        "checking your browser",
        "verify you are human",
        "cf-challenge",
        "challenge-platform",
        "turnstile",
        "captcha",
    ]:
        if token.lower() in haystack:
            indicators.append(token)
    return {
        "hasChallenge": bool(indicators),
        "indicators": indicators,
        "title": page_info.get("title", ""),
        "url": page_info.get("url", ""),
    }


def detect_login_wall(page_info: dict[str, object]) -> dict[str, object]:
    login_hits = []
    combined = " ".join([str(page_info.get("bodySnippet", "")), str(page_info.get("title", ""))]).lower()
    for token in ["sign in", "log in", "登录", "create your account", "sign up"]:
        if token.lower() in combined:
            login_hits.append(token)
    url = str(page_info.get("url", "")).lower()
    for token in ["/login", "/signin", "/auth", "/i/flow/login"]:
        if token in url and token not in login_hits:
            login_hits.append(token)
    return {
        "hasLoginWall": bool(login_hits),
        "loginHits": login_hits,
        "title": page_info.get("title", ""),
        "url": page_info.get("url", ""),
    }


def gather_page_info(port: int, target_id: str | None) -> dict[str, object]:
    expression = """(() => {
      const title = document.title || '';
      const url = location.href || '';
      const bodyText = document.body ? (document.body.innerText || '') : '';
      const html = document.documentElement ? (document.documentElement.outerHTML || '') : '';
      return {
        title,
        url,
        bodySnippet: bodyText.slice(0, 2000),
        htmlSnippet: html.slice(0, 4000)
      };
    })()"""
    value = evaluate(port, target_id, expression)
    if not isinstance(value, dict):
        raise CdpError("page-info did not return an object")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="cdp-eval", description="Evaluate page state over the Chrome DevTools Protocol.")
    parser.add_argument("--port", type=int, required=True, help="CDP HTTP/WebSocket port")
    parser.add_argument("--target-id", help="Specific target id from /json/list")
    parser.add_argument("--check", choices=["challenge", "login-wall", "page-info"])
    parser.add_argument("--eval", dest="expression", help="Arbitrary JavaScript expression for Runtime.evaluate")
    args = parser.parse_args()
    if bool(args.check) == bool(args.expression):
        parser.error("provide exactly one of --check or --eval")
    return args


def main() -> int:
    args = parse_args()
    try:
        if args.expression:
            print(json.dumps(evaluate(args.port, args.target_id, args.expression), ensure_ascii=False))
            return 0

        page_info = gather_page_info(args.port, args.target_id)
        if args.check == "page-info":
            result = {
                "title": page_info.get("title", ""),
                "url": page_info.get("url", ""),
                "bodySnippet": page_info.get("bodySnippet", ""),
            }
        elif args.check == "challenge":
            result = detect_challenge(page_info)
        else:
            result = detect_login_wall(page_info)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (OSError, urllib.error.URLError, socket.timeout) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1
    except CdpError as exc:
        print(json.dumps({"error": str(exc)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
