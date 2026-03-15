#!/usr/bin/env python3
"""Package backtest results into an upload bundle for platform verification.

Usage:
    python package_upload.py \
        --bot-name "利弗莫尔" \
        --bot-personality "趋势投机者" \
        --params-file bot_params.json \
        --fingerprint-file fingerprint.json \
        --result-file backtest_result.json \
        --output upload_package.json

    # 进化回测上传（必须带 evolution_log，平台才会做分段 stitched 回放，否则退化成单参回放，和本地结果对不上）：
    python package_upload.py ... \
        --params-file /tmp/bot_params.json \
        --result-file /tmp/evolve_result_final.json \
        --evolution-log-file /tmp/evolve_result_final.json
    # 若 result-file 已是 run_evolve_backtest 输出（含 evolution_log），可不传 --evolution-log-file，脚本会从 result 里自动带出。
"""

import argparse
import json
import os
import re
import sys

# 数据源必须与本地一致：Skill 仅使用 Binance USDT-M 期货 (binanceusdm)。
# 上传时默认原样使用 fingerprint 的 exchange，不再映射为 binance，避免平台用现货数据校验导致指纹/结果不一致。
# 若平台仅接受 binance 且将 binance 视为期货，可传 --exchange binance 覆盖。


def main():
    parser = argparse.ArgumentParser(description="Package upload bundle")
    parser.add_argument("--bot-name", required=True)
    parser.add_argument("--bot-personality", default="")
    parser.add_argument("--bot-description", default="")
    parser.add_argument("--params-file", required=True)
    parser.add_argument("--fingerprint-file", required=True)
    parser.add_argument("--result-file", required=True)
    parser.add_argument("--evolution-log-file", default=None)
    parser.add_argument("--evolution-config", default=None, help="JSON string for evolution config")
    parser.add_argument("--output", default="upload_package.json")
    parser.add_argument("--platform-url", default=None, help="Platform base URL (e.g. http://54.255.3.5:8088)")
    parser.add_argument("--creds", default=None,
                        help="Path to agent_creds.json (bind 后保存的 api_key/api_secret)。上传验证必须提供")
    parser.add_argument("--user-uuid", default=None,
                        help="平台查询 job 状态需 user_uuid。可从 Moss Trader 个人中心获取，或 MOSS_USER_UUID 环境变量")
    parser.add_argument("--exchange", default=None,
                        help="Override data_fingerprint.exchange. Default: use fingerprint's exchange (binanceusdm). Set to binance only if platform requires it.")
    args = parser.parse_args()

    user_uuid = args.user_uuid or os.environ.get("MOSS_USER_UUID") or None
    if user_uuid == "default_user":
        user_uuid = None

    with open(args.params_file) as f:
        params = json.load(f)
    with open(args.fingerprint_file) as f:
        fingerprint = json.load(f)
    with open(args.result_file) as f:
        result_data = json.load(f)

    # 平台 verifier 根据 evolution_log 是否为空决定：空则单参数普通回放，非空则分段 stitched evolve 回放。
    # 上传进化回测时必须带上 evolution_log，否则平台用 bot.params 单参回放，和本地“分段进化”结果不是同一类回测，必然对不上。
    evolution_log = []
    if args.evolution_log_file:
        with open(args.evolution_log_file) as f:
            evo_data = json.load(f)
        evolution_log = evo_data.get("evolution_log", evo_data) if isinstance(evo_data, dict) else evo_data
        if not isinstance(evolution_log, list):
            evolution_log = []
    if not evolution_log and isinstance(result_data, dict) and result_data.get("evolution_log"):
        evolution_log = result_data["evolution_log"]

    evolution_config = None
    if args.evolution_config:
        evolution_config = json.loads(args.evolution_config)

    PARAM_DEFAULTS = {
        "trend_weight": 0.30, "momentum_weight": 0.25, "mean_revert_weight": 0.15,
        "volume_weight": 0.15, "volatility_weight": 0.15,
        "entry_threshold": 0.20, "exit_threshold": 0.10, "long_bias": 0.50,
        "fast_ma_period": 10, "slow_ma_period": 50, "trend_strength_min": 25,
        "supertrend_mult": 3.0, "rsi_period": 14, "rsi_overbought": 70,
        "rsi_oversold": 30, "macd_fast": 12, "macd_slow": 26, "macd_signal": 9,
        "bb_period": 20, "bb_std": 2.0, "base_leverage": 10, "max_leverage": 100,
        "risk_per_trade": 0.10, "max_position_pct": 0.50,
        "sl_atr_mult": 2.0, "tp_rr_ratio": 3.0,
        "trailing_enabled": False, "trailing_activation_pct": 0.02,
        "trailing_distance_atr": 1.5, "rolling_enabled": False,
        "rolling_trigger_pct": 0.30, "rolling_reinvest_pct": 0.80,
        "rolling_max_times": 3, "rolling_move_stop": True,
        "regime_sensitivity": 0.50, "exit_on_regime_change": True,
    }
    for k, v in PARAM_DEFAULTS.items():
        if k not in params or params[k] is None or params[k] == 0:
            if k not in ("long_bias", "regime_sensitivity", "volatility_weight", "mean_revert_weight"):
                params.setdefault(k, v)

    def _to_rfc3339(ts: str) -> str:
        if not ts:
            return ""
        ts = ts.strip()
        if "T" in ts and ts.endswith("Z"):
            return ts
        ts = re.sub(r"(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})", r"\1T\2Z", ts)
        return ts

    backtest_result = result_data.get("backtest_result", result_data)
    trades = result_data.get("trades", [])
    for t in trades:
        if "entry_time" in t:
            t["entry_time"] = _to_rfc3339(t["entry_time"])
        if "exit_time" in t:
            t["exit_time"] = _to_rfc3339(t["exit_time"])

    package = {
        "version": "1.0",
        "bot": {
            "name": args.bot_name,
            "personality": args.bot_personality or args.bot_name,
            "description": args.bot_description or f"{args.bot_name} - {args.bot_personality}",
            "params": params,
            "evolution_config": evolution_config,
        },
        "data_fingerprint": {
            "symbol": fingerprint["symbol"],
            "timeframe": fingerprint["timeframe"],
            "exchange": args.exchange or fingerprint.get("exchange", "binanceusdm"),
            "start": _to_rfc3339(fingerprint["start"]),
            "end": _to_rfc3339(fingerprint["end"]),
            "bars": fingerprint["bars"],
            "first_close": fingerprint["first_close"],
            "last_close": fingerprint["last_close"],
            "checksum": fingerprint.get("checksum", ""),
        },
        "backtest_result": {
            "total_return": float(backtest_result["total_return"]),
            "sharpe_ratio": float(backtest_result["sharpe_ratio"]),
            "max_drawdown": float(backtest_result["max_drawdown"]),
            "win_rate": float(backtest_result["win_rate"]),
            "profit_factor": float(backtest_result["profit_factor"]),
            "total_trades": int(backtest_result["total_trades"]),
            "blowup_count": int(backtest_result.get("blowup_count", 0)),
        },
        "evolution_log": evolution_log,
        "trades": trades[:500],
    }

    with open(args.output, "w") as f:
        json.dump(package, f, indent=2, ensure_ascii=False)
    print(f"Upload package saved to {args.output}")

    if args.platform_url:
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            os.environ.setdefault("TRADE_API_URL", args.platform_url)
            from trading_client import TradingClient

            creds_path = args.creds or os.environ.get("AGENT_CREDS_PATH")
            if not creds_path or not os.path.isfile(creds_path):
                print(
                    "Error: --creds required for platform upload. Path to agent_creds.json (from bind).",
                    file=sys.stderr,
                )
                sys.exit(1)
            with open(creds_path) as f:
                creds = json.load(f)
            api_key = creds.get("api_key", "")
            api_secret = creds.get("api_secret", "")
            client = TradingClient(api_key=api_key, api_secret=api_secret, base_url=args.platform_url)
            print(f"\nSubmitting to {args.platform_url}...")
            result = client.verify_backtest_and_wait(package, user_uuid=user_uuid)
            print(f"Platform response:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Upload failed: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
