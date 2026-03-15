"""Discord subcommands — guilds, channels, history, sync, sync-all, search, members."""

import asyncio
import json as json_mod

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..client import (
    fetch_messages,
    get_client,
    get_guild_info,
    list_channels,
    list_guilds,
    list_members,
    resolve_guild_id,
    search_guild_messages,
)
from ..db import MessageDB

console = Console(stderr=True)


@click.group("dc")
def discord_group():
    """Discord operations — list servers, fetch history, sync."""
    pass


@discord_group.command("guilds")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def dc_guilds(as_json: bool):
    """List joined Discord servers."""

    async def _run():
        async with get_client() as client:
            return await list_guilds(client)

    guilds = asyncio.run(_run())

    if as_json:
        click.echo(json_mod.dumps(guilds, ensure_ascii=False, indent=2))
        return

    table = Table(title="Discord Servers")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold")
    table.add_column("Owner", justify="center")

    for g in guilds:
        table.add_row(g["id"], g["name"], "✓" if g["owner"] else "")

    console.print(table)
    console.print(f"\nTotal: {len(guilds)} servers")


@discord_group.command("channels")
@click.argument("guild")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def dc_channels(guild: str, as_json: bool):
    """List text channels in a GUILD (server ID or name)."""

    async def _run():
        async with get_client() as client:
            guild_id = await resolve_guild_id(client, guild)
            if not guild_id:
                console.print(f"[red]Guild '{guild}' not found.[/red]")
                return []
            return await list_channels(client, guild_id)

    channels = asyncio.run(_run())
    if not channels:
        return

    if as_json:
        click.echo(json_mod.dumps(channels, ensure_ascii=False, indent=2))
        return

    table = Table(title="Text Channels")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold")
    table.add_column("Topic", max_width=50)

    for ch in channels:
        table.add_row(ch["id"], f"#{ch['name']}", (ch.get("topic") or "")[:50])

    console.print(table)
    console.print(f"\nTotal: {len(channels)} text channels")


@discord_group.command("history")
@click.argument("channel")
@click.option("-n", "--limit", default=1000, help="Max messages to fetch")
@click.option("--guild-name", help="Guild name to store with messages")
@click.option("--channel-name", help="Channel name to store with messages")
def dc_history(channel: str, limit: int, guild_name: str | None, channel_name: str | None):
    """Fetch historical messages from CHANNEL (channel ID)."""

    async def _run():
        with MessageDB() as db:
            async with get_client() as client:
                ch_name = channel_name
                g_name = guild_name

                if not ch_name:
                    try:
                        ch_info = await client.get(f"/channels/{channel}")
                        if ch_info.status_code == 200:
                            ch_data = ch_info.json()
                            ch_name = ch_data.get("name", channel)
                            if not g_name and ch_data.get("guild_id"):
                                g_info = await get_guild_info(client, ch_data["guild_id"])
                                if g_info:
                                    g_name = g_info["name"]
                    except Exception:
                        pass

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task(f"Fetching messages from {ch_name or channel}...", total=None)
                    messages = await fetch_messages(client, channel, limit=limit)
                    progress.update(task, description=f"Fetched {len(messages)} messages")

                for msg in messages:
                    msg["guild_name"] = g_name
                    msg["channel_name"] = ch_name

                inserted = db.insert_batch(messages)
                return len(messages), inserted

    total, inserted = asyncio.run(_run())
    console.print(f"\n[green]✓[/green] Fetched {total} messages, stored {inserted} new")


@discord_group.command("sync")
@click.argument("channel")
@click.option("-n", "--limit", default=5000, help="Max messages per sync")
def dc_sync(channel: str, limit: int):
    """Incremental sync — fetch only new messages from CHANNEL."""

    async def _run():
        with MessageDB() as db:
            last_id = db.get_last_msg_id(channel)
            if last_id:
                console.print(f"Syncing from msg_id > {last_id}...")

            async with get_client() as client:
                ch_name = None
                g_name = None
                try:
                    ch_info = await client.get(f"/channels/{channel}")
                    if ch_info.status_code == 200:
                        ch_data = ch_info.json()
                        ch_name = ch_data.get("name")
                        if ch_data.get("guild_id"):
                            g_info = await get_guild_info(client, ch_data["guild_id"])
                            if g_info:
                                g_name = g_info["name"]
                except Exception:
                    pass

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task_id = progress.add_task(f"Syncing {ch_name or channel}...", total=None)
                    messages = await fetch_messages(client, channel, limit=limit, after=last_id)
                    progress.update(task_id, description=f"Fetched {len(messages)} new messages")

                for msg in messages:
                    msg["guild_name"] = g_name
                    msg["channel_name"] = ch_name

                inserted = db.insert_batch(messages)
                return len(messages), inserted

    total, inserted = asyncio.run(_run())
    console.print(f"\n[green]✓[/green] Synced {total} messages, stored {inserted} new")


@discord_group.command("sync-all")
@click.option("-n", "--limit", default=5000, help="Max messages per channel")
def dc_sync_all(limit: int):
    """Sync ALL channels in the database."""

    async def _run():
        with MessageDB() as db:
            channels = db.get_channels()
            if not channels:
                console.print("[yellow]No channels in database. Run 'discord dc history' first.[/yellow]")
                return {}

            console.print(f"Syncing {len(channels)} channels...")

            async with get_client() as client:
                results: dict[str, int] = {}
                for ch in channels:
                    ch_id = ch["channel_id"]
                    ch_name = ch.get("channel_name") or ch_id
                    last_id = db.get_last_msg_id(ch_id)
                    try:
                        messages = await fetch_messages(client, ch_id, limit=limit, after=last_id)
                        for msg in messages:
                            msg["guild_name"] = ch.get("guild_name")
                            msg["channel_name"] = ch.get("channel_name")
                        inserted = db.insert_batch(messages)
                        results[ch_name] = inserted
                        if inserted > 0:
                            console.print(f"  [green]✓[/green] {ch_name}: +{inserted}")
                        else:
                            console.print(f"  [dim]✓ {ch_name}: no new messages[/dim]")
                    except Exception as e:
                        console.print(f"  [red]✗ {ch_name}: {e}[/red]")
                        results[ch_name] = 0
                return results

    results = asyncio.run(_run())
    total_new = sum(results.values())
    console.print(f"\n[green]✓[/green] Synced {total_new} new messages across {len(results)} channels")


@discord_group.command("search")
@click.argument("guild")
@click.argument("keyword")
@click.option("-c", "--channel", help="Filter by channel ID")
@click.option("-n", "--limit", default=25, help="Max results")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def dc_search(guild: str, keyword: str, channel: str | None, limit: int, as_json: bool):
    """Search messages in a GUILD by KEYWORD (Discord native search)."""

    async def _run():
        async with get_client() as client:
            guild_id = await resolve_guild_id(client, guild)
            if not guild_id:
                console.print(f"[red]Guild '{guild}' not found.[/red]")
                return []
            return await search_guild_messages(client, guild_id, keyword, channel_id=channel, limit=limit)

    results = asyncio.run(_run())

    if not results:
        console.print("[yellow]No messages found.[/yellow]")
        return

    if as_json:
        click.echo(json_mod.dumps(results, ensure_ascii=False, indent=2, default=str))
        return

    for msg in results:
        ts = str(msg.get("timestamp", ""))[:19]
        sender = msg.get("sender_name") or "Unknown"
        content = (msg.get("content") or "")[:200]
        console.print(f"[dim]{ts}[/dim] [bold]{sender}[/bold]: {content}")

    console.print(f"\n[dim]Found {len(results)} messages[/dim]")


@discord_group.command("members")
@click.argument("guild")
@click.option("-n", "--max", "limit", default=50, help="Max members to list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def dc_members(guild: str, limit: int, as_json: bool):
    """List members of a GUILD (server)."""

    async def _run():
        async with get_client() as client:
            guild_id = await resolve_guild_id(client, guild)
            if not guild_id:
                console.print(f"[red]Guild '{guild}' not found.[/red]")
                return []
            return await list_members(client, guild_id, limit=limit)

    members = asyncio.run(_run())

    if not members:
        console.print("[yellow]No members found (may require Privileged Intents).[/yellow]")
        return

    if as_json:
        click.echo(json_mod.dumps(members, ensure_ascii=False, indent=2, default=str))
        return

    table = Table(title=f"Members ({len(members)})")
    table.add_column("ID", style="dim")
    table.add_column("Username", style="bold")
    table.add_column("Display", style="cyan")
    table.add_column("Nick", style="green")
    table.add_column("Bot", justify="center")

    for m in members:
        display = m.get("global_name") or ""
        table.add_row(
            m["id"],
            f"@{m['username']}" if m.get("username") else "—",
            display,
            m.get("nick") or "",
            "🤖" if m.get("bot") else "",
        )

    console.print(table)


@discord_group.command("info")
@click.argument("guild")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def dc_info(guild: str, as_json: bool):
    """Show detailed info about a GUILD (server)."""

    async def _run():
        async with get_client() as client:
            guild_id = await resolve_guild_id(client, guild)
            if not guild_id:
                return None
            return await get_guild_info(client, guild_id)

    info = asyncio.run(_run())
    if not info:
        console.print(f"[red]Could not find guild: {guild}[/red]")
        return

    if as_json:
        click.echo(json_mod.dumps(info, ensure_ascii=False, indent=2, default=str))
        return

    table = Table(title="Guild Info", show_header=False)
    table.add_column("Field", style="bold")
    table.add_column("Value")

    for k, v in info.items():
        table.add_row(k, str(v) if v is not None else "—")

    console.print(table)
