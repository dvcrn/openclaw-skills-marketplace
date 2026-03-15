#!/bin/bash

# Error Handler Module for Ralph Loop Agent
# Provides error handling and retry logic with exponential backoff
# Version: 1.0.0

ERROR_HANDLER_VERSION="1.0.0"
MAX_RETRIES="${MAX_RETRIES:-0}"
BACKOFF_FACTOR="${BACKOFF_FACTOR:-2}"
BACKOFF_BASE="${BACKOFF_BASE:-1}"
CONTINUE_ON_ERROR="${CONTINUE_ON_ERROR:-false}"

# Error codes
ERROR_HANDLER_MAX_RETRIES_EXCEEDED=100
ERROR_HANDLER_INVALID_ARGUMENT=101
ERROR_HANDLER_FILE_NOT_FOUND=102
ERROR_HANDLER_PERMISSION_DENIED=103
ERROR_HANDLER_TIMEOUT=104

# Global error state (using arrays instead of associative arrays)
ERROR_KEYS=(
    "last_error"
    "error_count"
    "retry_count"
    "total_attempts"
)

ERROR_VALUES=(
    ""
    "0"
    "0"
    "0"
)

# Get error value by key
error_handler_get_index() {
    local key="$1"
    case "$key" in
        "last_error") echo 0 ;;
        "error_count") echo 1 ;;
        "retry_count") echo 2 ;;
        "total_attempts") echo 3 ;;
        *) echo -1 ;;
    esac
}

# Get error value
error_handler_get() {
    local key="$1"
    local index=$(error_handler_get_index "$key")
    if [[ $index -ge 0 && $index -lt ${#ERROR_KEYS[@]} ]]; then
        echo "${ERROR_VALUES[$index]}"
    fi
}

# Set error value
error_handler_set() {
    local key="$1"
    local value="$2"
    local index=$(error_handler_get_index "$key")
    if [[ $index -ge 0 && $index -lt ${#ERROR_KEYS[@]} ]]; then
        ERROR_VALUES[$index]="$value"
        return 0
    fi
    return 1
}

# Initialize error handler
error_handler_init() {
    error_handler_set "last_error" ""
    error_handler_set "error_count" "0"
    error_handler_set "retry_count" "0"
    error_handler_set "total_attempts" "0"
    return 0
}

# Handle error with retry logic
error_handler_handle() {
    local error_message="$1"
    local exit_code="${2:-1}"
    local should_retry="${3:-false}"
    
    # Update error state
    error_handler_set "last_error" "$error_message"
    local current_count=$(error_handler_get "error_count")
    error_handler_set "error_count" $((current_count + 1))
    local current_attempts=$(error_handler_get "total_attempts")
    error_handler_set "total_attempts" $((current_attempts + 1))
    
    # Log error
    logger_log "error" "$error_message"
    
    # Handle retry logic
    if [[ "$should_retry" == "true" ]]; then
        local retry_count=$(error_handler_get "retry_count")
        if [[ $retry_count -lt $MAX_RETRIES ]]; then
            return error_handler_retry "$error_message" "$exit_code"
        fi
    fi
    
    # Handle continue on error
    if [[ "$CONTINUE_ON_ERROR" == "true" ]]; then
        logger_log "warn" "Continuing despite error: $error_message"
        return 0
    fi
    
    # Exit with error code
    return $exit_code
}

# Retry with exponential backoff
error_handler_retry() {
    local error_message="$1"
    local exit_code="$2"
    
    local retry_count=$(error_handler_get "retry_count")
    error_handler_set "retry_count" $((retry_count + 1))
    
    # Calculate backoff delay
    local backoff_delay=$((BACKOFF_BASE * (BACKOFF_FACTOR ** (retry_count + 1))))
    
    logger_log "warn" "Attempt $((retry_count + 1)) failed: $error_message"
    logger_log "info" "Retrying in $backoff_delay seconds... (attempt $((retry_count + 1)) of $MAX_RETRIES)"
    
    # Sleep for backoff delay
    sleep $backoff_delay
    
    # Return special retry code
    return $ERROR_HANDLER_MAX_RETRIES_EXCEEDED
}

# Check if should continue on error
error_handler_should_continue() {
    [[ "$CONTINUE_ON_ERROR" == "true" ]]
    return $?
}

# Get error state
error_handler_get_state() {
    echo "last_error=$(error_handler_get 'last_error')"
    echo "error_count=$(error_handler_get 'error_count')"
    echo "retry_count=$(error_handler_get 'retry_count')"
    echo "total_attempts=$(error_handler_get 'total_attempts')"
    echo "max_retries=$MAX_RETRIES"
    echo "continue_on_error=$CONTINUE_ON_ERROR"
}

# Reset error state
error_handler_reset() {
    error_handler_set "last_error" ""
    error_handler_set "error_count" "0"
    error_handler_set "retry_count" "0"
    error_handler_set "total_attempts" "0"
    return 0
}

# Validate input arguments
error_handler_validate_args() {
    local args=("$@")
    local i=0
    local errors=0
    
    while [[ $i -lt ${#args[@]} ]]; do
        case "${args[$i]}" in
            --help|-h)
                error_handler_show_help
                return 0
                ;;
            --max-retries)
                i=$((i + 1))
                if [[ $i -lt ${#args[@]} && "${args[$i]}" =~ ^[0-9]+$ ]]; then
                    MAX_RETRIES="${args[$i]}"
                else
                    echo "ERROR: Max retries must be numeric" >&2
                    ((errors++))
                fi
                ;;
            --backoff-factor)
                i=$((i + 1))
                if [[ $i -lt ${#args[@]} && "${args[$i]}" =~ ^[0-9]+$ ]]; then
                    BACKOFF_FACTOR="${args[$i]}"
                else
                    echo "ERROR: Backoff factor must be numeric" >&2
                    ((errors++))
                fi
                ;;
            --backoff-base)
                i=$((i + 1))
                if [[ $i -lt ${#args[@]} && "${args[$i]}" =~ ^[0-9]+$ ]]; then
                    BACKOFF_BASE="${args[$i]}"
                else
                    echo "ERROR: Backoff base must be numeric" >&2
                    ((errors++))
                fi
                ;;
            --continue-on-error)
                # Valid option
                ;;
            --*)
                echo "ERROR: Unknown option: ${args[$i]}" >&2
                ((errors++))
                ;;
        esac
        i=$((i + 1))
    done
    
    if [[ $errors -gt 0 ]]; then
        return 1
    fi
    
    return 0
}

# Show help for error handler
error_handler_show_help() {
    echo "Error Handler Options:"
    echo "  --max-retries N        Maximum number of retry attempts (default: $MAX_RETRIES)"
    echo "  --backoff-factor F     Exponential backoff factor (default: $BACKOFF_FACTOR)"
    echo "  --backoff-base B       Base delay for backoff in seconds (default: $BACKOFF_BASE)"
    echo "  --continue-on-error    Continue execution on error"
    echo "  --help, -h             Show this help"
}

# Export functions
export -f error_handler_init error_handler_handle error_handler_retry error_handler_should_continue error_handler_get_state error_handler_reset error_handler_validate_args error_handler_show_help error_handler_get error_handler_set error_handler_get_index

# Export variables
export ERROR_HANDLER_VERSION MAX_RETRIES BACKOFF_FACTOR BACKOFF_BASE CONTINUE_ON_ERROR ERROR_KEYS ERROR_VALUES