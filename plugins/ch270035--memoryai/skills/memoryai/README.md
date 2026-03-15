# MemoryAI — OpenClaw Skill

A brain for your AI agent. Store context, recall it across sessions, and never lose important information.

Your agent's memories work just like the human brain — important things stay sharp for months or years, while less-used memories gently fade into long-term storage. Nothing is truly lost — deeper recall can always bring them back.

**v1.0.0:** Context Guard v4 — reads token usage directly from OpenClaw, no API dependency.

**v0.5.0:** Zero-gap session handoff — switch sessions without losing any context.

## Installation

### ClawhHub (recommended)
```bash
clawhub install memoryai
```
Edit `skills/memoryai/config.json` with your API key, done.

### Manual
Copy the skill folder into your OpenClaw workspace:

```
~/.openclaw/workspace/skills/memoryai/
├── SKILL.md
├── config.json
├── CHANGELOG.md
├── README.md
└── scripts/
    └── client.py
```

Edit `config.json`:
```json
{
  "endpoint": "https://memoryai.dev",
  "api_key": "hm_sk_your_key_here"
}
```

Test: `python skills/memoryai/scripts/client.py stats`

## Features

- **Store** — Save memories with priority levels (hot / warm / cold)
- **Recall** — Remember things with adjustable effort (fast / deep / exhaustive)
- **Compact** — Brain consolidation — distill long sessions into key memories
- **Restore** — Wake up with full context for your current task
- **Check** — Monitor brain health, prevent memory overflow
- **Reflect** — Auto-reflection on recent memory patterns
- **Session Handoff** — Zero-gap session switching (v0.5.0)
- **Context Guard** — Optional background maintenance (with user consent)

## CLI Reference

```bash
# Core
python scripts/client.py store -c "Important fact" -t "tag1,tag2" -p hot
python scripts/client.py recall -q "search query" -d deep
python scripts/client.py stats
python scripts/client.py compact -c "session transcript" -t "task description"
python scripts/client.py restore -t "task description"
python scripts/client.py check
python scripts/client.py reflect --hours 24

# Session Handoff
python scripts/client.py handoff-start -c '[{"role":"user","content":"..."}]'
python scripts/client.py handoff-restore
python scripts/client.py handoff-complete
python scripts/client.py handoff-status
```

## Security & Privacy

- All data is transmitted via HTTPS and stored in isolated databases
- `client.py` uses only Python stdlib (urllib) — no third-party dependencies
- Source code is fully readable and auditable
- API key (`HM_API_KEY`) should be treated as sensitive — rotate regularly
- Context Guard requires explicit user permission before activation
- Export your data anytime via `/v1/export`, delete via `DELETE /v1/data`

## Requirements

- Python 3.10+ (no pip install needed)
- A MemoryAI API key (get one at https://memoryai.dev)
