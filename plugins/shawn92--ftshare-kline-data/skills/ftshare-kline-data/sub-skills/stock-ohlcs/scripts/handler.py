#!/usr/bin/env python3
"""查询单只 A 股股票 OHLC K 线数据（含 MA5/MA10/MA20）"""
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

BASE_URL = "https://market.ft.tech/app"
ENDPOINT = "/api/v2/stocks/{stock}/ohlcs"
HEADERS = {
    "X-Client-Name": "ft-web",
    "Content-Type": "application/json",
}


def fetch(stock: str, span: str, limit: Optional[int], until_ts_ms: Optional[int]) -> dict:
    params: dict = {"span": span}
    if limit is not None:
        params["limit"] = limit
    if until_ts_ms is not None:
        params["until_ts_ms"] = until_ts_ms

    url = f"{BASE_URL}{ENDPOINT.format(stock=stock)}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="查询单只 A 股股票 OHLC K 线数据")
    parser.add_argument(
        "--stock",
        required=True,
        help="股票标的键，需携带市场后缀，如 688295.XSHG / 000001.SZ / 920036.BJ",
    )
    parser.add_argument(
        "--span",
        required=True,
        choices=["DAY1", "WEEK1", "MONTH1", "YEAR1"],
        help="K 线周期：DAY1（日线）、WEEK1（周线）、MONTH1（月线）、YEAR1（年线）",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="返回 K 线根数上限，建议不超过 2000；不传则返回全部",
    )
    parser.add_argument(
        "--until_ts_ms",
        type=int,
        default=None,
        help="截止时间戳（毫秒），返回该时间点及之前的 K 线；不传则截止到当前",
    )
    args = parser.parse_args()

    result = fetch(args.stock, args.span, args.limit, args.until_ts_ms)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
