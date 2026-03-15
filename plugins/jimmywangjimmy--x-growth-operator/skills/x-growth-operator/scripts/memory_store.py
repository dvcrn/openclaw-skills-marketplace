from __future__ import annotations

from collections import Counter
from typing import Any

from common import load_json, write_json


def default_memory() -> dict[str, Any]:
    return {
        "successful_topics": {},
        "successful_action_types": {},
        "high_signal_accounts": {},
        "avoid_accounts": {},
        "feedback_events": [],
        "updated_at": "",
    }


def load_memory(path: str) -> dict[str, Any]:
    try:
        payload = load_json(path)
        if isinstance(payload, dict):
            return {**default_memory(), **payload}
    except FileNotFoundError:
        pass
    return default_memory()


def save_memory(path: str, payload: dict[str, Any]) -> None:
    write_json(path, payload)


def apply_feedback(memory: dict[str, Any], feedback_items: list[dict[str, Any]], updated_at: str) -> dict[str, Any]:
    success_topics = Counter(memory.get("successful_topics", {}))
    success_actions = Counter(memory.get("successful_action_types", {}))
    high_signal_accounts = Counter(memory.get("high_signal_accounts", {}))
    avoid_accounts = Counter(memory.get("avoid_accounts", {}))
    feedback_events = list(memory.get("feedback_events", []))

    for item in feedback_items:
        result = item.get("result")
        account = item.get("source_account", "")
        action_type = item.get("action_type", "")
        topics = item.get("topics", [])

        feedback_events.append(item)
        if result == "positive":
            for topic in topics:
                success_topics[topic] += 1
            if action_type:
                success_actions[action_type] += 1
            if account:
                high_signal_accounts[account] += 1
        elif result == "negative" and account:
            avoid_accounts[account] += 1

    return {
        "successful_topics": dict(success_topics),
        "successful_action_types": dict(success_actions),
        "high_signal_accounts": dict(high_signal_accounts),
        "avoid_accounts": dict(avoid_accounts),
        "feedback_events": feedback_events[-100:],
        "updated_at": updated_at,
    }
