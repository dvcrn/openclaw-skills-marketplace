#!/usr/bin/env python3
"""
Portfolio Drift Monitor for Kalshi

Monitors Kalshi portfolio positions for significant drift (position changes).
Alerts when any position moves beyond configured threshold percentage.

Environment variables:
  KALSHI_KEY_ID: API key ID from dev.kalshi.com
  KALSHI_KEY_PATH: Path to Kalshi private key file (PEM format)
  PORTFOLIO_DRIFT_THRESHOLD: Percentage change to trigger alert (default: 5.0)
  PORTFOLIO_DRIFT_INTERVAL: Minutes between checks for rate limiting (default: 60)

State file:
  ~/.openclaw/state/portfolio_snapshot.json - Stores last known portfolio state
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

try:
    from kalshi_python_sync import Configuration, KalshiClient
except ImportError:
    try:
        from kalshi_python import Configuration, KalshiClient
    except ImportError:
        print("ERROR: Neither kalshi_python_sync nor kalshi_python found.")
        sys.exit(1)

try:
    import yaml
except ImportError:
    yaml = None


# ── API Schema Normalization ────────────────────────────────────────────────
def _normalize_position(p: dict) -> dict:
    """Normalize Kalshi API v3 position fields.

    Kalshi API may change position field names. This helper ensures we handle
    both old and new field names gracefully. Currently a pass-through; if Kalshi
    changes position schema, update this function to normalize field names.
    """
    # Currently positions use position_fp, average_price, realized_pnl which are stable.
    # If Kalshi renames these, add normalization logic here.
    return p


class PortfolioDriftMonitor:
    """Monitors Kalshi portfolio drift with rate limiting and threshold alerts."""

    def __init__(self):
        """Initialize monitor with configuration from config.yaml (env vars as fallback)."""
        # Load from config.yaml first, env vars as fallback
        config = self._load_config()
        kalshi_cfg = config.get("kalshi", {})

        self.key_id = kalshi_cfg.get("api_key_id") or os.getenv("KALSHI_KEY_ID")
        self.key_path = kalshi_cfg.get("private_key_file") or os.getenv("KALSHI_KEY_PATH")
        self.threshold_pct = float(os.getenv("PORTFOLIO_DRIFT_THRESHOLD", "5.0"))
        self.interval_minutes = int(os.getenv("PORTFOLIO_DRIFT_INTERVAL", "60"))

        # Validate credentials
        if not self.key_id or not self.key_path:
            raise ValueError(
                "Kalshi credentials required in ~/.openclaw/config.yaml or env vars"
            )

        if not os.path.exists(self.key_path):
            raise FileNotFoundError(f"Kalshi key file not found: {self.key_path}")

        # State file location
        self.state_dir = Path.home() / ".openclaw" / "state"
        self.state_file = self.state_dir / "portfolio_snapshot.json"
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Kalshi client (v3 SDK pattern)
        try:
            with open(self.key_path) as f:
                private_key = f.read()

            config_obj = Configuration(
                host="https://api.elections.kalshi.com/trade-api/v2"
            )
            config_obj.api_key_id = self.key_id
            config_obj.private_key_pem = private_key
            self.client = KalshiClient(config_obj)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Kalshi client: {e}")

    @staticmethod
    def _load_config() -> dict:
        """Load config from ~/.openclaw/config.yaml."""
        config_path = Path.home() / ".openclaw" / "config.yaml"
        if config_path.exists() and yaml:
            with open(config_path) as f:
                return yaml.safe_load(f) or {}
        return {}

    def get_current_portfolio(self) -> Dict[str, Any]:
        """
        Fetch current portfolio from Kalshi API using raw API call.

        Uses _portfolio_api.get_positions_without_preload_content() to avoid
        SDK v3 pydantic deserialization bugs (typed get_positions() returns
        None attributes for position fields, causing false empty portfolios).

        Returns:
            Dict with portfolio metadata and positions indexed by market symbol
        """
        try:
            # Raw API call — avoids SDK pydantic deserialization bug (Issue #9)
            # SDK typed get_positions() returns broken pydantic objects with None fields
            resp = self.client._portfolio_api.get_positions_without_preload_content(limit=100)
            raw_data = json.loads(resp.read())

            # Schema validation
            _KNOWN_POS_KEYS = ("event_positions", "positions", "market_positions")
            _EMPTY_ONLY_KEYS = {"cursor"}  # Kalshi returns only cursor when portfolio is empty

            if raw_data and not any(k in raw_data for k in _KNOWN_POS_KEYS):
                if not set(raw_data.keys()) <= _EMPTY_ONLY_KEYS:
                    raise RuntimeError(
                        f"SCHEMA DRIFT: Kalshi API response has none of the expected position keys. "
                        f"Got: {sorted(raw_data.keys())}. Expected one of: {_KNOWN_POS_KEYS}. "
                        f"Kalshi changed their API — fix field names in portfolio_drift.py."
                    )

            raw_positions = (
                raw_data.get("event_positions")
                or raw_data.get("positions")
                or raw_data.get("market_positions")
                or []
            )

            # Index by market ticker, filter out zero-quantity positions
            positions = {}
            for pos in raw_positions:
                pos = _normalize_position(pos)
                ticker = pos.get("ticker") or pos.get("market_ticker") or "unknown"
                side = pos.get("side", "unknown")
                # v3 API: position_fp (float string), v2: position (int)
                _pos_val = pos.get("position_fp") or pos.get("position") or pos.get("total_traded") or pos.get("shares", 0)
                try:
                    shares = float(_pos_val or 0)
                except (ValueError, TypeError):
                    shares = 0.0

                if shares == 0.0:
                    continue  # Skip settled/zero positions

                avg_price = float(pos.get("average_price", pos.get("avg_price", 0)) or 0)
                pnl = float(pos.get("realized_pnl", pos.get("pnl", 0)) or 0)

                positions[ticker] = {
                    "side": side,
                    "shares": shares,
                    "avg_price": avg_price,
                    "pnl": pnl,
                    "pnl_percent": 0.0,
                    "risk": 0.0,
                    "timestamp": datetime.utcnow().isoformat()
                }

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "positions": positions,
                "total_positions": len(positions)
            }
        except Exception as e:
            raise RuntimeError(f"Failed to fetch positions from Kalshi: {e}")

    def load_portfolio_snapshot(self) -> Dict[str, Any]:
        """
        Load last saved portfolio snapshot.

        Returns:
            Previous portfolio state, or empty dict if no snapshot exists
        """
        if not self.state_file.exists():
            return {}

        try:
            with open(self.state_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"WARNING: Failed to load snapshot: {e}")
            return {}

    def save_portfolio_snapshot(self, portfolio: Dict[str, Any]) -> None:
        """
        Save current portfolio as baseline for next check.

        Args:
            portfolio: Current portfolio state from get_current_portfolio()
        """
        try:
            with open(self.state_file, "w") as f:
                json.dump(portfolio, f, indent=2)
        except Exception as e:
            print(f"ERROR: Failed to save snapshot: {e}")

    def should_check_now(self, last_snapshot: Dict[str, Any]) -> bool:
        """
        Check if enough time has elapsed for next check (rate limiting).

        Args:
            last_snapshot: Previous portfolio state

        Returns:
            True if interval has elapsed or no previous snapshot, False otherwise
        """
        if not last_snapshot or "timestamp" not in last_snapshot:
            return True

        try:
            last_time = datetime.fromisoformat(last_snapshot["timestamp"])
            elapsed = datetime.utcnow() - last_time
            return elapsed >= timedelta(minutes=self.interval_minutes)
        except Exception:
            return True

    def calculate_drift(self, current: Dict[str, Any], previous: Dict[str, Any]) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Compare current and previous positions to detect drift.

        Args:
            current: Current portfolio from get_current_portfolio()
            previous: Previous portfolio snapshot

        Returns:
            List of (symbol, percent_change, details) tuples for positions exceeding threshold
        """
        current_pos = current.get("positions", {})
        prev_pos = previous.get("positions", {})

        drifted = []

        # Check all positions (current and previous)
        all_symbols = set(current_pos.keys()) | set(prev_pos.keys())

        for symbol in all_symbols:
            curr = current_pos.get(symbol, {})
            prev = prev_pos.get(symbol, {})

            # Calculate changes in key metrics
            changes = {}
            max_drift = 0.0

            # Shares drift
            curr_shares = curr.get("shares", 0)
            prev_shares = prev.get("shares", 0)
            if prev_shares != 0:
                share_drift = abs((curr_shares - prev_shares) / prev_shares * 100)
                changes["shares"] = (curr_shares - prev_shares, share_drift)
                max_drift = max(max_drift, share_drift)

            # P&L drift
            curr_pnl = curr.get("pnl", 0)
            prev_pnl = prev.get("pnl", 0)
            if prev_pnl != 0:
                pnl_drift = abs((curr_pnl - prev_pnl) / prev_pnl * 100)
                changes["pnl"] = (curr_pnl - prev_pnl, pnl_drift)
                max_drift = max(max_drift, pnl_drift)

            # Price drift (avg entry)
            curr_price = curr.get("avg_price", 0)
            prev_price = prev.get("avg_price", 0)
            if prev_price != 0:
                price_drift = abs((curr_price - prev_price) / prev_price * 100)
                changes["price"] = (curr_price - prev_price, price_drift)
                max_drift = max(max_drift, price_drift)

            # Flag if exceeds threshold
            if max_drift >= self.threshold_pct:
                drifted.append((symbol, max_drift, {
                    "current": curr,
                    "previous": prev,
                    "changes": changes
                }))

        return drifted

    def format_drift_alert(self, symbol: str, drift_pct: float, details: Dict[str, Any]) -> str:
        """
        Format drift detection as readable alert.

        Args:
            symbol: Market symbol
            drift_pct: Percentage change
            details: Position details with current/previous/changes

        Returns:
            Formatted alert string with emoji indicators
        """
        curr = details.get("current", {})
        prev = details.get("previous", {})
        changes = details.get("changes", {})

        # Determine direction
        curr_pnl = curr.get("pnl", 0)
        prev_pnl = prev.get("pnl", 0)
        direction_emoji = "📈" if curr_pnl >= prev_pnl else "📉"
        arrow = "↑" if curr_pnl >= prev_pnl else "↓"

        # Side indicator
        side = curr.get("side", "?")

        # Build change details
        change_strs = []

        if "pnl" in changes:
            pnl_change, _ = changes["pnl"]
            change_strs.append(f"{arrow}${abs(pnl_change):.0f} P&L")

        if "shares" in changes:
            share_change, _ = changes["shares"]
            change_strs.append(f"{arrow}{abs(share_change):.0f} shares")

        change_detail = ", ".join(change_strs) if change_strs else "position change"

        # Calculate minutes since last check
        try:
            prev_time = datetime.fromisoformat(prev.get("timestamp", ""))
            minutes_ago = int((datetime.utcnow() - prev_time).total_seconds() / 60)
            time_str = f"Last check: {minutes_ago} minutes ago"
        except Exception:
            time_str = "Last check: unknown time"

        return f"{direction_emoji} {side}/{symbol} → +{drift_pct:.1f}% ({change_detail})\n   {time_str}"

    def _preflight_schema_check(self) -> None:
        """Verify Kalshi API response schema before running drift check.

        Uses raw API call (not SDK typed method) to fetch 1 position and assert
        expected keys exist. Raises RuntimeError if schema has drifted.
        """
        try:
            resp = self.client._portfolio_api.get_positions_without_preload_content(limit=1)
            data = json.loads(resp.read())

            _KNOWN_POS_KEYS = ("event_positions", "positions", "market_positions")
            _EMPTY_ONLY_KEYS = {"cursor"}  # Kalshi returns only cursor when portfolio is empty
            if data and not any(k in data for k in _KNOWN_POS_KEYS):
                if set(data.keys()) <= _EMPTY_ONLY_KEYS:
                    return  # Empty portfolio, schema is fine
                raise RuntimeError(
                    f"SCHEMA DRIFT DETECTED: Kalshi API response contains none of the expected "
                    f"position keys {_KNOWN_POS_KEYS}. Got: {sorted(data.keys())}. "
                    f"Kalshi changed their API — update field names in portfolio_drift.py before "
                    f"the drift monitor silently reports empty portfolios."
                )
        except RuntimeError:
            raise  # re-raise schema drift errors
        except Exception as e:
            # Non-schema errors (auth, network) are handled downstream — don't block startup
            print(f"WARNING: Preflight schema check skipped: {e}")

    def run(self) -> None:
        """Execute portfolio drift check and output alerts."""
        # Preflight: verify API schema hasn't changed
        self._preflight_schema_check()

        # Load previous snapshot
        previous_snapshot = self.load_portfolio_snapshot()

        # Check rate limit
        if not self.should_check_now(previous_snapshot):
            try:
                prev_time = datetime.fromisoformat(previous_snapshot["timestamp"])
                elapsed = datetime.utcnow() - prev_time
                remaining = self.interval_minutes - int(elapsed.total_seconds() / 60)
                print(f"Rate limited: next check in {remaining} minutes")
            except Exception:
                print("Rate limited: check again soon")
            return

        # Fetch current portfolio
        try:
            current_portfolio = self.get_current_portfolio()
        except Exception as e:
            print(f"ERROR: {e}")
            return

        # Handle empty portfolio
        if current_portfolio.get("total_positions", 0) == 0:
            print("Portfolio is empty — no positions to monitor")
            self.save_portfolio_snapshot(current_portfolio)
            return

        # First run: establish baseline
        if not previous_snapshot:
            print(f"✅ Baseline established: {current_portfolio['total_positions']} positions recorded")
            self.save_portfolio_snapshot(current_portfolio)
            return

        # Detect drift
        drifted_positions = self.calculate_drift(current_portfolio, previous_snapshot)

        if drifted_positions:
            print("🚨 Portfolio Drift Alert\n")
            for symbol, drift_pct, details in drifted_positions:
                print(self.format_drift_alert(symbol, drift_pct, details))

            print("\n---")
            stable_count = current_portfolio["total_positions"] - len(drifted_positions)
            if stable_count > 0:
                stable_symbols = [
                    s for s in current_portfolio["positions"].keys()
                    if not any(s == sym for sym, _, _ in drifted_positions)
                ]
                print(f"✓ Stable ({stable_count}): {', '.join(stable_symbols[:5])}")
        else:
            print(f"✓ No drift detected ({current_portfolio['total_positions']} positions stable)")

        # Update snapshot for next check
        self.save_portfolio_snapshot(current_portfolio)


def main():
    """Entry point."""
    try:
        monitor = PortfolioDriftMonitor()
        monitor.run()
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(130)
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
