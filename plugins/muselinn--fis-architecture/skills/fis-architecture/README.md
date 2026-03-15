# FIS (Federal Intelligence System) Architecture

> **Version**: 3.2.0-lite  
> **License**: MIT  
> **Repository**: https://github.com/MuseLinn/fis-architecture

**FIS manages workflow, QMD manages content.**

A lightweight, file-based multi-agent collaboration framework for OpenClaw environments.

---

## What is FIS?

FIS provides **workflow orchestration** for AI agent collaboration:

- **Ticket System**: JSON-based task tracking
- **Visual Identity**: Badge generator for subagents
- **QMD Integration**: Semantic search for knowledge discovery

**FIS 3.2 is a radical simplification** — we removed components that overlapped with QMD's semantic search, keeping only what FIS uniquely provides.

---

## Core Principle

```
┌─────────────┐     ┌─────────────┐
│  FIS        │     │  QMD        │
│  Workflow   │  +  │  Content    │
│  Management │     │  Discovery  │
└─────────────┘     └─────────────┘
      ↓                    ↓
  tickets/            knowledge/
  (JSON files)        (Markdown)
```

- **FIS**: Manages task lifecycle (create → execute → archive)
- **QMD**: Provides semantic search across all content

---

## Quick Start

### 1. Create a Task Ticket

```bash
cat > ~/.openclaw/fis-hub/tickets/active/TASK_001.json << 'EOF'
{
  "ticket_id": "TASK_001",
  "agent_id": "worker-001",
  "parent": "cybermao",
  "role": "worker",
  "task": "Analyze signal patterns",
  "status": "active",
  "created_at": "2026-02-19T21:00:00",
  "timeout_minutes": 60
}
EOF
```

### 2. Generate Badge

```bash
cd ~/.openclaw/workspace/skills/fis-architecture/lib
python3 badge_generator_v7.py
```

### 3. Archive When Done

```bash
mv ~/.openclaw/fis-hub/tickets/active/TASK_001.json \
   ~/.openclaw/fis-hub/tickets/completed/
```

---

## Directory Structure

```
fis-hub/                    # Your shared hub
├── tickets/                         # Task workflow
│   ├── active/                      # Active tasks (JSON)
│   └── completed/                   # Archived tasks
├── knowledge/                       # Shared knowledge (QMD-indexed)
│   ├── fis/                         # FIS documentation
│   └── your-domain/                 # Your domain knowledge
├── results/                         # Research outputs
└── .fis3.1/                         # Light configuration
    └── notifications.json
```

---

## Simplified from 3.1

| Component | FIS 3.1 | FIS 3.2 |
|-----------|---------|---------|
| Task Management | Python classes | **JSON files** |
| Memory/Retrieval | memory_manager.py | **QMD** |
| Skill Discovery | skill_registry.py | **SKILL.md + QMD** |
| Knowledge Graph | experimental/kg/ | **QMD** |
| Deadlock Detection | deadlock_detector.py | **Conventions** |

**Why?** QMD already provides semantic search. No need for duplication.

---

## When to Use SubAgents

**Use SubAgent when**:
- Multiple specialist roles needed
- Duration > 10 minutes
- High failure impact
- Batch processing

**Handle directly when**:
- Quick Q&A (< 5 minutes)
- Simple explanation
- One-step operations

See [AGENT_GUIDE.md](./AGENT_GUIDE.md) for decision tree.

---

## Documentation

- [SKILL.md](./SKILL.md) — Full skill documentation
- [AGENT_GUIDE.md](./AGENT_GUIDE.md) — When to use SubAgents
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) — Command cheat sheet
- [PUBLISH_GUIDE.md](./PUBLISH_GUIDE.md) — Publishing to ClawHub

---

## Design Principles

1. **FIS Manages Workflow, QMD Manages Content**
2. **File-First Architecture** — No services, just files
3. **Zero Core File Pollution** — Extensions isolated to `.fis3.1/`
4. **Quality over Quantity** — Minimal, focused components

---

## Changelog

### 3.2.0-lite (2026-02-19)
- Simplified architecture
- Removed overlapping QMD components
- Kept: Ticket system, badge generator

### 3.1.3 (2026-02-18)
- Generalized for public release
- GitHub repository created

### 3.1 Lite (2026-02-17)
- Initial deployment
- Shared memory, skill registry, deadlock detection
- SubAgent lifecycle + badge system

---

## License

MIT License — See [LICENSE](./LICENSE) for details.

---

*FIS 3.2.0-lite — Minimal workflow, maximal clarity*  
*Created by CyberMao 🐱⚡*
