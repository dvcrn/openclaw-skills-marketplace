#!/bin/bash
#
# add-insight.sh - Add a new insight
# Usage: ./add-insight.sh "Insight content" --tags tag1,tag2 --priority high
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="${INSIGHT_DATA_DIR:-$SKILL_DIR/data}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Parse arguments
CONTENT=""
TAGS=""
PRIORITY="medium"
SOURCE="session"

while [[ $# -gt 0 ]]; do
    case $1 in
        --tags)
            TAGS="$2"
            shift 2
            ;;
        --priority)
            PRIORITY="$2"
            shift 2
            ;;
        --source)
            SOURCE="$2"
            shift 2
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            CONTENT="$1"
            shift
            ;;
    esac
done

if [[ -z "$CONTENT" ]]; then
    echo "Usage: $0 \"Insight content\" [--tags tag1,tag2] [--priority high|medium|low] [--source source]"
    exit 1
fi

# Create data directory
mkdir -p "$DATA_DIR"

# Generate ID
DATE=$(date +%Y%m%d)
COUNTER=1
while [[ -f "$DATA_DIR/INS-${DATE}-$(printf "%03d" $COUNTER).md" ]]; do
    COUNTER=$((COUNTER + 1))
done
INSIGHT_ID="INS-${DATE}-$(printf "%03d" $COUNTER)"

# Create insight file
cat > "$DATA_DIR/$INSIGHT_ID.md" << EOF
---
id: $INSIGHT_ID
content: "$CONTENT"
source: $SOURCE
tags: ${TAGS:-general}
priority: $PRIORITY
status: active
created: $(date -u +%Y-%m-%dT%H:%M:%SZ)
---

# $INSIGHT_ID

## Content
$CONTENT

## Metadata
- **Source**: $SOURCE
- **Tags**: ${TAGS:-general}
- **Priority**: $PRIORITY
- **Status**: active
- **Created**: $(date -u +%Y-%m-%dT%H:%M:%SZ)
EOF

echo -e "${GREEN}✅ Insight added: $INSIGHT_ID${NC}"
echo -e "${BLUE}📄 Location: $DATA_DIR/$INSIGHT_ID.md${NC}"
