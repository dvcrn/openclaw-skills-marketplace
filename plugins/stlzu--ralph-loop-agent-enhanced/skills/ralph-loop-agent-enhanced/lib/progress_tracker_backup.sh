#!/bin/bash

# Progress Tracker Module for Ralph Loop Agent
# Provides real-time progress tracking with percentage, ETA, and statistics
# Version: 1.0.0

PROGRESS_TRACKER_VERSION="1.0.0"
PROGRESS_ENABLED="${PROGRESS_ENABLED:-true}"
PROGRESS_FORMAT="${PROGRESS_FORMAT:-percentage}"
PROGRESS_UPDATE_INTERVAL="${PROGRESS_UPDATE_INTERVAL:-0.1}"

# Progress tracking variables (using arrays instead of associative arrays)
PROGRESS_KEYS=(
    "total"
    "current"
    "start_time"
    "last_update"
    "eta_seconds"
    "remaining_iterations"
    "speed_iterations_per_second"
    "estimated_completion"
)

PROGRESS_VALUES=(
    "0"
    "0"
    "0"
    "0"
    "0"
    "0"
    "0"
    ""
)

# Progress display formatting
PROGRESS_BAR_WIDTH="${PROGRESS_BAR_WIDTH:-50}"
PROGRESS_BAR_CHAR="${PROGRESS_BAR_CHAR:-#}"
PROGRESS_EMPTY_CHAR="${PROGRESS_EMPTY_CHAR:--}"

# Get progress value by key
progress_tracker_get_index() {
    local key="$1"
    case "$key" in
        "total") echo 0 ;;
        "current") echo 1 ;;
        "start_time") echo 2 ;;
        "last_update") echo 3 ;;
        "eta_seconds") echo 4 ;;
        "remaining_iterations") echo 5 ;;
        "speed_iterations_per_second") echo 6 ;;
        "estimated_completion") echo 7 ;;
        *) echo -1 ;;
    esac
}

# Get progress value
progress_tracker_get() {
    local key="$1"
    local index=$(progress_tracker_get_index "$key")
    if [[ $index -ge 0 && $index -lt ${#PROGRESS_KEYS[@]} ]]; then
        echo "${PROGRESS_VALUES[$index]}"
    fi
}

# Set progress value
progress_tracker_set() {
    local key="$1"
    local value="$2"
    local index=$(progress_tracker_get_index "$key")
    if [[ $index -ge 0 && $index -lt ${#PROGRESS_KEYS[@]} ]]; then
        PROGRESS_VALUES[$index]="$value"
        return 0
    fi
    return 1
}

# Initialize progress tracker
progress_tracker_init() {
    local total="$1"
    
    if [[ ! "$total" =~ ^[0-9]+$ ]] || [[ $total -eq 0 ]]; then
        echo "ERROR: Invalid total count for progress tracking: $total" >&2
        return 1
    fi
    
    progress_tracker_set "total" "$total"
    progress_tracker_set "current" "0"
    progress_tracker_set "start_time" "$(date +%s)"
    progress_tracker_set "last_update" "$(date +%s)"
    
    if [[ "$PROGRESS_ENABLED" == "true" ]]; then
        # progress_tracker_display  # Comment out to avoid display during init
    fi
    
    return 0
}

# Update progress
progress_tracker_update() {
    local current="$1"
    local force_update="${2:-false}"
    
    if [[ ! "$current" =~ ^[0-9]+$ ]]; then
        echo "ERROR: Invalid current progress: $current" >&2
        return 1
    fi
    
    # Update current progress
    progress_tracker_set "current" "$current"
    local total=$(progress_tracker_get "total")
    progress_tracker_set "remaining_iterations" $((total - current))
    
    # Calculate statistics
    local current_time=$(date +%s)
    local start_time=$(progress_tracker_get "start_time")
    local elapsed_seconds=$((current_time - start_time))
    
    if [[ $elapsed_seconds -gt 0 && $current -gt 0 ]]; then
        # Calculate speed (iterations per second)
        local speed=$(echo "scale=2; $current / $elapsed_seconds" | bc -l 2>/dev/null || echo "0")
        progress_tracker_set "speed_iterations_per_second" "$speed"
        
        # Calculate ETA
        if [[ $current -lt $total ]]; then
            local avg_time_per_iteration=$(echo "scale=2; $elapsed_seconds / $current" | bc -l 2>/dev/null || echo "0")
            local eta_seconds=$(echo "scale=0; $((total - current)) * $avg_time_per_iteration" | bc -l 2>/dev/null || echo "0")
            progress_tracker_set "eta_seconds" "$eta_seconds"
            
            # Calculate estimated completion time
            if command -v date >/dev/null 2>&1; then
                local completion_time=$((current_time + eta_seconds))
                local estimated_completion=$(date -d "@$completion_time" +"%H:%M:%S" 2>/dev/null || echo "N/A")
            else
                local estimated_completion="Calculating..."
            fi
            progress_tracker_set "estimated_completion" "$estimated_completion"
        else
            progress_tracker_set "eta_seconds" "0"
            progress_tracker_set "estimated_completion" "Complete"
        fi
    else
        progress_tracker_set "speed_iterations_per_second" "0"
        progress_tracker_set "eta_seconds" "0"
        progress_tracker_set "estimated_completion" "Calculating..."
    fi
    
    # Update display
    local last_update=$(progress_tracker_get "last_update")
    local time_since_update=$((current_time - last_update))
    
    # Convert update interval to seconds (handle decimal)
    local update_interval_seconds=$(echo "$PROGRESS_UPDATE_INTERVAL" | bc -l 2>/dev/null || echo "1")
    
    if [[ "$force_update" == "true" ]] || [[ $time_since_update -ge $(echo "$update_interval_seconds" | bc -l 2>/dev/null || echo "1") ]]; then
        if [[ "$PROGRESS_ENABLED" == "true" ]]; then
            progress_tracker_display
        fi
        progress_tracker_set "last_update" "$current_time"
    fi
    
    return 0
}

# Format time duration
progress_tracker_format_duration() {
    local seconds="$1"
    local hours=$((seconds / 3600))
    local minutes=$(( (seconds % 3600) / 60 ))
    local secs=$((seconds % 60))
    
    printf "%02d:%02d:%02d" $hours $minutes $secs
}

# Display progress
progress_tracker_display() {
    local current=$(progress_tracker_get "current")
    local total=$(progress_tracker_get "total")
    local percentage=$((current * 100 / total))
    local eta_seconds=$(progress_tracker_get "eta_seconds")
    local eta_formatted=$(progress_tracker_get "estimated_completion")
    local speed=$(progress_tracker_get "speed_iterations_per_second")
    
    case "$PROGRESS_FORMAT" in
        "percentage")
            printf "\rProgress: %d%% (%d/%d) [ETA: %s] Speed: %.2f iter/sec" \
                "$percentage" "$current" "$total" "$eta_formatted" "$speed"
            ;;
        "bar")
            local filled=$((PROGRESS_BAR_WIDTH * percentage / 100))
            local empty=$((PROGRESS_BAR_WIDTH - filled))
            local bar=$(printf "%*s" $filled | tr ' ' "$PROGRESS_BAR_CHAR")
            local empty_bar=$(printf "%*s" $empty | tr ' ' "$PROGRESS_EMPTY_CHAR")
            printf "\r[%s%s] %d%% (%d/%d) [ETA: %s]" \
                "$bar" "$empty_bar" "$percentage" "$current" "$total" "$eta_formatted"
            ;;
        "detailed")
            printf "\rProgress: %d%% (%d/%d) | ETA: %s | Speed: %.2f iter/sec | Remaining: %d" \
                "$percentage" "$current" "$total" "$eta_formatted" "$speed" "$(progress_tracker_get 'remaining_iterations')"
            ;;
        "simple")
            printf "\r%d/%d" "$current" "$total"
            ;;
    esac
    
    # Move to beginning of line and don't add newline
    printf "\r"
    
    # Complete on 100%
    if [[ $percentage -eq 100 ]]; then
        printf "\n"
    else
        # Clear to end of line
        printf "%*s" 80 " "
        printf "\r"
    fi
    
    return 0
}

# Complete progress tracking
progress_tracker_complete() {
    local final_percentage=$(( $(progress_tracker_get "current") * 100 / $(progress_tracker_get "total") ))
    local start_time=$(progress_tracker_get "start_time")
    local total_time=$(( $(date +%s) - start_time ))
    local speed=$(progress_tracker_get "speed_iterations_per_second")
    
    if [[ "$PROGRESS_ENABLED" == "true" ]]; then
        local duration_formatted=$(progress_tracker_format_duration "$total_time")
        printf "\rProgress: %d%% (%d/%d) | Total time: %s | Speed: %.2f iter/sec\n" \
            "$final_percentage" "$(progress_tracker_get 'current')" "$(progress_tracker_get 'total')" "$duration_formatted" "$speed"
    fi
    
    return 0
}

# Get progress statistics
progress_tracker_get_stats() {
    local current=$(progress_tracker_get "current")
    local total=$(progress_tracker_get "total")
    
    echo "total=$total"
    echo "current=$current"
    echo "percentage=$((current * 100 / total))"
    echo "start_time=$(progress_tracker_get 'start_time')"
    echo "eta_seconds=$(progress_tracker_get 'eta_seconds')"
    echo "remaining_iterations=$(progress_tracker_get 'remaining_iterations')"
    echo "speed_iterations_per_second=$(progress_tracker_get 'speed_iterations_per_second')"
    echo "estimated_completion=$(progress_tracker_get 'estimated_completion')"
    echo "total_time=$(( $(date +%s) - $(progress_tracker_get 'start_time') ))"
}

# Reset progress tracker
progress_tracker_reset() {
    progress_tracker_set "total" "0"
    progress_tracker_set "current" "0"
    progress_tracker_set "start_time" "0"
    progress_tracker_set "last_update" "0"
    progress_tracker_set "eta_seconds" "0"
    progress_tracker_set "remaining_iterations" "0"
    progress_tracker_set "speed_iterations_per_second" "0"
    progress_tracker_set "estimated_completion" ""
    
    return 0
}

# Cleanup progress tracker
progress_tracker_cleanup() {
    if [[ "$PROGRESS_ENABLED" == "true" ]]; then
        # Move to next line after progress
        echo ""
    fi
    
    return 0
}

# Export functions
export -f progress_tracker_init progress_tracker_update progress_tracker_display progress_tracker_complete progress_tracker_get_stats progress_tracker_reset progress_tracker_cleanup progress_tracker_get progress_tracker_set progress_tracker_get_index progress_tracker_format_duration

# Export variables
export PROGRESS_TRACKER_VERSION PROGRESS_ENABLED PROGRESS_FORMAT PROGRESS_UPDATE_INTERVAL PROGRESS_KEYS PROGRESS_VALUES PROGRESS_BAR_WIDTH PROGRESS_BAR_CHAR PROGRESS_EMPTY_CHAR