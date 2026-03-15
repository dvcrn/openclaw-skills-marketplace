---
name: free-scaling
description: "$0 test-time scaling with NVIDIA NIM free tier. Smart cascade routes questions to the best free model based on measured capability profiles, escalating only on uncertainty. 15 models, 7 capability categories, data-driven panels. Use for auditing, code review, fact-checking, compliance, or any judgment task."
---

# NIM Ensemble

$0 multi-model reasoning using NVIDIA NIM free tier. Two modes:

- **`smart_vote()`** — cascade: routes to the best expert for the task type, escalates only on uncertainty. Average 1.2 API calls per question.
- **`vote()`** — flat ensemble: asks N models, majority vote. Simple but uses more calls.

## Setup

1. Go to [build.nvidia.com](https://build.nvidia.com) and sign in (free NVIDIA account)
2. Pick any model (e.g. [Llama 3.3 70B](https://build.nvidia.com/meta/llama-3_3-70b-instruct)) and click **"Get API Key"**
3. One key works for all NIM models — no per-model setup needed
4. Set it in your environment:
   ```bash
   export NVIDIA_API_KEY="nvapi-..."
   ```
5. No pip dependencies — stdlib only (Python 3.10+)

## Quick Start

```python
from nim_ensemble import scale

# k=3: ask 3 diverse models, majority vote
result = scale("Is eval(input()) safe?", k=3, answer_patterns=["SAFE", "VULNERABLE"])
print(result.answer)      # VULNERABLE
print(result.calls_made)  # 3
print(result.confidence)  # 1.0

# k="auto": smart cascade (starts with 1, escalates on uncertainty)
result = scale("Is this correct?", k="auto", answer_patterns=["YES", "NO"])
```

## CLI

```bash
# Scale to k models
python3 -m nim_ensemble.cli scale "Is this code vulnerable?" -k 3 --answers "SAFE,VULNERABLE"
# → VULNERABLE (k=3, conf=100%, 3 calls, 1.2s)

# Single model (fastest)
python3 -m nim_ensemble.cli scale "Is 91 prime?" -k 1 --answers "YES,NO"

# Auto-scale (smart cascade)
python3 -m nim_ensemble.cli scale "Is this safe?" -k auto

# List models and panels
python3 -m nim_ensemble.cli models
python3 -m nim_ensemble.cli panels

# Benchmark all models on a question
python3 -m nim_ensemble.cli bench "Is 91 prime? YES or NO." --speed fast
```

## How Smart Cascade Works

```
Question → classify task type (code/compliance/reasoning/factual/nuance)
        → call best expert for that type (1 call)
        → confident? (weight ≥ 85%) → done
        → uncertain? → call arbiter (mistral-large, 100% all categories)
        → still split? → full panel, weighted vote by measured accuracy
```

Most questions resolve at stage 1. Hallucinating models never get called because the capability map routes around their blind spots.

## Capability Profiling

No hardcoded capability scores — profile models on **your** tasks:

```bash
# Profile specific models (3 trials each)
python3 -m nim_ensemble.capability_map --models llama-3.3 gemma-27b mistral-large --trials 3

# Profile all fast models
python3 -m nim_ensemble.capability_map --speed fast --trials 2
```

This generates `capability_map.json` with per-model accuracy, latency, strengths/weaknesses, and error correlations. The cascade automatically loads it for data-driven routing.

**Without profiling**, the cascade uses sensible defaults (mistral-large as arbiter, diverse 3-model panels). Profiling lets it route around your models' specific blind spots.

## Default Panels

Panels maximize architectural diversity (independent errors cancel out):

| Panel | Models | Use Case |
|-------|--------|----------|
| `general` | mistral-large, llama-3.3, gemma-27b | Default (3 families) |
| `fast` | llama-3.3, nemotron-super-49b, gemma-27b | All <1.5s |
| `max` | 5 models across 5 families | High-stakes |
| `arbiter` | mistral-large | Single tiebreaker |

For task-specific panels, run `capability_map` to profile models on your data.

## Python API

```python
from nim_ensemble import scale, smart_vote, vote, call_model

# scale() — the core API, control k
result = scale("Is X safe?", k=3, answer_patterns=["SAFE", "VULNERABLE"])
result = scale("Is X safe?", k="auto")  # smart cascade
result = scale("Is X safe?", k=1)       # single model

# smart_vote() — cascade with task-type routing
result = smart_vote("Is X correct?", answer_patterns=["YES", "NO"])

# vote() — flat ensemble with named panels
result = vote("Is X true?", panel="general", answer_patterns=["YES", "NO"])

# call_model() — single model, raw access
from nim_ensemble import call_model
answer, raw = call_model("Is X true?", "mistral-large")
```

## Prompt Tips

For best results with ensemble voting:
- Ask for the answer on the **first line**: "Answer YES or NO on the first line, then explain."
- Give **explicit answer options**: "Answer SAFE, UNSAFE, or NEEDS_REVIEW."
- Include **context/evidence** in the question, not just the judgment call.

## Architecture

```
nim_ensemble/
├── __init__.py       # Public API: smart_vote, vote, call_model
├── cascade.py        # Smart cascade with capability routing
├── voter.py          # Flat ensemble voting engine
├── models.py         # Model registry + data-driven panels
├── parser.py         # Answer extraction (thinking models, word boundaries)
├── cli.py            # CLI interface
├── benchmark.py      # Single-trial model profiling
└── capability_map.py # Multi-trial profiling with error correlation
```

## Requirements

- `NVIDIA_API_KEY` environment variable (free at [build.nvidia.com](https://build.nvidia.com))
- Python 3.10+
- No pip dependencies (stdlib only, uses `urllib` for API calls)
