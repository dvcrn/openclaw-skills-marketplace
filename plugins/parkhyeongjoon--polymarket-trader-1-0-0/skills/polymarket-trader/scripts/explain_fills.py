import argparse
import json
import math
import os
from datetime import datetime, timezone
from dateutil import parser as dateparser
import urllib.request
from urllib.parse import urlencode

BINANCE = "https://api.binance.com"

def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / (2.0**0.5)))

def fetch_json(url: str) -> object:
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

def binance_1m_closes(limit: int = 60) -> list[float]:
    url = BINANCE + "/api/v3/klines?" + urlencode({"symbol": "BTCUSDT", "interval": "1m", "limit": int(limit)})
    k = fetch_json(url)
    return [float(row[4]) for row in k]

def realized_sigma_1m(closes: list[float]) -> float | None:
    if len(closes) < 3: return None
    rets = [(b - a) / a for a, b in zip(closes[:-1], closes[1:]) if a > 0]
    if len(rets) < 3: return None
    mu = sum(rets) / len(rets)
    var = sum((x - mu) ** 2 for x in rets) / (len(rets) - 1)
    return var ** 0.5

def binance_spot() -> float | None:
    try:
        j = fetch_json(BINANCE + "/api/v3/ticker/price?symbol=BTCUSDT")
        return float(j.get("price"))
    except: return None

def binance_1h_open_at(start_ms: int) -> float | None:
    url = BINANCE + "/api/v3/klines?" + urlencode({"symbol": "BTCUSDT", "interval": "1h", "startTime": int(start_ms), "limit": 1})
    k = fetch_json(url)
    return float(k[0][1]) if k else None

def estimate_p_up(open_px, spot, sigma, mins_left):
    if open_px <= 0: return 0.5, 0.0
    cur_ret = (spot - open_px) / open_px
    if not sigma or sigma <= 0 or mins_left <= 0:
        return (1.0 if cur_ret > 0 else (0.0 if cur_ret < 0 else 0.5)), 0.0
    stdev = sigma * math.sqrt(max(0.1, mins_left))
    z = cur_ret / max(1e-9, stdev)
    return max(0.0, min(1.0, norm_cdf(z))), z

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", default="events.jsonl")
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--sec_to_end", type=float, default=1800.0)
    args = ap.parse_args()

    if not os.path.exists(args.events):
        print(f"알림: '{args.events}' 파일이 없습니다. 'touch events.jsonl'로 빈 파일을 만듭니다.")
        with open(args.events, "w") as f: pass

    fills = []
    with open(args.events, "r", encoding="utf-8") as f:
        for line in f:
            try:
                j = json.loads(line)
                if j.get("type") == "fill": fills.append(j)
            except: continue

    if not fills:
        print("분석할 데이터가 없습니다 (events.jsonl이 비어있음).")
        return 0

    fills = fills[-args.n:]
    closes = binance_1m_closes(60)
    sigma = realized_sigma_1m(closes)
    spot = binance_spot()

    print("ts\tside\ttoken\tpx\tfair_up\tz\tagainst_trend")
    for j in fills:
        ts, token, side = j.get("ts"), j.get("token"), j.get("side")
        px = float(j.get("px") or 0.0)
        if spot and ts:
            dt = dateparser.parse(ts).astimezone(timezone.utc)
            ms = int(dt.replace(minute=0, second=0, microsecond=0).timestamp() * 1000)
            open_px = binance_1h_open_at(ms) or spot
            fair_up, z = estimate_p_up(open_px, spot, sigma, args.sec_to_end / 60.0)
            against = "YES" if (("Up" in str(token) and z < -0.25) or ("Down" in str(token) and z > 0.25)) else "NO"
            print(f"{ts}\t{side}\t{token}\t{px:.4f}\t{fair_up:.3f}\t{z:.2f}\t{against}")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
