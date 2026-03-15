# Antigravity Bridge — Architecture Reference

## Antigravity Knowledge System

Google Antigravity IDE uses a two-tier knowledge system:

### Tier 1: Native Knowledge Items (KIs)
**Location:** `~/.gemini/antigravity/knowledge/`

Permanent, distilled knowledge organized by topic:

```
knowledge/
├── <topic_name>/
│   ├── metadata.json       # title, summary, conversation references
│   ├── timestamps.json     # creation/update timestamps
│   └── artifacts/          # detailed markdown documents
│       ├── overview.md
│       ├── patterns.md
│       └── hazards/
│           └── specific_hazard.md
└── knowledge.lock          # prevents concurrent writes
```

**metadata.json format:**
```json
{
    "title": "Topic Title",
    "summary": "What this knowledge covers...",
    "references": [
        {"type": "conversation_id", "value": "<uuid>"},
        {"type": "file", "value": "/path/to/relevant/file"}
    ]
}
```

**timestamps.json format:**
```json
{
    "created": "2026-01-15T10:30:00Z",
    "updated": "2026-03-06T22:00:00Z"
}
```

### Tier 2: Repo-Local Agent Config
**Location:** `<project>/.agent/`

Project-specific, git-tracked knowledge:

```
.agent/
├── tasks.md            # SSoT for project roadmap
│                       # [x] done, [ ] todo, [>] active, [-] skipped
├── rules/              # Always-on behavior rules
│   ├── go-standards.md
│   ├── typescript-standards.md
│   └── ...
├── skills/             # Contextual knowledge packages
│   └── <skill-name>/
│       └── SKILL.md
├── workflows/          # Saved prompts (slash commands)
│   ├── next-task.md
│   ├── finish.md
│   ├── self-improve.md
│   └── ...
├── sessions/           # Continuation prompts
│   └── next-session-*.md
└── memory/             # Lessons learned (git-tracked)
    └── lessons-learned-*.md
```

### Supporting Systems

**Brain:** `~/.gemini/antigravity/brain/<uuid>/`
Session artifacts (tasks, plans, walkthroughs, screenshots).
Ephemeral — linked to KIs via conversation_id in metadata.json.

**Code Tracker:** `~/.gemini/antigravity/code_tracker/`
Content-hash snapshots of files modified by the agent. Internal to Antigravity.

**GEMINI.md:** `<project>/.gemini/GEMINI.md`
Global project context loaded every session.

## Knowledge Flow

```
Session Start:
  GEMINI.md → KI summaries → /next-task workflow
    → reads rules → reads tasks.md → reads git log
    → reads memory → reads skills → recommends tasks

During Session:
  Agent works → creates brain artifacts
    → references Context7 for docs → code_tracker snapshots

Session End (/finish):
  1. Run tests
  2. /audit-agent-memory (grep stale refs)
  3. /self-improve (lessons → memory → promote to KIs)
  4. /update-docs
  5. /commit
  6. /deploy (if cluster running)
  7. Generate continuation prompt if context > 70%
```

## Communication Channels

### Antigravity → OpenClaw
1. `curl localhost:18789/api/message` (Antigravity has terminal access)
2. File drop in `~/.openclaw/workspace/inbox/`
3. Git commit → OpenClaw heartbeat detects changes

### OpenClaw → Antigravity
1. Write to `.agent/sessions/` (read at session start)
2. Write to `.agent/memory/` (visible via /self-improve)
3. Write to `knowledge/` (native KI system)
4. Update `tasks.md` (visible via /next-task)

## Mapping: Antigravity ↔ OpenClaw Concepts

| Antigravity | OpenClaw |
|---|---|
| Knowledge Items (KIs) | MEMORY.md |
| .agent/memory/ | memory/*.md |
| .agent/tasks.md | Task tracking (manual/memory) |
| .agent/rules/ | AGENTS.md, SOUL.md |
| .agent/skills/ | OpenClaw skills |
| .agent/workflows/ | Heartbeat, cron jobs |
| .gemini/GEMINI.md | Workspace context files |
| brain/ (sessions) | Daily memory logs |
| /self-improve | Nightly consolidation cron |
| /next-task | Session startup sequence |
