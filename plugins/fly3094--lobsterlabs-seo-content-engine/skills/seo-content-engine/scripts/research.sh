#!/bin/bash
# SEO Content Research Script
# Usage: ./research.sh "keyword" [num_results]

KEYWORD="$1"
NUM_RESULTS="${2:-10}"

if [ -z "$KEYWORD" ]; then
    echo "Usage: ./research.sh \"keyword\" [num_results]"
    exit 1
fi

echo "🔍 Researching: $KEYWORD"
echo "📊 Top $NUM_RESULTS results analysis"
echo ""

# Use SearXNG for privacy-focused search
SEARXNG_URL="${SEARXNG_URL:-http://localhost:8080}"

# Search and extract top results
curl -s "$SEARXNG_URL/search?q=$KEYWORD&format=json" | \
    python3 -c "
import sys, json
data = json.load(sys.stdin)
results = data.get('results', [])[:$NUM_RESULTS]
print('TOP RANKING CONTENT:')
print('=' * 50)
for i, r in enumerate(results, 1):
    print(f\"{i}. {r.get('title', 'N/A')}\")
    print(f\"   URL: {r.get('url', 'N/A')}\")
    print(f\"   Source: {r.get('engine', 'N/A')}\")
    print()
"

echo ""
echo "💡 Next steps:"
echo "   1. Analyze these pages for content gaps"
echo "   2. Generate outline based on common themes"
echo "   3. Write draft with unique angles"
