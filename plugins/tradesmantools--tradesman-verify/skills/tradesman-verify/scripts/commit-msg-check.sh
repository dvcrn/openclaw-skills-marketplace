#!/usr/bin/env bash
# commit-msg-check.sh — Block external names, PII, and sensitive terms in commit messages.
#
# Usage:
#   As pre-commit hook:  entry: bash scripts/commit-msg-check.sh .git/COMMIT_EDITMSG
#   With --public flag:  entry: bash scripts/commit-msg-check.sh --public .git/COMMIT_EDITMSG
#   In CI mode:          bash scripts/commit-msg-check.sh --ci
#
# Exit 0 = clean, Exit 1 = blocked.

set -euo pipefail

# ── Parse flags ──────────────────────────────────────────────────────────────

PUBLIC_REPO=false
CI_MODE=false
MSG_FILE=""

for arg in "$@"; do
  case "$arg" in
    --public) PUBLIC_REPO=true ;;
    --ci)     CI_MODE=true ;;
    *)        MSG_FILE="$arg" ;;
  esac
done

# ── CI mode: scan recent commits from git log ───────────────────────────────

if $CI_MODE; then
  # Scan last 10 commits (or since origin/main~10)
  MSGS=$(git log --format="%s%n%b" -10 2>/dev/null || echo "")
  if [ -z "$MSGS" ]; then
    echo "commit-msg-check: no commits to scan"
    exit 0
  fi
  # In CI, always enforce public rules
  PUBLIC_REPO=true
else
  # Hook mode: read commit message from file
  if [ -z "$MSG_FILE" ]; then
    # pre-commit passes the file as $1 for commit-msg stage
    echo "commit-msg-check: no message file provided"
    exit 0
  fi
  if [ ! -f "$MSG_FILE" ]; then
    echo "commit-msg-check: file not found: $MSG_FILE"
    exit 0
  fi
  MSGS=$(cat "$MSG_FILE")
fi

# ── Blocklists ───────────────────────────────────────────────────────────────

# External contacts — NEVER allowed in any commit message (use handles instead)
EXTERNAL_NAMES="Jason Gregoire|Paul Snow|Eric Schedeler|Nadim Chamoun|Ryan Haczynski"
EXTERNAL_NAMES="$EXTERNAL_NAMES|Jeroen Offerijns|Peter Gaffney|Jay Smith|Benoy Varghese"
EXTERNAL_NAMES="$EXTERNAL_NAMES|Michael LeSane|Christo Becker|Olga Moroz|Sanjay Dandekar"
EXTERNAL_NAMES="$EXTERNAL_NAMES|Ralph Montague|Sandy Martinez|Michael Jagdeo|Nikki Estes"
EXTERNAL_NAMES="$EXTERNAL_NAMES|Chenny Cantano|ALShimaa Allam|Jason Kgregoire"

# Team members — allowed in PRIVATE repos only (full names + first names)
TEAM_NAMES="Jonathon Chambless|Esau Ramos|Priya Bhardwaj|Justin McKinnie"
TEAM_NAMES="$TEAM_NAMES|Jonathon|Chambless|Esau|Priya|McKinnie"

# Hard Block terms (PUBLIC repos only)
HARD_BLOCK="ACMEDesk|IPAssetCredential|tradesman-verify-pro|DACHSESA|DAAVAR|ATLASIP"
HARD_BLOCK="$HARD_BLOCK|OXTSA|CSA|ProjectAtlas|MicroPayUSD|MPUSD"
HARD_BLOCK="$HARD_BLOCK|PermitBox|MicroPay grant|Inveniam license|MicroPay equity"

# Allowed email domains
ALLOWED_DOMAINS="@bigapp\\.work|@ppcs\\.pro|@lv8rlabs\\.com|@anthropic\\.com|@users\\.noreply\\.github\\.com"

# ── Check functions ──────────────────────────────────────────────────────────

BLOCKED=false

check_pattern() {
  local label="$1"
  local pattern="$2"
  local match
  match=$(echo "$MSGS" | grep -iE "$pattern" 2>/dev/null | head -3) || true
  if [ -n "$match" ]; then
    echo "BLOCKED: $label"
    echo "  Match: $match"
    BLOCKED=true
  fi
}

# ── Run checks ───────────────────────────────────────────────────────────────

# 1. External names — always blocked
check_pattern "External person name in commit message (use @handle instead)" "$EXTERNAL_NAMES"

# 2. Team names — blocked in PUBLIC repos
if $PUBLIC_REPO; then
  check_pattern "Team member name in public repo commit (use handle or role)" "$TEAM_NAMES"
fi

# 3. Email addresses (except allowed domains)
# Match emails, then filter out allowed domains
EMAIL_MATCH=$(echo "$MSGS" | grep -ioE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' 2>/dev/null || true)
if [ -n "$EMAIL_MATCH" ]; then
  DISALLOWED=$(echo "$EMAIL_MATCH" | grep -ivE "$ALLOWED_DOMAINS" || true)
  if [ -n "$DISALLOWED" ]; then
    echo "BLOCKED: Email address in commit message"
    echo "  Match: $DISALLOWED"
    BLOCKED=true
  fi
fi

# 4. Phone numbers (+1XXXXXXXXXX or XXX-XXX-XXXX or (XXX) XXX-XXXX)
check_pattern "Phone number in commit message" '\+1[0-9]{10}|[0-9]{3}-[0-9]{3}-[0-9]{4}|\([0-9]{3}\)\s*[0-9]{3}-[0-9]{4}'

# 5. IP addresses (except 127.0.0.1, 0.0.0.0, common localhost patterns)
IP_MATCH=$(echo "$MSGS" | grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' 2>/dev/null || true)
if [ -n "$IP_MATCH" ] && ! $PUBLIC_REPO; then
  # Private repos: allow IP addresses
  :
elif [ -n "$IP_MATCH" ]; then
  DISALLOWED_IP=$(echo "$IP_MATCH" | grep -vE '^(127\.0\.0\.1|0\.0\.0\.0|localhost)$' || true)
  if [ -n "$DISALLOWED_IP" ]; then
    echo "BLOCKED: IP address in public repo commit message"
    echo "  Match: $DISALLOWED_IP"
    BLOCKED=true
  fi
fi

# 6. Hard Block terms — PUBLIC repos only
if $PUBLIC_REPO; then
  check_pattern "Hard Block term in public repo commit message" "$HARD_BLOCK"
fi

# ── Result ───────────────────────────────────────────────────────────────────

if $BLOCKED; then
  echo ""
  echo "Commit message failed hygiene check."
  echo "Fix: rewrite the message without names, emails, or blocked terms."
  echo "Ref: CLAUDE.md > Commit Message Hygiene"
  exit 1
fi

exit 0
