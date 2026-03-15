# pyright: reportMissingImports=false

import json
import subprocess

from constants import (
    AT_IS_ALWAYS_ONCE,
    OPENCLAW_BIN,
    SCHEDULE_KIND_AT,
    SCHEDULE_KIND_CRON,
    SCHEDULE_KIND_EVERY,
    VALID_SCHEDULE_KINDS,
)
from utils import (
    build_channel_tag,
    format_schedule,
    format_status_icon,
    format_timestamp_ms,
    parse_schedule_arg,
)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _run(cmd: list[str]) -> tuple[int, str, str]:
    """Run a subprocess command and return (returncode, stdout, stderr)."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _fetch_all_jobs() -> tuple[list[dict], str | None]:
    """Fetch all cron jobs from the gateway and return (jobs, error)."""
    code, out, err = _run([OPENCLAW_BIN, "cron", "list", "--json", "--all"])
    if code != 0:
        return [], err or out
    try:
        data = json.loads(out)
        return data.get("jobs", []), None
    except json.JSONDecodeError:
        return [], f"Could not parse cron list output: {out}"


def _jobs_for_channel(jobs: list[dict], channel: str, to: str) -> list[dict]:
    """Filter jobs to only those tagged for a specific channel and chat ID."""
    tag = build_channel_tag(channel, to)
    return [j for j in jobs if tag in (j.get("description") or "")]


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


def create_reminder(
    name: str,
    message: str,
    schedule: str,
    channel: str,
    to: str,
    once: bool = False,
) -> str:
    """Create a new cron reminder scoped to the given channel and chat ID.

    Returns a formatted plain-text confirmation or error string.
    """
    try:
        kind, value = parse_schedule_arg(schedule)
    except ValueError as exc:
        return f"Error: {exc}"

    if kind not in VALID_SCHEDULE_KINDS:
        return (
            f"Error: Unknown schedule kind '{kind}'. "
            f"Use one of: {', '.join(VALID_SCHEDULE_KINDS)}"
        )

    if kind == SCHEDULE_KIND_EVERY:
        schedule_flags = ["--every", value]
    elif kind == SCHEDULE_KIND_CRON:
        schedule_flags = ["--cron", value]
    else:
        # at: schedules are always one-shot
        schedule_flags = ["--at", value]
        if AT_IS_ALWAYS_ONCE:
            once = True

    tag = build_channel_tag(channel, to)
    description = f"remind-me skill | channel:{channel} | to:{to} | {tag}"

    cmd = [
        OPENCLAW_BIN,
        "cron",
        "add",
        "--name",
        name,
        "--message",
        message,
        "--description",
        description,
        "--channel",
        channel,
        "--to",
        to,
        "--announce",
        *schedule_flags,
    ]

    if once:
        cmd.append("--delete-after-run")

    code, out, err = _run(cmd)

    if code != 0:
        return f"Error: Failed to create reminder.\n{err or out}"

    try:
        job = json.loads(out)
        sched_str = format_schedule(job.get("schedule", {}))
        job_id = job.get("id", "unknown")
        once_label = " (one-time)" if once else " (recurring)"
        return (
            f"✅ Reminder set!\n"
            f"Name:     {name}\n"
            f"Schedule: {sched_str}{once_label}\n"
            f"Message:  {message}\n"
            f"Channel:  {channel} → {to}\n"
            f"ID:       {job_id}"
        )
    except json.JSONDecodeError:
        return f"✅ Reminder created.\n{out}"


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


def list_reminders(channel: str, to: str) -> str:
    """List all active reminders scoped to a specific channel and chat ID.

    Returns a formatted plain-text summary or error string.
    """
    jobs, error = _fetch_all_jobs()

    if error:
        return f"Error: Could not fetch reminders.\n{error}"

    mine = _jobs_for_channel(jobs, channel, to)

    if not mine:
        return "You have no active reminders in this chat."

    lines = [f"You have {len(mine)} reminder(s) in this chat:\n"]

    for i, job in enumerate(mine, 1):
        name = job.get("name", "Unnamed")
        enabled = job.get("enabled", False)
        sched = format_schedule(job.get("schedule", {}))
        msg = job.get("payload", {}).get("message", "")
        next_run = format_timestamp_ms(job.get("state", {}).get("nextRunAtMs"))
        last_status = job.get("state", {}).get("lastRunStatus")
        status_icon = format_status_icon(last_status)
        paused_label = " ⏸ (disabled)" if not enabled else ""

        lines.append(
            f"{i}. {status_icon} {name}{paused_label}\n"
            f"   Schedule: {sched}\n"
            f"   Message:  {msg}\n"
            f"   Next run: {next_run}\n"
            f"   ID: {job.get('id', 'N/A')}"
        )

    return "\n\n".join(lines)


# ---------------------------------------------------------------------------
# Cancel
# ---------------------------------------------------------------------------


def cancel_reminder_by_name(name: str) -> str:
    """Cancel a reminder by its human-readable name.

    Returns a plain-text confirmation or error string.
    """
    jobs, error = _fetch_all_jobs()

    if error:
        return f"Error: Could not fetch reminders.\n{error}"

    matched = [j for j in jobs if j.get("name") == name]

    if not matched:
        return f"Error: No reminder found with name '{name}'."

    if len(matched) > 1:
        ids = ", ".join(j["id"] for j in matched)
        return (
            f"Error: Multiple reminders found with name '{name}'. "
            f"Use the ID to cancel a specific one.\nIDs: {ids}"
        )

    return cancel_reminder_by_id(matched[0]["id"], display_name=name)


def cancel_reminder_by_id(job_id: str, display_name: str = "") -> str:
    """Cancel a reminder by its job ID.

    Returns a plain-text confirmation or error string.
    """
    code, out, err = _run([OPENCLAW_BIN, "cron", "rm", job_id])

    if code != 0:
        return f"Error: Failed to cancel reminder '{job_id}'.\n{err or out}"

    label = f"'{display_name}'" if display_name else f"ID {job_id}"
    return f"✅ Reminder {label} has been cancelled."


# ---------------------------------------------------------------------------
# Output dispatchers — called by main.py
# ---------------------------------------------------------------------------


def format_create_output(
    name: str,
    message: str,
    schedule: str,
    channel: str,
    to: str,
    once: bool,
) -> str:
    """Dispatch to create_reminder and return its formatted plain-text output."""
    return create_reminder(name, message, schedule, channel, to, once)


def format_list_output(channel: str, to: str) -> str:
    """Dispatch to list_reminders and return its formatted plain-text output."""
    return list_reminders(channel, to)


def format_cancel_output(job_id: str | None, name: str | None) -> str:
    """Dispatch to the correct cancel function and return its formatted plain-text output."""
    if job_id:
        return cancel_reminder_by_id(job_id)
    if name:
        return cancel_reminder_by_name(name)
    return "Error: Provide either a job ID or a name to cancel a reminder."
