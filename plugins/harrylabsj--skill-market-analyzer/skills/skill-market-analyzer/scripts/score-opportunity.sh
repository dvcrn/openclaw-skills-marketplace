#!/bin/bash
#
# score-opportunity.sh - Score a skill opportunity
# Usage: ./score-opportunity.sh --name "idea" --demand 8 --competition 3 --effort 5
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="${MARKET_DATA_DIR:-$SKILL_DIR/data}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Parse arguments
NAME=""
DEMAND=""
COMPETITION=""
QUALITY_GAP=""
STRATEGIC_FIT=""
EFFORT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --name)
            NAME="$2"
            shift 2
            ;;
        --demand)
            DEMAND="$2"
            shift 2
            ;;
        --competition)
            COMPETITION="$2"
            shift 2
            ;;
        --quality-gap)
            QUALITY_GAP="$2"
            shift 2
            ;;
        --strategic-fit)
            STRATEGIC_FIT="$2"
            shift 2
            ;;
        --effort)
            EFFORT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate required inputs
if [[ -z "$NAME" || -z "$DEMAND" || -z "$COMPETITION" || -z "$EFFORT" ]]; then
    echo "Usage: $0 --name \"idea\" --demand <1-10> --competition <1-10> --effort <1-10>"
    echo "Optional: --quality-gap <1-10> --strategic-fit <1-10>"
    echo ""
    echo "Example: $0 --name \"AI Task Manager\" --demand 8 --competition 3 --effort 6"
    exit 1
fi

# Set defaults
QUALITY_GAP=${QUALITY_GAP:-5}
STRATEGIC_FIT=${STRATEGIC_FIT:-5}

# Validate ranges
for var in DEMAND COMPETITION QUALITY_GAP STRATEGIC_FIT EFFORT; do
    val=${!var}
    if [[ $val -lt 1 || $val -gt 10 ]]; then
        echo "Error: $var must be between 1 and 10"
        exit 1
    fi
done

# Calculate opportunity score
# Formula: (demand + (11-competition) + quality_gap + strategic_fit + (11-effort)) / 5
SCORE=$(echo "scale=1; ($DEMAND + (11 - $COMPETITION) + $QUALITY_GAP + $STRATEGIC_FIT + (11 - $EFFORT)) / 5" | bc)

# Determine recommendation
if (( $(echo "$SCORE >= 8" | bc -l) )); then
    RECOMMENDATION="Strong opportunity - proceed immediately"
    REC_COLOR=$GREEN
elif (( $(echo "$SCORE >= 6" | bc -l) )); then
    RECOMMENDATION="Good opportunity - consider pursuing"
    REC_COLOR=$YELLOW
else
    RECOMMENDATION="Weak opportunity - reconsider or pivot"
    REC_COLOR=$RED
fi

# Create data directory
mkdir -p "$DATA_DIR"

# Save score card
SCORE_FILE="$DATA_DIR/SCORE-$(echo "$NAME" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')-$(date +%Y%m%d).json"

cat > "$SCORE_FILE" << EOF
{
  "opportunity": "$NAME",
  "score": $SCORE,
  "generated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "breakdown": {
    "demand": $DEMAND,
    "competition": $COMPETITION,
    "quality_gap": $QUALITY_GAP,
    "strategic_fit": $STRATEGIC_FIT,
    "effort": $EFFORT
  },
  "calculations": {
    "demand_contribution": $DEMAND,
    "competition_contribution": $((11 - COMPETITION)),
    "quality_contribution": $QUALITY_GAP,
    "fit_contribution": $STRATEGIC_FIT,
    "effort_contribution": $((11 - EFFORT))
  },
  "recommendation": "$RECOMMENDATION"
}
EOF

echo ""
echo "================================"
echo "Opportunity Score Card"
echo "================================"
echo ""
echo -e "${BLUE}Opportunity:${NC} $NAME"
echo -e "${BLUE}Overall Score:${NC} ${REC_COLOR}$SCORE/10${NC}"
echo ""
echo "Breakdown:"
echo "  Demand:        $DEMAND/10"
echo "  Competition:   $COMPETITION/10 (inverted: $((11 - COMPETITION)))"
echo "  Quality Gap:   $QUALITY_GAP/10"
echo "  Strategic Fit: $STRATEGIC_FIT/10"
echo "  Effort:        $EFFORT/10 (inverted: $((11 - EFFORT)))"
echo ""
echo -e "${REC_COLOR}Recommendation: $RECOMMENDATION${NC}"
echo ""
echo -e "${BLUE}📄 Score card saved: $SCORE_FILE${NC}"
