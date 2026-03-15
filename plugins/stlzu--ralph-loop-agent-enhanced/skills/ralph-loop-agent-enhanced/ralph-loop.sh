#!/bin/bash

# Ralph Loop Agent for OpenClaw
# Provides loop-based execution capabilities with advanced logging and configuration
# Version: 2.1.0

set -e  # Exit on error

RALPH_LOOP_VERSION="2.1.0"

# Library paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/lib"

# Initialize logging early
LOG_ENABLED="${LOG_ENABLED:-false}"
LOG_LEVEL="${LOG_LEVEL:-info}"
LOG_FORMAT="${LOG_FORMAT:-text}"

# Basic logger function (for early logging)
logger_log() {
    local level="$1"
    local message="$2"
    
    if [[ "${LOG_ENABLED}" == "true" ]]; then
        local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
        echo "[$timestamp] [$level] $message"
    fi
}

# Load core libraries with error handling
load_libraries() {
    local failed=false
    
    # Required libraries
    local required_libs=("config_parser.sh" "logger.sh" "error_handler.sh" "progress_tracker.sh" "loop_engine.sh")
    
    for lib in "${required_libs[@]}"; do
        local lib_path="$LIB_DIR/$lib"
        if [[ -f "$lib_path" ]]; then
            if source "$lib_path" 2>/dev/null; then
                echo "INFO: Loaded library: $lib"
            else
                echo "ERROR: Failed to load library: $lib" >&2
                failed=true
            fi
        else
            echo "ERROR: Library not found: $lib" >&2
            failed=true
        fi
    done
    
    # Phase 2 libraries
    local phase2_libs=("rich_logger.sh" "config_file.sh" "state_manager.sh")
    for lib in "${phase2_libs[@]}"; do
        local lib_path="$LIB_DIR/$lib"
        if [[ -f "$lib_path" ]]; then
            if source "$lib_path" 2>/dev/null; then
                echo "INFO: Loaded Phase 2 library: $lib"
            else
                echo "ERROR: Failed to load Phase 2 library: $lib" >&2
                failed=true
            fi
        else
            echo "WARN: Phase 2 library not found: $lib (Phase 2 features will be disabled)"
        fi
    done
    
    if [[ "$failed" == "true" ]]; then
        return 1
    fi
    
    return 0
}

# Initialize all components
ralph_loop_init() {
    logger_log "info" "Initializing Ralph Loop Agent v$RALPH_LOOP_VERSION"
    
    # Initialize components
    echo "DEBUG: Before config_parser_init, loop_type='$(config_parser_get "loop_type")'"
    config_parser_init
    echo "DEBUG: After config_parser_init, loop_type='$(config_parser_get "loop_type")'"
    
    echo "DEBUG: Before config_file_init, loop_type='$(config_parser_get "loop_type")'"
    config_file_init
    echo "DEBUG: After config_file_init, loop_type='$(config_parser_get "loop_type")'"
    
    echo "DEBUG: Before logger_init, loop_type='$(config_parser_get "loop_type")'"
    logger_init
    echo "DEBUG: After logger_init, loop_type='$(config_parser_get "loop_type")'"
    
    echo "DEBUG: Before error_handler_init, loop_type='$(config_parser_get "loop_type")'"
    error_handler_init
    echo "DEBUG: After error_handler_init, loop_type='$(config_parser_get "loop_type")'"
    
    local default_iterations=$(config_parser_get "iterations")
    echo "DEBUG: Before progress_tracker_init, loop_type='$(config_parser_get "loop_type")'"
    progress_tracker_init "$default_iterations"
    echo "DEBUG: After progress_tracker_init, loop_type='$(config_parser_get "loop_type")'"
    
    echo "DEBUG: Before loop_engine_init, loop_type='$(config_parser_get "loop_type")'"
    loop_engine_init
    echo "DEBUG: After loop_engine_init, loop_type='$(config_parser_get "loop_type")'"
    
    # Set up signal handlers
    trap 'ralph_loop_cleanup; exit 1' INT TERM
    trap 'ralph_loop_cleanup' EXIT
    
    echo "DEBUG: After signal handlers, loop_type='$(config_parser_get "loop_type")'"
    
    # Initialize session
    SESSION_START_TIME=$(date +%s)
    LOOP_STATE["session_id"]=$(date +"%Y%m%d_%H%M%S_%N_%s")
    # Initialize rich logging if available
    if command -v rich_logger_init >/dev/null 2>&1; then
        rich_logger_init
        rich_logger_log "SESSION_START" "Ralph Loop Agent session started" "version" "$RALPH_LOOP_VERSION" "session_id" "${LOOP_STATE[session_id]}"
    else
        logger_log "info" "Rich logging not available, using basic logging"
    fi
    
    # Initialize state management
    state_manager_init
    
    # Generate and store config hash
    local config_hash=$(state_manager_generate_config_hash)
    state_manager_set "config_hash" "$config_hash"
    
    # Ensure loop_type is set to 'for' after initialization
    config_parser_set "loop_type" "for"
    logger_log "info" "Ralph Loop Agent initialized successfully"
    return 0
}

# Parse command line arguments
ralph_loop_parse_args() {
    local args=("$@")
    local i=0
    
    # Parse command line arguments
    while [[ $i -lt ${#args[@]} ]]; do
        case "${args[$i]}" in
            --help|-h)
                config_parser_show_help
                exit 0
                ;;
            --version|-v)
                echo "Ralph Loop Agent v$RALPH_LOOP_VERSION"
                exit 0
                ;;
            --demo)
                ralph_loop_demo
                exit 0
                ;;
            --verbose)
                config_parser_set "verbose" "true"
                LOG_ENABLED="true"
                ;;
            *)
                # If loop_type is not set, use this as the loop type
                if [[ "$(config_parser_get "loop_type")" == "for" && "${args[$i]}" != -* ]]; then
                    config_parser_set "loop_type" "${args[$i]}"
                fi
                ;;
        esac
        i=$((i + 1))
    done
    
    # Parse full options
    config_parser_parse_args "$@"
    
    # Set default values
    local current_loop_type=$(config_parser_get "loop_type")
    if [[ "$current_loop_type" == "for" ]]; then
        config_parser_set "loop_type" "for"
    fi
    local iterations=$(config_parser_get "iterations")
    if [[ -z "$iterations" ]]; then
        config_parser_set "iterations" "5"
    fi
    local delay_ms=$(config_parser_get "delay_ms")
    if [[ -z "$delay_ms" ]]; then
        config_parser_set "delay_ms" "0"
    fi
    local retry_count=$(config_parser_get "retry_count")
    if [[ -z "$retry_count" ]]; then
        config_parser_set "retry_count" "0"
    fi
    
    # Load configuration files
    local config_file=$(config_parser_get "config_file")
    if [[ -n "$config_file" ]]; then
        config_file_load "$config_file"
    else
        config_file_load
    fi
    
    # Validate configuration
    if ! config_parser_validate; then
        echo "Configuration validation failed" >&2
        exit 1
    fi
    
    # Initialize rich logging
    local log_enabled=$(config_parser_get "log_enabled")
    local log_format=$(config_parser_get "log_format")
    local log_file=$(config_parser_get "log_file")
    if command -v rich_logger_set_enabled >/dev/null 2>&1 && [[ "$log_enabled" == "true" ]]; then
        rich_logger_set_enabled true
        rich_logger_set_format "$log_format"
        if [[ -n "$log_file" ]]; then
            rich_logger_set_file "$log_file"
        fi
    fi
    
    return 0
}

# Show help
ralph_loop_show_help() {
    echo "Ralph Loop Agent v$RALPH_LOOP_VERSION"
    echo "Loop-based task execution and automation"
    echo ""
    echo "Usage:"
    echo "  ralph-loop [options] [loop_type]"
    echo ""
    echo "Loop Types:"
    echo "  for           - Fixed iteration count"
    echo "  while         - Conditional execution"
    echo "  until         - Execute until condition"
    echo "  range         - Custom numeric range"
    echo ""
    echo "Options:"
    echo "  --type, -t TYPE        Loop type (for|while|until|range)"
    echo "  --iterations, -n COUNT  Number of iterations (default: 5)"
    echo "  --delay, -d MS         Delay between iterations in ms (default: 0)"
    echo "  --retry, -r COUNT      Number of retries on failure (default: 0)"
    echo "  --continue-on-error, -c Continue on error"
    echo "  --no-progress          Disable progress display"
    echo "  --log                 Enable logging"
    echo "  --log-file PATH       Log file path (default: ./ralph-loop.log)"
    echo "  --log-format FORMAT   Log format (json|text, default: json)"
    echo "  --config, -f FILE     Configuration file path"
    echo "  --verbose, -v         Verbose output"
    echo "  --help, -h            Show this help"
    echo "  --version             Show version"
    echo "  demo                  Run demonstration"
    echo ""
    echo "Environment Variables:"
    echo "  RALPH_LOOP_TYPE        Loop type"
    echo "  RALPH_LOOP_ITERATIONS  Iteration count"
    echo "  RALPH_LOOP_DELAY_MS    Delay in milliseconds"
    echo "  RALPH_LOOP_RETRY_COUNT Retry count"
    echo "  RALPH_LOOP_CONTINUE_ON_ERROR Continue on error (true/false)"
    echo "  RALPH_LOOP_LOG_ENABLED Enable logging (true/false)"
    echo "  RALPH_LOOP_LOG_FORMAT  Log format (json/text)"
    echo "  RALPH_LOOP_VERBOSE    Verbose output (true/false)"
    echo ""
    echo "Configuration Files:"
    echo "  YAML: ~/.config/ralph-loop/ralph-loop.yaml"
    echo "  JSON: ~/.config/ralph-loop/ralph-loop.json"
    echo "  System: /etc/ralph-loop/ralph-loop.{yaml,json}"
    echo ""
    echo "Examples:"
    echo "  ralph-loop for --iterations 10"
    echo "  ralph-loop while --delay 1000"
    echo "  ralph-loop range --config my-config.yaml"
    echo ""
    echo "Integration:"
    echo "  Use in OpenClaw conversations for loop-based automation"
    echo "  Full documentation available in the skills directory"
}

# Run demonstration
ralph_loop_demo() {
    echo "Running Ralph Loop Agent demonstration..."
    echo ""
    
    # Demo configuration is set by the --demo argument in main()
    # Initialize demo
    if ! ralph_loop_init; then
        echo "Initialization failed" >&2
        exit 1
    fi
    
    # Initialize progress tracking
    local demo_iterations=$(config_parser_get "iterations")
    progress_tracker_init "$demo_iterations"
    
    # Run demo loop
    local demo_loop_type=$(config_parser_get "loop_type")
    local demo_delay_ms=$(config_parser_get "delay_ms")
    local demo_retry_count=$(config_parser_get "retry_count")
    local demo_continue_on_error=$(config_parser_get "continue_on_error")
    if ! loop_engine_execute "$demo_loop_type" "$demo_iterations" "$demo_delay_ms" "$demo_retry_count" "$demo_continue_on_error" "demo_callback"; then
        echo "Demo failed" >&2
        exit 1
    fi
    
    # Complete demo
    ralph_loop_cleanup
    
    echo ""
    echo "Demo completed successfully!"
    
    # Show statistics
    if command -v loop_engine_get_stats >/dev/null 2>&1; then
        echo "Statistics:"
        loop_engine_get_stats | sed 's/^/  /'
    fi
    
    return 0
}

# Demo callback function
demo_callback() {
    local iteration="$1"
    local total="$2"
    
    # Update state
    state_manager_set "current_iteration" "$iteration"
    state_manager_set "last_update" "$(date +%s)"
    
    # Calculate progress percentage
    local percentage=$(( iteration * 100 / total ))
    state_manager_set "progress_percentage" "$percentage"
    
    # Calculate remaining iterations and estimated completion
    local remaining=$(( total - iteration ))
    state_manager_set "remaining_iterations" "$remaining"
    
    if command -v date >/dev/null 2>&1; then
        local current_time=$(date +%s)
        local elapsed_time=$((current_time - $(state_manager_get "start_time")))
        local avg_time_per_iteration=$(( elapsed_time / iteration ))
        local eta_seconds=$(( remaining * avg_time_per_iteration ))
        
        if [[ $eta_seconds -gt 0 ]]; then
            local completion_time=$((current_time + eta_seconds))
            local estimated_completion=$(date -d "@$completion_time" +"%H:%M:%S" 2>/dev/null || echo "Calculating...")
        else
            local estimated_completion="Complete"
        fi
        state_manager_set "estimated_completion" "$estimated_completion"
    fi
    
    # Save state every 5 iterations or on last iteration
    if (( iteration % 5 == 0 || iteration == total )); then
        state_manager_save_state
    fi
    
    echo "Demo iteration $iteration of $total: Processing"
    
    # Simulate work
    sleep 0.3
    
    # Simulate occasional failure
    if [[ $iteration -eq 3 ]]; then
        echo "Demo: Simulated failure in iteration $iteration" >&2
        return 1
    fi
    
    return 0
}

# Main loop execution function
ralph_loop_execute() {
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
    
    # Initialize state management
    local session_id="${LOOP_STATE[session_id]}"
    state_manager_set "session_id" "$session_id"
    state_manager_set "loop_type" "$loop_type"
    state_manager_set "total_iterations" "$iterations"
    state_manager_set "current_iteration" "0"
    state_manager_set "start_time" "$(date +%s)"
    state_manager_set "last_update" "$(date +%s)"
    state_manager_set "status" "running"
    state_manager_set "callback_function" "$callback"
    
    # Save initial state
    state_manager_save_state
    
    logger_log "info" "Starting $loop_type loop with $iterations iterations (Session: $session_id)"
    
    # Initialize tracking
    TOTAL_ITERATIONS=0
    SUCCESS_COUNT=0
    FAILURE_COUNT=0
    
    # Progress tracking
    local progress_enabled=$(config_parser_get "progress_enabled")
    if [[ "$progress_enabled" == "true" ]]; then
        progress_tracker_init "$iterations"
    fi
    
    # Execute loop
    local result
    result=$(loop_engine_execute "$loop_type" "$iterations" "$delay_ms" "$retry_count" "$continue_on_error" "$callback")
    
    # Track completion
    TOTAL_ITERATIONS=$iterations
    if [[ $result -eq 0 ]]; then
        SUCCESS_COUNT=$iterations
    else
        if command -v loop_engine_get_stats >/dev/null 2>&1; then
            local successful_iterations
            successful_iterations=$(loop_engine_get_stats | grep "successful_iterations=" | cut -d'=' -f2)
            SUCCESS_COUNT=${successful_iterations:-0}
        fi
        FAILURE_COUNT=$((iterations - SUCCESS_COUNT))
    fi
    
    # Progress tracker cleanup
    local progress_enabled=$(config_parser_get "progress_enabled")
    if [[ "$progress_enabled" == "true" ]]; then
        progress_tracker_cleanup
    fi
    
    # Log results
    if command -v rich_logger_log >/dev/null 2>&1; then
        rich_logger_log "LOOP_COMPLETE" "Loop execution completed" "type" "$loop_type" "iterations" "$iterations" "success" "$SUCCESS_COUNT" "failure" "$FAILURE_COUNT"
    else
        logger_log "info" "Loop execution completed: $SUCCESS_COUNT successful, $FAILURE_COUNT failed"
    fi
    
    return $result
}

# Clean up resources
ralph_loop_cleanup() {
    SESSION_END_TIME=$(date +%s)
    local duration=$((SESSION_END_TIME - SESSION_START_TIME))
    
    # Log session end
    if command -v rich_logger_log >/dev/null 2>&1; then
        rich_logger_log "SESSION_END" "Ralph Loop Agent session ended" "duration_seconds" "$duration" "total_iterations" "$TOTAL_ITERATIONS" "success_count" "$SUCCESS_COUNT" "failure_count" "$FAILURE_COUNT"
    else
        logger_log "info" "Session ended in $duration seconds"
    fi
    
    # Rich logger cleanup
    local log_enabled=$(config_parser_get "log_enabled")
    if command -v rich_logger_cleanup >/dev/null 2>&1 && [[ "$log_enabled" == "true" ]]; then
        rich_logger_cleanup
    fi
    
    # Progress tracker cleanup
    local progress_enabled=$(config_parser_get "progress_enabled")
    if [[ "$progress_enabled" == "true" ]]; then
        progress_tracker_cleanup
    fi
    
    # Show final statistics
    local verbose=$(config_parser_get "verbose")
    if [[ "$verbose" == "true" ]]; then
        echo ""
        echo "Session Statistics:"
        echo "  Duration: $duration seconds"
        echo "  Total iterations: $TOTAL_ITERATIONS"
        echo "  Successful: $SUCCESS_COUNT"
        echo "  Failed: $FAILURE_COUNT"
        if [[ $TOTAL_ITERATIONS -gt 0 ]]; then
            local success_rate=$(echo "scale=1; $SUCCESS_COUNT * 100 / $TOTAL_ITERATIONS" | bc -l 2>/dev/null || echo "0")
            echo "  Success rate: $success_rate%"
        fi
    fi
    
    return 0
}

# Main entry point
main() {
    
    # Initialize early logging
    if [[ "$1" == "--verbose" || "$1" == "-v" ]]; then
        LOG_ENABLED="true"
    fi
    
    logger_log "info" "Starting Ralph Loop Agent v$RALPH_LOOP_VERSION"
    
    # Load libraries
    if ! load_libraries; then
        echo "ERROR: Failed to load libraries" >&2
        exit 1
    fi
    
    # Initialize
    if ! ralph_loop_init; then
        echo "Initialization failed" >&2
        exit 1
    fi
    
    # Parse arguments
    ralph_loop_parse_args "$@"
    
    # Execute loop if type specified
    
    # Execute loop if type specified
    local loop_type=$(config_parser_get "loop_type")
    local demo=$(config_parser_get "demo")
    local iterations=$(config_parser_get "iterations")
    local delay_ms=$(config_parser_get "delay_ms")
    local retry_count=$(config_parser_get "retry_count")
    local continue_on_error=$(config_parser_get "continue_on_error")
    
    if [[ -n "$loop_type" ]]; then
        # Determine callback function
        local callback_function="user_callback"
        if [[ "$demo" == "true" ]]; then
            callback_function="demo_callback"
        fi
        
        # Execute loop
        if ! ralph_loop_execute "$loop_type" "$iterations" "$delay_ms" "$retry_count" "$continue_on_error" "$callback_function"; then
            logger_log "error" "Loop execution failed"
            exit 1
        fi
    fi
    
    exit 0
}

# User callback function (placeholder for user-defined loop logic)
user_callback() {
    local iteration="$1"
    local total="$2"
    local value="$3"
    
    # Update state
    state_manager_set "current_iteration" "$iteration"
    state_manager_set "last_update" "$(date +%s)"
    
    # Calculate progress percentage
    local percentage=$(( iteration * 100 / total ))
    state_manager_set "progress_percentage" "$percentage"
    
    # Calculate remaining iterations and estimated completion
    local remaining=$(( total - iteration ))
    state_manager_set "remaining_iterations" "$remaining"
    
    if command -v date >/dev/null 2>&1; then
        local current_time=$(date +%s)
        local elapsed_time=$((current_time - $(state_manager_get "start_time")))
        local avg_time_per_iteration=$(( elapsed_time / iteration ))
        local eta_seconds=$(( remaining * avg_time_per_iteration ))
        
        if [[ $eta_seconds -gt 0 ]]; then
            local completion_time=$((current_time + eta_seconds))
            local estimated_completion=$(date -d "@$completion_time" +"%H:%M:%S" 2>/dev/null || echo "Calculating...")
        else
            local estimated_completion="Complete"
        fi
        state_manager_set "estimated_completion" "$estimated_completion"
    fi
    
    # Save state every 10 iterations or on last iteration
    if (( iteration % 10 == 0 || iteration == total )); then
        state_manager_save_state
    fi
    
    # Default implementation - user should override this
    echo "Processing iteration $iteration of $total"
    if [[ -n "$value" && "$value" != "$iteration" ]]; then
        echo "  Value: $value"
    fi
    
    # Simulate work
    sleep 0.1
    
    # Random failure for testing
    if [[ $((RANDOM % 10)) -eq 0 ]]; then
        echo "Random failure in iteration $iteration" >&2
        return 1
    fi
    
    return 0
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi