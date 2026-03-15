#!/bin/bash

# Debug script for Ralph Loop Agent

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/lib"

echo "Debug Test"
echo "=========="
echo "Script directory: $SCRIPT_DIR"
echo "Library directory: $LIB_DIR"
echo ""

echo "Checking libraries:"
for lib in config_parser.sh logger.sh error_handler.sh progress_tracker.sh loop_engine.sh rich_logger.sh config_file.sh; do
    local_path="$LIB_DIR/$lib"
    if [[ -f "$local_path" ]]; then
        echo "✅ $lib exists"
        # Test if we can source it
        if source "$local_path"; then
            echo "  ✅ Can source successfully"
        else
            echo "  ❌ Failed to source"
        fi
    else
        echo "❌ $lib missing"
    fi
    echo ""
done

echo "Testing main script:"
bash -n "$SCRIPT_DIR/ralph-loop.sh" && echo "✅ Syntax OK" || echo "❌ Syntax error"

echo ""
echo "Testing minimal run:"
timeout 5 bash "$SCRIPT_DIR/ralph-loop.sh" --help || echo "Command timed out or failed"