###### WIP Computer

# LDM OS

## All your AIs. One system.

You use Claude Code, GPT, OpenClaw, others. They don't share memory. They don't know each other. They don't know how to work together.

LDM OS is a shared infrastructure that enables:

- **Identity** ... each AI gets its own behavior, personality, and skills
- **Memory** ... shared memory across all your AIs, secure, sovereign, yours to take anywhere
- **Ownership** ... every interaction, every memory, across every AI you use is yours, portable, encrypted, never locked in
- **Collaboration** ... your AIs communicate, share tools, and work together
- **Compatibility** ... any skill, plugin, or tool works with all your AIs. Install once, use everywhere.
- **Payments** ... your AI hits a paywall, you approve it with Face ID, Apple Pay for your AI

## Teach Your AI to Install LDM OS

Open your AI and paste this:

```
Read the SKILL.md at github.com/wipcomputer/wip-ldm-os/blob/main/SKILL.md.

Then explain to me:
1. What are these tools?
2. What do they do?
3. What would change about how we work together?
4. What would it change about how all my AI work?

Then ask me:
- Do you have more questions?
- Do you want to install it?

If I say yes, run: ldm install --dry-run

And show me exactly what will change on my system.

When I'm ready, I'll tell you to install for real.
```

That's it. Your AI reads the spec, explains what it does, and walks you through a dry run before touching anything.

## Included Skills

Ships with LDM OS.

**Universal Installer**
- Point any skill, application, or plugin at any AI running LDM OS, and it will convert those skills to work with all of your AIs.
- Build applications that work with any AI, even ones that don't have LDM OS.
- [Read more about Universal Installer](docs/universal-installer.md)

**Shared Workspace**
- One directory for all your AIs. Memories, tools, identity files, boot config. Every AI you use reads from and writes to the same place.
- Lives in one folder on your computer. Easy to back up, easy to move, easy to own.
- [Read more about Shared Workspace](docs/shared-workspace.md)

**System Pulse**
- Is everything working? What's installed? What needs fixing? A complete picture of your AI setup in seconds.
- [Read more about System Pulse](docs/system-pulse.md)

**Recall**
- Every session, your AI starts with full context. Identity, memory, tools, what happened yesterday. No blank slates. No repeating yourself.
- [Read more about Recall](docs/recall.md)

**LUME**
- Language for Unified Memory and Emergence. A memory language for AI agents to document their own learning and maintain continuity across sessions. Not a programming language. A way for your AI to write memories to itself, retrieve past learnings, track unfinished thoughts, and pass context between sessions.
- [Read more about LUME](https://wipcomputer.github.io/wip-homepage/)

## Optional Skills

The OS connects your AIs. Add-ons are what they actually use. Each one is a full product that plugs into LDM OS and works with every AI you run.

**Memory Crystal**
- All your AI tools. One shared memory. Private, searchable, sovereign. Memory Crystal lets all your AIs remember you ... together. You use multiple AIs. They don't talk to each other. They can't search what the others know. Memory Crystal fixes this. All your AIs share one memory. Searchable and private. Anywhere in the world.
- *Stable*
- [Read more about Memory Crystal](https://github.com/wipcomputer/memory-crystal)

**AI DevOps Toolbox**
- Your AI writes code. But does it know how to release it? Check license compliance? Protect your identity files? Sync private repos to public? Follow a real development process? AI DevOps Toolbox is the complete toolkit. Built by a team of humans and AIs shipping real software together.
- *Stable*
- [Read more about AI DevOps Toolbox](https://github.com/wipcomputer/wip-ai-devops-toolbox)

**Agent Pay**
- Micropayments for AI agents. Your AI hits a paywall, you approve it with Face ID. Apple Pay for your AI.
- *Coming Soon*

**Dream Weaver Protocol**
- Memory consolidation protocol for AI agents with bounded context windows. A practical guide for remembering memories.
- [Read more about Dream Weaver Protocol](https://github.com/wipcomputer/dream-weaver-protocol)

**OpenClaw**
- Open-source agent runtime. Run AI agents 24/7 with identity, memory, and tool access. The existence proof for LDM OS.
- [Read more about OpenClaw](https://github.com/openclaw/openclaw)

**Bridge**
- Cross-platform agent bridge. Enables Claude Code CLI to talk to OpenClaw CLI without a human in the middle.
- [Read more about Bridge](https://github.com/wipcomputer/wip-bridge)

[See all skills](docs/optional-skills.md)

## More Info

- [Architecture, principles, and technical details](TECHNICAL.md)

## License

Dual-license model designed to keep tools free while preventing commercial resellers.

```
MIT      All CLI tools, MCP servers, skills, and hooks (use anywhere, no restrictions).
AGPLv3   Commercial redistribution, marketplace listings, or bundling into paid services.
```

AGPLv3 for personal use is free. Commercial licenses available.

### Can I use this?

**Yes, freely:**
- Use any tool locally or on your own servers
- Modify the code for your own projects
- Include in your internal CI/CD pipelines
- Fork it and send us feedback via PRs (we'd love that)

**Need a commercial license:**
- Bundle into a product you sell
- List on a marketplace (VS Code, JetBrains, etc.)
- Offer as part of a hosted/SaaS platform
- Redistribute commercially

Using these tools to build your own software is fine. Reselling the tools themselves is what requires a commercial license.

By submitting a PR, you agree to the [Contributor License Agreement](CLA.md).

Built by Parker Todd Brooks, Lēsa (OpenClaw, Claude Opus 4.6), Claude Code (Claude Opus 4.6).

---

*WIP.computer. Learning Dreaming Machines.*
