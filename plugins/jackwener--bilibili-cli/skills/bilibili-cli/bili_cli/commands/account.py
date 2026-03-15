"""Account and authentication related commands."""

from __future__ import annotations

import json

import click
from rich.panel import Panel

from . import common


@click.command()
def login():
    """扫码登录 Bilibili。"""
    try:
        common.run(common.qr_login())
    except RuntimeError as e:
        common.exit_error(str(e))
    except Exception as e:
        common.exit_error(f"登录失败: {e}")


@click.command()
def logout():
    """注销并清除保存的凭证。"""
    common.clear_credential()
    common.console.print("[green]✅ 已注销，凭证已清除[/green]")


@click.command()
def status():
    """检查登录状态。"""
    cred = common.require_login(message="未登录。使用 [bold]bili login[/bold] 登录。")

    from .. import client

    info = common.run_or_exit(client.get_self_info(cred), "检查登录状态失败")
    name = info.get("name", "unknown")
    uid = info.get("mid", "unknown")
    common.console.print(f"[green]✅ 已登录：[bold]{name}[/bold]  (UID: {uid})[/green]")


@click.command()
@click.option("--json", "as_json", is_flag=True, help="输出原始 JSON。")
def whoami(as_json: bool):
    """查看当前登录用户的详细信息。"""
    from .. import client

    cred = common.require_login(message="未登录。使用 [bold]bili login[/bold] 登录。")

    info = common.run_or_exit(client.get_self_info(cred), "获取用户信息失败")
    uid = info.get("mid", "unknown")
    relation = common.run_or_exit(
        client.get_user_relation_info(uid, credential=cred),
        "获取用户信息失败",
    )

    if as_json:
        click.echo(json.dumps({"info": info, "relation": relation}, ensure_ascii=False, indent=2))
        return

    name = info.get("name", "unknown")
    level = info.get("level", "?")
    coins = info.get("coins", 0)
    follower = relation.get("follower", 0)
    following = relation.get("following", 0)

    vip = info.get("vip", {})
    vip_label = ""
    if vip.get("status") == 1:
        vip_type = "大会员" if vip.get("type") == 2 else "小会员"
        vip_label = f"  |  🏅 {vip_type}"

    sign = info.get("sign", "").strip()

    lines = [
        f"👤 [bold]{name}[/bold]  (UID: {uid})",
        f"⭐ Level {level}  |  🪙 硬币 {coins}{vip_label}",
        f"👥 粉丝 {common.format_count(follower)}  |  🔔 关注 {common.format_count(following)}",
    ]
    if sign:
        lines.append(f"📝 {sign}")

    common.console.print(Panel(
        "\n".join(lines),
        title="个人信息",
        border_style="green",
    ))
