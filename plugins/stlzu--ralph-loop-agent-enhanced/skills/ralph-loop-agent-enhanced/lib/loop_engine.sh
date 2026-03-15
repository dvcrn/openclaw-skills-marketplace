#!/bin/bash

# Loop Engine Module for Ralph Loop Agent
# Handles different loop types and execution logic
# Version: 1.0.0

LOOP_ENGINE_VERSION="1.0.0"

# Loop execution statistics (using arrays instead of associative arrays)
LOOP_KEYS=(
    "total_iterations"
    "successful_iterations"
    "failed_iterations"
    "start_time"
    "end_time"
    "total_duration"
)

LOOP_VALUES=(
    "0"
    "0"
    "0"
    "0"
    "0"
    "0"
)

# Get loop value by key
loop_engine_get_index() {
    local key="$1"
    case "$key" in
        "total_iterations") echo 0 ;;
        "successful_iterations") echo 1 ;;
        "failed_iterations") echo 2 ;;
        "start_time") echo 3 ;;
        "end_time") echo 4 ;;
        "total_duration") echo 5 ;;
        *) echo -1 ;;
    esac
}

# Get loop value
loop_engine_get() {
    local key="$1"
    local index=$(loop_engine_get_index "$key")
    if [[ $index -ge 0 && $index -lt ${#LOOP_KEYS[@]} ]]; then
        echo "${LOOP_VALUES[$index]}"
    fi
}

# Set loop value
loop_engine_set() {
    local key="$1"
    local value="$2"
    local index=$(loop_engine_get_index "$key")
    if [[ $index -ge 0 && $index -lt ${#LOOP_KEYS[@]} ]]; then
        LOOP_VALUES[$index]="$value"
        return 0
    fi
    return 1
}

# Initialize loop engine
loop_engine_init() {
    return 0
}

# Execute loop based on type
loop_engine_execute() {
    local loop_type="$1"
    local iterations="$2"
    local delay_ms="$3"
    local retry_count="$4"
    local continue_on_error="$5"
    local callback="$6"
    
    # Validate inputs
    if [[ -z "$loop_type" || -z "$callback" ]]; then
        echo "ERROR: Loop type and callback are required" >&2
        return 1
    fi
    
    # Initialize statistics
    loop_engine_set "total_iterations" "0"
    loop_engine_set "successful_iterations" "0"
    loop_engine_set "failed_iterations" "0"
    loop_engine_set "start_time" "$(date +%s)"
    
    # Execute based on loop type
    local result=0
    case "$loop_type" in
        "for")
            result=$(loop_engine_for_loop "$iterations" "$delay_ms" "$retry_count" "$continue_on_error" "$callback")
            ;;
        "while")
            result=$(loop_engine_while_loop "$delay_ms" "$retry_count" "$continue_on_error" "$callback")
            ;;
        "until")
            result=$(loop_engine_until_loop "$delay_ms" "$retry_count" "$continue_on_error" "$callback")
            ;;
        "range")
            result=$(loop_engine_range_loop "$iterations" "$delay_ms" "$retry_count" "$continue_on_error" "$callback")
            ;;
        *)
            echo "ERROR: Unsupported loop type: $loop_type" >&2
            return 1
            ;;
    esac
    
    # Finalize statistics
    loop_engine_set "end_time" "$(date +%s)"
    local start_time=$(loop_engine_get "start_time")
    loop_engine_set "total_duration" $(( $(date +%s) - start_time ))
    
    return $result
}

# Execute for loop
loop_engine_for_loop() {
    local iterations="$1"
    local delay_ms="$2"
    local retry_count="$3"
    local continue_on_error="$4"
    local callback="$5"
    
    local delay_seconds=$(echo "$delay_ms / 1000" | bc -l 2>/dev/null || echo "0")
    
    for ((i=1; i<=iterations; i++)); do
        loop_engine_set "total_iterations" $(( $(loop_engine_get "total_iterations") + 1 ))
        
        # Execute callback with retry logic
        local result=0
        for ((retry=0; retry<=retry_count; retry++)); do
            if [[ "$callback" == "demo_callback" ]]; then
                result=$($callback "$i" "$iterations")
            else
                result=$($callback "$i" "$iterations" 2>&1)
            fi
            
            if [[ $result -eq 0 ]]; then
                # Success
                loop_engine_set "successful_iterations" $(( $(loop_engine_get "successful_iterations") + 1 ))
                break
            else
                # Failure
                if [[ $retry -lt $retry_count ]]; then
                    logger_log "warn" "Retry $((retry + 1)) of $retry_count for iteration $i"
                    sleep "$delay_seconds"
                else
                    loop_engine_set "failed_iterations" $(( $(loop_engine_get "failed_iterations") + 1 ))
                    if [[ "$continue_on_error" != "true" ]]; then
                        echo "ERROR: Callback failed for iteration $i after $retry_count retries" >&2
                        return 1
                    fi
                fi
            fi
        done
        
        # Delay between iterations (except for last)
        if [[ $i -lt $iterations && $delay_seconds -gt 0 ]]; then
            sleep "$delay_seconds"
        fi
    done
    
    # Check if all iterations succeeded
    local failed_count=$(loop_engine_get "failed_iterations")
    if [[ $failed_count -gt 0 && "$continue_on_error" != "true" ]]; then
        return 1
    fi
    
    return 0
}

# Execute while loop
loop_engine_while_loop() {
    local delay_ms="$1"
    local retry_count="$2"
    local continue_on_error="$3"
    local callback="$4"
    
    local delay_seconds=$(echo "$delay_ms / 1000" | bc -l 2>/dev/null || echo "0")
    local iteration=1
    
    while true; do
        loop_engine_set "total_iterations" $(( $(loop_engine_get "total_iterations") + 1 ))
        
        # Execute callback with retry logic
        local result=0
        for ((retry=0; retry<=retry_count; retry++)); do
            if [[ "$callback" == "demo_callback" ]]; then
                result=$($callback "$iteration" "infinite")
            else
                result=$($callback "$iteration" "infinite" 2>&1)
            fi
            
            if [[ $result -eq 0 ]]; then
                # Success - check if we should continue
                break
            else
                # Failure
                if [[ $retry -lt $retry_count ]]; then
                    logger_log "warn" "Retry $((retry + 1)) of $retry_count for iteration $iteration"
                    sleep "$delay_seconds"
                else
                    loop_engine_set "failed_iterations" $(( $(loop_engine_get "failed_iterations") + 1 ))
                    if [[ "$continue_on_error" != "true" ]]; then
                        echo "ERROR: Callback failed for iteration $iteration after $retry_count retries" >&2
                        return 1
                    fi
                fi
            fi
        done
        
        iteration=$((iteration + 1))
        
        # Default while loop runs indefinitely - user callback should control exit
        # For safety, we'll limit to 1000 iterations
        if [[ $iteration -gt 1000 ]]; then
            logger_log "info" "Iteration limit reached (1000), stopping while loop"
            break
        fi
        
        if [[ $delay_seconds -gt 0 ]]; then
            sleep "$delay_seconds"
        fi
    done
    
    return 0
}

# Execute until loop
loop_engine_until_loop() {
    local delay_ms="$1"
    local retry_count="$2"
    local continue_on_error="$3"
    local callback="$4"
    
    local delay_seconds=$(echo "$delay_ms / 1000" | bc -l 2>/dev/null || echo "0")
    local iteration=1
    
    # Execute until callback succeeds or limit reached
    while true; do
        loop_engine_set "total_iterations" $(( $(loop_engine_get "total_iterations") + 1 ))
        
        # Execute callback with retry logic
        local result=0
        for ((retry=0; retry<=retry_count; retry++)); do
            if [[ "$callback" == "demo_callback" ]]; then
                result=$($callback "$iteration" "until_success")
            else
                result=$($callback "$iteration" "until_success" 2>&1)
            fi
            
            if [[ $result -eq 0 ]]; then
                # Success - until loop completed
                loop_engine_set "successful_iterations" $(( $(loop_engine_get "successful_iterations") + 1 ))
                break 2  # Exit both loops
            else
                # Failure
                if [[ $retry -lt $retry_count ]]; then
                    logger_log "warn" "Retry $((retry + 1)) of $retry_count for iteration $iteration"
                    sleep "$delay_seconds"
                else
                    loop_engine_set "failed_iterations" $(( $(loop_engine_get "failed_iterations") + 1 ))
                    if [[ "$continue_on_error" != "true" ]]; then
                        echo "ERROR: Callback failed for iteration $iteration after $retry_count retries" >&2
                        return 1
                    fi
                fi
            fi
        done
        
        iteration=$((iteration + 1))
        
        # Safety limit
        if [[ $iteration -gt 1000 ]]; then
            logger_log "info" "Iteration limit reached (1000), stopping until loop"
            break
        fi
        
        if [[ $delay_seconds -gt 0 ]]; then
            sleep "$delay_seconds"
        fi
    done
    
    return 0
}

# Execute range loop
loop_engine_range_loop() {
    local config="$1"
    local delay_ms="$2"
    local retry_count="$3"
    local continue_on_error="$4"
    local callback="$5"
    
    local delay_seconds=$(echo "$delay_ms / 1000" | bc -l 2>/dev/null || echo "0")
    
    # Parse range configuration (format: start:end:step)
    local start=1
    local end=10
    local step=1
    
    if [[ "$config" =~ ^([0-9]+):([0-9]+):([0-9]+)$ ]]; then
        start="${BASH_REMATCH[1]}"
        end="${BASH_REMATCH[2]}"
        step="${BASH_REMATCH[3]}"
    elif [[ "$config" =~ ^([0-9]+):([0-9]+)$ ]]; then
        start="${BASH_REMATCH[1]}"
        end="${BASH_REMATCH[2]}"
    else
        # Default range
        start=1
        end=$config
    fi
    
    # Validate range
    if [[ $start -gt $end && $step -gt 0 ]]; then
        echo "ERROR: Invalid range: start=$start > end=$end with positive step=$step" >&2
        return 1
    fi
    
    # Execute range loop
    local iteration=1
    local current=$start
    while true; do
        loop_engine_set "total_iterations" $(( $(loop_engine_get "total_iterations") + 1 ))
        
        # Execute callback with retry logic
        local result=0
        for ((retry=0; retry<=retry_count; retry++)); do
            if [[ "$callback" == "demo_callback" ]]; then
                result=$($callback "$current" "$iteration")
            else
                result=$($callback "$current" "$iteration" 2>&1)
            fi
            
            if [[ $result -eq 0 ]]; then
                # Success
                loop_engine_set "successful_iterations" $(( $(loop_engine_get "successful_iterations") + 1 ))
                break
            else
                # Failure
                if [[ $retry -lt $retry_count ]]; then
                    logger_log "warn" "Retry $((retry + 1)) of $retry_count for value $current"
                    sleep "$delay_seconds"
                else
                    loop_engine_set "failed_iterations" $(( $(loop_engine_get "failed_iterations") + 1 ))
                    if [[ "$continue_on_error" != "true" ]]; then
                        echo "ERROR: Callback failed for value $current after $retry_count retries" >&2
                        return 1
                    fi
                fi
            fi
        done
        
        # Move to next value
        current=$((current + step))
        iteration=$((iteration + 1))
        
        # Check if we've reached the end
        if [[ $step -gt 0 && $current -gt $end ]]; then
            break
        elif [[ $step -lt 0 && $current -lt $end ]]; then
            break
        fi
        
        if [[ $delay_seconds -gt 0 ]]; then
            sleep "$delay_seconds"
        fi
    done
    
    # Check if all iterations succeeded
    local failed_count=$(loop_engine_get "failed_iterations")
    if [[ $failed_count -gt 0 && "$continue_on_error" != "true" ]]; then
        return 1
    fi
    
    return 0
}

# Get loop statistics
loop_engine_get_stats() {
    local total=$(loop_engine_get "total_iterations")
    local successful=$(loop_engine_get "successful_iterations")
    local failed=$(loop_engine_get "failed_iterations")
    local start=$(loop_engine_get "start_time")
    local end=$(loop_engine_get "end_time")
    local duration=$(loop_engine_get "total_duration")
    
    echo "total_iterations=$total"
    echo "successful_iterations=$successful"
    echo "failed_iterations=$failed"
    echo "start_time=$start"
    echo "end_time=$end"
    echo "total_duration=$duration"
    
    # Calculate success rate
    if [[ $total -gt 0 ]]; then
        local success_rate=$(echo "scale=2; $successful * 100 / $total" | bc -l 2>/dev/null || echo "0")
        echo "success_rate=$success_rate%"
    else
        echo "success_rate=0%"
    fi
}

# Reset loop statistics
loop_engine_reset() {
    loop_engine_set "total_iterations" "0"
    loop_engine_set "successful_iterations" "0"
    loop_engine_set "failed_iterations" "0"
    loop_engine_set "start_time" "0"
    loop_engine_set "end_time" "0"
    loop_engine_set "total_duration" "0"
    
    return 0
}

# Export functions
export -f loop_engine_init loop_engine_execute loop_engine_for_loop loop_engine_while_loop loop_engine_until_loop loop_engine_range_loop loop_engine_get_stats loop_engine_reset loop_engine_get loop_engine_set loop_engine_get_index

# Export variables
export LOOP_ENGINE_VERSION LOOP_KEYS LOOP_VALUES