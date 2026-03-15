# SoulGuard — Soul Integrity Checker

This file contains the integrity check script for verifying that OpenClaw's core configuration has not been tampered with.

## Usage

- **Action `store`**: Record the current SHA256 hash of core config files as a baseline ("this is my clean state")
- **Action `verify`**: Compare current hash against the stored baseline to detect tampering

**Execution instruction for OpenClaw:**
1. Detect the user's OS (Windows → PowerShell, otherwise → Bash)
2. Write the corresponding script to a temp file:
   - Windows: `$env:TEMP\soulguard_integrity.ps1`
   - Linux/macOS: `/tmp/soulguard_integrity.sh`
3. Run it with the appropriate action (`store` or `verify`)
4. Include output in the audit report under "Soul Integrity Status"

**Default monitored file:**
- Windows: `%USERPROFILE%\.openclaw\openclaw.json`
- Linux/macOS: `~/.openclaw/openclaw.json`

---

## PowerShell Script (Windows)

```powershell
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("store", "verify")]
    [string]$Action,

    [Parameter(Mandatory=$false)]
    [string]$FilePath
)

$ErrorActionPreference = "Stop"

$StoreDir = Join-Path $env:USERPROFILE ".soulguard"
$HashFile = Join-Path $StoreDir "integrity_hashes.json"

$DefaultPaths = @(
    (Join-Path $env:USERPROFILE ".openclaw\openclaw.json")
)

if (-not (Test-Path $StoreDir)) {
    New-Item -ItemType Directory -Path $StoreDir -Force | Out-Null
}

if (-not (Test-Path $HashFile)) {
    '{}' | Set-Content $HashFile -Encoding UTF8
}

function Get-FileHashValue {
    param([string]$Path)
    if (Test-Path $Path -PathType Leaf) {
        return (Get-FileHash -Path $Path -Algorithm SHA256).Hash.ToLower()
    } else {
        return "FILE_NOT_FOUND"
    }
}

function Store-Hash {
    param([string]$Path)
    $hash = Get-FileHashValue $Path
    $timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    if ($hash -eq "FILE_NOT_FOUND") {
        Write-Output "[WARNING] File not found: $Path"
        return
    }
    $data = Get-Content $HashFile -Raw | ConvertFrom-Json
    $entry = @{ hash = $hash; stored_at = $timestamp }
    if ($data.PSObject.Properties.Name -contains $Path) {
        $data.$Path = $entry
    } else {
        $data | Add-Member -NotePropertyName $Path -NotePropertyValue $entry
    }
    $data | ConvertTo-Json -Depth 10 | Set-Content $HashFile -Encoding UTF8
    Write-Output "[OK] Stored hash for: $Path"
    Write-Output "   Hash: $hash"
    Write-Output "   Time: $timestamp"
}

function Verify-Hash {
    param([string]$Path)
    $currentHash = Get-FileHashValue $Path
    if ($currentHash -eq "FILE_NOT_FOUND") {
        Write-Output "[WARNING] File not found: $Path"
        return
    }
    $data = Get-Content $HashFile -Raw | ConvertFrom-Json
    if (-not ($data.PSObject.Properties.Name -contains $Path)) {
        Write-Output "[WARNING] No baseline hash found for: $Path"
        Write-Output "   Run with -Action store first to establish a baseline."
        return
    }
    $storedHash = $data.$Path.hash
    if ($currentHash -eq $storedHash) {
        Write-Output "[INTACT] $Path"
        Write-Output "   Hash: $currentHash"
    } else {
        Write-Output "[TAMPERED] $Path"
        Write-Output "   Expected: $storedHash"
        Write-Output "   Current:  $currentHash"
        Write-Output "   WARNING: Core configuration may have been modified!"
    }
}

Write-Output "=========================================="
Write-Output " SoulGuard Soul Integrity Check"
Write-Output "=========================================="
Write-Output "Action: $Action"
Write-Output "Time:   $((Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'))"
Write-Output "=========================================="
Write-Output ""

$pathsToCheck = if ($FilePath) { @($FilePath) } else { $DefaultPaths }

switch ($Action) {
    "store"  { foreach ($p in $pathsToCheck) { Store-Hash $p } }
    "verify" { foreach ($p in $pathsToCheck) { Verify-Hash $p } }
}

Write-Output ""
Write-Output "=========================================="
Write-Output " Integrity Check Complete"
Write-Output "=========================================="
```

---

## Bash Script (Linux/macOS)

```bash
#!/usr/bin/env bash
set -euo pipefail

ACTION="${1:?Usage: integrity.sh <store|verify> [file_path]}"
FILE_PATH="${2:-}"

STORE_DIR="$HOME/.soulguard"
HASH_FILE="$STORE_DIR/integrity_hashes.json"
DEFAULT_PATH="$HOME/.openclaw/openclaw.json"

mkdir -p "$STORE_DIR"
[ -f "$HASH_FILE" ] || echo '{}' > "$HASH_FILE"

get_hash() {
    local path="$1"
    if [ -f "$path" ]; then
        sha256sum "$path" 2>/dev/null | awk '{print $1}'
    else
        echo "FILE_NOT_FOUND"
    fi
}

store_hash() {
    local path="$1"
    local hash
    hash=$(get_hash "$path")
    if [ "$hash" = "FILE_NOT_FOUND" ]; then
        echo "[WARNING] File not found: $path"
        return
    fi
    local timestamp
    timestamp=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
    local key
    key=$(echo "$path" | sed 's/[^a-zA-Z0-9]/_/g')
    python3 -c "
import json, sys
with open('$HASH_FILE') as f:
    data = json.load(f)
data['$path'] = {'hash': '$hash', 'stored_at': '$timestamp'}
with open('$HASH_FILE', 'w') as f:
    json.dump(data, f, indent=2)
" 2>/dev/null || python -c "
import json
with open('$HASH_FILE') as f:
    data = json.load(f)
data['$path'] = {'hash': '$hash', 'stored_at': '$timestamp'}
with open('$HASH_FILE', 'w') as f:
    json.dump(data, f, indent=2)
"
    echo "[OK] Stored hash for: $path"
    echo "   Hash: $hash"
    echo "   Time: $timestamp"
}

verify_hash() {
    local path="$1"
    local current_hash
    current_hash=$(get_hash "$path")
    if [ "$current_hash" = "FILE_NOT_FOUND" ]; then
        echo "[WARNING] File not found: $path"
        return
    fi
    local stored_hash
    stored_hash=$(python3 -c "
import json
with open('$HASH_FILE') as f:
    data = json.load(f)
print(data.get('$path', {}).get('hash', 'NO_BASELINE'))
" 2>/dev/null || echo "NO_BASELINE")
    if [ "$stored_hash" = "NO_BASELINE" ]; then
        echo "[WARNING] No baseline hash found for: $path"
        echo "   Run 'integrity.sh store' first."
        return
    fi
    if [ "$current_hash" = "$stored_hash" ]; then
        echo "[INTACT] $path"
        echo "   Hash: $current_hash"
    else
        echo "[TAMPERED] $path"
        echo "   Expected: $stored_hash"
        echo "   Current:  $current_hash"
        echo "   WARNING: Core configuration may have been modified!"
    fi
}

TARGET="${FILE_PATH:-$DEFAULT_PATH}"

echo "=========================================="
echo " SoulGuard Soul Integrity Check"
echo "=========================================="
echo "Action: $ACTION / Target: $TARGET"
echo "=========================================="
echo ""

case "$ACTION" in
    store)  store_hash "$TARGET" ;;
    verify) verify_hash "$TARGET" ;;
    *) echo "Unknown action: $ACTION. Use 'store' or 'verify'." >&2; exit 1 ;;
esac

echo ""
echo "=========================================="
echo " Integrity Check Complete"
echo "=========================================="
```
