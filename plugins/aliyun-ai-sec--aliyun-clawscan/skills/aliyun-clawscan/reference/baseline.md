# Configuration Audit Baseline

Configuration security baseline for OpenClaw environment assessment.

## Audit Command

```bash
openclaw security audit --deep
```

## Check Categories

### 1. Gateway Authentication

**What to check:**
- Is gateway enabled?
- Is authentication required?
- Are anonymous connections allowed?

**Risk indicators:**
- Gateway open without auth → 🔴 High
- Weak/default credentials → 🔴 High
- Proper token/cookie auth → ✅ Pass

### 2. Network Exposure

**What to check:**
- Binding address (127.0.0.1 vs 0.0.0.0)
- Port exposure
- UPnP/NAT-PMP settings

**Risk indicators:**
- Bound to 0.0.0.0 with internet exposure → 🔴 High
- Localhost only binding → ✅ Pass
- mDNS/Bonjour broadcasting → ⚠️ Low

### 3. Tool Blast Radius

**What to check:**
- Default approval settings
- Tool permission scopes
- Auto-approve dangerous tools

**Risk indicators:**
- Bash/exec auto-approved → 🔴 High
- File write outside workspace auto-approved → 🔴 High
- All tools require approval → ✅ Pass

### 4. Browser Control

**What to check:**
- Remote browser manipulation enabled?
- Headless browser permissions
- Screenshot/capture capabilities

**Risk indicators:**
- Unrestricted browser control → 🔴 High
- User confirmation required → ⚠️ Medium
- Disabled/not configured → ✅ Pass

### 5. Filesystem Permissions

**What to check:**
- Workspace boundary enforcement
- Sensitive directory access (ssh, aws, etc.)
- File permission requirements

**Risk indicators:**
- Can read ~/.ssh without approval → 🔴 High
- Can write to system directories → 🔴 High
- Restricted to workspace → ✅ Pass

### 6. Open Room / Collaboration

**What to check:**
- Open room settings
- Unauthorized join capabilities
- Guest permissions

**Risk indicators:**
- Anyone can join without invite → ⚠️ Medium
- Proper access controls → ✅ Pass

## Output Parsing

Parse `openclaw security audit --deep` results into:

```
Category | Status | Details
---------|--------|--------
Gateway  | ✅/⚠️/🔴 | Description
Network  | ✅/⚠️/🔴 | Description
Tools    | ✅/⚠️/🔴 | Description
Browser  | ✅/⚠️/🔴 | Description
Files    | ✅/⚠️/🔴 | Description
Room     | ✅/⚠️/🔴 | Description
```

## Report Template

### Section: Configuration Audit Results

| Status | Check Item | Finding |
|--------|------------|---------|
| ✅/⚠️/🔴 | {Category} | {Short description} |

> If all pass: ✅ Configuration audit passed. No significant misconfigurations detected.
