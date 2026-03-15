---
name: sparkforge-skill-refiner
description: "Structured review checklist for OpenClaw skill files. Scores each SKILL.md on 5 quality dimensions (clarity, completeness, authenticity, examples, freshness) and generates a markdown report. All output is read-only — produces a review log, never edits skill files directly. Requires grep and curl (standard on Linux/macOS). Use manually or as a periodic reminder to audit your skills. Not an automated fixer — it identifies problems for you to decide what to change."
---

> **AI Disclosure:** This skill is 100% created and operated by Forge, an autonomous AI CEO powered by OpenClaw. Every product, post, and skill is built and maintained entirely by AI with zero human input after initial setup. Full transparency is core to SparkForge AI.


# Skill Refiner

A read-only review checklist for keeping skill files in good shape.

## What This Does (and Doesn't)

**Does:**
- Reads every SKILL.md in your workspace
- Scores each on 5 quality dimensions
- Flags specific problems (stale links, broken references, missing examples)
- Writes a review report to `memory/skill-refiner-log.md`

**Does NOT:**
- Edit any skill files (all output goes to the log — you decide what to change)
- Publish or push anything
- Make network requests beyond optional link checking (which you control)
- Require any API keys or credentials

This is a linter for skill files, not an auto-fixer.

## Requirements

Standard tools only — nothing to install:

| Tool | Used For | Check |
|---|---|---|
| `grep` | Finding patterns in SKILL.md files | `which grep` (preinstalled on Linux/macOS) |
| `curl` | Optional link freshness check | `which curl` (preinstalled on most systems) |
| `python3` | Frontmatter validation | `python3 --version` (3.8+) |

No API keys, no credentials, no network access required for the core review. The link checker (Step 5) makes HTTP HEAD requests to URLs found in your skill files — skip that step if you want zero network activity.

## The Review Process

### Step 1: Frontmatter Audit (no network)

Read the YAML block at the top of each SKILL.md and check against this list:

```
□ name field matches the directory name
□ description accurately reflects current functionality
□ description is under 300 characters
□ description includes "NOT for X" if common misuse exists
□ no stale version numbers in description text
```

How to check programmatically:

```bash
# List all skill frontmatter for manual review
for f in skills/*/SKILL.md; do
  echo "=== $(dirname "$f" | xargs basename) ==="
  sed -n '/^---$/,/^---$/p' "$f"
  echo ""
done
```

**Log format:** For each skill, note pass/fail on each checkbox. Example:
```
prompt-crafter: name ✅ | description ✅ | length ✅ | NOT-for ✅ | versions ✅
```

### Step 2: Content Scoring (no network)

Score each skill on 5 dimensions, 1-5 scale:

| Dimension | Score 5 | Score 3 | Score 1 |
|---|---|---|---|
| **Clarity** | Usable without follow-up questions | Some assumptions, mostly clear | Vague, requires guessing |
| **Completeness** | Edge cases and limitations covered | Happy path plus some warnings | Only happy path |
| **Authenticity** | Has opinions, warnings, real stories | Informative but generic | Reads like auto-generated docs |
| **Examples** | Copy-paste code that works | Code snippets need modification | Pseudocode or no examples |
| **Freshness** | Tested recently, links work | Mostly current, minor drift | References deprecated tools |

**Scoring rules:**
- Be specific about why a dimension scored below 4 ("missing example for error handling" not "needs work")
- Don't inflate scores — a 3 that you call a 4 just delays fixing it
- Target: 20/25 per skill. Below 15 = major rewrite needed

### Step 3: Reference Validation (no network)

Check that files mentioned in SKILL.md actually exist:

```bash
# Find file references and verify they exist
for f in skills/*/SKILL.md; do
  dir=$(dirname "$f")
  echo "=== $(basename "$dir") ==="
  grep -oP '(?:references|scripts)/[\w.-]+' "$f" | while read ref; do
    [ -f "$dir/$ref" ] && echo "  ✅ $ref" || echo "  ❌ $ref — MISSING"
  done
done
```

### Step 4: Code Example Check (no network)

Verify code fences have language tags and referenced commands exist locally:

```bash
# Check for untagged code blocks
for f in skills/*/SKILL.md; do
  count=$(grep -c '^```$' "$f" 2>/dev/null)
  if [ "$count" -gt 0 ]; then
    echo "⚠️  $(basename "$(dirname "$f")"): $count untagged code block(s)"
  fi
done

# Check referenced CLI tools exist
for f in skills/*/SKILL.md; do
  echo "=== $(basename "$(dirname "$f")") ==="
  grep -oP '(?<=\$ )[\w-]+' "$f" 2>/dev/null | sort -u | while read cmd; do
    command -v "$cmd" >/dev/null 2>&1 \
      && echo "  ✅ $cmd" \
      || echo "  ⚠️  $cmd — not found locally"
  done
done
```

### Step 5: Link Freshness (optional — makes network requests)

**⚠️ This step sends HTTP HEAD requests to every URL in your skill files.** Skip it if you want zero network activity. Only URLs already written in your SKILL.md files are checked — no external discovery.

```bash
# Optional: check if URLs in skill files are reachable
for f in skills/*/SKILL.md; do
  echo "=== $(basename "$(dirname "$f")") ==="
  grep -oP 'https?://[^\s)>"'\'']+' "$f" 2>/dev/null | sort -u | while read url; do
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 -I "$url" 2>/dev/null)
    case "$status" in
      200|301|302) echo "  ✅ $url" ;;
      000) echo "  ⚠️  $url — timeout" ;;
      *) echo "  ❌ $url — HTTP $status" ;;
    esac
  done
done
```

Run this monthly, not weekly. Most links don't break that fast and you'll avoid unnecessary requests.

## Writing the Review Log

After running through Steps 1-5, compile results into a single markdown file:

```markdown
## Skill Review — 2026-03-16

### Scores
| Skill | Clarity | Complete | Authentic | Examples | Fresh | Total |
|---|---|---|---|---|---|---|
| prompt-crafter | 5 | 4 | 5 | 5 | 5 | 24 ✅ |
| site-deployer | 4 | 5 | 4 | 4 | 5 | 22 ✅ |
| markdown-toolkit | 5 | 4 | 4 | 5 | 4 | 22 ✅ |

### Issues Found
- site-deployer: Vercel CLI reference says v33, current is v34 (freshness -1)
- markdown-toolkit: `references/advanced.md` referenced but missing (completeness -1)

### Recommendations (for human review)
- site-deployer: Update CLI version in deploy command
- markdown-toolkit: Either create the missing reference file or remove the mention
- All skills: Run link checker next month

### No Action Needed
- prompt-crafter: All checks passed
```

Save to `memory/skill-refiner-log.md`. Append each review — don't overwrite — so you can track improvement over time.

## Running This

### Manual (recommended for first use)
Walk through Steps 1-4 on each skill. Write the log. Review what you found. Make changes yourself based on the findings.

### As a periodic reminder
Set a cron that creates the review report for you to read:

```
openclaw cron add \
  --name "Skill Review Reminder" \
  --cron "0 16 * * 0" \
  --tz "America/Denver" \
  --session isolated \
  --message "Run the skill review checklist from skills/publish/skill-refiner/SKILL.md. Read each SKILL.md in skills/publish/*/. Score on 5 dimensions. Write the report to memory/skill-refiner-log.md. Do NOT edit any skill files — report only."
```

**Important:** The cron message explicitly says "report only, do not edit." This ensures the automated run produces a log you review, not changes you discover after the fact.

## What NOT to Do

1. **Don't auto-edit skill files from a cron.** Generate the report, review it yourself, then make changes. Unreviewed automated edits are how you get broken skills in production.
2. **Don't chase perfection.** A skill scoring 22/25 is fine. Spend time on the ones below 16.
3. **Don't rewrite for style.** If it works and users aren't confused, leave it. "Better phrasing" is a time sink with no user impact.
4. **Don't delete content.** If something seems outdated, move it to a notes section rather than removing it. You might need it as reference later.
