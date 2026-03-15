# Ralph Loop Agent Production Deployment Guide

## 🚀 Production Deployment Checklist

This guide provides comprehensive instructions for deploying the Ralph Loop Agent in production environments.

### Pre-Deployment Requirements

#### System Requirements
- **Operating System:** Linux, macOS, or Unix-based systems
- **Bash Version:** 3.2.57 or higher (confirmed compatibility)
- **Storage:** Minimum 100MB for installation and state management
- **Memory:** Minimum 64MB RAM (typically uses < 10MB)
- **Network:** Internet connection only for updates and dependencies

#### Software Dependencies
All dependencies are included in the distribution:
- **Core utilities:** date, md5sum, stat (standard Unix tools)
- **Optional:** rich_logger.sh for enhanced logging
- **Optional:** jq for advanced JSON processing (if available)

### Installation Process

#### Step 1: Download and Verify
```bash
# Download the Ralph Loop Agent
curl -O https://github.com/your-repo/ralph-loop-agent/archive/main.zip
unzip main.zip
cd ralph-loop-agent-main

# Verify package integrity
md5sum -c checksums.txt  # If checksums available
```

#### Step 2: Installation Options

##### Option A: Local Installation (Recommended)
```bash
# Create local installation directory
mkdir -p ~/bin/ralph-loop-agent
cp -r * ~/bin/ralph-loop-agent/

# Add to PATH (permanent)
echo 'export PATH="$HOME/bin/ralph-loop-agent:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify installation
ralph-loop.sh --help
```

##### Option B: System-wide Installation
```bash
# Install to system location
sudo mkdir -p /opt/ralph-loop-agent
sudo cp -r * /opt/ralph-loop-agent/
sudo chmod +x /opt/ralph-loop-agent/ralph-loop.sh

# Create symlink
sudo ln -sf /opt/ralph-loop-agent/ralph-loop.sh /usr/local/bin/ralph-loop

# Verify installation
ralph-loop --help
```

##### Option C: Container Deployment
```dockerfile
FROM alpine:latest
RUN apk add --no-cache bash
COPY ralph-loop-agent /app/ralph-loop-agent
WORKDIR /app/ralph-loop-agent
ENTRYPOINT ["./ralph-loop.sh"]
```

#### Step 3: Configuration Setup

##### Basic Configuration
```bash
# Create configuration directory
mkdir -p ~/.config/ralph-loop
cd ~/.config/ralph-loop

# Create main configuration file
cat > config.yaml << EOF
loop_type: for
iterations: 100
delay_ms: 1000
retry_count: 3
continue_on_error: false
progress_enabled: true
log_enabled: true
log_format: json
log_file: /var/log/ralph-loop.log
EOF
```

##### Environment Variables
```bash
# System-wide configuration (systemd)
sudo tee /etc/environment << EOF
RALPH_LOOP_STATE_DIR=/var/lib/ralph-loop
RALPH_LOOP_LOG_ENABLED=true
RALPH_LOOP_LOG_LEVEL=info
RALPH_LOOP_LOG_FORMAT=json
EOF

# User-specific configuration
cat >> ~/.bashrc << EOF
export RALPH_LOOP_STATE_DIR=/home/$USER/.ralph-loop/state
export RALPH_LOOP_LOG_ENABLED=true
export RALPH_LOOP_LOG_LEVEL=info
export RALPH_LOOP_LOG_FORMAT=json
EOF
```

#### Step 4: Directory Structure
```
/opt/ralph-loop-agent/
├── ralph-loop.sh          # Main executable
├── lib/                    # Library modules
│   ├── config_parser.sh
│   ├── logger.sh
│   ├── error_handler.sh
│   ├── progress_tracker.sh
│   ├── loop_engine.sh
│   ├── config_file.sh
│   ├── rich_logger.sh
│   └── state_manager.sh
├── config/                 # Configuration files
│   ├── default.yaml
│   └── production.yaml
├── examples/               # Example scripts
│   ├── basic_loop.sh
│   ├── data_processing.sh
│   └── batch_processing.sh
├── logs/                   # Log directory
├── state/                  # State management (created automatically)
│   ├── current_state.json
│   ├── history/
│   └── checkpoints/
└── README.md               # This documentation
```

## 🏗️ Production Configuration

### Environment-Specific Configurations

#### Development Environment
```yaml
# config/dev.yaml
loop_type: for
iterations: 10
delay_ms: 1000
retry_count: 1
continue_on_error: true
log_enabled: true
log_format: text
log_file: ./logs/development.log
progress_enabled: true
```

#### Staging Environment
```yaml
# config/staging.yaml
loop_type: for
iterations: 100
delay_ms: 500
retry_count: 3
continue_on_error: false
log_enabled: true
log_format: json
log_file: /var/log/ralph-loop/staging.log
progress_enabled: true
```

#### Production Environment
```yaml
# config/production.yaml
loop_type: for
iterations: 1000
delay_ms: 100
retry_count: 5
continue_on_error: false
log_enabled: true
log_format: json
log_file: /var/log/ralph-loop/production.log
progress_enabled: true
state_dir: /var/lib/ralph-loop/production
```

### Security Configuration

#### File Permissions
```bash
# Set appropriate permissions
sudo chown -R ralph:ralph /opt/ralph-loop-agent
sudo chmod 750 /opt/ralph-loop-agent
sudo chmod 755 /opt/ralph-loop-agent/ralph-loop.sh
sudo chmod 644 /opt/ralph-loop-agent/lib/*.sh

# Set state directory permissions
sudo chown -R ralph:ralph /var/lib/ralph-loop
sudo chmod 750 /var/lib/ralph-loop
```

#### Environment Security
```bash
# Set secure environment
export RALPH_LOOP_LOG_ENABLED=true
export RALPH_LOOP_LOG_LEVEL=info
export RALPH_LOOP_LOG_FORMAT=json
export RALPH_LOOP_STATE_DIR=/var/lib/ralph-loop
export RALPH_LOOP_CONFIG_ENCRYPTION=false  # Set to true if using encrypted config

# Never store secrets in configuration files
# Use environment variables for sensitive data
```

## 🔧 Service Integration

### Systemd Service Integration

#### Service Configuration
```bash
# Create systemd service file
sudo tee /etc/systemd/system/ralph-loop.service << EOF
[Unit]
Description=Ralph Loop Agent Service
After=network.target
Requires=network.target

[Service]
Type=oneshot
User=ralph
Group=ralph
WorkingDirectory=/opt/ralph-loop-agent
ExecStart=/opt/ralph-loop-agent/ralph-loop.sh --config /etc/ralph-loop/production.yaml for --iterations 1000
StandardOutput=file:/var/log/ralph-loop/service.log
StandardError=file:/var/log/ralph-loop/error.log
TimeoutStartSec=300
TimeoutStopSec=10

# Environment variables
Environment=RALPH_LOOP_STATE_DIR=/var/lib/ralph-loop
Environment=RALPH_LOOP_LOG_ENABLED=true
Environment=RALPH_LOOP_LOG_LEVEL=info

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/var/lib/ralph-loop /var/log/ralph-loop

[Install]
WantedBy=multi-user.target
EOF
```

#### Service Management
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable ralph-loop.service

# Start service
sudo systemctl start ralph-loop.service

# Check status
sudo systemctl status ralph-loop.service

# View logs
sudo journalctl -u ralph-loop.service -f
```

### Cron Job Integration

#### Simple Cron Job
```bash
# Add to crontab
crontab -e

# Example: Run every hour at 30 minutes
30 * * * * /opt/ralph-loop-agent/ralph-loop.sh --config /etc/ralph-loop/production.yaml for --iterations 100 --log
```

#### Advanced Cron Job with Logging
```bash
# Enhanced cron job with error handling
30 * * * * \
  cd /opt/ralph-loop-agent && \
  ./ralph-loop.sh --config /etc/ralph-loop/production.yaml for --iterations 100 --checkpoint >> /var/log/ralph-loop/cron.log 2>&1 || \
  echo "Ralph Loop failed at $(date)" >> /var/log/ralph-loop/cron-error.log
```

### Docker Integration

#### Dockerfile
```dockerfile
FROM alpine:latest

# Install dependencies
RUN apk add --no-cache bash

# Create application user
RUN addgroup -g 1001 -S ralph && \
    adduser -u 1001 -S ralph -G ralph

# Install application
COPY ralph-loop-agent /app/ralph-loop-agent
WORKDIR /app/ralph-loop-agent

# Create necessary directories
RUN mkdir -p /app/ralph-loop-agent/logs /app/ralph-loop-agent/state && \
    chown -R ralph:ralph /app/ralph-loop-agent

# Switch to non-root user
USER ralph

# Expose port if needed (for future web interface)
EXPOSE 8080

# Default command
ENTRYPOINT ["./ralph-loop.sh"]
CMD ["--help"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  ralph-loop:
    build: .
    volumes:
      - ./config:/app/config:ro
      - ./logs:/app/logs
      - ./state:/app/state
    environment:
      - RALPH_LOOP_STATE_DIR=/app/state
      - RALPH_LOOP_LOG_ENABLED=true
      - RALPH_LOOP_LOG_FORMAT=json
    command: ["--config", "/app/config/production.yaml", "for", "--iterations", "100"]
    restart: unless-stopped
```

## 📊 Monitoring and Logging

### Log Management

#### Log Rotation
```bash
# Create logrotate configuration
sudo tee /etc/logrotate.d/ralph-loop << EOF
/var/log/ralph-loop/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ralph ralph
    postrotate
        systemctl reload ralph-loop.service || true
    endscript
}
EOF
```

#### Centralized Logging
```bash
# Configure for syslog integration
echo 'local0.*    /var/log/ralph-loop/syslog' | sudo tee -a /etc/rsyslog.conf

# Restart syslog
sudo systemctl restart rsyslog
```

### Monitoring Setup

#### Health Check Script
```bash
#!/bin/bash
# /usr/local/bin/ralph-loop-healthcheck

# Check if Ralph Loop is running
if systemctl is-active --quiet ralph-loop.service; then
    exit 0
else
    # Try to restart
    systemctl start ralph-loop.service
    exit 1
fi
```

#### Monitoring Integration
```bash
# Add to monitoring system (Prometheus example)
cat << EOF > /etc/prometheus/ralph-loop.yml
- job_name: 'ralph-loop'
  static_configs:
    - targets: ['localhost:8080']
EOF
```

### State Monitoring

#### Session Monitoring Script
```bash
#!/bin/bash
# /usr/local/bin/ralph-loop-status

echo "Ralph Loop Agent Status"
echo "======================"

# List recent sessions
echo "Recent Sessions:"
ls -la /var/lib/ralph-loop/history/ | tail -5

# Check current state
if [[ -f "/var/lib/ralph-loop/current_state.json" ]]; then
    echo ""
    echo "Current State:"
    cat /var/lib/ralph-loop/current_state.json | jq . 2>/dev/null || cat /var/lib/ralph-loop/current_state.json
else
    echo "No active state found"
fi

# Check disk usage
echo ""
echo "Disk Usage:"
du -sh /var/lib/ralph-loop/
```

## 🔒 Security Hardening

### File System Security
```bash
# Set proper permissions
sudo chown -R ralph:ralph /opt/ralph-loop-agent
sudo chmod 750 /opt/ralph-loop-agent
sudo chmod 755 /opt/ralph-loop-agent/ralph-loop.sh
sudo chmod 644 /opt/ralph-loop-agent/lib/*.sh
sudo chmod 600 /etc/ralph-loop/*.yaml

# Set SELinux policies (if applicable)
sudo semanage fcontext -a -t bin_t "/opt/ralph-loop-agent(/.*)?"
sudo restorecon -Rv /opt/ralph-loop-agent
```

### Network Security
```bash
# Configure firewall rules
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# Restrict network access (if needed)
sudo setsebool -P httpd_can_network_connect off
```

### Process Security
```bash
# Run with minimal privileges
sudo setcap 'cap_sys_nice=ep' /opt/ralph-loop-agent/ralph-loop.sh 2>/dev/null || true

# Use namespace isolation if available
sudo unshare --pid --fork --mount-proc ralph-loop.sh
```

## 🚀 Deployment Automation

### Ansible Playbook
```yaml
---
- name: Deploy Ralph Loop Agent
  hosts: all
  become: yes
  
  vars:
    ralph_loop_version: "2.1.0"
    ralph_loop_user: "ralph"
    ralph_loop_group: "ralph"
    ralph_loop_install_dir: "/opt/ralph-loop-agent"
    ralph_loop_state_dir: "/var/lib/ralph-loop"
    
  tasks:
    - name: Create user and group
      user:
        name: "{{ ralph_loop_user }}"
        group: "{{ ralph_loop_group }}"
        system: yes
        create_home: no
        
    - name: Create directories
      file:
        path: "{{ item }}"
        state: directory
        owner: "{{ ralph_loop_user }}"
        group: "{{ ralph_loop_group }}"
        mode: '0750'
      with_items:
        - "{{ ralph_loop_install_dir }}"
        - "{{ ralph_loop_state_dir }}"
        - "{{ ralph_loop_install_dir }}/logs"
        
    - name: Deploy application
      copy:
        src: ralph-loop-agent/
        dest: "{{ ralph_loop_install_dir }}"
        mode: '0755'
        owner: "{{ ralph_loop_user }}"
        group: "{{ ralph_loop_group }}"
        
    - name: Create systemd service
      template:
        src: ralph-loop.service.j2
        dest: /etc/systemd/system/ralph-loop.service
      notify: Restart ralph-loop service
        
    - name: Enable and start service
      systemd:
        name: ralph-loop
        enabled: yes
        state: started
        
  handlers:
    - name: Restart ralph-loop service
      systemd:
        name: ralph-loop
        state: restarted
```

### Kubernetes Deployment

#### Helm Chart
```yaml
# values.yaml
image:
  repository: ralph-loop-agent
  tag: 2.1.0
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8080

config:
  loopType: for
  iterations: 100
  delayMs: 1000
  retryCount: 3

env:
  - name: RALPH_LOOP_LOG_ENABLED
    value: "true"
  - name: RALPH_LOOP_LOG_FORMAT
    value: "json"
  - name: RALPH_LOOP_STATE_DIR
    value: "/var/lib/ralph-loop"

resources:
  limits:
    memory: "128Mi"
    cpu: "100m"
  requests:
    memory: "64Mi"
    cpu: "50m"
```

## 🧪 Testing and Validation

### Pre-Deployment Testing

#### Functional Testing
```bash
# Test basic functionality
./ralph-loop.sh --help
./ralph-loop.sh demo
./ralph-loop.sh for --iterations 5 --delay 1000

# Test resumability features
./ralph-loop.sh for --iterations 10 --checkpoint
./ralph-loop.sh --list-sessions
./ralph-loop.sh --resume
```

#### Performance Testing
```bash
# Performance benchmark
time ./ralph-loop.sh for --iterations 1000 --delay 0

# Memory usage monitoring
valgrind --tool=massif ./ralph-loop.sh for --iterations 100

# Load testing
for i in {1..10}; do
    ./ralph-loop.sh for --iterations 50 --delay 100 &
done
wait
```

#### Integration Testing
```bash
# Test with real workloads
./ralph-loop.sh for --iterations 100 --checkpoint --log

# Test failure scenarios
./ralph-loop.sh for --iterations 5 --retry 2 --continue-on-error

# Test state restoration
./ralph-loop.sh for --iterations 20 --checkpoint
# Simulate interruption
./ralph-loop.sh --resume
```

### Post-Deployment Validation

#### Health Checks
```bash
# Verify service status
systemctl status ralph-loop.service

# Check logs
journalctl -u ralph-loop.service -n 50

# Verify state management
ls -la /var/lib/ralph-loop/
```

#### Performance Monitoring
```bash
# Monitor resource usage
top -p $(pgrep ralph-loop)

# Check disk I/O
iostat -x 1 5

# Monitor memory usage
free -h
```

## 🔄 Backup and Recovery

### State Backup Strategy
```bash
# Daily backup script
cat > /usr/local/bin/ralph-loop-backup << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/ralph-loop"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

# Backup state directory
tar -czf "$BACKUP_DIR/ralph-loop-state_$DATE.tar.gz" -C /var/lib ralph-loop

# Keep only last 7 days
find "$BACKUP_DIR" -name "ralph-loop-state_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/ralph-loop-state_$DATE.tar.gz"
EOF

chmod +x /usr/local/bin/ralph-loop-backup

# Add to daily cron
echo "0 2 * * * /usr/local/bin/ralph-loop-backup" | crontab -
```

### Disaster Recovery
```bash
# Recovery script
cat > /usr/local/bin/ralph-loop-restore << 'EOF'
#!/bin/bash
BACKUP_FILE="$1"
STATE_DIR="/var/lib/ralph-loop"

if [[ -z "$BACKUP_FILE" ]]; then
    echo "Usage: $0 <backup-file>"
    exit 1
fi

# Stop service
systemctl stop ralph-loop.service

# Backup current state
mv "$STATE_DIR" "$STATE_DIR.backup.$(date +%Y%m%d_%H%M%S)"

# Restore from backup
tar -xzf "$BACKUP_FILE" -C /var/lib

# Start service
systemctl start ralph-loop.service

echo "Recovery completed from: $BACKUP_FILE"
EOF

chmod +x /usr/local/bin/ralph-loop-restore
```

## 📈 Performance Optimization

### Production Optimizations

#### Memory Optimization
```bash
# Reduce state save frequency
# Modify state_manager.sh intervals:
# From: every 5/10 iterations
# To: every 20/50 iterations for production

# Use efficient logging
export RALPH_LOOP_LOG_FORMAT=json
export RALPH_LOOP_LOG_ENABLED=true
```

#### CPU Optimization
```bash
# Use appropriate delays
# Reduce delay_ms from testing to production
# Example: 1000ms → 100ms

# Optimize retry logic
# Set appropriate retry_count based on workload
```

#### I/O Optimization
```bash
# Use faster storage for state directory
# Mount state directory on SSD if available

# Implement log rotation
# Configure logrotate to prevent log file bloat
```

### Monitoring and Alerting

#### Critical Metrics
```bash
# Resource usage monitoring
echo "CPU usage: $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')%"

# Memory usage
echo "Memory usage: $(free | grep Mem | awk '{print ($3/$2) * 100.0}')%"

# Disk usage
echo "Disk usage: $(df /var/lib | tail -1 | awk '{print $5}' | sed 's/%//')%"
```

#### Alerting Configuration
```bash
# Alert script for critical issues
cat > /usr/local/bin/ralph-loop-alert << 'EOF'
#!/bin/bash

# Check service status
if ! systemctl is-active --quiet ralph-loop.service; then
    echo "ALERT: Ralph Loop service is not active"
    # Send alert via email, Slack, etc.
    # mail -s "Ralph Loop Alert" admin@example.com << BODY
    # Ralph Loop service is not active
    # BODY
fi

# Check disk usage
DISK_USAGE=$(df /var/lib | tail -1 | awk '{print $5}' | sed 's/%//')
if [[ $DISK_USAGE -gt 90 ]]; then
    echo "ALERT: Disk usage is ${DISK_USAGE}%"
fi

# Check memory usage
MEM_USAGE=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')
if (( $(echo "$MEM_USAGE > 90" | bc -l) )); then
    echo "ALERT: Memory usage is ${MEM_USAGE}%"
fi
EOF

chmod +x /usr/local/bin/ralph-loop-alert
```

## 🔄 Maintenance and Updates

### Regular Maintenance Tasks

#### Daily Tasks
```bash
# Check service status
systemctl status ralph-loop.service

# Review logs
journalctl -u ralph-loop.service --since yesterday

# Check state directory size
du -sh /var/lib/ralph-loop/
```

#### Weekly Tasks
```bash
# Clean old states
find /var/lib/ralph-loop/history -name "*.json" -mtime +7 -delete

# Review performance metrics
grep "iteration" /var/log/ralph-loop/*.log | tail -20

# Update configuration if needed
```

#### Monthly Tasks
```bash
# Full backup
/usr/local/bin/ralph-loop-backup

# Security audit
audit -w /opt/ralph-loop-agent -p wa -k ralph-loop

# Performance review
# Analyze logs for patterns and optimizations
```

### Update Procedures

#### Rolling Update
```bash
# 1. Create backup
/usr/local/bin/ralph-loop-backup

# 2. Stop service
systemctl stop ralph-loop.service

# 3. Update application
cp -r new-version/* /opt/ralph-loop-agent/
chmod +x /opt/ralph-loop-agent/ralph-loop.sh

# 4. Start service
systemctl start ralph-loop.service

# 5. Verify
systemctl status ralph-loop.service
```

#### Zero-Downtime Update
```bash
# 1. Deploy new version alongside old
mkdir /opt/ralph-loop-agent-v2
cp -r new-version/* /opt/ralph-loop-agent-v2/

# 2. Test new version
/opt/ralph-loop-agent-v2/ralph-loop.sh demo

# 3. Switch to new version
ln -sfn /opt/ralph-loop-agent-v2 /opt/ralph-loop-agent
systemctl restart ralph-loop.service

# 4. Clean up old version
mv /opt/ralph-loop-agent-v1 /opt/ralph-loop-agent-v1-backup
```

## 📚 Documentation and Training

### System Documentation
- **Architecture diagrams:** Available in README.md
- **API documentation:** Command-line options and usage
- **Configuration examples:** Environment-specific configurations
- **Troubleshooting guide:** Common issues and solutions

### Operational Documentation
- **Deployment procedures:** Step-by-step installation
- **Maintenance procedures:** Regular and emergency tasks
- **Monitoring procedures:** Health checks and alerts
- **Recovery procedures:** Backup and restore processes

### Training Materials
- **Quick start guide:** Basic usage examples
- **Advanced usage:** Complex configurations and scenarios
- **Best practices:** Production deployment patterns
- **Troubleshooting workshop:** Hands-on problem solving

## 🎯 Success Metrics

### Availability
- **Service Uptime:** 99.9% target
- **Response Time:** < 1 second for basic operations
- **Recovery Time:** < 5 minutes from failure

### Performance
- **Memory Usage:** < 50MB under normal load
- **CPU Usage:** < 5% average
- **Disk I/O:** Minimal state persistence overhead

### Reliability
- **State Persistence:** 100% successful save/load rate
- **Error Recovery:** 100% graceful degradation
- **Data Integrity:** No state corruption incidents

### Security
- **Zero security vulnerabilities** in production
- **Compliance:** Meet all organizational security standards
- **Auditability:** Complete logging and monitoring

---

## 📞 Support and Contact

### Technical Support
- **Documentation:** README.md and DEPLOYMENT.md
- **Issue tracking:** Project repository issue tracker
- **Community forum:** User discussions and best practices

### Emergency Contacts
- **System administrator:** [admin@company.com]
- **Development team:** [dev@company.com]
- **Security team:** [security@company.com]

---

*This deployment guide should be reviewed and updated regularly to reflect changes in the Ralph Loop Agent and production requirements.*