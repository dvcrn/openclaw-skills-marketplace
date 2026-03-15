"""Stock CLI commands with mock data."""

from __future__ import annotations

import json

import click

from ..config_store import load_config, save_config

VALID_RANGES = {"1d", "5d", "1m", "3m", "6m", "1y", "5y"}
VALID_MARKETS = {"US", "CN", "HK"}


def _emit(content: str) -> None:
    click.echo(content)


@click.command()
def market():
    """查看大盘指数总览。"""
    _emit("暂无数据")


@click.command()
@click.argument("tickers", nargs=-1, required=True)
def quote(tickers: tuple[str, ...]):
    """查看单只或多只股票实时行情。"""
    _emit("暂无数据")


@click.command(name="search")
@click.argument("keyword")
def search(keyword: str):
    """按名称/关键词搜索股票。"""
    _emit("暂无数据")


@click.command()
@click.argument("ticker")
@click.option(
    "-r",
    "--range",
    "period",
    default="1m",
    show_default=True,
    type=click.Choice(sorted(VALID_RANGES), case_sensitive=False),
    help="时间范围",
)
def history(ticker: str, period: str):
    """历史K线数据。"""
    _emit("暂无数据")


@click.group()
def config():
    """配置管理。"""


@config.command(name="show")
def config_show():
    """查看当前配置。"""
    click.echo(json.dumps(load_config(), ensure_ascii=False, indent=2))


@config.command(name="set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """设置配置项。"""
    if key != "market":
        raise click.BadParameter("only 'market' can be set currently")
    upper = value.upper()
    if upper not in VALID_MARKETS:
        raise click.BadParameter("market must be one of: US | CN | HK")
    cfg = load_config()
    cfg["market"] = upper
    save_config(cfg)
    click.echo(json.dumps(cfg, ensure_ascii=False, indent=2))
