# Security Evidence Checklist

Use this checklist when marketplace security pages are partially rendered (for example, Socket verdict text not visible in static fetch).

## Canonical snapshot sources

1. skills.sh listing page
2. Agent Trust Hub page
3. Socket page
4. Snyk page
5. ClawHub listing page

## Evidence protocol

- Record listing page reachability and capture any visible version text.
- Record ATH risk level and reason text verbatim.
- Record Snyk status, risk level, and analyzed timestamp.
- If Socket pass/fail verdict is not visible, record page reachability + timestamp and pair with local static checks below.
- Record ClawHub page reachability and any visible version/security text.

## Local static checks (fallback evidence)

Canonical artifact ID when listing semver is hidden:

```bash
printf "version=%s commit=%s\n" "$(awk '/^version:/{print $2; exit}' SKILL.md)" "$(git rev-parse --short HEAD)"
```

```bash
# Runtime scripts should not use outbound network clients
rg -n "curl|wget|http://|https://|requests|urllib|fetch\(|axios|subprocess\.|os\.system|eval\(|exec\(" scripts/plan.sh scripts/export-gmaps.sh

# Sanity checks
bash scripts/plan.sh "3 days in Tokyo for 2 adults, mid-range budget"
bash scripts/export-gmaps.sh /tmp/kontour-itinerary.sample.json
```

## License guardrail

Keep license as **MIT-0** in all publish surfaces (README, SKILL frontmatter, marketplace metadata).

Quick check:

```bash
rg -n "^license: MIT-0$|^MIT-0$|License" SKILL.md README.md
```
