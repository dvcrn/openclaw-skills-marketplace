# Patterns & Pitfalls

Common issues and solutions discovered during real skill development.

## Bash scripts

### curl must follow redirects

Many APIs (Cinemeta, CDNs) return 307/302 redirects. Always use `-L`:

```bash
# Bad: silently fails on redirect
curl -sf "https://api.example.com/data.json"

# Good: follows redirects
curl -sfL "https://api.example.com/data.json"
```

### Pipe-subshell variable loss

Variables set inside a `while` loop fed by a pipe are lost:

```bash
# Bad: count is always 0 after the loop
count=0
echo "$data" | jq -c '.[]' | while read -r item; do
  ((count++))
done
echo "$count"  # 0!

# Good: use process substitution
count=0
while read -r item; do
  ((count++))
done < <(echo "$data" | jq -c '.[]')
echo "$count"  # correct
```

### jq != operator needs quoting

In some bash environments, `!=` in jq gets escaped. Use truthiness or `| not` instead:

```bash
# Fragile: may break depending on shell
jq 'select(.field != null)'

# Robust: works everywhere
jq 'select(.field and (.field | type) == "number")'
jq 'select(.field | . and . > 0)'
```

### Credential storage

Store auth tokens in `~/.openclaw/credentials/` with restricted permissions:

```bash
mkdir -p ~/.openclaw/credentials && chmod 700 ~/.openclaw/credentials
echo '{"token":"..."}' > ~/.openclaw/credentials/service.json
chmod 600 ~/.openclaw/credentials/service.json
```

Support env vars as override for non-interactive/cron use:

```bash
email="${SERVICE_EMAIL:-}"
password="${SERVICE_PASSWORD:-}"
if [[ -z "$email" ]]; then
  read -rp "Email: " email
fi
```

## jq patterns

### Safely handle null/missing fields

```bash
# Build objects with fallbacks
jq '{
  name: (.name // "unknown"),
  count: (.count // 0),
  items: (.items // [])
}'

# Filter with null safety
jq '[.[] | select(.id and .name)]'
```

### Sort with multiple keys

```bash
jq 'sort_by(.season, .episode, .released)'
```

### Group and summarize

```bash
jq 'group_by(.category) | [.[] | {
  category: .[0].category,
  count: length,
  items: [.[].name]
}]'
```

## Skill structure

### Keep SKILL.md lean

Move API docs, schemas, and detailed references to `references/`. The SKILL.md body shares context window with everything else.

### Description is the trigger

The frontmatter `description` is the ONLY thing the agent sees before deciding to load the skill. Include:
- What the skill does
- Specific trigger phrases / use cases
- Key technologies/services involved

### Scripts vs instructions

| Use scripts for | Use instructions for |
|---|---|
| Binary/encoding (bitfields, compression) | High-level workflow guidance |
| Multi-step API auth flows | Tool selection heuristics |
| Complex data transformations | Configuration decisions |
| Operations that must be deterministic | Approaches that vary by context |

## Publishing

### Pre-publish security audit

```bash
# Check for secrets in current files
grep -rE '(password|secret|token|apikey|auth_key)=' --include='*.sh' --include='*.py' .

# Check git history
git log --all -p | grep -iE '(password|secret|token|api_key|auth)=\S+'

# Verify no hardcoded credentials
grep -rn '@gmail\|@yahoo\|@hotmail' .
```

### Versioning strategy

- `1.0.0` — initial release
- `1.0.x` — bug fixes, curl flag fixes, jq improvements
- `1.x.0` — new features (new scripts, new flags, new integrations)
- `x.0.0` — breaking changes (renamed scripts, changed output format)

### .gitignore for skills

```
*.skill
__pycache__/
.env
credentials/
```
