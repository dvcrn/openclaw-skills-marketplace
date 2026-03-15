---
name: crazyrouter-chat
description: "Chat with 627+ AI models via Crazyrouter. GPT-5, Claude Opus 4.6, Gemini 3, DeepSeek R1, Llama 4, Qwen3, Grok 4. Use when user wants to query a specific model, compare model responses, or get a second opinion from a different AI."
---

# Multi-Model Chat via Crazyrouter

Chat with any of 627+ AI models through [Crazyrouter](https://crazyrouter.com) — one API key, all providers.

## Supported Models (highlights)

| Provider | Models |
|----------|--------|
| OpenAI | gpt-5, gpt-5-mini, gpt-4.1, gpt-4o, o3, o4-mini |
| Anthropic | claude-opus-4-6, claude-sonnet-4, claude-haiku-3.5 |
| Google | gemini-3-pro, gemini-2.5-flash |
| DeepSeek | deepseek-r1, deepseek-v3 |
| Meta | llama-4-scout, llama-4-maverick |
| Alibaba | qwen3-235b, qwen3-32b |
| xAI | grok-4, grok-3 |
| Mistral | mistral-large, codestral |

## Script Directory

**Agent Execution**:
1. `SKILL_DIR` = this SKILL.md file's directory
2. Script path = `${SKILL_DIR}/scripts/main.ts`

## Step 0: Check API Key ⛔ BLOCKING

```bash
echo "${CRAZYROUTER_API_KEY:-not_set}"
```

| Result | Action |
|--------|--------|
| Key found | Continue |
| Key NOT found | Ask user to set `CRAZYROUTER_API_KEY`. Get key at https://crazyrouter.com |

## Usage

```bash
# Ask GPT-5 a question
npx -y bun ${SKILL_DIR}/scripts/main.ts --model gpt-5 --prompt "Explain quantum computing in 3 sentences"

# Compare models
npx -y bun ${SKILL_DIR}/scripts/main.ts --model deepseek-r1 --prompt "Write a sorting algorithm in Python"
npx -y bun ${SKILL_DIR}/scripts/main.ts --model claude-opus-4-6 --prompt "Write a sorting algorithm in Python"

# With system prompt
npx -y bun ${SKILL_DIR}/scripts/main.ts --model gemini-3-pro --system "You are a pirate" --prompt "Tell me about the weather"

# With temperature
npx -y bun ${SKILL_DIR}/scripts/main.ts --model gpt-5-mini --prompt "Write a poem" --temperature 1.2

# Save output to file
npx -y bun ${SKILL_DIR}/scripts/main.ts --model gpt-5 --prompt "Write a README" --output readme.md

# List available models
npx -y bun ${SKILL_DIR}/scripts/main.ts --list-models
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--prompt <text>` | User message (required) | — |
| `--model <id>` | Model to use | `gpt-5-mini` |
| `--system <text>` | System prompt | — |
| `--temperature <num>` | Sampling temperature (0-2) | — |
| `--max-tokens <num>` | Max response tokens | — |
| `--output <path>` | Save response to file | — |
| `--list-models` | List popular models | — |
| `--json` | Output raw JSON | — |
