---
name: openclaw-skill-creator
description: "Create, improve, or evaluate OpenClaw skills (SKILL.md). Use when: (1) designing a new skill from scratch, (2) improving an existing skill's description for better triggering accuracy, (3) evaluating whether a skill description would trigger correctly, (4) reviewing the skill library for quality issues. NOT for: creating Claude Code / Codex skills (those use a different format), editing skill scripts/assets unrelated to skill design."
---

# OpenClaw Skill Creator

A skill for creating and iteratively improving OpenClaw skills — inspired by Anthropic's skill-creator, adapted for the OpenClaw skill format.

## OpenClaw Skill Architecture

Skills are directories containing a `SKILL.md` file and optional resources.

**Custom skills** (user-created) are typically placed in the OpenClaw workspace:
```
<workspace>/skills/<skill-name>/
```

**Built-in skills** ship with the OpenClaw installation.

Custom skills in the workspace take precedence over built-ins of the same name.

### Minimal structure

```
<skill-name>/
├── SKILL.md          ← required
└── scripts/          ← optional, executable helpers
```

No packaging step needed. The directory is the skill.

### SKILL.md format

```yaml
---
name: skill-name
description: <trigger description — the most important field>
---

# Skill Name

Instructions for the agent...
```

Only `name` and `description` in frontmatter. No other fields.

Use `{baseDir}` in scripts/instructions to reference the skill's own directory:
```bash
python3 {baseDir}/scripts/my_script.py
```

---

## Writing Descriptions (Most Critical Part)

The `description` field is the **only** triggering mechanism. The body is never read unless the skill triggers first.

### Core principles

1. **Be pushy**: Agents tend to undertrigger skills. Make the description slightly aggressive — list specific contexts where this skill MUST be used.
2. **Use when + NOT for**: Explicit structure reduces both under-triggering and false positives.
3. **Include trigger phrases**: List common user phrasings. Include non-English phrases if the user communicates in other languages.
4. **Describe context, not just function**: "What the skill does AND when to use it."

### Template

```
<what the skill does>. Use when: (1) <context 1>, (2) <context 2>, (3) phrases like "<example phrase>". NOT for: <anti-patterns>.
```

### Example (before → after)

❌ Before: `"Track work time per project with start/stop timers."`

✅ After: `"Track work time and generate productivity reports. Use this skill whenever the user wants to start/stop a timer, log time to a project, or generate a time report — including phrases like 'start timer', 'log my time', 'how long did I work this week'. NOT for: calendar scheduling, task management."`

---

## Skill Creation Process

### 1. Capture Intent

Ask the user:
- What should this skill enable the agent to do?
- When should it trigger? What would the user say?
- What's the expected output?
- Does it need scripts, or is it purely instructional?

Ask one or two questions at a time; don't overwhelm.

### 2. Interview for Edge Cases

Before writing, ask about:
- Input formats, edge cases, failure modes
- Dependencies (external APIs, CLIs, files)
- What it should NOT do (important for the NOT for clause)

### 3. Write the SKILL.md

- Keep body under 300 lines — lean and focused
- Only include what the agent doesn't already know
- Move detailed reference material to `references/` files and link from SKILL.md
- Add scripts to `scripts/` when the same code would be rewritten repeatedly

### 4. Eval: Test the Description

Run a manual trigger eval:
1. Write 5–10 test prompts (mix of should-trigger and should-not-trigger)
2. For each, ask: "Would I read this skill's SKILL.md given only the description?"
3. If < 80% correct → improve the description

Use the eval script:
```bash
python3 {baseDir}/scripts/eval_description.py --skill path/to/SKILL.md --evals path/to/evals.json
```

See `scripts/eval_description.py` for the evals JSON format.

### 5. Iterate

After the skill is used on real tasks:
- If the skill often doesn't trigger when it should → description too narrow, add more trigger phrases
- If the skill triggers on unrelated requests → description too broad, add NOT for clause
- If the body is too long → split into `references/` files

---

## Improving Existing Skills

When asked to improve an existing skill:

1. Read the current `SKILL.md`
2. Check description against the principles above
3. Propose a new description with reasoning
4. Optionally run eval to compare before/after trigger accuracy
5. Update only after user confirmation

---

## Skill Quality Checklist

Before finalising a skill, verify:

- [ ] `name` is lowercase kebab-case, under 64 characters
- [ ] `description` includes "Use when" with specific trigger contexts
- [ ] `description` includes "NOT for" to prevent false positives
- [ ] Body is under 300 lines
- [ ] No README, CHANGELOG, or auxiliary docs (keep the skill lean)
- [ ] Scripts are tested and working
- [ ] References files are linked from SKILL.md with guidance on when to read them
