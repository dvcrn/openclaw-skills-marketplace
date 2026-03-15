#!/bin/bash

# Simple test script for Ralph Loop Agent
# Test each component individually

echo "=== Simple Test Script ==="
echo ""

# Test 1: Check if libraries load
echo "Test 1: Library Loading"
for lib in lib/*.sh; do
    echo "Testing $lib..."
    if source "$lib"; then
        echo "✅ $lib loaded successfully"
    else
        echo "❌ Failed to load $lib"
    fi
done
echo ""

# Test 2: Test basic functions
echo "Test 2: Basic Functions"
if command -v config_parser_show_help >/dev/null 2>&1; then
    echo "✅ config_parser functions available"
else
    echo "❌ config_parser functions not available"
fi
echo ""

# Test 3: Test version display
echo "Test 3: Version Display"
echo "BASH_VERSION: $BASH_VERSION"
echo "config_parser version: $(config_parser_get version 2>/dev/null echo 'Not available')"
echo ""

echo "=== Test Complete ==="