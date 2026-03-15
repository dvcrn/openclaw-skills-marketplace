# SoulGuard — Audit History Manager

This file contains the audit history script for recording and querying past Skill audit results.

## Usage

- **Action `add`**: Record a new audit result
- **Action `query`**: Look up all audits for a specific Skill
- **Action `list`**: Show a summary of all audited Skills

**Execution instruction for OpenClaw:**
1. Detect the user's OS (Windows → PowerShell, otherwise → Bash)
2. Write the corresponding script to a temp file:
   - Windows: `$env:TEMP\soulguard_history.ps1`
   - Linux/macOS: `/tmp/soulguard_history.sh`
3. After generating the audit report, call with action `add` to record the result
4. When the user asks about past audits, call with action `query` or `list`

**Storage location:** `~/.soulguard/audit_history.json`

---

## PowerShell Script (Windows)

```powershell
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("add", "query", "list")]
    [string]$Action,

    [Parameter(Mandatory=$false)]
    [string]$SkillName,

    [Parameter(Mandatory=$false)]
    [string]$RiskLevel,

    [Parameter(Mandatory=$false)]
    [string]$Summary
)

$ErrorActionPreference = "Stop"

$StoreDir = Join-Path $env:USERPROFILE ".soulguard"
$HistoryFile = Join-Path $StoreDir "audit_history.json"

if (-not (Test-Path $StoreDir)) {
    New-Item -ItemType Directory -Path $StoreDir -Force | Out-Null
}

if (-not (Test-Path $HistoryFile)) {
    '{"audits":[]}' | Set-Content $HistoryFile -Encoding UTF8
}

$data = Get-Content $HistoryFile -Raw | ConvertFrom-Json

switch ($Action) {
    "add" {
        if (-not $SkillName -or -not $RiskLevel -or -not $Summary) {
            Write-Error "Usage: -Action add -SkillName <name> -RiskLevel <level> -Summary <text>"
            exit 1
        }
        $timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        $entry = @{
            skill_name = $SkillName
            risk_level = $RiskLevel
            summary    = $Summary
            audited_at = $timestamp
        }
        if ($null -eq $data.audits) { $data.audits = @() }
        $data.audits += $entry
        $data | ConvertTo-Json -Depth 10 | Set-Content $HistoryFile -Encoding UTF8
        Write-Output "[OK] Recorded audit for: $SkillName"
        Write-Output "   Risk Level: $RiskLevel"
        Write-Output "   Time: $timestamp"
    }
    "query" {
        if (-not $SkillName) {
            Write-Error "Usage: -Action query -SkillName <name>"
            exit 1
        }
        Write-Output "=========================================="
        Write-Output " Audit History: $SkillName"
        Write-Output "=========================================="
        $results = $data.audits | Where-Object { $_.skill_name -eq $SkillName }
        if (-not $results -or $results.Count -eq 0) {
            Write-Output "No audit records found."
        } else {
            foreach ($r in $results) {
                Write-Output "  [$($r.audited_at)] Risk: $($r.risk_level)"
                Write-Output "  Summary: $($r.summary)"
                Write-Output ""
            }
        }
    }
    "list" {
        Write-Output "=========================================="
        Write-Output " All Audit Records"
        Write-Output "=========================================="
        if (-not $data.audits -or $data.audits.Count -eq 0) {
            Write-Output "No audit records found."
        } else {
            $grouped = $data.audits | Group-Object skill_name
            foreach ($group in $grouped) {
                $latest = $group.Group | Sort-Object audited_at | Select-Object -Last 1
                Write-Output "  $($group.Name): $($group.Count) audit(s), latest risk: $($latest.risk_level) ($($latest.audited_at))"
            }
        }
    }
}
```

---

## Bash Script (Linux/macOS)

```bash
#!/usr/bin/env bash
set -euo pipefail

ACTION="${1:?Usage: history.sh <add|query|list> [args]}"

STORE_DIR="$HOME/.soulguard"
HISTORY_FILE="$STORE_DIR/audit_history.json"

mkdir -p "$STORE_DIR"
[ -f "$HISTORY_FILE" ] || echo '{"audits":[]}' > "$HISTORY_FILE"

case "$ACTION" in
    add)
        SKILL_NAME="${2:?Missing skill name}"
        RISK_LEVEL="${3:?Missing risk level}"
        SUMMARY="${4:?Missing summary}"
        TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
        python3 -c "
import json
with open('$HISTORY_FILE') as f:
    data = json.load(f)
data.setdefault('audits', []).append({
    'skill_name': '$SKILL_NAME',
    'risk_level': '$RISK_LEVEL',
    'summary': '$SUMMARY',
    'audited_at': '$TIMESTAMP'
})
with open('$HISTORY_FILE', 'w') as f:
    json.dump(data, f, indent=2)
"
        echo "[OK] Recorded audit for: $SKILL_NAME"
        echo "   Risk Level: $RISK_LEVEL"
        echo "   Time: $TIMESTAMP"
        ;;
    query)
        SKILL_NAME="${2:?Missing skill name}"
        echo "=========================================="
        echo " Audit History: $SKILL_NAME"
        echo "=========================================="
        python3 -c "
import json
with open('$HISTORY_FILE') as f:
    data = json.load(f)
results = [a for a in data.get('audits', []) if a['skill_name'] == '$SKILL_NAME']
if not results:
    print('No audit records found.')
else:
    for r in results:
        print(f\"  [{r['audited_at']}] Risk: {r['risk_level']}\")
        print(f\"  Summary: {r.get('summary','')}\")
        print()
"
        ;;
    list)
        echo "=========================================="
        echo " All Audit Records"
        echo "=========================================="
        python3 -c "
import json
from collections import defaultdict
with open('$HISTORY_FILE') as f:
    data = json.load(f)
audits = data.get('audits', [])
if not audits:
    print('No audit records found.')
else:
    groups = defaultdict(list)
    for a in audits:
        groups[a['skill_name']].append(a)
    for name, records in groups.items():
        latest = sorted(records, key=lambda x: x['audited_at'])[-1]
        print(f\"  {name}: {len(records)} audit(s), latest risk: {latest['risk_level']} ({latest['audited_at']})\")
"
        ;;
    *)
        echo "Unknown action: $ACTION. Use add, query, or list." >&2
        exit 1
        ;;
esac
```
