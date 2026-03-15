# Contributing to agent-mineru Skill

This skill wraps the agent-mineru CLI. Determine where the problem lies before reporting issues.

## Issue Reporting Guide

### Open an issue in this repository if

- The skill documentation is unclear or missing
- Examples in SKILL.md do not work
- You need help using the CLI with this skill wrapper
- The skill is missing a command or feature

### Open an issue at the agent-mineru CLI repository if

- The CLI crashes or throws errors
- Commands do not behave as documented
- You found a bug in document parsing or post-processing
- You need a new feature in the CLI

## Before Opening an Issue

1. Install the latest version
   ```bash
   npm install -g agent-mineru@latest
   ```

2. Verify your token is set
   ```bash
   echo $MINERU_TOKEN
   ```

3. Test the command in your terminal to isolate the issue

## Issue Report Template

```markdown
### Description
[Provide a clear and concise description of the bug]

### Reproduction Steps
1. [First Step]
2. [Second Step]
3. [Observe error]

### Expected Behavior
[Describe what you expected to happen]

### Environment Details
- **Skill Version:** [e.g. 1.0.0]
- **agent-mineru Version:** [output of agent-mineru --version]
- **Node.js Version:** [output of node -v]
- **Operating System:** [e.g. macOS, Ubuntu 22.04]

### Additional Context
- [Full error output or stack trace]
- [File type being parsed]
- [Model version used]
```

## Adding New Commands to the Skill

Update SKILL.md when the CLI adds new commands.
- Keep the Installation and Authentication sections
- Add new commands in the correct category
- Include usage examples
- Note any HTML vs PDF limitations
