#!/usr/bin/env bash
# Kontour Travel Planner — Quick Planning Script
# Usage: ./plan.sh "your trip description"
# Outputs structured trip context JSON by extracting dimensions from natural language.
# No API keys or external services required — runs entirely offline.

set -euo pipefail

QUERY="${1:-}"
if [ -z "$QUERY" ]; then
  echo "Usage: $0 \"<trip description>\""
  echo "Example: $0 \"2 weeks in Japan for a couple, mid-range budget, food and temples\""
  exit 1
fi

# Validate input boundary: capped length + strict character allowlist
if [ "${#QUERY}" -gt 280 ]; then
  echo "Error: Query too long (max 280 chars)." >&2
  exit 1
fi
if ! echo "$QUERY" | grep -qE '^[a-zA-Z0-9 ,.\-\/\$€£¥()!?'\''&]+$'; then
  echo "Error: Query contains unsupported characters." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
DEST_FILE="$SKILL_DIR/references/destinations.json"

# All processing done in Python with proper argument passing (no shell interpolation)
python3 - "$QUERY" "$DEST_FILE" << 'PYEOF'
import json, sys, re, os

query = sys.argv[1]
dest_file = sys.argv[2]

def extract_destination(text):
    m = re.search(r'\b(?:in|to|visit|visiting|explore|exploring)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text)
    if m:
        dest = re.sub(r'\s+[Ff]or$', '', m.group(1))
        return dest
    return ""

def extract_duration(text):
    m = re.search(r'(\d+)\s*(days?|weeks?|nights?)', text, re.IGNORECASE)
    if m:
        num = int(m.group(1))
        if 'week' in m.group(2).lower():
            return num * 7
        return num
    return None

def extract_travelers(text):
    t = text.lower()
    if 'solo' in t: return 1
    if 'couple' in t: return 2
    if 'family' in t: return 4
    m = re.search(r'(\d+)\s*(?:people|travelers|adults|persons)', t)
    if m: return int(m.group(1))
    return None

def extract_budget_tier(text):
    t = text.lower()
    if re.search(r'mid.range|moderate|comfort', t): return "mid"
    if re.search(r'budget|cheap|backpack', t): return "budget"
    if re.search(r'luxury|premium|high.end|splurge', t): return "luxury"
    return ""

def extract_interests(text):
    keywords = ['food', 'culinary', 'temple', 'culture', 'history', 'museum', 'art',
                'beach', 'adventure', 'hiking', 'nature', 'nightlife', 'shopping',
                'wellness', 'spa', 'photography', 'architecture', 'wine']
    t = text.lower()
    return [kw for kw in keywords if kw in t]

dest = extract_destination(query)
duration = extract_duration(query)
travelers = extract_travelers(query)
budget_tier = extract_budget_tier(query)
interests = extract_interests(query)

ctx = {}

# Look up destination in references
dest_data = None
if dest and os.path.isfile(dest_file):
    with open(dest_file) as f:
        dests = json.load(f)
    dest_lower = dest.lower()
    dest_data = next((d for d in dests if d['name'].lower() == dest_lower or d['country'].lower() == dest_lower), None)

if dest_data:
    ctx['destination'] = {
        'name': dest_data['name'],
        'country': dest_data['country'],
        'coordinates': dest_data['coordinates'],
        'currency': dest_data['currency'],
        'timezone': dest_data['timezone'],
        'avg_daily_cost_usd': dest_data['avg_daily_cost_usd']
    }
elif dest:
    ctx['destination'] = {'name': dest}

if duration:
    ctx['duration_days'] = duration
if travelers:
    ctx['travelers'] = {'adults': travelers}
if budget_tier:
    ctx['budget'] = {'tier': budget_tier}
    if dest_data:
        costs = dest_data.get('avg_daily_cost_usd', {})
        daily = costs.get(budget_tier, costs.get('mid'))
        if daily and duration:
            ctx['budget']['estimated_total'] = daily * duration * (travelers or 1)
            ctx['budget']['daily_per_person'] = daily
if interests:
    ctx['interests'] = interests

dims_complete = sum(1 for v in [dest, duration, travelers, budget_tier, interests] if v)
if dims_complete >= 6:
    ctx['planning_stage'] = 'refine'
elif dims_complete >= 4:
    ctx['planning_stage'] = 'develop'
else:
    ctx['planning_stage'] = 'discover'

ctx['open_decisions'] = []
if not dest: ctx['open_decisions'].append('destination')
if not duration: ctx['open_decisions'].append('dates/duration')
if not travelers: ctx['open_decisions'].append('travelers')
if not budget_tier: ctx['open_decisions'].append('budget')
if not interests: ctx['open_decisions'].append('interests')
ctx['open_decisions'].extend(['accommodation', 'transport', 'constraints'])

print(json.dumps(ctx, indent=2))
PYEOF
