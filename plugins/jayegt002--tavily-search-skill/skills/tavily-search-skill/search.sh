#!/bin/bash

# Tavily Search Script - Enhanced with quota management
# Usage: 
#   ./search.sh "query" [max_results] [include_images]
#   ./search.sh --usage                    # Check quota usage
#   ./search.sh --toggle-paid-mode         # Toggle paid mode
#   ./search.sh --status                   # Show current status

# Priority to environment variable, error if not set
if [ -z "$TAVILY_API_KEY" ]; then
    echo "ERROR: TAVILY_API_KEY environment variable is not set" >&2
    echo "Please set it with: export TAVILY_API_KEY='your-api-key'" >&2
    echo "Get API Key from: https://app.tavily.com/api-keys" >&2
    exit 1
fi
echo "[INFO] Using API Key: ${TAVILY_API_KEY:0:10}..." >&2
TAVILY_ENDPOINT="https://api.tavily.com/search"
TAVILY_USAGE_ENDPOINT="https://api.tavily.com/usage"

# State file paths
STATE_DIR="/tmp/tavily_state"
STATE_FILE="$STATE_DIR/usage_state.json"
CONFIG_FILE="$STATE_DIR/config.json"
LAST_CHECK_FILE="$STATE_DIR/last_check.txt"

# Ensure state directory exists
mkdir -p "$STATE_DIR"

# Initialize config file
init_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        cat > "$CONFIG_FILE" << 'EOF'
{
  "paid_mode_enabled": false,
  "api_initialized_date": "2026-03-08",
  "free_quota_limit": 1000,
  "disable_when_paid_quota_zero": true
}
EOF
    fi
}

# Get config value
get_config() {
    local key="$1"
    if [ -f "$CONFIG_FILE" ]; then
        jq -r ".$key // empty" "$CONFIG_FILE" 2>/dev/null
    fi
}

# Set config value
set_config() {
    local key="$1"
    local value="$2"
    if [ -f "$CONFIG_FILE" ]; then
        jq ".$key = $value" "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
    fi
}

# Log function
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >&2
}

# Check if need to update quota (always true, real-time update)
should_check_quota() {
    return 0
}

# Update last check time
update_last_check() {
    date '+%Y-%m-%d %H:%M:%S' > "$LAST_CHECK_FILE"
}

# Query API quota
fetch_quota_from_api() {
    local response=$(curl -s -X GET "$TAVILY_USAGE_ENDPOINT" \
        -H "Authorization: Bearer $TAVILY_API_KEY" \
        --connect-timeout 10 \
        --max-time 15 2>/dev/null)
    
    if [ -n "$response" ] && echo "$response" | jq -e . > /dev/null 2>&1; then
        # Save to state file
        echo "$response" | jq -c '.' > "$STATE_FILE"
        update_last_check
        echo "$response"
        return 0
    else
        return 1
    fi
}

# Get current quota status (real-time)
get_quota_status() {
    local response=$(curl -s -X GET "$TAVILY_USAGE_ENDPOINT" \
        -H "Authorization: Bearer $TAVILY_API_KEY" \
        --connect-timeout 10 \
        --max-time 15 2>/dev/null)
    
    if [ -n "$response" ] && echo "$response" | jq -e . > /dev/null 2>&1; then
        echo "$response" | jq -c '.' > "$STATE_FILE" 2>/dev/null
        update_last_check
        echo "$response"
        return 0
    else
        # Fallback to local cache on API failure
        if [ -f "$STATE_FILE" ]; then
            cat "$STATE_FILE"
            return 0
        fi
        return 1
    fi
}

# Parse quota info
parse_quota_info() {
    local status="$1"
    local plan=$(echo "$status" | jq -r '.account.current_plan // "unknown"')
    local total_credits=$(echo "$status" | jq -r '.account.plan_limit // 1000')
    local used_credits=$(echo "$status" | jq -r '.account.plan_usage // 0')
    local paygo_usage=$(echo "$status" | jq -r '.account.paygo_usage // 0')
    local paygo_limit=$(echo "$status" | jq -r '.account.paygo_limit // 0')
    
    # Handle null values
    if [ "$total_credits" = "null" ]; then
        total_credits=1000
    fi
    if [ "$used_credits" = "null" ]; then
        used_credits=0
    fi
    if [ "$paygo_limit" = "null" ]; then
        paygo_limit=0
    fi
    if [ "$paygo_usage" = "null" ]; then
        paygo_usage=0
    fi
    
    local plan_remaining=$((total_credits - used_credits))
    local paygo_remaining=0
    
    if [ "$paygo_limit" != "0" ] && [ "$paygo_limit" != "null" ]; then
        paygo_remaining=$((paygo_limit - paygo_usage))
    fi
    
    local remaining=$((plan_remaining + paygo_remaining))
    
    echo "{\"plan\":\"$plan\",\"total\":$total_credits,\"used\":$used_credits,\"remaining\":$remaining,\"paygo_used\":$paygo_usage,\"paygo_limit\":$paygo_limit}"
}

# Validate quota before search
validate_quota() {
    init_config
    
    local status=$(get_quota_status)
    if [ -z "$status" ]; then
        log_message "ERROR" "Failed to get quota info"
        return 1
    fi
    
    local plan=$(echo "$status" | jq -r '.account.current_plan // "unknown"' | tr -d '\n')
    local total_credits=$(echo "$status" | jq -r '.account.plan_limit // 1000' | tr -d '\n')
    local used_credits=$(echo "$status" | jq -r '.account.plan_usage // 0' | tr -d '\n')
    local paygo_usage=$(echo "$status" | jq -r '.account.paygo_usage // 0' | tr -d '\n')
    local paygo_limit=$(echo "$status" | jq -r '.account.paygo_limit // 0' | tr -d '\n')
    
    [ "$total_credits" = "null" ] && total_credits=1000
    [ "$used_credits" = "null" ] && used_credits=0
    [ "$paygo_limit" = "null" ] && paygo_limit=0
    [ "$paygo_usage" = "null" ] && paygo_usage=0
    
    local remaining=$((total_credits - used_credits))
    
    local paid_mode=$(get_config "paid_mode_enabled")
    local disable_when_zero=$(get_config "disable_when_paid_quota_zero")
    
    log_message "INFO" "Current plan: $plan, remaining: $remaining"
    log_message "INFO" "Paid mode: $paid_mode, disable when zero: $disable_when_zero"
    
    local free_remaining=$remaining
    local paid_remaining=0
    
    if [ "$paygo_limit" != "0" ] && [ -n "$paygo_limit" ]; then
        if [ $remaining -gt 1000 ]; then
            free_remaining=1000
            paid_remaining=$((remaining - 1000))
        else
            paid_remaining=$((paygo_limit - paygo_usage))
            [ $paid_remaining -lt 0 ] && paid_remaining=0
        fi
    fi
    
    log_message "INFO" "Free quota: $free_remaining, Paid quota: $paid_remaining"
    
    if [ "$paid_mode" = "true" ] && [ "$disable_when_zero" = "true" ] && [ $paid_remaining -le 0 ]; then
        log_message "ERROR" "Paid quota exhausted and disable switch is ON"
        echo "{\"error\":\"Paid quota exhausted and disable switch is ON\",\"free_remaining\":$free_remaining,\"paid_remaining\":$paid_remaining,\"status\":\"disabled\"}"
        return 1
    fi
    
    if [ $remaining -le 0 ]; then
        log_message "ERROR" "Quota exhausted"
        echo "{\"error\":\"Quota exhausted\",\"remaining\":0,\"status\":\"disabled\"}"
        return 1
    fi
    
    if [ $remaining -lt 10 ]; then
        log_message "WARN" "Low quota: only $remaining credits left"
    elif [ $remaining -lt 100 ]; then
        log_message "WARN" "Quota running low: $remaining credits left"
    fi
    
    return 0
}

# Show usage info
show_usage() {
    init_config
    
    echo "=== Tavily API Quota Usage ==="
    echo ""
    
    local status=$(get_quota_status)
    if [ -n "$status" ]; then
        local plan=$(echo "$status" | jq -r '.account.current_plan // "unknown"')
        local total_credits=$(echo "$status" | jq -r '.account.plan_limit // 1000')
        local used_credits=$(echo "$status" | jq -r '.account.plan_usage // 0')
        
        [ "$total_credits" = "null" ] && total_credits=1000
        [ "$used_credits" = "null" ] && used_credits=0
        
        local remaining=$((total_credits - used_credits))
        
        echo "Plan: $plan"
        echo "Total: $total_credits credits"
        echo "Used: $used_credits credits"
        echo "Remaining: $remaining credits"
        echo ""
        
        if [ -f "$LAST_CHECK_FILE" ]; then
            echo "Last update: $(cat "$LAST_CHECK_FILE")"
        fi
    else
        echo "Failed to get quota info"
    fi
    
    echo ""
    echo "=== Config Status ==="
    local paid_mode=$(get_config "paid_mode_enabled")
    local disable_when_zero=$(get_config "disable_when_paid_quota_zero")
    local init_date=$(get_config "api_initialized_date")
    
    echo "Paid mode: $paid_mode"
    echo "Disable when zero: $disable_when_zero"
    echo "API initialized: $init_date"
}

# Toggle paid mode
toggle_paid_mode() {
    init_config
    
    local current=$(get_config "paid_mode_enabled")
    local new_value="false"
    
    if [ "$current" = "false" ] || [ "$current" = "" ]; then
        new_value="true"
    fi
    
    set_config "paid_mode_enabled" "$new_value"
    echo "Paid mode toggled to: $new_value"
}

# Show status
show_status() {
    init_config
    show_usage
}

# Perform search
perform_search() {
    local query="$1"
    local max_results="${2:-5}"
    local include_images="${3:-false}"
    local max_retries=2
    local retry_count=0
    
    # Validate quota first
    if ! validate_quota; then
        exit 1
    fi
    
    log_message "INFO" "Searching: '$query' (max_results=$max_results)"
    
    # Execute search with retry
    while [ $retry_count -le $max_retries ]; do
        if [ $retry_count -gt 0 ]; then
            log_message "INFO" "Retry $retry_count..."
            sleep 1
        fi
        
        local response=$(curl -s -w "\n%{http_code}" -X POST "$TAVILY_ENDPOINT" \
            -H "Content-Type: application/json" \
            --connect-timeout 10 \
            --max-time 30 \
            -d "{
                \"api_key\": \"$TAVILY_API_KEY\",
                \"query\": \"$query\",
                \"max_results\": $max_results,
                \"include_images\": $include_images
            }" 2>/dev/null)
        
        local http_code=$(echo "$response" | tail -n1)
        local body=$(echo "$response" | sed '$d')
        
        log_message "DEBUG" "HTTP status: $http_code"
        
        if [ "$http_code" = "200" ]; then
            if echo "$body" | jq -e . > /dev/null 2>&1; then
                if echo "$body" | jq -e '.error' > /dev/null 2>&1; then
                    local error_msg=$(echo "$body" | jq -r '.error')
                    log_message "ERROR" "API error: $error_msg"
                    retry_count=$((retry_count + 1))
                    continue
                fi
                
                local quota_status=$(get_quota_status)
                local quota_info=$(parse_quota_info "$quota_status")
                local remaining=$(echo "$quota_info" | jq -r '.remaining')
                
                log_message "INFO" "Search success | Used: 1 credit | Remaining: $remaining credits"
                
                echo "$body" | jq --argjson quota "$quota_info" '{query: .query, results: .results, quota_info: $quota, response_time: .response_time}'
                exit 0
            else
                log_message "ERROR" "Invalid JSON response"
                retry_count=$((retry_count + 1))
                continue
            fi
        elif [ "$http_code" = "429" ]; then
            log_message "ERROR" "Rate limit (429)"
            retry_count=$((retry_count + 1))
            sleep 2
            continue
        elif [ "$http_code" = "401" ] || [ "$http_code" = "403" ]; then
            log_message "ERROR" "API Key invalid ($http_code)"
            echo "{\"error\":\"API Key invalid\",\"http_code\":$http_code,\"status\":\"failed\"}"
            exit 1
        else
            log_message "ERROR" "HTTP error: $http_code"
            retry_count=$((retry_count + 1))
            continue
        fi
    done
    
    log_message "FATAL" "All retries failed"
    echo "{\"error\":\"All retries failed\",\"status\":\"failed\",\"retry_count\":$retry_count}"
    exit 1
}

# Main logic
main() {
    # Check dependencies
    if ! command -v curl &> /dev/null; then
        log_message "ERROR" "curl is not installed"
        echo '{"error":"curl is not installed","status":"failed"}'
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        log_message "ERROR" "jq is not installed"
        echo '{"error":"jq is not installed","status":"failed"}'
        exit 1
    fi
    
    # Handle arguments
    case "$1" in
        --usage)
            show_usage
            ;;
        --toggle-paid-mode)
            toggle_paid_mode
            ;;
        --status)
            show_status
            ;;
        "")
            echo "Usage:"
            echo "  $0 \"search query\" [max_results] [include_images:true/false]"
            echo "  $0 --usage                              # Check quota usage"
            echo "  $0 --toggle-paid-mode                   # Toggle paid mode"
            echo "  $0 --status                             # Show current status"
            echo ""
            echo "Examples:"
            echo "  $0 \"OpenClaw\" 5"
            exit 1
            ;;
        *)
            perform_search "$1" "$2" "$3"
            ;;
    esac
}

main "$@"