#!/bin/bash
# Publish skill to ClawHub with automatic version/changelog sync.
#
# Usage: ./scripts/publish.sh 0.15.5
#
# What it does:
# 1. Updates version in docs/index.html footer
# 2. Generates docs/changelog.json from CHANGELOG.md
# 3. Commits version bump
# 4. Pushes to origin/main
# 5. Publishes to ClawHub

set -euo pipefail

VERSION="${1:?Usage: $0 <version>}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

echo "=== Publishing bitrix24@${VERSION} ==="

# 1. Update version in footer
echo "→ Updating docs/index.html footer..."
sed -i '' "s/Bitrix24 Skill v[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*/Bitrix24 Skill v${VERSION}/" docs/index.html

# 2. Generate changelog.json from CHANGELOG.md
echo "→ Generating docs/changelog.json..."
python3 "$SCRIPT_DIR/changelog_to_json.py" "$VERSION"

# 3. Commit
echo "→ Committing version bump..."
git add docs/index.html docs/changelog.json CHANGELOG.md
git commit -m "Release v${VERSION}" --allow-empty || true

# 4. Push
echo "→ Pushing to origin/main..."
git push origin main

# 5. Publish to ClawHub
echo "→ Publishing to ClawHub..."
npx clawhub publish . --version "$VERSION"

echo ""
echo "=== Done: bitrix24@${VERSION} published ==="
echo "Wait ~90s for security scan, then install:"
echo "  ssh slon-mac \"export PATH=\\\$HOME/.nvm/versions/node/*/bin:/opt/homebrew/bin:/usr/local/bin:\\\$PATH && npx clawhub install bitrix24 --version ${VERSION} --force\""
