---
name: openclaw-memory-os
description: "OpenClaw Memory-OS - Digital immortality service and cognitive continuity infrastructure for personal memory management"
---

# OpenClaw Memory-OS

Digital immortality service and cognitive continuity infrastructure

AI-powered personal memory management system for capturing, storing, and intelligently retrieving your digital memories.

数字永生服务 | 认知延续基础设施

## Installation

### Step 1: Install via ClawHub (Recommended)

```bash
# Install the skill
clawhub install openclaw-memory-os
```

### Step 2: Install the npm package

```bash
# Global installation
npm install -g openclaw-memory-os

# Or from source
git clone https://github.com/ZhenRobotics/openclaw-memory-os.git
cd openclaw-memory-os
npm install
npm run build
npm link
```

### Step 3: Initialize Memory-OS

```bash
# Initialize
openclaw-memory-os init

# Configure
openclaw-memory-os config set owner.name "Your Name"
openclaw-memory-os config set owner.email "your@email.com"
```

### Step 4: Verify Installation

```bash
openclaw-memory-os status
```

---

## Usage

### When to Use This Skill

**AUTO-TRIGGER** when user's message contains:

- Keywords: `memory`, `remember`, `recall`, `记忆`, `回忆`, `记住`, `保存`
- Wants to save information: "remember this", "save this note", "记住这个"
- Wants to retrieve information: "what did I say about", "find my notes on", "我之前关于...说了什么"
- Wants to manage knowledge: "organize my notes", "build knowledge graph"
- Agent needs long-term memory capabilities

**TRIGGER EXAMPLES:**

- "Remember: I prefer using TypeScript for all projects" ← Save as memory
- "What did I say about AI last week?" ← Query memory
- "Find all my notes about machine learning" ← Search memory
- "Show me what I did on March 1st" ← Timeline query
- "Build a knowledge graph of my ideas" ← Graph operation

**DO NOT USE** when:
- Simple reminders or todos (use task management)
- Real-time collaboration (use chat tools)

---

## Core Features

Complete memory management system:

- 🎤 **Multi-source Collection** - Collect from chat, files, code, media
- 🧠 **Semantic Search** - AI-powered semantic understanding (planned)
- 📊 **Knowledge Graph** - Automatic relation discovery (planned)
- ⏰ **Timeline** - Complete temporal tracking
- 💬 **Cognitive Chat** - Talk with your digital self (planned)
- 🔒 **Privacy-First** - Local storage, full control
- 🔧 **Extensible** - Modular collectors and processors
- 🤖 **Agent-Ready** - Perfect for AI agent long-term memory

---

## Agent Usage Guide

### Important Notes

**CRITICAL**: This is a foundational system for digital memory. Use it for:
- Storing agent conversation history
- Building personal knowledge base
- Retrieving context from past interactions
- Maintaining long-term context

**Package Name**: When importing, use `openclaw-memory-os`:
```typescript
import { MemoryOS, MemoryType } from 'openclaw-memory-os';
```

**CLI Name**: When using CLI, use `openclaw-memory-os`:
```bash
openclaw-memory-os init
openclaw-memory-os collect --source ~/Documents
```

### Pattern 1: Save Memory

When user wants to remember something:

```typescript
import { MemoryOS, MemoryType } from 'openclaw-memory-os';

const memory = new MemoryOS({});
await memory.init();

// Save text memory
await memory.collect({
  type: MemoryType.TEXT,
  content: 'User prefers using TypeScript for all projects',
  metadata: {
    tags: ['preference', 'development'],
    context: 'project-setup-discussion',
  },
});

// Response
console.log('✓ Saved to memory');
```

### Pattern 2: Search Memory

When user wants to recall something:

```typescript
// Semantic search
const results = await memory.search({
  query: 'TypeScript preferences',
  semantic: true,
  limit: 5,
});

// Display results
for (const result of results) {
  console.log(`[${result.memory.type}] ${result.memory.content}`);
  console.log(`  Relevance: ${(result.score * 100).toFixed(1)}%`);
  console.log(`  Date: ${result.memory.metadata.timestamp}`);
}
```

### Pattern 3: Timeline Query

When user wants to see past activities:

```typescript
// Query timeline
const timeline = await memory.timeline({
  date: new Date('2024-03-01'),
  range: 'day',
});

// Display
console.log(`\nActivities on ${timeline.date.toDateString()}:`);
console.log(`Total: ${timeline.stats.total} memories`);

timeline.memories.forEach(mem => {
  console.log(`- [${mem.type}] ${mem.content.substring(0, 60)}...`);
});
```

### Pattern 4: Agent Long-term Memory

Integration with AI agents:

```typescript
// In your agent conversation loop
async function handleConversation(userMessage: string) {
  // 1. Store current message
  await memory.collect({
    type: MemoryType.CHAT,
    content: {
      role: 'user',
      message: userMessage,
      timestamp: new Date(),
    },
    metadata: {
      source: 'agent-chat',
      tags: ['conversation'],
    },
  });

  // 2. Retrieve relevant context
  const relevant = await memory.search({
    query: userMessage,
    semantic: true,
    limit: 5,
  });

  // 3. Use context in response
  const context = relevant
    .map(r => `[${r.memory.metadata.timestamp}] ${r.memory.content}`)
    .join('\n');

  // 4. Generate response with context
  const response = await generateResponse({
    current: userMessage,
    context: context,
  });

  // 5. Store agent response
  await memory.collect({
    type: MemoryType.CHAT,
    content: {
      role: 'assistant',
      message: response,
      timestamp: new Date(),
    },
    metadata: {
      source: 'agent-chat',
      tags: ['conversation', 'response'],
    },
  });

  return response;
}
```

---

## CLI Commands

### Basic Operations

```bash
# Initialize
openclaw-memory-os init

# Collect memories
openclaw-memory-os collect --source ~/Documents
openclaw-memory-os collect --chat chat-export.json

# Search
openclaw-memory-os search "AI and machine learning"
openclaw-memory-os search --semantic "人工智能应用"

# Timeline
openclaw-memory-os timeline --date 2024-03-01
openclaw-memory-os timeline --range "last 7 days"

# Status
openclaw-memory-os status
```

### Advanced Operations

```bash
# Graph operations (planned)
openclaw-memory-os graph explore --topic "AI"
openclaw-memory-os graph stats

# Maintenance
openclaw-memory-os rebuild
openclaw-memory-os optimize
openclaw-memory-os export ~/backup.json
```

---

## Use Cases

### 1. Personal Knowledge Base

```bash
# Import all notes
openclaw-memory-os collect --source ~/Documents/Notes

# Search for specific topics
openclaw-memory-os search --semantic "machine learning algorithms"

# View knowledge graph (planned)
openclaw-memory-os graph explore
```

### 2. Agent Long-term Memory

```typescript
// Agent with memory
import { MemoryOS, MemoryType } from 'openclaw-memory-os';

class MemoryAgent {
  private memory: MemoryOS;

  async initialize() {
    this.memory = new MemoryOS({});
    await this.memory.init();
  }

  async chat(userMessage: string) {
    // Store message
    await this.memory.collect({
      type: MemoryType.CHAT,
      content: userMessage,
    });

    // Retrieve context
    const context = await this.memory.search({
      query: userMessage,
      limit: 5,
    });

    // Use context in response...
  }
}
```

### 3. Developer Memory

```bash
# Collect code repos
openclaw-memory-os collect --code ~/projects

# Search code patterns
openclaw-memory-os search "authentication implementation"

# Timeline of changes
openclaw-memory-os timeline --type code --range "last month"
```

---

## Configuration

Memory-OS stores config in `~/.memory-os/config.json`:

```json
{
  "storage": {
    "path": "~/.memory-os/data",
    "backend": "local"
  },
  "embedding": {
    "provider": "openai",
    "apiKey": "${OPENAI_API_KEY}",
    "model": "text-embedding-3-small"
  },
  "collectors": {
    "auto": true,
    "sources": ["~/Documents", "~/Downloads"]
  },
  "privacy": {
    "encryption": false,
    "shareStats": false
  }
}
```

---

## Development

### Project Structure

```
openclaw-memory-os/
├── src/
│   ├── core/         # Core engine
│   ├── collectors/   # Data collectors
│   ├── storage/      # Storage layer
│   ├── query/        # Query engine
│   ├── agents/       # Agent system
│   └── cli/          # CLI tool
├── docs/             # Documentation
└── tests/            # Tests
```

### Adding Custom Collectors

```typescript
import { BaseCollector, MemoryType } from 'openclaw-memory-os';

export class CustomCollector extends BaseCollector {
  constructor() {
    super('custom', MemoryType.TEXT);
  }

  async collect(source: string): Promise<CollectResult> {
    // Implement collection logic
    const memories = [];
    // ... collect data
    return {
      collected: memories.length,
      failed: 0,
      memories,
    };
  }

  async validate(source: string): Promise<boolean> {
    // Validate source
    return true;
  }
}
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│         Memory-OS Core                   │
├─────────────────────────────────────────┤
│                                          │
│  Collectors → Processors → Storage       │
│      ↓            ↓           ↓          │
│  Multi-source  AI Process  Multi-layer  │
│                                          │
│  Query & Retrieval Engine                │
│      ↓                                   │
│  Cognitive Interface                     │
│                                          │
└─────────────────────────────────────────┘
```

See [ARCHITECTURE.md](https://github.com/ZhenRobotics/openclaw-memory-os/blob/main/ARCHITECTURE.md) for details.

---

## Skill Capabilities

This skill enables:

- ✅ Long-term memory for AI agents
- ✅ Personal knowledge management
- ✅ Semantic search across all memories (planned)
- ✅ Temporal memory tracking
- ✅ Knowledge graph construction (planned)
- ✅ Privacy-preserving local storage
- ✅ Extensible collector system
- ✅ Multi-modal memory support (planned)

---

## Documentation

- [README](https://github.com/ZhenRobotics/openclaw-memory-os#readme) - Complete guide
- [Architecture](https://github.com/ZhenRobotics/openclaw-memory-os/blob/main/ARCHITECTURE.md) - System design
- [Quickstart](https://github.com/ZhenRobotics/openclaw-memory-os/blob/main/QUICKSTART.md) - 5-minute guide

---

## Links

- **ClawHub**: https://clawhub.ai/ZhenStaff/openclaw-memory-os
- **npm**: https://www.npmjs.com/package/openclaw-memory-os
- **GitHub**: https://github.com/ZhenRobotics/openclaw-memory-os
- **Issues**: https://github.com/ZhenRobotics/openclaw-memory-os/issues

---

## Contributing

OpenClaw Memory-OS is open source. Contributions welcome!

---

## License

MIT License

---

**Memory-OS - Digital Immortality Through Memory**

Version: 0.1.0
Skill Name: openclaw-memory-os
Package Name: openclaw-memory-os
