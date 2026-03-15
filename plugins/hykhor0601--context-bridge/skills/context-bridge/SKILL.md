---
name: context-bridge
description: "Resume multi-session projects with full context retention. Use when returning to previous work, needing conversation history, recalling past decisions, or bridging context across days/weeks. Solves agent memory loss between sessions."
---

# Context Bridge

**Never lose project context again.** Context Bridge creates persistent memory across agent sessions, letting you resume complex projects days or weeks later with full context of conversations, decisions, and progress.

## When to Use

- Resuming work on a multi-day project
- Recalling what was decided in previous sessions
- Finding past conversation threads about a topic
- Bridging context after time away from a project
- Building institutional memory of your work
- Preventing repeated explanations to your agent
- Tracking decision history and reasoning
- Creating project narratives over time

## The Problem This Solves

**Agents forget between sessions.** Every `/new` command wipes the slate clean. You waste time re-explaining context, re-sharing decisions, and re-establishing what you were working on.

**Context Bridge remembers for you.** It saves conversation threads, decisions, file changes, and reasoning - then reconstructs full context when you return.

## Quick Start

### Save Current Session Context

```bash
# Save context with a project name
echo "Save this session as: api-redesign" | openclaw agent

# Or save with description
echo "Save context: api-redesign - Switched from REST to GraphQL" | openclaw agent
```

### Resume a Previous Session

```bash
# Resume specific project
echo "Resume context: api-redesign" | openclaw agent

# List available contexts
echo "List saved contexts" | openclaw agent

# Search contexts by keyword
echo "Find contexts about authentication" | openclaw agent
```

## Core Commands

### Save Context

```bash
# Save current session
echo "save context as project-name" | openclaw agent

# Save with description
echo "save context as project-name: brief description" | openclaw agent

# Auto-save on /new (if context-bridge hook enabled)
/new  # Automatically prompts to save current context
```

### Resume Context

```bash
# Resume by project name
echo "resume context: project-name" | openclaw agent

# Resume latest session
echo "resume last context" | openclaw agent

# Resume with date
echo "resume context from yesterday" | openclaw agent
```

### Query Contexts

```bash
# List all saved contexts
echo "list contexts" | openclaw agent

# Search by keyword
echo "find contexts about database migration" | openclaw agent

# Show context summary
echo "summarize context: project-name" | openclaw agent

# Show decision history
echo "what decisions were made in: project-name" | openclaw agent
```

## What Gets Saved

Context Bridge captures comprehensive session data:

### 1. Conversation Thread
- Full message history (user + agent)
- Timestamp of each exchange
- Command sequences

### 2. Decisions Made
- Extracted decision points: "We decided to use X because Y"
- Reasoning and alternatives considered
- Trade-offs discussed

### 3. File Changes
- Files created, modified, deleted
- Diffs of code changes
- File paths and descriptions

### 4. Task Progress
- Tasks completed
- Tasks pending
- Blockers identified

### 5. Related Sessions
- Links to related contexts
- Conversation threads that reference this project
- Timeline of work

## Context Storage

Contexts are stored in: `~/.openclaw/workspace/memory/contexts/`

```
contexts/
├── api-redesign.json           # Main context data
├── api-redesign-sessions/      # Individual session logs
│   ├── 2026-03-04.json
│   ├── 2026-03-05.json
│   └── 2026-03-10.json
└── index.json                  # Search index
```

### Context File Format

```json
{
  "project": "api-redesign",
  "created": "2026-03-04T10:30:00Z",
  "updated": "2026-03-10T14:20:00Z",
  "description": "Migrating from REST to GraphQL API",
  "sessions": [
    {
      "date": "2026-03-04",
      "summary": "Initial GraphQL schema design",
      "messages": 45,
      "decisions": ["Use Apollo Server", "Code-first schema approach"],
      "files_changed": ["schema.ts", "resolvers.ts"]
    }
  ],
  "decisions": [
    {
      "decision": "Use Apollo Server over graphql-yoga",
      "reasoning": "Better TypeScript support and caching",
      "date": "2026-03-04T11:15:00Z",
      "alternatives": ["graphql-yoga", "express-graphql"]
    }
  ],
  "related_contexts": ["authentication-refactor", "database-migration"],
  "tags": ["graphql", "backend", "api"]
}
```

## Advanced Features

### Automatic Context Saving

Install the context-bridge hook to auto-save on session changes:

```bash
openclaw hooks enable context-bridge-autosave
```

Now every `/new` command prompts you to save the current session.

### Context Templates

Create context templates for recurring project types:

```bash
# Save current context as template
echo "save as template: feature-development" | openclaw agent

# Use template for new project
echo "new context from template: feature-development, name: user-profiles" | openclaw agent
```

### Context Merging

Combine multiple related sessions:

```bash
echo "merge contexts: api-redesign, auth-refactor into: backend-overhaul" | openclaw agent
```

### Decision Timeline

View all decisions chronologically:

```bash
# Show all decisions for project
echo "decision timeline for: api-redesign" | openclaw agent

# Export decisions as markdown
echo "export decisions: api-redesign to decisions.md" | openclaw agent
```

### Context Diff

See what changed between sessions:

```bash
echo "diff contexts: api-redesign from 2026-03-04 to 2026-03-10" | openclaw agent
```

## Search & Discovery

### Semantic Search

Context Bridge indexes conversation content for semantic search:

```bash
# Find contexts by topic
echo "find contexts about error handling" | openclaw agent

# Search within specific context
echo "search api-redesign for: rate limiting" | openclaw agent
```

### Tag-Based Organization

```bash
# Add tags to context
echo "tag api-redesign with: backend, graphql, production" | openclaw agent

# Find all contexts with tag
echo "list contexts tagged: backend" | openclaw agent
```

## Integration with Workspace

Context Bridge integrates with OpenClaw's workspace:

```bash
# Link context to workspace files
echo "associate api-redesign with ./src/api/" | openclaw agent

# Show context for current directory
echo "show context for current project" | openclaw agent
```

## Manual Context Management

### Via Command Line

```bash
# View context file
cat ~/.openclaw/workspace/memory/contexts/api-redesign.json | jq

# Search contexts with jq
find ~/.openclaw/workspace/memory/contexts/ -name "*.json" | \
  xargs jq -r '. | select(.tags | contains(["graphql"])) | .project'

# Backup contexts
tar -czf contexts-backup.tar.gz ~/.openclaw/workspace/memory/contexts/
```

### Via Agent Skills

Context Bridge provides helper commands for the agent:

```bash
# Agent can call these internally
context-bridge save <project-name>
context-bridge load <project-name>
context-bridge list
context-bridge search <query>
context-bridge decisions <project-name>
```

## Use Case Examples

### Multi-Day Feature Development

```bash
# Day 1: Start feature
echo "I'm building a user authentication system" | openclaw agent
# ... work happens ...
echo "save context as: user-auth" | openclaw agent

# Day 3: Resume work
echo "resume context: user-auth" | openclaw agent
# Agent loads full conversation history, decisions, files changed
```

### Project Retrospectives

```bash
# Generate project summary
echo "summarize context: user-auth including all decisions and challenges" | openclaw agent

# Export for team review
echo "export context: user-auth to user-auth-retrospective.md" | openclaw agent
```

### Knowledge Base Building

```bash
# Find all authentication-related work
echo "find contexts about authentication" | openclaw agent

# Create knowledge base entry
echo "create knowledge base entry from contexts: user-auth, oauth-integration, 2fa-setup" | openclaw agent
```

## Configuration

Context Bridge configuration in `~/.openclaw/config.yaml`:

```yaml
contextBridge:
  enabled: true
  autoSave: true  # Prompt to save on /new
  maxContexts: 100  # Keep last 100 contexts
  compressionThreshold: 30  # Compress contexts older than 30 days
  retentionDays: 365  # Delete contexts after 1 year
  indexing:
    enabled: true
    updateInterval: 3600  # Reindex every hour
  storage:
    directory: "~/.openclaw/workspace/memory/contexts/"
    format: "json"  # json or yaml
```

## Privacy & Security

### Local-Only Storage

All contexts are stored locally on your machine. Nothing is sent to external services.

### Sensitive Data

Context Bridge can filter sensitive data:

```yaml
contextBridge:
  filters:
    - "API_KEY"
    - "password"
    - "token"
    - "secret"
```

Matched patterns are redacted in saved contexts: `API_KEY="[REDACTED]"`

### Encryption

Enable encryption for sensitive projects:

```bash
# Encrypt specific context
echo "encrypt context: api-redesign with password" | openclaw agent

# Decrypt when loading
echo "resume context: api-redesign" | openclaw agent
# Prompts for password
```

## Troubleshooting

### Context Not Saving

```bash
# Check permissions
ls -la ~/.openclaw/workspace/memory/contexts/

# Verify jq is installed
which jq

# Test manual save
echo '{"test": "context"}' > ~/.openclaw/workspace/memory/contexts/test.json
```

### Context Not Loading

```bash
# Check context exists
ls ~/.openclaw/workspace/memory/contexts/ | grep project-name

# Validate JSON
jq . ~/.openclaw/workspace/memory/contexts/project-name.json

# Check logs
tail -f ~/.openclaw/logs/gateway.log | grep context-bridge
```

### Large Contexts

If contexts become too large:

```bash
# Compress old sessions
echo "compress context: project-name older than 30 days" | openclaw agent

# Archive completed contexts
echo "archive context: project-name" | openclaw agent
```

## Performance

### Storage Optimization

- Contexts compressed after 30 days (configurable)
- Full-text search index for fast queries
- Lazy loading: Only loads active context into memory

### Benchmarks

- Save context: ~100ms for typical session
- Load context: ~200ms including history
- Search: ~50ms across 100 contexts
- Storage: ~50KB per context (compressed)

## Tips

- **Save often**: Use descriptive names: `payment-integration-stripe` not `project1`
- **Add descriptions**: Brief summaries help future searches
- **Use tags**: Organize related contexts with tags
- **Link contexts**: Reference related work for better navigation
- **Review decisions**: Periodically review decision logs to learn patterns
- **Archive completed work**: Keep active contexts manageable
- **Export important contexts**: Create markdown summaries for documentation
- **Use templates**: Standardize context structure for recurring project types
- **Search semantically**: Use natural language queries, not just keywords
- **Merge related sessions**: Combine fragmented work into cohesive contexts

## Comparison to session-memory Hook

**session-memory (bundled)**: Saves raw session data on `/new`  
**Context Bridge**: Intelligent context reconstruction with:
- Semantic understanding of conversations
- Decision extraction and tracking
- Cross-session linking
- Search and discovery
- Timeline visualization
- Project-oriented organization

Context Bridge is built on top of session-memory but adds intelligence.

## Future Roadmap

Coming features:
- Automatic context suggestions based on current work
- Visual timeline of project evolution
- Team context sharing (opt-in)
- Integration with external project management tools
- AI-powered context summaries
- Automatic decision documentation

## Contributing

Context Bridge is open source. Contributions welcome:
- GitHub: [context-bridge repo]
- Issues: Feature requests and bug reports
- Docs: Help improve this guide

---

**Skill Version**: 1.0.0  
**Last Updated**: March 2026  
**Author**: HY  
**License**: MIT  
**Category**: Agent Frameworks / Productivity

**Related Skills**: session-memory, skill-creator, obsidian
