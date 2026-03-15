"""
crypto_momentum_plugin.py — Starter template for crypto shadow strategies.

Copy this file, rename your class, and implement the three methods.
The framework handles storage, variant tracking, stats, and promotion.
You provide the signal logic.

Example variant grid (generates 18 auto-named variants):
    param_grid = {
        "coin":      ["BTC", "ETH", "SOL"],
        "timeframe": ["5m", "15m", "1h"],
        "threshold": [0.02, 0.03],
    }
    # Produces: coinBTC_thre0.02_time5m, coinETH_thre0.03_time1h, etc.
"""

from shadow_plugin_base import StrategyPlugin, TradeSignal, ShadowTrade


class CryptoPlugin(StrategyPlugin):
    """
    Starter template for a crypto shadow strategy.

    Params to customize:
      - coin:      Target asset (e.g. "BTC", "ETH", "XRP", "SOL")
      - timeframe: Candle interval for your signal (e.g. "5m", "15m", "1h", "4h")
      - threshold: Your signal entry threshold (meaning depends on your signal logic)
      - min_volume: Minimum 24h market volume to consider

    Variant grid: define param_grid to auto-generate all combinations.
    """

    name = "crypto"  # Change this — must be unique per strategy

    default_params = {
        "coin": "BTC",
        "timeframe": "5m",
        "threshold": 0.03,
        "min_volume": 5000.0,
    }

    # Auto-generates all combinations as named variants.
    # Start small, expand once you have signal confidence.
    param_grid = {
        "coin": ["BTC", "ETH"],
        "timeframe": ["5m", "15m"],
        "threshold": [0.02, 0.03, 0.05],
    }

    # Promotion gates — don't promote until you have enough data
    min_n = 30
    min_wr = 0.58
    min_ev_delta = 0.02

    def get_markets(self, client=None) -> list[dict]:
        """
        Return crypto markets to evaluate.

        Recommended: use the fast-markets endpoint for BTC/ETH/XRP/SOL —
        these aren't reliably available on the standard active markets list.

        client is a SimmerClient instance. Use it to discover markets.
        Filter by coin, time-to-resolution, or whatever criteria fit your strategy.

        Example (implement your own filtering):
            markets = client.get_fast_markets(asset=params["coin"])
            return [m for m in markets if <your filter>]
        """
        raise NotImplementedError("Implement get_markets() with your market discovery logic")

    def evaluate(self, market: dict, params: dict) -> TradeSignal | None:
        """
        Evaluate a single market and decide whether to shadow-trade it.

        Return a TradeSignal if your signal fires, None to skip.

        Typical pattern:
          1. Fetch your signal data (price feed, klines, on-chain data, etc.)
          2. Apply your entry logic with params["threshold"]
          3. Check market volume >= params["min_volume"]
          4. Return TradeSignal(...) or None

        market fields from fast-markets:
          market["id"]                  — market UUID
          market["current_probability"] — current YES price (0–1)
          market["question"]            — market title
          market["resolves_at"]         — resolution timestamp
          market["is_live_now"]         — True for currently active sprint markets
          (and others — inspect the response from your get_markets() call)
        """
        raise NotImplementedError("Implement evaluate() with your signal logic")

    def is_win(self, trade: ShadowTrade, market: dict | None = None) -> bool | None:
        """
        Check if a shadow trade resolved as a win.

        Return True (win), False (loss), or None (unresolved / skip).

        The framework calls cmd_resolve to fetch resolved positions and passes
        the resolved market data here. Use trade.side and the resolved outcome
        to determine win/loss.

        Example:
            if market is None:
                return None
            outcome = market.get("outcome", "").lower()   # "yes" or "no"
            if not outcome:
                return None
            return outcome == trade.side.lower()
        """
        raise NotImplementedError("Implement is_win() with your resolution logic")
