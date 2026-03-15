#!/bin/bash

# EkyBot Telemetry Streaming Script
# Sends telemetry data to EkyBot platform

set -e

CONFIG_DIR="$HOME/.openclaw/ekybot-connector"
CONFIG_FILE="$CONFIG_DIR/config.json"

# Default values
WORKSPACE_ID=""
API_KEY=""
SINGLE_SHOT=true

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_detail() {
    echo -e "${BLUE}[DETAIL]${NC} $1"
}

usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --workspace-id <id>    Override workspace ID"
    echo "  --api-key <key>        Override API key"
    echo "  --continuous           Run continuously (default: single shot)"
    echo "  --interval <seconds>   Interval for continuous mode (default: 300)"
    echo "  --verbose              Verbose output"
    echo "  --help                Show this help"
}

# Parse command line arguments
INTERVAL=300
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --workspace-id)
            WORKSPACE_ID="$2"
            shift 2
            ;;
        --api-key)
            API_KEY="$2"
            shift 2
            ;;
        --continuous)
            SINGLE_SHOT=false
            shift
            ;;
        --interval)
            INTERVAL="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Load configuration if not provided via CLI
if [[ -z "$WORKSPACE_ID" ]] || [[ -z "$API_KEY" ]]; then
    if [[ ! -f "$CONFIG_FILE" ]]; then
        print_error "EkyBot connector not configured and no credentials provided."
        print_error "Run scripts/register_workspace.sh first or provide --workspace-id and --api-key"
        exit 1
    fi
    
    if [[ -z "$WORKSPACE_ID" ]]; then
        WORKSPACE_ID=$(cat "$CONFIG_FILE" | python3 -c "import sys, json; print(json.load(sys.stdin)['workspace_id'])")
    fi
    if [[ -z "$API_KEY" ]]; then
        API_KEY=$(cat "$CONFIG_FILE" | python3 -c "import sys, json; print(json.load(sys.stdin)['api_key'])")
    fi
    
    TELEMETRY_ENDPOINT=$(cat "$CONFIG_FILE" | python3 -c "import sys, json; print(json.load(sys.stdin)['endpoints']['telemetry'])")
else
    TELEMETRY_ENDPOINT="https://www.ekybot.com/api/workspaces/$WORKSPACE_ID/telemetry"
fi

if [[ -z "$WORKSPACE_ID" ]] || [[ -z "$API_KEY" ]]; then
    print_error "Invalid configuration. Missing workspace ID or API key."
    exit 1
fi

send_telemetry() {
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)
    
    if [[ "$VERBOSE" == "true" ]]; then
        print_status "📡 Collecting telemetry data..."
    fi
    
    # Collect OpenClaw status
    local gateway_running="false"
    local active_sessions=0
    local agent_count=0
    
    if command -v openclaw &> /dev/null; then
        local status_output=$(openclaw status --json 2>/dev/null || echo '{"error":"failed"}')
        gateway_running=$(echo "$status_output" | python3 -c "import sys, json; data = json.load(sys.stdin); print('true' if 'error' not in data and data.get('gateway', {}).get('running', False) else 'false')" 2>/dev/null)
        
        if [[ "$gateway_running" == "true" ]]; then
            local sessions_output=$(openclaw sessions --json 2>/dev/null || echo '[]')
            active_sessions=$(echo "$sessions_output" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)
            
            # Count configured agents
            if [[ -f "$HOME/.openclaw/openclaw.json" ]]; then
                agent_count=$(cat "$HOME/.openclaw/openclaw.json" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('agents', {}).get('list', [])))" 2>/dev/null || echo 0)
            fi
        fi
    fi
    
    # Collect system metrics
    local cpu_usage="null"
    local disk_usage="null"
    local memory_info="null"
    
    if command -v top &> /dev/null; then
        cpu_usage="\"$(top -l 1 -n 0 | grep "CPU usage" | awk '{print $3}' | sed 's/%//' || echo "unknown")\""
    fi
    
    local disk_pct=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//' 2>/dev/null || echo "")
    if [[ -n "$disk_pct" ]]; then
        disk_usage="\"${disk_pct}%\""
    fi
    
    # Collect cost/usage data (placeholder for now)
    local tokens_used=0
    local api_calls=0
    local estimated_cost=0
    
    # Try to get rough estimates from session files
    if [[ -d "$HOME/.openclaw/agents" ]]; then
        # Count total lines in session files as rough proxy for activity
        local session_lines=$(find "$HOME/.openclaw/agents" -name "*.jsonl" -type f -exec wc -l {} \; 2>/dev/null | awk '{sum += $1} END {print sum}' || echo 0)
        api_calls=$((session_lines / 2)) # Rough estimate: 2 lines per API call
        tokens_used=$((api_calls * 1000)) # Rough estimate: 1000 tokens per call
        estimated_cost=$(echo "scale=4; $tokens_used * 0.00001" | bc -l 2>/dev/null || echo "0.0000") # Rough estimate
    fi
    
    # Prepare telemetry payload (events array format)
    local telemetry_data=$(cat <<EOF
{
  "events": [
    {
      "timestamp": "$timestamp",
      "type": "health_ping", 
      "data": {
        "workspace": {
          "id": "$WORKSPACE_ID",
          "status": "$(if [[ "$gateway_running" == "true" ]]; then echo "active"; else echo "inactive"; fi)"
        },
        "gateway": {
          "running": $gateway_running,
          "version": "$(openclaw --version 2>/dev/null || echo "unknown")"
        },
        "agents": {
          "configured_count": $agent_count,
          "active_sessions": $active_sessions
        },
        "system": {
          "platform": "$(uname -s)",
          "hostname": "$(hostname)",
          "cpu_usage": $cpu_usage,
          "disk_usage": $disk_usage,
          "memory_info": $memory_info
        },
        "usage": {
          "tokens_used": $tokens_used,
          "api_calls": $api_calls,
          "estimated_cost_usd": $estimated_cost
        },
        "metadata": {
          "collector_version": "1.0.0",
          "collection_method": "bash_script"
        }
      }
    }
  ]
}
EOF
    )
    
    if [[ "$VERBOSE" == "true" ]]; then
        print_detail "Sending telemetry to: $TELEMETRY_ENDPOINT"
        print_detail "Payload size: $(echo "$telemetry_data" | wc -c) bytes"
    fi
    
    # Send telemetry data
    local response=$(curl -s -X POST "$TELEMETRY_ENDPOINT" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d "$telemetry_data")
    
    if [[ $? -eq 0 ]]; then
        local success=$(echo "$response" | python3 -c "import sys, json; print(str(json.load(sys.stdin).get('success', False)).lower())" 2>/dev/null || echo "false")
        if [[ "$success" == "true" ]]; then
            if [[ "$VERBOSE" == "true" ]]; then
                print_status "✅ Telemetry sent successfully ($timestamp)"
            fi
            return 0
        else
            print_warning "Telemetry sent but server returned error:"
            echo "$response"
            return 1
        fi
    else
        print_error "Failed to send telemetry to EkyBot"
        return 1
    fi
}

# Main execution
print_status "📡 EkyBot Telemetry Streaming"
print_detail "Workspace: $WORKSPACE_ID"

if [[ "$SINGLE_SHOT" == "true" ]]; then
    print_status "Sending single telemetry report..."
    send_telemetry
    print_status "Telemetry sent."
else
    print_status "Starting continuous telemetry streaming (interval: ${INTERVAL}s)"
    print_status "Press Ctrl+C to stop"
    
    # Set up signal handling for graceful shutdown
    trap 'print_status "Stopping telemetry streaming..."; exit 0' INT TERM
    
    while true; do
        send_telemetry
        sleep "$INTERVAL"
    done
fi