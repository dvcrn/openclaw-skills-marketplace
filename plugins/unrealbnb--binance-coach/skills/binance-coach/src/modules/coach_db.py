"""
coach_db.py — Central SQLite database: source of truth for all BinanceCoach history.

Tables:
  portfolio_snapshots  — daily portfolio state per coin
  order_history        — imported Binance orders (opt-in)
  dca_analyses         — DCA recommendations given
  user_actions         — did the user follow the advice?
  market_history       — daily Fear & Greed + portfolio health
"""
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "coach.db"
_DB_INITIALIZED = False


def _init_db():
    global _DB_INITIALIZED
    if _DB_INITIALIZED:
        return
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                date             TEXT    NOT NULL,
                coin             TEXT    NOT NULL,
                amount           REAL,
                usd_value        REAL,
                portfolio_total  REAL,
                health_score     INTEGER,
                health_grade     TEXT,
                timestamp        INTEGER DEFAULT (strftime('%s','now')),
                UNIQUE(date, coin)
            );

            CREATE TABLE IF NOT EXISTS order_history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol      TEXT    NOT NULL,
                side        TEXT    NOT NULL,
                price       REAL,
                qty         REAL,
                spent_quote REAL,
                date        TEXT,
                timestamp   INTEGER,
                source      TEXT    DEFAULT 'binance_api',
                order_id    TEXT    UNIQUE
            );

            CREATE TABLE IF NOT EXISTS dca_analyses (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                date          TEXT    NOT NULL,
                symbol        TEXT    NOT NULL,
                price         REAL,
                rsi           REAL,
                fg_score      INTEGER,
                multiplier    REAL,
                weekly_amount REAL,
                recommendation TEXT,
                timestamp     INTEGER DEFAULT (strftime('%s','now'))
            );

            CREATE TABLE IF NOT EXISTS user_actions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id     INTEGER,
                date            TEXT    NOT NULL,
                symbol          TEXT,
                action_type     TEXT,
                amount_invested REAL,
                notes           TEXT,
                timestamp       INTEGER DEFAULT (strftime('%s','now')),
                FOREIGN KEY(analysis_id) REFERENCES dca_analyses(id)
            );

            CREATE TABLE IF NOT EXISTS market_history (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                date            TEXT    UNIQUE NOT NULL,
                fg_score        INTEGER,
                fg_label        TEXT,
                portfolio_total REAL,
                health_score    INTEGER,
                health_grade    TEXT,
                timestamp       INTEGER DEFAULT (strftime('%s','now'))
            );
        """)
        conn.commit()
    _DB_INITIALIZED = True


class CoachDB:
    """Central source-of-truth database for BinanceCoach."""

    def __init__(self):
        _init_db()

    # ── Portfolio Snapshots ───────────────────────────────────────────────────

    def save_portfolio_snapshot(self, date: str, balances: list,
                                 health_score: int, health_grade: str,
                                 total: float):
        """Save daily portfolio snapshot. Skips if snapshot for today already exists."""
        with sqlite3.connect(DB_PATH) as conn:
            existing = conn.execute(
                "SELECT id FROM portfolio_snapshots WHERE date=? LIMIT 1", (date,)
            ).fetchone()
            if existing:
                return  # Already snapshotted today

            for b in balances:
                conn.execute("""
                    INSERT OR REPLACE INTO portfolio_snapshots
                        (date, coin, amount, usd_value, portfolio_total, health_score, health_grade)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    date,
                    b.get("display", b.get("asset", "")),
                    b.get("amount", 0),
                    b.get("usd_value", 0),
                    total,
                    health_score,
                    health_grade,
                ))
            conn.commit()

    def get_portfolio_snapshot(self, date: str) -> list:
        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute(
                "SELECT coin, amount, usd_value, portfolio_total, health_score, health_grade "
                "FROM portfolio_snapshots WHERE date=? ORDER BY usd_value DESC",
                (date,)
            ).fetchall()
        return [
            {"coin": r[0], "amount": r[1], "usd_value": r[2],
             "portfolio_total": r[3], "health_score": r[4], "health_grade": r[5]}
            for r in rows
        ]

    def get_snapshot_dates(self, limit: int = 30) -> List[str]:
        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute(
                "SELECT DISTINCT date FROM portfolio_snapshots ORDER BY date DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return [r[0] for r in rows]

    def has_snapshot_for(self, date: str) -> bool:
        with sqlite3.connect(DB_PATH) as conn:
            r = conn.execute(
                "SELECT 1 FROM portfolio_snapshots WHERE date=? LIMIT 1", (date,)
            ).fetchone()
        return r is not None

    # ── Order History ─────────────────────────────────────────────────────────

    def save_order(self, symbol: str, side: str, price: float, qty: float,
                   spent_quote: float, date: str, timestamp: int,
                   source: str = "binance_api", order_id: Optional[str] = None):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT OR IGNORE INTO order_history
                    (symbol, side, price, qty, spent_quote, date, timestamp, source, order_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (symbol, side.upper(), price, qty, spent_quote, date, timestamp, source, order_id))
            conn.commit()

    def get_orders(self, symbol: Optional[str] = None, days: int = 365) -> list:
        cutoff_ts = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        with sqlite3.connect(DB_PATH) as conn:
            if symbol:
                sym = symbol.upper()
                if not sym.endswith("USDT"):
                    sym += "USDT"
                rows = conn.execute(
                    "SELECT symbol, side, price, qty, spent_quote, date, timestamp, source "
                    "FROM order_history WHERE symbol=? AND timestamp >= ? ORDER BY timestamp ASC",
                    (sym, cutoff_ts)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT symbol, side, price, qty, spent_quote, date, timestamp, source "
                    "FROM order_history WHERE timestamp >= ? ORDER BY timestamp ASC",
                    (cutoff_ts,)
                ).fetchall()
        return [
            {"symbol": r[0], "side": r[1], "price": r[2], "qty": r[3],
             "spent_quote": r[4], "date": r[5], "timestamp": r[6], "source": r[7]}
            for r in rows
        ]

    def has_orders(self) -> bool:
        with sqlite3.connect(DB_PATH) as conn:
            r = conn.execute("SELECT 1 FROM order_history LIMIT 1").fetchone()
        return r is not None

    def get_order_count(self) -> int:
        with sqlite3.connect(DB_PATH) as conn:
            r = conn.execute("SELECT COUNT(*) FROM order_history").fetchone()
        return r[0] if r else 0

    # ── DCA Analyses ──────────────────────────────────────────────────────────

    def save_dca_analysis(self, date: str, symbol: str, price: float,
                           rsi: float, fg_score: int, multiplier: float,
                           weekly_amount: float, recommendation: str) -> int:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute("""
                INSERT INTO dca_analyses
                    (date, symbol, price, rsi, fg_score, multiplier, weekly_amount, recommendation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (date, symbol.upper(), price, rsi, fg_score, multiplier, weekly_amount, recommendation))
            conn.commit()
            return cur.lastrowid

    def get_dca_history(self, symbol: Optional[str] = None, limit: int = 20) -> list:
        with sqlite3.connect(DB_PATH) as conn:
            if symbol:
                sym = symbol.upper()
                if not sym.endswith("USDT"):
                    sym += "USDT"
                rows = conn.execute(
                    "SELECT id, date, symbol, price, rsi, fg_score, multiplier, weekly_amount, recommendation "
                    "FROM dca_analyses WHERE symbol=? ORDER BY timestamp DESC LIMIT ?",
                    (sym, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, date, symbol, price, rsi, fg_score, multiplier, weekly_amount, recommendation "
                    "FROM dca_analyses ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                ).fetchall()
        return [
            {"id": r[0], "date": r[1], "symbol": r[2], "price": r[3],
             "rsi": r[4], "fg_score": r[5], "multiplier": r[6],
             "weekly_amount": r[7], "recommendation": r[8]}
            for r in rows
        ]

    # ── User Actions ──────────────────────────────────────────────────────────

    def save_user_action(self, analysis_id: Optional[int], symbol: str,
                          action_type: str, amount_invested: Optional[float] = None,
                          notes: str = ""):
        date = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT INTO user_actions
                    (analysis_id, date, symbol, action_type, amount_invested, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (analysis_id, date, symbol.upper(), action_type, amount_invested, notes))
            conn.commit()

    def get_user_actions(self, symbol: Optional[str] = None, limit: int = 20) -> list:
        with sqlite3.connect(DB_PATH) as conn:
            if symbol:
                rows = conn.execute(
                    "SELECT id, analysis_id, date, symbol, action_type, amount_invested, notes "
                    "FROM user_actions WHERE symbol=? ORDER BY timestamp DESC LIMIT ?",
                    (symbol.upper(), limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, analysis_id, date, symbol, action_type, amount_invested, notes "
                    "FROM user_actions ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                ).fetchall()
        return [
            {"id": r[0], "analysis_id": r[1], "date": r[2], "symbol": r[3],
             "action_type": r[4], "amount_invested": r[5], "notes": r[6]}
            for r in rows
        ]

    # ── Market History ────────────────────────────────────────────────────────

    def save_market_history(self, date: str, fg_score, fg_label,
                             portfolio_total: float, health_score: int, health_grade: str):
        """fg_score/fg_label may be None if F&G wasn't fetched this run."""
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT INTO market_history
                    (date, fg_score, fg_label, portfolio_total, health_score, health_grade)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    portfolio_total = excluded.portfolio_total,
                    health_score    = excluded.health_score,
                    health_grade    = excluded.health_grade,
                    fg_score        = COALESCE(excluded.fg_score, market_history.fg_score),
                    fg_label        = COALESCE(excluded.fg_label, market_history.fg_label)
            """, (date, fg_score, fg_label, portfolio_total, health_score, health_grade))
            conn.commit()

    def get_market_history(self, days: int = 30) -> list:
        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute(
                "SELECT date, fg_score, fg_label, portfolio_total, health_score, health_grade "
                "FROM market_history ORDER BY date DESC LIMIT ?",
                (days,)
            ).fetchall()
        return [
            {"date": r[0], "fg_score": r[1], "fg_label": r[2],
             "portfolio_total": r[3], "health_score": r[4], "health_grade": r[5]}
            for r in rows
        ]
