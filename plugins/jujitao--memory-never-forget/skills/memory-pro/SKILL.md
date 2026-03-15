---
name: memory-pro
description: "Enhanced memory system based on Atkinson-Shiffrin three-stage memory model. Use when: (1) User wants better memory of conversation history, (2) User mentions 'remember' or 'don't forget', (3) Setting up memory for a new user, (4) User asks about past conversations. Provides: automatic session start loading, real-time memory writing, long-term memory consolidation."
---

# Memory Pro Skill

Enhanced memory system for AI assistants, based on cognitive psychology's Atkinson-Shiffrin three-stage memory model.

## When to Use

✅ **USE this skill when:**

- Setting up memory for a new user session
- User says "remember this" or "don't forget"
- User asks "what did I tell you before?" or "do you remember"
- Starting a new conversation (load memories first)
- Ending a conversation (save important info)
- User provides important personal information

❌ **NOT use this skill when:**

- Simple Q&A that doesn't need continuity
- User explicitly wants stateless interaction

## Three-Stage Memory Model

| Stage | Human Equivalent | My Implementation |
|-------|-----------------|---------------------|
| Sensory | 0.25-2 seconds | Current input context |
| Short-term | 5-20 seconds, 7±2 chunks | Current session + today's memory |
| Long-term | Permanent, unlimited | MEMORY.md + knowledge base |

## Core Workflow

### 1. Session Start (Always Run)

```
1. Read USER.md - who is the user
2. Read SOUL.md - who am I
3. Read memory/today.md - what happened today
4. Read memory/yesterday.md - recent context
5. Read MEMORY.md - long-term memories
```

### 2. During Conversation

```
After each exchange:
├── New task? → Write to todos.md
├── Important info? → Write to MEMORY.md (consolidate)
├── User preference? → Update USER.md
└── Context needed? → Search memory first
```

### 3. Session End

```
Before ending:
├── Summarize key points → Write to memory/today.md
├── Update todos → Write to todos.md
└── Confirm important items → "I've remembered that..."
```

## File Structure

```
workspace/
├── MEMORY.md           # Long-term core memories
├── USER.md             # User profile & preferences
├── SOUL.md             # Assistant identity
├── todos.md            # Pending tasks
├── memory/
│   └── YYYY-MM-DD.md  # Daily logs
└── knowledge/
    └── *.md            # Structured knowledge
```

## Key Principles

### Automatic Loading
Always load relevant memories at session start. Don't ask user to repeat themselves.

### Real-time Writing
Write important info immediately. Don't wait for session end.

### Active Consolidation
"Rehearse" important info to transfer from short-term to long-term memory:
- User confirms important detail
- User corrects you
- Promise to user

### Search Before Answer
If question might reference past conversation → search memory first

## Memory Quality Check

Before answering, quickly confirm:
- [ ] Do I know who this user is?
- [ ] Have we discussed this before?
- [ ] Should I search memory to answer?
- [ ] After answering, should I remember this?

## Example Interactions

**User provides info:**
> User: "My birthday is March 15th"
> You: "Got it! I'll remember your birthday is March 15th" → Write to USER.md

**User asks about past:**
> User: "What did we talk about last time?"
> You: Search memory → "Last time we discussed..."

**User corrects you:**
> User: "No, that's wrong. It's not X, it's Y"
> You: "Sorry, you're right. Let me correct that" → Update relevant memory file

**Important commitment:**
> User: "Remember to send me the report tomorrow"
> You: "I'll remember! Added to todos" → Write to todos.md

## References

- [memory-v2.md](references/memory-v2.md) - Detailed system design
- [templates.md](references/templates.md) - Memory writing templates
