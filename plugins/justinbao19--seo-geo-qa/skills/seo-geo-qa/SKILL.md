---
name: seo-geo-qa
description: "Check blog posts and articles before publishing. Finds broken links, weak sources, missing SEO elements, and citation problems. Use when: reviewing a draft, auditing content quality, checking if links still work, verifying sources are credible, running pre-publish QA, or doing post-publish page checks. Also triggers on: 'check this article', 'verify my links', 'review before publishing', 'content audit', 'source quality check', 'are my links working', 'SEO review', 'pre-publish checklist'. Generates markdown+JSON reports with PASS/FAIL verdict. Python stdlib only, no dependencies."
---

# SEO Content QA

Use this skill to audit content reliability before or after publishing.

## Requirements

- **Python 3.10+** (scripts use modern type syntax)
- `curl` available in PATH (for HTTP HEAD checks)
- No pip dependencies — standard library only

## Quick start

Run the unified runner for normal draft review:

```bash
python3 skills/seo-geo-qa/scripts/seo_qa_runner.py path/to/article.md --keyword "best email apps"
```

If you know the site's main domain, pass it so internal vs external links are counted correctly:

```bash
python3 skills/seo-geo-qa/scripts/seo_qa_runner.py path/to/article.md --keyword "best email apps" --site-domain example.com
```

If you want project defaults, pass a lightweight JSON config:

```bash
python3 skills/seo-geo-qa/scripts/seo_qa_runner.py path/to/article.md --keyword "best email apps" --config path/to/seo-geo-qa.json
```

## Standard workflow

1. Run `seo_qa_runner.py` on the draft.
2. Read the markdown report for the human audit trail.
3. Use the JSON report for automation or later aggregation.
4. Fix critical issues first.
5. Re-run until the article reaches PASS (or REVISE in writer mode).
6. After publishing, run `post_publish_check.py` on the live URL.

## Lower-level tools

Use these only when debugging a specific failure mode.

### Link/source verification
```bash
python3 skills/seo-geo-qa/scripts/verify_links.py path/to/article.md
python3 skills/seo-geo-qa/scripts/verify_links.py path/to/article.md --json
```

### SERP gap analysis

> **Note:** Auto-search uses DuckDuckGo's HTML endpoint, which may be blocked or return empty results depending on your environment. For reliable results, pass competitor URLs directly with `--urls`.

```bash
# Auto-search (best-effort, may degrade)
python3 skills/seo-geo-qa/scripts/serp_gap_analyzer.py "best email apps" path/to/article.md

# Recommended: supply competitor URLs directly
python3 skills/seo-geo-qa/scripts/serp_gap_analyzer.py "best email apps" path/to/article.md --urls https://competitor1.com https://competitor2.com
```

### Post-publish page check
```bash
python3 skills/seo-geo-qa/scripts/post_publish_check.py https://example.com/blog/post
python3 skills/seo-geo-qa/scripts/post_publish_check.py https://example.com/blog/post --json
```

## Report persistence

The runner writes timestamped markdown + JSON reports by default.

Default behavior:
- saves to `qa-reports/<article-slug>/` next to the article
- does not overwrite old reports
- uses markdown for human review and JSON for machine state

Override with `--report-dir` or config.

## Configuration

Read `references/configuration.md` when you need project-level defaults.

## Source quality

Read `references/source-tiers.md` when you need to decide whether a citation is acceptable.

## Verdict rules

Read `references/verdict-rules.md` when you need to tune PASS / FAIL / REVISE behavior.

## Example output

Read `references/example-report.md` for a real QA report with annotations on how to interpret each section.

## Design intent

This skill is not a writing assistant. It is a reliability layer.

Use scripts for deterministic checks.
Use AI judgment for tone, search intent, framing, and final editorial decisions.
