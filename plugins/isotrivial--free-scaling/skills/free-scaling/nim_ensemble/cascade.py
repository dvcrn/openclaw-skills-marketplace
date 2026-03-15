"""Smart cascade — capability-aware routing with confidence gating.

Instead of "ask 3 models, vote", this does:
  1. Classify task type from the question
  2. Pick the best model for that type (from capability map)
  3. If confident → done (1 API call)
  4. If uncertain → escalate to arbiter
  5. If arbiter uncertain → full panel vote
  6. Weight votes by measured accuracy

Average: ~1.2 calls per question instead of 3.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

from .models import MODELS, PANELS, get_panel
from .voter import call_model, vote, VoteResult
from .parser import parse_answer


# Load capability map if available
_CAPABILITY_MAP = None

def _load_capability_map() -> dict:
    global _CAPABILITY_MAP
    if _CAPABILITY_MAP is not None:
        return _CAPABILITY_MAP
    
    # Try multiple locations
    candidates = [
        Path(__file__).parent.parent / "capability_map.json",
        Path(os.environ.get("OPENCLAW_WORKSPACE", "")) / "skills" / "nim-ensemble" / "capability_map.json",
    ]
    for p in candidates:
        if p.exists():
            with open(p) as f:
                _CAPABILITY_MAP = json.load(f)
            return _CAPABILITY_MAP
    
    _CAPABILITY_MAP = {}
    return _CAPABILITY_MAP


# Task type classification keywords
TASK_KEYWORDS = {
    "code": [
        "code", "function", "bug", "vulnerability", "sql", "injection", 
        "safe", "unsafe", "secure", "insecure", "python", "javascript",
        "cursor.execute", "eval(", "exec(", "import os", "subprocess",
        "def ", "class ", "return ", "```",
    ],
    "compliance": [
        "compliant", "violated", "following the rule", "follow the rule",
        "preamble", "personality", "soul", "character", "behavior", "tone",
        "helpdesk", "filler", "direct", "rule", "policy", "guideline",
    ],
    "reasoning": [
        "taller than", "greater than", "then", "therefore",
        "majority", "consistent", "inconsistent", "implies",
        "logically", "deduce", "infer",
    ],
    "factual": [
        "prime", "multiply", "calculate", "what is", "is it true",
        "how many", "which year", "capital of",
    ],
    "nuance": [
        "urgent", "routine", "fyi", "priority", "severity",
        "subtle", "gray area", "borderline", "edge case",
        "drifting", "minor", "major",
    ],
}

# Default panels — good starting points, override via capability_map.json
_DEFAULT_BEST_FOR_TASK = {
    "code":       ["gemma-27b", "mistral-large", "llama-3.3"],
    "compliance": ["llama-3.3", "gemma-27b", "mistral-large"],
    "reasoning":  ["mistral-large", "llama-3.3", "nemotron-super-49b"],
    "factual":    ["mistral-large", "llama-3.3", "gemma-27b"],
    "nuance":     ["llama-3.3", "gemma-27b", "mistral-large"],
    "general":    ["mistral-large", "llama-3.3", "gemma-27b"],
}

# Default weights (equal) — override via capability_map.json profiling
_DEFAULT_MODEL_WEIGHT = 0.75


def _get_routing():
    """Load routing from capability_map.json if available, else use defaults."""
    cap = _load_capability_map()
    
    if not cap or "routing_policy" not in cap:
        return _DEFAULT_BEST_FOR_TASK, {}
    
    policy = cap["routing_policy"]
    
    # Build BEST_FOR_TASK from routing_policy panels (try both key names)
    best_for = {}
    panels = policy.get("panels", policy.get("recommended_panels", {}))
    for task_type, models in panels.items():
        best_for[task_type] = models
    # Merge defaults for any missing task types
    for k, v in _DEFAULT_BEST_FOR_TASK.items():
        if k not in best_for:
            best_for[k] = v
    
    # Build MODEL_WEIGHTS from profiles — extract accuracy floats from nested dicts
    weights = {}
    for alias, profile in cap.get("profiles", {}).items():
        cats = profile.get("category_scores", {})
        w = {}
        for cat, info in cats.items():
            # Handle both formats: {"accuracy": 0.9, ...} or plain float 0.9
            if isinstance(info, dict):
                w[cat] = info.get("accuracy", _DEFAULT_MODEL_WEIGHT)
            else:
                w[cat] = float(info)
        # Add overall as "general"
        if "general" not in w:
            w["general"] = profile.get("accuracy", _DEFAULT_MODEL_WEIGHT)
        weights[alias] = w
    
    return best_for, weights

ARBITER = "mistral-large"  # 100% across all categories


@dataclass
class CascadeResult:
    """Result of a smart cascade."""
    answer: str
    confidence: float        # 0-1 weighted confidence
    task_type: str           # detected task type
    stage: str               # "primary", "arbiter", "panel"
    calls_made: int          # total API calls
    models_used: list[str]
    votes: list[tuple[str, str, float]]  # (model, answer, weight)
    elapsed_s: float = 0.0
    reasoning: str = ""      # why this answer


def classify_task(question: str) -> str:
    """Classify a question into a task type using keyword matching."""
    question_lower = question.lower()
    
    scores = {}
    for task_type, keywords in TASK_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in question_lower)
        if score > 0:
            scores[task_type] = score
    
    if not scores:
        return "general"
    
    return max(scores, key=scores.get)


def smart_vote(
    question: str,
    task_type: str = None,
    answer_patterns: list[str] = None,
    system_prompt: str = None,
    max_tokens: int = 150,
    confidence_threshold: float = 0.85,
    skip_cascade: bool = False,
) -> CascadeResult:
    """Capability-aware cascade with confidence gating.
    
    Stage 1: Best model for task type (1 call)
      → if answer is clear and model weight ≥ threshold → done
    Stage 2: Arbiter verification (1 more call)
      → if arbiter agrees → done
      → if arbiter disagrees → weighted vote between them
    Stage 3: Full panel (3 more calls, 5 total)
      → weighted majority vote
    
    Args:
        question: The question to answer
        task_type: Override auto-classification (code/compliance/reasoning/factual/nuance/general)
        answer_patterns: Expected answer tokens
        system_prompt: Optional system prompt
        max_tokens: Max tokens per call
        confidence_threshold: Min weighted confidence to accept at stage 1
        skip_cascade: If True, go straight to full panel vote (fallback mode)
    """
    t0 = time.time()
    
    # Classify task
    # Normalize answer patterns to uppercase
    if answer_patterns:
        answer_patterns = [p.strip().upper() for p in answer_patterns]
    if task_type is None:
        task_type = classify_task(question)
    
    # Load routing (from capability_map.json if available, else defaults)
    best_for_task, model_weights = _get_routing()
    
    if skip_cascade:
        # Fallback: just do weighted panel vote
        return _weighted_panel_vote(question, task_type, answer_patterns, 
                                    system_prompt, max_tokens, t0,
                                    best_for_task, model_weights)
    
    # Get best model for this task type
    best_models = best_for_task.get(task_type, best_for_task["general"])
    primary = best_models[0]
    
    # Stage 1: Primary expert
    ans1, raw1 = call_model(question, primary, system_prompt, max_tokens)
    
    # Re-parse with custom patterns
    if answer_patterns and ans1 != "ERROR":
        ans1 = parse_answer(raw1, patterns=answer_patterns)
    
    # Arbiter gets full weight by default; others get default weight
    default_w = 1.0 if primary == ARBITER else _DEFAULT_MODEL_WEIGHT
    weight1 = model_weights.get(primary, {}).get(task_type, default_w)
    calls = 1
    
    if ans1 == "ERROR":
        # Primary failed, go to arbiter
        pass
    elif ans1 == "UNCLEAR":
        # Primary uncertain, escalate
        pass
    elif weight1 >= confidence_threshold:
        # Primary confident and reliable → done
        return CascadeResult(
            answer=ans1,
            confidence=weight1,
            task_type=task_type,
            stage="primary",
            calls_made=1,
            models_used=[primary],
            votes=[(primary, ans1, weight1)],
            elapsed_s=time.time() - t0,
            reasoning=f"{primary} answered {ans1} (weight {weight1:.0%} on {task_type}). High confidence, no escalation needed.",
        )
    
    # Stage 2: Arbiter
    if primary == ARBITER:
        # Primary IS the arbiter — skip stage 2 entirely, go to panel
        arbiter_ans = ans1
        arbiter_weight = weight1
    else:
        arbiter_ans, arbiter_raw = call_model(question, ARBITER, system_prompt, max_tokens)
        calls += 1
        
        if answer_patterns and arbiter_ans != "ERROR":
            arbiter_ans = parse_answer(arbiter_raw, patterns=answer_patterns)
        
        arbiter_weight = model_weights.get(ARBITER, {}).get(task_type, 1.0)  # Arbiter gets full weight by default
    
        # If primary answered and arbiter agrees → done
        if ans1 not in ("ERROR", "UNCLEAR") and arbiter_ans == ans1:
            combined_conf = (weight1 + arbiter_weight) / 2
            return CascadeResult(
                answer=ans1,
                confidence=combined_conf,
                task_type=task_type,
                stage="arbiter",
                calls_made=calls,
                models_used=[primary, ARBITER],
                votes=[(primary, ans1, weight1), (ARBITER, arbiter_ans, arbiter_weight)],
                elapsed_s=time.time() - t0,
                reasoning=f"{primary} and {ARBITER} agree on {ans1}. Combined confidence {combined_conf:.0%}.",
            )
        
        # If arbiter is confident and primary wasn't → trust arbiter
        if arbiter_ans not in ("ERROR", "UNCLEAR") and arbiter_weight >= confidence_threshold:
            if ans1 in ("ERROR", "UNCLEAR"):
                return CascadeResult(
                    answer=arbiter_ans,
                    confidence=arbiter_weight,
                    task_type=task_type,
                    stage="arbiter",
                    calls_made=calls,
                    models_used=[primary, ARBITER],
                    votes=[(primary, ans1, weight1), (ARBITER, arbiter_ans, arbiter_weight)],
                    elapsed_s=time.time() - t0,
                    reasoning=f"{primary} was {ans1}. {ARBITER} answered {arbiter_ans} (weight {arbiter_weight:.0%}). Trusting arbiter.",
                )
    
    # Stage 3: Disagreement or low confidence → full panel weighted vote
    # Get remaining models from the task panel (excluding already-called)
    panel_models = best_for_task.get(task_type, best_for_task.get("general", _DEFAULT_BEST_FOR_TASK["general"]))
    already_called = {primary, ARBITER} if primary != ARBITER else {primary}
    remaining = [m for m in panel_models if m not in already_called]
    
    # Add more models if panel is too small
    if len(remaining) < 2:
        backup = [m for m in ["llama-3.3", "gemma-27b", "nemotron-super-49b", "kimi-k2"] 
                  if m not in already_called and m not in remaining]
        remaining.extend(backup[:3 - len(remaining)])
    
    # Start with primary vote (no duplicates)
    all_votes = []
    if ans1 not in ("ERROR",):
        all_votes.append((primary, ans1, weight1))
    # Add arbiter only if it's a different model
    if primary != ARBITER and arbiter_ans not in ("ERROR",):
        all_votes.append((ARBITER, arbiter_ans, arbiter_weight))
    
    for model in remaining:
        ans, raw = call_model(question, model, system_prompt, max_tokens)
        calls += 1
        if answer_patterns and ans != "ERROR":
            ans = parse_answer(raw, patterns=answer_patterns)
        w = model_weights.get(model, {}).get(task_type, _DEFAULT_MODEL_WEIGHT)
        if ans != "ERROR":
            all_votes.append((model, ans, w))
    
    # Weighted majority vote
    answer, confidence = _weighted_majority(all_votes)
    all_models = [primary] + ([ARBITER] if primary != ARBITER else []) + remaining
    
    return CascadeResult(
        answer=answer,
        confidence=confidence,
        task_type=task_type,
        stage="panel",
        calls_made=calls,
        models_used=all_models,
        votes=all_votes,
        elapsed_s=time.time() - t0,
        reasoning=f"Full panel vote: {len(all_votes)} votes across {calls} calls. Weighted majority: {answer} ({confidence:.0%}).",
    )


def _weighted_majority(votes: list[tuple[str, str, float]]) -> tuple[str, float]:
    """Compute weighted majority from (model, answer, weight) tuples."""
    if not votes:
        return "UNCLEAR", 0.0
    
    # Accumulate weights per answer
    answer_weights = {}
    total_weight = 0
    for model, ans, weight in votes:
        if ans not in ("ERROR", "UNCLEAR"):
            answer_weights[ans] = answer_weights.get(ans, 0) + weight
            total_weight += weight
    
    if not answer_weights:
        return "UNCLEAR", 0.0
    
    best_answer = max(answer_weights, key=answer_weights.get)
    confidence = answer_weights[best_answer] / total_weight if total_weight > 0 else 0
    
    return best_answer, round(confidence, 3)


def _weighted_panel_vote(question, task_type, answer_patterns, system_prompt, 
                         max_tokens, t0, best_for_task=None, model_weights=None) -> CascadeResult:
    """Direct weighted panel vote (skip cascade)."""
    if best_for_task is None:
        best_for_task, _ = _get_routing()
    if model_weights is None:
        _, model_weights = _get_routing()
    panel_models = best_for_task.get(task_type, best_for_task.get("general", ["mistral-large", "llama-3.3", "gemma-27b"]))
    
    all_votes = []
    calls = 0
    for model in panel_models:
        ans, raw = call_model(question, model, system_prompt, max_tokens)
        calls += 1
        if answer_patterns and ans != "ERROR":
            ans = parse_answer(raw, patterns=answer_patterns)
        w = model_weights.get(model, {}).get(task_type, _DEFAULT_MODEL_WEIGHT)
        if ans != "ERROR":
            all_votes.append((model, ans, w))
    
    answer, confidence = _weighted_majority(all_votes)
    
    return CascadeResult(
        answer=answer,
        confidence=confidence,
        task_type=task_type,
        stage="panel",
        calls_made=calls,
        models_used=panel_models,
        votes=all_votes,
        elapsed_s=time.time() - t0,
        reasoning=f"Direct panel vote ({task_type}): {answer} ({confidence:.0%}).",
    )


def smart_vote_batch(
    questions: list[dict],
    max_parallel: int = 5,
    **kwargs,
) -> list[CascadeResult]:
    """Smart vote on multiple questions.
    
    Each question dict: {"text": "...", "task_type": "code", "answer_patterns": [...]}
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    results = [None] * len(questions)
    
    def _vote_one(idx, q):
        text = q.get("text", q.get("question_text", ""))
        kw = {**kwargs}
        if "task_type" in q:
            kw["task_type"] = q["task_type"]
        if "answer_patterns" in q:
            kw["answer_patterns"] = q["answer_patterns"]
        return idx, smart_vote(text, **kw)
    
    with ThreadPoolExecutor(max_workers=max_parallel) as pool:
        futures = {pool.submit(_vote_one, i, q): i for i, q in enumerate(questions)}
        for fut in as_completed(futures):
            idx, result = fut.result()
            results[idx] = result
    
    return results


def scale(
    question: str,
    k: int | str = "auto",
    answer_patterns: list[str] = None,
    system_prompt: str = None,
    max_tokens: int = 150,
) -> CascadeResult:
    """Scale inference by asking k models the same question.
    
    The core API — control the cost/accuracy tradeoff with a single parameter.
    
    Args:
        question: The question to answer
        k: Number of models to query:
           - "auto": smart cascade (start with 1, escalate on uncertainty)
           - 1: single best model (fastest, cheapest)
           - 3: ensemble of 3 diverse models (balanced)
           - 5: maximum confidence panel
           - Any int: picks that many models from diverse families
        answer_patterns: Expected answer tokens (e.g. ["YES", "NO"])
        system_prompt: Optional system prompt
        max_tokens: Max tokens per call
    
    Returns:
        CascadeResult with answer, confidence, calls_made
    """
    if k == "auto":
        return smart_vote(question, answer_patterns=answer_patterns,
                         system_prompt=system_prompt, max_tokens=max_tokens)
    
    k = int(k)
    if k < 1:
        raise ValueError("k must be >= 1 or 'auto'")
    
    t0 = time.time()
    
    # Pick k models — maximize family diversity
    all_models = list(MODELS.keys())
    # Sort by family to interleave different architectures
    families_seen = set()
    diverse_order = []
    # First pass: one per family
    # Order: strongest voters first, then diverse families
    # Verified working on NIM as of 2026-03-14
    for alias in ["mistral-large", "llama-3.3", "gemma-27b",
                  "nemotron-super-49b", "kimi-k2", "llama-405b", "qwen-397b",
                  "jamba-mini", "dracarys-70b",
                  "mistral-medium"]:
        if alias in MODELS:
            fam = MODELS[alias]["family"]
            if fam not in families_seen:
                diverse_order.append(alias)
                families_seen.add(fam)
            else:
                diverse_order.append(alias)  # still add, but after first-of-family
    
    # Cap k to available models
    effective_k = min(k, len(diverse_order))
    selected = diverse_order[:effective_k]
    
    if k == 1:
        # Single model — use arbiter
        model = ARBITER
        ans, raw = call_model(question, model, system_prompt, max_tokens)
        if answer_patterns:
            answer_patterns = [p.strip().upper() for p in answer_patterns]
            if answer_patterns and ans != "ERROR":
                ans = parse_answer(raw, patterns=answer_patterns)
        
        return CascadeResult(
            answer=ans,
            confidence=1.0 if ans != "ERROR" else 0.0,
            task_type="general",
            stage="primary",
            calls_made=1,
            models_used=[model],
            votes=[(model, ans, 1.0)],
            elapsed_s=time.time() - t0,
            reasoning=f"Single model ({model}): {ans}",
        )
    
    # k >= 2: parallel ensemble vote
    if answer_patterns:
        answer_patterns = [p.strip().upper() for p in answer_patterns]
    
    all_votes = []
    calls = 0
    
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    def _call(alias):
        ans, raw = call_model(question, alias, system_prompt, max_tokens)
        # Always reparse with answer_patterns when provided
        if answer_patterns and ans != "ERROR":
            ans = parse_answer(raw, patterns=answer_patterns)
        return alias, ans, raw
    
    with ThreadPoolExecutor(max_workers=effective_k) as pool:
        futures = {pool.submit(_call, alias): alias for alias in selected}
        for fut in as_completed(futures):
            alias, ans, raw = fut.result()
            calls += 1
            if ans != "ERROR":
                all_votes.append((alias, ans, 1.0))  # Equal weight without profiling
    
    answer, confidence = _weighted_majority(all_votes)
    
    return CascadeResult(
        answer=answer,
        confidence=confidence,
        task_type="general",
        stage=f"scale-{effective_k}",
        calls_made=calls,
        models_used=selected,
        votes=all_votes,
        elapsed_s=time.time() - t0,
        reasoning=f"Scaled to {effective_k} models{f' (capped from k={k})' if effective_k < k else ''}: {answer} ({confidence:.0%} agreement).",
    )
