#!/bin/bash
# verify-backup.sh v1.2.1 — integrity checker for healthy-backup archives
# Usage: ./verify-backup.sh [file.tgz.gpg | /backup/dir]
# Default target: backupRoot from openclaw.json, else ~/openclaw-backups
set -euo pipefail

G='\033[0;32m' R='\033[0;31m' Y='\033[1;33m' BO='\033[1m' X='\033[0m'
ok()   { echo -e "${G}  ✓${X} $*"; }
fail() { echo -e "${R}  ✗${X} $*"; }
warn() { echo -e "${Y}  ⚠${X} $*"; }

# Resolve default backup root from openclaw config
CFG="$HOME/.openclaw/openclaw.json"
ROOT="$HOME/openclaw-backups"
[ -f "$CFG" ] && {
    v=$(jq -r '.skills.entries["healthy-backup"].config.backupRoot // empty' "$CFG" 2>/dev/null)
    v="${v/#\~/$HOME}"; ROOT="${v:-$ROOT}"
}

TARGET="${1:-$ROOT}"
echo -e "\n${BO}━━━ BACKUP INTEGRITY CHECK${X} — $TARGET\n"

PASS=0 FAIL=0 SKIP=0

check() {
    local archive="$1" cs="${1}.sha256"
    echo -e "${BO}$(basename "$archive")${X}"
    if [ ! -f "$cs" ]; then
        warn "No .sha256 — skipping"; SKIP=$((SKIP+1)); return
    fi
    sha256sum --check "$cs" --status 2>/dev/null \
        && { ok "SHA256 OK"; PASS=$((PASS+1)); } \
        || { fail "SHA256 MISMATCH"; FAIL=$((FAIL+1)); }
    gpg --batch --list-packets "$archive" &>/dev/null \
        && ok "GPG envelope intact" \
        || { fail "GPG envelope damaged"; FAIL=$((FAIL+1)); }
    echo ""
}

if   [ -f "$TARGET" ]; then check "$TARGET"
elif [ -d "$TARGET" ]; then
    shopt -s nullglob
    archives=("$TARGET"/healthy-backup-*.tgz.gpg)
    [ "${#archives[@]}" -eq 0 ] && { echo "No archives found in $TARGET"; exit 0; }
    for a in "${archives[@]}"; do check "$a"; done
else
    echo -e "${R}Error:${X} '$TARGET' is not a file or directory."; exit 1
fi

echo -e "${BO}━━━ RESULT${X}  ${G}OK: $PASS${X}  ${Y}Skip: $SKIP${X}  ${R}Fail: $FAIL${X}\n"
[ "$FAIL" -gt 0 ] && exit 1; exit 0

# END OF FILE — verify-backup.sh v1.2.1
