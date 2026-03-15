# -*- coding: utf-8 -*-
"""
InvAssistant — 三条红线检查引擎
核心的建仓过滤条件检查，支持配置化参数。

三条红线：
  红线1 — 情绪释放型下跌 (单日跌≥4% 或 连续3天下跌)
  红线2 — 技术止跌信号 (缩量/均线强承接/Higher Low)
  红线3 — 市场未进入系统性风险 (QQQ/SPX未连续暴跌, VIX<25)

重要：红线是过滤条件(Filter)，全部通过才可建仓，不是评分制(Scoring)。
"""
import pandas as pd


# ============ 默认参数 ============
DEFAULT_REDLINE_PARAMS = {
    "emotion_drop_threshold": -4,   # 单日跌幅触发阈值 (%)
    "consecutive_days": 3,          # 连续下跌天数触发阈值
    "ma_proximity": 0.03,           # 均线接近度 (3%)
    "bounce_threshold": 1.5,        # 强反弹涨幅阈值 (%)
    "volume_ratio": 1.2,            # 放量判定倍数 (120%)
    "entry_size": 0.3               # 建仓仓位 (30%)
}

DEFAULT_MARKET_PARAMS = {
    "vix_threshold": 25
}


def check_emotion(df, params=None):
    """
    红线1：情绪释放型下跌

    触发条件（满足任一）：
    - 单日跌幅 ≥ emotion_drop_threshold (默认4%)
    - 连续 consecutive_days (默认3) 个交易日下跌

    Args:
        df: 股票 OHLCV DataFrame
        params: 策略参数 dict

    Returns:
        (passed: bool, detail: str)
    """
    if df is None or len(df) < 5:
        return False, "数据不足"

    p = {**DEFAULT_REDLINE_PARAMS, **(params or {})}
    threshold = p["emotion_drop_threshold"]
    consec_req = p["consecutive_days"]

    df = df.copy()
    df['Return'] = df['Close'].pct_change() * 100

    latest_return = df['Return'].iloc[-1]
    results = []

    # 检查1：单日跌幅
    if latest_return <= threshold:
        results.append(f"单日跌幅 {latest_return:.2f}% (≥{abs(threshold)}%)")

    # 检查2：连续下跌
    consecutive_down = 0
    for i in range(len(df) - 1, 0, -1):
        if df.iloc[i]['Return'] < 0:
            consecutive_down += 1
        else:
            break

    if consecutive_down >= consec_req:
        results.append(f"连续 {consecutive_down} 个交易日下跌")

    if results:
        return True, "; ".join(f"✓ {r}" for r in results)
    return False, "未检测到明显情绪释放"


def check_tech(df, params=None):
    """
    红线2：技术止跌信号（严格标准）

    需要真实的止跌确认，"接近均线"或"单次反弹"不算通过：
    - 放量下跌后缩量（量能萎缩至前日70%以下）
    - 均线强承接（下影线 + 收涨 + 放量120%+ 或 强反弹≥1.5%）
    - 完整 Higher Low 结构（低点A→反弹→低点B>A→2日确认）

    Args:
        df: 股票 OHLCV DataFrame
        params: 策略参数 dict

    Returns:
        (passed: bool, detail: str)
    """
    if df is None or len(df) < 20:
        return False, "数据不足(需要20日数据)"

    p = {**DEFAULT_REDLINE_PARAMS, **(params or {})}

    df = df.copy()
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else None
    close_price = latest['Close']

    signals = []

    # ---- 检查1: 缩量信号 ----
    if prev is not None and len(df) > 2:
        prev2 = df.iloc[-3]
        vol_ratio = latest['Volume'] / prev['Volume'] if prev['Volume'] > 0 else 1
        prev_down = prev['Close'] < prev2['Close']
        today_shrink = vol_ratio < 0.7
        if prev_down and today_shrink:
            signals.append(f"✓ 放量跌后缩量 (量能{vol_ratio:.0%})")

    # ---- 检查2: 均线强承接 ----
    # 下影线：低点远离收盘，说明有买盘承接
    has_lower_shadow = (latest['Close'] - latest['Low']) > (latest['High'] - latest['Close']) * 1.5
    today_up = latest['Close'] > latest['Open']
    today_return = (latest['Close'] - latest['Open']) / latest['Open'] * 100 if latest['Open'] > 0 else 0
    vol_up = prev is not None and latest['Volume'] > prev['Volume'] * p["volume_ratio"]
    strong_bounce = today_return >= p["bounce_threshold"]
    # 真实承接 = 下影线 + 收涨 + (放量 或 强反弹)
    real_support = has_lower_shadow and today_up and (vol_up or strong_bounce)

    ma20 = latest['MA20']
    ma50 = latest['MA50']

    if pd.notna(ma20) and abs(close_price - ma20) / ma20 < p["ma_proximity"]:
        if real_support:
            signals.append(f"✓ MA20承接 (${ma20:.2f}, 下影线+{'放量' if vol_up else ''}反弹{today_return:+.1f}%)")

    if pd.notna(ma50) and abs(close_price - ma50) / ma50 < p["ma_proximity"]:
        if real_support:
            signals.append(f"✓ MA50承接 (${ma50:.2f}, 下影线+{'放量' if vol_up else ''}反弹{today_return:+.1f}%)")

    # ---- 检查3: 完整 Higher Low 结构 ----
    if len(df) >= 15:
        recent_lows = []
        for i in range(len(df) - 15, len(df) - 1):
            if i > 0 and i < len(df) - 1:
                if df.iloc[i]['Low'] < df.iloc[i-1]['Low'] and df.iloc[i]['Low'] < df.iloc[i+1]['Low']:
                    recent_lows.append((i, df.iloc[i]['Low'], df.index[i].strftime('%m-%d')))

        if len(recent_lows) >= 2:
            low_a = recent_lows[-2]
            low_b = recent_lows[-1]
            if low_b[1] > low_a[1]:
                days_after_b = len(df) - 1 - low_b[0]
                if days_after_b >= 2:
                    prices_after = [df.iloc[j]['Close'] for j in range(low_b[0]+1, min(low_b[0]+3, len(df)))]
                    if all(p_val > low_b[1] for p_val in prices_after):
                        signals.append(f"✓ Higher Low确认 ({low_a[2]}${low_a[1]:.0f}→{low_b[2]}${low_b[1]:.0f})")

    if signals:
        return True, "; ".join(signals)

    # 诊断信息
    diag = []
    if pd.notna(ma20):
        diag.append(f"MA20=${ma20:.2f}({(close_price-ma20)/ma20*100:+.1f}%)")
    diag.append("有下影线" if has_lower_shadow else "无下影线")
    diag.append("收涨" if today_up else "收跌")
    return False, f"未确认止跌 ({', '.join(diag)})"


def check_market(market_data, params=None):
    """
    红线3：市场未进入系统性风险

    必须全部满足：
    - QQQ 未连续3日下跌
    - SPX 未连续3日下跌
    - VIX < vix_threshold (默认25)

    Args:
        market_data: dict 包含 QQQ, ^GSPC, ^VIX 的 DataFrame
        params: 含 vix_threshold 的参数 dict

    Returns:
        (passed: bool, detail: str)
    """
    p = {**DEFAULT_MARKET_PARAMS, **(params or {})}
    vix_threshold = p["vix_threshold"]

    qqq = market_data.get("QQQ")
    spx = market_data.get("^GSPC")
    vix = market_data.get("^VIX")

    if qqq is None or spx is None or vix is None:
        return False, "市场数据缺失"

    results = []
    checks_passed = 0

    # QQQ 检查
    qqq_returns = qqq['Close'].pct_change().dropna()
    if len(qqq_returns) >= 3:
        if not all(r < 0 for r in qqq_returns.tail(3)):
            checks_passed += 1
            results.append("✓ QQQ 未连续暴跌")
        else:
            results.append("✗ QQQ 连续3日下跌")
    else:
        checks_passed += 1
        results.append("✓ QQQ 数据不足，默认通过")

    # VIX 检查
    latest_vix = vix['Close'].iloc[-1]
    if latest_vix < vix_threshold:
        checks_passed += 1
        results.append(f"✓ VIX = {latest_vix:.2f} (<{vix_threshold})")
    else:
        results.append(f"✗ VIX = {latest_vix:.2f} (≥{vix_threshold})")

    # SPX 检查
    spx_returns = spx['Close'].pct_change().dropna()
    if len(spx_returns) >= 3:
        if not all(r < 0 for r in spx_returns.tail(3)):
            checks_passed += 1
            results.append("✓ SPX 未连续暴跌")
        else:
            results.append("✗ SPX 连续3日下跌")
    else:
        checks_passed += 1
        results.append("✓ SPX 数据不足，默认通过")

    passed = checks_passed >= 3
    return passed, "; ".join(results)


def check_pullback(df, threshold=0.06):
    """
    回调检查：判断是否达到加仓阈值。

    Args:
        df: 股票 OHLCV DataFrame
        threshold: 回调幅度阈值 (默认6%)

    Returns:
        (signal: bool, detail: str, pullback_pct: str)
    """
    if df is None or len(df) < 10:
        return False, "数据不足", "N/A"

    high = df["Close"].tail(20).max()
    cur = df["Close"].iloc[-1]
    pb = (high - cur) / high

    return pb >= threshold, f"回调{pb*100:.1f}%", f"{pb*100:.1f}%"


def run_redline_check(df, market_data, params=None, market_params=None):
    """
    执行完整的三条红线检查。

    Args:
        df: 目标股票 OHLCV DataFrame
        market_data: 市场指标数据 dict
        params: 红线策略参数
        market_params: 市场环境参数

    Returns:
        dict 包含 rl1, rl2, rl3, all_passed, action, detail
    """
    rl1_passed, rl1_detail = check_emotion(df, params)
    rl2_passed, rl2_detail = check_tech(df, params)
    rl3_passed, rl3_detail = check_market(market_data, market_params)

    all_passed = rl1_passed and rl2_passed and rl3_passed
    passed_count = sum([rl1_passed, rl2_passed, rl3_passed])

    entry_size = (params or {}).get("entry_size", DEFAULT_REDLINE_PARAMS["entry_size"])

    if all_passed:
        action = f"三条红线全部通过 → 可建仓{int(entry_size*100)}%"
    else:
        failed = []
        if not rl1_passed:
            failed.append("情绪释放")
        if not rl2_passed:
            failed.append("技术止跌")
        if not rl3_passed:
            failed.append("市场环境")
        action = f"不建仓 | 未通过: {', '.join(failed)}"

    return {
        "red_line_1": {"passed": rl1_passed, "detail": rl1_detail},
        "red_line_2": {"passed": rl2_passed, "detail": rl2_detail},
        "red_line_3": {"passed": rl3_passed, "detail": rl3_detail},
        "passed_count": passed_count,
        "all_passed": all_passed,
        "action": action
    }
