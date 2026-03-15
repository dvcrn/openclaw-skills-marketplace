"""
Bayesian Confidence Scorer — NIMA v3.3.0

Tracks per-memory recall success/failure using a Beta distribution posterior.
Provides confidence estimates that improve with evidence and decay with
failures, complementing ACT-R temporal decay in the retrieval ranking formula.

Math:
    confidence = (successes + 1) / (total + 2)    # Laplace smoothing
    - New memory:         1/2 = 0.50  (neutral prior)
    - Recalled 10×, 0 failures: 11/12 = 0.92
    - Recalled 5×, 5 dismissed:   6/12 = 0.50  (reset to neutral)
    - Dismissed 5×, 0 success:    1/7  = 0.14  (low confidence)

Integrates with lazy_recall.py via:
    final_score = actr_score * 0.50 + bayes_confidence * 0.30 + fe_score * 0.20
"""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

MAX_NODE_ID_LEN = 256
NIMA_HOME_DEFAULT = str(Path.home() / ".nima")


class BayesianScorer:
    """
    Beta-distribution confidence scorer for NIMA memory nodes.

    Maintains a lightweight SQLite table (separate from graph.sqlite by default,
    or can share the same path) tracking recall outcomes per node_id.

    Usage::

        scorer = BayesianScorer()
        # After a successful recall:
        conf = scorer.record_recall(node_id, success=True)
        # After user ignores / dismisses a surfaced memory:
        conf = scorer.record_recall(node_id, success=False)
        # At retrieval time:
        conf = scorer.get_confidence(node_id)  # 0.5 if unseen
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize BayesianScorer with SQLite path, creating DB if needed."""
        if db_path is None:
            nima_home = os.environ.get("NIMA_HOME", NIMA_HOME_DEFAULT)
            db_path = str(Path(nima_home) / "memory" / "graph.sqlite")

        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    # ─── Internal ─────────────────────────────────────────────────────────────

    def _connect(self) -> sqlite3.Connection:
        """Return a context-managed SQLite connection."""
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Create bayes_scores table if not present."""
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bayes_scores (
                    node_id      TEXT PRIMARY KEY,
                    successes    INTEGER NOT NULL DEFAULT 0,
                    total        INTEGER NOT NULL DEFAULT 0,
                    confidence   REAL    NOT NULL DEFAULT 0.5,
                    last_updated TEXT
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_bayes_confidence"
                " ON bayes_scores(confidence)"
            )

    @staticmethod
    def _compute(successes: int, total: int) -> float:
        """Beta distribution posterior with Laplace smoothing."""
        return (successes + 1) / (total + 2)

    # ─── Write ────────────────────────────────────────────────────────────────

    def record_recall(self, node_id: str, success: bool = True) -> float:
        """
        Record a recall event for the given node.

        Args:
            node_id:  Memory node identifier (max 256 chars).
            success:  True if the recall was useful; False if dismissed/ignored.

        Returns:
            Updated confidence score (0.0–1.0).
        """
        if not node_id or len(node_id) > MAX_NODE_ID_LEN:
            raise ValueError(f"node_id must be 1–{MAX_NODE_ID_LEN} characters")

        now = datetime.now(timezone.utc).isoformat()
        try:
            with self._connect() as conn:
                # BEGIN IMMEDIATE serializes concurrent read-modify-write
                conn.execute("BEGIN IMMEDIATE")
                row = conn.execute(
                    "SELECT successes, total FROM bayes_scores WHERE node_id = ?",
                    (node_id,),
                ).fetchone()

                if row:
                    new_succ = int(row["successes"]) + (1 if success else 0)
                    new_total = int(row["total"]) + 1
                else:
                    new_succ = 1 if success else 0
                    new_total = 1

                confidence = self._compute(new_succ, new_total)

                conn.execute(
                    """INSERT INTO bayes_scores (node_id, successes, total, confidence, last_updated)
                       VALUES (?, ?, ?, ?, ?)
                       ON CONFLICT(node_id) DO UPDATE SET
                           successes    = excluded.successes,
                           total        = excluded.total,
                           confidence   = excluded.confidence,
                           last_updated = excluded.last_updated""",
                    (node_id, new_succ, new_total, confidence, now),
                )
                conn.execute("COMMIT")

            return confidence
        except Exception as exc:
            logger.warning("BayesianScorer.record_recall error: %s", exc)
            raise

    # ─── Read ─────────────────────────────────────────────────────────────────

    def get_confidence(self, node_id: str) -> float:
        """
        Return stored confidence for node_id, or 0.5 (neutral prior) if unseen.
        """
        if not node_id or len(node_id) > MAX_NODE_ID_LEN:
            return 0.5
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT confidence FROM bayes_scores WHERE node_id = ?",
                    (node_id,),
                ).fetchone()
                return float(row["confidence"]) if row else 0.5
        except Exception as exc:
            logger.warning("BayesianScorer.get_confidence error: %s", exc)
            return 0.5

    def get_batch_confidence(self, node_ids: list[str]) -> dict[str, float]:
        """
        Return confidence scores for multiple node IDs.
        Missing nodes get the neutral prior (0.5).

        Args:
            node_ids: List of memory node identifiers.

        Returns:
            Dict mapping each node_id → confidence.
        """
        if not node_ids:
            return {}
        valid = [n for n in node_ids if n and len(n) <= MAX_NODE_ID_LEN]
        result = {n: 0.5 for n in node_ids}
        if not valid:
            return result
        # SQLite parameter limit — chunk to avoid SQLITE_LIMIT_VARIABLE_NUMBER
        SQLITE_MAX_VARS = 999
        try:
            with self._connect() as conn:
                for i in range(0, len(valid), SQLITE_MAX_VARS):
                    chunk = valid[i : i + SQLITE_MAX_VARS]
                    placeholders = ",".join("?" * len(chunk))
                    rows = conn.execute(
                        f"SELECT node_id, confidence FROM bayes_scores"  # noqa: S608
                        f" WHERE node_id IN ({placeholders})",
                        chunk,
                    ).fetchall()
                    for row in rows:
                        result[row["node_id"]] = float(row["confidence"])
        except Exception as exc:
            logger.warning("BayesianScorer.get_batch_confidence error: %s", exc)
        return result

    def get_stats(self) -> dict:
        """Return aggregate statistics across all tracked nodes."""
        try:
            with self._connect() as conn:
                row = conn.execute("""
                    SELECT
                        COUNT(*)            AS total_nodes,
                        AVG(confidence)     AS avg_confidence,
                        MIN(confidence)     AS min_confidence,
                        MAX(confidence)     AS max_confidence,
                        SUM(successes)      AS total_successes,
                        SUM(total)          AS total_recalls
                    FROM bayes_scores
                """).fetchone()
                return dict(row) if row else {}
        except Exception as exc:
            logger.warning("BayesianScorer.get_stats error: %s", exc)
            return {}

    # ─── Management ───────────────────────────────────────────────────────────

    def reset_node(self, node_id: str) -> None:
        """Delete the Bayesian record for a node (fresh-start next recall)."""
        if not node_id or len(node_id) > MAX_NODE_ID_LEN:
            raise ValueError("invalid node_id")
        try:
            with self._connect() as conn:
                conn.execute(
                    "DELETE FROM bayes_scores WHERE node_id = ?", (node_id,)
                )
        except Exception as exc:
            logger.warning("BayesianScorer.reset_node error: %s", exc)

    def self_test(self) -> bool:
        """
        In-memory smoke test. Returns True if all operations pass.
        Safe to call in production health checks — uses a temp DB, not self.db_path.
        """
        import tempfile, os
        _tf = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        tmp = _tf.name
        _tf.close()
        try:
            scorer = BayesianScorer(db_path=tmp)

            # Neutral prior for unseen node
            assert scorer.get_confidence("unknown") == 0.5, "neutral prior failed"

            # Record successes — confidence should rise monotonically
            c1 = scorer.record_recall("node-A", success=True)
            c2 = scorer.record_recall("node-A", success=True)
            c3 = scorer.record_recall("node-A", success=True)
            assert c1 <= c2 <= c3, "confidence should rise monotonically with successes"
            assert c3 > c1, "confidence should rise with successes"

            # Record failures — confidence should fall below neutral
            f1 = scorer.record_recall("node-B", success=False)
            f2 = scorer.record_recall("node-B", success=False)
            assert f1 >= f2, "confidence should fall monotonically with failures"
            assert f2 < 0.5, "confidence should fall with failures"

            # Batch
            batch = scorer.get_batch_confidence(["node-A", "node-B", "node-C"])
            assert "node-A" in batch and "node-C" in batch
            assert batch["node-C"] == 0.5, "missing node should be neutral"

            # Stats
            stats = scorer.get_stats()
            assert stats["total_nodes"] == 2

            # Reset
            scorer.reset_node("node-A")
            assert scorer.get_confidence("node-A") == 0.5, "reset failed"

            return True
        except AssertionError as exc:
            logger.error("BayesianScorer.self_test assertion: %s", exc)
            return False
        except Exception as exc:
            logger.error("BayesianScorer.self_test error: %s", exc)
            return False
        finally:
            try:
                import os
                os.unlink(tmp)
            except OSError:
                pass


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    ok = BayesianScorer().self_test()
    print("self_test:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
