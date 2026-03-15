from datetime import datetime


def format_timestamp_ms(ts_ms: int | None) -> str:
    """Format a millisecond epoch timestamp into a human-readable UTC string."""
    if ts_ms is None:
        return "N/A"
    try:
        return datetime.utcfromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (TypeError, ValueError, OSError):
        return "N/A"


def format_schedule(schedule: dict) -> str:
    """Format a cron job schedule dict into a readable string."""
    if not schedule:
        return "N/A"

    kind = schedule.get("kind", "")

    if kind == "at":
        raw = schedule.get("at", "")
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            return f"Once at {dt.strftime('%Y-%m-%d %H:%M UTC')}"
        except Exception:
            return f"Once at {raw}"

    if kind == "every":
        return f"Every {schedule.get('every', 'N/A')}"

    if kind == "cron":
        return f"Cron: {schedule.get('expr', 'N/A')}"

    return str(schedule)


def format_status_icon(status: str | None) -> str:
    """Map a last-run status string to a display icon."""
    if status == "ok":
        return "✅"
    if status == "error":
        return "❌"
    if status is None:
        return "⏳"
    return "⚠️"


def build_channel_tag(channel: str, to: str) -> str:
    """Build a scoping tag embedded in job descriptions for channel-based filtering.

    Format: [remind-me:<channel>:<chatId>]
    """
    return f"[remind-me:{channel}:{to}]"


def parse_schedule_arg(schedule: str) -> tuple[str, str]:
    """Parse a prefixed schedule string into (kind, value).

    Accepts: every:<duration> | cron:<expr> | at:<duration>
    Returns a tuple of (kind, value) or raises ValueError.
    """
    if ":" not in schedule:
        raise ValueError(
            f"Invalid schedule '{schedule}'. "
            "Expected: every:<duration>, cron:<expr>, or at:<duration>"
        )
    kind, _, value = schedule.partition(":")
    return kind.strip().lower(), value.strip()
