"""
shadow_plugin_base.py — Base class and data types for shadow tracker plugins.

Subclass StrategyPlugin and implement the three methods to create a strategy.

Part of the polymarket-crypto-shadow-tracker skill.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from itertools import product
from typing import Any


@dataclass
class TradeSignal:
    """Represents a shadow trade signal emitted by a plugin."""
    market_id: str
    side: str              # "YES" or "NO"
    entry_price: float     # price at signal time (0-1)
    signal: str            # human-readable reason
    meta: dict = field(default_factory=dict)  # arbitrary extra data

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ShadowTrade:
    """A logged shadow trade entry."""
    variant: str
    market_id: str
    side: str
    entry_price: float
    signal: str
    params: dict
    timestamp: str
    resolved: bool = False
    outcome: str | None = None   # "win" | "loss" | None
    payout: float | None = None  # net payout per dollar risked
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> ShadowTrade:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class StrategyPlugin(ABC):
    """
    Base class for shadow tracker strategy plugins.

    Subclasses must set:
        name: str           — unique strategy identifier
        default_params: dict — default parameter values
        param_grid: dict    — {param_name: [values]} for variant generation
                              (leave empty to run default_params only)

    And implement:
        get_markets(client)  — return list of market dicts to evaluate.
                               `client` is a SimmerClient instance (from simmer_sdk).
        evaluate(market, params) — return TradeSignal or None
        is_win(trade, market)    — return True/False/None (None = unresolved)
    """

    name: str = "unnamed"
    default_params: dict = {}
    param_grid: dict = {}       # e.g. {"threshold": [0.15, 0.18], "ratio": [1.0, 1.5]}

    # Promotion thresholds (override per-plugin or via CLI)
    min_n: int = 20
    min_wr: float = 0.55
    min_ev_delta: float = 0.02  # vs baseline variant

    def variants(self) -> list[tuple[str, dict]]:
        """Generate all (variant_name, params) combinations from param_grid."""
        if not self.param_grid:
            return [("default", dict(self.default_params))]

        keys = sorted(self.param_grid.keys())
        combos = list(product(*(self.param_grid[k] for k in keys)))
        results = []
        for combo in combos:
            params = dict(self.default_params)
            parts = []
            for k, v in zip(keys, combo):
                params[k] = v
                short = k[:4].replace("_", "")
                parts.append(f"{short}{v}")
            variant_name = "_".join(parts)
            results.append((variant_name, params))
        return results

    @abstractmethod
    def get_markets(self, client: Any = None) -> list[dict]:
        """Return markets to evaluate. `client` is a SimmerClient instance."""
        ...

    @abstractmethod
    def evaluate(self, market: dict, params: dict) -> TradeSignal | None:
        """Evaluate a market with given params. Return TradeSignal or None."""
        ...

    @abstractmethod
    def is_win(self, trade: ShadowTrade, market: dict | None = None) -> bool | None:
        """Check if a trade won. Return True/False or None if unresolved."""
        ...
