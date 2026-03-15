"""NIM Ensemble — $0 test-time scaling with NVIDIA NIM free tier.

Two APIs:
  vote()       — flat ensemble (ask N models, majority vote)
  smart_vote() — cascade (best expert first, escalate on uncertainty)

Usage:
    from nim_ensemble import smart_vote
    result = smart_vote("Is this code safe?")
    print(result.answer, result.confidence, result.calls_made)
    # UNSAFE 1.0 1  (resolved at stage 1, no escalation)
"""

from .voter import vote, vote_batch, call_model, call_copilot, COPILOT_MODELS, VoteResult
from .cascade import smart_vote, smart_vote_batch, classify_task, scale, CascadeResult
from .models import MODELS, PANELS, get_model, get_panel, list_models, is_thinking
from .parser import parse_answer, strip_thinking, extract_content

__all__ = [
    # Core API
    "scale",
    # Cascade
    "smart_vote", "smart_vote_batch", "classify_task", "CascadeResult",
    # Flat ensemble (legacy)
    "vote", "vote_batch", "call_model", "VoteResult",
    # Models
    "MODELS", "PANELS", "get_model", "get_panel", "list_models", "is_thinking",
    # Parser
    "parse_answer", "strip_thinking", "extract_content",
]
