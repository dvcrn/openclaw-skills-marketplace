#!/bin/bash
# codex-hook daemon starter
# Starts the watcher in the background

# Ensure result directory exists
mkdir -p /tmp/codex-results

# Start watcher daemon
echo "Starting codex-hook watcher daemon..."
nohup ~/bin/watcher.py --daemon --interval 5 > /tmp/codex-results/logs/daemon.log 2>&1 &

# Save PID
echo $! > /tmp/codex-results/watcher.pid

echo "Daemon started (PID: $!)"
echo "Log: tail -f /tmp/codex-results/logs/daemon.log"
