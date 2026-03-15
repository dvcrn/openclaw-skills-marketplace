#!/bin/bash

# Basic Loop Example for Ralph Loop Agent
# This script demonstrates basic usage of the Ralph Loop Agent
# with a simple data processing workflow

# Include the Ralph Loop Agent
source "$(dirname "$0")/../ralph-loop.sh"

# Custom callback function for basic data processing
user_callback() {
    local iteration="$1"
    local total="$2"
    local value="$3"
    
    # Basic processing logic
    echo "Processing item $iteration of $total"
    
    # Process the value (this could be any work you need to do)
    if [[ -n "$value" ]]; then
        echo "  Value: $value"
        
        # Simulate some work
        sleep 0.5
        
        # Example processing - you could replace this with your actual work
        result=$((value * 2))
        echo "  Result: $result"
        
        # Write result to a file
        echo "$iteration,$value,$result" >> ./results.csv
    else
        echo "  Processing generic item $iteration"
        sleep 0.3
    fi
    
    # Return 0 for success, 1 for failure
    return 0
}

# Function to demonstrate different loop types
demo_loop_types() {
    echo "=== Ralph Loop Agent - Basic Loop Demo ==="
    echo ""
    
    # Create results file
    echo "iteration,value,result" > results.csv
    
    # Test different loop types
    echo "1. Testing 'for' loop with 5 iterations:"
    ./ralph-loop.sh for --iterations 5 --delay 1000 --log
    echo ""
    
    echo "2. Testing 'for' loop with custom values:"
    ./ralph-loop.sh for --iterations 3 --delay 500
    
    echo ""
    echo "3. Testing resumability features:"
    echo "   Running loop with checkpoint..."
    ./ralph-loop.sh for --iterations 10 --checkpoint --delay 200
    
    echo ""
    echo "4. Listing available sessions:"
    ./ralph-loop.sh --list-sessions
    
    echo ""
    echo "5. Resuming from last state:"
    echo "   (You can test this by interrupting the above loop and running:)"
    echo "   ./ralph-loop.sh --resume"
    
    echo ""
    echo "Demo completed! Check results.csv for output."
}

# Function to run a practical example
practical_example() {
    echo "=== Practical Example: File Processing ==="
    echo ""
    
    # Create a sample file if it doesn't exist
    if [[ ! -f "sample_data.txt" ]]; then
        echo "Creating sample data file..."
        for i in {1..20}; do
            echo "Line $i with data: value_$i" >> sample_data.txt
        done
    fi
    
    echo "Processing sample_data.txt..."
    echo "This would process each line of the file."
    echo ""
    echo "To implement this, modify the user_callback function to:"
    echo "1. Read the file line by line"
    echo "2. Process each line (your custom logic)"
    echo "3. Write results to output"
    echo ""
    echo "Example implementation:"
    echo "  user_callback() {"
    echo "      local iteration=\$1"
    echo "      local total=\$2"
    echo "      # Read the specific line from the file"
    echo "      local line=\$(sed -n \"\$iteration p\" sample_data.txt)"
    echo "      # Process the line"
    echo "      echo \"Processing: \$line\""
    echo "      # Return 0 for success"
    echo "      return 0"
    echo "  }"
    echo ""
    echo "Then run: ./ralph-loop.sh for --iterations 20"
}

# Function to show error handling
error_handling_example() {
    echo "=== Error Handling Example ==="
    echo ""
    
    echo "This script demonstrates error handling features:"
    echo ""
    echo "1. Retry on failure:"
    echo "   ./ralph-loop.sh for --iterations 5 --retry 3 --delay 1000"
    echo ""
    echo "2. Continue on error:"
    echo "   ./ralph-loop.sh for --iterations 5 --continue-on-error --delay 500"
    echo ""
    echo "3. Combined error handling:"
    echo "   ./ralph-loop.sh for --iterations 10 --retry 2 --continue-on-error --delay 300"
    echo ""
    echo "To test error handling, modify the user_callback function to:"
    echo "  return 1  # This will trigger error handling"
    echo ""
    echo "Example:"
    echo "  user_callback() {"
    echo "      local iteration=\$1"
    echo "      local total=\$2"
    echo "      echo \"Processing iteration \$iteration\""
    echo "      # Simulate occasional failure"
    echo "      if [[ \$iteration -eq 3 ]]; then"
    echo "          echo \"Error in iteration \$iteration\" >&2"
    echo "          return 1  # This will trigger retry"
    echo "      fi"
    echo "      return 0"
    echo "  }"
}

# Main execution
case "${1:-}" in
    "demo")
        demo_loop_types
        ;;
    "practical")
        practical_example
        ;;
    "error")
        error_handling_example
        ;;
    "help"|"-h"|"--help"|"-?"|"")
        echo "Basic Loop Examples for Ralph Loop Agent"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  demo     - Run basic loop demonstrations"
        echo "  practical - Show practical file processing example"
        echo "  error    - Show error handling examples"
        echo "  help     - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 demo"
        echo "  $0 practical"
        echo "  $0 error"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information."
        exit 1
        ;;
esac