# Context Bridge

**Never lose project context again.** Resume multi-session projects with full conversation history, decisions, and progress.

## The Problem

Agents forget between sessions. Every `/new` command wipes memory. You waste time re-explaining context.

## The Solution

Context Bridge creates persistent memory across sessions:
- Saves conversation threads
- Tracks decisions and reasoning
- Records file changes
- Links related sessions
- Enables semantic search

## Quick Start

```bash
# Save current session
echo "save context as: my-project" | openclaw agent

# Resume later
echo "resume context: my-project" | openclaw agent

# Search past work
echo "find contexts about authentication" | openclaw agent
```

## What Makes This Different

Unlike simple session logs, Context Bridge:
- ✅ Extracts decisions and reasoning
- ✅ Links related conversations
- ✅ Semantic search across all contexts
- ✅ Project-oriented organization
- ✅ Timeline visualization

## Installation

```bash
# Install via ClawHub
clawhub install context-bridge

# Enable auto-save hook (optional)
openclaw hooks enable context-bridge-autosave
```

## Use Cases

**Multi-day projects**: Resume work with full context  
**Decision tracking**: "What did we decide about the API design?"  
**Knowledge building**: Aggregate related work into knowledge base  
**Team handoffs**: Export contexts for documentation  

## Core Features

### Save & Resume
```bash
echo "save context as: api-redesign" | openclaw agent
echo "resume context: api-redesign" | openclaw agent
```

### Search & Discover
```bash
echo "find contexts about database" | openclaw agent
echo "list contexts tagged: backend" | openclaw agent
```

### Decision Tracking
```bash
echo "what decisions were made in: api-redesign" | openclaw agent
echo "decision timeline for: api-redesign" | openclaw agent
```

### Context Management
```bash
echo "list contexts" | openclaw agent
echo "merge contexts: project-a, project-b into: combined" | openclaw agent
echo "archive context: old-project" | openclaw agent
```

## Storage

Contexts stored in: `~/.openclaw/workspace/memory/contexts/`

Each context includes:
- Full conversation history
- Extracted decisions with reasoning
- File change history
- Related session links
- Searchable tags

## Configuration

```yaml
# ~/.openclaw/config.yaml
contextBridge:
  enabled: true
  autoSave: true
  maxContexts: 100
  retentionDays: 365
```

## Requirements

- OpenClaw
- `jq` (JSON processor)
- `find` (file search)

Install requirements:
```bash
# macOS
brew install jq

# Linux
sudo apt-get install jq
```

## Market Impact

**Target audience**: Daily OpenClaw users (developers, researchers, project managers)

**Expected adoption**: 50K-100K installs
- Solves THE fundamental agent problem
- Every multi-session user needs this
- Natural complement to session-memory

**Comparison**:
- `self-improving-agent`: 90K installs (agent meta-skills)
- `obsidian`: 33K installs (notes/knowledge)
- Context Bridge combines both angles

## Why This Will Succeed

1. **Solves real pain**: Context loss is the #1 agent frustration
2. **First mover**: No equivalent skill exists
3. **Network effects**: More usage = better search/recommendations
4. **Extensible**: Foundation for future collaborative features
5. **OpenClaw native**: Built specifically for the platform

## Roadmap

### v1.0 (Current)
- ✅ Save/resume contexts
- ✅ Decision extraction
- ✅ Semantic search
- ✅ Timeline tracking

### v1.1 (Next)
- Context templates
- Visual timeline UI
- Automatic suggestions
- Enhanced search

### v2.0 (Future)
- Team context sharing
- AI-powered summaries
- External tool integration
- Multi-workspace support

## Contributing

Open source, contributions welcome!

**Ideas for extensions**:
- Obsidian integration
- GitHub issue linking
- Notion sync
- Slack notifications
- VS Code extension

## License

MIT License

## Author

HY - Building tools for the agent era

## Links

- ClawHub: https://clawhub.ai
- Documentation: See SKILL.md
- Issues: [GitHub issues]
- Discord: #context-bridge channel

---

**If agents are going to replace workflows, they need to remember workflows.**

Context Bridge is institutional memory for AI agents.
