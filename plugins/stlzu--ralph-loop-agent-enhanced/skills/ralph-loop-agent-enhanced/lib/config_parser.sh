#!/bin/bash

# Configuration Parser Module for Ralph Loop Agent
# Handles command line argument parsing and validation
# Version: 1.0.0

CONFIG_PARSER_VERSION="1.0.0"

# Global configuration storage (using arrays instead of associative arrays)
CONFIG_KEYS=(
    "help"
    "version"
    "demo"
    "loop_type"
    "iterations"
    "delay_ms"
    "retry_count"
    "continue_on_error"
    "progress_enabled"
    "log_enabled"
    "log_file"
    "log_format"
    "config_file"
    "verbose"
)

CONFIG_VALUES=(
    "false"
    "false"
    "false"
    "for"
    "5"
    "0"
    "0"
    "false"
    "true"
    "false"
    "./ralph-loop.log"
    "json"
    ""
    "false"
)

# Get config value by index
config_parser_get_index() {
    local key="$1"
    case "$key" in
        "help") echo 0 ;;
        "version") echo 1 ;;
        "demo") echo 2 ;;
        "loop_type") echo 3 ;;
        "iterations") echo 4 ;;
        "delay_ms") echo 5 ;;
        "retry_count") echo 6 ;;
        "continue_on_error") echo 7 ;;
        "progress_enabled") echo 8 ;;
        "log_enabled") echo 9 ;;
        "log_file") echo 10 ;;
        "log_format") echo 11 ;;
        "resume") echo 12 ;;
        "session_id") echo 13 ;;
        "create_checkpoint") echo 14 ;;
        "list_sessions") echo 15 ;;
        "config_file") echo 12 ;;
        "verbose") echo 13 ;;
        *) echo -1 ;;
    esac
}

# Get configuration value
config_parser_get() {
    local key="$1"
    local default="$2"
    
    local index=$(config_parser_get_index "$key")
    if [[ $index -ge 0 && $index -lt ${#CONFIG_KEYS[@]} ]]; then
        echo "${CONFIG_VALUES[$index]}"
    elif [[ -n "$default" ]]; then
        echo "$default"
    else
        return 1
    fi
}

# Set configuration value
config_parser_set() {
    local key="$1"
    local value="$2"
    
    local index=$(config_parser_get_index "$key")
    if [[ $index -ge 0 && $index -lt ${#CONFIG_KEYS[@]} ]]; then
        CONFIG_VALUES[$index]="$value"
        return 0
    fi
    
    return 1
}

# Initialize configuration parser
config_parser_init() {
    # Set default values
    CONFIG_VALUES[0]="false"      # help
    CONFIG_VALUES[1]="false"      # version
    CONFIG_VALUES[2]="false"      # demo
    CONFIG_VALUES[3]="for"        # loop_type
    CONFIG_VALUES[4]="5"          # iterations
    CONFIG_VALUES[5]="0"          # delay_ms
    CONFIG_VALUES[6]="0"          # retry_count
    CONFIG_VALUES[7]="false"      # continue_on_error
    CONFIG_VALUES[8]="false"     # resume
    CONFIG_VALUES[9]=""           # session_id
    CONFIG_VALUES[10]="false"     # create_checkpoint
    CONFIG_VALUES[11]="false"     # list_sessions
    CONFIG_VALUES[8]="true"       # progress_enabled
    CONFIG_VALUES[9]="false"      # log_enabled
    CONFIG_VALUES[10]="./ralph-loop.log"  # log_file
    CONFIG_VALUES[11]="json"      # log_format
    CONFIG_VALUES[12]=""          # config_file
    CONFIG_VALUES[13]="false"      # verbose
    
    return 0
}

# Parse command line arguments
config_parser_parse_args() {
    local args=("$@")
    local i=0
    
    while [[ $i -lt ${#args[@]} ]]; do
        case "${args[$i]}" in
            --help|-h)
                config_parser_set "help" "true"
                ;;
            --version|-v)
                config_parser_set "version" "true"
                ;;
            --demo)
                config_parser_set "demo" "true"
                ;;
            --type|-t)
                i=$((i + 1))
                if [[ $i -lt ${#args[@]} ]]; then
                    config_parser_set "loop_type" "${args[$i]}"
                else
                    echo "ERROR: --type requires an argument" >&2
                    return 1
                fi
                ;;
            --iterations|-n)
                i=$((i + 1))
                if [[ $i -lt ${#args[@]} ]]; then
                    config_parser_set "iterations" "${args[$i]}"
                else
                    echo "ERROR: --iterations requires an argument" >&2
                    return 1
                fi
                ;;
            --delay|-d)
                i=$((i + 1))
                if [[ $i -lt ${#args[@]} ]]; then
                    config_parser_set "delay_ms" "${args[$i]}"
                else
                    echo "ERROR: --delay requires an argument" >&2
                    return 1
                fi
                ;;
            --retry|-r)
                i=$((i + 1))
                if [[ $i -lt ${#args[@]} ]]; then
                    config_parser_set "retry_count" "${args[$i]}"
                else
                    echo "ERROR: --retry requires an argument" >&2
                    return 1
                fi
                ;;
            --continue-on-error|-c)
                config_parser_set "continue_on_error" "true"
                ;;
            --no-progress)
                config_parser_set "progress_enabled" "false"
                ;;
            --log)
                config_parser_set "log_enabled" "true"
                ;;
            --log-file)
                i=$((i + 1))
                if [[ $i -lt ${#args[@]} ]]; then
                    config_parser_set "log_file" "${args[$i]}"
                else
                    echo "ERROR: --log-file requires an argument" >&2
                    return 1
                fi
                ;;
            --log-format)
                i=$((i + 1))
                if [[ $i -lt ${#args[@]} ]]; then
                    config_parser_set "log_format" "${args[$i]}"
                else
                    echo "ERROR: --log-format requires an argument" >&2
                    return 1
                fi
                ;;
            --config|-f)
                i=$((i + 1))
                if [[ $i -lt ${#args[@]} ]]; then
                    config_parser_set "config_file" "${args[$i]}"
                else
                    echo "ERROR: --config requires an argument" >&2
                    return 1
                fi
                ;;
            --verbose)
                config_parser_set "verbose" "true"
                ;;
            --resume|-r)
                config_parser_set "resume" "true"
                ;;
            --session|-s)
                i=$((i + 1))
                if [[ $i -lt ${#args[@]} ]]; then
                    config_parser_set "session_id" "${args[$i]}"
                else
                    echo "ERROR: --session requires an argument" >&2
                    return 1
                fi
                ;;
            --checkpoint)
                config_parser_set "create_checkpoint" "true"
                ;;
            --list-sessions)
                config_parser_set "list_sessions" "true"
                ;;
            --*)
                echo "ERROR: Unknown option: ${args[$i]}" >&2
                return 1
                ;;
            *)
                # Handle special commands first
                if [[ "${args[$i]}" == "demo" ]]; then
                    config_parser_set "demo" "true"
                    # Ensure loop_type doesn't get set to demo
                    config_parser_set "loop_type" "for"
                else
                    # If loop_type is not set, use this as the loop type
                    local current_loop_type=$(config_parser_get "loop_type")
                    echo "DEBUG: current_loop_type='$current_loop_type', arg='${args[$i]}'"
                    if [[ "$current_loop_type" == "for" && "${args[$i]}" != -* ]]; then
                        # Only set loop_type if it's a valid loop type
                        case "${args[$i]}" in
                            for|while|until|range)
                                config_parser_set "loop_type" "${args[$i]}"
                                ;;
                            *)
                                echo "ERROR: Unknown argument: ${args[$i]}" >&2
                                return 1
                                ;;
                        esac
                    else
                        echo "ERROR: Unknown argument: ${args[$i]}" >&2
                        return 1
                    fi
                fi
                ;;
        esac
        i=$((i + 1))
    done
    
    return 0
}

# Validate configuration values
config_parser_validate() {
    local errors=0
    
    # Validate loop type
    local loop_type=$(config_parser_get "loop_type")
    case "$loop_type" in
        for|while|until|range)
            # Valid type
            ;;
        *)
            echo "ERROR: Invalid loop type: $loop_type" >&2
            echo "Valid types: for, while, until, range" >&2
            ((errors++))
            ;;
    esac
    
    # Validate numeric values
    local iterations=$(config_parser_get "iterations")
    if [[ ! "$iterations" =~ ^[0-9]+$ ]]; then
        echo "ERROR: iterations must be numeric, got: $iterations" >&2
        ((errors++))
    fi
    
    local delay_ms=$(config_parser_get "delay_ms")
    if [[ ! "$delay_ms" =~ ^[0-9]+$ ]]; then
        echo "ERROR: delay_ms must be numeric, got: $delay_ms" >&2
        ((errors++))
    fi
    
    local retry_count=$(config_parser_get "retry_count")
    if [[ ! "$retry_count" =~ ^[0-9]+$ ]]; then
        echo "ERROR: retry_count must be numeric, got: $retry_count" >&2
        ((errors++))
    fi
    
    # Validate log format
    local log_format=$(config_parser_get "log_format")
    if [[ "$log_format" != "json" && "$log_format" != "text" ]]; then
        echo "ERROR: Log format must be 'json' or 'text', got: $log_format" >&2
        ((errors++))
    fi
    
    # Validate that log file path is not empty if log is enabled
    if [[ "$(config_parser_get "log_enabled")" == "true" && -z "$(config_parser_get "log_file")" ]]; then
        echo "ERROR: Log file path is required when --log is enabled" >&2
        ((errors++))
    fi
    
    return $errors
}

# Get all configuration values
config_parser_get_all() {
    for i in "${!CONFIG_KEYS[@]}"; do
        echo "${CONFIG_KEYS[$i]}=${CONFIG_VALUES[$i]}"
    done
}

# Show help information
config_parser_show_help() {
    echo "Ralph Loop Agent Configuration Options:"
    echo ""
    echo "Loop Types:"
    echo "  for           - Fixed iteration count (default)"
    echo "  while         - Conditional execution"
    echo "  until         - Execute until condition"
    echo "  range         - Custom numeric range"
    echo ""
    echo "Options:"
    echo "  --type, -t TYPE        Loop type"
    echo "  --iterations, -n COUNT  Number of iterations (default: 5)"
    echo "  --delay, -d MS         Delay between iterations in ms (default: 0)"
    echo "  --retry, -r COUNT      Number of retries on failure (default: 0)"
    echo "  --continue-on-error, -c Continue on error"
    echo "  --no-progress          Disable progress display"
    echo "  --log                 Enable logging"
    echo "  --log-file PATH       Log file path"
    echo "  --log-format FORMAT   Log format (json/text)"
    echo "  --config, -f FILE     Configuration file"
    echo ""
    echo "Resumability Options:"
    echo "  --resume, -r          Resume from last state"
    echo "  --session, -s ID      Resume from specific session"
    echo "  --checkpoint          Create checkpoint before execution"
    echo "  --list-sessions       List available sessions"
    echo "  --verbose             Verbose output"
    echo "  --help, -h            Show this help"
    echo "  --version             Show version"
    echo "  --demo                Run demonstration"
    echo ""
    echo "Example Usage:"
    echo "  ralph-loop for --iterations 10"
    echo "  ralph-loop while --delay 1000 --verbose"
    echo "  ralph-loop range --config my-config.yaml"
}

# Export functions
export -f config_parser_init config_parser_parse_args config_parser_validate config_parser_get config_parser_set config_parser_get_all config_parser_show_help config_parser_get_index

# Export variables
export CONFIG_PARSER_VERSION CONFIG_KEYS CONFIG_VALUES