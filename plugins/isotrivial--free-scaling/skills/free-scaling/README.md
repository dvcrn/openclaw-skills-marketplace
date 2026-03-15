# Free Scaling

$0 test-time scaling using [NVIDIA NIM](https://build.nvidia.com) free tier. Ask multiple models, get one reliable answer.

```python
from nim_ensemble import scale

result = scale("Is this code safe?", k=3, answer_patterns=["SAFE", "VULNERABLE"])
# → VULNERABLE (k=3, conf=100%, 3 calls, 1.2s)
```

## Why

Single models hallucinate. Ensembles don't (as much). NIM gives you 15 models for free. This library turns them into a single reliable oracle with one parameter: **k** — the number of models to ask.

**Zero cost. Zero dependencies. Just stdlib Python + a free API key.**

## Setup

### NIM Backend (primary)
1. Get a free API key at [build.nvidia.com](https://build.nvidia.com) — sign in, pick any model, click "Get API Key"
2. One key works for all 15 models:
   ```bash
   export NVIDIA_API_KEY="nvapi-..."
   ```

### Copilot Backend (optional)
GitHub Copilot models (cp-4.1, cp-mini, cp-sonnet, etc.) can also be used as voters — useful for hybrid setups where you want smarter models on harder questions and NIM for fast/diverse voting.

```python
from nim_ensemble import call_copilot

# Requires a Copilot token at ~/.openclaw/credentials/github-copilot.token.json
ans, raw = call_copilot("Is this safe?", "cp-4.1")
```

Available Copilot models: `cp-4.1` (GPT-4.1), `cp-mini` (GPT-5-mini), `cp-4o`, `cp-flash`, `cp-haiku`, `cp-sonnet`.

### Clone and use
```bash
git clone https://github.com/isotrivial/free-scaling.git
cd free-scaling
```

No pip install needed — stdlib only (Python 3.10+).

## Quick Start

### CLI
```bash
# Scale to 3 models
python3 -m nim_ensemble.cli scale "Is eval(input()) safe?" -k 3 --answers "SAFE,VULNERABLE"
# → VULNERABLE (k=3, conf=100%, 3 calls, 1.2s)

# Single model (fastest)
python3 -m nim_ensemble.cli scale "Is 91 prime?" -k 1 --answers "YES,NO"
# → NO (k=1, conf=100%, 1 call, 0.5s)

# Auto-scale (smart cascade — starts with 1, adds more if uncertain)
python3 -m nim_ensemble.cli scale "Is this compliant?" -k auto
```

### Python
```python
from nim_ensemble import scale

# k=1: single best model (fast, cheap)
result = scale("Is this safe?", k=1)

# k=3: 3 diverse models (balanced)
result = scale("Is this safe?", k=3, answer_patterns=["SAFE", "VULNERABLE"])

# k=5: maximum confidence
result = scale("Is this safe?", k=5)

# k="auto": smart cascade (1→2→N, escalates on uncertainty)
result = scale("Is this safe?", k="auto")

print(result.answer)      # VULNERABLE
print(result.confidence)  # 1.0
print(result.calls_made)  # 3
```

## How It Works

**`k=1`**: Asks the single best model (mistral-large).

**`k=N`**: Asks N models from diverse families (Mistral, Meta, Qwen, Google, etc.), majority vote. Models are selected to maximize architectural diversity — independent errors cancel out.

**`k="auto"`** (smart cascade):
```
Question → classify task type → call best expert (1 call)
        → confident? → done
        → uncertain? → call arbiter
        → still split? → full panel vote
```

Most questions resolve with 1-2 calls. Scales up only when needed.

## Capability Profiling (optional)

Default panels are diversity-based. For data-driven routing, profile models on your tasks:

```bash
python3 -m nim_ensemble.capability_map --models llama-3.3 gemma-27b mistral-large --trials 3
```

Generates `capability_map.json` — the cascade loads it automatically to route around each model's measured blind spots.

## 15 Models Included

| Tier | Models |
|------|--------|
| Fast (<1s) | llama-3.3 70B, gemma-27b, nemotron-super-49b, dracarys-70b, jamba-mini |
| Medium (1-3s) | mistral-large 675B, kimi-k2, qwen-397b, llama-405b, mistral-medium |
| Slow (3s+) | deepseek-v3.1, minimax-m2.5 🧠, kimi-k2.5 🧠 |

All free via NVIDIA NIM. One API key covers everything.

## Presets

### Audit Preset
A ready-made behavioral compliance auditor. Collects system state, generates judgment questions, and pipes them through `scale()` with hybrid routing (Copilot for behavioral checks, NIM for operational checks):

```bash
# Full audit with hybrid backend (default)
python3 -m presets.audit --backend hybrid -k 3

# NIM-only (no Copilot token needed)
python3 -m presets.audit --backend nim -k 3

# JSON output for CI pipelines
python3 -m presets.audit --json
```

Produces a structured report with severity classification (🔴 CRITICAL / 🟡 WARNING / ✅ OK) and health score.

## Use Cases

- **Code review** — "Is this code vulnerable?" across multiple models
- **Fact-checking** — consensus answers to factual questions
- **Compliance auditing** — check if outputs follow rules/policies
- **Agent self-evaluation** — verify agent behavior against specs
- **CI pipelines** — automated judgment gates with JSON output
- **Any binary/categorical judgment** — scale compute to match stakes

## Also an OpenClaw Skill

```bash
clawhub install free-scaling
```

See [SKILL.md](SKILL.md) for the full agent skill reference.

## License

MIT — see [LICENSE](LICENSE).
