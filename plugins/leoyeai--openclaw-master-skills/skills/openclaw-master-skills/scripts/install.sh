#!/usr/bin/env bash
# Install skills from OpenClaw Master Skills collection
# Usage: bash install.sh [skill-name] [target-dir]
#   No args: lists all available skills
#   With skill-name: installs that skill to target-dir (default: ./skills/)

set -euo pipefail

REPO="https://github.com/LeoYeAI/openclaw-master-skills"
BRANCH="main"

if [ $# -eq 0 ]; then
    echo "OpenClaw Master Skills — 339+ curated skills"
    echo ""
    echo "Usage:"
    echo "  bash install.sh <skill-name> [target-dir]"
    echo "  bash install.sh --list"
    echo "  bash install.sh --all [target-dir]"
    echo ""
    echo "Examples:"
    echo "  bash install.sh github ~/.openclaw/workspace/skills/"
    echo "  bash install.sh --all ~/.openclaw/workspace/skills/"
    echo ""
    echo "Browse: $REPO"
    exit 0
fi

if [ "$1" = "--list" ]; then
    echo "Fetching skill list from GitHub..."
    curl -sL "$REPO/raw/$BRANCH/README.md" | grep -oP '(?<=\[`)[^`]+(?=`\])' | sort
    exit 0
fi

TARGET="${2:-./skills}"
mkdir -p "$TARGET"

if [ "$1" = "--all" ]; then
    echo "Cloning full collection..."
    TMPDIR=$(mktemp -d)
    git clone --depth 1 "$REPO.git" "$TMPDIR/repo" 2>/dev/null
    cp -r "$TMPDIR/repo/skills/"* "$TARGET/"
    rm -rf "$TMPDIR"
    echo "✅ All skills installed to $TARGET/"
else
    SKILL="$1"
    echo "Installing $SKILL..."
    TMPDIR=$(mktemp -d)
    cd "$TMPDIR"
    git init -q
    git remote add origin "$REPO.git"
    git sparse-checkout init
    git sparse-checkout set "skills/$SKILL"
    git pull --depth 1 origin "$BRANCH" 2>/dev/null
    if [ -d "skills/$SKILL" ]; then
        cp -r "skills/$SKILL" "$TARGET/"
        echo "✅ $SKILL installed to $TARGET/$SKILL/"
    else
        echo "❌ Skill '$SKILL' not found"
        exit 1
    fi
    cd ->/dev/null
    rm -rf "$TMPDIR"
fi
