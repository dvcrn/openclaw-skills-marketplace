# Ralph Loop Agent Troubleshooting Guide

This guide provides solutions for common issues encountered when using the Ralph Loop Agent.

## 🔍 Common Issues and Solutions

### Installation Issues

#### Permission Denied Errors
**Problem:**
```
chmod: ralph-loop.sh: Permission denied
bash: ralph-loop.sh: command not found
```

**Solution:**
```bash
# Make the script executable
chmod +x ralph-loop.sh

# Or for system-wide installation
sudo chmod +x /opt/ralph-loop-agent/ralph-loop.sh
sudo chmod +x /usr/local/bin/ralph-loop

# Check permissions
ls -la ralph-loop.sh
```

#### Library Loading Errors
**Problem:**
``./ralph-loop.sh: line XX: lib/config_parser.sh: No such file or directory``

**Solution:**
```bash
# Ensure all library files exist
ls -la lib/

# If missing files, download complete package
# Or restore from backup

# Verify library permissions
chmod +x lib/*.sh
```

#### Missing Dependencies
**Problem:**
``bash: md5sum: command not found
bash: bc: command not found``

**Solution:**
```bash
# On Alpine Linux
apk add bash coreutils bc

# On Ubuntu/Debian
sudo apt-get install bash coreutils bc

# On CentOS/RHEL
sudo yum install bash coreutils bc

# Alternative: Use built-in commands only
# The system works with minimal dependencies
```

### Configuration Issues

#### YAML Configuration Errors
**Problem:**
```
YAML parsing error: while scanning a simple key
```

**Solution:**
```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Check for proper indentation
# Use spaces, not tabs
# Ensure consistent indentation (2 or 4 spaces)

# Example correct format:
loop_type: for
iterations: 10
delay_ms: 1000
```

#### Environment Variable Issues
**Problem:**
```
Environment variable RALPH_LOOP_LOG_LEVEL not recognized
```

**Solution:**
```bash
# Set environment variables correctly
export RALPH_LOOP_LOG_LEVEL=info
export RALPH_LOOP_LOG_ENABLED=true

# Or use set command in script
export RALPH_LOOP_LOG_LEVEL="info"

# Verify environment is loaded
echo $RALPH_LOOP_LOG_LEVEL
```

### Loop Execution Issues

#### Loop Type Not Recognized
**Problem:**
```
ERROR: Invalid loop type: unknown_type
```

**Solution:**
```bash
# Check available loop types
./ralph-loop.sh --help

# Use supported loop types: for, while, until, range
./ralph-loop.sh for --iterations 5
./ralph-loop.sh while --iterations 5
```

#### Invalid Iteration Count
**Problem:**
```
ERROR: Invalid iterations: not_a_number
```

**Solution:**
```bash
# Use numeric values only
./ralph-loop.sh for --iterations 10    # Correct
./ralph-loop.sh for --iterations "10"  # Also works
./ralph-loop.sh for --iterations abc   # Error

# For large numbers, use appropriate format
./ralph-loop.sh for --iterations 10000
```

### Progress Tracking Issues

#### Progress Display Not Working
**Problem:**
```
No progress bar shown
```

**Solution:**
```bash
# Enable progress display
./ralph-loop.sh --progress for --iterations 5

# Or check configuration
grep progress_enabled config.yaml

# Enable in configuration:
# progress_enabled: true
```

#### ETA Calculation Issues
**Problem:**
```
ETA shows "Calculating..." for too long
```

**Solution:**
```bash
# Ensure callback function is implemented
# The ETA calculation requires proper timing

# Check if date command is available
which date

# Callback should update state properly:
user_callback() {
    local iteration="$1"
    local total="$2"
    # Update state with timing information
    state_manager_set "last_update" "$(date +%s)"
    # ... rest of callback
}
```

### Error Handling Issues

#### Retry Not Working
**Problem:**
```
Retry mechanism not activating on failure
```

**Solution:**
```bash
# Enable retry configuration
./ralph-loop.sh for --iterations 5 --retry 3

# Check callback return code
# Callback should return 1 on failure to trigger retry

user_callback() {
    # ... processing ...
    if [[ condition -eq true ]]; then
        return 1  # Trigger retry
    fi
    return 0
}
```

#### Continue on Error Not Working
**Problem:**
```
Script stops on first error even with --continue-on-error
```

**Solution:**
```bash
# Ensure continue_on_error is set correctly
./ralph-loop.sh for --iterations 5 --continue-on-error

# Check callback implementation
# Callback should handle errors gracefully

user_callback() {
    # ... processing ...
    if [[ error_condition ]]; then
        echo "Error in iteration $iteration" >&2
        return 1  # Error, but processing continues
    fi
    return 0
}
```

### State Management Issues

#### State Persistence Problems
**Problem:**
```
Cannot restore previous state
```

**Solution:**
```bash
# Check state directory permissions
ls -la state/
chmod 755 state/

# Verify state files exist
ls -la state/history/
ls -la state/checkpoints/

# Check state file integrity
cat state/current_state.json
```

#### Session Not Found
**Problem:**
```
ERROR: No state found for session ID: xxx
```

**Solution:**
```bash
# List available sessions
./ralph-loop.sh --list-sessions

# Check correct session ID format
# Session IDs should be: YYYYMMDD_HHMMSS_PID_TIMESTAMP

# Use most recent session:
./ralph-loop.sh --resume

# Or specify correct session ID
./ralph-loop.sh --resume --session 20260308_150000_12345_1710199230
```

### Logging Issues

#### Log Files Not Created
**Problem:**
```
Log files not being created
```

**Solution:**
```bash
# Check log directory permissions
mkdir -p logs
chmod 755 logs

# Enable logging in configuration
log_enabled: true
log_file: "./logs/app.log"

# Check file system space
df -h

# Ensure write permissions
touch test.log && rm test.log
```

#### Log Format Issues
**Problem:**
```
JSON logs not properly formatted
```

**Solution:**
```bash
# Validate JSON format
python3 -c "import json; json.load(open('logs/app.log'))"

# Check log format configuration
log_format: json

# For manual testing, generate sample JSON:
echo '{"timestamp": "2026-03-08", "level": "info", "message": "test"}' > test.json
```

### Performance Issues

#### Slow Execution
**Problem:**
```
Loop execution is slower than expected
```

**Solution:**
```bash
# Check delay configuration
./ralph-loop.sh for --iterations 5 --delay 0  # No delay

# Profile callback performance
time ./ralph-loop.sh for --iterations 100

# Optimize callback function
# Remove unnecessary operations from callback

# Use appropriate batch sizes
```

#### High Memory Usage
**Problem:**
```
Memory usage is too high
```

**Solution:**
```bash
# Enable memory-efficient mode
# Set memory_efficient: true in configuration

# Check memory usage
free -h
ps aux | grep ralph-loop

# Reduce state save frequency
# Increase checkpoint_interval in state_manager.sh
```

### Security Issues

#### Permission Issues with State Files
**Problem:**
```
Cannot access state directory
```

**Solution:**
```bash
# Set proper permissions
sudo chown -R $USER:$USER state/
sudo chmod -R 755 state/

# Or set state directory with user permissions
export STATE_DIR="./user_state"
mkdir -p user_state
chmod 755 user_state
```

#### Configuration Security
**Problem:**
```
Configuration contains sensitive information
```

**Solution:**
```bash
# Use environment variables for sensitive data
export DATABASE_PASSWORD="secret"
export API_KEY="secret_key"

# Never commit sensitive config to version control
# Add config/secrets.yaml to .gitignore

# Use encrypted configuration files
```

## 🛠️ Debug Mode

### Enable Debug Mode
```bash
# Enable debug output
export LOG_LEVEL=debug
export DEBUG_MODE=true

# Run with verbose output
./ralph-loop.sh --verbose for --iterations 5

# Check debug logs
grep DEBUG logs/app.log
```

### Debug Commands
```bash
# Test configuration loading
./ralph-loop.sh --help

# Test individual components
bash -n lib/config_parser.sh
bash -n lib/state_manager.sh

# Validate syntax
bash -n ralph-loop.sh
```

## 🔄 Recovery Procedures

### Corrupted State Files
```bash
# Backup corrupted files
mv state state_corrupted
mkdir state

# Clean state directory
rm -rf state/*
mkdir -p state/history state/checkpoints

# Restart with fresh state
./ralph-loop.sh for --iterations 10
```

### Interrupted Execution
```bash
# List available sessions
./ralph-loop.sh --list-sessions

# Resume from last checkpoint
./ralph-loop.sh --resume

# Or resume from specific session
./ralph-loop.sh --resume --session <SESSION_ID>
```

### Log Recovery
```bash
# Compress old logs
tar -czf logs_backup.tar.gz logs/

# Create new log directory
mkdir -p logs_new
mv logs logs_old

# Start fresh logging
./ralph-loop.sh --log for --iterations 10
```

## 📊 Performance Monitoring

### System Monitoring
```bash
# Monitor process
top -p $(pgrep ralph-loop)

# Check memory usage
ps aux | grep ralph-loop | awk '{print $4" "$11}'

# Monitor disk I/O
iostat -x 1 5

# Check network usage
netstat -i
```

### Application Monitoring
```bash
# Check progress
./ralph-loop.sh --list-sessions

# Monitor state files
ls -la state/history/
ls -la state/checkpoints/

# Check log sizes
du -sh logs/
```

## 🔧 Common Script Fixes

### Fix Script Permissions
```bash
#!/bin/bash

# Fix all script permissions
chmod +x ralph-loop.sh
chmod +x lib/*.sh
chmod +x examples/*.sh

# Verify permissions
ls -la | grep ralph
```

### Fix Configuration Paths
```bash
#!/bin/bash

# Ensure correct paths in configuration
sed -i 's|/wrong/path/to|/correct/path/to|g' config/*.yaml

# Validate paths
cat config/production.yaml | grep -E "path|dir"
```

### Fix Environment Variables
```bash
#!/bin/bash

# Set environment variables correctly
export RALPH_LOOP_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export STATE_DIR="$RALPH_LOOP_SCRIPT_DIR/state"
export LOG_DIR="$RALPH_LOOP_SCRIPT_DIR/logs"

# Verify environment
echo "SCRIPT_DIR: $RALPH_LOOP_SCRIPT_DIR"
echo "STATE_DIR: $STATE_DIR"
echo "LOG_DIR: $LOG_DIR"
```

## 🚨 Emergency Procedures

### System Freeze
```bash
# Kill hanging processes
pkill -f ralph-loop.sh

# Clean up state files
rm -f state/current_state.json

# Restart with fresh state
./ralph-loop.sh for --iterations 5
```

### Disk Space Issues
```bash
# Clean old logs
find logs/ -name "*.log" -mtime +30 -delete

# Clean old state files
find state/ -name "*.json" -mtime +7 -delete

# Compress large files
gzip -9 logs/*.log
```

### Security Breach
```bash
# Revoke access
chmod 000 state/
chmod 000 logs/

# Change passwords/keys
# Rotate API keys
# Audit configuration files

# Restore from backup
cp -r backup/* .
```

## 📞 Support and Contact

### Issue Reporting
When reporting issues, include:
1. **System Information:** OS, bash version, hardware
2. **Error Messages:** Complete error output
3. **Configuration:** Relevant configuration files
4. **Steps to Reproduce:** Detailed reproduction steps
5. **Expected vs Actual:** What should happen vs what happens

### Debug Information
```bash
# Collect system information
echo "=== System Information ==="
uname -a
bash --version
echo "=== Configuration ==="
cat config/*.yaml 2>/dev/null || echo "No config files found"
echo "=== Environment ==="
env | grep -i ralph
echo "=== Disk Space ==="
df -h .
echo "=== Memory ==="
free -h
```

### Performance Metrics
```bash
# Collect performance data
echo "=== Performance ==="
time ./ralph-loop.sh for --iterations 10
echo "=== Memory Usage ==="
ps aux | grep ralph-loop | awk '{print $4" "$11}'
echo "=== Disk Usage ==="
du -sh ./*
```

---

This troubleshooting guide should help resolve most common issues with the Ralph Loop Agent. For additional support, please check the documentation or contact the development team.