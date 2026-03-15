#!/bin/bash
#
# release-check.sh - Main release guard check script
# Usage: ./release-check.sh <skill-directory> [--fix]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="${1:-.}"
FIX_MODE=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Parse arguments
if [[ "$2" == "--fix" ]]; then
    FIX_MODE=true
fi

# Validate skill directory exists
if [[ ! -d "$SKILL_DIR" ]]; then
    echo -e "${RED}❌ Error: Directory not found: $SKILL_DIR${NC}"
    exit 1
fi

SKILL_NAME=$(basename "$(cd "$SKILL_DIR" && pwd)")

echo -e "${BLUE}🛡️  Release Guard${NC}"
echo "=================="
echo "Skill: $SKILL_NAME"
echo "Mode: $([[ "$FIX_MODE" == true ]] && echo "Fix" || echo "Check")"
echo ""

# Counters
CRITICAL_PASSED=0
CRITICAL_FAILED=0
STANDARD_PASSED=0
STANDARD_FAILED=0
OPTIONAL_PASSED=0
OPTIONAL_FAILED=0

# Check function
check() {
    local level="$1"
    local name="$2"
    local condition="$3"
    
    if eval "$condition"; then
        echo -e "  ${GREEN}✅${NC} $name"
        case "$level" in
            critical) CRITICAL_PASSED=$((CRITICAL_PASSED + 1)) ;;
            standard) STANDARD_PASSED=$((STANDARD_PASSED + 1)) ;;
            optional) OPTIONAL_PASSED=$((OPTIONAL_PASSED + 1)) ;;
        esac
        return 0
    else
        echo -e "  ${RED}❌${NC} $name"
        case "$level" in
            critical) CRITICAL_FAILED=$((CRITICAL_FAILED + 1)) ;;
            standard) STANDARD_FAILED=$((STANDARD_FAILED + 1)) ;;
            optional) OPTIONAL_FAILED=$((OPTIONAL_FAILED + 1)) ;;
        esac
        return 1
    fi
}

warn() {
    local name="$1"
    echo -e "  ${YELLOW}⚠️${NC} $name"
    STANDARD_FAILED=$((STANDARD_FAILED + 1))
}

# ====================
# CRITICAL CHECKS
# ====================
echo -e "${BLUE}Critical Checks${NC}"

# C1: SKILL.md exists
if ! check critical "SKILL.md exists" "[[ -f '$SKILL_DIR/SKILL.md' ]]"; then
    echo -e "${RED}❌ CRITICAL FAILURE: Cannot proceed without SKILL.md${NC}"
    exit 1
fi

# C2: Valid YAML frontmatter
check critical "YAML frontmatter valid" "grep -q '^---$' '$SKILL_DIR/SKILL.md'"

# C3: Required fields
if [[ -f "$SKILL_DIR/SKILL.md" ]]; then
    check critical "Has 'name:' field" "grep -q '^name:' '$SKILL_DIR/SKILL.md'"
    check critical "Has 'description:' field" "grep -q '^description:' '$SKILL_DIR/SKILL.md'"
fi

# C4: No nested skills
NESTED=$(find "$SKILL_DIR" -mindepth 2 -name "SKILL.md" 2>/dev/null | wc -l)
if [[ $NESTED -eq 0 ]]; then
    echo -e "  ${GREEN}✅${NC} No nested skills"
    CRITICAL_PASSED=$((CRITICAL_PASSED + 1))
else
    echo -e "  ${RED}❌${NC} Found $NESTED nested SKILL.md files"
    CRITICAL_FAILED=$((CRITICAL_FAILED + 1))
fi

# C5: No secrets (basic check)
if [[ -f "$SKILL_DIR/SKILL.md" ]]; then
    # Look for potential secrets, excluding documentation mentions
    SECRETS=$(grep -iE "(api_key|apikey|password|secret|token)" "$SKILL_DIR/SKILL.md" 2>/dev/null | \
        grep -v "demo\|example\|placeholder\|No hardcoded\|No secrets\|documentation\|README\|checklist\|security\|scan" | \
        grep -vE "^\s*[-#*]\s*(No |Check |Scan )" | \
        wc -l | tr -d ' ')
    if [[ $SECRETS -eq 0 ]]; then
        echo -e "  ${GREEN}✅${NC} No obvious secrets detected"
        CRITICAL_PASSED=$((CRITICAL_PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠️${NC} Potential secrets detected ($SECRETS matches) - review manually"
        CRITICAL_FAILED=$((CRITICAL_FAILED + 1))
    fi
fi

echo ""

# ====================
# STANDARD CHECKS
# ====================
echo -e "${BLUE}Standard Checks${NC}"

# S1: References directory
if [[ -d "$SKILL_DIR/references" ]]; then
    echo -e "  ${GREEN}✅${NC} references/ directory exists"
    STANDARD_PASSED=$((STANDARD_PASSED + 1))
else
    warn "Missing references/ directory"
    if [[ "$FIX_MODE" == true ]]; then
        mkdir -p "$SKILL_DIR/references"
        echo -e "    ${GREEN}🔧 Fixed: Created references/${NC}"
    fi
fi

# S2: Scripts executable
if [[ -d "$SKILL_DIR/scripts" ]]; then
    NON_EXEC=$(find "$SKILL_DIR/scripts" -type f ! -perm +111 2>/dev/null | wc -l)
    if [[ $NON_EXEC -eq 0 ]]; then
        echo -e "  ${GREEN}✅${NC} All scripts executable"
        STANDARD_PASSED=$((STANDARD_PASSED + 1))
    else
        warn "$NON_EXEC scripts not executable"
        if [[ "$FIX_MODE" == true ]]; then
            chmod +x "$SKILL_DIR/scripts/"*.sh 2>/dev/null || true
            echo -e "    ${GREEN}🔧 Fixed: chmod +x scripts/*.sh${NC}"
        fi
    fi
else
    echo -e "  ${YELLOW}⚠️${NC} No scripts/ directory"
fi

# S3: Meaningful description
if [[ -f "$SKILL_DIR/SKILL.md" ]]; then
    DESC=$(grep "^description:" "$SKILL_DIR/SKILL.md" | cut -d: -f2- | tr -d '[:space:]')
    if [[ ${#DESC} -gt 20 ]]; then
        echo -e "  ${GREEN}✅${NC} Description is meaningful"
        STANDARD_PASSED=$((STANDARD_PASSED + 1))
    else
        warn "Description too short"
    fi
fi

# S4: Content length
if [[ -f "$SKILL_DIR/SKILL.md" ]]; then
    LINES=$(wc -l < "$SKILL_DIR/SKILL.md")
    if [[ $LINES -ge 50 ]]; then
        echo -e "  ${GREEN}✅${NC} Content length adequate ($LINES lines)"
        STANDARD_PASSED=$((STANDARD_PASSED + 1))
    else
        warn "Content seems short ($LINES lines)"
    fi
fi

# S5: Examples provided
if [[ -f "$SKILL_DIR/SKILL.md" ]]; then
    if grep -qE "(Example|example|trigger)" "$SKILL_DIR/SKILL.md"; then
        echo -e "  ${GREEN}✅${NC} Examples provided"
        STANDARD_PASSED=$((STANDARD_PASSED + 1))
    else
        warn "No examples found"
    fi
fi

echo ""

# ====================
# OPTIONAL CHECKS
# ====================
echo -e "${BLUE}Optional Checks${NC}"

# O1: README.md
if [[ -f "$SKILL_DIR/README.md" ]]; then
    echo -e "  ${GREEN}✅${NC} README.md exists"
    OPTIONAL_PASSED=$((OPTIONAL_PASSED + 1))
else
    echo -e "  ${YELLOW}ℹ️${NC} No README.md"
    OPTIONAL_FAILED=$((OPTIONAL_FAILED + 1))
fi

# O2: Test script
if [[ -f "$SKILL_DIR/scripts/test.sh" ]]; then
    echo -e "  ${GREEN}✅${NC} test.sh exists"
    OPTIONAL_PASSED=$((OPTIONAL_PASSED + 1))
else
    echo -e "  ${YELLOW}ℹ️${NC} No test.sh"
    OPTIONAL_FAILED=$((OPTIONAL_FAILED + 1))
fi

# O3: LICENSE
if [[ -f "$SKILL_DIR/LICENSE" ]]; then
    echo -e "  ${GREEN}✅${NC} LICENSE exists"
    OPTIONAL_PASSED=$((OPTIONAL_PASSED + 1))
else
    echo -e "  ${YELLOW}ℹ️${NC} No LICENSE"
    OPTIONAL_FAILED=$((OPTIONAL_FAILED + 1))
fi

echo ""
echo "=================="

# Calculate score
CRITICAL_TOTAL=$((CRITICAL_PASSED + CRITICAL_FAILED))
STANDARD_TOTAL=$((STANDARD_PASSED + STANDARD_FAILED))
OPTIONAL_TOTAL=$((OPTIONAL_PASSED + OPTIONAL_FAILED))

TOTAL_SCORE=$((CRITICAL_PASSED * 10 + STANDARD_PASSED * 5 + OPTIONAL_PASSED * 2))
MAX_SCORE=$((CRITICAL_TOTAL * 10 + STANDARD_TOTAL * 5 + OPTIONAL_TOTAL * 2))

if [[ $MAX_SCORE -gt 0 ]]; then
    PERCENTAGE=$((TOTAL_SCORE * 100 / MAX_SCORE))
else
    PERCENTAGE=0
fi

# Determine status
if [[ $CRITICAL_FAILED -gt 0 ]]; then
    STATUS="${RED}BLOCKED${NC}"
    EXIT_CODE=1
elif [[ $PERCENTAGE -ge 80 ]]; then
    STATUS="${GREEN}APPROVED${NC}"
    EXIT_CODE=0
elif [[ $PERCENTAGE -ge 60 ]]; then
    STATUS="${YELLOW}APPROVED_WITH_WARNINGS${NC}"
    EXIT_CODE=0
else
    STATUS="${RED}BLOCKED${NC}"
    EXIT_CODE=1
fi

echo -e "Score: ${BLUE}$PERCENTAGE%${NC} ($TOTAL_SCORE/$MAX_SCORE)"
echo -e "Status: $STATUS"
echo ""
echo "Summary:"
echo "  Critical: $CRITICAL_PASSED/$CRITICAL_TOTAL passed"
echo "  Standard: $STANDARD_PASSED/$STANDARD_TOTAL passed"
echo "  Optional: $OPTIONAL_PASSED/$OPTIONAL_TOTAL passed"

exit $EXIT_CODE
