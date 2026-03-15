---
name: nous-genai
description: "Unified interface for all providers and all modalities: use one nous-genai CLI/SDK flow to run text/image/audio/video/embedding across OpenAI, Gemini, Claude, DashScope, Volcengine, and Tuzi, with support for authenticated local MCP workflows."
---

# nous-genai

## Quick Start

**IMPORTANT:** If you rely on `.env.*` files, run commands in the directory that contains those files (typically this skill base directory). If you pass runtime env vars (inline/export), working directory is not restricted.

```bash
# 1) Create `.env.local` in this skill directory
(cd "<SKILL_BASE_DIR>" && { test -f .env.local || touch .env.local; })

# 2) Edit `<SKILL_BASE_DIR>/.env.local` and set at least one provider key (see "Supported Environment Variables").
# Example (OpenAI):
#   NOUS_GENAI_OPENAI_API_KEY=...

# 3) Text
(cd "<SKILL_BASE_DIR>" && uvx --from nous-genai genai --model openai:gpt-4o-mini --prompt "Hello")

# 4) See what you can use (requires at least one provider key configured)
(cd "<SKILL_BASE_DIR>" && uvx --from nous-genai genai model available --all)
```

If `uvx` is unavailable, install once and use `genai` directly:

```bash
python -m pip install --upgrade nous-genai
(cd "<SKILL_BASE_DIR>" && genai --model openai:gpt-4o-mini --prompt "Hello")
```

## Configuration (Env Vars, Zero-parameter)

Configuration is managed via environment variables.

You can set env vars in two ways:

1. Runtime env vars (inline before command, or `export` in shell)
2. Env files (`.env.local`, `.env.production`, `.env.development`, `.env.test`)

Recommended for this skill:

- Put stable/project-level config in `<SKILL_BASE_DIR>/.env.local`
- Use runtime env vars for one-off overrides

Runtime example (inline):

```bash
(cd "<SKILL_BASE_DIR>" && NOUS_GENAI_OPENAI_API_KEY=... uvx --from nous-genai genai --model openai:gpt-4o-mini --prompt "Hello")
```

When env files are used, SDK/CLI/MCP loads them automatically with priority (high -> low):

- `.env.local > .env.production > .env.development > .env.test`

Process env vars override `.env.*` (SDK uses `os.environ.setdefault()`).

Minimal `.env.local` (OpenAI text only):

```bash
NOUS_GENAI_OPENAI_API_KEY=...
NOUS_GENAI_TIMEOUT_MS=120000
```

Notes:

- Do not commit `.env.local` (add it to `.gitignore` if needed).
- Provider keys also accept non-prefixed vars like `OPENAI_API_KEY`, but prefer `NOUS_GENAI_*` for clarity.

## Supported Environment Variables

### Common runtime

- `NOUS_GENAI_TIMEOUT_MS` (default: `120000`)
- `NOUS_GENAI_URL_DOWNLOAD_MAX_BYTES` (default: `134217728`)
- `NOUS_GENAI_ALLOW_PRIVATE_URLS` (`1/true/yes` to allow private/loopback URL download)
- `NOUS_GENAI_TRANSPORT` (internal transport marker; MCP server uses `mcp`, legacy `sse` is accepted)

### Provider credentials

- OpenAI: `NOUS_GENAI_OPENAI_API_KEY` or `OPENAI_API_KEY`
- Google (Gemini): `NOUS_GENAI_GOOGLE_API_KEY` or `GOOGLE_API_KEY`
- Anthropic (Claude): `NOUS_GENAI_ANTHROPIC_API_KEY` or `ANTHROPIC_API_KEY`
- Aliyun (DashScope/百炼): `NOUS_GENAI_ALIYUN_API_KEY` or `ALIYUN_API_KEY`
- Volcengine (Ark/豆包): `NOUS_GENAI_VOLCENGINE_API_KEY` or `VOLCENGINE_API_KEY`

### Provider base URL overrides

- `ALIYUN_OAI_BASE_URL` (default: `https://dashscope.aliyuncs.com/compatible-mode/v1`)
- `VOLCENGINE_OAI_BASE_URL` (default: `https://ark.cn-beijing.volces.com/api/v3`)
- `TUZI_BASE_URL` (default: `https://api.tu-zi.com`)
- `TUZI_OAI_BASE_URL` (optional override)
- `TUZI_GOOGLE_BASE_URL` (optional override)
- `TUZI_ANTHROPIC_BASE_URL` (optional override)

### Tuzi credentials

- `NOUS_GENAI_TUZI_WEB_API_KEY` or `TUZI_WEB_API_KEY`
- `NOUS_GENAI_TUZI_OPENAI_API_KEY` or `TUZI_OPENAI_API_KEY`
- `NOUS_GENAI_TUZI_GOOGLE_API_KEY` or `TUZI_GOOGLE_API_KEY`
- `NOUS_GENAI_TUZI_ANTHROPIC_API_KEY` or `TUZI_ANTHROPIC_API_KEY`

### MCP server

- `NOUS_GENAI_MCP_HOST` (default: `127.0.0.1`)
- `NOUS_GENAI_MCP_PORT` (default: `6001`)
- `NOUS_GENAI_MCP_PUBLIC_BASE_URL`
- `NOUS_GENAI_MCP_BEARER_TOKEN`
- `NOUS_GENAI_MCP_TOKEN_RULES`

## Model Format

Model string is `{provider}:{model_id}` (example: `openai:gpt-4o-mini`).

Use this to pick a model by output modality:

```bash
(cd "<SKILL_BASE_DIR>" && uvx --from nous-genai genai model available --all)
# Look for: out=text / out=image / out=audio / out=video / out=embedding
```

If you have not configured any keys yet, you can still view the SDK curated list:

```bash
(cd "<SKILL_BASE_DIR>" && uvx --from nous-genai genai model sdk)
```

## Common Scenarios

### Image understanding

```bash
(cd "<SKILL_BASE_DIR>" && uvx --from nous-genai genai --model openai:gpt-4o-mini --prompt "Describe this image" --image-path "/path/to/image.png")
```

### Image generation (save to file)

```bash
(cd "<SKILL_BASE_DIR>" && uvx --from nous-genai genai --model openai:gpt-image-1 --prompt "A red square, minimal" --output-path "/tmp/out.png")
```

### Speech-to-text (transcription)

```bash
(cd "<SKILL_BASE_DIR>" && uvx --from nous-genai genai --model openai:whisper-1 --audio-path "/path/to/audio.wav")
```

### Text-to-speech (save to file)

```bash
(cd "<SKILL_BASE_DIR>" && uvx --from nous-genai genai --model openai:tts-1 --prompt "你好" --output-path "/tmp/tts.mp3")
```

## Python SDK

Install:

```bash
python -m pip install --upgrade nous-genai
```

Minimal example:

```python
from nous.genai import Client, GenerateRequest, Message, OutputSpec, Part

client = Client()
resp = client.generate(
    GenerateRequest(
        model="openai:gpt-4o-mini",
        input=[Message(role="user", content=[Part.from_text("Hello")])],
        output=OutputSpec(modalities=["text"]),
    )
)
print(resp.output[0].content[0].text)
```

Note: `Client()` loads `.env.*` from the current working directory; run your script in the directory that contains
`.env.local`, or export env vars in the process environment.

## MCP Server

Start server (Streamable HTTP: `/mcp`, SSE: `/sse`):

```bash
(cd "<SKILL_BASE_DIR>" && uvx --from nous-genai genai-mcp-server)
```

Recommended: set auth via runtime env vars or `.env.local` before exposing the server:

```bash
# NOUS_GENAI_MCP_BEARER_TOKEN=sk-...
```

Debug with MCP CLI:

```bash
(cd "<SKILL_BASE_DIR>" && uvx --from nous-genai genai-mcp-cli env)
(cd "<SKILL_BASE_DIR>" && uvx --from nous-genai genai-mcp-cli tools)
(cd "<SKILL_BASE_DIR>" && uvx --from nous-genai genai-mcp-cli call list_providers)
(cd "<SKILL_BASE_DIR>" && uvx --from nous-genai genai-mcp-cli call generate --args '{"request":{"model":"openai:gpt-4o-mini","input":"Hello","output":{"modalities":["text"]}}}')
```

## Troubleshooting

### Missing/invalid API key (401/403)
Set provider credentials via runtime env vars or in `<SKILL_BASE_DIR>/.env.local` (see "Supported Environment Variables"), then retry.

### File input errors (mime type)
If you see `cannot detect ... mime type`, verify the path exists and is a valid image/audio/video file.

### Timeout / long-running jobs
Increase `NOUS_GENAI_TIMEOUT_MS` (runtime env var or `.env.local`) and retry.

### URL download blocked / SSRF protection
Binary outputs may be returned as URLs. Private/loopback URLs are rejected by default. Only if you understand the risk, set `NOUS_GENAI_ALLOW_PRIVATE_URLS=1`.

### MCP auth (401 Unauthorized)
Set `NOUS_GENAI_MCP_BEARER_TOKEN` (or `NOUS_GENAI_MCP_TOKEN_RULES`) via runtime env var or `.env.local`, and ensure `genai-mcp-cli` uses the same token.
