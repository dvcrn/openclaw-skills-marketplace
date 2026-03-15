#!/usr/bin/env python3
"""Taco Trading Platform CLI client.

Usage:
    python taco_client.py --config config.json kline --symbol BTCUSDT --interval 1h --exchange Binance
    python taco_client.py --config config.json account
    python taco_client.py --config config.json open --exchange Binance --symbol BTCUSDT --notional 100 --long --leverage 3
    python taco_client.py --config config.json close --exchange Binance --symbol BTCUSDT --notional 100 --long
    python taco_client.py indicator --exchange Binance --symbol BTCUSDT --interval 1h --type EMA --period 20
"""

import argparse
import json
import sys
from pathlib import Path
try:
    import requests
except ImportError:
    print("Error: 'requests' package required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://api.dev.taco.trading"
CONFIG_PATH = Path.home() / ".openclaw" / "workspace" / "taco" / "config.json"

VALID_INTERVALS = {"1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"}
VALID_EXCHANGES = {"Binance", "Hyper", "Aster", "Grvt", "StandX", "Lighter"}


def load_config(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        print(f"Error: config file not found: {path}", file=sys.stderr)
        print(f"Create it with: python {sys.argv[0]} init", file=sys.stderr)
        sys.exit(1)
    with open(p) as f:
        cfg = json.load(f)
    required = ["user_id", "api_token", "trader_ids"]
    missing = [k for k in required if not cfg.get(k)]
    if missing:
        print(f"Error: config missing required fields: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(cfg["trader_ids"], dict) or not cfg["trader_ids"]:
        print("Error: 'trader_ids' must be a non-empty mapping of exchange -> trader_id", file=sys.stderr)
        sys.exit(1)
    return cfg


def get_trader_id(cfg: dict, exchange: str) -> str:
    trader_ids = cfg["trader_ids"]
    if exchange not in trader_ids:
        print(f"Error: no trader_id configured for exchange '{exchange}'", file=sys.stderr)
        print(f"Configured exchanges: {', '.join(sorted(trader_ids.keys()))}", file=sys.stderr)
        sys.exit(1)
    return trader_ids[exchange]


def api_request(method: str, endpoint: str, params: dict = None, json_body: dict = None, token: str = None) -> dict:
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        if method == "GET":
            resp = requests.get(url, params=params, headers=headers, timeout=30)
        else:
            resp = requests.post(url, params=params, json=json_body, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        if hasattr(e, "response") and e.response is not None:
            try:
                print(f"Response: {e.response.text}", file=sys.stderr)
            except Exception:
                pass
        sys.exit(1)


def cmd_kline(args):
    if args.interval not in VALID_INTERVALS:
        print(f"Error: invalid interval '{args.interval}'. Valid: {', '.join(sorted(VALID_INTERVALS))}", file=sys.stderr)
        sys.exit(1)
    if args.exchange not in VALID_EXCHANGES:
        print(f"Error: invalid exchange '{args.exchange}'. Valid: {', '.join(sorted(VALID_EXCHANGES))}", file=sys.stderr)
        sys.exit(1)

    params = {"symbol": args.symbol, "interval": args.interval, "exchange": args.exchange}
    if args.start_time:
        params["start_time"] = args.start_time
    if args.end_time:
        params["end_time"] = args.end_time

    result = api_request("GET", "/market/klines", params=params)
    print(json.dumps(result, indent=2))


def cmd_account(args, cfg):
    if args.exchange not in VALID_EXCHANGES:
        print(f"Error: invalid exchange '{args.exchange}'. Valid: {', '.join(sorted(VALID_EXCHANGES))}", file=sys.stderr)
        sys.exit(1)
    trader_id = get_trader_id(cfg, args.exchange)
    params = {"user_id": cfg["user_id"], "trader_id": trader_id}
    result = api_request("GET", "/auth/autopilot/positions", params=params, token=cfg["api_token"])
    print(json.dumps(result, indent=2))


def cmd_open(args, cfg):
    if args.exchange not in VALID_EXCHANGES:
        print(f"Error: invalid exchange '{args.exchange}'. Valid: {', '.join(sorted(VALID_EXCHANGES))}", file=sys.stderr)
        sys.exit(1)
    if args.notional <= 0:
        print("Error: notional_position must be positive", file=sys.stderr)
        sys.exit(1)
    if args.leverage <= 0:
        print("Error: leverage must be positive", file=sys.stderr)
        sys.exit(1)

    trader_id = get_trader_id(cfg, args.exchange)
    body = {
        "api_token": cfg["api_token"],
        "user_id": cfg["user_id"],
        "trader_id": trader_id,
        "exchange": args.exchange,
        "symbol": args.symbol,
        "notional_position": args.notional,
        "long": args.long,
        "leverage": args.leverage,
    }
    if args.sl_price is not None:
        body["sl_price"] = args.sl_price
    if args.tp_price is not None:
        body["tp_price"] = args.tp_price

    params = {"user_id": cfg["user_id"]}
    result = api_request("POST", "/auth/autopilot/position/open", params=params, json_body=body, token=cfg["api_token"])
    print(json.dumps(result, indent=2))


def cmd_close(args, cfg):
    if args.exchange not in VALID_EXCHANGES:
        print(f"Error: invalid exchange '{args.exchange}'. Valid: {', '.join(sorted(VALID_EXCHANGES))}", file=sys.stderr)
        sys.exit(1)
    if args.notional <= 0:
        print("Error: notional_position must be positive", file=sys.stderr)
        sys.exit(1)

    trader_id = get_trader_id(cfg, args.exchange)
    body = {
        "api_token": cfg["api_token"],
        "user_id": cfg["user_id"],
        "trader_id": trader_id,
        "exchange": args.exchange,
        "symbol": args.symbol,
        "notional_position": args.notional,
        "long": args.long,
    }

    params = {"user_id": cfg["user_id"]}
    result = api_request("POST", "/auth/autopilot/position/close", params=params, json_body=body, token=cfg["api_token"])
    print(json.dumps(result, indent=2))


def cmd_update_tp_sl(args, cfg):
    if args.exchange not in VALID_EXCHANGES:
        print(f"Error: invalid exchange '{args.exchange}'. Valid: {', '.join(sorted(VALID_EXCHANGES))}", file=sys.stderr)
        sys.exit(1)
    if args.price <= 0:
        print("Error: price must be positive", file=sys.stderr)
        sys.exit(1)

    trader_id = get_trader_id(cfg, args.exchange)
    body = {
        "api_token": cfg["api_token"],
        "user_id": cfg["user_id"],
        "trader_id": trader_id,
        "exchange": args.exchange,
        "symbol": args.symbol,
        "price": args.price,
        "take_profit": args.take_profit,
    }

    params = {"user_id": cfg["user_id"]}
    result = api_request("POST", "/auth/autopilot/position/triggering", params=params, json_body=body, token=cfg["api_token"])
    print(json.dumps(result, indent=2))


VALID_INDICATORS = {"EMA", "MACD", "RSI", "ATR", "BollingerBands", "DonchianChannel"}


def calc_ema(closes, period):
    if len(closes) < period:
        return [None] * len(closes)
    multiplier = 2.0 / (period + 1)
    ema = [None] * (period - 1)
    ema.append(sum(closes[:period]) / period)
    for i in range(period, len(closes)):
        ema.append(closes[i] * multiplier + ema[-1] * (1 - multiplier))
    return ema


def calc_macd(closes, fast=12, slow=26, signal_period=9):
    ema_fast = calc_ema(closes, fast)
    ema_slow = calc_ema(closes, slow)
    macd_line = []
    for f, s in zip(ema_fast, ema_slow):
        if f is not None and s is not None:
            macd_line.append(f - s)
        else:
            macd_line.append(None)
    macd_values = [v for v in macd_line if v is not None]
    signal_line_raw = calc_ema(macd_values, signal_period) if len(macd_values) >= signal_period else [None] * len(macd_values)
    results = []
    mi = 0
    for v in macd_line:
        if v is None:
            results.append(None)
        else:
            sig = signal_line_raw[mi]
            hist = v - sig if sig is not None else None
            results.append({"macd": v, "signal": sig, "histogram": hist})
            mi += 1
    return results


def calc_rsi(closes, period=14):
    if len(closes) < period + 1:
        return [None] * len(closes)
    results = [None] * period
    gains = []
    losses = []
    for i in range(1, period + 1):
        change = closes[i] - closes[i - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        results.append(100.0)
    else:
        rs = avg_gain / avg_loss
        results.append(100.0 - 100.0 / (1.0 + rs))
    for i in range(period + 1, len(closes)):
        change = closes[i] - closes[i - 1]
        gain = max(change, 0)
        loss = max(-change, 0)
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        if avg_loss == 0:
            results.append(100.0)
        else:
            rs = avg_gain / avg_loss
            results.append(100.0 - 100.0 / (1.0 + rs))
    return results


def calc_atr(highs, lows, closes, period=14):
    if len(closes) < 2:
        return [None] * len(closes)
    true_ranges = [highs[0] - lows[0]]
    for i in range(1, len(closes)):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        true_ranges.append(tr)
    if len(true_ranges) < period:
        return [None] * len(closes)
    results = [None] * (period - 1)
    atr = sum(true_ranges[:period]) / period
    results.append(atr)
    for i in range(period, len(true_ranges)):
        atr = (atr * (period - 1) + true_ranges[i]) / period
        results.append(atr)
    return results


def calc_bollinger(closes, period=20, std_dev=2.0):
    results = []
    for i in range(len(closes)):
        if i < period - 1:
            results.append(None)
            continue
        window = closes[i - period + 1:i + 1]
        middle = sum(window) / period
        variance = sum((x - middle) ** 2 for x in window) / period
        sd = variance ** 0.5
        results.append({"upper": middle + std_dev * sd, "middle": middle, "lower": middle - std_dev * sd})
    return results


def calc_donchian(highs, lows, period=20):
    results = []
    for i in range(len(highs)):
        if i < period - 1:
            results.append(None)
            continue
        upper = max(highs[i - period + 1:i + 1])
        lower = min(lows[i - period + 1:i + 1])
        results.append({"upper": upper, "middle": (upper + lower) / 2.0, "lower": lower})
    return results


def cmd_indicator(args):
    if args.interval not in VALID_INTERVALS:
        print(f"Error: invalid interval '{args.interval}'. Valid: {', '.join(sorted(VALID_INTERVALS))}", file=sys.stderr)
        sys.exit(1)
    if args.exchange not in VALID_EXCHANGES:
        print(f"Error: invalid exchange '{args.exchange}'. Valid: {', '.join(sorted(VALID_EXCHANGES))}", file=sys.stderr)
        sys.exit(1)
    if args.type not in VALID_INDICATORS:
        print(f"Error: invalid indicator type '{args.type}'. Valid: {', '.join(sorted(VALID_INDICATORS))}", file=sys.stderr)
        sys.exit(1)

    params = {"symbol": args.symbol, "interval": args.interval, "exchange": args.exchange}
    if args.start_time:
        params["start_time"] = args.start_time
    if args.end_time:
        params["end_time"] = args.end_time

    result = api_request("GET", "/market/klines", params=params)
    if isinstance(result, list):
        klines = result
    elif isinstance(result, dict):
        klines = result.get("klines", result.get("data", []))
    else:
        klines = []
    if not klines:
        print("Error: no kline data returned", file=sys.stderr)
        sys.exit(1)

    # Support both dict-style (API response) and list-style klines
    sample = klines[0]
    if isinstance(sample, dict):
        timestamps = [k.get("open_time", k.get("time", 0)) for k in klines]
        highs = [float(k["high"]) for k in klines]
        lows = [float(k["low"]) for k in klines]
        closes = [float(k["close"]) for k in klines]
    else:
        timestamps = [k[0] for k in klines]
        highs = [float(k[2]) for k in klines]
        lows = [float(k[3]) for k in klines]
        closes = [float(k[4]) for k in klines]

    indicator_type = args.type
    indicator_params = {}

    if indicator_type == "EMA":
        period = args.period or 20
        indicator_params = {"period": period}
        raw = calc_ema(closes, period)
        values = [{"time": t, "ema": round(v, 6)} for t, v in zip(timestamps, raw) if v is not None]

    elif indicator_type == "MACD":
        fast = args.fast or 12
        slow = args.slow or 26
        signal = args.signal or 9
        indicator_params = {"fast": fast, "slow": slow, "signal": signal}
        raw = calc_macd(closes, fast, slow, signal)
        values = []
        for t, v in zip(timestamps, raw):
            if v is not None:
                entry = {"time": t, "macd": round(v["macd"], 6)}
                entry["signal"] = round(v["signal"], 6) if v["signal"] is not None else None
                entry["histogram"] = round(v["histogram"], 6) if v["histogram"] is not None else None
                values.append(entry)

    elif indicator_type == "RSI":
        period = args.period or 14
        indicator_params = {"period": period}
        raw = calc_rsi(closes, period)
        values = [{"time": t, "rsi": round(v, 4)} for t, v in zip(timestamps, raw) if v is not None]

    elif indicator_type == "ATR":
        period = args.period or 14
        indicator_params = {"period": period}
        raw = calc_atr(highs, lows, closes, period)
        values = [{"time": t, "atr": round(v, 6)} for t, v in zip(timestamps, raw) if v is not None]

    elif indicator_type == "BollingerBands":
        period = args.period or 20
        std_dev = args.std_dev or 2.0
        indicator_params = {"period": period, "std_dev": std_dev}
        raw = calc_bollinger(closes, period, std_dev)
        values = [{"time": t, "upper": round(v["upper"], 6), "middle": round(v["middle"], 6), "lower": round(v["lower"], 6)}
                  for t, v in zip(timestamps, raw) if v is not None]

    elif indicator_type == "DonchianChannel":
        period = args.period or 20
        indicator_params = {"period": period}
        raw = calc_donchian(highs, lows, period)
        values = [{"time": t, "upper": round(v["upper"], 6), "middle": round(v["middle"], 6), "lower": round(v["lower"], 6)}
                  for t, v in zip(timestamps, raw) if v is not None]

    if args.limit and args.limit > 0:
        values = values[-args.limit:]

    output = {
        "indicator": indicator_type,
        "params": indicator_params,
        "symbol": args.symbol,
        "exchange": args.exchange,
        "interval": args.interval,
        "values": values,
    }
    print(json.dumps(output, indent=2))


def cmd_init(args):
    p = Path(args.config)
    if p.exists():
        print(f"Config already exists at {p}", file=sys.stderr)
        print("Delete it first if you want to reinitialize.", file=sys.stderr)
        sys.exit(1)
    user_id = input("Enter your Taco user_id: ").strip()
    api_token = input("Enter your Taco api_token: ").strip()
    if not all([user_id, api_token]):
        print("Error: user_id and api_token are required", file=sys.stderr)
        sys.exit(1)
    trader_ids = {}
    print(f"Configure trader_id for each exchange (leave blank to skip).")
    print(f"Supported exchanges: {', '.join(sorted(VALID_EXCHANGES))}")
    for exchange in sorted(VALID_EXCHANGES):
        tid = input(f"  trader_id for {exchange}: ").strip()
        if tid:
            trader_ids[exchange] = tid
    if not trader_ids:
        print("Error: at least one exchange trader_id is required", file=sys.stderr)
        sys.exit(1)
    p.parent.mkdir(parents=True, exist_ok=True)
    cfg = {"user_id": user_id, "api_token": api_token, "trader_ids": trader_ids}
    with open(p, "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"Config saved to {p}")


def main():
    parser = argparse.ArgumentParser(description="Taco Trading Platform CLI")
    parser.add_argument("--config", default=str(CONFIG_PATH), help=f"Path to JSON config file (default: {CONFIG_PATH})")
    sub = parser.add_subparsers(dest="command", required=True)

    # init
    sub.add_parser("init", help="Initialize config file with credentials")

    # kline
    p_kline = sub.add_parser("kline", help="Get kline/candlestick data")
    p_kline.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    p_kline.add_argument("--interval", required=True, help="Kline interval, e.g. 1h, 4h, 1d")
    p_kline.add_argument("--exchange", required=True, help="Exchange name, e.g. Binance")
    p_kline.add_argument("--start-time", type=int, dest="start_time", help="Start time (Unix ms)")
    p_kline.add_argument("--end-time", type=int, dest="end_time", help="End time (Unix ms)")

    # account
    p_account = sub.add_parser("account", help="Check account positions and balance")
    p_account.add_argument("--exchange", required=True, help="Exchange name (uses its bound trader_id)")

    # open
    p_open = sub.add_parser("open", help="Open a perpetual position")
    p_open.add_argument("--exchange", required=True, help="Exchange name")
    p_open.add_argument("--symbol", required=True, help="Trading pair")
    p_open.add_argument("--notional", required=True, type=float, help="Notional position size")
    p_open.add_argument("--long", action="store_true", default=False, help="Open long (default: short)")
    p_open.add_argument("--leverage", type=float, default=1.0, help="Leverage (default: 1.0)")
    p_open.add_argument("--sl-price", type=float, dest="sl_price", help="Stop-loss price")
    p_open.add_argument("--tp-price", type=float, dest="tp_price", help="Take-profit price")

    # close
    p_close = sub.add_parser("close", help="Close a perpetual position")
    p_close.add_argument("--exchange", required=True, help="Exchange name")
    p_close.add_argument("--symbol", required=True, help="Trading pair")
    p_close.add_argument("--notional", required=True, type=float, help="Notional position size to close")
    p_close.add_argument("--long", action="store_true", default=False, help="Close long position (default: short)")

    # update-tp-sl
    p_tpsl = sub.add_parser("update-tp-sl", help="Update take-profit or stop-loss price for a position")
    p_tpsl.add_argument("--exchange", required=True, help="Exchange name")
    p_tpsl.add_argument("--symbol", required=True, help="Trading pair")
    p_tpsl.add_argument("--price", required=True, type=float, help="New trigger price")
    p_tpsl.add_argument("--take-profit", action="store_true", default=False, dest="take_profit",
                         help="Update take-profit (default: update stop-loss)")

    # indicator
    p_ind = sub.add_parser("indicator", help="Calculate technical indicators from kline data")
    p_ind.add_argument("--exchange", required=True, help="Exchange name")
    p_ind.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    p_ind.add_argument("--interval", required=True, help="Kline interval, e.g. 1h, 4h, 1d")
    p_ind.add_argument("--type", required=True, help=f"Indicator type: {', '.join(sorted(VALID_INDICATORS))}")
    p_ind.add_argument("--period", type=int, default=None, help="Indicator period (default varies by type)")
    p_ind.add_argument("--fast", type=int, default=None, help="MACD fast period (default: 12)")
    p_ind.add_argument("--slow", type=int, default=None, help="MACD slow period (default: 26)")
    p_ind.add_argument("--signal", type=int, default=None, help="MACD signal period (default: 9)")
    p_ind.add_argument("--std-dev", type=float, default=None, dest="std_dev", help="BollingerBands std dev multiplier (default: 2.0)")
    p_ind.add_argument("--start-time", type=int, dest="start_time", help="Start time (Unix ms)")
    p_ind.add_argument("--end-time", type=int, dest="end_time", help="End time (Unix ms)")
    p_ind.add_argument("--limit", type=int, default=0, help="Show only the last N values (default: 0 = all)")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
        return

    if args.command == "indicator":
        cmd_indicator(args)
        return

    if args.command == "kline":
        cmd_kline(args)
        return

    cfg = load_config(args.config)

    if args.command == "account":
        cmd_account(args, cfg)
    elif args.command == "open":
        cmd_open(args, cfg)
    elif args.command == "close":
        cmd_close(args, cfg)
    elif args.command == "update-tp-sl":
        cmd_update_tp_sl(args, cfg)


if __name__ == "__main__":
    main()
