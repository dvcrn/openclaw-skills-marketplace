#!/bin/bash
#
# test.sh - Run tests for release-guard skill
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo "🧪 Testing release-guard skill"
echo "=============================="

# Test 1: SKILL.md exists
echo "Test 1: Check SKILL.md exists..."
if [[ -f "$SKILL_DIR/SKILL.md" ]]; then
    echo "  ✅ PASS: SKILL.md exists"
else
    echo "  ❌ FAIL: SKILL.md not found"
    exit 1
fi

# Test 2: YAML frontmatter
echo "Test 2: Check YAML frontmatter..."
if grep -q "^---$" "$SKILL_DIR/SKILL.md"; then
    echo "  ✅ PASS: YAML frontmatter present"
else
    echo "  ❌ FAIL: Missing YAML frontmatter"
    exit 1
fi

# Test 3: Required fields
echo "Test 3: Check required fields..."
for field in "name:" "description:"; do
    if grep -q "^$field" "$SKILL_DIR/SKILL.md"; then
        echo "  ✅ PASS: Found $field"
    else
        echo "  ❌ FAIL: Missing $field"
        exit 1
    fi
done

# Test 4: References directory
echo "Test 4: Check references directory..."
if [[ -d "$SKILL_DIR/references" ]]; then
    echo "  ✅ PASS: references/ directory exists"
else
    echo "  ❌ FAIL: references/ directory not found"
    exit 1
fi

# Test 5: Checklist exists
echo "Test 5: Check checklist reference..."
if [[ -f "$SKILL_DIR/references/checklist.md" ]]; then
    echo "  ✅ PASS: checklist.md exists"
else
    echo "  ❌ FAIL: checklist.md not found"
    exit 1
fi

# Test 6: Severity matrix exists
echo "Test 6: Check severity matrix..."
if [[ -f "$SKILL_DIR/references/severity-matrix.md" ]]; then
    echo "  ✅ PASS: severity-matrix.md exists"
else
    echo "  ❌ FAIL: severity-matrix.md not found"
    exit 1
fi

# Test 7: release-check.sh exists
echo "Test 7: Check release-check.sh..."
if [[ -f "$SKILL_DIR/scripts/release-check.sh" ]]; then
    echo "  ✅ PASS: release-check.sh exists"
else
    echo "  ❌ FAIL: release-check.sh not found"
    exit 1
fi

# Test 8: Scripts are executable
echo "Test 8: Check scripts are executable..."
for script in "$SKILL_DIR/scripts/"*.sh; do
    if [[ -f "$script" ]]; then
        if [[ -x "$script" ]]; then
            echo "  ✅ PASS: $(basename "$script") is executable"
        else
            echo "  ⚠️  WARN: $(basename "$script") is not executable"
        fi
    fi
done

echo ""
echo "=============================="
echo "✅ All critical tests passed!"
