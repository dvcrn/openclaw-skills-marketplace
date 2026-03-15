# Ralph Loop Agent

A powerful, production-ready loop execution system with advanced logging, progress tracking, and resumability features.

## 🚀 Features

### Phase 1: Core Loop Engine
- **Multiple Loop Types:** `for`, `while`, `until`, `range`
- **Flexible Configuration:** Iterations, delays, retry logic
- **Progress Tracking:** Real-time progress display with percentage and ETA
- **Error Handling:** Automatic retry and graceful degradation

### Phase 2: Advanced Features
- **Rich Logging:** JSON format with rotation and compression
- **Configuration Management:** Multiple sources (env, files, command-line)
- **Progress Enhancement:** Advanced statistics and performance metrics
- **Module Architecture:** Extensible design with 8 specialized modules

### Phase 3: Resumability
- **State Persistence:** JSON-based state saving and loading
- **Checkpoint System:** Automatic and manual checkpoints
- **Session Management:** Unique session identifiers and recovery
- **Progress Tracking:** Real-time updates with percentage, remaining iterations, and ETA

## 📦 Installation

### Requirements
- Bash 3.2+ (minimum version)
- Standard Unix utilities (date, md5sum, stat)
- Optional: rich_logger.sh for enhanced logging

### Quick Setup
```bash
# Clone or download the Ralph Loop Agent
cd /path/to/ralph-loop-agent

# Make the script executable
chmod +x ralph-loop.sh

# Test installation
./ralph-loop.sh --help
```

### Dependencies
The system includes all required libraries:
- `config_parser.sh` - Configuration management
- `logger.sh` - Basic logging
- `error_handler.sh` - Error handling and recovery
- `progress_tracker.sh` - Progress tracking and statistics
- `loop_engine.sh` - Core loop execution
- `config_file.sh` - Configuration file handling
- `rich_logger.sh` - Enhanced logging (optional)
- `state_manager.sh` - State persistence and resumability

## 🎯 Usage

### Basic Loop Execution
```bash
# Basic for loop with 5 iterations
./ralph-loop.sh for --iterations 5

# While loop with delay
./ralph-loop.sh while --delay 1000 --iterations 10

# Until loop with retry
./ralph-loop.sh until --retry 3 --iterations 5

# Range loop
./ralph-loop.sh range --iterations 5
```

### Advanced Configuration
```bash
# With progress tracking
./ralph-loop.sh for --iterations 10 --progress

# With logging to file
./ralph-loop.sh for --iterations 5 --log --log-file output.log

# With error handling
./ralph-loop.sh for --iterations 5 --retry 2 --continue-on-error
```

### Resumability Features
```bash
# List available sessions
./ralph-loop.sh --list-sessions

# Create checkpoint before execution
./ralph-loop.sh for --iterations 100 --checkpoint

# Resume from last state
./ralph-loop.sh --resume

# Resume from specific session
./ralph-loop.sh --resume --session <SESSION_ID>
```

### Demo and Testing
```bash
# Run demonstration
./ralph-loop.sh demo

# Get help and usage
./ralph-loop.sh --help
```

## 📋 Command Reference

### Loop Types
| Type | Description | Use Case |
|------|-------------|----------|
| `for` | Fixed iteration count | Known number of iterations |
| `while` | Conditional execution | Until condition becomes false |
| `until` | Execute until condition | Until condition becomes true |
| `range` | Custom numeric range | Sequential numeric operations |

### Command-Line Options

#### Basic Options
| Option | Description | Default |
|--------|-------------|---------|
| `--type, -t TYPE` | Loop type | `for` |
| `--iterations, -n COUNT` | Number of iterations | `5` |
| `--delay, -d MS` | Delay between iterations (ms) | `0` |
| `--retry, -r COUNT` | Retry count on failure | `0` |

#### Advanced Options
| Option | Description | Default |
|--------|-------------|---------|
| `--continue-on-error, -c` | Continue on error | `false` |
| `--no-progress` | Disable progress display | Progress enabled |
| `--log` | Enable logging | `false` |
| `--log-file PATH` | Log file path | Console output |
| `--log-format FORMAT` | Log format (json/text) | `text` |
| `--config, -f FILE` | Configuration file | None |

#### Resumability Options
| Option | Description | Default |
|--------|-------------|---------|
| `--resume, -r` | Resume from last state | `false` |
| `--session, -s ID` | Resume from specific session | None |
| `--checkpoint` | Create checkpoint before execution | `false` |
| `--list-sessions` | List available sessions | `false` |

#### System Options
| Option | Description |
|--------|-------------|
| `--help, -h` | Show help information |
| `--version` | Show version information |
| `--demo` | Run demonstration |

## ⚙️ Configuration

### Environment Variables
```bash
# Enable verbose logging
export LOG_ENABLED=true

# Set log level
export LOG_LEVEL=info

# Set log format
export LOG_FORMAT=json

# Custom state directory
export STATE_DIR=/custom/path/state
```

### Configuration Files
The system supports YAML and JSON configuration files:

```yaml
# config.yaml
loop_type: for
iterations: 10
delay_ms: 500
retry_count: 2
continue_on_error: false
progress_enabled: true
log_enabled: true
log_format: json
```

```json
// config.json
{
  "loop_type": "for",
  "iterations": 10,
  "delay_ms": 500,
  "retry_count": 2,
  "continue_on_error": false,
  "progress_enabled": true,
  "log_enabled": true,
  "log_format": "json"
}
```

### Configuration Priority
1. Command-line arguments (highest)
2. Configuration files
3. Environment variables
4. Default values (lowest)

## 🏗️ Architecture

### Module System
The Ralph Loop Agent is built on a modular architecture:

```
ralph-loop.sh (Main Entry Point)
├── config_parser.sh    # Configuration management
├── logger.sh           # Basic logging
├── error_handler.sh    # Error handling
├── progress_tracker.sh # Progress tracking
├── loop_engine.sh      # Core loop execution
├── config_file.sh      # File-based configuration
├── rich_logger.sh      # Enhanced logging (optional)
└── state_manager.sh    # State persistence (resumability)
```

### State Management
The resumability system maintains comprehensive state:

- **Session ID:** Unique identifier for each execution
- **Progress:** Current iteration, percentage, remaining iterations
- **Timing:** Start time, last update, estimated completion
- **Configuration:** Configuration hash for change detection
- **Statistics:** Success/failure counts, checkpoint count

### Data Persistence
States are stored in JSON format for maximum compatibility:

```json
{
  "session_id": "20260308_154500_12345_1710199230",
  "timestamp": "20260308_154505",
  "loop_type": "for",
  "total_iterations": 100,
  "current_iteration": 25,
  "progress_percentage": 25,
  "status": "running",
  "remaining_iterations": 75,
  "estimated_completion": "15:55:10"
}
```

## 🔄 Resumability System

### Automatic Checkpoints
- Every 5 iterations for `demo` callback
- Every 10 iterations for `user_callback`
- On completion (100% or failure)

### Manual Checkpoints
- Use `--checkpoint` flag to create checkpoint before execution
- Checkpoints stored with unique timestamps
- Available for restoration at any time

### Session Management
- Unique session identifiers based on timestamp and process ID
- Comprehensive state history
- Session listing with metadata
- Automatic cleanup (7-day retention)

### Recovery Process
```bash
# 1. List available sessions
./ralph-loop.sh --list-sessions

# 2. Choose session to resume
./ralph-loop.sh --resume --session <SESSION_ID>

# 3. Or resume from last state
./ralph-loop.sh --resume
```

## 🔧 Custom Callbacks

### User Callback Function
Override the `user_callback()` function in your script:

```bash
#!/bin/bash
# my_loop_script.sh

# Include Ralph Loop Agent
source ralph-loop-agent/ralph-loop.sh

# Custom callback function
user_callback() {
    local iteration="$1"
    local total="$2"
    local value="$3"
    
    # Your custom logic here
    echo "Processing item $iteration of $total"
    if [[ -n "$value" ]]; then
        echo "  Value: $value"
        # Add your processing logic
    fi
    
    # Return 0 for success, 1 for failure
    return 0
}

# Execute the loop
./ralph-loop.sh for --iterations 10
```

### Demo Callback
The system includes a built-in demo callback for testing:

```bash
./ralph-loop.sh demo
```

## 📊 Progress Tracking

### Real-time Statistics
- **Current iteration:** Iteration number being processed
- **Total iterations:** Target number of iterations
- **Progress percentage:** Calculated completion percentage
- **Remaining iterations:** Iterations remaining to completion
- **Estimated completion:** Time of completion (ETA)

### Performance Metrics
- **Start time:** When the loop began
- **Last update:** Most recent state save
- **Duration:** Total elapsed time
- **Speed:** Iterations per second

### Progress Display
```bash
# Progress bar and statistics
[===================] 75% (75/100) ETA: 00:02:30
```

## 🔒 Security and Reliability

### Error Handling
- **Automatic retry:** Configurable retry count
- **Graceful degradation:** Continue on optional
- **Error recovery:** Automatic state preservation
- **Logging:** Complete error documentation

### Data Integrity
- **Checksum validation:** Configuration hash verification
- **Atomic operations:** State saves are atomic
- **Backup system:** Automatic state history
- **Cleanup:** Automatic cleanup of old files

### Performance Optimization
- **Minimal overhead:** Efficient state management
- **Selective saves:** Smart checkpoint intervals
- **Memory efficient:** Array-based storage
- **Resource friendly:** Clean shutdown on interrupt

## 🚀 Production Deployment

### Step 1: Installation
```bash
# 1. Download or clone the repository
git clone <repository-url>
cd ralph-loop-agent

# 2. Make executable
chmod +x ralph-loop.sh

# 3. Test installation
./ralph-loop.sh --help
./ralph-loop.sh demo
```

### Step 2: Configuration
```bash
# 1. Create configuration file (optional)
cat > config.yaml << EOF
loop_type: for
iterations: 1000
delay_ms: 100
retry_count: 3
log_enabled: true
log_format: json
EOF

# 2. Set environment variables (optional)
export STATE_DIR=/var/lib/ralph-loop
export LOG_ENABLED=true
export LOG_LEVEL=info
```

### Step 3: Integration
```bash
# Include in your scripts
#!/bin/bash

source ralph-loop-agent/ralph-loop.sh

# Your custom callback
user_callback() {
    # Your business logic here
    process_data "$1" "$2"
    return 0
}

# Execute loop with configuration
./ralph-loop.sh --config config.yaml for --iterations 1000
```

### Step 4: Automation
```bash
# Systemd service example
[Unit]
Description=Ralph Loop Agent Service
After=network.target

[Service]
Type=oneshot
User=ralph
ExecStart=/usr/local/bin/ralph-loop.sh --config /etc/ralph-loop/config.yaml for --iterations 1000
WorkingDirectory=/opt/ralph-loop-agent
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Step 5: Monitoring
```bash
# Check status
./ralph-loop.sh --list-sessions

# Resume interrupted work
./ralph-loop.sh --resume

# Create backup checkpoint
./ralph-loop.sh --checkpoint for --iterations 1000
```

## 🐛 Troubleshooting

### Common Issues

#### Permission Errors
```bash
# Fix permissions
chmod +x ralph-loop.sh
chmod 755 lib/*.sh
```

#### Configuration Errors
```bash
# Validate configuration
./ralph-loop.sh --config config.yaml --help

# Check syntax
bash -n ralph-loop.sh
bash -n lib/*.sh
```

#### State Issues
```bash
# Clear state if corrupted
rm -rf state/

# List sessions manually
ls state/history/
```

#### Performance Issues
```bash
# Reduce checkpoint frequency
# Modify state_manager.sh intervals
# Use smaller iterations for testing
```

### Debug Mode
Enable verbose logging for troubleshooting:

```bash
# Enable detailed logging
export LOG_LEVEL=debug
export LOG_ENABLED=true

# Run with verbose output
./ralph-loop.sh --log for --iterations 5
```

## 📈 Performance Optimization

### Best Practices
1. **Smart checkpointing:** Use appropriate intervals for your use case
2. **Efficient callbacks:** Minimize work in callback functions
3. **Memory management:** Clean up resources in callbacks
4. **Error handling:** Implement proper error recovery
5. **Configuration:** Use appropriate delay and retry settings

### Benchmarking
```bash
# Performance test
time ./ralph-loop.sh for --iterations 1000 --delay 0

# Memory usage monitoring
valgrind --tool=massif ./ralph-loop.sh for --iterations 100
```

## 🔄 Changelog

### Version 2.1.0 (Current)
- **Phase 1:** Basic loop execution
- **Phase 2:** Advanced features and logging
- **Phase 3:** Resumability and state management
- **Complete documentation:** Production deployment guide

## 📞 Support

### Documentation
- This README.md file
- In-line help with `--help`
- Example scripts in the repository

### Community
- Report issues on the project repository
- Contribute improvements and documentation
- Share use cases and best practices

## 📄 License

This project is released under the MIT License. See LICENSE file for details.

---

*The Ralph Loop Agent - Powering reliable, resumable loop operations since 2026*