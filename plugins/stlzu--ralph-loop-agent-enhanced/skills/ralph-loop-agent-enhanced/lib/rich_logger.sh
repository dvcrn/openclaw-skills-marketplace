#!/bin/bash

# Rich Logger Module for Ralph Loop Agent
# Provides advanced logging capabilities with file output, JSON format, rotation, and compression
# Version: 1.0.0

# Configuration variables
LOG_RICH_VERSION="1.0.0"
LOG_RICH_ENABLED="${LOG_RICH_ENABLED:-false}"
LOG_RICH_FILE="${LOG_RICH_FILE:-./ralph-loop.log}"
LOG_RICH_FORMAT="${LOG_RICH_FORMAT:-json}"
LOG_RICH_ROTATION_SIZE="${LOG_RICH_ROTATION_SIZE:-10485760}"  # 10MB
LOG_RICH_ROTATION_COUNT="${LOG_RICH_ROTATION_COUNT:-5}"
LOG_RICH_RETENTION_DAYS="${LOG_RICH_RETENTION_DAYS:-7}"
LOG_RICH_COMPRESSION="${LOG_RICH_COMPRESSION:-true}"

# Session tracking variables
LOG_RICH_SESSION_ID=""
LOG_RICH_SESSION_START=""

# Initialize rich logger
rich_logger_init() {
    # Generate session ID if not exists
    if [[ -z "$LOG_RICH_SESSION_ID" ]]; then
        LOG_RICH_SESSION_ID=$(date +"%Y%m%d_%H%M%S_%N_%s")
        LOG_RICH_SESSION_START=$(date +"%Y-%m-%dT%H:%M:%S%z")
    fi
    
    # Create log directory if it doesn't exist
    local log_dir=$(dirname "$LOG_RICH_FILE")
    if [[ ! -d "$log_dir" ]]; then
        mkdir -p "$log_dir" || {
            echo "ERROR: Cannot create log directory: $log_dir" >&2
            return 1
        }
    fi
    
    # Log session start
    rich_logger_log "SESSION_START" "session_id" "$LOG_RICH_SESSION_ID" "session_start" "$LOG_RICH_SESSION_START"
    
    return 0
}

# Log with rich formatting
rich_logger_log() {
    local level="$1"
    local message="$2"
    shift 2
    
    # Only log if rich logging is enabled
    [[ "$LOG_RICH_ENABLED" != "true" ]] && return 0
    
    # Prepare timestamp
    local timestamp=$(date +"%Y-%m-%dT%H:%M:%S%z")
    
    # Prepare additional fields
    local additional_fields=""
    while [[ $# -gt 0 ]]; do
        local key="$1"
        local value="$2"
        additional_fields+="$key\":\"$value\","
        shift 2
    done
    
    # Create JSON log entry
    local json_entry="{"
    json_entry+="\"timestamp\":\"$timestamp\","
    json_entry+="\"level\":\"$level\","
    json_entry+="\"message\":\"$message\","
    json_entry+="\"session_id\":\"$LOG_RICH_SESSION_ID\","
    if [[ -n "$additional_fields" ]]; then
        json_entry+="${additional_fields%,},"
    fi
    json_entry+="\"hostname\":\"$(hostname)\","
    json_entry+="\"pid\":$$"
    json_entry+="}"
    
    # Write to log file
    if [[ "$LOG_RICH_FORMAT" == "json" ]]; then
        echo "$json_entry" >> "$LOG_RICH_FILE"
    else
        # Fallback to plain text format
        echo "[$timestamp] [$level] [$LOG_RICH_SESSION_ID] $message" >> "$LOG_RICH_FILE"
    fi
    
    # Check for rotation
    rich_logger_check_rotation
    
    return 0
}

# Check if log rotation is needed
rich_logger_check_rotation() {
    [[ ! -f "$LOG_RICH_FILE" ]] && return 0
    
    local file_size=$(stat -f%z "$LOG_RICH_FILE" 2>/dev/null || stat -c%s "$LOG_RICH_FILE" 2>/dev/null)
    
    if [[ $file_size -gt $LOG_RICH_ROTATION_SIZE ]]; then
        rich_logger_rotate
    fi
}

# Rotate log files
rich_logger_rotate() {
    # Get current timestamp for rotation
    local rotation_time=$(date +"%Y%m%d_%H%M%S")
    
    # Compress and rotate existing logs
    for i in $(seq $((LOG_RICH_ROTATION_COUNT-1)) -1 1); do
        local old_file="${LOG_RICH_FILE}.${i}"
        local new_file="${LOG_RICH_FILE}.${i+1}"
        
        if [[ -f "$old_file" ]]; then
            if [[ "$LOG_RICH_COMPRESSION" == "true" ]]; then
                mv "$old_file" "${new_file}.gz" 2>/dev/null || mv "$old_file" "$new_file"
            else
                mv "$old_file" "$new_file"
            fi
        fi
    done
    
    # Rotate current log
    if [[ "$LOG_RICH_COMPRESSION" == "true" ]]; then
        gzip -f "$LOG_RICH_FILE" && mv "${LOG_RICH_FILE}.gz" "${LOG_RICH_FILE}.1" 2>/dev/null || true
    else
        mv "$LOG_RICH_FILE" "${LOG_RICH_FILE}.1" 2>/dev/null || true
    fi
    
    # Create new log file
    touch "$LOG_RICH_FILE"
    
    rich_logger_log "LOG_ROTATION" "Log file rotated" "rotation_time" "$rotation_time" "rotation_size" "$LOG_RICH_ROTATION_SIZE"
}

# Clean up old log files
rich_logger_cleanup() {
    local find_cmd="find \"$(dirname "$LOG_RICH_FILE")\" -name \"$(basename "$LOG_RICH_FILE")*\" -mtime +$LOG_RICH_RETENTION_DAYS"
    
    if [[ "$LOG_RICH_COMPRESSION" == "true" ]]; then
        find_cmd+=" -name \"*.gz\""
    else
        find_cmd+=" ! -name \"*.gz\""
    fi
    
    eval "$find_cmd" -delete 2>/dev/null || true
}

# Log summary at end of session
rich_logger_summary() {
    local session_end=$(date +"%Y-%m-%dT%H:%M:%S%z")
    local duration_seconds=$(($(date +%s) - $(date -j -f "%Y-%m-%dT%H:%M:%S%z" "$LOG_RICH_SESSION_START" +%s)))
    local duration_formatted=$(printf "%02d:%02d:%02d" $((duration_seconds/3600)) $(((duration_seconds%3600)/60)) $((duration_seconds%60)))
    
    rich_logger_log "SESSION_END" "Session completed" "session_id" "$LOG_RICH_SESSION_ID" "session_end" "$session_end" "duration_seconds" "$duration_seconds" "duration_formatted" "$duration_formatted"
    
    # Clean up old logs
    rich_logger_cleanup
    
    return 0
}

# Set up exit trap for cleanup
rich_logger_setup_trap() {
    trap 'rich_logger_summary' EXIT
    trap 'rich_logger_summary; exit 1' INT TERM
    
    return 0
}

# Configuration validation
rich_logger_validate_config() {
    # Check required variables
    [[ -z "$LOG_RICH_FILE" ]] && { echo "ERROR: LOG_RICH_FILE not set" >&2; return 1; }
    [[ "$LOG_RICH_ENABLED" != "true" ]] && return 0
    
    # Validate numeric values
    [[ ! "$LOG_RICH_ROTATION_SIZE" =~ ^[0-9]+$ ]] && { echo "ERROR: LOG_RICH_ROTATION_SIZE must be numeric" >&2; return 1; }
    [[ ! "$LOG_RICH_ROTATION_COUNT" =~ ^[0-9]+$ ]] && { echo "ERROR: LOG_RICH_ROTATION_COUNT must be numeric" >&2; return 1; }
    [[ ! "$LOG_RICH_RETENTION_DAYS" =~ ^[0-9]+$ ]] && { echo "ERROR: LOG_RICH_RETENTION_DAYS must be numeric" >&2; return 1; }
    
    return 0
}

# Setter functions
rich_logger_set_enabled() {
    LOG_RICH_ENABLED="$1"
    return 0
}

rich_logger_set_file() {
    LOG_RICH_FILE="$1"
    return 0
}

rich_logger_set_format() {
    LOG_RICH_FORMAT="$1"
    return 0
}

# Export functions
export -f rich_logger_init rich_logger_log rich_logger_check_rotation rich_logger_rotate rich_logger_cleanup rich_logger_summary rich_logger_setup_trap rich_logger_validate_config rich_logger_set_enabled rich_logger_set_file rich_logger_set_format

# Export variables
export LOG_RICH_VERSION LOG_RICH_ENABLED LOG_RICH_FILE LOG_RICH_FORMAT LOG_RICH_ROTATION_SIZE LOG_RICH_ROTATION_COUNT LOG_RICH_RETENTION_DAYS LOG_RICH_COMPRESSION LOG_RICH_SESSION_ID LOG_RICH_SESSION_START

# Initialize configuration system when loaded
rich_logger_validate_config