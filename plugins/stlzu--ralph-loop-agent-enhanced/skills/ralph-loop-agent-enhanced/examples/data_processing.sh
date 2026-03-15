#!/bin/bash

# Data Processing Example for Ralph Loop Agent
# This script demonstrates how to use the Ralph Loop Agent
# for batch data processing tasks

# Include the Ralph Loop Agent
source "$(dirname "$0")/../ralph-loop.sh"

# Configuration
DATA_FILE="${1:-data.csv}"
OUTPUT_FILE="processed_results.csv"
BATCH_SIZE="${2:-100}"

# Ensure data file exists
if [[ ! -f "$DATA_FILE" ]]; then
    echo "Creating sample data file: $DATA_FILE"
    echo "id,value,category,status" > "$DATA_FILE"
    for i in {1..500}; do
        category=$((i % 3 + 1))  # Categories 1, 2, 3
        status=$((RANDOM % 2))    # Status 0 or 1
        value=$((RANDOM % 1000))
        echo "$i,$value,$category,$status" >> "$DATA_FILE"
    done
    echo "Created $DATA_FILE with 500 sample records"
fi

# Custom callback function for data processing
user_callback() {
    local iteration="$1"
    local total="$2"
    local value="$3"  # This will be empty for basic loops
    
    # Get the current line from data file
    local data_line
    data_line=$(sed -n "${iteration}p" "$DATA_FILE" 2>/dev/null)
    
    if [[ -z "$data_line" ]]; then
        echo "Warning: No data found for iteration $iteration" >&2
        return 0
    fi
    
    # Parse CSV line (simple approach for bash 3.2 compatibility)
    local id value category status
    IFS=',' read -r id value category status <<< "$data_line"
    
    # Process the data
    echo "Processing record $id: value=$value, category=$category, status=$status"
    
    # Calculate some metrics
    local processed_value=$((value * 2))
    local normalized_value=$(echo "scale=2; $value / 10" | bc -l 2>/dev/null || echo "$((value / 10)).0")
    
    # Apply category-based processing
    local category_multiplier=1
    case "$category" in
        1) category_multiplier=1.2 ;;
        2) category_multiplier=1.5 ;;
        3) category_multiplier=1.8 ;;
    esac
    
    local final_value=$(echo "scale=2; $processed_value * $category_multiplier" | bc -l 2>/dev/null || echo "$((processed_value * category_multiplier))")
    
    # Status-based processing
    local status_text="processed"
    if [[ $status -eq 0 ]]; then
        status_text="skipped"
        final_value=0
    fi
    
    # Write result to output file
    echo "$id,$value,$category,$status,$processed_value,$normalized_value,$final_value,$status_text" >> "$OUTPUT_FILE"
    
    # Simulate processing time
    sleep 0.1
    
    # Return 0 for success, 1 for failure
    return 0
}

# Function to run data processing
run_data_processing() {
    echo "=== Data Processing with Ralph Loop Agent ==="
    echo ""
    echo "Input file: $DATA_FILE"
    echo "Output file: $OUTPUT_FILE"
    echo "Total records: $(wc -l < "$DATA_FILE")"
    echo ""
    
    # Create output file header
    echo "id,value,category,status,processed_value,normalized_value,final_value,status_text" > "$OUTPUT_FILE"
    
    # Run the processing
    echo "Starting data processing..."
    local total_records=$(wc -l < "$DATA_FILE")
    
    ./ralph-loop.sh for --iterations "$total_records" --delay 100 --log \
        --config << EOF
loop_type: for
iterations: $total_records
delay_ms: 100
log_enabled: true
log_format: json
EOF
    
    echo ""
    echo "Data processing completed!"
    echo "Results saved to: $OUTPUT_FILE"
    
    # Show summary
    echo ""
    echo "=== Processing Summary ==="
    echo "Total records processed: $(wc -l < "$OUTPUT_FILE")"
    echo "Processing rate: $(echo "scale=2; $total_records / 10" | bc -l) records/second"
    
    # Show sample results
    echo ""
    echo "Sample results:"
    head -5 "$OUTPUT_FILE" | tail -4
}

# Function to run batch processing
run_batch_processing() {
    echo "=== Batch Data Processing ==="
    echo ""
    
    local total_records=$(wc -l < "$DATA_FILE")
    local batches=$(( (total_records + BATCH_SIZE - 1) / BATCH_SIZE ))
    
    echo "Total records: $total_records"
    echo "Batch size: $BATCH_SIZE"
    echo "Number of batches: $batches"
    echo ""
    
    # Process in batches
    for ((batch=1; batch<=batches; batch++)); do
        local start_record=$(( (batch - 1) * BATCH_SIZE + 1 ))
        local end_record=$(( batch * BATCH_SIZE ))
        if [[ $end_record -gt $total_records ]]; then
            end_record=$total_records
        fi
        
        local batch_size=$((end_record - start_record + 1))
        
        echo "=== Processing batch $batch ($start_record-$end_record) ==="
        
        # Extract batch data
        sed -n "${start_record},${end_record}p" "$DATA_FILE" > "batch_${batch}.csv"
        
        # Process batch
        ./ralph-loop.sh for --iterations "$batch_size" --delay 50 --log \
            --config << EOF
loop_type: for
iterations: $batch_size
delay_ms: 50
log_enabled: true
log_format: json
EOF
        
        # Clean up batch file
        rm -f "batch_${batch}.csv"
        
        echo "Batch $batch completed"
    done
    
    echo ""
    echo "All batches processed!"
}

# Function to demonstrate resumability
run_resumable_processing() {
    echo "=== Resumable Data Processing ==="
    echo ""
    
    local total_records=$(wc -l < "$DATA_FILE")
    
    echo "Starting long-running processing with checkpoints..."
    echo "Use Ctrl+C to interrupt, then resume with --resume"
    echo ""
    
    ./ralph-loop.sh for --iterations "$total_records" --delay 50 --checkpoint --log \
        --config << EOF
loop_type: for
iterations: $total_records
delay_ms: 50
log_enabled: true
log_format: json
checkpoint_interval: 50
EOF
    
    echo ""
    echo "Processing completed. Checkpoints saved for resuming."
}

# Function to show monitoring
show_monitoring() {
    echo "=== Processing Monitoring ==="
    echo ""
    
    echo "Available sessions:"
    ./ralph-loop.sh --list-sessions
    
    echo ""
    echo "Current state (if any):"
    if [[ -f "../state/current_state.json" ]]; then
        cat ../state/current_state.json | jq . 2>/dev/null || cat ../state/current_state.json
    else
        echo "No active processing state"
    fi
}

# Function to analyze results
analyze_results() {
    echo "=== Results Analysis ==="
    echo ""
    
    if [[ ! -f "$OUTPUT_FILE" ]]; then
        echo "No results file found. Run processing first."
        return 1
    fi
    
    local total_records=$(wc -l < "$OUTPUT_FILE")
    local processed_records=$((total_records - 1))  # Subtract header
    
    echo "Total records: $processed_records"
    echo ""
    
    # Basic statistics
    echo "Basic Statistics:"
    echo "  Total records: $processed_records"
    
    if command -v bc >/dev/null 2>&1; then
        echo "  Average value: $(tail -n +2 "$OUTPUT_FILE" | cut -d',' -f2 | awk '{sum+=$1} END {print sum/NR}')"
        echo "  Max value: $(tail -n +2 "$OUTPUT_FILE" | cut -d',' -f2 | sort -nr | head -1)"
        echo "  Min value: $(tail -n +2 "$OUTPUT_FILE" | cut -d',' -f2 | sort -n | head -1)"
    fi
    
    echo ""
    
    # Category breakdown
    echo "Category Breakdown:"
    tail -n +2 "$OUTPUT_FILE" | cut -d',' -f3 | sort | uniq -c | while read count category; do
        echo "  Category $category: $count records"
    done
    
    echo ""
    
    # Status breakdown
    echo "Status Breakdown:"
    tail -n +2 "$OUTPUT_FILE" | cut -d',' -f8 | sort | uniq -c | while read count status; do
        echo "  $status: $count records"
    done
    
    echo ""
    echo "Analysis complete. Full results in: $OUTPUT_FILE"
}

# Main execution
case "${1:-help}" in
    "process")
        run_data_processing
        ;;
    "batch")
        run_batch_processing
        ;;
    "resume")
        run_resumable_processing
        ;;
    "monitor")
        show_monitoring
        ;;
    "analyze")
        analyze_results
        ;;
    "setup")
        echo "Setting up data processing environment..."
        mkdir -p logs state
        echo "Environment ready. Use '$0 process' to start."
        ;;
    "help"|"-h"|"--help"|"-?"|"")
        echo "Data Processing Examples for Ralph Loop Agent"
        echo ""
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  process     - Run full data processing"
        echo "  batch       - Run batch processing"
        echo "  resume      - Run resumable processing with checkpoints"
        echo "  monitor     - Show processing status and sessions"
        echo "  analyze     - Analyze processing results"
        echo "  setup       - Set up processing environment"
        echo "  help        - Show this help message"
        echo ""
        echo "Options:"
        echo "  data_file   - Input CSV file (default: data.csv)"
        echo "  batch_size  - Batch size for batch processing (default: 100)"
        echo ""
        echo "Examples:"
        echo "  $0 process"
        echo "  $0 process custom_data.csv"
        echo "  $0 batch 50"
        echo "  $0 resume"
        echo ""
        echo "Input file format: id,value,category,status"
        echo "Output file format: id,value,category,status,processed_value,normalized_value,final_value,status_text"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information."
        exit 1
        ;;
esac