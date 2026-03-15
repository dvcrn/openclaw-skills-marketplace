"""
alerts.py — Context-rich price alert system
Alerts tell you not just WHAT happened, but WHY it matters
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from rich.console import Console
from modules.i18n import t

logger = logging.getLogger(__name__)

console = Console()

DB_PATH = str(Path(__file__).parent.parent / "data" / "alerts.db")


def init_alerts_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                condition TEXT,
                threshold REAL,
                triggered INTEGER DEFAULT 0,
                created_at TEXT,
                triggered_at TEXT,
                notes TEXT
            )
        """)
        conn.commit()


class AlertManager:
    """Manages and evaluates context-rich price alerts."""

    def __init__(self, market, telegram_notify=None):
        self.market = market
        self.telegram_notify = telegram_notify
        init_alerts_db()

    def add_alert(self, symbol: str, condition: str, threshold: float, notes: str = ""):
        """
        Add a price alert.
        condition: 'above' | 'below' | 'rsi_above' | 'rsi_below'
        """
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT INTO alerts (symbol, condition, threshold, created_at, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (symbol, condition, threshold, datetime.utcnow().isoformat(), notes))
            conn.commit()

    def check_alerts(self) -> list:
        """Check all untriggered alerts and fire any that match."""
        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute(
                "SELECT id, symbol, condition, threshold, notes FROM alerts WHERE triggered=0"
            ).fetchall()

        fired = []
        for alert_id, symbol, condition, threshold, notes in rows:
            try:
                ctx = self.market.get_market_context(symbol)
                price = ctx["price"]
                rsi = ctx["rsi"]
                triggered = False
                trigger_value = None

                if condition == "above" and price >= threshold:
                    triggered = True
                    trigger_value = price
                elif condition == "below" and price <= threshold:
                    triggered = True
                    trigger_value = price
                elif condition == "rsi_above" and rsi >= threshold:
                    triggered = True
                    trigger_value = rsi
                elif condition == "rsi_below" and rsi <= threshold:
                    triggered = True
                    trigger_value = rsi

                if triggered:
                    context_msg = self._build_context_message(symbol, ctx, condition, threshold, trigger_value)
                    self._mark_triggered(alert_id)
                    fired.append({
                        "symbol": symbol,
                        "condition": condition,
                        "threshold": threshold,
                        "trigger_value": trigger_value,
                        "context": context_msg,
                        "notes": notes,
                    })

            except Exception as exc:
                logger.warning("Alert check failed for %s: %s", symbol, exc)

        return fired

    def _build_context_message(self, symbol: str, ctx: dict, condition: str, threshold: float, trigger_value: float) -> str:
        """Build a rich context message explaining WHY the alert matters."""
        fg = ctx["fear_greed"]
        price = ctx["price"]
        rsi = ctx["rsi"]
        trend = ctx["trend"]
        vs_sma200 = ctx["vs_sma200_pct"]

        emoji = "📈" if condition == "above" else "📉"
        msg = f"{emoji} *{symbol} Alert Triggered!*\n\n"

        if condition in ("above", "below"):
            msg += t("alert.ctx.price_hit", value=f"{trigger_value:,.4f}", threshold=f"{threshold:,.4f}")
        else:
            msg += t("alert.ctx.rsi_hit", value=f"{trigger_value:.1f}", threshold=threshold)

        msg += t("alert.ctx.header")
        msg += f"• {t('market.price')}: ${price:,.4f}\n"
        msg += f"• {t('market.rsi')}: {rsi:.1f} ({ctx['rsi_zone']})\n"
        msg += f"• {t('market.trend')}: {trend}\n"
        msg += f"• {t('market.fear_greed')}: {fg['value']} ({fg['classification']})\n"
        msg += f"• {t('market.vs_sma200')}: {vs_sma200:+.1f}%\n\n"

        msg += t("alert.ctx.meaning")

        if condition == "above":
            if rsi > 70:
                msg += t("alert.ctx.rsi_ob_caution")
            elif fg["value"] > 75:
                msg += t("alert.ctx.greed_caution")
            else:
                msg += t("alert.ctx.healthy_break")
            if ctx["above_sma200"]:
                msg += t("alert.ctx.above_sma200")

        elif condition == "below":
            if rsi < 30:
                msg += t("alert.ctx.oversold_buy")
            elif fg["value"] < 25:
                msg += t("alert.ctx.extreme_fear_buy")
            else:
                msg += t("alert.ctx.dropped")
            if not ctx["above_sma200"]:
                msg += t("alert.ctx.below_sma200")

        return msg

    def _mark_triggered(self, alert_id: int):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "UPDATE alerts SET triggered=1, triggered_at=? WHERE id=?",
                (datetime.utcnow().isoformat(), alert_id)
            )
            conn.commit()

    def list_alerts(self):
        """List all active alerts."""
        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute(
                "SELECT symbol, condition, threshold, created_at, notes FROM alerts WHERE triggered=0"
            ).fetchall()

        if not rows:
            console.print(f"[yellow]{t('alert.none')}[/yellow]")
            return

        from rich.table import Table
        table = Table(title=t("alert.title"))
        table.add_column(t("alert.col.symbol"))
        table.add_column(t("alert.col.condition"))
        table.add_column(t("alert.col.threshold"))
        table.add_column(t("alert.col.created"))
        table.add_column(t("alert.col.notes"))

        for symbol, condition, threshold, created_at, notes in rows:
            table.add_row(symbol, condition, str(threshold), created_at[:10], notes or "")
        console.print(table)
