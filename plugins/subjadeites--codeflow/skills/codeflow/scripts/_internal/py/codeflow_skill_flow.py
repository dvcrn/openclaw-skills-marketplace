#!/usr/bin/env python3
"""Deterministic /codeflow control flow.

Why this exists:
- /codeflow soft mode needs a reliable way to send inline buttons.
- Plain skill prose is not enough; button delivery must be script-owned.
- On routing failures, print a stable fallback payload so the LLM can reply.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from openclaw_gateway import edit_message, extract_message_id, infer_message_route, send_message


class NeedLlmRoute(RuntimeError):
    pass


def codeflow_bin() -> str:
    override = (os.environ.get("CODEFLOW_SKILL_CODEFLOW_BIN") or "").strip()
    if override:
        return override
    return str(Path(__file__).resolve().parents[2] / "codeflow")


def normalize_buttons(raw: Any) -> List[List[Dict[str, str]]]:
    out: List[List[Dict[str, str]]] = []
    if not isinstance(raw, list):
        return out

    for row in raw:
        if not isinstance(row, list):
            continue
        clean_row: List[Dict[str, str]] = []
        for btn in row:
            if not isinstance(btn, dict):
                continue
            text = str(btn.get("text") or "").strip()
            callback_data = str(btn.get("callback_data") or "").strip()
            if not text or not callback_data:
                continue
            clean_row.append({"text": text, "callback_data": callback_data})
        if clean_row:
            out.append(clean_row)
    return out


def require_send_message(session_key: str, text: str, buttons: Optional[List[List[Dict[str, str]]]] = None) -> Dict[str, Any]:
    resp = send_message(session_key, text, buttons=buttons)
    if not isinstance(resp, dict) or resp.get("ok") is False:
        raise NeedLlmRoute(f"tools_invoke failed: {resp}")
    return resp


def require_edit_message(session_key: str, message_id: str, text: str, buttons: Optional[List[List[Dict[str, str]]]] = None) -> Dict[str, Any]:
    resp = edit_message(session_key, message_id, text, buttons=buttons)
    if not isinstance(resp, dict) or resp.get("ok") is False:
        raise NeedLlmRoute(f"tools_invoke failed: {resp}")
    return resp


def strip_callback_prefix(text: str) -> str:
    value = (text or "").strip()
    if value.lower().startswith("callback_data:"):
        value = value.split(":", 1)[1].strip()
    return value


def parse_control_request(raw_text: str) -> Dict[str, str]:
    text = strip_callback_prefix(raw_text)
    lower = text.lower()

    if lower.startswith("cfe:install"):
        parts = text.split(":", 2)
        message_id = parts[2].strip() if len(parts) >= 3 else ""
        return {"action": "install", "message_id": message_id}

    if text.startswith("/codeflow"):
        text = text[len("/codeflow") :].strip()
    elif lower.startswith("codeflow "):
        text = text[len("codeflow") :].strip()
    elif lower == "codeflow":
        text = ""
    else:
        return {"action": "unsupported", "message_id": ""}

    parts = text.split()
    root = parts[0].lower() if parts else ""

    if root in {"", "on", "enable", "activate"}:
        return {"action": "activate", "message_id": ""}
    if root == "status":
        return {"action": "status", "message_id": ""}
    if root in {"off", "disable", "deactivate"}:
        return {"action": "deactivate", "message_id": ""}
    return {"action": "unsupported", "message_id": ""}


def run_codeflow(argv: List[str], session_key: str = "") -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    if session_key:
        env["OPENCLAW_SESSION_KEY"] = session_key
        env["OPENCLAW_SESSION"] = session_key
    return subprocess.run(
        ["/bin/bash", codeflow_bin(), *argv],
        capture_output=True,
        text=True,
        env=env,
    )


def tail_text(value: str, max_chars: int = 800) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    return text if len(text) <= max_chars else text[-max_chars:]


def require_ok(proc: subprocess.CompletedProcess[str], label: str) -> None:
    if proc.returncode == 0:
        return
    detail = tail_text(proc.stderr) or tail_text(proc.stdout) or f"{label} failed"
    raise RuntimeError(detail)


def load_enforcer_status(session_key: str) -> Dict[str, Any]:
    argv = ["enforcer", "status", "--json"]
    if session_key:
        argv.extend(["--session-key", session_key])
    proc = run_codeflow(argv, session_key=session_key)
    require_ok(proc, "enforcer status")
    try:
        data = json.loads(proc.stdout)
    except Exception as e:
        raise RuntimeError(f"invalid enforcer status json: {e}") from e
    if not isinstance(data, dict):
        raise RuntimeError("invalid enforcer status payload")
    return data


def run_guard_action(action: str, session_key: str) -> None:
    proc = run_codeflow(["guard", action, "-P", "auto"], session_key=session_key)
    require_ok(proc, f"guard {action}")


def headline_for(action: str, guard: Dict[str, Any]) -> str:
    active = bool(guard.get("active"))
    state = str(guard.get("state") or "").strip().lower()

    if action == "activate":
        return (
            "Codeflow guard activated for this chat/topic."
            if active
            else "Codeflow activation was requested, but the guard is not active yet."
        )

    if action == "deactivate":
        return (
            "Codeflow guard deactivated for this chat/topic."
            if not active
            else "Codeflow deactivation was requested, but the guard still reports active."
        )

    if action == "status":
        if active:
            return "Codeflow guard is active for this chat/topic."
        if state == "inactive":
            return "Codeflow guard is configured but inactive for this chat/topic."
        if state == "unbound":
            return "Codeflow guard is not active for this chat/topic."
        return "Codeflow guard status is unavailable for this chat/topic."

    if action == "install":
        return "Installing the bundled Codeflow enforcer and restarting the OpenClaw gateway."

    return "Codeflow control request processed."


def fallback_command(status: Dict[str, Any], buttons_sent: bool) -> str:
    if buttons_sent:
        return ""

    recommendation = status.get("recommendation") or {}
    action = str(recommendation.get("action") or "").strip().lower()

    if action == "install":
        return str(status.get("installCommand") or "").strip()
    if action == "restart":
        return str(status.get("restartCommand") or "").strip()
    return ""


def build_control_reply(action: str, status: Dict[str, Any], buttons_supported: bool) -> Dict[str, Any]:
    guard = status.get("guard") or {}
    recommendation = status.get("recommendation") or {}

    buttons = normalize_buttons(recommendation.get("buttons")) if buttons_supported else []
    buttons_sent = len(buttons) > 0

    parts: List[str] = [headline_for(action, guard)]

    binding = str(guard.get("bindingKey") or "").strip()
    if binding and action in {"activate", "status"}:
        parts.append(f"Binding: {binding}")

    rec_message = str(recommendation.get("message") or "").strip()
    if rec_message:
        parts.append(rec_message)

    fallback = fallback_command(status, buttons_sent=buttons_sent)
    if fallback:
        verb = "Restart" if str((recommendation or {}).get("action") or "").strip().lower() == "restart" else "Install"
        parts.append(f"{verb}: {fallback}")

    return {
        "message": "\n\n".join(p for p in parts if p),
        "buttons": buttons,
    }


def build_install_notice() -> Dict[str, Any]:
    return {
        "message": (
            "Installing the bundled Codeflow enforcer and restarting the OpenClaw gateway.\n\n"
            "This may interrupt or reset the current conversation/thread."
        ),
        "buttons": [],
    }


def attach_install_message_id(buttons: List[List[Dict[str, str]]], message_id: str) -> List[List[Dict[str, str]]]:
    if not message_id:
        return buttons

    out: List[List[Dict[str, str]]] = []
    for row in buttons:
        new_row: List[Dict[str, str]] = []
        for btn in row:
            new_btn = dict(btn)
            callback_data = str(new_btn.get("callback_data") or "").strip()
            if callback_data == "cfe:install":
                new_btn["callback_data"] = f"cfe:install:{message_id}"
            new_row.append(new_btn)
        out.append(new_row)
    return out


def emit_need_llm_route(payload: Dict[str, Any]) -> int:
    print("NEED_LLM_ROUTE", file=sys.stdout)
    print(json.dumps(payload, ensure_ascii=False), file=sys.stdout)
    return 3


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--session-key", required=True, help="OpenClaw sessionKey for routing/guard binding")
    ap.add_argument("--text", required=True, help="Raw user text, e.g. /codeflow or callback_data: cfe:install")
    args = ap.parse_args()

    session_key = args.session_key.strip()
    request = parse_control_request(args.text)
    action = request["action"]
    callback_message_id = request.get("message_id", "").strip()

    if action == "unsupported":
        print(json.dumps({"ok": False, "error": "UNSUPPORTED"}, ensure_ascii=False))
        return 2

    buttons_supported = infer_message_route(session_key) is not None
    fallback_payload: Dict[str, Any] = {"message": "Codeflow request processed.", "buttons": []}

    try:
        if action == "install":
            notice = build_install_notice()
            fallback_payload = notice
            if buttons_supported and callback_message_id:
                require_edit_message(session_key, callback_message_id, notice["message"], buttons=[])
            elif buttons_supported:
                require_send_message(session_key, notice["message"], buttons=None)

            proc = run_codeflow(["enforcer", "install", "--restart"], session_key=session_key)
            require_ok(proc, "enforcer install")

            if buttons_supported:
                return 0

            return emit_need_llm_route(notice)

        if action in {"activate", "deactivate"}:
            run_guard_action(action, session_key=session_key)

        status = load_enforcer_status(session_key)
        reply = build_control_reply(action, status, buttons_supported=buttons_supported)
        fallback_payload = reply

        if buttons_supported:
            if reply["buttons"]:
                resp = require_send_message(session_key, reply["message"], buttons=None)
                mid = extract_message_id(resp) or ""
                buttons = attach_install_message_id(reply["buttons"], mid)
                if mid and buttons:
                    require_edit_message(session_key, mid, reply["message"], buttons=buttons)
                elif buttons:
                    require_send_message(session_key, reply["message"], buttons=buttons)
            else:
                require_send_message(session_key, reply["message"], buttons=None)
            return 0

        return emit_need_llm_route(reply)

    except NeedLlmRoute:
        return emit_need_llm_route(fallback_payload)
    except Exception as e:
        message = f"Codeflow request failed.\n\n{str(e).strip() or type(e).__name__}"
        if buttons_supported:
            try:
                if callback_message_id:
                    require_edit_message(session_key, callback_message_id, message, buttons=[])
                else:
                    require_send_message(session_key, message, buttons=None)
                return 1
            except NeedLlmRoute:
                pass
        return emit_need_llm_route({"message": message, "buttons": []})


if __name__ == "__main__":
    raise SystemExit(main())
