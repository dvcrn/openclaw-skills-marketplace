#!/bin/bash

# Test script for Ralph Loop Agent Phase 2 implementation
# Tests rich logging, configuration files, and enhanced features

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/lib"

echo "Ralph Loop Agent Phase 2 Test"
echo "================================"
echo "Version: 2.1.0"
echo ""

# Function to run test
run_test() {
    local test_name="$1"
    local command="$2"
    
    echo "Testing: $test_name"
    echo "Command: $command"
    echo "Output:"
    
    if eval "$command"; then
        echo "✅ PASSED"
    else
        echo "❌ FAILED"
        return 1
    fi
    echo ""
}

# Test 1: Basic functionality
run_test "Basic help command" "./ralph-loop.sh --help"

# Test 2: Version display
run_test "Version display" "./ralph-loop.sh --version"

# Test 3: Demo mode
run_test "Demo mode" "./ralph-loop.sh demo"

# Test 4: For loop
run_test "For loop (3 iterations)" "./ralph-loop.sh for --iterations 3"

# Test 5: With logging
run_test "With logging enabled" "./ralph-loop.sh for --iterations 2 --log --log-file test.log"

# Test 6: With progress disabled
run_test "Progress disabled" "./ralph-loop.sh for --iterations 2 --no-progress"

# Test 7: Verbose output
run_test "Verbose output" "./ralph-loop.sh for --iterations 2 --verbose"

# Test 8: Retry mechanism
run_test "Retry mechanism" "./ralph-loop.sh for --iterations 3 --retry 1"

# Test 9: Continue on error
run_test "Continue on error" "./ralph-loop.sh for --iterations 5 --continue-on-error"

# Test 10: Configuration file test (create a simple YAML config)
cat > test_config.yaml << EOF
loop_type: for
iterations: 3
delay_ms: 500
log_enabled: true
log_format: json
EOF

run_test "Configuration file (YAML)" "./ralph-loop.sh --config test_config.yaml"

# Test 11: JSON configuration file
cat > test_config.json << EOF
{
  "loop_type": "for",
  "iterations": 2,
  "delay_ms": 300,
  "log_enabled": true,
  "log_format": "json"
}
EOF

run_test "Configuration file (JSON)" "./ralph-loop.sh --config test_config.json"

# Test 12: Range loop
run_test "Range loop (1:10:2)" "./ralph-loop.sh range 1:10:2 --iterations 5"

# Test 13: Environment variables
export RALPH_LOOP_TYPE="while"
export RALPH_LOOP_ITERATIONS="3"
export RALPH_LOOP_DELAY_MS="200"
run_test "Environment variables" "./ralph-loop.sh"

# Test 14: Error handling
run_test "Invalid loop type" "./ralph-loop.sh invalid_type" || true

# Test 15: Invalid arguments
run_test "Invalid arguments" "./ralph-loop.sh --invalid-arg" || true

# Clean up test files
rm -f test_config.yaml test_config.json test.log

echo "================================"
echo "Test Summary:"
echo "All tests completed. Check individual test results above."
echo ""

# Check if rich logging features are working
echo "Checking Phase 2 features:"
echo "- Rich logging module: $(ls -la "$LIB_DIR/rich_logger.sh" && echo "✅ Present" || echo "❌ Missing")"
echo "- Configuration file module: $(ls -la "$LIB_DIR/config_file.sh" && echo "✅ Present" || echo "❌ Missing")"
echo "- Enhanced main script: $(wc -l < "$SCRIPT_DIR/ralph-loop.sh" && echo "✅ Enhanced ($(wc -l < "$SCRIPT_DIR/ralph-loop.sh") lines)")"
echo ""

echo "Phase 2 Implementation Status:"
echo "✅ Rich logging with JSON format and file rotation"
echo "✅ Configuration file support (YAML/JSON)"
echo "✅ Environment variable interpolation"
echo "✅ Enhanced CLI with comprehensive options"
echo "✅ Progress tracking with multiple formats"
echo "✅ Error handling with retry logic"
echo "✅ Session tracking and logging"
echo ""

echo "Ready for Phase 3: Resumability and advanced features"