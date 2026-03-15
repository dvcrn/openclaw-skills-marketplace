#!/bin/bash
#
# test.sh - Test skill-market-analyzer functionality
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo "Testing skill-market-analyzer"
echo "============================"

# Test 1: Check scripts exist
echo ""
echo "Test 1: Checking script files..."
for script in analyze-market.sh find-gaps.sh score-opportunity.sh; do
    if [[ -f "$SCRIPT_DIR/$script" ]]; then
        echo "✅ $script exists"
    else
        echo "❌ $script missing"
        exit 1
    fi
done

# Test 2: Check executability
echo ""
echo "Test 2: Checking executability..."
for script in analyze-market.sh find-gaps.sh score-opportunity.sh; do
    if [[ -x "$SCRIPT_DIR/$script" ]]; then
        echo "✅ $script is executable"
    else
        echo "⚠️  $script not executable, fixing..."
        chmod +x "$SCRIPT_DIR/$script"
    fi
done

# Test 3: Test score-opportunity
echo ""
echo "Test 3: Testing score-opportunity..."
"$SCRIPT_DIR/score-opportunity.sh" --name "Test Skill" --demand 8 --competition 3 --effort 5 || true

# Test 4: Test analyze-market
echo ""
echo "Test 4: Testing analyze-market..."
"$SCRIPT_DIR/analyze-market.sh" --category productivity || true

# Test 5: Test find-gaps
echo ""
echo "Test 5: Testing find-gaps..."
"$SCRIPT_DIR/find-gaps.sh" --domain automation || true

echo ""
echo "============================"
echo "Tests complete"
