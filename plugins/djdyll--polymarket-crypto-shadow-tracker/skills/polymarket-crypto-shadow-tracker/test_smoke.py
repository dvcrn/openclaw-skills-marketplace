#!/usr/bin/env python3
"""Smoke tests for polymarket-crypto-shadow-tracker. No real API key needed."""

import json
import os
import sys
import tempfile

# Ensure we can import from this directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock simmer_sdk.skill before importing shadow_tracker
import types
mock_skill = types.ModuleType("simmer_sdk.skill")
mock_skill.load_config = lambda schema, f, slug=None: {k: v["default"] for k, v in schema.items()}
mock_skill.update_config = lambda updates, f: updates
mock_skill.get_config_path = lambda f: "/tmp/mock_config.json"
sys.modules["simmer_sdk.skill"] = mock_skill
sys.modules.setdefault("simmer_sdk", types.ModuleType("simmer_sdk"))

passed = 0
failed = 0

def test(name):
    global passed, failed
    class _T:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, tb):
            global passed, failed
            if exc_type:
                print(f"FAIL [{name}]: {exc_val}")
                failed += 1
                return True  # suppress
            else:
                print(f"PASS [{name}]")
                passed += 1
    return _T()

# ─── Test 1: Plugin loads ───
with test("1. plugin loads"):
    from shadow_tracker import load_plugin
    plugin = load_plugin("crypto_momentum_plugin.py")
    assert plugin.name == "crypto", f"Expected 'crypto', got '{plugin.name}'"

# ─── Test 2: Variant generation ───
with test("2. variant generation"):
    variants = plugin.variants()
    assert len(variants) > 0, "No variants generated"
    assert len(variants) == 12, f"Expected 12 variants (2×2×3), got {len(variants)}"
    for name, params in variants:
        assert "_" in name, f"Variant name missing underscore: {name}"
        assert isinstance(params, dict)
    print(f"  {len(variants)} variants, sample: {[v[0] for v in variants[:5]]}")

# ─── Test 3: Dedup logic ───
with test("3. dedup"):
    from shadow_plugin_base import ShadowTrade
    from shadow_tracker import existing_keys
    t1 = ShadowTrade(variant="test", market_id="abc", side="YES", entry_price=0.5,
                     signal="x", params={}, timestamp="2026-01-01")
    keys = existing_keys([t1])
    assert "test:abc" in keys, f"Expected 'test:abc' in keys, got {keys}"

# ─── Test 4: JSONL roundtrip ───
with test("4. JSONL roundtrip"):
    trade = ShadowTrade(variant="coinBTC_time5m_thre0.02", market_id="uuid-123",
                        side="YES", entry_price=0.42, signal="test signal",
                        params={"coin": "BTC"}, timestamp="2026-03-14T00:00:00+00:00")
    line = trade.to_json()
    restored = ShadowTrade.from_dict(json.loads(line))
    assert restored.variant == trade.variant
    assert restored.market_id == trade.market_id
    assert restored.entry_price == trade.entry_price
    assert restored.params == trade.params

# ─── Test 5: Stats math ───
with test("5. stats math"):
    from shadow_tracker import compute_stats
    trades = [
        ShadowTrade("default", "m1", "YES", 0.4, "s", {}, "t", resolved=True, outcome="win", payout=1.5),
        ShadowTrade("default", "m2", "YES", 0.5, "s", {}, "t", resolved=True, outcome="win", payout=1.0),
        ShadowTrade("default", "m3", "YES", 0.6, "s", {}, "t", resolved=True, outcome="loss", payout=-1.0),
        ShadowTrade("default", "m4", "YES", 0.3, "s", {}, "t", resolved=False),
    ]
    stats = compute_stats(trades)
    vs = stats["default"]
    assert vs.n == 4, f"n={vs.n}"
    assert vs.wins == 2, f"wins={vs.wins}"
    assert vs.losses == 1, f"losses={vs.losses}"
    assert vs.unresolved == 1, f"unresolved={vs.unresolved}"
    assert vs.resolved == 3, f"resolved={vs.resolved}"
    assert abs(vs.wr - 2/3) < 0.001, f"wr={vs.wr}"
    print(f"  WR={vs.wr:.3f}, EV={vs.ev:.3f}")

# ─── Test 6: Promote gate logic ───
with test("6. promote gates"):
    from shadow_tracker import cmd_promote
    # Create a plugin-like object with mock data
    from shadow_plugin_base import StrategyPlugin
    
    class MockPlugin(StrategyPlugin):
        name = "test_promote"
        min_n = 5
        min_wr = 0.55
        min_ev_delta = 0.01
        def get_markets(self, client=None): return []
        def evaluate(self, market, params): return None
        def is_win(self, trade, market=None): return None

    # Write test trades to temp dir
    import shadow_tracker as st
    old_data_dir = st.DATA_DIR
    with tempfile.TemporaryDirectory() as tmpdir:
        st.DATA_DIR = type(old_data_dir)(tmpdir)
        test_trades = [
            ShadowTrade("default", f"m{i}", "YES", 0.5, "s", {}, "t",
                        resolved=True, outcome="win", payout=0.5)
            for i in range(10)
        ] + [
            ShadowTrade("default", f"l{i}", "YES", 0.5, "s", {}, "t",
                        resolved=True, outcome="loss", payout=-1.0)
            for i in range(5)
        ] + [
            ShadowTrade("variant_a", f"m{i}", "YES", 0.4, "s", {"x": 1}, "t",
                        resolved=True, outcome="win", payout=0.8)
            for i in range(8)
        ] + [
            ShadowTrade("variant_a", f"l{i}", "YES", 0.4, "s", {"x": 1}, "t",
                        resolved=True, outcome="loss", payout=-1.0)
            for i in range(2)
        ]
        st.write_trades("test_promote", test_trades)
        mp = MockPlugin()
        # Should print promotion analysis without crashing
        cmd_promote(mp, variant="variant_a")
        st.DATA_DIR = old_data_dir

# ─── Test 7: CLI help (already tested via shell) ───
with test("7. CLI help"):
    # Just verify argparse doesn't crash on import
    import shadow_tracker
    assert hasattr(shadow_tracker, 'main')

# ─── Test 8: Missing API key ───
with test("8. missing API key clean error"):
    # get_client() should sys.exit with clean message when no key
    old_key = os.environ.pop("SIMMER_API_KEY", None)
    from shadow_tracker import get_client
    import shadow_tracker as st
    st._client = None  # reset singleton
    try:
        get_client()
        assert False, "Should have exited"
    except SystemExit:
        pass  # clean exit, good
    finally:
        if old_key:
            os.environ["SIMMER_API_KEY"] = old_key
        st._client = None

# ─── Test 9: Empty JSONL / no data ───
with test("9. empty data"):
    old_data_dir = st.DATA_DIR
    with tempfile.TemporaryDirectory() as tmpdir:
        st.DATA_DIR = type(old_data_dir)(tmpdir)
        from shadow_tracker import cmd_stats
        cmd_stats(plugin)  # should print "No shadow trades" not crash
        st.DATA_DIR = old_data_dir

# ─── Test 10: Plugin with no param_grid ───
with test("10. no param_grid (default only)"):
    class MinimalPlugin(StrategyPlugin):
        name = "minimal"
        default_params = {"x": 1}
        param_grid = {}
        def get_markets(self, client=None): return []
        def evaluate(self, market, params): return None
        def is_win(self, trade, market=None): return None
    
    mp = MinimalPlugin()
    variants = mp.variants()
    assert len(variants) == 1, f"Expected 1 variant, got {len(variants)}"
    assert variants[0][0] == "default", f"Expected 'default', got '{variants[0][0]}'"
    assert variants[0][1] == {"x": 1}

# ─── Summary ───
print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed")
if failed:
    sys.exit(1)
else:
    print("All tests PASS ✓")
