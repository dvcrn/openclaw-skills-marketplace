"""Guardian Source Trust Level definitions and policy enforcement.

Trust levels classify content sources and govern blocking behaviour:

  Level 0 (internal)     — workspace files, cron, system prompts: log only, never block.
  Level 1 (owner)        — authenticated owner channel (e.g. Telegram owner DM): flag only.
  Level 2 (semi_trusted) — web_fetch results, known email addresses: block at score >= 85.
  Level 3 (external)     — unknown webhooks, unknown email senders: block at any threat.
"""

from __future__ import annotations

from typing import Dict

# --- Level constants ---
TRUST_INTERNAL = 0      # cron, workspace files, system prompts
TRUST_OWNER = 1         # owner-authenticated channel (Telegram DM)
TRUST_SEMI_TRUSTED = 2  # web_fetch, known email addresses
TRUST_EXTERNAL = 3      # unknown webhooks, external skill content

TRUST_NAMES: Dict[int, str] = {
    TRUST_INTERNAL: "internal",
    TRUST_OWNER: "owner",
    TRUST_SEMI_TRUSTED: "semi_trusted",
    TRUST_EXTERNAL: "external",
}

# Default channel → trust level mapping.
# Channels not listed default to TRUST_SEMI_TRUSTED.
CHANNEL_TRUST_DEFAULTS: Dict[str, int] = {
    # Level 0 — internal
    "cron": TRUST_INTERNAL,
    "system": TRUST_INTERNAL,
    "file": TRUST_INTERNAL,
    "workspace": TRUST_INTERNAL,
    # Level 1 — owner channel
    "telegram": TRUST_OWNER,
    # Level 2 — semi-trusted
    "email": TRUST_SEMI_TRUSTED,
    "unknown": TRUST_SEMI_TRUSTED,
    # Level 3 — external / untrusted
    "webhook": TRUST_EXTERNAL,
}

# Block thresholds per trust level (score must *exceed* this to block).
# None means never block; 0 means block on any non-zero score.
BLOCK_THRESHOLDS: Dict[int, int | None] = {
    TRUST_INTERNAL: None,         # Never block
    TRUST_OWNER: None,            # Never block — flag only
    TRUST_SEMI_TRUSTED: 85,       # Block only high-confidence threats
    TRUST_EXTERNAL: 0,            # Block any detected threat
}

# Human-readable action descriptions per trust level.
TRUST_ACTIONS: Dict[int, str] = {
    TRUST_INTERNAL: "log_only",
    TRUST_OWNER: "flag_only",
    TRUST_SEMI_TRUSTED: "block_high_confidence",
    TRUST_EXTERNAL: "block_any_threat",
}


def resolve_trust_level(channel: str, config: dict | None = None) -> int:
    """Return the effective trust level integer for *channel*.

    Checks the optional *config* ``trust_levels.channel_map`` override first,
    then falls back to :data:`CHANNEL_TRUST_DEFAULTS`, and finally defaults to
    :data:`TRUST_SEMI_TRUSTED` for unknown channels.

    Args:
        channel: The source channel name (e.g. ``"telegram"``, ``"webhook"``).
        config:  Optional Guardian config dict; used to read ``trust_levels``
                 section overrides.

    Returns:
        Trust level integer in the range [0, 3].
    """
    config = config or {}
    channel_map: dict = (
        config.get("trust_levels", {}).get("channel_map", {})
    )
    level = channel_map.get(channel, CHANNEL_TRUST_DEFAULTS.get(channel))
    if level is None:
        level = TRUST_SEMI_TRUSTED  # sensible default for unknown channels
    return max(0, min(3, int(level)))


def should_block(score: int, trust_level: int) -> tuple[bool, str | None]:
    """Decide whether to block content given its *score* and *trust_level*.

    Returns:
        A ``(blocked, reason)`` tuple.  *reason* is a short string when blocking
        is suppressed by trust policy, otherwise ``None``.
    """
    threshold = BLOCK_THRESHOLDS.get(trust_level)

    if trust_level == TRUST_INTERNAL:
        return False, "trust_internal_no_block"

    if trust_level == TRUST_OWNER:
        return False, "trust_owner_flag_only"

    if threshold is None:
        # Should not reach here for levels 2/3, but guard defensively.
        return False, "trust_no_threshold"

    blocked = score > threshold
    return blocked, None


def trust_name(level: int) -> str:
    """Return the human-readable name for *level*."""
    return TRUST_NAMES.get(level, "unknown")
