---
name: skill-priority-setup
description: "Scans installed skills, suggests L0-L3 priority tiers, and auto-configures skill injection policy. Use when: setting up skill priorities, optimizing token budget, or migrating to tiered skill architecture."
---

# Skill Priority Setup

Automated skill tiering and injection policy configuration for OpenClaw.

## What This Skill Does

1. **Discovery Phase**: Scans all installed skills across standard directories
2. **Analysis Phase**: Suggests L0-L3 tier assignments based on skill characteristics
3. **Configuration Phase**: Applies the tiered architecture to your setup
4. **Validation Phase**: Verifies configuration and estimates token savings

## Quick Start

```bash
# Run the interactive setup wizard
python3 ~/.openclaw/workspace/skills/skill-priority-setup/scripts/setup.py

# Or non-interactive mode with defaults
python3 ~/.openclaw/workspace/skills/skill-priority-setup/scripts/setup.py --auto
```

## When to Use

- **New Setup**: Just installed multiple skills and want optimal configuration
- **Performance Issues**: High token usage or slow responses
- **Migration**: Upgrading from flat skill structure to tiered architecture
- **Audit**: Reviewing and optimizing existing skill priorities

## Architecture Overview

This skill implements a 4-tier priority system:

### L0 - ROM Core (Always Active)
- `semantic-system`: Semantic routing (message injector)
- `agent-evolution`: Self-improvement behaviors (SOUL.md)
- `config-modification`: Config safety (on-demand)
- `skill-safe-install`: Installation safety (on-demand)

### L1 - Routing Layer (Task-Triggered)
- `browser-automation`: Web automation
- `find-skills`: Skill discovery
- `teamtask`: Multi-agent coordination

### L2 - Domain Skills (Keyword-Triggered)
- Document: `word-docx`, `tesseract-ocr`
- Media: `youtube-transcript`
- Platform: `discord`, `wechat-suite`, `evomap`
- Automation: `automation-workflows`

### L3 - Extensions (Manual/On-Demand)
- Third-party integrations: `notion`, `slack`, `github`, etc.

## Workflow

```
┌─────────────────┐
│ 1. Scan Skills  │ → Find all SKILL.md files
└────────┬────────┘
         ▼
┌─────────────────┐
│ 2. Analyze      │ → Detect skill types & dependencies
└────────┬────────┘
         ▼
┌─────────────────┐
│ 3. Suggest Tiers│ → Propose L0-L3 assignments
└────────┬────────┘
         ▼
┌─────────────────┐
│ 4. User Review  │ → Confirm or modify suggestions
└────────┬────────┘
         ▼
┌─────────────────┐
│ 5. Apply Config │ → Update AGENTS.md, SOUL.md, etc.
└────────┬────────┘
         ▼
┌─────────────────┐
│ 6. Validate     │ → Check JSON, test injection
└─────────────────┘
```

## Token Budget

- **L0 Core**: ≤300 tokens/round (minimal rules)
- **L1 Triggered**: ≤400 tokens per injection
- **Total Budget**: ≤900 tokens/round
- **Overflow Strategy**: Inject summary + file path only

## Safety Features

- Backup before any configuration changes
- JSON validation before applying
- Dry-run mode (`--dry-run`)
- Rollback capability

## Files Created

- `SKILL_PRIORITY_POLICY.md`: Your custom policy document
- `AGENTS.md` updates: Core constraints added
- `SOUL.md` updates: Agent evolution behaviors
- Backup files: `.backup/*.timestamp`

## Configuration

Edit `~/.openclaw/workspace/skills/skill-priority-setup/config.yaml` to customize:

```yaml
# Default tier assignments (override per skill)
default_tiers:
  semantic-router: L0
  browser: L1
  word-docx: L2
  
# Token budgets
token_budget:
  l0_max: 300
  l1_max: 400
  total_max: 900
  
# Safety settings
backup_before_change: true
validate_json: true
auto_rollback: true
```

## Troubleshooting

### Gateway Won't Start
- Check if message injector content exceeds limit
- Run with `--diagnose` flag

### Skills Not Loading
- Verify allowBundled list in openclaw.json
- Check file permissions

### High Token Usage
- Review L0 assignments (should be minimal)
- Consider moving skills to lower tiers

## References

- Original Implementation: [SKILL_PRIORITY_POLICY.md](../SKILL_PRIORITY_POLICY.md)
- OpenClaw Docs: https://docs.openclaw.ai/skills
