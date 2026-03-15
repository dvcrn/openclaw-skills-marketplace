"""WebSocket client wrapper (connects to molt-message WebSocket endpoint).

[INPUT]: SDKConfig, DIDIdentity (JWT token)
[OUTPUT]: WsClient class (connect/send/receive/close)
[POS]: Provides WebSocket message channel client wrapper for upper-layer applications and tests.
       send_message auto-generates client_msg_id for idempotent delivery.

[PROTOCOL]:
1. Update this header when logic changes
2. Check the folder's CLAUDE.md after updates
"""

from __future__ import annotations

import asyncio
import json
import logging
import ssl
import uuid
from typing import Any

import websockets
from websockets.asyncio.client import ClientConnection

from utils.client import _resolve_verify
from utils.config import SDKConfig
from utils.identity import DIDIdentity

logger = logging.getLogger(__name__)


class WsClient:
    """molt-message WebSocket client.

    Uses JWT Bearer authentication to connect to the WebSocket endpoint,
    supporting JSON-RPC request sending and push notification receiving.

    Usage::

        async with WsClient(config, identity) as ws:
            # Send a message
            result = await ws.send_message(
                receiver_did="did:wba:...",
                content="Hello!",
            )

            # Receive push notifications
            notification = await ws.receive(timeout=5.0)
    """

    def __init__(
        self,
        config: SDKConfig,
        identity: DIDIdentity,
    ) -> None:
        self._config = config
        self._identity = identity
        self._conn: ClientConnection | None = None
        self._request_id = 0

    async def connect(self) -> None:
        """Establish WebSocket connection.

        Uses JWT token via query parameter for authentication (best compatibility).
        """
        if not self._identity.jwt_token:
            raise ValueError("identity missing jwt_token, call get_jwt_via_wba first")

        # Convert HTTP URL to WebSocket URL
        base_url = self._config.molt_message_ws_url or self._config.molt_message_url
        if base_url.startswith("ws://") or base_url.startswith("wss://"):
            ws_url = base_url.rstrip("/")
        else:
            ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
        url = f"{ws_url}/message/ws?token={self._identity.jwt_token}"

        ssl_context: ssl.SSLContext | bool | None = None
        verify_target = (
            base_url.replace("ws://", "http://").replace("wss://", "https://")
        )
        verify = _resolve_verify(verify_target)
        if url.startswith("wss://"):
            if isinstance(verify, ssl.SSLContext):
                ssl_context = verify
            elif verify is not False:
                ssl_context = True

        self._conn = await websockets.connect(url, ssl=ssl_context)
        logger.info("[WsClient] Connected to %s", url.split("?")[0])

    async def close(self) -> None:
        """Close the connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def __aenter__(self) -> WsClient:
        await self.connect()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    async def send_rpc(
        self,
        method: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a JSON-RPC request and wait for the response.

        Args:
            method: RPC method name.
            params: Method parameters.

        Returns:
            JSON-RPC result field content.

        Raises:
            RuntimeError: Not connected or received an error response.
        """
        if not self._conn:
            raise RuntimeError("WebSocket not connected")

        req_id = self._next_id()
        request: dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": method,
            "id": req_id,
        }
        if params:
            request["params"] = params

        await self._conn.send(json.dumps(request))

        # Wait for the matching response (skip push notifications received in between)
        while True:
            raw = await self._conn.recv()
            data = json.loads(raw)

            # Skip notifications (no id field)
            if "id" not in data:
                continue

            if data.get("id") != req_id:
                continue

            if "error" in data and data["error"]:
                error = data["error"]
                raise RuntimeError(
                    f"JSON-RPC error {error.get('code')}: {error.get('message')}"
                )
            return data.get("result", {})

    async def send_message(
        self,
        content: str,
        receiver_did: str | None = None,
        receiver_id: str | None = None,
        group_did: str | None = None,
        group_id: str | None = None,
        msg_type: str = "text",
        client_msg_id: str | None = None,
        title: str | None = None,
    ) -> dict[str, Any]:
        """Convenience method for sending messages.

        sender_did is automatically injected by the server.
        client_msg_id is auto-generated (uuid4) if not provided, for idempotent delivery.

        Returns:
            Message response dict.
        """
        if client_msg_id is None:
            client_msg_id = str(uuid.uuid4())

        params: dict[str, Any] = {
            "content": content,
            "type": msg_type,
            "client_msg_id": client_msg_id,
        }
        if receiver_did:
            params["receiver_did"] = receiver_did
        if receiver_id:
            params["receiver_id"] = receiver_id
        if group_did:
            params["group_did"] = group_did
        if group_id:
            params["group_id"] = group_id
        if title is not None:
            params["title"] = title
        return await self.send_rpc("send", params)

    async def ping(self) -> bool:
        """Send an application-layer heartbeat and wait for pong."""
        if not self._conn:
            raise RuntimeError("WebSocket not connected")

        await self._conn.send(json.dumps({"jsonrpc": "2.0", "method": "ping"}))
        raw = await self._conn.recv()
        data = json.loads(raw)
        return data.get("method") == "pong"

    async def receive(self, timeout: float = 10.0) -> dict[str, Any] | None:
        """Receive a single message (request response or push notification).

        Args:
            timeout: Timeout in seconds.

        Returns:
            JSON message dict, or None on timeout.
        """
        if not self._conn:
            raise RuntimeError("WebSocket not connected")

        try:
            raw = await asyncio.wait_for(self._conn.recv(), timeout=timeout)
            return json.loads(raw)
        except asyncio.TimeoutError:
            return None

    async def receive_notification(self, timeout: float = 10.0) -> dict[str, Any] | None:
        """Receive a single push notification (skipping request responses).

        Args:
            timeout: Timeout in seconds.

        Returns:
            JSON-RPC Notification dict, or None on timeout.
        """
        if not self._conn:
            raise RuntimeError("WebSocket not connected")

        deadline = asyncio.get_event_loop().time() + timeout
        while True:
            remaining = deadline - asyncio.get_event_loop().time()
            if remaining <= 0:
                return None
            try:
                raw = await asyncio.wait_for(self._conn.recv(), timeout=remaining)
                data = json.loads(raw)
                # Notifications have no id field
                if "id" not in data:
                    return data
            except asyncio.TimeoutError:
                return None


__all__ = ["WsClient"]
