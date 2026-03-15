"""Check inbox, view private/group history, and mark messages as read.

Usage:
    # View inbox
    uv run python scripts/check_inbox.py

    # Limit result count
    uv run python scripts/check_inbox.py --limit 5

    # View chat history with a specific DID
    uv run python scripts/check_inbox.py --history "did:wba:localhost:user:abc123"

    # View only group messages from the mixed inbox feed
    uv run python scripts/check_inbox.py --scope group

    # View one group's message history directly
    uv run python scripts/check_inbox.py --group-id grp_123 --limit 50

    # Mark messages as read
    uv run python scripts/check_inbox.py --mark-read msg_id_1 msg_id_2

[INPUT]: SDK (RPC calls), credential_store (load identity credentials), local_store,
         E2EE runtime helpers, group RPC history reads, outbox tracking,
         logging_config
[OUTPUT]: Inbox message list / private-or-group history / mark-read result,
          with immediate private E2EE protocol processing, plaintext decryption
          when possible, local group snapshot persistence, and automatic local
          incremental cursors for group history reads
[POS]: Unified message receiving and history script for private chats and
       discovery-group reads

[PROTOCOL]:
1. Update this header when logic changes
2. Check the folder's CLAUDE.md after updating
"""

import argparse
import asyncio
import json
import logging
import sys
from typing import Any

from utils import (
    SDKConfig,
    E2eeClient,
    create_molt_message_client,
    create_user_service_client,
    authenticated_rpc_call,
    resolve_to_did,
)
from utils.logging_config import configure_logging
from credential_store import create_authenticator, load_identity
from e2ee_outbox import record_remote_failure
from e2ee_store import load_e2ee_state, save_e2ee_state
from utils.e2ee import (
    SUPPORTED_E2EE_VERSION,
    build_e2ee_error_content,
    build_e2ee_error_message,
)
import local_store
from manage_group import _persist_group_messages

logger = logging.getLogger(__name__)


MESSAGE_RPC = "/message/rpc"
GROUP_RPC = "/group/rpc"
_E2EE_MSG_TYPES = {"e2ee_init", "e2ee_ack", "e2ee_msg", "e2ee_rekey", "e2ee_error"}
_E2EE_SESSION_SETUP_TYPES = {"e2ee_init", "e2ee_rekey"}
_E2EE_TYPE_ORDER = {"e2ee_init": 0, "e2ee_ack": 1, "e2ee_rekey": 2, "e2ee_msg": 3, "e2ee_error": 4}
_E2EE_USER_NOTICE = "This is an encrypted message."
_MESSAGE_SCOPES = {"all", "direct", "group"}


def _message_time_value(message: dict[str, Any]) -> str:
    """Return a sortable timestamp string for one message."""
    timestamp = message.get("sent_at") or message.get("created_at")
    return timestamp if isinstance(timestamp, str) else ""


def _message_sort_key(message: dict[str, Any]) -> tuple[Any, ...]:
    """Build a stable E2EE inbox ordering key with server_seq priority inside a sender stream."""
    sender_did_raw = message.get("sender_did")
    sender_did = sender_did_raw if isinstance(sender_did_raw, str) else ""
    server_seq = message.get("server_seq")
    has_server_seq = 0 if isinstance(server_seq, int) else 1
    server_seq_value = server_seq if isinstance(server_seq, int) else 0
    return (
        sender_did,
        has_server_seq,
        server_seq_value,
        _message_time_value(message),
        _E2EE_TYPE_ORDER.get(message.get("type"), 99),
    )


def _decorate_user_visible_e2ee_message(
    message: dict[str, Any],
    *,
    original_type: str,
    plaintext: str,
) -> dict[str, Any]:
    """Decorate a decrypted E2EE message for user-facing output."""
    rendered = dict(message)
    rendered["type"] = original_type
    rendered["content"] = plaintext
    rendered["_e2ee"] = True
    rendered["_e2ee_notice"] = _E2EE_USER_NOTICE
    rendered.pop("title", None)
    return rendered


def _strip_hidden_user_fields(message: dict[str, Any]) -> dict[str, Any]:
    """Remove fields intentionally hidden from user-facing output."""
    rendered = dict(message)
    rendered.pop("title", None)
    return rendered


def _filter_messages_by_scope(
    messages: list[dict[str, Any]],
    scope: str,
) -> list[dict[str, Any]]:
    """Filter mixed inbox messages by the requested scope."""
    if scope not in _MESSAGE_SCOPES or scope == "all":
        return messages
    if scope == "group":
        return [msg for msg in messages if msg.get("group_id")]
    return [msg for msg in messages if not msg.get("group_id")]


def _parse_group_history_target(target: str) -> str | None:
    """Parse a group-prefixed history target into a group ID."""
    prefix = "group:"
    if not isinstance(target, str) or not target.startswith(prefix):
        return None
    group_id = target[len(prefix):].strip()
    return group_id or None


def _resolve_group_since_seq(
    *,
    owner_did: str,
    group_id: str,
    explicit_since_seq: int | None,
) -> tuple[int | None, str]:
    """Resolve the incremental cursor for one group history read."""
    if explicit_since_seq is not None:
        return explicit_since_seq, "argument"

    conn = local_store.get_connection()
    try:
        local_store.ensure_schema(conn)
        group_row = conn.execute(
            """
            SELECT last_synced_seq
            FROM groups
            WHERE owner_did = ? AND group_id = ?
            """,
            (owner_did, group_id),
        ).fetchone()
        if group_row is not None and isinstance(group_row["last_synced_seq"], int):
            return group_row["last_synced_seq"], "group_snapshot"

        message_row = conn.execute(
            """
            SELECT MAX(server_seq) AS max_server_seq
            FROM messages
            WHERE owner_did = ? AND group_id = ? AND server_seq IS NOT NULL
            """,
            (owner_did, group_id),
        ).fetchone()
        max_server_seq = message_row["max_server_seq"] if message_row is not None else None
        if isinstance(max_server_seq, int):
            return max_server_seq, "message_cache"
        return None, "none"
    finally:
        conn.close()


def _load_or_create_e2ee_client(local_did: str, credential_name: str) -> E2eeClient:
    """Load persisted E2EE state or create a fresh client."""
    cred = load_identity(credential_name)
    signing_pem: str | None = None
    x25519_pem: str | None = None
    if cred is not None:
        signing_pem = cred.get("e2ee_signing_private_pem")
        x25519_pem = cred.get("e2ee_agreement_private_pem")

    state = load_e2ee_state(credential_name)
    if state is not None and state.get("local_did") == local_did:
        if signing_pem is not None:
            state["signing_pem"] = signing_pem
        if x25519_pem is not None:
            state["x25519_pem"] = x25519_pem
        return E2eeClient.from_state(state)

    return E2eeClient(local_did, signing_pem=signing_pem, x25519_pem=x25519_pem)


async def _send_msg(http_client, sender_did, receiver_did, msg_type, content, *, auth, credential_name="default"):
    """Send an E2EE protocol/error message."""
    if isinstance(content, dict):
        content = json.dumps(content)
    return await authenticated_rpc_call(
        http_client,
        MESSAGE_RPC,
        "send",
        params={
            "sender_did": sender_did,
            "receiver_did": receiver_did,
            "content": content,
            "type": msg_type,
        },
        auth=auth,
        credential_name=credential_name,
    )


async def _group_rpc_call(
    *,
    credential_name: str,
    method: str,
    params: dict[str, Any],
    auth: Any,
) -> dict[str, Any]:
    """Run one authenticated discovery-group RPC call."""
    async with create_user_service_client(SDKConfig()) as client:
        return await authenticated_rpc_call(
            client,
            GROUP_RPC,
            method,
            params,
            auth=auth,
            credential_name=credential_name,
        )


def _classify_decrypt_error(exc: BaseException) -> tuple[str, str]:
    """Map decryption failures to e2ee_error code and retry hint."""
    msg = str(exc).lower()
    if "unsupported_version" in msg:
        return "unsupported_version", "drop"
    if "session" in msg and ("not found" in msg or "find session" in msg):
        return "session_not_found", "rekey_then_resend"
    if "expired" in msg:
        return "session_expired", "rekey_then_resend"
    if "seq" in msg or "sequence" in msg:
        return "invalid_seq", "rekey_then_resend"
    return "decryption_failed", "resend"


async def _auto_process_e2ee_messages(
    messages: list[dict[str, Any]],
    *,
    local_did: str,
    auth: Any,
    credential_name: str,
) -> tuple[list[dict[str, Any]], list[str], E2eeClient]:
    """Immediately process E2EE protocol messages and decrypt plaintext when possible."""
    e2ee_client = _load_or_create_e2ee_client(local_did, credential_name)
    processed_ids: list[str] = []
    rendered_messages: list[dict[str, Any]] = []

    async with create_molt_message_client(SDKConfig()) as client:
        for msg in messages:
            msg_type = msg.get("type", "")
            sender_did = msg.get("sender_did", "")
            if msg_type not in _E2EE_MSG_TYPES:
                rendered_messages.append(_strip_hidden_user_fields(msg))
                continue

            try:
                content = json.loads(msg.get("content", ""))
            except (TypeError, json.JSONDecodeError):
                rendered_messages.append(_strip_hidden_user_fields(msg))
                continue

            if msg_type == "e2ee_msg":
                if sender_did == local_did:
                    rendered = _render_local_outgoing_e2ee_message(
                        credential_name,
                        msg,
                    )
                    rendered_messages.append(rendered or _strip_hidden_user_fields(msg))
                    continue
                try:
                    original_type, plaintext = e2ee_client.decrypt_message(content)
                    rendered = _decorate_user_visible_e2ee_message(
                        msg,
                        original_type=original_type,
                        plaintext=plaintext,
                    )
                    rendered_messages.append(rendered)
                    processed_ids.append(msg["id"])
                except Exception as exc:
                    error_code, retry_hint = _classify_decrypt_error(exc)
                    error_content = build_e2ee_error_content(
                        error_code=error_code,
                        session_id=content.get("session_id"),
                        failed_msg_id=msg.get("id"),
                        failed_server_seq=msg.get("server_seq"),
                        retry_hint=retry_hint,
                        required_e2ee_version=SUPPORTED_E2EE_VERSION if error_code == "unsupported_version" else None,
                        message=build_e2ee_error_message(
                            error_code,
                            required_e2ee_version=SUPPORTED_E2EE_VERSION if error_code == "unsupported_version" else None,
                            detail=str(exc),
                        ),
                    )
                    await _send_msg(
                        client, local_did, sender_did, "e2ee_error", error_content,
                        auth=auth, credential_name=credential_name,
                    )
                continue

            if msg_type == "e2ee_error":
                if sender_did == local_did:
                    continue
                record_remote_failure(
                    credential_name=credential_name,
                    peer_did=sender_did,
                    content=content,
                )

            if sender_did == local_did:
                continue

            responses = await e2ee_client.process_e2ee_message(msg_type, content)
            for resp_type, resp_content in responses:
                await _send_msg(
                    client, local_did, sender_did, resp_type, resp_content,
                    auth=auth, credential_name=credential_name,
                )

            if msg_type in _E2EE_SESSION_SETUP_TYPES:
                if e2ee_client.has_session_id(content.get("session_id")):
                    processed_ids.append(msg["id"])
            else:
                processed_ids.append(msg["id"])

    save_e2ee_state(e2ee_client.export_state(), credential_name)
    return rendered_messages, processed_ids, e2ee_client


def _render_local_outgoing_e2ee_message(
    credential_name: str,
    message: dict[str, Any],
) -> dict[str, Any] | None:
    """Replace an outgoing encrypted history item with local plaintext when available."""
    msg_id = message.get("id") or message.get("msg_id")
    if not msg_id:
        return None
    credential = load_identity(credential_name)
    try:
        conn = local_store.get_connection()
        local_store.ensure_schema(conn)
        stored = local_store.get_message_by_id(
            conn,
            msg_id=msg_id,
            owner_did=credential.get("did") if credential else None,
            credential_name=credential_name,
        )
        conn.close()
    except Exception:
        logger.debug("Failed to load local plaintext for outgoing E2EE message", exc_info=True)
        return None

    if stored is None or not stored.get("is_e2ee"):
        return None

    return _decorate_user_visible_e2ee_message(
        message,
        original_type=stored.get("content_type", message.get("type", "text")),
        plaintext=stored.get("content", message.get("content", "")),
    )


async def check_inbox(
    credential_name: str = "default",
    limit: int = 20,
    scope: str = "all",
) -> None:
    """View inbox and immediately process private E2EE messages when possible."""
    config = SDKConfig()
    auth_result = create_authenticator(credential_name, config)
    if auth_result is None:
        print(f"Credential '{credential_name}' unavailable; please create an identity first")
        sys.exit(1)

    auth, data = auth_result
    async with create_molt_message_client(config) as client:
        inbox = await authenticated_rpc_call(
            client,
            MESSAGE_RPC,
            "get_inbox",
            params={"user_did": data["did"], "limit": limit},
            auth=auth,
            credential_name=credential_name,
        )

        # Store fetched messages locally (offline backfill)
        _store_inbox_messages(credential_name, data["did"], inbox)

        messages = inbox.get("messages", [])
        messages.sort(key=_message_sort_key)
        rendered_messages, processed_ids, _ = await _auto_process_e2ee_messages(
            messages,
            local_did=data["did"],
            auth=auth,
            credential_name=credential_name,
        )
        rendered_messages = _filter_messages_by_scope(rendered_messages, scope)
        inbox["messages"] = rendered_messages
        inbox["total"] = len(rendered_messages)
        inbox["scope"] = scope

        if processed_ids:
            await authenticated_rpc_call(
                client,
                MESSAGE_RPC,
                "mark_read",
                params={"user_did": data["did"], "message_ids": processed_ids},
                auth=auth,
                credential_name=credential_name,
            )

        print(json.dumps(inbox, indent=2, ensure_ascii=False))


async def get_history(
    peer_did: str,
    credential_name: str = "default",
    limit: int = 50,
) -> None:
    """View chat history with a specific DID and immediately render E2EE plaintext when possible."""
    config = SDKConfig()
    auth_result = create_authenticator(credential_name, config)
    if auth_result is None:
        print(f"Credential '{credential_name}' unavailable; please create an identity first")
        sys.exit(1)

    auth, data = auth_result
    async with create_molt_message_client(config) as client:
        history = await authenticated_rpc_call(
            client,
            MESSAGE_RPC,
            "get_history",
            params={
                "user_did": data["did"],
                "peer_did": peer_did,
                "limit": limit,
            },
            auth=auth,
            credential_name=credential_name,
        )

        # Store fetched messages locally (offline backfill)
        _store_history_messages(credential_name, data["did"], peer_did, history)

        messages = history.get("messages", [])
        messages.sort(key=_message_sort_key)
        rendered_messages, _, _ = await _auto_process_e2ee_messages(
            messages,
            local_did=data["did"],
            auth=auth,
            credential_name=credential_name,
        )
        history["messages"] = rendered_messages
        history["total"] = len(rendered_messages)

        print(json.dumps(history, indent=2, ensure_ascii=False))


async def get_group_history(
    group_id: str,
    credential_name: str = "default",
    limit: int = 50,
    since_seq: int | None = None,
) -> None:
    """View one discovery group's message history."""
    config = SDKConfig()
    auth_result = create_authenticator(credential_name, config)
    if auth_result is None:
        print(f"Credential '{credential_name}' unavailable; please create an identity first")
        sys.exit(1)

    auth, data = auth_result
    resolved_since_seq, cursor_source = _resolve_group_since_seq(
        owner_did=str(data["did"]),
        group_id=group_id,
        explicit_since_seq=since_seq,
    )
    params: dict[str, Any] = {"group_id": group_id, "limit": limit}
    if resolved_since_seq is not None:
        params["since_seq"] = resolved_since_seq

    history = await _group_rpc_call(
        credential_name=credential_name,
        method="list_messages",
        params=params,
        auth=auth,
    )
    _persist_group_messages(
        credential_name=credential_name,
        identity_data=data,
        group_id=group_id,
        payload=history,
    )
    history["messages"] = [
        _strip_hidden_user_fields(message)
        for message in history.get("messages", [])
    ]
    history["total"] = len(history.get("messages", []))
    history["group_id"] = group_id
    history["since_seq"] = resolved_since_seq
    history["cursor_source"] = cursor_source
    print(json.dumps(history, indent=2, ensure_ascii=False))


async def mark_read(
    message_ids: list[str],
    credential_name: str = "default",
) -> None:
    """Mark messages as read."""
    config = SDKConfig()
    auth_result = create_authenticator(credential_name, config)
    if auth_result is None:
        print(f"Credential '{credential_name}' unavailable; please create an identity first")
        sys.exit(1)

    auth, data = auth_result
    async with create_molt_message_client(config) as client:
        result = await authenticated_rpc_call(
            client,
            MESSAGE_RPC,
            "mark_read",
            params={
                "user_did": data["did"],
                "message_ids": message_ids,
            },
            auth=auth,
            credential_name=credential_name,
        )
        print("Marked as read successfully:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


def _store_inbox_messages(
    credential_name: str, my_did: str, inbox: Any,
) -> None:
    """Store inbox messages locally (best-effort, non-critical)."""
    try:
        messages = inbox if isinstance(inbox, list) else inbox.get("messages", [])
        if not messages:
            return
        conn = local_store.get_connection()
        local_store.ensure_schema(conn)
        batch = []
        for msg in messages:
            sender_did = msg.get("sender_did", "")
            batch.append({
                "msg_id": msg.get("id", msg.get("msg_id", "")),
                "thread_id": local_store.make_thread_id(
                    my_did, peer_did=sender_did, group_id=msg.get("group_id"),
                ),
                "direction": 0,
                "sender_did": sender_did,
                "receiver_did": msg.get("receiver_did"),
                "group_id": msg.get("group_id"),
                "group_did": msg.get("group_did"),
                "content_type": msg.get("type", "text"),
                "content": str(msg.get("content", "")),
                "title": msg.get("title"),
                "server_seq": msg.get("server_seq"),
                "sent_at": msg.get("sent_at") or msg.get("created_at"),
                "sender_name": msg.get("sender_name"),
                "metadata": (
                    json.dumps(
                        {"system_event": msg.get("system_event")},
                        ensure_ascii=False,
                    )
                    if msg.get("system_event") is not None
                    else None
                ),
            })
        local_store.store_messages_batch(
            conn,
            batch,
            owner_did=my_did,
            credential_name=credential_name,
        )
        group_snapshots: dict[str, Any] = {}
        for msg in messages:
            group_id = str(msg.get("group_id") or "")
            if not group_id:
                continue
            current = group_snapshots.get(group_id)
            current_seq = current.get("server_seq") if isinstance(current, dict) else None
            next_seq = msg.get("server_seq")
            if current is not None and isinstance(current_seq, int) and isinstance(next_seq, int):
                if next_seq <= current_seq:
                    continue
            group_snapshots[group_id] = msg

        for group_id, msg in group_snapshots.items():
            local_store.upsert_group(
                conn,
                owner_did=my_did,
                group_id=str(group_id),
                group_did=msg.get("group_did"),
                name=msg.get("group_name"),
                membership_status="active",
                last_synced_seq=msg.get("server_seq"),
                last_message_at=msg.get("sent_at") or msg.get("created_at"),
                credential_name=credential_name,
            )
        for msg in messages:
            group_id = str(msg.get("group_id") or "")
            system_event = msg.get("system_event")
            if not group_id or not isinstance(system_event, dict):
                continue
            local_store.sync_group_member_from_system_event(
                conn,
                owner_did=my_did,
                group_id=group_id,
                system_event=system_event,
                credential_name=credential_name,
            )
        # Record senders in contacts
        seen_dids: set[str] = set()
        for msg in messages:
            s = msg.get("sender_did", "")
            if s and s not in seen_dids:
                seen_dids.add(s)
                local_store.upsert_contact(
                    conn,
                    owner_did=my_did,
                    did=s,
                    name=msg.get("sender_name"),
                )
        conn.close()
    except Exception:
        logger.debug("Failed to store inbox messages locally", exc_info=True)


def _store_history_messages(
    credential_name: str, my_did: str, peer_did: str, history: Any,
) -> None:
    """Store chat history messages locally (best-effort, non-critical)."""
    try:
        messages = history if isinstance(history, list) else history.get("messages", [])
        if not messages:
            return
        conn = local_store.get_connection()
        local_store.ensure_schema(conn)
        batch = []
        for msg in messages:
            sender_did = msg.get("sender_did", "")
            is_outgoing = sender_did == my_did
            batch.append({
                "msg_id": msg.get("id", msg.get("msg_id", "")),
                "thread_id": local_store.make_thread_id(
                    my_did, peer_did=peer_did, group_id=msg.get("group_id"),
                ),
                "direction": 1 if is_outgoing else 0,
                "sender_did": sender_did,
                "receiver_did": msg.get("receiver_did"),
                "group_id": msg.get("group_id"),
                "group_did": msg.get("group_did"),
                "content_type": msg.get("type", "text"),
                "content": str(msg.get("content", "")),
                "title": msg.get("title"),
                "server_seq": msg.get("server_seq"),
                "sent_at": msg.get("sent_at") or msg.get("created_at"),
                "sender_name": msg.get("sender_name"),
            })
        local_store.store_messages_batch(
            conn,
            batch,
            owner_did=my_did,
            credential_name=credential_name,
        )
        # Record senders in contacts
        seen_dids: set[str] = set()
        for msg in messages:
            s = msg.get("sender_did", "")
            if s and s not in seen_dids:
                seen_dids.add(s)
                local_store.upsert_contact(
                    conn,
                    owner_did=my_did,
                    did=s,
                    name=msg.get("sender_name"),
                )
        conn.close()
    except Exception:
        logger.debug("Failed to store history messages locally", exc_info=True)


def main() -> None:
    configure_logging(level=logging.INFO, console_level=None, mirror_stdio=True)
    logger.info("check_inbox CLI started")

    parser = argparse.ArgumentParser(description="Check inbox and manage messages")
    action = parser.add_mutually_exclusive_group()
    action.add_argument(
        "--history",
        type=str,
        help="View chat history with a specific DID/handle, or group:GROUP_ID",
    )
    action.add_argument("--group-id", type=str, help="View one group's message history")
    action.add_argument(
        "--mark-read",
        nargs="+",
        type=str,
        help="Mark specified message IDs as read",
    )
    parser.add_argument(
        "--scope",
        choices=sorted(_MESSAGE_SCOPES),
        default="all",
        help="Inbox scope filter: all, direct, or group",
    )
    parser.add_argument(
        "--limit", type=int, default=20,
        help="Result count limit (default: 20)",
    )
    parser.add_argument(
        "--since-seq",
        type=int,
        help="Incremental cursor for group history reads",
    )
    parser.add_argument(
        "--credential", type=str, default="default",
        help="Credential name (default: default)",
    )

    args = parser.parse_args()

    if args.mark_read:
        if args.since_seq is not None:
            parser.error("--since-seq only supports group history reads")
        asyncio.run(mark_read(args.mark_read, args.credential))
    elif args.group_id:
        asyncio.run(
            get_group_history(
                args.group_id,
                args.credential,
                args.limit,
                args.since_seq,
            )
        )
    elif args.history:
        group_id = _parse_group_history_target(args.history)
        if group_id is not None:
            asyncio.run(
                get_group_history(
                    group_id,
                    args.credential,
                    args.limit,
                    args.since_seq,
                )
            )
        else:
            if args.since_seq is not None:
                parser.error("--since-seq only supports group history reads")
            peer_did = asyncio.run(resolve_to_did(args.history))
            asyncio.run(get_history(peer_did, args.credential, args.limit))
    else:
        if args.since_seq is not None:
            parser.error("--since-seq only supports group history reads")
        asyncio.run(check_inbox(args.credential, args.limit, args.scope))


if __name__ == "__main__":
    main()
