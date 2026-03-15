"""
NIMA Core — Storage Layer
==========================

Provides cognitive memory primitives for ACT-R temporal decay,
Hebbian associative learning, Bayesian confidence scoring, and
protocol governance.

Modules
-------
temporal_decay
    ACT-R base-level activation scorer.  Tracks access history and
    computes activation scores using the formula B_i = ln(Σ t_j^(-d)).

hebbian_updater
    Hebbian edge-weight manager for the memory graph.  Strengthens
    associations between co-activated memories and decays unused edges.

bayesian_scorer
    Beta-distribution confidence scorer.  Tracks recall successes/failures
    and maintains a posterior confidence estimate per memory node.

protocol_store
    Constitutional governance layer.  Stores and retrieves ProtocolNodes:
    rules that govern agent reasoning, retrieved contextually by keyword/domain.

Typical import::

    from storage.temporal_decay  import ACTRDecayScorer
    from storage.hebbian_updater import HebbianGraphUpdater
    from storage.bayesian_scorer import BayesianScorer
    from storage.protocol_store  import ProtocolStore, seed_protocols
"""

from .temporal_decay  import ACTRDecayScorer
from .hebbian_updater import HebbianGraphUpdater
from .bayesian_scorer import BayesianScorer
from .protocol_store  import ProtocolStore, seed_protocols

__all__ = [
    "ACTRDecayScorer",
    "HebbianGraphUpdater",
    "BayesianScorer",
    "ProtocolStore",
    "seed_protocols",
]
