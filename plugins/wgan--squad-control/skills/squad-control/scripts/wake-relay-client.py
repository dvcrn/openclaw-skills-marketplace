#!/usr/bin/env python3
"""Minimal stdlib WebSocket client for Squad Control wake relay."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import secrets
import select
import socket
import ssl
import struct
import subprocess
import sys
import time
from urllib.parse import urlparse


OPCODE_TEXT = 0x1
OPCODE_CLOSE = 0x8
OPCODE_PING = 0x9
OPCODE_PONG = 0xA
HANDOFF_EXIT_CODE = 10


def log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def read_exact(sock: socket.socket, length: int) -> bytes:
    chunks: list[bytes] = []
    remaining = length
    while remaining > 0:
        chunk = sock.recv(remaining)
        if not chunk:
            raise ConnectionError("Wake relay connection closed unexpectedly")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def send_frame(sock: socket.socket, opcode: int, payload: bytes = b"") -> None:
    first_byte = 0x80 | opcode
    payload_length = len(payload)
    mask_key = os.urandom(4)

    if payload_length < 126:
        header = bytes([first_byte, 0x80 | payload_length])
    elif payload_length < 65536:
        header = bytes([first_byte, 0x80 | 126]) + struct.pack("!H", payload_length)
    else:
        header = bytes([first_byte, 0x80 | 127]) + struct.pack("!Q", payload_length)

    masked = bytes(byte ^ mask_key[index % 4] for index, byte in enumerate(payload))
    sock.sendall(header + mask_key + masked)


def recv_frame(sock: socket.socket) -> tuple[int, bytes]:
    header = read_exact(sock, 2)
    opcode = header[0] & 0x0F
    masked = bool(header[1] & 0x80)
    payload_length = header[1] & 0x7F

    if payload_length == 126:
        payload_length = struct.unpack("!H", read_exact(sock, 2))[0]
    elif payload_length == 127:
        payload_length = struct.unpack("!Q", read_exact(sock, 8))[0]

    mask_key = read_exact(sock, 4) if masked else b""
    payload = read_exact(sock, payload_length)
    if masked:
        payload = bytes(
            byte ^ mask_key[index % 4] for index, byte in enumerate(payload)
        )

    return opcode, payload


def connect_websocket(relay_url: str, token: str, connect_timeout_sec: int) -> socket.socket:
    parsed = urlparse(relay_url)
    scheme = parsed.scheme.lower()
    if scheme not in {"ws", "wss"}:
        raise ValueError(f"Unsupported relay scheme: {parsed.scheme}")

    host = parsed.hostname
    if not host:
        raise ValueError("Wake relay URL is missing a host")

    port = parsed.port or (443 if scheme == "wss" else 80)
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"

    raw_sock = socket.create_connection((host, port), timeout=connect_timeout_sec)
    if scheme == "wss":
        context = ssl.create_default_context()
        sock = context.wrap_socket(raw_sock, server_hostname=host)
    else:
        sock = raw_sock
    sock.setblocking(True)

    websocket_key = base64.b64encode(secrets.token_bytes(16)).decode("ascii")
    request_lines = [
        f"GET {path} HTTP/1.1",
        f"Host: {host}:{port}" if parsed.port else f"Host: {host}",
        "Upgrade: websocket",
        "Connection: Upgrade",
        f"Authorization: Bearer {token}",
        "Sec-WebSocket-Version: 13",
        f"Sec-WebSocket-Key: {websocket_key}",
        "",
        "",
    ]
    sock.sendall("\r\n".join(request_lines).encode("utf-8"))

    response = bytearray()
    while b"\r\n\r\n" not in response:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("Wake relay handshake failed")
        response.extend(chunk)

    header_blob = bytes(response).split(b"\r\n\r\n", 1)[0].decode("utf-8", "replace")
    lines = header_blob.split("\r\n")
    status_line = lines[0]
    if " 101 " not in status_line:
        raise ConnectionError(f"Wake relay rejected websocket handshake: {status_line}")

    headers = {}
    for line in lines[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        headers[key.strip().lower()] = value.strip()

    expected_accept = base64.b64encode(
        hashlib.sha1(
            f"{websocket_key}258EAFA5-E914-47DA-95CA-C5AB0DC85B11".encode("utf-8")
        ).digest()
    ).decode("ascii")
    if headers.get("sec-websocket-accept") != expected_accept:
        raise ConnectionError("Wake relay handshake returned an invalid accept key")

    return sock


def run_poll_script(poll_script: str) -> None:
    result = subprocess.run([poll_script], check=False)
    if result.returncode != 0:
        log("WARN: wake-triggered poll failed; continuing listener loop")


def handle_message(poll_script: str, raw_payload: bytes, exit_after_wake: bool) -> int:
    try:
        payload = json.loads(raw_payload.decode("utf-8"))
    except json.JSONDecodeError:
        log("WARN: wake relay sent invalid JSON")
        return 0

    message_type = payload.get("type")
    if message_type == "wake":
        log(f"WAKE_EVENT: {json.dumps(payload, separators=(',', ':'))}")
        if exit_after_wake:
            log("WAKE_LISTENER_HANDOFF")
            return HANDOFF_EXIT_CODE
        run_poll_script(poll_script)
    elif message_type == "connected":
        log(
            f"WAKE_LISTENER_CONNECTED: "
            f"{json.dumps(payload, separators=(',', ':'))}"
        )
    elif message_type == "error":
        log(f"WARN: wake relay error: {payload.get('error', 'unknown')}")
    return 0


def run_listener(args: argparse.Namespace) -> int:
    sock = connect_websocket(args.relay_url, args.token, args.connect_timeout_sec)
    log(f"WAKE_RELAY_SESSION: listenerId={args.listener_id}")

    next_heartbeat_at = time.monotonic() + args.heartbeat_sec

    try:
        while time.time() < args.deadline_epoch:
            timeout = max(
                0.0,
                min(
                    args.deadline_epoch - time.time(),
                    next_heartbeat_at - time.monotonic(),
                ),
            )
            readable, _, _ = select.select([sock], [], [], timeout)
            if readable:
                opcode, payload = recv_frame(sock)
                if opcode == OPCODE_TEXT:
                    message_result = handle_message(
                        args.poll_script,
                        payload,
                        bool(args.exit_after_wake),
                    )
                    if message_result == HANDOFF_EXIT_CODE:
                        return HANDOFF_EXIT_CODE
                elif opcode == OPCODE_PING:
                    send_frame(sock, OPCODE_PONG, payload)
                elif opcode == OPCODE_CLOSE:
                    send_frame(sock, OPCODE_CLOSE)
                    return 0

            if time.monotonic() >= next_heartbeat_at and time.time() < args.deadline_epoch:
                send_frame(
                    sock,
                    OPCODE_TEXT,
                    json.dumps({"type": "heartbeat"}).encode("utf-8"),
                )
                next_heartbeat_at = time.monotonic() + args.heartbeat_sec
    finally:
        try:
            send_frame(sock, OPCODE_CLOSE)
        except OSError:
            pass
        sock.close()

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--relay-url", required=True)
    parser.add_argument("--token", required=True)
    parser.add_argument("--listener-id", required=True)
    parser.add_argument("--poll-script", required=True)
    parser.add_argument("--deadline-epoch", required=True, type=int)
    parser.add_argument("--heartbeat-sec", type=int, default=30)
    parser.add_argument("--connect-timeout-sec", type=int, default=10)
    parser.add_argument("--exit-after-wake", type=int, default=0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        return run_listener(args)
    except Exception as exc:  # pragma: no cover - shell wrapper handles fallback
        log(f"WARN: wake relay client failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
