#!/bin/bash

# Configuration File Module for Ralph Loop Agent
# Provides configuration file parsing (YAML, JSON) with environment variable interpolation and layered configuration
# Version: 1.0.0

# Configuration variables
CONFIG_FILE_VERSION="1.0.0"
CONFIG_FILE_SEARCH_PATHS=("${HOME}/.config/ralph-loop" "/etc/ralph-loop" "./config")
CONFIG_FILE_ORDER=("cli" "file" "environment" "defaults")

# Error codes
CONFIG_FILE_ERROR_INVALID_FORMAT=1
CONFIG_FILE_ERROR_FILE_NOT_FOUND=2
CONFIG_FILE_ERROR_VALIDATION_FAILED=3
CONFIG_FILE_ERROR_PARSE_FAILED=4

# Global configuration storage (using arrays instead of associative arrays)
CONFIG_FILE_KEYS=(
    "loop_type"
    "iterations"
    "delay_ms"
    "retry_count"
    "continue_on_error"
    "progress_enabled"
    "log_enabled"
    "log_file"
    "log_format"
    "log_rotation_size"
    "log_rotation_count"
    "log_retention_days"
    "log_compression"
    "config_file_path"
    "verbose"
)

CONFIG_FILE_VALUES=(
    "for"
    "5"
    "0"
    "0"
    "false"
    "true"
    "false"
    "ralph-loop.log"
    "json"
    "10485760"
    "5"
    "7"
    "true"
    ""
    "false"
)

# Get config value by index
config_file_get_index() {
    local key="$1"
    case "$key" in
        "loop_type") echo 0 ;;
        "iterations") echo 1 ;;
        "delay_ms") echo 2 ;;
        "retry_count") echo 3 ;;
        "continue_on_error") echo 4 ;;
        "progress_enabled") echo 5 ;;
        "log_enabled") echo 6 ;;
        "log_file") echo 7 ;;
        "log_format") echo 8 ;;
        "log_rotation_size") echo 9 ;;
        "log_rotation_count") echo 10 ;;
        "log_retention_days") echo 11 ;;
        "log_compression") echo 12 ;;
        "config_file_path") echo 13 ;;
        "verbose") echo 14 ;;
        *) echo -1 ;;
    esac
}

# Get configuration value
config_file_get() {
    local key="$1"
    local default="$2"
    
    local index=$(config_file_get_index "$key")
    if [[ $index -ge 0 && $index -lt ${#CONFIG_FILE_KEYS[@]} ]]; then
        echo "${CONFIG_FILE_VALUES[$index]}"
    elif [[ -n "$default" ]]; then
        echo "$default"
    else
        return 1
    fi
}

# Set configuration value
config_file_set() {
    local key="$1"
    local value="$2"
    
    local index=$(config_file_get_index "$key")
    if [[ $index -ge 0 && $index -lt ${#CONFIG_FILE_KEYS[@]} ]]; then
        CONFIG_FILE_VALUES[$index]="$value"
        return 0
    fi
    
    return 1
}

# Initialize configuration system
config_file_init() {
    # Set default values
    config_file_set "loop_type" "for"
    config_file_set "iterations" "5"
    config_file_set "delay_ms" "0"
    config_file_set "retry_count" "0"
    config_file_set "continue_on_error" "false"
    config_file_set "progress_enabled" "true"
    config_file_set "log_enabled" "false"
    config_file_set "log_file" "ralph-loop.log"
    config_file_set "log_format" "json"
    config_file_set "log_rotation_size" "10485760"
    config_file_set "log_rotation_count" "5"
    config_file_set "log_retention_days" "7"
    config_file_set "log_compression" "true"
    config_file_set "config_file_path" ""
    config_file_set "verbose" "false"
    
    return 0
}

# Load configuration from multiple sources
config_file_load() {
    local config_file_path="$1"
    
    # Search for config file if not provided
    if [[ -z "$config_file_path" ]]; then
        for path in "${CONFIG_FILE_SEARCH_PATHS[@]}"; do
            if [[ -f "$path/ralph-loop.yaml" ]]; then
                config_file_path="$path/ralph-loop.yaml"
                break
            elif [[ -f "$path/ralph-loop.json" ]]; then
                config_file_path="$path/ralph-loop.json"
                break
            fi
        done
    fi
    
    # Store config file path
    config_file_set "config_file_path" "$config_file_path"
    
    # Load configuration in priority order
    for source in "${CONFIG_FILE_ORDER[@]}"; do
        case "$source" in
            "defaults")
                # Already set in init()
                ;;
            "environment")
                config_file_load_environment
                ;;
            "file")
                if [[ -n "$config_file_path" ]]; then
                    config_file_load_file "$config_file_path"
                fi
                ;;
            "cli")
                # CLI arguments are handled separately
                ;;
        esac
    done
    
    return 0
}

# Load configuration from environment variables
config_file_load_environment() {
    # Check for environment variables
    if [[ -n "$RALPH_LOOP_TYPE" ]]; then
        config_file_set "loop_type" "$RALPH_LOOP_TYPE"
    fi
    
    if [[ -n "$RALPH_LOOP_ITERATIONS" ]]; then
        config_file_set "iterations" "$RALPH_LOOP_ITERATIONS"
    fi
    
    if [[ -n "$RALPH_LOOP_DELAY_MS" ]]; then
        config_file_set "delay_ms" "$RALPH_LOOP_DELAY_MS"
    fi
    
    if [[ -n "$RALPH_LOOP_RETRY_COUNT" ]]; then
        config_file_set "retry_count" "$RALPH_LOOP_RETRY_COUNT"
    fi
    
    if [[ -n "$RALPH_LOOP_CONTINUE_ON_ERROR" ]]; then
        config_file_set "continue_on_error" "$RALPH_LOOP_CONTINUE_ON_ERROR"
    fi
    
    if [[ -n "$RALPH_LOOP_PROGRESS_ENABLED" ]]; then
        config_file_set "progress_enabled" "$RALPH_LOOP_PROGRESS_ENABLED"
    fi
    
    if [[ -n "$RALPH_LOOP_LOG_ENABLED" ]]; then
        config_file_set "log_enabled" "$RALPH_LOOP_LOG_ENABLED"
    fi
    
    if [[ -n "$RALPH_LOOP_LOG_FILE" ]]; then
        config_file_set "log_file" "$RALPH_LOOP_LOG_FILE"
    fi
    
    if [[ -n "$RALPH_LOOP_LOG_FORMAT" ]]; then
        config_file_set "log_format" "$RALPH_LOOP_LOG_FORMAT"
    fi
    
    if [[ -n "$RALPH_LOOP_LOG_ROTATION_SIZE" ]]; then
        config_file_set "log_rotation_size" "$RALPH_LOOP_LOG_ROTATION_SIZE"
    fi
    
    if [[ -n "$RALPH_LOOP_LOG_ROTATION_COUNT" ]]; then
        config_file_set "log_rotation_count" "$RALPH_LOOP_LOG_ROTATION_COUNT"
    fi
    
    if [[ -n "$RALPH_LOOP_LOG_RETENTION_DAYS" ]]; then
        config_file_set "log_retention_days" "$RALPH_LOOP_LOG_RETENTION_DAYS"
    fi
    
    if [[ -n "$RALPH_LOOP_LOG_COMPRESSION" ]]; then
        config_file_set "log_compression" "$RALPH_LOOP_LOG_COMPRESSION"
    fi
    
    if [[ -n "$RALPH_LOOP_VERBOSE" ]]; then
        config_file_set "verbose" "$RALPH_LOOP_VERBOSE"
    fi
    
    return 0
}

# Load configuration from file
config_file_load_file() {
    local file_path="$1"
    
    [[ ! -f "$file_path" ]] && return $CONFIG_FILE_ERROR_FILE_NOT_FOUND
    
    local file_extension="${file_path##*.}"
    
    case "$file_extension" in
        "yaml"|"yml")
            config_file_parse_yaml "$file_path"
            ;;
        "json")
            if command -v jq >/dev/null 2>&1; then
                config_file_parse_json_jq "$file_path"
            else
                config_file_parse_json_bash "$file_path"
            fi
            ;;
        *)
            echo "WARNING: Unsupported configuration file format: $file_extension" >&2
            return $CONFIG_FILE_ERROR_INVALID_FORMAT
            ;;
    esac
    
    return $?
}

# Parse YAML configuration file
config_file_parse_yaml() {
    local file_path="$1"
    local current_section=""
    
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Remove comments and trim
        line=$(echo "$line" | sed 's/#.*//' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
        
        # Skip empty lines
        [[ -z "$line" ]] && continue
        
        # Handle sections
        if [[ "$line" =~ ^[[:space:]]*\[([^\]]+)\][[:space:]]*$ ]]; then
            current_section="${BASH_REMATCH[1]}"
            continue
        fi
        
        # Handle key-value pairs
        if [[ "$line" =~ ^([[:space:]]*)([^:]+)[[:space:]]*:[[:space:]]*(.*)[[:space:]]*$ ]]; then
            local indent="${BASH_REMATCH[1]}"
            local key="${BASH_REMATCH[2]}"
            local value="${BASH_REMATCH[3]}"
            
            # Trim quotes from value
            value=$(echo "$value" | sed "s/^['\"]//" | sed "s/['\"]\$//")
            
            # Expand environment variables
            value=$(config_file_expand_env_vars "$value")
            
            # Build full key name
            local full_key="$key"
            if [[ -n "$current_section" ]]; then
                full_key="${current_section}.${key}"
            fi
            
            # Store value - only handle known keys
            case "$key" in
                loop_type|iterations|delay_ms|retry_count|continue_on_error|progress_enabled|log_enabled|log_file|log_format|log_rotation_size|log_rotation_count|log_retention_days|log_compression|verbose)
                    config_file_set "$key" "$value"
                    ;;
            esac
        fi
    done < "$file_path"
    
    return 0
}

# Parse JSON configuration file using jq
config_file_parse_json_jq() {
    local file_path="$1"
    
    if ! command -v jq >/dev/null 2>&1; then
        return $CONFIG_FILE_ERROR_PARSE_FAILED
    fi
    
    # Use jq to extract key-value pairs for known keys
    for key in loop_type iterations delay_ms retry_count continue_on_error progress_enabled log_enabled log_file log_format log_rotation_size log_rotation_count log_retention_days log_compression verbose; do
        local value
        value=$(jq -r ".\"$key\" // empty" "$file_path" 2>/dev/null)
        if [[ -n "$value" && "$value" != "null" ]]; then
            # Expand environment variables
            value=$(config_file_expand_env_vars "$value")
            config_file_set "$key" "$value"
        fi
    done
    
    return 0
}

# Parse JSON configuration file using bash (fallback)
config_file_parse_json_bash() {
    local file_path="$1"
    
    # Simple JSON parser (basic implementation)
    local json_content
    json_content=$(cat "$file_path")
    
    # Extract key-value pairs using regex for known keys
    for key in loop_type iterations delay_ms retry_count continue_on_error progress_enabled log_enabled log_file log_format log_rotation_size log_rotation_count log_retention_days log_compression verbose; do
        # Look for key-value pairs
        while [[ "$json_content" =~ \"$key\"[[:space:]]*:[[:space:]]*\"([^\"]+)\" ]]; do
            local value="${BASH_REMATCH[1]}"
            
            # Expand environment variables
            value=$(config_file_expand_env_vars "$value")
            
            config_file_set "$key" "$value"
            
            # Remove processed pair to prevent infinite loop
            json_content="${json_content#*\"$key\"[[:space:]]*:[[:space:]]*\"${BASH_REMATCH[1]}\"}"
        done
    done
    
    return 0
}

# Expand environment variables in string
config_file_expand_env_vars() {
    local text="$1"
    
    # Handle ${VAR} format
    while [[ "$text" =~ \$\{([^}]+)\} ]]; do
        local var_name="${BASH_REMATCH[1]}"
        local var_value="${!var_name:-}"
        text="${text/\${$var_name}/$var_value}"
    done
    
    # Handle $VAR format (at start of string or after non-alphanumeric)
    while [[ "$text" =~ \$([a-zA-Z_][a-zA-Z0-9_]*) ]]; do
        local var_name="${BASH_REMATCH[1]}"
        local var_value="${!var_name:-}"
        text="${text/\$$var_name/$var_value}"
    done
    
    echo "$text"
}

# Validate configuration
config_file_validate() {
    local errors=0
    
    # Validate numeric values
    for key in "iterations" "delay_ms" "retry_count" "log_rotation_size" "log_rotation_count" "log_retention_days"; do
        local value
        value=$(config_file_get "$key")
        
        if [[ ! "$value" =~ ^[0-9]+$ ]]; then
            echo "ERROR: Configuration key '$key' must be numeric, got: $value" >&2
            ((errors++))
        fi
    done
    
    # Validate boolean values
    for key in "continue_on_error" "progress_enabled" "log_enabled" "log_compression" "verbose"; do
        local value
        value=$(config_file_get "$key")
        
        if [[ "$value" != "true" && "$value" != "false" ]]; then
            echo "ERROR: Configuration key '$key' must be true/false, got: $value" >&2
            ((errors++))
        fi
    done
    
    # Validate log format
    local log_format
    log_format=$(config_file_get "log_format")
    if [[ "$log_format" != "json" && "$log_format" != "text" ]]; then
        echo "ERROR: Configuration key 'log_format' must be json/text, got: $log_format" >&2
        ((errors++))
    fi
    
    return $errors
}

# Get all configuration values
config_file_get_all() {
    for i in "${!CONFIG_FILE_KEYS[@]}"; do
        echo "${CONFIG_FILE_KEYS[$i]}=${CONFIG_FILE_VALUES[$i]}"
    done
}

# Export functions
export -f config_file_init config_file_load config_file_load_environment config_file_load_file config_file_parse_yaml config_file_parse_json_jq config_file_parse_json_bash config_file_expand_env_vars config_file_get config_file_set config_file_validate config_file_get_all config_file_get_index

# Export variables
export CONFIG_FILE_VERSION CONFIG_FILE_SEARCH_PATHS CONFIG_FILE_ORDER CONFIG_FILE_ERROR_INVALID_FORMAT CONFIG_FILE_ERROR_FILE_NOT_FOUND CONFIG_FILE_ERROR_VALIDATION_FAILED CONFIG_FILE_ERROR_PARSE_FAILED CONFIG_FILE_KEYS CONFIG_FILE_VALUES

# Initialize configuration system when loaded
config_file_init