#!/bin/bash
# Sitemap generator - fetches and displays all docs by category
# Usage: sitemap.sh [--json]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

JSON=false
[[ "${OPENCLAW_SAGE_OUTPUT}" == "json" ]] && JSON=true
for arg in "$@"; do
  [ "$arg" = "--json" ] && JSON=true
done

SITEMAP_CACHE="${CACHE_DIR}/sitemap.txt"
SITEMAP_XML="${CACHE_DIR}/sitemap.xml"

# --- JSON output path ---
if $JSON; then
  if ! command -v python3 &>/dev/null; then
    echo '{"error": "python3 required for --json output"}' >&2
    exit 1
  fi

  # Ensure sitemap XML is available
  if ! is_cache_fresh "$SITEMAP_XML" "$SITEMAP_TTL"; then
    if check_online; then
      curl -sf --max-time 10 "${DOCS_BASE_URL}/sitemap.xml" -o "$SITEMAP_XML" 2>/dev/null
    else
      echo "Offline: cannot reach ${DOCS_BASE_URL}" >&2
      [ -f "$SITEMAP_XML" ] && echo "Using stale cached sitemap." >&2
    fi
  fi

  if [ -f "$SITEMAP_XML" ]; then
    python3 - "$SITEMAP_XML" "$DOCS_BASE_URL" <<'PYEOF'
import sys, json, xml.etree.ElementTree as ET
from collections import defaultdict

tree = ET.parse(sys.argv[1])
root = tree.getroot()
base_url = sys.argv[2]
ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

categories = defaultdict(list)
for url in root.findall('.//sm:url', ns):
    loc = url.find('sm:loc', ns)
    if loc is None:
        continue
    path = loc.text.replace(base_url + '/', '').strip('/')
    if not path:
        continue
    cat = path.split('/')[0]
    if cat:
        categories[cat].append(path)

result = [{'category': cat, 'paths': sorted(paths)}
          for cat, paths in sorted(categories.items())]
print(json.dumps(result, indent=2))
PYEOF
  else
    # Offline fallback — hardcoded known structure
    python3 - <<'PYEOF'
import json
result = [
  {"category": "start",      "paths": ["start/getting-started", "start/setup", "start/faq"]},
  {"category": "gateway",    "paths": ["gateway/configuration", "gateway/configuration-examples", "gateway/security", "gateway/health", "gateway/logging", "gateway/tailscale", "gateway/troubleshooting"]},
  {"category": "providers",  "paths": ["providers/discord", "providers/telegram", "providers/whatsapp", "providers/slack", "providers/signal", "providers/imessage", "providers/msteams", "providers/troubleshooting"]},
  {"category": "concepts",   "paths": ["concepts/agent", "concepts/sessions", "concepts/messages", "concepts/models", "concepts/queues", "concepts/streaming", "concepts/system-prompt"]},
  {"category": "tools",      "paths": ["tools/bash", "tools/browser", "tools/skills", "tools/reactions", "tools/subagents", "tools/thinking", "tools/browser-linux-troubleshooting"]},
  {"category": "automation", "paths": ["automation/cron-jobs", "automation/webhook", "automation/polling", "automation/gmail-pubsub"]},
  {"category": "cli",        "paths": ["cli/gateway", "cli/message", "cli/sandbox", "cli/update"]},
  {"category": "platforms",  "paths": ["platforms/linux", "platforms/macos", "platforms/windows", "platforms/ios", "platforms/android", "platforms/hetzner"]},
  {"category": "nodes",      "paths": ["nodes/camera", "nodes/audio", "nodes/images", "nodes/location", "nodes/voice"]},
  {"category": "web",        "paths": ["web/webchat", "web/dashboard"]},
  {"category": "install",    "paths": ["install/docker", "install/ansible", "install/bun", "install/nix", "install/updating"]},
  {"category": "reference",  "paths": ["reference/templates", "reference/rpc", "reference/device-models"]},
]
print(json.dumps(result, indent=2))
PYEOF
  fi
  exit 0
fi

# --- Human-readable output ---
if is_cache_fresh "$SITEMAP_CACHE" "$SITEMAP_TTL"; then
  cat "$SITEMAP_CACHE"
  exit 0
fi

echo "Fetching OpenClaw documentation sitemap..." >&2

_fetched=false
if ! check_online; then
  echo "Offline: cannot reach ${DOCS_BASE_URL}" >&2
  if [ -f "$SITEMAP_CACHE" ]; then
    echo "Using stale cached sitemap." >&2
    cat "$SITEMAP_CACHE"
    exit 0
  fi
elif curl -sf --max-time 10 "${DOCS_BASE_URL}/sitemap.xml" -o "$SITEMAP_XML" 2>/dev/null; then
  _fetched=true
fi

if $_fetched; then
  grep -o '<loc>[^<]*</loc>' "$SITEMAP_XML" \
    | sed 's/<[^>]*>//g' \
    | grep "docs\.openclaw\.ai/" \
    | sed "s|${DOCS_BASE_URL}/||" \
    | grep -v '^$' \
    | sort \
    | awk -F'/' '
        {
          cat = $1
          if (cat == "") next
          if (cat != prev_cat) {
            if (prev_cat != "") print ""
            print "📁 /" cat "/"
            prev_cat = cat
          }
          if (NF > 1) print "  - " $0
        }
      ' \
    | tee "$SITEMAP_CACHE"
else
  echo "Warning: Could not fetch live sitemap. Showing known categories." >&2
  {
    printf "📁 /start/\n  - start/getting-started\n  - start/setup\n  - start/faq\n\n"
    printf "📁 /gateway/\n  - gateway/configuration\n  - gateway/configuration-examples\n  - gateway/security\n  - gateway/health\n  - gateway/logging\n  - gateway/tailscale\n  - gateway/troubleshooting\n\n"
    printf "📁 /providers/\n  - providers/discord\n  - providers/telegram\n  - providers/whatsapp\n  - providers/slack\n  - providers/signal\n  - providers/imessage\n  - providers/msteams\n  - providers/troubleshooting\n\n"
    printf "📁 /concepts/\n  - concepts/agent\n  - concepts/sessions\n  - concepts/messages\n  - concepts/models\n  - concepts/queues\n  - concepts/streaming\n  - concepts/system-prompt\n\n"
    printf "📁 /tools/\n  - tools/bash\n  - tools/browser\n  - tools/skills\n  - tools/reactions\n  - tools/subagents\n  - tools/thinking\n  - tools/browser-linux-troubleshooting\n\n"
    printf "📁 /automation/\n  - automation/cron-jobs\n  - automation/webhook\n  - automation/polling\n  - automation/gmail-pubsub\n\n"
    printf "📁 /cli/\n  - cli/gateway\n  - cli/message\n  - cli/sandbox\n  - cli/update\n\n"
    printf "📁 /platforms/\n  - platforms/linux\n  - platforms/macos\n  - platforms/windows\n  - platforms/ios\n  - platforms/android\n  - platforms/hetzner\n\n"
    printf "📁 /nodes/\n  - nodes/camera\n  - nodes/audio\n  - nodes/images\n  - nodes/location\n  - nodes/voice\n\n"
    printf "📁 /web/\n  - web/webchat\n  - web/dashboard\n\n"
    printf "📁 /install/\n  - install/docker\n  - install/ansible\n  - install/bun\n  - install/nix\n  - install/updating\n\n"
    printf "📁 /reference/\n  - reference/templates\n  - reference/rpc\n  - reference/device-models\n"
  } | tee "$SITEMAP_CACHE"
fi
