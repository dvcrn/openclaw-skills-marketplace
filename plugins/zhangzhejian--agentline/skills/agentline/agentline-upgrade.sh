#!/usr/bin/env bash
# agentline-upgrade.sh — Check for updates and upgrade Agentline CLI tools.
#
# Usage:
#   agentline-upgrade.sh [--check] [--force] [--hub <url>]
#
#   --check   Only check if an update is available (do not install)
#   --force   Re-install even if already on latest version
#   --hub     Override hub URL (default: https://agentgram.chat)

set -euo pipefail

# ── Minimal helpers (no dependency on agentline-common.sh) ────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'; BOLD='\033[1m'

die() { printf "${RED}error:${NC} %s\n" "$1" >&2; exit 1; }
info() { printf "${GREEN}✓${NC} %s\n" "$1"; }
warn() { printf "${YELLOW}⚠${NC} %s\n" "$1"; }

# ── Dependency check ─────────────────────────────────────────
command -v curl >/dev/null 2>&1 || die "curl is required but not found"
command -v jq   >/dev/null 2>&1 || die "jq is required but not found"

# ── Parse args ───────────────────────────────────────────────
HUB="https://agentgram.chat"
CHECK_ONLY=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --check) CHECK_ONLY=true; shift ;;
        --force) FORCE=true; shift ;;
        --hub)   HUB="$2"; shift 2 ;;
        --help|-h)
            echo "Usage: agentline-upgrade.sh [--check] [--force] [--hub <url>]"
            echo ""
            echo "  --check   Only check if an update is available (do not install)"
            echo "  --force   Re-install even if already on latest version"
            echo "  --hub     Override hub URL (default: https://agentgram.chat)"
            exit 0
            ;;
        *) die "Unknown option: $1" ;;
    esac
done

# ── Read local version ───────────────────────────────────────
VERSION_FILE="${HOME}/.agentline/version"
if [[ -f "$VERSION_FILE" ]]; then
    LOCAL_VERSION="$(cat "$VERSION_FILE" | tr -d '[:space:]')"
else
    LOCAL_VERSION="0.0.0"
fi

# ── Fetch remote version ─────────────────────────────────────
VERSION_URL="${HUB}/skill/agentgram/version.json"

HTTP_BODY="$(curl -fsSL "$VERSION_URL" 2>/dev/null)" \
    || die "Failed to fetch version info from ${VERSION_URL}"

REMOTE_VERSION="$(jq -r '.latest // empty' <<< "$HTTP_BODY")" \
    || die "Failed to parse version.json"
INSTALL_URL="$(jq -r '.install_url // empty' <<< "$HTTP_BODY")" \
    || die "Failed to parse install_url from version.json"

[[ -n "$REMOTE_VERSION" ]] || die "Empty 'latest' field in version.json"
[[ -n "$INSTALL_URL" ]]    || die "Empty 'install_url' field in version.json"

# ── Compare versions ─────────────────────────────────────────
UPDATE_AVAILABLE=false
if [[ "$LOCAL_VERSION" != "$REMOTE_VERSION" ]]; then
    UPDATE_AVAILABLE=true
fi

# --check: print status and exit
if $CHECK_ONLY; then
    jq -n \
        --arg local  "$LOCAL_VERSION" \
        --arg remote "$REMOTE_VERSION" \
        --argjson update_available "$UPDATE_AVAILABLE" \
        '{local_version: $local, remote_version: $remote, update_available: $update_available}'
    exit 0
fi

# Already up to date (no --force)
if [[ "$UPDATE_AVAILABLE" == "false" ]] && ! $FORCE; then
    info "Already up to date (v${LOCAL_VERSION})"
    jq -n \
        --arg version "$LOCAL_VERSION" \
        '{upgraded: false, version: $version, reason: "already_up_to_date"}'
    exit 0
fi

# ── Perform upgrade ──────────────────────────────────────────
if $FORCE && [[ "$UPDATE_AVAILABLE" == "false" ]]; then
    warn "Forcing reinstall of v${REMOTE_VERSION}"
else
    info "Upgrading from v${LOCAL_VERSION} → v${REMOTE_VERSION}..."
fi

curl -fsSL "$INSTALL_URL" | bash

info "Upgrade complete!"

# ── Show changelog between versions ─────────────────────────
# semver_compare: returns 0 if a==b, 1 if a>b, 2 if a<b
semver_compare() {
    local IFS=.
    local -a A=($1) B=($2)
    for i in 0 1 2; do
        local a="${A[$i]:-0}" b="${B[$i]:-0}"
        if (( a > b )); then return 1; fi
        if (( a < b )); then return 2; fi
    done
    return 0
}

# semver_gt: true if $1 > $2
semver_gt() { semver_compare "$1" "$2"; [[ $? -eq 1 ]]; }

# semver_le: true if $1 <= $2
semver_le() { semver_compare "$1" "$2"; [[ $? -ne 1 ]]; }

CHANGELOG_URL="${HUB}/skill/agentgram/CHANGELOG.json"
CHANGELOG_BODY="$(curl -fsSL "$CHANGELOG_URL" 2>/dev/null)" || CHANGELOG_BODY=""

CHANGELOG_MAX_CHARS=5000

if [[ -n "$CHANGELOG_BODY" ]]; then
    # Build plain-text changelog buffer (newest first), then truncate
    RELEVANT="$(jq -r '.[].version' <<< "$CHANGELOG_BODY")" || RELEVANT=""
    CHANGELOG_BUF=""

    for ver in $RELEVANT; do
        if semver_gt "$ver" "$LOCAL_VERSION" && semver_le "$ver" "$REMOTE_VERSION"; then
            CHANGELOG_BUF+=$'\n'"v${ver}"$'\n'
            while IFS= read -r line; do
                CHANGELOG_BUF+="  • ${line}"$'\n'
            done < <(jq -r --arg v "$ver" '.[] | select(.version == $v) | .changes[]' <<< "$CHANGELOG_BODY")
        fi
    done

    if [[ -n "$CHANGELOG_BUF" ]]; then
        printf "\n${BOLD}${CYAN}── What's new ──${NC}\n"
        if (( ${#CHANGELOG_BUF} > CHANGELOG_MAX_CHARS )); then
            # Truncate to last complete line within limit
            TRUNCATED_BUF="${CHANGELOG_BUF:0:$CHANGELOG_MAX_CHARS}"
            # Trim to last newline to avoid partial lines
            TRUNCATED_BUF="${TRUNCATED_BUF%$'\n'*}"
            printf "%s\n" "$TRUNCATED_BUF"
            printf "\n${YELLOW}(changelog truncated at %d chars — run 'curl <hub>/skill/agentgram/CHANGELOG.json | jq' for full log)${NC}\n" "$CHANGELOG_MAX_CHARS"
        else
            printf "%s" "$CHANGELOG_BUF"
        fi
        printf "\n"
    fi
fi

jq -n \
    --arg from "$LOCAL_VERSION" \
    --arg to   "$REMOTE_VERSION" \
    --argjson forced "$FORCE" \
    '{upgraded: true, from_version: $from, to_version: $to, forced: $forced}'
