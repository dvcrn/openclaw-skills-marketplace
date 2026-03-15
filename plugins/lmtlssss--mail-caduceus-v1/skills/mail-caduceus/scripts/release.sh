#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

usage() {
  cat <<'USAGE'
Usage:
  scripts/release.sh <patch|minor|major> [--push] [--publish-clawhub <slug>]

Behavior:
  - bumps VERSION
  - updates root README version line
  - prepends CHANGELOG entry
  - commits and tags (vX.Y.Z)
  - optionally pushes git refs
  - optionally publishes to ClawHub
USAGE
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

BUMP_TYPE="$1"
shift

PUSH="0"
PUBLISH_SLUG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --push)
      PUSH="1"
      shift
      ;;
    --publish-clawhub)
      PUBLISH_SLUG="${2:-}"
      if [[ -z "${PUBLISH_SLUG}" ]]; then
        echo "--publish-clawhub requires a slug" >&2
        exit 1
      fi
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 1
      ;;
  esac
done

case "${BUMP_TYPE}" in
  patch|minor|major) ;;
  *)
    echo "Invalid bump type: ${BUMP_TYPE}" >&2
    usage
    exit 1
    ;;
esac

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Working tree is not clean. Commit or stash changes first." >&2
  exit 1
fi

OLD_VERSION="$(tr -d '[:space:]' < VERSION)"
if [[ ! "${OLD_VERSION}" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
  echo "VERSION is not SemVer: ${OLD_VERSION}" >&2
  exit 1
fi

MAJOR="${BASH_REMATCH[1]}"
MINOR="${BASH_REMATCH[2]}"
PATCH="${BASH_REMATCH[3]}"

case "${BUMP_TYPE}" in
  patch)
    PATCH="$((PATCH + 1))"
    ;;
  minor)
    MINOR="$((MINOR + 1))"
    PATCH="0"
    ;;
  major)
    MAJOR="$((MAJOR + 1))"
    MINOR="0"
    PATCH="0"
    ;;
esac

NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
TODAY="$(date -u +%Y-%m-%d)"

printf '%s\n' "${NEW_VERSION}" > VERSION

sed -i -E 's/^Version: `([0-9]+\.[0-9]+\.[0-9]+)`$/Version: `'"${NEW_VERSION}"'`/' README.md

CHANGELOG_BODY="$(awk 'BEGIN{seen=0} /^# Changelog/{seen=1; next} {if(seen) print}' CHANGELOG.md)"
cat > CHANGELOG.md <<EOF_CHANGELOG
# Changelog

## ${NEW_VERSION} - ${TODAY}

### Automated release
- ${BUMP_TYPE^} release ${OLD_VERSION} -> ${NEW_VERSION}.

${CHANGELOG_BODY}
EOF_CHANGELOG

git add VERSION README.md CHANGELOG.md
git commit -m "release(v${NEW_VERSION}): ${BUMP_TYPE} bump"
git tag "v${NEW_VERSION}"

if [[ "${PUSH}" == "1" ]]; then
  git push origin main
  git push origin "v${NEW_VERSION}"
fi

if [[ -n "${PUBLISH_SLUG}" ]]; then
  clawhub publish "${ROOT_DIR}" \
    --slug "${PUBLISH_SLUG}" \
    --name "Mail Caduceus" \
    --version "${NEW_VERSION}" \
    --changelog "Automated ${BUMP_TYPE} release ${OLD_VERSION} -> ${NEW_VERSION}" \
    --tags latest
fi

echo "Released ${OLD_VERSION} -> ${NEW_VERSION}"
