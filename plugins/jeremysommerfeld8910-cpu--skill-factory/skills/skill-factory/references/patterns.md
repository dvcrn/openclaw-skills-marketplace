# OpenClaw Skill Patterns

_Scanned 64 skills._

## Skills Inventory

| Skill | Tools | Examples | Error Handling |
|-------|-------|----------|----------------|
| 1password | openclaw, tmux | 1 | — |
| Crypto & Stock Market Data (Node.js) | node, npm, openclaw | 7 | — |
| Webhook | — | 0 | retry, timeout |
| apple-notes | openclaw | 0 | — |
| apple-reminders | openclaw | 0 | — |
| automation-workflows | — | 0 | — |
| bear-notes | openclaw | 5 | timeout |
| blogwatcher | openclaw | 0 | — |
| blucli | openclaw | 0 | — |
| bluebubbles | openclaw | 0 | — |
| camsnap | openclaw | 0 | — |
| canvas | curl, jq, node, openclaw | 4 | — |
| clawhub | node, npm, openclaw | 7 | — |
| coding-agent | gh, git, npm, openclaw | 11 | timeout |
| cron-mastery | openclaw | 0 | timeout |
| crypto-trading-bot | node, python | 0 | — |
| day-trading-investor-pro | — | 0 | — |
| discord | openclaw | 0 | — |
| eightctl | openclaw | 0 | — |
| elite-longterm-memory | git, npm, openclaw, python3 | 11 | — |
| fast-browser-use | fast-browser-use, node | 8 | — |
| food-order | openclaw | 0 | — |
| gemini | openclaw | 0 | — |
| gifgrep | jq, openclaw | 0 | — |
| github | gh, git, jq, openclaw | 6 | — |
| gog | gog, openclaw | 2 | — |
| goplaces | openclaw | 0 | — |
| healthcheck | npm, openclaw | 0 | — |
| himalaya | openclaw | 26 | — |
| imsg | openclaw | 4 | — |
| mcporter | node, openclaw | 0 | — |
| model-usage | openclaw, python | 2 | — |
| nano-banana-pro | openclaw | 3 | — |
| nano-pdf | openclaw | 1 | retry |
| notion | curl, openclaw | 10 | — |
| obsidian | openclaw | 0 | — |
| openai-image-gen | openclaw, python, python3 | 2 | — |
| openai-whisper | openclaw | 0 | — |
| openai-whisper-api | curl, openclaw | 2 | — |
| openhue | openclaw | 0 | — |
| oracle | git, node, npx, openclaw | 0 | fallback, timeout |
| ordercli | openclaw | 0 | — |
| peekaboo | openclaw, screen | 9 | retry, timeout |
| realtime-crypto-price-api | npm, npx | 2 | — |
| reddit | docker, python3 | 4 | — |
| sag | openclaw | 1 | — |
| session-logs | jq, openclaw | 10 | — |
| sherpa-onnx-tts | node, openclaw | 2 | — |
| skill-creator | docker, fast-browser-use, node, openclaw | 3 | retry, circuit breaker |
| skill-creator | gh, python | 4 | — |
| slack | openclaw | 0 | — |
| songsee | openclaw | 0 | — |
| sonoscli | openclaw | 0 | — |
| spotify-player | openclaw | 0 | fallback |
| startclaw-optimizer | npm, openclaw, python3 | 2 | retry, circuit breaker |
| strategic-research-engine | — | 0 | — |
| summarize | openclaw | 2 | fallback |
| things-mac | openclaw | 0 | — |
| tmux | git, openclaw, python, python3 | 4 | timeout |
| trello | curl, jq, openclaw | 9 | — |
| video-frames | openclaw | 2 | — |
| voice-call | openclaw | 1 | fallback |
| wacli | openclaw | 0 | — |
| weather | curl, openclaw | 4 | fallback |

## Tool Usage Patterns

**openclaw** — used in: elite-longterm-memory, startclaw-optimizer, Crypto & Stock Market Data (Node.js), cron-mastery, skill-creator, github, ordercli, oracle, camsnap, songsee, tmux, food-order, obsidian, 1password, bear-notes, nano-pdf, goplaces, session-logs, sag, openai-whisper-api, nano-banana-pro, slack, video-frames, sonoscli, blogwatcher, coding-agent, mcporter, himalaya, blucli, clawhub, model-usage, gemini, spotify-player, weather, apple-reminders, openhue, openai-whisper, eightctl, discord, voice-call, gifgrep, trello, peekaboo, bluebubbles, summarize, gog, openai-image-gen, imsg, apple-notes, healthcheck, canvas, notion, things-mac, sherpa-onnx-tts, wacli
**node** — used in: crypto-trading-bot, fast-browser-use, Crypto & Stock Market Data (Node.js), skill-creator, oracle, mcporter, clawhub, canvas, sherpa-onnx-tts
**npm** — used in: realtime-crypto-price-api, elite-longterm-memory, startclaw-optimizer, Crypto & Stock Market Data (Node.js), coding-agent, clawhub, healthcheck
**python** — used in: crypto-trading-bot, skill-creator, tmux, model-usage, openai-image-gen, skill-creator
**python3** — used in: reddit, elite-longterm-memory, startclaw-optimizer, skill-creator, tmux, openai-image-gen
**git** — used in: elite-longterm-memory, github, oracle, tmux, coding-agent
**jq** — used in: github, session-logs, gifgrep, trello, canvas
**curl** — used in: openai-whisper-api, weather, trello, canvas, notion
**gh** — used in: github, coding-agent, skill-creator
**npx** — used in: realtime-crypto-price-api, oracle
**docker** — used in: reddit, skill-creator
**fast-browser-use** — used in: fast-browser-use, skill-creator
**tmux** — used in: tmux, 1password
**screen** — used in: peekaboo, canvas
**gog** — used in: gog

## Output Formats

- `json` — 38 skills
- `log` — 29 skills
- `table` — 10 skills
- `markdown` — 8 skills
- `yaml` — 6 skills

## Error Handling Patterns

- **timeout** — 8 skills
- **fallback** — 6 skills
- **retry** — 5 skills
- **backoff** — 2 skills
- **circuit breaker** — 2 skills

## Trigger Phrase Vocabulary

Common description patterns from existing skills:

- [reddit] `Clawdbot needs to browse Reddit content - read posts from subreddits`
- [reddit] `Read and search Reddit posts via web scraping of old.reddit.com. Use when Clawdbot needs to browse R`
- [fast-browser-use] `you need speed`
- [fast-browser-use] `High-performance browser automation for heavy scraping, multi-tab management, and precise DOM extrac`
- [elite-longterm-memory] `author: NextFrontierBuilds keywords: [memory, ai-agent, ai-coding, long-term-memory, vector-search, `
- [elite-longterm-memory] `Ultimate AI agent memory system for Cursor, Claude, ChatGPT & Copilot. WAL protocol + vector search `
- [startclaw-optimizer] `Master optimization system. Routes Haiku vs Sonnet by task complexity, monitors context size, warns `
- [skill-creator] `building a new skill from scratch`
- [skill-creator] `create a skill`
- [skill-creator] `build a skill`
- [skill-creator] `make a skill`
- [skill-creator] `eval this skill`
- [skill-creator] `improve this skill`
- [skill-creator] `benchmark skill versions`
- [skill-creator] `analyze skill patterns`
- [skill-creator] `synthesize skill from patterns`
- [skill-creator] `package skill`
- [skill-creator] `publish skill`
- [skill-creator] `Create, evaluate, improve, benchmark, and publish OpenClaw skills. Use when building a new skill fro`
- [github] `metadata:   {`
- [github] `:       {`
- [github] `:           [             {`
- [github] `,             },             {`
- [github] `Interact with GitHub using the `gh` CLI. Use `gh issue`, `gh pr`, `gh run`, and `gh api` for issues,`
- [himalaya] `homepage: https://github.com/pimalaya/himalaya metadata:   {`
- [himalaya] `CLI to manage emails via IMAP/SMTP. Use `himalaya` to list, read, write, reply, forward, search, and`
- [discord] `metadata: {`
- [discord] `] } } } allowed-tools: [`
- [discord] `Discord ops via the message tool (channel=discord)." metadata: { "openclaw": { "emoji": "🎮", "requir`