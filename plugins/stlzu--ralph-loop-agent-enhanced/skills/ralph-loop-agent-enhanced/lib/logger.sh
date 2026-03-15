#!/bin/bash

# Basic Logger Module for Ralph Loop Agent
# Provides simple logging functionality
# Version: 1.0.0

LOGGER_VERSION="1.0.0"
LOG_ENABLED="${LOG_ENABLED:-false}"
LOG_LEVEL="${LOG_LEVEL:-info}"
LOG_FORMAT="${LOG_FORMAT:-text}"

# Log level mapping (using arrays instead of associative arrays)
LOG_LEVELS_error=0
LOG_LEVELS_warn=1
LOG_LEVELS_info=2
LOG_LEVELS_debug=3

# Global log buffer
LOG_BUFFER=()

# Initialize logger
logger_init() {
    return 0
}

# Get log level value
logger_get_level_value() {
    local level="$1"
    local level_var="LOG_LEVELS_$level"
    echo "${!level_var}"
}

# Log message
logger_log() {
    local level="$1"
    local message="$2"
    
    # Check if level is enabled
    local current_level=$(logger_get_level_value "$level")
    local threshold_level=$(logger_get_level_value "$LOG_LEVEL")
    
    if [[ $current_level -gt $threshold_level ]]; then
        return 0
    fi
    
    # Format message
    local formatted_message
    if [[ "$LOG_FORMAT" == "json" ]]; then
        formatted_message=$(printf '{"timestamp":"%s","level":"%s","message":"%s"}' "$(date +%Y-%m-%dT%H:%M:%S%z)" "$level" "$message")
    else
        formatted_message=$(printf "[%s] [%s] %s" "$(date +"%Y-%m-%d %H:%M:%S")" "$level" "$message")
    fi
    
    # Add to buffer
    LOG_BUFFER+=("$formatted_message")
    
    # Print to console if enabled
    if [[ "$LOG_ENABLED" == "true" ]]; then
        echo "$formatted_message"
    fi
    
    return 0
}

# Log at specific levels
logger_error() { logger_log "error" "$1"; }
logger_warn() { logger_log "warn" "$1"; }
logger_info() { logger_log "info" "$1"; }
logger_debug() { logger_log "debug" "$1"; }

# Flush buffer to file
logger_flush() {
    local file_path="$1"
    
    if [[ -z "$file_path" || ${#LOG_BUFFER[@]} -eq 0 ]]; then
        return 0
    fi
    
    # Create directory if needed
    local dir_path=$(dirname "$file_path")
    if [[ ! -d "$dir_path" ]]; then
        mkdir -p "$dir_path" || {
            logger_error "Cannot create log directory: $dir_path"
            return 1
        }
    fi
    
    # Write buffer to file
    {
        printf "%s\n" "${LOG_BUFFER[@]}"
    } >> "$file_path" 2>/dev/null || {
        logger_error "Cannot write to log file: $file_path"
        return 1
    }
    
    # Clear buffer
    LOG_BUFFER=()
    
    return 0
}

# Clear log buffer
logger_clear() {
    LOG_BUFFER=()
    return 0
}

# Export functions
export -f logger_init logger_log logger_error logger_warn logger_info logger_debug logger_flush logger_clear logger_get_level_value

# Export variables
export LOGGER_VERSION LOG_ENABLED LOG_LEVEL LOG_FORMAT LOG_BUFFER