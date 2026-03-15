# SoulGuard — Dangerous Pattern Scanner

This file contains the scan script for detecting dangerous patterns in a target Skill directory.
When executing, read the appropriate code block for the user's OS, write it to a temp file, and run it.

## Usage

- **Windows (PowerShell)**: Extract and run the PowerShell block below
- **Linux/macOS (Bash)**: Extract and run the Bash block below

**Execution instruction for OpenClaw:**
1. Detect the user's OS (Windows → PowerShell, otherwise → Bash)
2. Write the corresponding script content to a temp file:
   - Windows: `$env:TEMP\soulguard_scan.ps1`
   - Linux/macOS: `/tmp/soulguard_scan.sh`
3. Execute it with the target Skill path as the argument
4. Include output in the audit report under "Auxiliary Scan Results"

---

## PowerShell Script (Windows)

```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$TargetPath
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $TargetPath -PathType Container)) {
    Write-Error "Directory not found: $TargetPath"
    exit 1
}

Write-Output "=========================================="
Write-Output " SoulGuard Dangerous Pattern Scan"
Write-Output "=========================================="
Write-Output "Target: $TargetPath"
Write-Output "Time:   $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')"
Write-Output "=========================================="
Write-Output ""

$FoundCount = 0

function Scan-Pattern {
    param(
        [string]$Category,
        [string]$Description,
        [string]$Pattern
    )

    $files = Get-ChildItem -Path $TargetPath -Recurse -File -ErrorAction SilentlyContinue
    $scanResults = @()

    foreach ($file in $files) {
        try {
            $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
            if ($null -eq $content) { continue }

            $lineNum = 0
            foreach ($line in (Get-Content $file.FullName -ErrorAction SilentlyContinue)) {
                $lineNum++
                if ($line -match $Pattern) {
                    $filePath = $file.FullName
                    $scanResults += "   -> ${filePath}:${lineNum}: $($line.Trim())"
                }
            }
        } catch {
            # Skip binary or unreadable files
        }
    }

    if ($scanResults.Count -gt 0) {
        $script:FoundCount++
        Write-Output "[WARNING] [$Category] $Description"
        Write-Output "   Pattern: $Pattern"
        Write-Output "   Matches:"
        $scanResults | ForEach-Object { Write-Output $_ }
        Write-Output ""
    }
}

Write-Output "--- Credential Access ---"
Scan-Pattern "CREDENTIAL" "SSH key directory access" '~[/\\]\.ssh|\.ssh[/\\]|id_rsa|id_ed25519|authorized_keys'
Scan-Pattern "CREDENTIAL" "AWS credential access" '~[/\\]\.aws|\.aws[/\\]credentials|AWS_SECRET|AWS_ACCESS_KEY'
Scan-Pattern "CREDENTIAL" "Browser cookie/data access" 'cookies\.sqlite|Cookies|Login Data|\.mozilla|\.chrome|\.chromium'
Scan-Pattern "CREDENTIAL" "Wallet/crypto data access" 'wallet\.dat|\.bitcoin|\.ethereum|keystore'
Scan-Pattern "CREDENTIAL" "Generic secret/token patterns" 'API_KEY|SECRET_KEY|PRIVATE_KEY|ACCESS_TOKEN|Bearer [A-Za-z0-9]'
Scan-Pattern "CREDENTIAL" "Environment variable extraction" 'process\.env|os\.environ|getenv'

Write-Output "--- External Code Execution ---"
Scan-Pattern "EXEC" "Pipe-to-shell pattern" 'curl.*\|.*sh|wget.*\|.*sh|curl.*\|.*bash|wget.*\|.*bash'
Scan-Pattern "EXEC" "Remote script download and execute" 'curl.*-o.*&&.*chmod|wget.*&&.*chmod|curl.*>/tmp/|wget.*>/tmp/'
Scan-Pattern "EXEC" "Eval/exec of dynamic content" 'eval\s*\(|exec\s*\(|Function\s*\(|child_process'
Scan-Pattern "EXEC" "PowerShell remote execution" 'Invoke-Expression|IEX\s*\(|Invoke-WebRequest.*\|.*iex|DownloadString'

Write-Output "--- Persistence Mechanisms ---"
Scan-Pattern "PERSIST" "System startup directories" '/etc/init\.d|/etc/systemd|/etc/cron|crontab|\.bashrc|\.bash_profile|\.zshrc|\.profile'
Scan-Pattern "PERSIST" "Windows startup/scheduled tasks" 'schtasks|Start-Up|Startup|HKLM.*Run|HKCU.*Run|Register-ScheduledTask'
Scan-Pattern "PERSIST" "LaunchAgent/LaunchDaemon (macOS)" 'LaunchAgents|LaunchDaemons|\.plist'

Write-Output "--- Perception Blocking ---"
Scan-Pattern "STEALTH" "Log suppression" 'disable.*log|>\s*/dev/null|2>/dev/null|Out-Null|-ErrorAction\s+SilentlyContinue'
Scan-Pattern "STEALTH" "Configuration tampering" 'openclaw\.json|\.openclaw[/\\]|config.*overwrite|config.*replace'
Scan-Pattern "STEALTH" "Instruction override attempts" 'ignore.*previous|ignore.*instructions|forget.*above|disregard.*system|override.*prompt'

Write-Output "--- Data Exfiltration ---"
Scan-Pattern "EXFIL" "Encoded data patterns" 'base64|btoa|atob|base64_encode|base64_decode'
Scan-Pattern "EXFIL" "Network upload to unknown targets" 'curl.*-X\s*POST|curl.*--data|wget.*--post|fetch.*POST|axios\.post|http\.post'
Scan-Pattern "EXFIL" "DNS/network tunneling indicators" 'nslookup|dig\s|nc\s.*-e|ncat|socat'

Write-Output "--- Identity Manipulation ---"
Scan-Pattern "IDENTITY" "System prompt override" 'system.*prompt|System.*Prompt|SYSTEM.*PROMPT|system_message|systemMessage'
Scan-Pattern "IDENTITY" "Memory/personality manipulation" 'forget.*everything|reset.*personality|new.*identity|you are now|act as'

Write-Output "=========================================="
Write-Output " Scan Complete"
Write-Output " Findings: $FoundCount pattern categories matched"
Write-Output "=========================================="
```

---

## Bash Script (Linux/macOS)

```bash
#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:?Usage: scan.sh <target_skill_path>}"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory not found: $TARGET_DIR" >&2
    exit 1
fi

echo "=========================================="
echo " SoulGuard Dangerous Pattern Scan"
echo "=========================================="
echo "Target: $TARGET_DIR"
echo "Time:   $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "=========================================="
echo ""

FOUND_COUNT=0

scan_pattern() {
    local category="$1"
    local description="$2"
    local pattern="$3"

    local results
    results=$(grep -rnI --include="*" -E "$pattern" "$TARGET_DIR" 2>/dev/null || true)

    if [ -n "$results" ]; then
        FOUND_COUNT=$((FOUND_COUNT + 1))
        echo "[WARNING] [$category] $description"
        echo "   Pattern: $pattern"
        echo "   Matches:"
        while IFS= read -r line; do
            echo "   -> $line"
        done <<< "$results"
        echo ""
    fi
}

echo "--- Credential Access ---"
scan_pattern "CREDENTIAL" "SSH key directory access" '~[/\\]\.ssh|\.ssh[/\\]|id_rsa|id_ed25519|authorized_keys'
scan_pattern "CREDENTIAL" "AWS credential access" '~[/\\]\.aws|\.aws[/\\]credentials|AWS_SECRET|AWS_ACCESS_KEY'
scan_pattern "CREDENTIAL" "Browser cookie/data access" 'cookies\.sqlite|Cookies|Login Data|\.mozilla|\.chrome|\.chromium'
scan_pattern "CREDENTIAL" "Wallet/crypto data access" 'wallet\.dat|\.bitcoin|\.ethereum|keystore'
scan_pattern "CREDENTIAL" "Generic secret/token patterns" 'API_KEY|SECRET_KEY|PRIVATE_KEY|ACCESS_TOKEN|Bearer [A-Za-z0-9]'
scan_pattern "CREDENTIAL" "Environment variable extraction" 'process\.env|os\.environ|\$ENV\{|getenv'

echo "--- External Code Execution ---"
scan_pattern "EXEC" "Pipe-to-shell pattern" 'curl.*\|.*sh|wget.*\|.*sh|curl.*\|.*bash|wget.*\|.*bash'
scan_pattern "EXEC" "Remote script download and execute" 'curl.*-o.*&&.*chmod|wget.*&&.*chmod|curl.*>/tmp/|wget.*>/tmp/'
scan_pattern "EXEC" "Eval/exec of dynamic content" 'eval\s*\(|exec\s*\(|Function\s*\(|child_process'
scan_pattern "EXEC" "PowerShell remote execution" 'Invoke-Expression|IEX\s*\(|DownloadString'

echo "--- Persistence Mechanisms ---"
scan_pattern "PERSIST" "System startup directories" '/etc/init\.d|/etc/systemd|/etc/cron|crontab|\.bashrc|\.bash_profile|\.zshrc|\.profile'
scan_pattern "PERSIST" "Windows startup/scheduled tasks" 'schtasks|HKLM.*Run|HKCU.*Run|Register-ScheduledTask'
scan_pattern "PERSIST" "LaunchAgent/LaunchDaemon (macOS)" 'LaunchAgents|LaunchDaemons|\.plist'

echo "--- Perception Blocking ---"
scan_pattern "STEALTH" "Log suppression" 'disable.*log|>/dev/null|2>/dev/null|Out-Null|--quiet'
scan_pattern "STEALTH" "Configuration tampering" 'openclaw\.json|\.openclaw/|config.*overwrite|config.*replace'
scan_pattern "STEALTH" "Instruction override attempts" 'ignore.*previous|ignore.*instructions|forget.*above|disregard.*system|override.*prompt'

echo "--- Data Exfiltration ---"
scan_pattern "EXFIL" "Encoded data patterns" 'base64|btoa|atob|base64_encode|base64_decode'
scan_pattern "EXFIL" "Network upload to unknown targets" 'curl.*-X POST|curl.*--data|wget.*--post|fetch.*POST|axios\.post|http\.post'
scan_pattern "EXFIL" "DNS/network tunneling indicators" 'nslookup|dig |nc .*-e|ncat|socat'

echo "--- Identity Manipulation ---"
scan_pattern "IDENTITY" "System prompt override" 'system.*prompt|System.*Prompt|SYSTEM.*PROMPT|system_message|systemMessage'
scan_pattern "IDENTITY" "Memory/personality manipulation" 'forget.*everything|reset.*personality|new.*identity|you are now|act as'

echo "=========================================="
echo " Scan Complete"
echo " Findings: $FOUND_COUNT pattern categories matched"
echo "=========================================="
```
