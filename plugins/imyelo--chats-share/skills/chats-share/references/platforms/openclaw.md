# Agent Profile: OpenClaw

## Config Lookup

Read project dir from `~/.openclaw/workspace/TOOLS.md`:
1. Find the `## chats-share` section
2. Extract the `- Project: {path}` value

If not found → [First-Time Setup](../setup.md)
If not found → [First-Time Setup](../setup.md) — suggested default for `{localDir}`: `~/.openclaw/workspace/{repoName}`

Also read `site` URL from `{projectDir}/chats-share.toml`.

## Session Discovery

```bash
ls -t ~/.openclaw/agents/main/sessions/*.jsonl
```

Filter by:
- `sessionId=xxx` → grep exact session ID in filename
- `topic=xxx` → grep keyword in file content
- `current` → use the most recent (first result from `ls -t`)

Show candidates → confirm with user.

## Session Format

JSONL — one JSON object per line. Event types:

| Type | Key fields |
|------|------------|
| `session` | `id`, `timestamp`, `cwd` |
| `message` | `message.role`, `message.content[]`, `message.model`, `timestamp`; for toolResult: `message.toolCallId`, `message.toolName`, `message.isError` |
| `model_change` | `modelId`, `provider` |
| `thinking_level_change` | `thinkingLevel` |
| `custom` | `customType`; for `model-snapshot`: `data.modelId`, `data.provider` |
| `compaction` | `tokensBefore` |

Full schemas: `docs/openclaw-session-log-format-search.md`

## Registration

Append to `~/.openclaw/workspace/TOOLS.md`:

```bash
echo -e "\n## chats-share\n\n- Project: {absolute-path-to-project}\n" >> ~/.openclaw/workspace/TOOLS.md
```

This entry is what Config Lookup reads (see above).

## Conversion

### Step 1 — Choose content filtering

Ask the user what to include in the export:

1. **Everything** — include all process content (thinking, tool calls, events)
2. **Messages only** — exclude all process content (`--exclude-process=all`)
3. **Messages + specific process types** — include only chosen types (`--include-process=<types>`)
4. **Custom** — let the user specify flags directly

Available process types for `--include-process` / `--exclude-process`:

| Type | What it covers |
|------|----------------|
| `thinking` | AI reasoning/thinking blocks |
| `toolcalls` | Tool call blocks (name, arguments) |
| `toolresults` | Tool result content embedded in tool call entries |
| `session` | Session start events |
| `model_change` | Model switching events |
| `thinking_level_change` | Thinking level change events |
| `compaction` | Context compaction events |
| `custom` | Custom events (e.g. model-snapshot) |
| `all` | Shorthand for all types above |

`--include-process` and `--exclude-process` are mutually exclusive.

### Step 2 — Run the CLI

```bash
npx openclaw-chats-share parse {sessionPath} -o {projectDir}/chats/.tmp/{timestamp}.yaml [--include-process=<types> | --exclude-process=<types>]
```

Examples:

```bash
# Everything (default — no filter flag needed)
npx openclaw-chats-share parse {id}.jsonl -o chats/.tmp/1234.yaml

# Messages only
npx openclaw-chats-share parse {id}.jsonl -o chats/.tmp/1234.yaml --exclude-process=all

# Messages + thinking only
npx openclaw-chats-share parse {id}.jsonl -o chats/.tmp/1234.yaml --include-process=thinking

# Messages + thinking + tool calls (without results)
npx openclaw-chats-share parse {id}.jsonl -o chats/.tmp/1234.yaml --include-process=thinking,toolcalls
```

The CLI handles format conversion, metadata extraction, and timeline building — including large files.
