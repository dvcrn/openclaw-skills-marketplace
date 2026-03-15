from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import quote as url_quote
from urllib.request import Request, urlopen

import click

from .quote import get_query_code


@dataclass
class DayLineItem:
    date: str
    open: float
    close: float
    high: float
    low: float
    volume: float
    amount: float


@dataclass
class BollBand:
    up: float
    mid: float
    low: float


@dataclass
class KDJResult:
    k: float
    d: float
    j: float
    rsv: float


def _is_a_stock(query_code: str) -> bool:
    return query_code.startswith(("sh", "sz", "bj"))


def _to_float(value: str | int | float, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _get_standard_deviation(data: list[float]) -> float:
    n = len(data)
    if n == 0:
        return 0.0
    mean = sum(data) / n
    variance = sum((value - mean) ** 2 for value in data) / n
    return variance**0.5


def _get_simple_moving_average(data: list[float]) -> float:
    if not data:
        return 0.0
    return sum(data) / len(data)


def ema(data: list[DayLineItem], period: int) -> list[float]:
    if not data:
        return []
    if period <= 0:
        raise click.ClickException("EMA 周期必须大于 0")
    multiplier = 2 / (period + 1)
    results: list[float] = []
    current_ema: float | None = None
    for index, item in enumerate(data):
        current_price = item.close
        if current_ema is None:
            if index == 0:
                current_ema = current_price
            elif index == period - 1:
                current_ema = _get_simple_moving_average([x.close for x in data[: index + 1]])
        else:
            current_ema = current_price * multiplier + current_ema * (1 - multiplier)
        results.append(round(current_ema or 0.0, 2))
    return results


def boll(data: list[DayLineItem], period: int = 20, std_dev_multiplier: int = 2) -> list[BollBand]:
    if not data:
        return []
    if period <= 0:
        raise click.ClickException("BOLL 周期必须大于 0")
    if std_dev_multiplier < 0:
        raise click.ClickException("BOLL 标准差倍数不能为负")
    values: list[BollBand] = []
    for index in range(len(data)):
        if index < period - 1:
            values.append(BollBand(up=0.0, mid=0.0, low=0.0))
            continue
        period_data = data[index - period + 1 : index + 1]
        closes = [x.close for x in period_data]
        mid = _get_simple_moving_average(closes)
        std_dev = _get_standard_deviation(closes)
        up = mid + std_dev_multiplier * std_dev
        low = mid - std_dev_multiplier * std_dev
        values.append(BollBand(up=round(up, 2), mid=round(mid, 2), low=round(low, 2)))
    return values


def _calculate_rsv(period_data: list[DayLineItem]) -> float:
    highest = max(x.high for x in period_data)
    lowest = min(x.low for x in period_data)
    close = period_data[-1].close
    if highest == lowest:
        return 0.0
    return round((close - lowest) / (highest - lowest) * 100, 2)


def kdj(data: list[DayLineItem], period_k: int = 9, period_d: int = 3, period_j: int = 3) -> list[KDJResult]:
    start_index = period_k - 1
    results: list[KDJResult] = [KDJResult(k=0.0, d=0.0, j=0.0, rsv=0.0) for _ in range(start_index)]
    for index in range(start_index, len(data)):
        period_data = data[index - start_index : index + 1]
        rsv = _calculate_rsv(period_data)
        if index == start_index:
            k_value = rsv
            d_value = rsv
        else:
            prev = results[-1]
            k_value = round((rsv + (period_d - 1) * prev.k) / period_d, 2)
            d_value = round((k_value + (period_j - 1) * prev.d) / period_j, 2)
        j_value = round(3 * k_value - 2 * d_value, 2)
        results.append(KDJResult(k=k_value, d=d_value, j=j_value, rsv=rsv))
    return results


def rsi(data: list[DayLineItem], period: int = 6) -> list[float]:
    values: list[float] = [0.0 for _ in range(len(data))]
    gains: list[float] = []
    losses: list[float] = []
    for index in range(1, len(data)):
        change = data[index].close - data[index - 1].close
        if change > 0:
            gains.append(change)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(abs(change))
    if period <= 0:
        raise click.ClickException("RSI 周期必须大于 0")
    avg_gain = sum(gains[: period - 1]) / period
    avg_loss = sum(losses[: period - 1]) / period
    for index in range(period - 1, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[index]) / period
        avg_loss = (avg_loss * (period - 1) + losses[index]) / period
        if avg_loss == 0:
            values[index + 1] = 100.0
        else:
            rs = avg_gain / avg_loss
            values[index + 1] = round(100 - (100 / (1 + rs)), 2)
    return values


def _parse_lines(raw_lines: list[list[str]]) -> list[DayLineItem]:
    parsed: list[DayLineItem] = []
    for item in raw_lines:
        if len(item) < 9:
            continue
        parsed.append(
            DayLineItem(
                date=str(item[0]).replace("-", ""),
                open=_to_float(item[1]),
                close=_to_float(item[2]),
                high=_to_float(item[3]),
                low=_to_float(item[4]),
                volume=_to_float(item[5]),
                amount=_to_float(item[8]),
            )
        )
    return parsed


def get_kline_data(symbol: str, count: int = 45) -> dict:
    query_code = get_query_code(symbol)
    url = (
        "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get"
        f"?param={url_quote(query_code)},day,,,90,qfq"
    )
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
            text = resp.read().decode("utf-8", errors="ignore")
    except HTTPError as exc:
        raise click.ClickException(f"日K接口请求失败: HTTP {exc.code}") from exc
    except URLError as exc:
        raise click.ClickException(f"日K接口不可用: {exc.reason}") from exc
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise click.ClickException("日K接口返回解析失败") from exc
    symbol_data = payload.get("data", {}).get(query_code)
    if not isinstance(symbol_data, dict):
        raise click.ClickException("无效股票代码或暂无日K数据")
    raw_lines = symbol_data.get("qfqday") or symbol_data.get("day") or []
    if not isinstance(raw_lines, list) or not raw_lines:
        raise click.ClickException("暂无日K数据")
    lines = _parse_lines(raw_lines)
    if not lines:
        raise click.ClickException("暂无有效日K数据")
    ema_5 = ema(lines, 5)
    ema_10 = ema(lines, 10)
    ema_20 = ema(lines, 20)
    boll_result = boll(lines)
    kdj_result = kdj(lines)
    rsi_6 = rsi(lines, 6)
    rsi_12 = rsi(lines, 12)
    market_index = 0 if _is_a_stock(query_code) else 1
    qt = symbol_data.get("qt", {}).get(query_code, [])
    sliced_lines = lines[-count:]
    return {
        "lines": [
            {
                "时间": int(item.date),
                "开盘价": item.open,
                "收盘价": item.close,
                "最高价": item.high,
                "最低价": item.low,
                "成交量": f"{round(item.volume)}手",
                "成交额": f"{item.amount}万",
            }
            for item in sliced_lines
        ],
        "now": {
            "name": qt[1] if len(qt) > 1 else query_code,
            "vr": qt[49 + market_index] if len(qt) > 49 + market_index else "",
            "price": qt[3] if len(qt) > 3 else "",
            "change_rate": qt[32] if len(qt) > 32 else "",
        },
        "factors": {
            "ema_5": ema_5[-1],
            "ema_10": ema_10[-1],
            "ema_20": ema_20[-1],
            "boll_up": boll_result[-1].up,
            "boll_mid": boll_result[-1].mid,
            "boll_low": boll_result[-1].low,
            "kdj_k": kdj_result[-1].k,
            "kdj_d": kdj_result[-1].d,
            "kdj_j": kdj_result[-1].j,
            "rsi_6": rsi_6[-1],
            "rsi_12": rsi_12[-1],
        },
    }


def format_kline_markdown(data: dict) -> str:
    lines = data.get("lines", [])
    if not lines:
        raise click.ClickException("暂无日K数据")
    headers = list(lines[0].keys())
    csv_rows = [",".join(str(item[key]) for key in headers) for item in lines]
    factors = data["factors"]
    return "\n".join(
        [
            "## 日K线",
            "",
            "```csv",
            ",".join(headers),
            *csv_rows,
            "```",
            "",
            "**技术指标**",
            "",
            f"- EMA5: {factors['ema_5']}",
            f"- EMA10: {factors['ema_10']}",
            f"- EMA20: {factors['ema_20']}",
            f"- BOLL(20,2): UP:{factors['boll_up']}, MID:{factors['boll_mid']}, LOW:{factors['boll_low']}",
            f"- KDJ(9,3,3): K:{factors['kdj_k']}, D:{factors['kdj_d']}, J:{factors['kdj_j']}",
            f"- RSI6: {factors['rsi_6']}",
            f"- RSI12: {factors['rsi_12']}",
        ]
    )


@click.command(name="kline")
@click.argument("code")
@click.option("--count", default=45, show_default=True, type=click.IntRange(1, 90), help="输出最近N条日K")
def kline(code: str, count: int):
    data = get_kline_data(code, count=count)
    click.echo(format_kline_markdown(data))
