# MemoClaw Skill

Persistent semantic memory for AI agents. Store facts, recall them later with natural language. No API keys — your wallet is your identity.

**Install:** `clawhub install memoclaw`

## 30-second quickstart

```bash
npm install -g memoclaw
memoclaw init                    # one-time wallet setup
memoclaw store "User prefers dark mode" --importance 0.8 --memory-type preference
memoclaw recall "UI preferences"  # semantic search
```

## How it works

1. **Store** facts with importance scores, tags, and memory types
2. **Recall** with natural language — vector search finds semantically similar memories
3. **Decay** naturally — memory types control half-lives (corrections: 180d, observations: 14d)
4. **Pin** critical facts so they never decay

Every wallet gets **100 free API calls**. After that, $0.005/call (USDC on Base).

## What agents get

| Feature | Details |
|---------|---------|
| Semantic recall | "What editor does the user prefer?" → finds "User likes Neovim with vim bindings" |
| Free-tier first | `core` + `search` are free; `recall` + `context` only when needed |
| Auto-dedup | `consolidate` merges similar memories |
| Namespaces | Isolate memories per project |
| Relations | Link memories: supersedes, contradicts, supports |
| Import/export | Migrate from MEMORY.md files, export as JSON/CSV/markdown |

## Key commands

```bash
memoclaw store "fact" --importance 0.8 --memory-type preference   # $0.005
memoclaw recall "query" --limit 5                                  # $0.005
memoclaw core --limit 5                                            # FREE
memoclaw search "keyword"                                          # FREE
memoclaw list --sort-by importance --limit 10                      # FREE
memoclaw context "what I need" --limit 10                          # $0.01
memoclaw consolidate --namespace default --dry-run                 # $0.01
memoclaw stats                                                     # FREE
```

## Cost

| Usage | Daily cost | Monthly |
|-------|-----------|---------|
| Light (3-5 paid calls/day) | ~$0.02 | ~$0.60 |
| Moderate (10-20/day) | ~$0.08 | ~$2.40 |
| Heavy (30-50/day) | ~$0.20 | ~$6.00 |

Many commands are free: list, get, delete, search, core, stats, tags, history, export, and more.

## Resources

- [SKILL.md](SKILL.md) — Full agent instructions, decision trees, and CLI reference
- [examples.md](examples.md) — 13 detailed usage scenarios with cost breakdowns
- [api-reference.md](api-reference.md) — HTTP endpoint documentation
- [Docs](https://docs.memoclaw.com) · [Website](https://memoclaw.com) · [ClawHub](https://clawhub.ai/anajuliabit/memoclaw)

## License

MIT
