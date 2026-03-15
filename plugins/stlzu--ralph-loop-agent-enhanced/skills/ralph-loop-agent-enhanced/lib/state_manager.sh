#!/bin/bash

# State Manager Module for Ralph Loop Agent
# Handles state persistence, checkpoint creation, and resumability features
# Version: 1.0.0

STATE_MANAGER_VERSION="1.0.0"

# State directories
STATE_DIR="${STATE_DIR:-$SCRIPT_DIR/state}"
STATE_CURRENT_FILE="$STATE_DIR/current_state.json"
STATE_HISTORY_DIR="$STATE_DIR/history"
STATE_CHECKPOINTS_DIR="$STATE_DIR/checkpoints"

# State tracking variables (using arrays instead of associative arrays)
STATE_KEYS=(
    "session_id"
    "loop_type"
    "total_iterations"
    "current_iteration"
    "start_time"
    "last_update"
    "status"
    "progress_percentage"
    "remaining_iterations"
    "estimated_completion"
    "callback_function"
    "config_hash"
    "checkpoint_count"
    "error_count"
    "retry_count"
)

STATE_VALUES=(
    ""
    ""
    "0"
    "0"
    "0"
    "0"
    "initialized"
    "0"
    "0"
    ""
    ""
    ""
    "0"
    "0"
    "0"
)

# Get state value index
state_manager_get_index() {
    local key="$1"
    case "$key" in
        "session_id") echo 0 ;;
        "loop_type") echo 1 ;;
        "total_iterations") echo 2 ;;
        "current_iteration") echo 3 ;;
        "start_time") echo 4 ;;
        "last_update") echo 5 ;;
        "status") echo 6 ;;
        "progress_percentage") echo 7 ;;
        "remaining_iterations") echo 8 ;;
        "estimated_completion") echo 9 ;;
        "callback_function") echo 10 ;;
        "config_hash") echo 11 ;;
        "checkpoint_count") echo 12 ;;
        "error_count") echo 13 ;;
        "retry_count") echo 14 ;;
        *) echo -1 ;;
    esac
}

# Get state value
state_manager_get() {
    local key="$1"
    local index=$(state_manager_get_index "$key")
    if [[ $index -ge 0 && $index -lt ${#STATE_KEYS[@]} ]]; then
        echo "${STATE_VALUES[$index]}"
    fi
}

# Set state value
state_manager_set() {
    local key="$1"
    local value="$2"
    local index=$(state_manager_get_index "$key")
    if [[ $index -ge 0 && $index -lt ${#STATE_KEYS[@]} ]]; then
        STATE_VALUES[$index]="$value"
        return 0
    fi
    return 1
}

# Initialize state directories
state_manager_init() {
    # Create state directories if they don't exist
    mkdir -p "$STATE_DIR"
    mkdir -p "$STATE_HISTORY_DIR"
    mkdir -p "$STATE_CHECKPOINTS_DIR"
    
    # Set default values
    state_manager_set "status" "initialized"
    state_manager_set "checkpoint_count" "0"
    state_manager_set "error_count" "0"
    state_manager_set "retry_count" "0"
    
    return 0
}

# Generate configuration hash for change detection
state_manager_generate_config_hash() {
    local loop_type=$(config_parser_get "loop_type")
    local iterations=$(config_parser_get "iterations")
    local delay_ms=$(config_parser_get "delay_ms")
    local retry_count=$(config_parser_get "retry_count")
    
    echo "${loop_type}:${iterations}:${delay_ms}:${retry_count}" | md5sum 2>/dev/null | cut -d' ' -f1 || echo "unknown"
}

# Save current state to file
state_manager_save_state() {
    local session_id=$(state_manager_get "session_id")
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    
    if [[ -z "$session_id" ]]; then
        echo "ERROR: Session ID not set, cannot save state" >&2
        return 1
    fi
    
    # Generate current state JSON
    local state_json='{
        "session_id": "'"$session_id"'",
        "timestamp": "'"$timestamp"'",
        "loop_type": "'$(state_manager_get "loop_type")'",
        "total_iterations": '$(state_manager_get "total_iterations")',
        "current_iteration": '$(state_manager_get "current_iteration")',
        "start_time": '$(state_manager_get "start_time")',
        "last_update": '$(state_manager_get "last_update")',
        "status": "'$(state_manager_get "status")'",
        "progress_percentage": '$(state_manager_get "progress_percentage")',
        "remaining_iterations": '$(state_manager_get "remaining_iterations")',
        "estimated_completion": "'$(state_manager_get "estimated_completion")'",
        "callback_function": "'$(state_manager_get "callback_function")'",
        "config_hash": "'$(state_manager_get "config_hash")'",
        "checkpoint_count": '$(state_manager_get "checkpoint_count")',
        "error_count": '$(state_manager_get "error_count")',
        "retry_count": '$(state_manager_get "retry_count")'
    }'
    
    # Save to current state file
    echo "$state_json" > "$STATE_CURRENT_FILE"
    
    # Save to history
    local history_file="$STATE_HISTORY_DIR/${session_id}_${timestamp}.json"
    echo "$state_json" > "$history_file"
    
    return 0
}

# Create checkpoint
state_manager_create_checkpoint() {
    local session_id=$(state_manager_get "session_id")
    local iteration=$(state_manager_get "current_iteration")
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    
    if [[ -z "$session_id" ]]; then
        echo "ERROR: Session ID not set, cannot create checkpoint" >&2
        return 1
    fi
    
    local checkpoint_file="$STATE_CHECKPOINTS_DIR/${session_id}_checkpoint_${iteration}_${timestamp}.json"
    
    # Copy current state to checkpoint
    cp "$STATE_CURRENT_FILE" "$checkpoint_file" 2>/dev/null || {
        # If current state doesn't exist, create fresh checkpoint
        local state_json='{
            "session_id": "'"$session_id"'",
            "timestamp": "'"$timestamp"'",
            "iteration": "'"$iteration"'",
            "checkpoint_type": "manual"
        }'
        echo "$state_json" > "$checkpoint_file"
    }
    
    # Update checkpoint count
    local current_count=$(state_manager_get "checkpoint_count")
    state_manager_set "checkpoint_count" "$((current_count + 1))"
    
    echo "Checkpoint created: $checkpoint_file"
    
    return 0
}

# Load state from file
state_manager_load_state() {
    local session_id="$1"
    
    if [[ -z "$session_id" ]]; then
        echo "ERROR: Session ID not provided" >&2
        return 1
    fi
    
    # Look for most recent state file
    local latest_file=$(ls -t "$STATE_HISTORY_DIR/${session_id}"*.json 2>/dev/null | head -1)
    
    if [[ -z "$latest_file" ]]; then
        echo "ERROR: No state found for session ID: $session_id" >&2
        return 1
    fi
    
    # Parse and load state from JSON
    if [[ -f "$latest_file" ]]; then
        # Extract values using simple text parsing (avoiding external dependencies)
        local state_content=$(cat "$latest_file")
        
        # Parse JSON values (basic approach for bash 3.2 compatibility)
        local loop_type=$(echo "$state_content" | grep -o '"loop_type": *"[^"]*"' | cut -d'"' -f4)
        local total_iterations=$(echo "$state_content" | grep -o '"total_iterations": *[0-9]*' | cut -d':' -f2 | tr -d ' ')
        local current_iteration=$(echo "$state_content" | grep -o '"current_iteration": *[0-9]*' | cut -d':' -f2 | tr -d ' ')
        local start_time=$(echo "$state_content" | grep -o '"start_time": *[0-9]*' | cut -d':' -f2 | tr -d ' ')
        local status=$(echo "$state_content" | grep -o '"status": *"[^"]*"' | cut -d'"' -f4)
        
        # Load values into state
        state_manager_set "session_id" "$session_id"
        state_manager_set "loop_type" "$loop_type"
        state_manager_set "total_iterations" "$total_iterations"
        state_manager_set "current_iteration" "$current_iteration"
        state_manager_set "start_time" "$start_time"
        state_manager_set "status" "$status"
        
        echo "State loaded successfully from: $latest_file"
        return 0
    else
        echo "ERROR: State file not found: $latest_file" >&2
        return 1
    fi
}

# List available sessions
state_manager_list_sessions() {
    echo "Available sessions:"
    ls "$STATE_HISTORY_DIR"/*.json 2>/dev/null | while read file; do
        local session_id=$(basename "$file" | sed 's/^\([^.]*\).*/\1/')
        local timestamp=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$file" 2>/dev/null || echo "unknown")
        local count=$(ls "$STATE_HISTORY_DIR/${session_id}"*.json 2>/dev/null | wc -l)
        echo "  $session_id - $timestamp ($count states)"
    done
}

# Clean old state files
state_manager_cleanup() {
    local max_days="${1:-7}"
    
    # Clean old history files
    find "$STATE_HISTORY_DIR" -name "*.json" -mtime +$max_days -delete 2>/dev/null
    
    # Clean old checkpoint files
    find "$STATE_CHECKPOINTS_DIR" -name "*.json" -mtime +$max_days -delete 2>/dev/null
    
    echo "State cleanup completed (keeping last $max_days days)"
    return 0
}

# Get state summary
state_manager_get_summary() {
    local session_id=$(state_manager_get "session_id")
    local status=$(state_manager_get "status")
    local current=$(state_manager_get "current_iteration")
    local total=$(state_manager_get "total_iterations")
    local checkpoints=$(state_manager_get "checkpoint_count")
    local errors=$(state_manager_get "error_count")
    
    echo "Session: $session_id"
    echo "Status: $status"
    echo "Progress: $current/$total"
    
    if [[ $total -gt 0 ]]; then
        local percentage=$(( current * 100 / total ))
        echo "Percentage: $percentage%"
    fi
    
    echo "Checkpoints: $checkpoints"
    echo "Errors: $errors"
}

# Export functions
export -f state_manager_init state_manager_save_state state_manager_load_state state_manager_create_checkpoint state_manager_list_sessions state_manager_cleanup state_manager_get_summary state_manager_get state_manager_set state_manager_get_index

# Export variables
export STATE_MANAGER_VERSION STATE_DIR STATE_CURRENT_FILE STATE_HISTORY_DIR STATE_CHECKPOINTS_DIR STATE_KEYS STATE_VALUES