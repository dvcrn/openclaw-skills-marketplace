#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/lib"

echo "Testing minimal load..."
echo "Script dir: $SCRIPT_DIR"
echo "Lib dir: $LIB_DIR"

# Test with function definitions
load_libraries() {
    echo "DEBUG: Inside load_libraries()"
    # Required libraries
    local required_libs=("config_parser.sh" "logger.sh" "error_handler.sh" "progress_tracker.sh" "loop_engine.sh")
    
    for lib in "${required_libs[@]}"; do
        local lib_path="$LIB_DIR/$lib"
        echo "DEBUG: Checking $lib_path"
        if [[ -f "$lib_path" ]]; then
            if source "$lib_path" 2>/dev/null; then
                echo "INFO: Loaded library: $lib"
            else
                echo "ERROR: Failed to load library: $lib" >&2
                return 1
            fi
        else
            echo "ERROR: Library not found: $lib" >&2
            return 1
        fi
    done
    return 0
}

# Test loading
echo "Calling load_libraries..."
if load_libraries; then
    echo "load_libraries() succeeded"
    if command -v config_parser_get >/dev/null 2>&1; then
        echo "config_parser_get available after load_libraries"
    else
        echo "config_parser_get NOT available after load_libraries"
    fi
else
    echo "load_libraries() failed"
fi