"""CLI entry point for stock-cli."""

from __future__ import annotations

import logging

import click

from . import __version__
from .commands.kline import kline
from .commands.market import config, history, market, search
from .commands.quote import quote


@click.group()
@click.version_option(__version__, "-v", "--version", prog_name="stock")
@click.option("-d", "--verbose", is_flag=True, help="启用调试日志")
@click.option(
    "-i",
    "--interval",
    default=10,
    show_default=True,
    type=click.IntRange(1, 3600),
    help="dashboard 刷新间隔（秒）",
)
@click.option("--no-color", is_flag=True, help="禁用颜色输出")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, interval: int, no_color: bool):
    """stock — 股市行情命令行工具 📈"""
    ctx.ensure_object(dict)
    ctx.obj["interval"] = interval
    ctx.color = not no_color
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(name)s %(message)s")
    else:
        logging.basicConfig(level=logging.WARNING)


cli.add_command(market)
cli.add_command(quote)
cli.add_command(search)
cli.add_command(history)
cli.add_command(config)
cli.add_command(kline)

if __name__ == "__main__":
    cli()
