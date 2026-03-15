#!/bin/bash

# EkyBot Telemetry Daemon Starter
# Starts continuous telemetry streaming as a background process

set -e

CONFIG_DIR="$HOME/.openclaw/ekybot-connector"
CONFIG_FILE="$CONFIG_DIR/config.json"
PID_FILE="$CONFIG_DIR/telemetry.pid"
LOG_FILE="$CONFIG_DIR/telemetry.log"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_detail() {
    echo -e "${BLUE}[DETAIL]${NC} $1"
}

usage() {
    echo "Usage: $0 [action] [options]"
    echo "Actions:"
    echo "  start      Start telemetry daemon (default)"
    echo "  stop       Stop telemetry daemon"
    echo "  restart    Restart telemetry daemon"
    echo "  status     Check daemon status"
    echo ""
    echo "Options:"
    echo "  --interval <seconds>   Telemetry interval (default: 300)"
    echo "  --verbose              Enable verbose logging"
    echo "  --help                Show this help"
}

# Default values
ACTION="start"
INTERVAL=300
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        start|stop|restart|status)
            ACTION="$1"
            shift
            ;;
        --interval)
            INTERVAL="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Check if configured
if [[ ! -f "$CONFIG_FILE" ]] && [[ "$ACTION" != "status" ]]; then
    print_error "EkyBot connector not configured. Run scripts/register_workspace.sh first."
    exit 1
fi

# Create config directory if needed
mkdir -p "$CONFIG_DIR"

# Function to check if daemon is running
is_running() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            # PID file exists but process is dead
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to start daemon
start_daemon() {
    if is_running; then
        print_warning "Telemetry daemon is already running (PID: $(cat "$PID_FILE"))"
        return 1
    fi
    
    print_status "Starting EkyBot telemetry daemon..."
    
    # Get script directory
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    
    # Build command
    local cmd="$SCRIPT_DIR/send_telemetry.sh --continuous --interval $INTERVAL"
    if [[ "$VERBOSE" == "true" ]]; then
        cmd="$cmd --verbose"
    fi
    
    # Start daemon in background
    nohup $cmd >> "$LOG_FILE" 2>&1 &
    local pid=$!
    
    # Save PID
    echo $pid > "$PID_FILE"
    
    # Wait a moment and check if it's still running
    sleep 2
    if is_running; then
        print_status "✅ Telemetry daemon started (PID: $pid)"
        print_detail "Log file: $LOG_FILE"
        print_detail "Interval: ${INTERVAL}s"
        return 0
    else
        print_error "Failed to start telemetry daemon"
        if [[ -f "$LOG_FILE" ]]; then
            print_error "Last log entries:"
            tail -10 "$LOG_FILE"
        fi
        return 1
    fi
}

# Function to stop daemon
stop_daemon() {
    if ! is_running; then
        print_warning "Telemetry daemon is not running"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    print_status "Stopping EkyBot telemetry daemon (PID: $pid)..."
    
    # Send TERM signal
    kill -TERM "$pid" 2>/dev/null
    
    # Wait for graceful shutdown
    local count=0
    while is_running && [[ $count -lt 10 ]]; do
        sleep 1
        ((count++))
    done
    
    # Force kill if still running
    if is_running; then
        print_warning "Daemon didn't stop gracefully, force killing..."
        kill -KILL "$pid" 2>/dev/null
        sleep 1
    fi
    
    # Clean up PID file
    rm -f "$PID_FILE"
    
    if is_running; then
        print_error "Failed to stop telemetry daemon"
        return 1
    else
        print_status "✅ Telemetry daemon stopped"
        return 0
    fi
}

# Function to show status
show_status() {
    print_status "🔍 EkyBot Telemetry Daemon Status"
    echo
    
    if is_running; then
        local pid=$(cat "$PID_FILE")
        print_status "✅ Running (PID: $pid)"
        
        # Show process info
        if command -v ps &> /dev/null; then
            print_detail "Process info:"
            ps -p "$pid" -o pid,ppid,etime,cmd 2>/dev/null | tail -1
        fi
        
        # Show recent log entries
        if [[ -f "$LOG_FILE" ]]; then
            print_detail "Recent log entries (last 5):"
            tail -5 "$LOG_FILE" | while read line; do
                echo "  $line"
            done
        fi
    else
        print_warning "❌ Not running"
    fi
    
    # Show configuration
    if [[ -f "$CONFIG_FILE" ]]; then
        print_detail "Configuration:"
        local workspace_id=$(cat "$CONFIG_FILE" | python3 -c "import sys, json; print(json.load(sys.stdin)['workspace_id'])" 2>/dev/null)
        local workspace_name=$(cat "$CONFIG_FILE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('workspace_name', 'unknown'))" 2>/dev/null)
        local interval=$(cat "$CONFIG_FILE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('telemetry_interval', 300))" 2>/dev/null)
        echo "  Workspace: $workspace_name ($workspace_id)"
        echo "  Interval: ${interval}s"
    fi
    
    # Show files
    echo
    print_detail "Files:"
    echo "  Config: $CONFIG_FILE"
    echo "  PID file: $PID_FILE"
    echo "  Log file: $LOG_FILE"
    if [[ -f "$LOG_FILE" ]]; then
        local log_size=$(du -h "$LOG_FILE" | cut -f1)
        echo "  Log size: $log_size"
    fi
}

# Main execution
case "$ACTION" in
    start)
        start_daemon
        ;;
    stop)
        stop_daemon
        ;;
    restart)
        if is_running; then
            stop_daemon
        fi
        sleep 1
        start_daemon
        ;;
    status)
        show_status
        ;;
    *)
        print_error "Unknown action: $ACTION"
        usage
        exit 1
        ;;
esac