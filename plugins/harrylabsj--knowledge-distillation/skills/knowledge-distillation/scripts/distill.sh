#!/bin/bash
#
# distill.sh - Run knowledge distillation on memory files
# Usage: ./distill.sh [memory-dir] [output-dir]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
MEMORY_DIR="${1:-/Users/jianghaidong/.openclaw/workspace/agents/main/memory}"
OUTPUT_DIR="${2:-$SKILL_DIR/dist}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔬 Knowledge Distillation${NC}"
echo "=========================="
echo "Memory source: $MEMORY_DIR"
echo "Output: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Generate dated filename
DATE=$(date +%Y-%m-%d)
OUTPUT_FILE="$OUTPUT_DIR/knowledge-distillation-$DATE.md"

# Check for existing files and increment if needed
if [[ -f "$OUTPUT_FILE" ]]; then
    COUNTER=1
    while [[ -f "${OUTPUT_FILE%.md}-$(printf "%02d" $COUNTER).md" ]]; do
        COUNTER=$((COUNTER + 1))
    done
    OUTPUT_FILE="${OUTPUT_FILE%.md}-$(printf "%02d" $COUNTER).md"
fi

echo -e "${GREEN}📄 Output file: $(basename "$OUTPUT_FILE")${NC}"
echo ""
echo "To complete distillation:"
echo "1. Review memory files in: $MEMORY_DIR"
echo "2. Extract new knowledge points and leads"
echo "3. Write results to: $OUTPUT_FILE"
echo ""
echo "Template location: $SKILL_DIR/references/output-templates.md"
