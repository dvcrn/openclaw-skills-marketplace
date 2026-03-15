#!/bin/bash

# Batch Processing Example for Ralph Loop Agent
# This script demonstrates advanced batch processing with
# error handling, resumability, and monitoring

# Include the Ralph Loop Agent
source "$(dirname "$0")/../ralph-loop.sh"

# Global configuration
CONFIG_FILE="batch_config.yaml"
LOG_DIR="logs"
STATE_DIR="state"
ERROR_LOG="$LOG_DIR/batch_errors.log"
PROGRESS_LOG="$LOG_DIR/progress.log"
BATCH_RESULTS="batch_results.csv"

# Configuration management
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        echo "Using configuration from: $CONFIG_FILE"
        # Load configuration from file
        source <(python3 -c "
import yaml
with open('$CONFIG_FILE') as f:
    config = yaml.safe_load(f)
for key, value in config.items():
    print(f'export {key.upper()}=\"{value}\"')
" 2>/dev/null || echo "echo 'Configuration file parsing failed'")
    else
        echo "Using default configuration"
        set_defaults
    fi
}

# Set default configuration
set_defaults() {
    export BATCH_SIZE="${BATCH_SIZE:-100}"
    export MAX_RETRIES="${MAX_RETRIES:-3}"
    export DELAY_MS="${DELAY_MS:-100}"
    export LOG_ENABLED="${LOG_ENABLED:-true}"
    export CONTINUE_ON_ERROR="${CONTINUE_ON_ERROR:-false}"
    export CREATE_CHECKPOINTS="${CREATE_CHECKPOINTS:-true}"
    export CLEANUP_OLD_FILES="${CLEANUP_OLD_FILES:-true}"
}

# Create sample tasks if they don't exist
create_sample_tasks() {
    local tasks_file="${1:-tasks.csv}"
    
    if [[ ! -f "$tasks_file" ]]; then
        echo "Creating sample tasks file: $tasks_file"
        echo "task_id,task_type,priority,data_size,status" > "$tasks_file"
        
        # Create various task types
        for i in {1..1000}; do
            task_type=$((i % 4 + 1))  # 4 different task types
            priority=$((RANDOM % 5 + 1))  # Priority 1-5
            data_size=$((RANDOM % 10000 + 1000))  # 1KB-10KB
            status=$((RANDOM % 3))  # Status 0=pending, 1=running, 2=completed
            
            echo "task_$i,$task_type,$priority,$data_size,$status" >> "$tasks_file"
        done
        
        echo "Created $tasks_file with 1000 sample tasks"
    fi
}

# Custom callback for batch processing
batch_callback() {
    local iteration="$1"
    local total="$2"
    local value="$3"
    
    # Get task data
    local task_data
    task_data=$(sed -n "${iteration}p" tasks.csv 2>/dev/null)
    
    if [[ -z "$task_data" ]]; then
        echo "Error: No task data found for iteration $iteration" >&2
        echo "Iteration $iteration,Total $total,Error,No data found" >> "$ERROR_LOG"
        return 1
    fi
    
    # Parse task data
    local task_id task_type priority data_size status
    IFS=',' read -r task_id task_type priority data_size status <<< "$task_data"
    
    # Update progress
    local percentage=$(( iteration * 100 / total ))
    echo "$(date '+%Y-%m-%d %H:%M:%S'),$iteration,$total,$percentage,$task_id,$task_type" >> "$PROGRESS_LOG"
    
    # Process task based on type
    local result="completed"
    local return_code=0
    local processing_time=0
    
    case "$task_type" in
        1)
            # Type 1: Data validation
            echo "Validating task $task_id (type=$task_type, priority=$priority)"
            processing_time=$((RANDOM % 100 + 50))  # 50-150ms
            
            # Simulate validation
            if [[ $priority -ge 4 ]]; then
                echo "  High priority validation - detailed checks"
                sleep 0.2
            else
                echo "  Standard validation - quick checks"
                sleep 0.05
            fi
            
            # Simulate validation failure
            if [[ $((RANDOM % 10)) -eq 0 ]]; then
                result="validation_failed"
                return_code=1
                echo "  Validation failed for task $task_id" >&2
            fi
            ;;
            
        2)
            # Type 2: Data transformation
            echo "Transforming task $task_id (type=$task_type, priority=$priority)"
            processing_time=$((RANDOM % 200 + 100))  # 100-300ms
            
            # Simulate transformation
            if [[ $priority -ge 3 ]]; then
                echo "  Complex transformation"
                sleep 0.3
            else
                echo "  Simple transformation"
                sleep 0.1
            fi
            
            # Simulate transformation error
            if [[ $((RANDOM % 20)) -eq 0 ]]; then
                result="transformation_error"
                return_code=1
                echo "  Transformation error for task $task_id" >&2
            fi
            ;;
            
        3)
            # Type 3: Data analysis
            echo "Analyzing task $task_id (type=$task_type, priority=$priority)"
            processing_time=$((RANDOM % 500 + 200))  # 200-700ms
            
            # Simulate analysis
            echo "  Performing analysis on $data_size bytes"
            if [[ $priority -ge 5 ]]; then
                echo "  High performance analysis"
                sleep 0.5
            else
                echo "  Standard analysis"
                sleep 0.2
            fi
            
            # Simulate analysis timeout
            if [[ $((RANDOM % 15)) -eq 0 ]]; then
                result="analysis_timeout"
                return_code=1
                echo "  Analysis timeout for task $task_id" >&2
            fi
            ;;
            
        4)
            # Type 4: Data export
            echo "Exporting task $task_id (type=$task_type, priority=$priority)"
            processing_time=$((RANDOM % 300 + 150))  # 150-450ms
            
            # Simulate export
            echo "  Exporting $data_size bytes to destination"
            if [[ $priority -ge 4 ]]; then
                echo "  High priority export"
                sleep 0.4
            else
                echo "  Standard export"
                sleep 0.15
            fi
            
            # Simulate export failure
            if [[ $((RANDOM % 25)) -eq 0 ]]; then
                result="export_failed"
                return_code=1
                echo "  Export failed for task $task_id" >&2
            fi
            ;;
    esac
    
    # Log result
    echo "$(date '+%Y-%m-%d %H:%M:%S'),$iteration,$total,$task_id,$task_type,$priority,$data_size,$status,$result,$processing_time" >> "$BATCH_RESULTS"
    
    # Return status
    return $return_code
}

# Initialize batch processing
init_batch() {
    echo "=== Batch Processing Initialization ==="
    echo ""
    
    # Create directories
    mkdir -p "$LOG_DIR" "$STATE_DIR"
    
    # Load configuration
    load_config
    
    # Create sample tasks
    create_sample_tasks
    
    # Initialize logs
    echo "timestamp,iteration,total,percentage,task_id,task_type" > "$PROGRESS_LOG"
    echo "timestamp,iteration,total,task_id,task_type,priority,data_size,status,result,processing_time" > "$BATCH_RESULTS"
    
    # Show configuration
    echo "Configuration:"
    echo "  Batch size: $BATCH_SIZE"
    echo "  Max retries: $MAX_RETRIES"
    echo "  Delay: $DELAY_MS ms"
    echo "  Log enabled: $LOG_ENABLED"
    echo "  Continue on error: $CONTINUE_ON_ERROR"
    echo "  Create checkpoints: $CREATE_CHECKPOINTS"
    echo ""
    
    # Show task statistics
    local total_tasks=$(wc -l < tasks.csv)
    local pending_tasks=$(tail -n +2 tasks.csv | cut -d',' -f5 | grep -c "0")
    local running_tasks=$(tail -n +2 tasks.csv | cut -d',' -f5 | grep -c "1")
    local completed_tasks=$(tail -n +2 tasks.csv | cut -d',' -f5 | grep -c "2")
    
    echo "Task Statistics:"
    echo "  Total tasks: $total_tasks"
    echo "  Pending tasks: $pending_tasks"
    echo "  Running tasks: $running_tasks"
    echo "  Completed tasks: $completed_tasks"
    echo ""
}

# Run batch processing
run_batch() {
    echo "Starting batch processing..."
    echo ""
    
    local total_tasks=$(($(wc -l < tasks.csv) - 1))  # Subtract header
    
    # Run with appropriate configuration
    ./ralph-loop.sh for --iterations "$total_tasks" --delay "$DELAY_MS" \
        --retry "$MAX_RETRIES" \
        --continue-on-error "$CONTINUE_ON_ERROR" \
        --checkpoint \
        --log \
        --config << EOF
loop_type: for
iterations: $total_tasks
delay_ms: $DELAY_MS
retry_count: $MAX_RETRIES
continue_on_error: $CONTINUE_ON_ERROR
log_enabled: true
log_format: json
EOF
    
    echo ""
    echo "Batch processing completed!"
}

# Run batch monitoring
monitor_batch() {
    echo "=== Batch Processing Monitoring ==="
    echo ""
    
    # Show progress
    if [[ -f "$PROGRESS_LOG" ]]; then
        echo "Recent progress:"
        tail -10 "$PROGRESS_LOG"
        echo ""
    fi
    
    # Show sessions
    echo "Available sessions:"
    ./ralph-loop.sh --list-sessions
    echo ""
    
    # Show current state
    if [[ -f "../state/current_state.json" ]]; then
        echo "Current processing state:"
        cat ../state/current_state.json | jq . 2>/dev/null || cat ../state/current_state.json
    else
        echo "No active processing state"
    fi
}

# Analyze batch results
analyze_batch() {
    echo "=== Batch Processing Analysis ==="
    echo ""
    
    if [[ ! -f "$BATCH_RESULTS" ]]; then
        echo "No results found. Run batch processing first."
        return 1
    fi
    
    local total_tasks=$(($(wc -l < "$BATCH_RESULTS") - 1))
    
    echo "Processing Summary:"
    echo "  Total tasks processed: $total_tasks"
    echo ""
    
    # Task type distribution
    echo "Task Type Distribution:"
    tail -n +2 "$BATCH_RESULTS" | cut -d',' -f3 | sort | uniq -c | while read count task_type; do
        echo "  Type $task_type: $count tasks"
    done
    echo ""
    
    # Status distribution
    echo "Result Distribution:"
    tail -n +2 "$BATCH_RESULTS" | cut -d',' -f8 | sort | uniq -c | while read count result; do
        echo "  $result: $count tasks"
    done
    echo ""
    
    # Success rate
    local success_count=$(tail -n +2 "$BATCH_RESULTS" | grep -c "completed")
    local failure_count=$((total_tasks - success_count))
    local success_rate=$(echo "scale=2; $success_count * 100 / $total_tasks" | bc -l 2>/dev/null || echo "$((success_count * 100 / total_tasks)).0")
    
    echo "Success Rate: $success_rate% ($success_count/$total_tasks)"
    echo ""
    
    # Average processing time
    if command -v bc >/dev/null 2>&1; then
        local avg_time=$(tail -n +2 "$BATCH_RESULTS" | cut -d',' -f10 | awk '{sum+=$1} END {print sum/NR}')
        echo "Average processing time: ${avg_time}ms"
    fi
    
    # Error analysis
    if [[ -f "$ERROR_LOG" ]]; then
        echo ""
        echo "Error Log Analysis:"
        echo "  Total errors: $(wc -l < "$ERROR_LOG")"
        echo ""
        echo "Recent errors:"
        tail -5 "$ERROR_LOG"
    fi
}

# Cleanup old files
cleanup() {
    echo "=== Cleanup ==="
    echo ""
    
    if [[ "$CLEANUP_OLD_FILES" != "true" ]]; then
        echo "Cleanup disabled. Set CLEANUP_OLD_FILES=true to enable."
        return 0
    fi
    
    # Clean old logs
    echo "Cleaning old logs..."
    find "$LOG_DIR" -name "*.log" -mtime +7 -delete
    
    # Clean old states
    echo "Cleaning old states..."
    find "$STATE_DIR" -name "*.json" -mtime +7 -delete
    
    # Keep only recent results
    echo "Cleaning old results..."
    ls -t "$LOG_DIR"/progress_* 2>/dev/null | tail -n +10 | xargs rm -f
    
    echo "Cleanup completed."
}

# Main execution
case "${1:-help}" in
    "init")
        init_batch
        ;;
    "run")
        init_batch
        run_batch
        ;;
    "monitor")
        monitor_batch
        ;;
    "analyze")
        analyze_batch
        ;;
    "config")
        load_config
        echo "Current configuration:"
        env | grep -E "BATCH_|MAX_|DELAY_|LOG_|CONTINUE_|CREATE_|CLEANUP_" | sort
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|"-h"|"--help"|"-?"|"")
        echo "Batch Processing Examples for Ralph Loop Agent"
        echo ""
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  init        - Initialize batch processing environment"
        echo "  run         - Run batch processing (recommended)"
        echo "  monitor     - Monitor batch processing progress"
        echo "  analyze     - Analyze batch processing results"
        echo "  config      - Show current configuration"
        echo "  cleanup     - Clean up old files and logs"
        echo "  help        - Show this help message"
        echo ""
        echo "Configuration Options:"
        echo "  BATCH_SIZE          - Number of tasks per batch (default: 100)"
        echo "  MAX_RETRIES         - Maximum retry attempts (default: 3)"
        echo "  DELAY_MS            - Delay between tasks (ms, default: 100)"
        echo "  LOG_ENABLED         - Enable logging (default: true)"
        echo "  CONTINUE_ON_ERROR   - Continue on error (default: false)"
        echo "  CREATE_CHECKPOINTS  - Create checkpoints (default: true)"
        echo "  CLEANUP_OLD_FILES    - Cleanup old files (default: true)"
        echo ""
        echo "Environment Variables:"
        echo "  Set any configuration option as environment variable"
        echo "  Example: BATCH_SIZE=50 MAX_RETRIES=5 $0 run"
        echo ""
        echo "Examples:"
        echo "  $0 init          # Initialize environment"
        echo "  $0 run           # Run batch processing"
        echo "  $0 monitor       # Check progress"
        echo "  $0 analyze       # View results"
        echo "  BATCH_SIZE=200 $0 run  # Custom batch size"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information."
        exit 1
        ;;
esac