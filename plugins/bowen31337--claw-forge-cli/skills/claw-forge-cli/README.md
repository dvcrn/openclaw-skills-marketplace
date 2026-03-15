# claw-forge-cli — OpenClaw Agent Skill

[![ClawHub](https://img.shields.io/badge/clawhub-claw--forge--cli-blue)](https://clawhub.com/skills/claw-forge-cli)

An OpenClaw agent skill that teaches AI agents how to use the [claw-forge](https://github.com/clawinfra/claw-forge) CLI — the autonomous coding agent harness.

## Install

```bash
clawhub install claw-forge-cli
```

## What this skill does

Once installed in OpenClaw, your agent knows how to:

- **Bootstrap** a project with `claw-forge init`
- **Plan** a feature DAG from a spec with `claw-forge plan`
- **Run agents** in parallel with `claw-forge run`
- **Monitor progress** with `claw-forge status` and `claw-forge ui`
- **Add features** to existing projects (brownfield)
- **Fix bugs** with the reproduce-first `claw-forge fix` protocol
- **Choose the right edit mode**: `str_replace` vs `hashline`

## Quick reference

```bash
# Full greenfield workflow
claw-forge init
claw-forge plan app_spec.txt
claw-forge run --concurrency 5
claw-forge status

# Weaker/cheaper models — use hashline edit mode
# (benchmark: 6.7% → 68.3% success rate)
claw-forge run --edit-mode hashline --model claude-haiku-4-5
```

## Contents

| File | Description |
|------|-------------|
| `SKILL.md` | OpenClaw skill definition — all CLI commands, flags, workflows, config |
| `README.md` | This file |

## Related

- [claw-forge repo](https://github.com/clawinfra/claw-forge)
- [PyPI](https://pypi.org/project/claw-forge/)
- [ClawHub skill page](https://clawhub.com/skills/claw-forge-cli)
- [Agent skill docs](https://github.com/clawinfra/claw-forge/blob/main/docs/agent-skill.md)

## License

MIT
