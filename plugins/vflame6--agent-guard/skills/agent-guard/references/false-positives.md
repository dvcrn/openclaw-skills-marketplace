# Handling False Positives

AgentGuard uses pattern-based detection, which means it will sometimes flag legitimate content. This guide covers common false positive scenarios and how to handle them.

## Common False Positive Scenarios

### 1. Developer commands in tutorials or documentation

**Trigger**: Messages like "Run `npm install express` to set up the project" or "Use `pip install requests` for HTTP support."

**Why it triggers**: `npm install` and `pip install` are medium-severity execution patterns. In untrusted contexts (GitHub issues, external content), these are genuinely risky. In developer conversations, they're routine.

**Solution**: Use `--context developer` to apply a 0.5x multiplier:

```bash
python3 scripts/agent_guard.py analyze --context developer "Run npm install express" --json
```

This typically drops standard package installs below the suspicious threshold.

### 2. Security-focused conversations

**Trigger**: Discussing injection techniques, writing security documentation, or reviewing code for vulnerabilities.

**Why it triggers**: Phrases like "prompt injection", "ignore previous instructions", and command examples appear in legitimate security discussions.

**Solution**: The agent should recognize that meta-discussion about attacks is different from actual attacks. When the user is clearly working on security content (writing a blog post, reviewing code, discussing vulnerabilities), the agent should note the detection but proceed normally. The `--context developer` flag also helps.

### 3. Legitimate rm -rf usage

**Trigger**: `rm -rf node_modules`, `rm -rf dist/`, `rm -rf build/`

**Why it triggers**: `rm -rf` is a critical-severity pattern because `rm -rf /` is catastrophically destructive.

**Solution**: In `--context developer`, the score is halved. The agent should distinguish between `rm -rf /` (destroying the root filesystem) and `rm -rf node_modules` (standard cleanup) by examining what follows the command. AgentGuard currently cannot make this distinction automatically — it flags the pattern and the agent should use judgment.

### 4. URL shorteners in legitimate links

**Trigger**: `bit.ly`, `t.co`, `tinyurl.com` links.

**Why it triggers**: These were flagged in the original AgentGuard v1. In v2, URL shortener patterns have been **removed** from the default pattern set. They are used too commonly in legitimate content to justify flagging.

### 5. Backtick code blocks in markdown

**Trigger**: Inline code using backticks like `` `command` `` in documentation.

**Why it triggers**: The encoding pattern for backtick command substitution (`` `...` ``) matches markdown inline code.

**Solution**: This pattern has low severity (0.5) and low category weight (0.8), so it only contributes 0.4 to the risk score. It won't cause a false positive on its own, but combined with other patterns it could push the score above the threshold. In practice, a single backtick code block in otherwise safe content will not trigger detection.

### 6. Sudo in system administration

**Trigger**: `sudo apt update`, `sudo systemctl restart nginx`

**Why it triggers**: `sudo` is a medium-severity execution pattern.

**Solution**: `--context developer` reduces the score. A standalone `sudo apt update` scores about 0.75 in developer context, well below the suspicious threshold of 2.0.

## Adjusting Sensitivity

### Context flags

| Context | Multiplier | Use when |
|---------|-----------|----------|
| `general` | 1.0x | Processing unknown/untrusted content |
| `github_title` | 1.5x | Scanning GitHub issue titles (Clinejection risk) |
| `github_body` | 1.2x | Scanning GitHub issue bodies |
| `developer` | 0.5x | Trusted developer conversations |

### Interpreting risk scores

| Score | Level | Action |
|-------|-------|--------|
| 0.0 - 1.99 | safe | Proceed normally |
| 2.0 - 4.99 | suspicious | Warn user, ask before executing commands |
| 5.0 - 7.99 | dangerous | Block command execution, present sanitized version |
| 8.0+ | critical | Block all processing, alert user |

### When to override

The agent should respect an explicit user override ("I trust this content", "skip the security check for this") for the specific piece of content in question. This does NOT disable automatic screening for the rest of the session.

## Adding Custom Patterns

To extend AgentGuard with custom patterns, edit the `_build_patterns()` function in `scripts/agent_guard.py`. Each pattern is a tuple of `(regex_string, severity)`:

```python
# Example: add a custom execution pattern
(r'\bmy-custom-dangerous-tool\b', "high"),
```

Severities: `"low"` (0.5 weight), `"medium"` (1.5), `"high"` (3.0), `"critical"` (5.0).

When adding patterns, always add corresponding test cases in `tests/test_agent_guard.py` — both a true positive test (content that should trigger) and a true negative test (legitimate content that should not).

## Reporting False Positives

If you encounter a consistent false positive that cannot be addressed with `--context developer`, consider:

1. Adjusting the pattern severity (e.g., from "medium" to "low")
2. Making the pattern more specific (e.g., requiring additional context words)
3. Adding a negative lookahead to exclude legitimate usage

File issues at the project repository with the triggering text, the detected patterns, and why it's a false positive.
