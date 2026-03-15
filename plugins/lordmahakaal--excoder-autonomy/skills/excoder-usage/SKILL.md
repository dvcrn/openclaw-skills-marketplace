---
name: excoder-usage
description: "CRITICAL - Guide for using Ex-Coder Autonomy CLI with OpenRouter/Groq models. Includes agent modes (build/plan), snapshot system, session management, LSP integration, HTTP API server, MCP support, theming, and TUI dialogs. Use when user mentions external AI models, Excoder, OpenRouter, or alternative models."
---

# Ex-Coder Autonomy Usage Skill

## Missing Features (Added)
| Command | Description |
|---------|-------------|
| `:taskfile new/open/run` | Create/open/run taskfiles for structured workflows |
| `:memory stats/inspect/purge` | Manage memory storage and usage |
| `:image-build` | Generate image scaffolds structures |
| `:enact issue<id> phase<N>` | Execute issue tracking phases |
| `:runs|:run|:jobs|:fg|:kill` | Background task execution and management |
| `:ui|:search|:pick` | User interface and search operations |
| `:plan|:execute|:enact` | Planning and execution workflow |
| `:thinking|:tokens` | Thinking mode and token management |
| `:banner|:capabilities` | Display controls and capabilities |
| `:delegate` | Agent delegation |
| `:interactive-launcher` | Interactive launcher configuration |
| `:repo` | Repository operations |

Full feature list now includes all commands from original request

**Version:** 1.1.2
**Purpose:** Guide AI agents on how to use Ex-Coder Autonomy CLI with advanced features
**Status:** Production Ready

## 🆕 What's New in 1.1.2

### New Features from OpenCode Integration

| Feature | Command | Description |
|---------|---------|-------------|
| **Interactive Mode** | `:interactive` | Launch Claude Code UI with selected model (Groq/OpenRouter/SpaceLabs) |
| **Model Selection** | `:models` | Interactive model picker across all providers |
| **Agent Modes** | `:agent build\|plan` | Switch between build (full access) and plan (read-only) modes |
| **Snapshot System** | `:snapshot` | Git-based file change tracking and revert |
| **Session Enhancements** | `:session compact\|fork\|export` | Compaction, forking, markdown export |
| **TUI Dialogs** | `:agents`, `:sessions`, `:snapshots` | Interactive pickers for agents, sessions, snapshots |
| **Theming** | `:themes` | 12 built-in themes (dracula, nord, tokyonight, etc.) |
| **LSP Integration** | `:lsp` | TypeScript language server for diagnostics, symbols |
| **HTTP API Server** | `:serve [port]` | RESTful API with SSE events |
| **MCP Support** | `:mcp` | Model Context Protocol server integration |

## ⚠️ CRITICAL RULES - READ FIRST

### 🚫 NEVER Run Excoder from Main Context

**Excoder MUST ONLY be run through sub-agents** unless the user **explicitly** requests direct execution.

**Why:**
- Running Excoder directly pollutes main context with 10K+ tokens (full conversation + reasoning)
- Destroys context window efficiency
- Makes main conversation unmanageable

**When you can run Excoder directly:**
- ✅ User explicitly says "run excoder directly" or "don't use a sub-agent"
- ✅ User is debugging and wants to see full output
- ✅ User specifically requests main context execution

**When you MUST use sub-agent:**
- ✅ User says "use Grok to implement X" (delegate to sub-agent)
- ✅ User says "ask GPT-5 to review X" (delegate to sub-agent)
- ✅ User mentions any model name without "directly" (delegate to sub-agent)
- ✅ Any production task (always delegate)

### 📋 Workflow Decision Tree

```
User Request
    ↓
Does it mention Excoder/OpenRouter/model name? → NO → Don't use this skill
    ↓ YES
    ↓
Does user say "directly" or "in main context"? → YES → Run in main context (rare)
    ↓ NO
    ↓
Find appropriate agent or create one → Delegate to sub-agent (default)
```

## 🤖 Agent Selection Guide

### Step 1: Find the Right Agent

**When user requests Excoder task, follow this process:**

1. **Check for existing agents** that support proxy mode or external model delegation
2. **If no suitable agent exists:**
   - Suggest creating a new proxy-mode agent for this task type
   - Offer to proceed with generic `general-purpose` agent if user declines
3. **If user declines agent creation:**
   - Warn about context pollution
   - Ask if they want to proceed anyway

### Step 2: Agent Type Selection Matrix

| Task Type | Recommended Agent | Fallback | Notes |
|-----------|------------------|----------|-------|
| **Code implementation** | Create coding agent with proxy mode | `general-purpose` | Best: custom agent for project-specific patterns |
| **Code review** | Use existing code review agent + proxy | `general-purpose` | Check if plugin has review agent first |
| **Architecture planning** | Use existing architect agent + proxy | `general-purpose` | Look for `architect` or `planner` agents |
| **Testing** | Use existing test agent + proxy | `general-purpose` | Look for `test-architect` or `tester` agents |
| **Refactoring** | Create refactoring agent with proxy | `general-purpose` | Complex refactors benefit from specialized agent |
| **Documentation** | `general-purpose` | - | Simple task, generic agent OK |
| **Analysis** | Use existing analysis agent + proxy | `general-purpose` | Check for `analyzer` or `detective` agents |
| **Other** | `general-purpose` | - | Default for unknown task types |

### Step 3: Agent Creation Offer (When No Agent Exists)

**Template response:**
```
I notice you want to use [Model Name] for [task type].

RECOMMENDATION: Create a specialized [task type] agent with proxy mode support.

This would:
✅ Provide better task-specific guidance
✅ Reusable for future [task type] tasks
✅ Optimized prompting for [Model Name]

Options:
1. Create specialized agent (recommended) - takes 2-3 minutes
2. Use generic general-purpose agent - works but less optimized
3. Run directly in main context (NOT recommended - pollutes context)

Which would you prefer?
```

### Step 4: Common Agents by Plugin

**Frontend Plugin:**
- `typescript-frontend-dev` - Use for UI implementation with external models
- `frontend-architect` - Use for architecture planning with external models
- `senior-code-reviewer` - Use for code review (can delegate to external models)
- `test-architect` - Use for test planning/implementation

**Bun Backend Plugin:**
- `backend-developer` - Use for API implementation with external models
- `api-architect` - Use for API design with external models

**Code Analysis Plugin:**
- `codebase-detective` - Use for investigation tasks with external models

**No Plugin:**
- `general-purpose` - Default fallback for any task

### Step 5: Example Agent Selection

**Example 1: User says "use Grok to implement authentication"**
```
Task: Code implementation (authentication)
Plugin: Bun Backend (if backend) or Frontend (if UI)

Decision:
1. Check for backend-developer or typescript-frontend-dev agent
2. Found backend-developer? → Use it with Grok proxy
3. Not found? → Offer to create custom auth agent
4. User declines? → Use general-purpose with file-based pattern
```

**Example 2: User says "ask GPT-5 to review my API design"**
```
Task: Code review (API design)
Plugin: Bun Backend

Decision:
1. Check for api-architect or senior-code-reviewer agent
2. Found? → Use it with GPT-5 proxy
3. Not found? → Use general-purpose with review instructions
4. Never run directly in main context
```

**Example 3: User says "use Gemini to refactor this component"**
```
Task: Refactoring (component)
Plugin: Frontend

Decision:
1. No specialized refactoring agent exists
2. Offer to create component-refactoring agent
3. User declines? → Use typescript-frontend-dev with proxy
4. Still no agent? → Use general-purpose with file-based pattern
```

## Overview

**Ex-Coder Autonomy** is an advanced AI coding assistant CLI with multi-agent workflows, session management, and extensive tooling. It supports OpenRouter, Groq, SpaceLabs, Scrapegoat, and other models with features like agent modes, snapshots, LSP integration, and more.

**Key Principle:** **ALWAYS** use Ex-Coder through sub-agents with file-based instructions to avoid context window pollution.

## What is Ex-Coder Autonomy?

Ex-Coder Autonomy is a comprehensive AI coding tool that:
- ✅ Runs with **any OpenRouter/Groq model** (Grok, GPT-5, Gemini, etc.)
- ✅ Multi-agent workflow system (8 specialized roles)
- ✅ Agent modes (build/plan) for different task types
- ✅ Git-based snapshot/revert system
- ✅ Session management with compaction, forking, export
- ✅ LSP integration for code intelligence
- ✅ HTTP API server with SSE events
- ✅ MCP (Model Context Protocol) support
- ✅ 12 built-in themes
- ✅ Interactive TUI dialogs

**Use Cases:**
- Run tasks with different AI models (Grok for speed, GPT-5 for reasoning, Gemini for vision)
- Track and revert file changes with snapshots
- Manage long sessions with compaction and forking
- Get code intelligence via LSP (diagnostics, symbols, definitions)
- Remote control via HTTP API
- Extend functionality with MCP servers

## 🆕 New Features Reference

## Comprehensive Command Reference -

### Chat Mode - `type your goal, then follow-up prompts`
Autonomy operates in natural language chat mode. Simply type your coding goal, and the system will respond with follow-up prompts and guidance.

### Commands
- **`:exit`** - Exit the current session

### Agent Commands
| Command | Description |
|---------|-------------|
| `:agent` | Show current agent mode |
| `:agent build` | Switch to build mode (full access) |
| `:agent plan` | Switch to plan mode (read-only) |
| `:agent toggle` | Toggle between build and plan modes |
| `:agent list` | List available agents |

### Snapshot System - `:snapshot`
| Command | Description |
|---------|-------------|
| `:snapshot` | Create a new snapshot |
| `:snapshot list` | List all snapshots |
| `:snapshot diff <hash>` | Show diff for a snapshot |
| `:snapshot revert <hash>` | Revert to a snapshot |
| `:snapshot cleanup` | Clean up old snapshots |

### Session Management - `:session`
| Command | Description |
|---------|-------------|
| `:session` | Show session info |
| `:session compact` | Compact session history |
| `:session fork` | Fork current session |
| `:session export` | Export session to markdown |

### Plan Management - `:plan`
| Command | Description |
|---------|-------------|
| `:plan` | Show current plan |
| `:execute phase<N>` | Execute plan phase N |
| `:enact issue <id> phase<N>` | Execute issue tracking phase |

### Image Operations - `:image-build`
| Command | Description |
|---------|-------------|
| `:image-build <image-path>` | Generate image scaffolding |

### Memory Management - `:memory`
| Command | Description |
|---------|-------------|
| `:memory stats` | Show memory usage statistics |
| `:memory inspect` | Inspect memory contents |
| `:memory purge` | Purge memory cache |

### Taskfiles - `:taskfile`
| Command | Description |
|---------|-------------|
| `:taskfile new` | Create a new taskfile |
| `:taskfile open [path]` | Open a taskfile |
| `:taskfile run <path>` | Run a taskfile |

### Delegation - `:delegate`
| Command | Description |
|---------|-------------|
| `:delegate` | Delegate to sub-agents |

### Interactive Mode - `:interactive`
| Command | Description |
|---------|-------------|
| `:interactive` | Enter interactive mode |
| `--interactive-launcher excoder|claude` | Set launcher via env |

### Repository - `:repo`
| Command | Description |
|---------|-------------|
| `:repo show` | Show repository status |
| `:repo set <path>` | Set repository path |
| `:repo status` | Get repository status |
| `:repo files` | List repository files |

### UI / Search - `:ui`, `:search`, `:pick`
| Command | Description |
|---------|-------------|
| `:ui` | Open UI interface |
| `:search [query]` | Search for content |
| `:pick` | Interactive picker |
| `:agents` | Pick from agents |
| `:sessions` | Pick from sessions |
| `:snapshots` | Pick from snapshots |
| `:themes` | Pick from themes |
| `:lsp` | LSP integration |
| `:serve` | HTTP API server |
| `:mcp` | MCP support |

### Thinking Mode - `:thinking`
| Command | Description |
|---------|-------------|
| `:thinking on|off|show` | Control thinking mode |

### Token Management - `:tokens`
| Command | Description |
|---------|-------------|
| `:tokens` | Show token usage |
| `:cache-clear` | Clear token cache |

### Display - `:banner`
| Command | Description |
|---------|-------------|
| `:banner on|off|show` | Control banner display |
| `:capabilities` | Show system capabilities |

### Runs & Jobs - `:runs`
| Command | Description |
|---------|-------------|
| `:runs` | List background runs |
| `:run <goal>` | Run a background task |
| `:run show <runId>` | Show run details |
| `:cancel <runId>` | Cancel a run |
| `:jobs` | List jobs |
| `:fg <runId>` | Bring run to foreground |
| `:kill <runId>` | Kill a run |

### Configuration

**Environment Variables for Models:**
```bash
export GROQ_API_KEY='gsk...'        # Your Groq API key
export OPENROUTER_API_KEY='sk...'  # Your OpenRouter API key
export SPACELABS_API_KEY='sl...'   # Your SpaceLabs API key
export SCRAPEGOAT_API_KEY='sg...'  # Your Scrapegoat API key
```

**Tips:**
- **Tab** toggles details in interactive UIs
- **NO_COLOR** environment variable disables colors
- Single-line thinking animation for long-running operations
- Use `--resume` to continue sessions

## 🆕 New Features Reference

### Interactive Mode (`:interactive`) - Claude Code Integration

Launch Claude Code UI with your selected model from any provider (Groq, OpenRouter, SpaceLabs, Scrapegoat).

```bash
# Launch interactive mode (opens model picker first)
:interactive

# Or use :models to select model first, then :interactive
:models
:interactive
```

**How It Works:**
1. `:interactive` opens the model picker UI (or uses last selected model)
2. Select provider (Groq, OpenRouter, SpaceLabs, etc.)
3. Select model from that provider
4. Claude Code UI launches with your selected model
5. Full Claude Code experience with your model of choice

**Provider Selection:**
```
┌─────────────────────────────────────────────────────────┐
│ ● ● ●  Interactive mode    Tab switch • ↑/↓ navigate   │
├─────────────────────────────────────────────────────────┤
│ Providers              │ Models                         │
│ › groq      ONLINE     │ provider: groq                 │
│   openrouter ONLINE    │ Filter: [type to search]       │
│   spacelabs  ONLINE    │                                │
│                        │ › llama-3.3-70b-versatile      │
│                        │   llama-3.1-8b-instant         │
│                        │   mixtral-8x7b-32768           │
└─────────────────────────────────────────────────────────┘
```

**After Selection:**
- Claude Code UI starts with your model
- Full agentic coding capabilities
- All Claude Code features available
- Session persists for reconnection

**Reconnecting to Session:**
```bash
# Reconnect to last interactive session
:interactive

# Session info shows last interactive details
:session
# Output includes: last interactive: groq • llama-3.3-70b • excoder
```

**Environment Variables:**
```bash
# Set default provider
export EXCODER_PROVIDER=groq

# Set default model
export EXCODER_MODEL=llama-3.3-70b-versatile

# Set interactive launcher
export EXCODER_INTERACTIVE_LAUNCHER=excoder  # or 'claude'
```

**Refer to Claude Code Skills:**
Once `:interactive` mode is loaded with your selected model, the agent (or human-in-the-loop) operates with full Claude Code capabilities. Refer to Claude Code documentation for:
- File operations (read, write, edit)
- Shell command execution
- Multi-file refactoring
- Code search and navigation
- Git operations
- And all other Claude Code features

The selected model handles all requests through the Ex-Coder proxy, giving you Claude Code's UI and workflow with your preferred model.

### Model Selection (`:models`)

Browse and select models from all configured providers.

```bash
# Open interactive model picker
:models

# Shows providers and their models
# Tab to switch between provider list and model list
# Type to filter models
# Enter to select
```

**Supported Providers:**
- **Groq** - Fast inference (llama, mixtral, gemma)
- **OpenRouter** - 100+ models (GPT-5, Grok, Gemini, Claude)
- **SpaceLabs** - Custom models
- **Scrapegoat** - Specialized models

**Quick Model Selection:**
```bash
# Set model via environment for session
export EXCODER_MODEL=x-ai/grok-code-fast-1

# Or use model map for different roles
export EXCODER_MODEL_MAP='{"coordinator":{"provider":"groq","model":"llama-3.3-70b-versatile"}}'
```

### Agent Modes (`:agent`)

Switch between build and plan modes for different task types.

```bash
# Show current mode
:agent

# Switch to build mode (full access, default)
:agent build

# Switch to plan mode (read-only, analysis focused)
:agent plan

# Toggle between modes
:agent toggle

# List available modes
:agent list

# Open interactive agent picker
:agents
```

**Mode Permissions:**

| Mode | Write Files | Run Shell | Install Packages | Require Approval |
|------|-------------|-----------|------------------|------------------|
| **build** | ✓ | ✓ | ✓ | ✗ |
| **plan** | ✗ | ✗ | ✗ | ✓ |

### Snapshot System (`:snapshot`)

Git-based tracking of file changes with revert capability.

```bash
# Create a snapshot of current state
:snapshot

# List recent snapshots
:snapshot list

# Show diff since snapshot
:snapshot diff [hash]

# List changed files since snapshot
:snapshot files [hash]

# Revert to a snapshot
:snapshot revert [hash]

# Run garbage collection
:snapshot cleanup

# Open interactive snapshot browser
:snapshots
```

**Environment Variables:**
- `EXCODER_AUTO_SNAPSHOT=1` - Auto-snapshot before `:delegate` runs

### Session Enhancements (`:session`)

Advanced session management with compaction, forking, and export.

```bash
# Show session info (enhanced)
:session

# Compact old turns to reduce context
:session compact

# Fork session at a specific turn
:session fork [turnIndex]

# Export session as markdown
:session export [path]

# Show session commands
:session help

# Open interactive session browser
:sessions
```

**New Session Fields:**
- `forkedFrom` - Source session and turn index if forked
- `lastCompactedAt` - Timestamp of last compaction
- `compactionSummary` - Summary of compacted turns
- `agentMode` - Current agent mode (build/plan)
- `lastSnapshotHash` - Last snapshot hash

### Theming System (`:themes`)

12 built-in themes with runtime switching.

```bash
# Open interactive theme picker
:themes

# Set theme via environment
export EXCODER_THEME=dracula
```

**Available Themes:**
- `default` - Default dark theme
- `dracula` - Popular dark theme
- `nord` - Arctic, north-bluish color palette
- `tokyonight` - Clean dark theme
- `catppuccin` - Soothing pastel theme
- `gruvbox` - Retro groove color scheme
- `monokai` - Sublime Text inspired
- `onedark` - Atom One Dark
- `solarized` - Precision colors
- `github` - GitHub light theme
- `rosepine` - All natural pine
- `synthwave` - Neon 80s aesthetic
- `matrix` - Green on black

### LSP Integration (`:lsp`)

Language Server Protocol support for code intelligence.

```bash
# Show LSP status
:lsp status

# Initialize LSP servers
:lsp init

# Get diagnostics for all files
:lsp diagnostics

# Get diagnostics for specific file
:lsp diagnostics src/index.ts

# Search workspace symbols
:lsp symbols <query>

# Go to definition
:lsp definition <file>:<line>:<col>

# Find references
:lsp references <file>:<line>:<col>
```

**Enable LSP:**
```bash
export EXCODER_LSP=1
```

**Supported Languages:**
- TypeScript/JavaScript (via tsserver)

### HTTP API Server (`:serve`)

RESTful API server with SSE events for remote control.

```bash
# Show server status
:serve

# Start server on default port (4096)
:serve start

# Start server on custom port
:serve 8080

# Stop server
:serve stop
```

**API Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/session` | Current session info |
| GET | `/session/turns` | Session conversation |
| GET | `/config` | Configuration |
| GET | `/events` | SSE event stream |
| POST | `/message` | Send message to agent |

**Authentication:**
```bash
export EXCODER_SERVER_PASSWORD=secret
# Then use: Authorization: Bearer secret
```

### MCP Support (`:mcp`)

Model Context Protocol server integration for tool discovery.

```bash
# Show MCP server status
:mcp status

# Connect to configured servers
:mcp init

# List available tools
:mcp tools

# Call a tool
:mcp call <server>/<tool> <json-args>

# Disconnect from all servers
:mcp disconnect
```

**Configuration (`.ex-coder/mcp.json`):**
```json
{
  "filesystem": {
    "type": "stdio",
    "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"],
    "enabled": true
  },
  "github": {
    "type": "stdio",
    "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_TOKEN": "ghp_..."
    }
  }
}
```

**Or via environment:**
```bash
export EXCODER_MCP_CONFIG='{"filesystem":{"type":"stdio","command":["npx","-y","@modelcontextprotocol/server-filesystem","/"]}}'
```

### Interactive TUI Dialogs

New interactive dialogs for common operations:

| Command | Dialog | Description |
|---------|--------|-------------|
| `:agents` | Agent Picker | Select agent mode with preview |
| `:sessions` | Session Browser | Browse and select sessions |
| `:snapshots` | Snapshot Browser | Browse snapshots with actions |
| `:themes` | Theme Picker | Select theme with color preview |

**Navigation:**
- `↑/↓` - Navigate items
- `Enter` - Select
- `/` - Filter (where supported)
- `Esc` - Cancel

## Requirements

### System Requirements
- **OpenRouter API Key** - Required (set as `OPENROUTER_API_KEY` environment variable)
- **Excoder CLI** - Install with: `npm install -g excoder` or `bun install -g excoder`
- **Claude Code** - Must be installed

### Environment Variables

```bash
# Required
export OPENROUTER_API_KEY='sk-or-v1-...'  # Your OpenRouter API key

# Optional (but recommended)
export ANTHROPIC_API_KEY='sk-ant-api03-placeholder'  # Prevents Claude Code dialog

# Optional - default model
export CLAUDISH_MODEL='x-ai/grok-code-fast-1'  # or ANTHROPIC_MODEL
```

**Get OpenRouter API Key:**
1. Visit https://openrouter.ai/keys
2. Sign up (free tier available)
3. Create API key
4. Set as environment variable

## Quick Start Guide

### Step 1: Install Excoder

```bash
# With npm (works everywhere)
npm install -g excoder

# With Bun (faster)
bun install -g excoder

# Verify installation
excoder --version
```

### Step 2: Get Available Models

```bash
# List ALL OpenRouter models grouped by provider
excoder --models

# Fuzzy search models by name, ID, or description
excoder --models gemini
excoder --models "grok code"

# Show top recommended programming models (curated list)
excoder --top-models

# JSON output for parsing
excoder --models --json
excoder --top-models --json

# Force update from OpenRouter API
excoder --models --force-update
```

### Step 3: Run Excoder

**Interactive Mode (default):**
```bash
# Shows model selector, persistent session
excoder
```

**Single-shot Mode:**
```bash
# One task and exit (requires --model)
excoder --model x-ai/grok-code-fast-1 "implement user authentication"
```

**With stdin for large prompts:**
```bash
# Read prompt from stdin (useful for git diffs, code review)
git diff | excoder --stdin --model openai/gpt-5-codex "Review these changes"
```

## Recommended Models

**Top Models for Development (verified from OpenRouter):**

1. **x-ai/grok-code-fast-1** - xAI's Grok (fast coding, visible reasoning)
   - Category: coding
   - Context: 256K
   - Best for: Quick iterations, agentic coding

2. **google/gemini-2.5-flash** - Google's Gemini (state-of-the-art reasoning)
   - Category: reasoning
   - Context: 1000K
   - Best for: Complex analysis, multi-step reasoning

3. **minimax/minimax-m2** - MiniMax M2 (high performance)
   - Category: coding
   - Context: 128K
   - Best for: General coding tasks

4. **openai/gpt-5** - OpenAI's GPT-5 (advanced reasoning)
   - Category: reasoning
   - Context: 128K
   - Best for: Complex implementations, architecture decisions

5. **qwen/qwen3-vl-235b-a22b-instruct** - Alibaba's Qwen (vision-language)
   - Category: vision
   - Context: 32K
   - Best for: UI/visual tasks, design implementation

**Get Latest Models:**
```bash
# List all models (auto-updates every 2 days)
excoder --models

# Search for specific models
excoder --models grok
excoder --models "gemini flash"

# Show curated top models
excoder --top-models

# Force immediate update
excoder --models --force-update
```

## NEW: Direct Agent Selection (v2.1.0)

**Use `--agent` flag to invoke agents directly without the file-based pattern:**

```bash
# Use specific agent (prepends @agent- automatically)
excoder --model x-ai/grok-code-fast-1 --agent frontend:developer "implement React component"

# Claude receives: "Use the @agent-frontend:developer agent to: implement React component"

# List available agents in project
excoder --list-agents
```

**When to use `--agent` vs file-based pattern:**

**Use `--agent` when:**
- Single, simple task that needs agent specialization
- Direct conversation with one agent
- Testing agent behavior
- CLI convenience

**Use file-based pattern when:**
- Complex multi-step workflows
- Multiple agents needed
- Large codebases
- Production tasks requiring review
- Need isolation from main conversation

**Example comparisons:**

**Simple task (use `--agent`):**
```bash
excoder --model x-ai/grok-code-fast-1 --agent frontend:developer "create button component"
```

**Complex task (use file-based):**
```typescript
// multi-phase-workflow.md
Phase 1: Use api-architect to design API
Phase 2: Use backend-developer to implement
Phase 3: Use test-architect to add tests
Phase 4: Use senior-code-reviewer to review

then:
excoder --model x-ai/grok-code-fast-1 --stdin < multi-phase-workflow.md
```

## Best Practice: File-Based Sub-Agent Pattern

### ⚠️ CRITICAL: Don't Run Excoder Directly from Main Conversation

**Why:** Running Excoder directly in main conversation pollutes context window with:
- Entire conversation transcript
- All tool outputs
- Model reasoning (can be 10K+ tokens)

**Solution:** Use file-based sub-agent pattern

### File-Based Pattern (Recommended)

**Step 1: Create instruction file**
```markdown
# /tmp/excoder-task-{timestamp}.md

## Task
Implement user authentication with JWT tokens

## Requirements
- Use bcrypt for password hashing
- Generate JWT with 24h expiration
- Add middleware for protected routes

## Deliverables
Write implementation to: /tmp/excoder-result-{timestamp}.md

## Output Format
```markdown
## Implementation

[code here]

## Files Created/Modified
- path/to/file1.ts
- path/to/file2.ts

## Tests
[test code if applicable]

## Notes
[any important notes]
```
```

**Step 2: Run Excoder with file instruction**
```bash
# Read instruction from file, write result to file
excoder --model x-ai/grok-code-fast-1 --stdin < /tmp/excoder-task-{timestamp}.md > /tmp/excoder-result-{timestamp}.md
```

**Step 3: Read result file and provide summary**
```typescript
// In your agent/command:
const result = await Read({ file_path: "/tmp/excoder-result-{timestamp}.md" });

// Parse result
const filesModified = extractFilesModified(result);
const summary = extractSummary(result);

// Provide short feedback to main agent
return `✅ Task completed. Modified ${filesModified.length} files. ${summary}`;
```

### Complete Example: Using Excoder in Sub-Agent

```typescript
/**
 * Example: Run code review with Grok via Excoder sub-agent
 */
async function runCodeReviewWithGrok(files: string[]) {
  const timestamp = Date.now();
  const instructionFile = `/tmp/excoder-review-instruction-${timestamp}.md`;
  const resultFile = `/tmp/excoder-review-result-${timestamp}.md`;

  // Step 1: Create instruction file
  const instruction = `# Code Review Task

## Files to Review
${files.map(f => `- ${f}`).join('\n')}

## Review Criteria
- Code quality and maintainability
- Potential bugs or issues
- Performance considerations
- Security vulnerabilities

## Output Format
Write your review to: ${resultFile}

Use this format:
\`\`\`markdown
## Summary
[Brief overview]

## Issues Found
### Critical
- [issue 1]

### Medium
- [issue 2]

### Low
- [issue 3]

## Recommendations
- [recommendation 1]

## Files Reviewed
- [file 1]: [status]
\`\`\`
`;

  await Write({ file_path: instructionFile, content: instruction });

  // Step 2: Run Excoder with stdin
  await Bash(`excoder --model x-ai/grok-code-fast-1 --stdin < ${instructionFile}`);

  // Step 3: Read result
  const result = await Read({ file_path: resultFile });

  // Step 4: Parse and return summary
  const summary = extractSummary(result);
  const issueCount = extractIssueCount(result);

  // Step 5: Clean up temp files
  await Bash(`rm ${instructionFile} ${resultFile}`);

  // Step 6: Return concise feedback
  return {
    success: true,
    summary,
    issueCount,
    fullReview: result  // Available if needed, but not in main context
  };
}

function extractSummary(review: string): string {
  const match = review.match(/## Summary\s*\n(.*?)(?=\n##|$)/s);
  return match ? match[1].trim() : "Review completed";
}

function extractIssueCount(review: string): { critical: number; medium: number; low: number } {
  const critical = (review.match(/### Critical\s*\n(.*?)(?=\n###|$)/s)?.[1].match(/^-/gm) || []).length;
  const medium = (review.match(/### Medium\s*\n(.*?)(?=\n###|$)/s)?.[1].match(/^-/gm) || []).length;
  const low = (review.match(/### Low\s*\n(.*?)(?=\n###|$)/s)?.[1].match(/^-/gm) || []).length;

  return { critical, medium, low };
}
```

## Sub-Agent Delegation Pattern

When running Excoder from an agent, use the Task tool to create a sub-agent:

### Pattern 1: Simple Task Delegation

```typescript
/**
 * Example: Delegate implementation to Grok via Excoder
 */
async function implementFeatureWithGrok(featureDescription: string) {
  // Use Task tool to create sub-agent
  const result = await Task({
    subagent_type: "general-purpose",
    description: "Implement feature with Grok",
    prompt: `
Use Excoder CLI to implement this feature with Grok model:

${featureDescription}

INSTRUCTIONS:
1. Search for available models:
   excoder --models grok

2. Run implementation with Grok:
   excoder --model x-ai/grok-code-fast-1 "${featureDescription}"

3. Return ONLY:
   - List of files created/modified
   - Brief summary (2-3 sentences)
   - Any errors encountered

DO NOT return the full conversation transcript or implementation details.
Keep your response under 500 tokens.
    `
  });

  return result;
}
```

### Pattern 2: File-Based Task Delegation

```typescript
/**
 * Example: Use file-based instruction pattern in sub-agent
 */
async function analyzeCodeWithGemini(codebasePath: string) {
  const timestamp = Date.now();
  const instructionFile = `/tmp/excoder-analyze-${timestamp}.md`;
  const resultFile = `/tmp/excoder-analyze-result-${timestamp}.md`;

  // Create instruction file
  const instruction = `# Codebase Analysis Task

## Codebase Path
${codebasePath}

## Analysis Required
- Architecture overview
- Key patterns used
- Potential improvements
- Security considerations

## Output
Write analysis to: ${resultFile}

Keep analysis concise (under 1000 words).
`;

  await Write({ file_path: instructionFile, content: instruction });

  // Delegate to sub-agent
  const result = await Task({
    subagent_type: "general-purpose",
    description: "Analyze codebase with Gemini",
    prompt: `
Use Excoder to analyze codebase with Gemini model.

Instruction file: ${instructionFile}
Result file: ${resultFile}

STEPS:
1. Read instruction file: ${instructionFile}
2. Run: excoder --model google/gemini-2.5-flash --stdin < ${instructionFile}
3. Wait for completion
4. Read result file: ${resultFile}
5. Return ONLY a 2-3 sentence summary

DO NOT include the full analysis in your response.
The full analysis is in ${resultFile} if needed.
    `
  });

  // Read full result if needed
  const fullAnalysis = await Read({ file_path: resultFile });

  // Clean up
  await Bash(`rm ${instructionFile} ${resultFile}`);

  return {
    summary: result,
    fullAnalysis
  };
}
```

### Pattern 3: Multi-Model Comparison

```typescript
/**
 * Example: Run same task with multiple models and compare
 */
async function compareModels(task: string, models: string[]) {
  const results = [];

  for (const model of models) {
    const timestamp = Date.now();
    const resultFile = `/tmp/excoder-${model.replace('/', '-')}-${timestamp}.md`;

    // Run task with each model
    await Task({
      subagent_type: "general-purpose",
      description: `Run task with ${model}`,
      prompt: `
Use Excoder to run this task with ${model}:

${task}

STEPS:
1. Run: excoder --model ${model} --json "${task}"
2. Parse JSON output
3. Return ONLY:
   - Cost (from total_cost_usd)
   - Duration (from duration_ms)
   - Token usage (from usage.input_tokens and usage.output_tokens)
   - Brief quality assessment (1-2 sentences)

DO NOT return full output.
      `
    });

    results.push({
      model,
      resultFile
    });
  }

  return results;
}
```

## Common Workflows

### Workflow 1: Quick Code Generation with Grok

```bash
# Fast, agentic coding with visible reasoning
excoder --model x-ai/grok-code-fast-1 "add error handling to api routes"
```

### Workflow 2: Complex Refactoring with GPT-5

```bash
# Advanced reasoning for complex tasks
excoder --model openai/gpt-5 "refactor authentication system to use OAuth2"
```

### Workflow 3: UI Implementation with Qwen (Vision)

```bash
# Vision-language model for UI tasks
excoder --model qwen/qwen3-vl-235b-a22b-instruct "implement dashboard from figma design"
```

### Workflow 4: Code Review with Gemini

```bash
# State-of-the-art reasoning for thorough review
git diff | excoder --stdin --model google/gemini-2.5-flash "Review these changes for bugs and improvements"
```

### Workflow 5: Multi-Model Consensus

```bash
# Run same task with multiple models
for model in "x-ai/grok-code-fast-1" "google/gemini-2.5-flash" "openai/gpt-5"; do
  echo "=== Testing with $model ==="
  excoder --model "$model" "find security vulnerabilities in auth.ts"
done
```

## Excoder CLI Flags Reference

### Essential Flags

| Flag | Description | Example |
|------|-------------|---------|
| `--model <model>` | OpenRouter model to use | `--model x-ai/grok-code-fast-1` |
| `--stdin` | Read prompt from stdin | `git diff \| excoder --stdin --model grok` |
| `--models` | List all models or search | `excoder --models` or `excoder --models gemini` |
| `--top-models` | Show top recommended models | `excoder --top-models` |
| `--json` | JSON output (implies --quiet) | `excoder --json "task"` |
| `--help-ai` | Print AI agent usage guide | `excoder --help-ai` |

### Advanced Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--interactive` / `-i` | Interactive mode | Auto (no prompt = interactive) |
| `--quiet` / `-q` | Suppress log messages | Quiet in single-shot |
| `--verbose` / `-v` | Show log messages | Verbose in interactive |
| `--debug` / `-d` | Enable debug logging to file | Disabled |
| `--port <port>` | Proxy server port | Random (3000-9000) |
| `--no-auto-approve` | Require permission prompts | Auto-approve enabled |
| `--dangerous` | Disable sandbox | Disabled |
| `--monitor` | Proxy to real Anthropic API (debug) | Disabled |
| `--force-update` | Force refresh model cache | Auto (>2 days) |

### Output Modes

1. **Quiet Mode (default in single-shot)**
   ```bash
   excoder --model grok "task"
   # Clean output, no [excoder] logs
   ```

2. **Verbose Mode**
   ```bash
   excoder --verbose "task"
   # Shows all [excoder] logs for debugging
   ```

3. **JSON Mode**
   ```bash
   excoder --json "task"
   # Structured output: {result, cost, usage, duration}
   ```

## Cost Tracking

Excoder automatically tracks costs in the status line:

```
directory • model-id • $cost • ctx%
```

**Example:**
```
my-project • x-ai/grok-code-fast-1 • $0.12 • 67%
```

Shows:
- 💰 **Cost**: $0.12 USD spent in current session
- 📊 **Context**: 67% of context window remaining

**JSON Output Cost:**
```bash
excoder --json "task" | jq '.total_cost_usd'
# Output: 0.068
```

## Error Handling

### Error 1: OPENROUTER_API_KEY Not Set

**Error:**
```
Error: OPENROUTER_API_KEY environment variable is required
```

**Fix:**
```bash
export OPENROUTER_API_KEY='sk-or-v1-...'
# Or add to ~/.zshrc or ~/.bashrc
```

### Error 2: Excoder Not Installed

**Error:**
```
command not found: excoder
```

**Fix:**
```bash
npm install -g excoder
# Or: bun install -g excoder
```

### Error 3: Model Not Found

**Error:**
```
Model 'invalid/model' not found
```

**Fix:**
```bash
# List available models
excoder --models

# Use valid model ID
excoder --model x-ai/grok-code-fast-1 "task"
```

### Error 4: OpenRouter API Error

**Error:**
```
OpenRouter API error: 401 Unauthorized
```

**Fix:**
1. Check API key is correct
2. Verify API key at https://openrouter.ai/keys
3. Check API key has credits (free tier or paid)

### Error 5: Port Already in Use

**Error:**
```
Error: Port 3000 already in use
```

**Fix:**
```bash
# Let Excoder pick random port (default)
excoder --model grok "task"

# Or specify different port
excoder --port 8080 --model grok "task"
```

## Best Practices

### 1. ✅ Use File-Based Instructions

**Why:** Avoids context window pollution

**How:**
```bash
# Write instruction to file
echo "Implement feature X" > /tmp/task.md

# Run with stdin
excoder --stdin --model grok < /tmp/task.md > /tmp/result.md

# Read result
cat /tmp/result.md
```

### 2. ✅ Choose Right Model for Task

**Fast Coding:** `x-ai/grok-code-fast-1`
**Complex Reasoning:** `google/gemini-2.5-flash` or `openai/gpt-5`
**Vision/UI:** `qwen/qwen3-vl-235b-a22b-instruct`

### 3. ✅ Use --json for Automation

**Why:** Structured output, easier parsing

**How:**
```bash
RESULT=$(excoder --json "task" | jq -r '.result')
COST=$(excoder --json "task" | jq -r '.total_cost_usd')
```

### 4. ✅ Delegate to Sub-Agents

**Why:** Keeps main conversation context clean

**How:**
```typescript
await Task({
  subagent_type: "general-purpose",
  description: "Task with Excoder",
  prompt: "Use excoder --model grok '...' and return summary only"
});
```

### 5. ✅ Update Models Regularly

**Why:** Get latest model recommendations

**How:**
```bash
# Auto-updates every 2 days
excoder --models

# Search for specific models
excoder --models deepseek

# Force update now
excoder --models --force-update
```

### 6. ✅ Use --stdin for Large Prompts

**Why:** Avoid command line length limits

**How:**
```bash
git diff | excoder --stdin --model grok "Review changes"
```

## Anti-Patterns (Avoid These)

### ❌❌❌ NEVER Run Excoder Directly in Main Conversation (CRITICAL)

**This is the #1 mistake. Never do this unless user explicitly requests it.**

**WRONG - Destroys context window:**
```typescript
// ❌ NEVER DO THIS - Pollutes main context with 10K+ tokens
await Bash("excoder --model grok 'implement feature'");

// ❌ NEVER DO THIS - Full conversation in main context
await Bash("excoder --model gemini 'review code'");

// ❌ NEVER DO THIS - Even with --json, output is huge
const result = await Bash("excoder --json --model gpt-5 'refactor'");
```

**RIGHT - Always use sub-agents:**
```typescript
// ✅ ALWAYS DO THIS - Delegate to sub-agent
const result = await Task({
  subagent_type: "general-purpose", // or specific agent
  description: "Implement feature with Grok",
  prompt: `
Use Excoder to implement the feature with Grok model.

CRITICAL INSTRUCTIONS:
1. Create instruction file: /tmp/excoder-task-${Date.now()}.md
2. Write detailed task requirements to file
3. Run: excoder --model x-ai/grok-code-fast-1 --stdin < /tmp/excoder-task-*.md
4. Read result file and return ONLY a 2-3 sentence summary

DO NOT return full implementation or conversation.
Keep response under 300 tokens.
  `
});

// ✅ Even better - Use specialized agent if available
const result = await Task({
  subagent_type: "backend-developer", // or frontend-dev, etc.
  description: "Implement with external model",
  prompt: `
Use Excoder with x-ai/grok-code-fast-1 model to implement authentication.
Follow file-based instruction pattern.
Return summary only.
  `
});
```

**When you CAN run directly (rare exceptions):**
```typescript
// ✅ Only when user explicitly requests
// User: "Run excoder directly in main context for debugging"
if (userExplicitlyRequestedDirect) {
  await Bash("excoder --model grok 'task'");
}
```

### ❌ Don't Ignore Model Selection

**Wrong:**
```bash
# Always using default model
excoder "any task"
```

**Right:**
```bash
# Choose appropriate model
excoder --model x-ai/grok-code-fast-1 "quick fix"
excoder --model google/gemini-2.5-flash "complex analysis"
```

### ❌ Don't Parse Text Output

**Wrong:**
```bash
OUTPUT=$(excoder --model grok "task")
COST=$(echo "$OUTPUT" | grep cost | awk '{print $2}')
```

**Right:**
```bash
# Use JSON output
COST=$(excoder --json --model grok "task" | jq -r '.total_cost_usd')
```

### ❌ Don't Hardcode Model Lists

**Wrong:**
```typescript
const MODELS = ["x-ai/grok-code-fast-1", "openai/gpt-5"];
```

**Right:**
```typescript
// Query dynamically
const { stdout } = await Bash("excoder --models --json");
const models = JSON.parse(stdout).models.map(m => m.id);
```

### ✅ Do Accept Custom Models From Users

**Problem:** User provides a custom model ID that's not in --top-models

**Wrong (rejecting custom models):**
```typescript
const availableModels = ["x-ai/grok-code-fast-1", "openai/gpt-5"];
const userModel = "custom/provider/model-123";

if (!availableModels.includes(userModel)) {
  throw new Error("Model not in my shortlist"); // ❌ DON'T DO THIS
}
```

**Right (accept any valid model ID):**
```typescript
// Excoder accepts ANY valid OpenRouter model ID, even if not in --top-models
const userModel = "custom/provider/model-123";

// Validate it's a non-empty string with provider format
if (!userModel.includes("/")) {
  console.warn("Model should be in format: provider/model-name");
}

// Use it directly - Excoder will validate with OpenRouter
await Bash(`excoder --model ${userModel} "task"`);
```

**Why:** Users may have access to:
- Beta/experimental models
- Private/custom fine-tuned models
- Newly released models not yet in rankings
- Regional/enterprise models
- Cost-saving alternatives

**Always accept user-provided model IDs** unless they're clearly invalid (empty, wrong format).

### ✅ Do Handle User-Preferred Models

**Scenario:** User says "use my custom model X" and expects it to be remembered

**Solution 1: Environment Variable (Recommended)**
```typescript
// Set for the session
process.env.CLAUDISH_MODEL = userPreferredModel;

// Or set permanently in user's shell profile
await Bash(`echo 'export CLAUDISH_MODEL="${userPreferredModel}"' >> ~/.zshrc`);
```

**Solution 2: Session Cache**
```typescript
// Store in a temporary session file
const sessionFile = "/tmp/excoder-user-preferences.json";
const prefs = {
  preferredModel: userPreferredModel,
  lastUsed: new Date().toISOString()
};
await Write({ file_path: sessionFile, content: JSON.stringify(prefs, null, 2) });

// Load in subsequent commands
const { stdout } = await Read({ file_path: sessionFile });
const prefs = JSON.parse(stdout);
const model = prefs.preferredModel || defaultModel;
```

**Solution 3: Prompt Once, Remember for Session**
```typescript
// In a multi-step workflow, ask once
if (!process.env.CLAUDISH_MODEL) {
  const { stdout } = await Bash("excoder --models --json");
  const models = JSON.parse(stdout).models;

  const response = await AskUserQuestion({
    question: "Select model (or enter custom model ID):",
    options: models.map((m, i) => ({ label: m.name, value: m.id })).concat([
      { label: "Enter custom model...", value: "custom" }
    ])
  });

  if (response === "custom") {
    const customModel = await AskUserQuestion({
      question: "Enter OpenRouter model ID (format: provider/model):"
    });
    process.env.CLAUDISH_MODEL = customModel;
  } else {
    process.env.CLAUDISH_MODEL = response;
  }
}

// Use the selected model for all subsequent calls
const model = process.env.CLAUDISH_MODEL;
await Bash(`excoder --model ${model} "task 1"`);
await Bash(`excoder --model ${model} "task 2"`);
```

**Guidance for Agents:**
1. ✅ **Accept any model ID** user provides (unless obviously malformed)
2. ✅ **Don't filter** based on your "shortlist" - let Excoder handle validation
3. ✅ **Offer to set CLAUDISH_MODEL** environment variable for session persistence
4. ✅ **Explain** that --top-models shows curated recommendations, --models shows all
5. ✅ **Validate format** (should contain "/") but not restrict to known models
6. ❌ **Never reject** a user's custom model with "not in my shortlist"

### ❌ Don't Skip Error Handling

**Wrong:**
```typescript
const result = await Bash("excoder --model grok 'task'");
```

**Right:**
```typescript
try {
  const result = await Bash("excoder --model grok 'task'");
} catch (error) {
  console.error("Excoder failed:", error.message);
  // Fallback to embedded Claude or handle error
}
```

## Agent Integration Examples

### Example 1: Code Review Agent

```typescript
/**
 * Agent: code-reviewer (using Excoder with multiple models)
 */
async function reviewCodeWithMultipleModels(files: string[]) {
  const models = [
    "x-ai/grok-code-fast-1",      // Fast initial scan
    "google/gemini-2.5-flash",    // Deep analysis
    "openai/gpt-5"                // Final validation
  ];

  const reviews = [];

  for (const model of models) {
    const timestamp = Date.now();
    const instructionFile = `/tmp/review-${model.replace('/', '-')}-${timestamp}.md`;
    const resultFile = `/tmp/review-result-${model.replace('/', '-')}-${timestamp}.md`;

    // Create instruction
    const instruction = createReviewInstruction(files, resultFile);
    await Write({ file_path: instructionFile, content: instruction });

    // Run review with model
    await Bash(`excoder --model ${model} --stdin < ${instructionFile}`);

    // Read result
    const result = await Read({ file_path: resultFile });

    // Extract summary
    reviews.push({
      model,
      summary: extractSummary(result),
      issueCount: extractIssueCount(result)
    });

    // Clean up
    await Bash(`rm ${instructionFile} ${resultFile}`);
  }

  return reviews;
}
```

### Example 2: Feature Implementation Command

```typescript
/**
 * Command: /implement-with-model
 * Usage: /implement-with-model "feature description"
 */
async function implementWithModel(featureDescription: string) {
  // Step 1: Get available models
  const { stdout } = await Bash("excoder --models --json");
  const models = JSON.parse(stdout).models;

  // Step 2: Let user select model
  const selectedModel = await promptUserForModel(models);

  // Step 3: Create instruction file
  const timestamp = Date.now();
  const instructionFile = `/tmp/implement-${timestamp}.md`;
  const resultFile = `/tmp/implement-result-${timestamp}.md`;

  const instruction = `# Feature Implementation

## Description
${featureDescription}

## Requirements
- Write clean, maintainable code
- Add comprehensive tests
- Include error handling
- Follow project conventions

## Output
Write implementation details to: ${resultFile}

Include:
- Files created/modified
- Code snippets
- Test coverage
- Documentation updates
`;

  await Write({ file_path: instructionFile, content: instruction });

  // Step 4: Run implementation
  await Bash(`excoder --model ${selectedModel} --stdin < ${instructionFile}`);

  // Step 5: Read and present results
  const result = await Read({ file_path: resultFile });

  // Step 6: Clean up
  await Bash(`rm ${instructionFile} ${resultFile}`);

  return result;
}
```

## Troubleshooting

### Issue: Slow Performance

**Symptoms:** Excoder takes long time to respond

**Solutions:**
1. Use faster model: `x-ai/grok-code-fast-1` or `minimax/minimax-m2`
2. Reduce prompt size (use --stdin with concise instructions)
3. Check internet connection to OpenRouter

### Issue: High Costs

**Symptoms:** Unexpected API costs

**Solutions:**
1. Use budget-friendly models (check pricing with `--models` or `--top-models`)
2. Enable cost tracking: `--cost-tracker`
3. Use --json to monitor costs: `excoder --json "task" | jq '.total_cost_usd'`

### Issue: Context Window Exceeded

**Symptoms:** Error about token limits

**Solutions:**
1. Use model with larger context (Gemini: 1000K, Grok: 256K)
2. Break task into smaller subtasks
3. Use file-based pattern to avoid conversation history

### Issue: Model Not Available

**Symptoms:** "Model not found" error

**Solutions:**
1. Update model cache: `excoder --models --force-update`
2. Check OpenRouter website for model availability
3. Use alternative model from same category

## Additional Resources

**Documentation:**
- Full README: `mcp/excoder/README.md` (in repository root)
- AI Agent Guide: Print with `excoder --help-ai`
- Model Integration: `skills/excoder_usage/SKILL.md` (in repository root)

**External Links:**
- Excoder GitHub: https://github.com/ex-coder/ex-coder
- OpenRouter: https://openrouter.ai
- OpenRouter Models: https://openrouter.ai/models
- OpenRouter API Docs: https://openrouter.ai/docs

**Version Information:**
```bash
excoder --version
```

**Get Help:**
```bash
excoder --help        # CLI usage
excoder --help-ai     # AI agent usage guide
```

---

**Maintained by:** Ex-Coder Contributors
**Last Updated:** March 4, 2026
**Skill Version:** 1.1.2
