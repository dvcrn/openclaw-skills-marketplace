"""
history.py — Portfolio snapshot comparison and history display.
Reads from coach.db as source of truth.
"""
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from .coach_db import CoachDB

console = Console()


class HistoryAnalyzer:

    def __init__(self, db: CoachDB, market=None):
        self.db     = db
        self.market = market

    def compare_snapshots(self, date1: str, date2: str) -> dict:
        """Compare two portfolio snapshots. Returns per-coin diff + totals."""
        snap1 = {r["coin"]: r for r in self.db.get_portfolio_snapshot(date1)}
        snap2 = {r["coin"]: r for r in self.db.get_portfolio_snapshot(date2)}

        all_coins = set(snap1) | set(snap2)
        diffs = []

        for coin in sorted(all_coins):
            v1 = snap1.get(coin, {}).get("usd_value", 0) or 0
            v2 = snap2.get(coin, {}).get("usd_value", 0) or 0
            change = v2 - v1
            pct    = (change / v1 * 100) if v1 > 0 else None
            diffs.append({
                "coin":      coin,
                "value_old": v1,
                "value_new": v2,
                "change":    change,
                "pct":       pct,
            })

        def _first(snap, field, default=None):
            """Safely get a field from the first coin row of a snapshot."""
            try:
                return snap[next(iter(snap))][field] if snap else default
            except (StopIteration, KeyError):
                return default

        total1       = _first(snap1, "portfolio_total", 0) or 0
        total2       = _first(snap2, "portfolio_total", 0) or 0
        total_change = total2 - total1
        total_pct    = (total_change / total1 * 100) if total1 > 0 else None
        hs1          = _first(snap1, "health_score")
        hs2          = _first(snap2, "health_score")

        return {
            "date_old":      date1,
            "date_new":      date2,
            "coins":         sorted(diffs, key=lambda x: abs(x["change"]), reverse=True),
            "total_old":     total1,
            "total_new":     total2,
            "total_change":  total_change,
            "total_pct":     total_pct,
            "health_old":    hs1,
            "health_new":    hs2,
        }

    def print_today_vs_yesterday(self):
        """Compare today's snapshot to yesterday's."""
        today     = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        dates = self.db.get_snapshot_dates(limit=10)

        if not dates:
            console.print("[yellow]No snapshots found. Run 'bc.sh portfolio' to capture one.[/yellow]")
            return

        # Use the two most recent dates
        date_new = dates[0]
        date_old = dates[1] if len(dates) > 1 else None

        if not date_old:
            console.print(f"[yellow]Only one snapshot found ({date_new}). Need at least two days of data.[/yellow]")
            console.print("[dim]Run 'bc.sh portfolio' daily to build history.[/dim]")
            return

        diff = self.compare_snapshots(date_old, date_new)
        self._print_comparison(diff)

    def print_history(self, days: int = 7):
        """Print portfolio value over last N days from snapshots."""
        history = self.db.get_market_history(days=days)

        if not history:
            console.print("[yellow]No market history yet. Run 'bc.sh portfolio' to start building it.[/yellow]")
            return

        table = Table(title=f"📅 Portfolio History — last {len(history)} days",
                      border_style="blue")
        table.add_column("Date",      width=12)
        table.add_column("Total $",   justify="right", width=12)
        table.add_column("Change",    justify="right", width=12)
        table.add_column("Health",    justify="right", width=10)
        table.add_column("F&G",       justify="right", width=8)
        table.add_column("Sentiment", width=16)

        prev_total = None
        for row in reversed(history):
            total   = row["portfolio_total"] or 0
            change  = (total - prev_total) if prev_total is not None else None
            pct     = (change / prev_total * 100) if (change is not None and prev_total) else None

            if change is not None:
                color  = "green" if change >= 0 else "red"
                c_str  = f"[{color}]{change:+.2f} ({pct:+.1f}%)[/{color}]"
            else:
                c_str  = "—"

            grade = row.get("health_grade") or "?"
            score = row.get("health_score")
            hs    = f"{score}/100 {grade}" if score else "—"

            fg    = row.get("fg_score")
            fg_s  = str(fg) if fg is not None else "—"
            label = row.get("fg_label") or "—"

            table.add_row(
                row["date"], f"${total:,.2f}", c_str, hs, fg_s, label
            )
            prev_total = total

        console.print(table)

    def _print_comparison(self, diff: dict):
        """Render a comparison panel between two snapshots."""
        date_old  = diff["date_old"]
        date_new  = diff["date_new"]
        tc        = diff["total_change"]
        tp        = diff["total_pct"]
        hs_old    = diff["health_old"]
        hs_new    = diff["health_new"]

        total_color = "green" if tc >= 0 else "red"
        pct_str     = f" ({tp:+.1f}%)" if tp is not None else ""

        table = Table(
            title=f"📊 {date_old} → {date_new}",
            border_style="cyan"
        )
        table.add_column("Coin",        width=14)
        table.add_column(date_old,      justify="right", width=12)
        table.add_column(date_new,      justify="right", width=12)
        table.add_column("Change $",    justify="right", width=12)
        table.add_column("Change %",    justify="right", width=10)

        for c in diff["coins"]:
            if c["value_old"] == 0 and c["value_new"] == 0:
                continue
            color  = "green" if c["change"] >= 0 else "red"
            pct    = f"[{color}]{c['pct']:+.1f}%[/{color}]" if c["pct"] is not None else "new"
            chg    = f"[{color}]{c['change']:+.2f}[/{color}]"
            table.add_row(
                c["coin"],
                f"${c['value_old']:,.2f}" if c["value_old"] else "—",
                f"${c['value_new']:,.2f}" if c["value_new"] else "—",
                chg, pct,
            )

        console.print(table)

        hs_str = ""
        if hs_old is not None and hs_new is not None:
            hs_color = "green" if hs_new >= hs_old else "red"
            hs_str = f"  Health: {hs_old} → [{hs_color}]{hs_new}[/{hs_color}]"

        console.print(
            f"\n[bold]Portfolio:[/bold] "
            f"${diff['total_old']:,.2f} → ${diff['total_new']:,.2f}  "
            f"[{total_color}]{tc:+.2f}{pct_str}[/{total_color}]"
            + hs_str
        )
