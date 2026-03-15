"""Self-contained backtest engine for the skill."""

import numpy as np
import pandas as pd

from core.decision import DecisionParams, compute_signals
from core.indicators import atr as compute_atr
from core.engine import Trade, BacktestResult


def _unrealized_pnl_pct(pos: Trade, current_price: float) -> float:
    if pos.direction == 1:
        return (current_price - pos.entry_price) / pos.entry_price * pos.leverage
    else:
        return (pos.entry_price - current_price) / pos.entry_price * pos.leverage


def run_backtest(
    df: pd.DataFrame,
    params: DecisionParams,
    regime: pd.Series,
    initial_capital: float = 10000.0,
    precomputed_signals: pd.Series = None,
) -> BacktestResult:
    df = df.copy().reset_index(drop=True)
    regime = regime.reset_index(drop=True)
    has_ts = "timestamp" in df.columns

    if precomputed_signals is not None:
        signals = precomputed_signals.reset_index(drop=True)
    else:
        signals = compute_signals(df, params, regime)

    atr_series = compute_atr(df, 14)
    atr_pct_series = (atr_series / df["close"]).fillna(0.02)

    capital = initial_capital
    total_deposited = initial_capital
    blowup_count = 0
    equity = [initial_capital]
    trades: list[Trade] = []
    positions: list[Trade] = []
    roll_count = 0
    prev_regime = regime.iloc[0]

    for i in range(1, len(df)):
        price = df["close"].iloc[i]
        high = df["high"].iloc[i]
        low = df["low"].iloc[i]
        curr_regime = regime.iloc[i]
        atr_pct = atr_pct_series.iloc[i] if not np.isnan(atr_pct_series.iloc[i]) else 0.02
        atr_val = atr_series.iloc[i] if not np.isnan(atr_series.iloc[i]) else price * 0.02

        if capital < initial_capital * 0.01 and not positions:
            blowup_count += 1
            capital = initial_capital
            total_deposited += initial_capital
            roll_count = 0

        closed_positions = []
        for pos in positions:
            exit_price = None
            exit_reason = ""

            liq_check = low if pos.direction == 1 else high
            if _unrealized_pnl_pct(pos, liq_check) <= -1.0:
                liq_threshold = pos.entry_price * (1 - 1.0 / pos.leverage) if pos.direction == 1 \
                    else pos.entry_price * (1 + 1.0 / pos.leverage)
                exit_price = liq_threshold
                exit_reason = "liquidation"

            if exit_price is None and pos.sl_price is not None:
                if pos.direction == 1 and low <= pos.sl_price:
                    exit_price = pos.sl_price
                    exit_reason = "stop_loss"
                elif pos.direction == -1 and high >= pos.sl_price:
                    exit_price = pos.sl_price
                    exit_reason = "stop_loss"

            if exit_price is None and pos.tp_price is not None:
                if pos.direction == 1 and high >= pos.tp_price:
                    exit_price = pos.tp_price
                    exit_reason = "take_profit"
                elif pos.direction == -1 and low <= pos.tp_price:
                    exit_price = pos.tp_price
                    exit_reason = "take_profit"

            if exit_price is None and params.trailing_enabled:
                trail_dist = params.trailing_distance_atr * atr_val
                if pos.direction == 1:
                    if pos.trailing_high is None or high > pos.trailing_high:
                        pos.trailing_high = high
                    if pos.trailing_high and pos.trailing_high > pos.entry_price * (1 + params.trailing_activation_pct):
                        trail_sl = pos.trailing_high - trail_dist
                        if low <= trail_sl:
                            exit_price = trail_sl
                            exit_reason = "trailing_stop"
                else:
                    if pos.trailing_low is None or low < pos.trailing_low:
                        pos.trailing_low = low
                    if pos.trailing_low and pos.trailing_low < pos.entry_price * (1 - params.trailing_activation_pct):
                        trail_sl = pos.trailing_low + trail_dist
                        if high >= trail_sl:
                            exit_price = trail_sl
                            exit_reason = "trailing_stop"

            if exit_price is None and params.exit_on_regime_change:
                if curr_regime != prev_regime:
                    exit_price = price
                    exit_reason = "regime_change"

            if exit_price is None:
                sig = signals.iloc[i]
                if sig != 0 and sig != pos.direction:
                    exit_price = price
                    exit_reason = "signal_reverse"

            if exit_price is not None:
                pnl_pct = _unrealized_pnl_pct(pos, exit_price)
                pnl_pct = max(pnl_pct, -1.0)
                pnl = pos.margin * pnl_pct
                pos.exit_idx = i
                pos.exit_price = exit_price
                pos.exit_time = str(df["timestamp"].iloc[i]) if has_ts else None
                pos.pnl = pnl
                pos.pnl_pct = pnl_pct
                pos.exit_reason = exit_reason
                capital += pos.margin + pnl
                capital = max(capital, 0)
                trades.append(pos)
                closed_positions.append(pos)

        for cp in closed_positions:
            positions.remove(cp)
            if cp.exit_reason != "liquidation":
                roll_count = max(0, roll_count - 1)

        if params.rolling_enabled and positions and roll_count < params.rolling_max_times:
            for pos in list(positions):
                unrealized = _unrealized_pnl_pct(pos, price)
                if unrealized >= params.rolling_trigger_pct:
                    float_profit = pos.margin * unrealized
                    new_margin = float_profit * params.rolling_reinvest_pct
                    if new_margin > 0 and capital >= new_margin:
                        leverage = min(params.base_leverage, params.max_leverage)
                        sl_dist = params.sl_atr_mult * atr_val
                        tp_dist = sl_dist * params.tp_rr_ratio
                        if pos.direction == 1:
                            sl_p = price - sl_dist
                            tp_p = price + tp_dist
                        else:
                            sl_p = price + sl_dist
                            tp_p = price - tp_dist
                        new_pos = Trade(
                            entry_idx=i, entry_price=price, direction=pos.direction,
                            leverage=leverage, margin=new_margin, sl_price=sl_p, tp_price=tp_p,
                            entry_time=str(df["timestamp"].iloc[i]) if has_ts else None,
                        )
                        capital -= new_margin
                        positions.append(new_pos)
                        roll_count += 1
                        if params.rolling_move_stop:
                            pos.sl_price = pos.entry_price

        if not positions and capital > 0:
            sig = signals.iloc[i]
            if sig != 0:
                direction = int(sig)
                leverage = min(params.base_leverage, params.max_leverage)
                margin = capital * params.risk_per_trade
                margin = min(margin, capital * params.max_position_pct, capital)
                sl_dist = params.sl_atr_mult * atr_val
                tp_dist = sl_dist * params.tp_rr_ratio
                if direction == 1:
                    sl_p = price - sl_dist
                    tp_p = price + tp_dist
                else:
                    sl_p = price + sl_dist
                    tp_p = price - tp_dist
                pos = Trade(
                    entry_idx=i, entry_price=price, direction=direction,
                    leverage=leverage, margin=margin, sl_price=sl_p, tp_price=tp_p,
                    entry_time=str(df["timestamp"].iloc[i]) if has_ts else None,
                )
                capital -= margin
                positions.append(pos)
                roll_count = 0

        total_eq = capital
        for pos in positions:
            unreal = _unrealized_pnl_pct(pos, price)
            total_eq += pos.margin * (1 + max(unreal, -1.0))
        equity.append(total_eq - (total_deposited - initial_capital))
        prev_regime = curr_regime

    for pos in positions:
        price = df["close"].iloc[-1]
        pnl_pct = _unrealized_pnl_pct(pos, price)
        pnl_pct = max(pnl_pct, -1.0)
        pos.exit_idx = len(df) - 1
        pos.exit_price = price
        pos.exit_time = str(df["timestamp"].iloc[-1]) if has_ts else None
        pos.pnl = pos.margin * pnl_pct
        pos.pnl_pct = pnl_pct
        pos.exit_reason = "end_of_data"
        capital += pos.margin + pos.pnl
        trades.append(pos)

    equity_series = pd.Series(equity)
    return _build_result(trades, equity_series, blowup_count, total_deposited, initial_capital)


def _build_result(trades, equity, blowup_count=0, total_deposited=0.0, initial_capital=10000.0):
    total_return = (equity.iloc[-1] - initial_capital) / initial_capital if initial_capital > 0 else 0
    peak = equity.expanding().max()
    dd = equity - peak
    safe_peak = peak.replace(0, np.nan)
    drawdown = (dd / safe_peak).min()
    drawdown = drawdown if not np.isnan(drawdown) else 0

    wins = [t for t in trades if t.pnl > 0]
    losses = [t for t in trades if t.pnl <= 0]
    win_rate = len(wins) / len(trades) if trades else 0

    returns = equity.pct_change().dropna()
    valid_returns = returns.replace([np.inf, -np.inf], np.nan).dropna()
    sharpe = (valid_returns.mean() / valid_returns.std() * np.sqrt(8760)) if len(valid_returns) > 1 and valid_returns.std() > 0 else 0

    total_win = sum(t.pnl for t in wins)
    total_loss = abs(sum(t.pnl for t in losses))
    pf = total_win / total_loss if total_loss > 0 else float("inf")

    avg_win = np.mean([t.pnl_pct for t in wins]) if wins else 0
    avg_loss = np.mean([t.pnl_pct for t in losses]) if losses else 0

    consec_w = consec_l = max_cw = max_cl = 0
    for t in trades:
        if t.pnl > 0:
            consec_w += 1; consec_l = 0; max_cw = max(max_cw, consec_w)
        else:
            consec_l += 1; consec_w = 0; max_cl = max(max_cl, consec_l)

    return BacktestResult(
        total_return=total_return, sharpe_ratio=sharpe, max_drawdown=abs(drawdown),
        win_rate=win_rate, profit_factor=pf, total_trades=len(trades),
        avg_trade_pnl=np.mean([t.pnl_pct for t in trades]) if trades else 0,
        avg_win=avg_win, avg_loss=avg_loss,
        max_consecutive_wins=max_cw, max_consecutive_losses=max_cl,
        trades=trades, equity_curve=equity, regime_performance={},
        blowup_count=blowup_count,
        total_deposited=total_deposited if total_deposited > 0 else initial_capital,
    )
