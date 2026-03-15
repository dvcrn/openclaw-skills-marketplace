---
name: sequential-thinking
description: "Structured reasoning through sequential thinking — break complex problems into steps, solve each independently, verify consistency, synthesize conclusions with confidence scoring. Use for complex analysis, debugging, and multi-step reasoning."
homepage: https://www.agxntsix.ai
---

# 🧩 Sequential Thinking

Structured reasoning through sequential thinking. Break complex problems into logical steps, solve each independently, verify consistency, and synthesize a final answer with a confidence score.

## Why Sequential Thinking?

LLMs often rush to conclusions. This skill forces step-by-step decomposition:

1. **Decompose** — Break the problem into discrete steps
2. **Solve** — Address each step independently
3. **Verify** — Check consistency between steps
4. **Synthesize** — Combine into a final answer with confidence

## Usage

```bash
# Basic sequential reasoning
python3 {baseDir}/scripts/sequential_think.py "What would happen to Earth's climate if the Moon disappeared?"

# Limit to 5 steps
python3 {baseDir}/scripts/sequential_think.py "Design a sustainable city for 1M people" --steps 5

# Enable self-verification
python3 {baseDir}/scripts/sequential_think.py "Is P=NP?" --verify

# Use a specific model
python3 {baseDir}/scripts/sequential_think.py "Explain quantum computing" --model anthropic/claude-sonnet-4

# JSON output
python3 {baseDir}/scripts/sequential_think.py "Compare React vs Vue" --json

# Verbose mode (show all intermediate reasoning)
python3 {baseDir}/scripts/sequential_think.py "Solve this logic puzzle..." --verbose
```

## Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--steps` | 7 | Maximum number of reasoning steps |
| `--verify` | off | Enable self-verification pass |
| `--model` | `anthropic/claude-sonnet-4` | Model to use |
| `--json` | off | Output structured JSON |
| `--verbose` | off | Show full intermediate reasoning |
| `--temperature` | 0.3 | Temperature for reasoning (lower = more focused) |

## Output Format

```
🧩 Sequential Thinking: "Your question here"
══════════════════════════════════════════

Step 1/5: [Step Title]
  → [Reasoning and conclusion for this step]

Step 2/5: [Step Title]
  → [Reasoning and conclusion for this step]

...

✅ Verification: [Pass/Fail — consistency notes]

📋 Synthesis:
  [Final combined answer]

🎯 Confidence: 85% (High)
```

## How It Works

1. **Decomposition prompt** asks the model to identify the key sub-questions
2. **Step-solving prompts** address each sub-question with context from prior steps
3. **Verification prompt** (optional) checks for contradictions between steps
4. **Synthesis prompt** combines all step conclusions into a coherent answer
5. **Confidence scoring** based on step agreement, verification results, and hedging language

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
