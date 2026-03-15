#!/usr/bin/env python3
"""
ACT-R Temporal Decay Scorer
=============================

Implements ACT-R base-level activation formula for NIMA memory retrieval.

Formula:
    B_i = ln(Σ t_j^(-d))

Where:
    - B_i = base-level activation of memory i
    - t_j = time (seconds) since j-th access
    - d   = decay rate (default 0.5)

References:
    Anderson, J. R., & Lebiere, C. (1998). The Atomic Components of Thought.
    Erlbaum Associates, Mahwah, NJ.

Usage:
    from storage.temporal_decay import ACTRDecayScorer
    scorer = ACTRDecayScorer()           # uses NIMA_HOME / ~/.nima
    scorer.record_access("memory_id")
    score = scorer.compute_activation("memory_id")  # 0.0–1.0
"""

import sqlite3
import math
import time
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class ACTRDecayScorer:
    """
    Persistent ACT-R-based temporal decay scorer.

    Tracks memory access history and computes activation scores.
    All SQL uses parameterised queries — no user data is interpolated into
    SQL text, so SQL-injection is structurally impossible.

    Thread safety: each public method opens/closes its own connection
    (safe for multi-threaded use; SQLite WAL handles concurrent writes).
    """

    DEFAULT_DECAY_RATE = 0.5
    MIN_ACTIVATION = 0.0
    MAX_ACTIVATION = 1.0

    def __init__(
        self,
        decay_rate: float = DEFAULT_DECAY_RATE,
        db_path: Optional[str] = None,
    ):
        """
        Initialize scorer.

        Args:
            decay_rate: ACT-R decay parameter d (default 0.5).
            db_path:    Path to the ACT-R SQLite database.
                        Defaults to  $NIMA_HOME/memory/actr_state.db
                        (NIMA_HOME defaults to ~/.nima).
        """
        self.decay_rate = decay_rate
        if self.decay_rate <= 0:
            raise ValueError("decay_rate must be > 0")

        if db_path is None:
            nima_home = Path(
                os.path.expanduser(os.environ.get("NIMA_HOME", "~/.nima"))
            )
            self.db_path = nima_home / "memory" / "actr_state.db"
        else:
            self.db_path = Path(db_path)

        self._ensure_db()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_db(self) -> None:
        """Create database and tables if they do not exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS actr_accesses (
                    node_id     TEXT NOT NULL,
                    access_time REAL NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_actr_node_id
                ON actr_accesses (node_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_actr_access_time
                ON actr_accesses (access_time)
            """)
            conn.commit()
        finally:
            conn.close()

    # Maximum allowed length for a node_id string.
    # Prevents unbounded-storage DoS via very long identifiers.
    MAX_NODE_ID_LEN = 256

    @staticmethod
    def _validate_node_id(node_id: object) -> bool:
        """Return True iff node_id is a non-empty string within length bounds."""
        return (
            isinstance(node_id, str)
            and bool(node_id)
            and len(node_id) <= ACTRDecayScorer.MAX_NODE_ID_LEN
        )

    @staticmethod
    def _compute_raw_activation(access_times: List[float], decay_rate: float) -> float:
        """
        Core ACT-R formula on a list of Unix timestamps.

        Returns the *raw* (un-normalised) activation value, or 0.0 when
        access_times is empty.
        """
        if not access_times:
            return 0.0
        now = time.time()
        total = sum(
            math.pow(max(now - t, 1.0), -decay_rate)
            for t in access_times
        )
        return math.log(total) if total > 0 else 0.0

    @staticmethod
    def _normalise(raw: float) -> float:
        """
        Map raw activation to [0.0, 1.0].

        Heuristic: raw values span roughly −5 … +5 for realistic access
        histories, so shifting by 5 and dividing by 10 gives a sensible
        linear mapping.  Values are clamped to [0, 1].
        """
        return min(max((raw + 5.0) / 10.0, 0.0), 1.0)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def record_access(self, node_id: str) -> None:
        """
        Record one access event for *node_id*.

        Args:
            node_id: Memory node identifier (must be a non-empty string).
        """
        if not self._validate_node_id(node_id):
            return

        access_time = time.time()
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        try:
            conn.execute(
                "INSERT INTO actr_accesses (node_id, access_time) VALUES (?, ?)",
                (node_id, access_time),
            )
            conn.commit()
        except sqlite3.Error as exc:
            # Log but do not raise — callers should not crash on metric errors.
            logger.warning("[ACTR] record_access error: %s", exc)
        finally:
            conn.close()

    def compute_activation(self, node_id: str) -> float:
        """
        Compute normalised ACT-R activation score for a single memory.

        Args:
            node_id: Memory node identifier.

        Returns:
            Float in [0.0, 1.0].  Returns 0.0 for unknown / invalid nodes.
            Note: a node with zero accesses returns 0.0 exactly (not 0.5),
            to distinguish "never seen" from "seen once long ago".
        """
        if not self._validate_node_id(node_id):
            return 0.0

        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        try:
            cursor = conn.execute(
                "SELECT access_time FROM actr_accesses WHERE node_id = ?",
                (node_id,),
            )
            access_times = [row[0] for row in cursor.fetchall()]
            if not access_times:
                return 0.0  # Never accessed — structurally distinct from low activation
            return self._normalise(
                self._compute_raw_activation(access_times, self.decay_rate)
            )
        except sqlite3.Error as exc:
            logger.warning("[ACTR] compute_activation error: %s", exc)
            return 0.0
        finally:
            conn.close()

    def compute_batch(self, node_ids: List[str]) -> Dict[str, float]:
        """
        Compute activation scores for multiple nodes in one DB round-trip.

        Args:
            node_ids: List of memory node identifiers (duplicates allowed).

        Returns:
            Dict mapping each unique node_id → normalised score.
        """
        if not node_ids:
            return {}

        # Validate and deduplicate while preserving input-order uniqueness.
        unique_ids = list(dict.fromkeys(
            n for n in node_ids if self._validate_node_id(n)
        ))
        if not unique_ids:
            return {}

        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        try:
            placeholders = ",".join("?" * len(unique_ids))
            cursor = conn.execute(
                f"SELECT node_id, access_time FROM actr_accesses"
                f" WHERE node_id IN ({placeholders})"
                f" ORDER BY node_id, access_time DESC",
                unique_ids,
            )

            # Group access times by node.
            accesses: Dict[str, List[float]] = {}
            for nid, ts in cursor.fetchall():
                accesses.setdefault(nid, []).append(ts)

            return {
                nid: (
                    self._normalise(
                        self._compute_raw_activation(accesses[nid], self.decay_rate)
                    )
                    if nid in accesses else 0.0  # Never accessed → 0.0 exactly
                )
                for nid in unique_ids
            }
        except sqlite3.Error as exc:
            logger.warning("[ACTR] compute_batch error: %s", exc)
            return {nid: 0.0 for nid in unique_ids}
        finally:
            conn.close()

    def get_top_activated(
        self,
        node_ids: Optional[List[str]] = None,
        top_k: int = 20,
    ) -> List[Tuple[str, float]]:
        """
        Return the *top_k* most-activated memories.

        Args:
            node_ids: Optional whitelist.  If *None*, all stored nodes are
                      considered.
            top_k:    Maximum number of results to return.

        Returns:
            List of ``(node_id, score)`` tuples, sorted descending by score.
        """
        if node_ids is not None:
            scores = self.compute_batch(node_ids)
        else:
            conn = sqlite3.connect(str(self.db_path), timeout=10.0)
            try:
                cursor = conn.execute(
                    "SELECT DISTINCT node_id FROM actr_accesses"
                )
                all_ids = [row[0] for row in cursor.fetchall()]
            except sqlite3.Error:
                return []
            finally:
                conn.close()
            scores = self.compute_batch(all_ids)

        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    def prune_old_accesses(self, max_age_days: int = 365) -> int:
        """
        Delete access records older than *max_age_days*.

        Args:
            max_age_days: Records older than this many days are deleted.

        Returns:
            Number of deleted rows.
        """
        cutoff = time.time() - (max_age_days * 86_400)
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        count = 0
        try:
            cursor = conn.execute(
                "DELETE FROM actr_accesses WHERE access_time < ?",
                (cutoff,),
            )
            # rowcount can be -1 on some SQLite builds — use a fallback.
            count = cursor.rowcount if cursor.rowcount >= 0 else 0
            conn.commit()
        except sqlite3.Error as exc:
            logger.warning("[ACTR] prune_old_accesses error: %s", exc)
        finally:
            conn.close()

        # VACUUM reclaims disk space but requires an exclusive lock.
        # Attempt it best-effort; never raise on failure.
        if count > 0:
            try:
                vconn = sqlite3.connect(str(self.db_path), timeout=3.0)
                try:
                    vconn.execute("VACUUM")
                finally:
                    vconn.close()
            except sqlite3.Error:
                pass  # Non-critical — space reclaimed on next successful VACUUM

        return count

    def get_stats(self) -> Dict:
        """
        Return summary statistics for the access table.

        Returns:
            Dict with keys: total_accesses, unique_nodes, oldest, newest.
        """
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        try:
            row = conn.execute(
                "SELECT COUNT(*), MIN(access_time), MAX(access_time)"
                " FROM actr_accesses"
            ).fetchone()
            total = row[0] or 0
            oldest = row[1]
            newest = row[2]

            unique = conn.execute(
                "SELECT COUNT(DISTINCT node_id) FROM actr_accesses"
            ).fetchone()[0] or 0

            return {
                "total_accesses": total,
                "unique_nodes": unique,
                "oldest": (
                    datetime.fromtimestamp(oldest).isoformat() if oldest else None
                ),
                "newest": (
                    datetime.fromtimestamp(newest).isoformat() if newest else None
                ),
            }
        except sqlite3.Error as exc:
            logger.warning("[ACTR] get_stats error: %s", exc)
            return {
                "total_accesses": 0,
                "unique_nodes": 0,
                "oldest": None,
                "newest": None,
            }
        finally:
            conn.close()


# ---------------------------------------------------------------------------
# Self-test (run with: python -m storage.temporal_decay)
# ---------------------------------------------------------------------------

def _run_tests() -> None:  # pragma: no cover
    """Smoke-test the ACTRDecayScorer."""
    import tempfile, shutil

    print("🧪 Running ACTRDecayScorer tests …")
    test_dir = tempfile.mkdtemp()
    test_db  = os.path.join(test_dir, "test_actr.db")

    try:
        s = ACTRDecayScorer(db_path=test_db)
        assert s.db_path == Path(test_db)
        print("  ✅ 1: init")

        s.record_access("m001")
        s.record_access("m001")
        s.record_access("m002")
        print("  ✅ 2: record_access")

        a001 = s.compute_activation("m001")
        a002 = s.compute_activation("m002")
        a999 = s.compute_activation("m999")
        assert a001 > 0 and a002 > 0 and a001 > a002 and a999 == 0.0
        print(f"  ✅ 3: activations (001={a001:.4f}, 002={a002:.4f}, 999={a999})")

        batch = s.compute_batch(["m001", "m002", "m999"])
        assert batch["m001"] > 0 and batch["m999"] == 0.0
        print("  ✅ 4: compute_batch")

        top = s.get_top_activated(top_k=2)
        assert top[0][0] == "m001"
        print(f"  ✅ 5: get_top_activated → {top}")

        stats = s.get_stats()
        assert stats["total_accesses"] == 3 and stats["unique_nodes"] == 2
        print(f"  ✅ 6: get_stats → {stats}")

        time.sleep(0.05)
        pruned = s.prune_old_accesses(max_age_days=0)
        assert pruned == 3
        assert s.get_stats()["total_accesses"] == 0
        print(f"  ✅ 7: prune_old_accesses ({pruned} rows)")

        print("\n🎉 All tests passed!")

    finally:
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    _run_tests()
