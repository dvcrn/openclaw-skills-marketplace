"""Query commands — search, stats, today, top, timeline."""

import json as json_mod
from collections import defaultdict

import click
from rich.console import Console
from rich.table import Table

from ..db import MessageDB

console = Console(stderr=True)


@click.group("query", invoke_without_command=True)
def query_group():
    """Query and analysis commands (registered at top-level)."""
    pass


@query_group.command("search")
@click.argument("keyword")
@click.option("-c", "--channel", help="Filter by channel name")
@click.option("-n", "--limit", default=50, help="Max results")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def search(keyword: str, channel: str | None, limit: int, as_json: bool):
    """Search stored messages by KEYWORD."""
    with MessageDB() as db:
        channel_id = db.resolve_channel_id(channel) if channel else None
        results = db.search(keyword, channel_id=channel_id, limit=limit)

    if not results:
        console.print("[yellow]No messages found.[/yellow]")
        return

    if as_json:
        click.echo(json_mod.dumps(results, ensure_ascii=False, indent=2, default=str))
        return

    for msg in results:
        ts = (msg.get("timestamp") or "")[:19]
        sender = msg.get("sender_name") or "Unknown"
        ch_name = msg.get("channel_name") or ""
        content = (msg.get("content") or "")[:200]
        console.print(
            f"[dim]{ts}[/dim] [cyan]#{ch_name}[/cyan] | "
            f"[bold]{sender}[/bold]: {content}"
        )

    console.print(f"\n[dim]Found {len(results)} messages[/dim]")


@query_group.command("stats")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def stats(as_json: bool):
    """Show message statistics per channel."""
    with MessageDB() as db:
        channels = db.get_channels()
        total = db.count()

    if as_json:
        click.echo(json_mod.dumps({"total": total, "channels": channels}, ensure_ascii=False, indent=2, default=str))
        return

    table = Table(title=f"Message Stats (Total: {total})")
    table.add_column("Channel ID", style="dim")
    table.add_column("Channel", style="bold")
    table.add_column("Guild", style="cyan")
    table.add_column("Messages", justify="right")
    table.add_column("First", style="dim")
    table.add_column("Last", style="dim")

    for c in channels:
        ch_id = str(c["channel_id"])
        table.add_row(
            ch_id[-6:] + "…" if len(ch_id) > 6 else ch_id,
            f"#{c['channel_name']}" if c["channel_name"] else "—",
            c.get("guild_name") or "—",
            str(c["msg_count"]),
            (c["first_msg"] or "")[:10],
            (c["last_msg"] or "")[:10],
        )

    console.print(table)


@query_group.command("today")
@click.option("-c", "--channel", help="Filter by channel name")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def today(channel: str | None, as_json: bool):
    """Show today's messages, grouped by channel."""
    with MessageDB() as db:
        channel_id = db.resolve_channel_id(channel) if channel else None
        msgs = db.get_today(channel_id=channel_id)

    if not msgs:
        console.print("[yellow]No messages today.[/yellow]")
        return

    if as_json:
        click.echo(json_mod.dumps(msgs, ensure_ascii=False, indent=2, default=str))
        return

    grouped: dict[str, list[dict]] = defaultdict(list)
    for m in msgs:
        key = f"#{m.get('channel_name') or 'unknown'}"
        if m.get("guild_name"):
            key = f"{m['guild_name']} > {key}"
        grouped[key].append(m)

    for ch_label, ch_msgs in sorted(grouped.items(), key=lambda x: -len(x[1])):
        console.print(f"\n[bold cyan]═══ {ch_label} ({len(ch_msgs)} msgs) ═══[/bold cyan]")
        for m in ch_msgs:
            ts = (m.get("timestamp") or "")[11:19]
            sender = m.get("sender_name") or "Unknown"
            content = (m.get("content") or "")[:200].replace("\n", " ")
            console.print(f"  [dim]{ts}[/dim] [bold]{sender[:15]}[/bold]: {content}")

    console.print(f"\n[green]Total: {len(msgs)} messages today[/green]")


@query_group.command("top")
@click.option("-c", "--channel", help="Filter by channel name")
@click.option("--hours", type=int, help="Only count messages within N hours")
@click.option("-n", "--limit", default=20, help="Top N senders")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def top(channel: str | None, hours: int | None, limit: int, as_json: bool):
    """Show most active senders."""
    with MessageDB() as db:
        channel_id = db.resolve_channel_id(channel) if channel else None
        results = db.top_senders(channel_id=channel_id, hours=hours, limit=limit)

    if not results:
        console.print("[yellow]No sender data found.[/yellow]")
        return

    if as_json:
        click.echo(json_mod.dumps(results, ensure_ascii=False, indent=2, default=str))
        return

    table = Table(title="Top Senders")
    table.add_column("#", style="dim", justify="right")
    table.add_column("Sender", style="bold")
    table.add_column("Messages", justify="right")
    table.add_column("First", style="dim")
    table.add_column("Last", style="dim")

    for i, r in enumerate(results, 1):
        table.add_row(
            str(i),
            r["sender_name"],
            str(r["msg_count"]),
            (r["first_msg"] or "")[:10],
            (r["last_msg"] or "")[:10],
        )

    console.print(table)


@query_group.command("timeline")
@click.option("-c", "--channel", help="Filter by channel name")
@click.option("--hours", type=int, help="Only show last N hours")
@click.option("--by", "granularity", type=click.Choice(["day", "hour"]), default="day")
def timeline(channel: str | None, hours: int | None, granularity: str):
    """Show message activity over time as a bar chart."""
    with MessageDB() as db:
        channel_id = db.resolve_channel_id(channel) if channel else None
        results = db.timeline(channel_id=channel_id, hours=hours, granularity=granularity)

    if not results:
        console.print("[yellow]No timeline data.[/yellow]")
        return

    max_count = max(r["msg_count"] for r in results)
    bar_width = 40

    for r in results:
        period = r["period"]
        count = r["msg_count"]
        bar_len = int(count / max_count * bar_width) if max_count > 0 else 0
        bar = "█" * bar_len
        console.print(f"[dim]{period}[/dim] {bar} [bold]{count}[/bold]")
