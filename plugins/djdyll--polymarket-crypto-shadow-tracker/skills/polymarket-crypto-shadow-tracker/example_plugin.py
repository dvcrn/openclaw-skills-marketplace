"""
example_plugin.py — Example shadow tracker plugin using SimmerClient.

Shows how to fetch markets, evaluate signals, and check resolution.
Replace the logic with your own strategy — this is a starting point.

SimmerClient SDK reference (v0.9.5):
    Market fields: id, question, status, current_probability, resolves_at,
                   liquidity_tier, import_source, is_live_now
    client.get_markets(status="active") → list[Market]
    client.get_market_by_id(market_id) → Market | None
    client.get_positions() → list[Position]
"""

from shadow_plugin_base import StrategyPlugin, TradeSignal, ShadowTrade


class ExampleStrategy(StrategyPlugin):
    name = "example"

    default_params = {
        "threshold": 0.18,
        "min_probability": 0.05,
    }

    # Framework auto-generates all combos: 3 × 2 = 6 variants
    param_grid = {
        "threshold": [0.15, 0.18, 0.20],
        "min_probability": [0.05, 0.10],
    }

    # Promotion thresholds
    min_n = 20
    min_wr = 0.55
    min_ev_delta = 0.02

    def get_markets(self, client=None) -> list[dict]:
        """
        Fetch active markets via SimmerClient.
        Convert Market objects to dicts for evaluate().
        """
        if client is None:
            return []

        markets = client.get_markets(status="active")
        return [
            {
                "id": m.id,
                "question": m.question,
                "price": m.current_probability,
                "status": m.status,
                "resolves_at": getattr(m, "resolves_at", None),
                "liquidity_tier": getattr(m, "liquidity_tier", None),
            }
            for m in markets
        ]

    def evaluate(self, market: dict, params: dict) -> TradeSignal | None:
        """
        Example signal: buy YES when probability is below threshold
        but above a minimum floor.
        """
        price = market.get("price", 0)

        if price < params["min_probability"]:
            return None

        if price < params["threshold"]:
            return TradeSignal(
                market_id=market["id"],
                side="YES",
                entry_price=price,
                signal=f"price {price:.2f} < threshold {params['threshold']:.2f}",
            )

        return None

    def is_win(self, trade: ShadowTrade, market: dict | None = None) -> bool | None:
        """
        Check resolution via market status.
        The framework fetches market data via client.get_market_by_id()
        and passes it here.

        Market.status will be "resolved" when the market has settled.
        For actual outcome checking, you'd need to cross-reference with
        positions API or market context — adapt to your strategy's needs.
        """
        if market is None:
            return None
        if market.get("status") != "resolved":
            return None
        # Placeholder: in a real plugin, check the resolved outcome
        # against trade.side. The positions API (/api/sdk/positions?status=resolved)
        # returns an "outcome" field with "yes" or "no".
        return None  # Replace with actual resolution logic
