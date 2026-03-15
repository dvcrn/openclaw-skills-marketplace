from __future__ import annotations

import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote as url_quote
from urllib.request import Request, urlopen

import click

_A_CODE_PATTERN = re.compile(r"^(?:[56]\d{5}|[031]\d{5}|4\d{5}|8\d{5}|92\d{4})$")
_HK_CODE_PATTERN = re.compile(r"^\d{5}$")


def test_a_code(code: str) -> bool:
    return bool(_A_CODE_PATTERN.fullmatch(code))


def test_hk_code(code: str) -> bool:
    return bool(_HK_CODE_PATTERN.fullmatch(code))


def get_stock_with_prefix(code: str) -> str:
    if re.fullmatch(r"(?:5|6)\d{5}", code):
        return f"sh{code}"
    if re.fullmatch(r"(?:0|3|1)\d{5}", code):
        return f"sz{code}"
    if re.fullmatch(r"(?:4\d{5}|8\d{5}|92\d{4})", code):
        return f"bj{code}"
    return code


def get_query_code(symbol: str) -> str:
    lower = symbol.lower()
    if lower.startswith("us"):
        return lower.split(".")[0]
    if test_a_code(lower):
        return get_stock_with_prefix(lower)
    if test_hk_code(lower):
        return f"hk{lower}"
    return lower


def _get(arr: list[str], index: int, default: str = "") -> str:
    if index < len(arr):
        return str(arr[index])
    return default


def _to_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _suffix_percent(value: str) -> str:
    return value if value.endswith("%") else f"{value}%"


def arr2obj(arr: list[str]) -> dict:
    prefix_map = {"1": "sh", "51": "sz", "62": "bj", "100": "hk", "200": "us"}
    prefix = prefix_map.get(_get(arr, 0), "")
    index_offset = 1 if prefix in {"us", "hk"} else 0
    volume = f"{_to_float(_get(arr, 36)) / 10000:.2f}万手"
    return {
        "symbol": f"{prefix}{_get(arr, 2)}",
        "code": _get(arr, 2),
        "name": _get(arr, 1),
        "price": _get(arr, 3),
        "change_rate": _suffix_percent(_get(arr, 32)),
        "previous_close": _get(arr, 4),
        "open": _get(arr, 5),
        "high": _get(arr, 33),
        "low": _get(arr, 34),
        "volume": volume,
        "market_value": f"{_get(arr, 45)}亿",
        "circulating_value": f"{_get(arr, 44)}亿",
        "turnover_rate": _suffix_percent(_get(arr, 38)),
        "pe": _get(arr, 39),
        "pb": _get(arr, 46),
        "vr": _get(arr, 49 + index_offset),
    }


def get_stock_by_code(symbol: str) -> dict:
    query_code = get_query_code(symbol)
    url = f"https://sqt.gtimg.cn/q={url_quote(query_code)}&fmt=json"
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Referer": "https://gu.qq.com/",
            "Accept": "application/json,text/plain,*/*",
        },
    )
    try:
        with urlopen(req, timeout=10) as resp:
            text = resp.read().decode("gbk", errors="ignore")
    except HTTPError as exc:
        raise click.ClickException(f"行情接口请求失败: HTTP {exc.code}") from exc
    except URLError as exc:
        raise click.ClickException(f"行情接口不可用: {exc.reason}") from exc
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise click.ClickException("行情接口返回解析失败") from exc
    arr = payload.get(query_code)
    if not isinstance(arr, list) or len(arr) < 2:
        raise click.ClickException("无效股票代码或暂无行情数据")
    return arr2obj(arr)


def format_quote_markdown(quote: dict) -> str:
    return "\n".join(
        [
            "# 个股信息",
            "",
            f"股票: {quote['name']}，代码: {quote['code']}",
            "",
            "## 实时数据",
            "",
            f"- 当前价格: {quote['price']}",
            f"- 涨跌幅: {quote['change_rate']}",
            f"- 昨收价: {quote['previous_close']}",
            f"- 开盘价: {quote['open']}",
            f"- 最高价: {quote['high']}",
            f"- 最低价: {quote['low']}",
            f"- 总市值: {quote['market_value']}",
            f"- 流通市值: {quote['circulating_value']}",
            f"- 市盈率: {quote['pe']}",
            f"- 市净率: {quote['pb']}",
            f"- 成交量: {quote['volume']}",
            f"- 量比: {quote['vr']}",
            f"- 换手率: {quote['turnover_rate']}",
        ]
    )


@click.command(name="quote")
@click.argument("symbol")
def quote(symbol: str):
    data = get_stock_by_code(symbol)
    click.echo(format_quote_markdown(data))
