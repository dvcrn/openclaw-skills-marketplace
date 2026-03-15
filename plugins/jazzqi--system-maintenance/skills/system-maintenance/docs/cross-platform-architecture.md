# Cross-Platform Architecture Design

## 📋 Overview

This document outlines the cross-platform architecture design for the **system-maintenance** skill, ensuring compatibility across macOS, Linux, and Windows (with appropriate adaptations).

## 🎯 Design Goals

### Primary Goals:
1. **Maintain macOS compatibility** as primary platform
2. **Support Linux** with minimal changes
3. **Provide Windows compatibility** through abstraction layers
4. **Allow platform-specific optimizations**
5. **Enable community contributions** for other platforms

### Core Principles:
- **Progressive Enhancement**: Start with macOS, add other platforms
- **Modular Design**: Platform-specific code in separate modules
- **Clear Documentation**: Guide users for different platforms
- **Backward Compatibility**: Don't break existing functionality

## 🏗️ Architecture Layers

### 1. **Platform Detection Layer**
```bash
# Detect platform at runtime
detect_platform() {
    case "$(uname -s)" in
        Darwin*)    echo "macos" ;;
        Linux*)     echo "linux" ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        *)          echo "unknown" ;;
    esac
}
```

### 2. **Abstraction Layer**
- **File Paths**: Abstract path separators and locations
- **Process Management**: Platform-specific process detection
- **Service Control**: Different service managers
- **Scheduling**: cron vs Task Scheduler vs launchd

### 3. **Configuration Layer**
- **Platform-specific defaults**
- **Adaptive behavior based on platform**
- **User-overridable settings**

### 4. **Implementation Layer**
- **Core logic** (platform-agnostic)
- **Platform adapters** (platform-specific)
- **Fallback mechanisms** (when platform-specific features unavailable)

## 🔧 Platform-Specific Considerations

### macOS (Current)
- **Process Detection**: `ps aux | grep` or `pgrep`
- **Service Management**: `launchctl`
- **Paths**: `/Users/`, `/tmp/`, `/Library/`
- **Scheduling**: `crontab` or `launchd`
- **Shell**: Bash (modern macOS uses zsh but bash available)

### Linux
- **Process Detection**: `ps aux`, `pgrep`, `systemctl status`
- **Service Management**: `systemctl`, `service`
- **Paths**: `/home/`, `/tmp/`, `/var/log/`
- **Scheduling**: `crontab`
- **Shell**: Bash (standard)

### Windows (with WSL/Cygwin/Git Bash)
- **Process Detection**: `tasklist`, `Get-Process` (PowerShell)
- **Service Management**: `sc`, `net start/stop`
- **Paths**: `C:\Users\`, `%TEMP%`, `\` separator
- **Scheduling**: Task Scheduler, `schtasks`
- **Shell**: Bash (via WSL), PowerShell, CMD

## 📁 Directory Structure for Cross-Platform

```
system-maintenance/
├── 📄 README.md                    # Cross-platform documentation
├── 📄 SKILL.md                     # Skill documentation
├── 📄 package.json                 # Version and metadata
├── 📄 entry.js                     # Skill entry point
├── 🛠️  scripts/                    # Core scripts
│   ├── common/                     # Platform-agnostic functions
│   │   ├── platform-detection.sh   # Platform detection
│   │   ├── logging.sh              # Unified logging
│   │   └── config-loader.sh        # Configuration loading
│   ├── platform/                   # Platform-specific adapters
│   │   ├── macos/                  # macOS implementations
│   │   │   ├── process-detection.sh
│   │   │   ├── service-control.sh
│   │   │   └── paths.sh
│   │   ├── linux/                  # Linux implementations
│   │   │   ├── process-detection.sh
│   │   │   ├── service-control.sh
│   │   │   └── paths.sh
│   │   └── windows/                # Windows implementations
│   │       ├── process-detection.ps1
│   │       ├── service-control.ps1
│   │       └── paths.ps1
│   ├── main/                       # Main script entry points
│   │   ├── weekly-optimization.sh  # Uses common and platform modules
│   │   ├── real-time-monitor.sh
│   │   ├── log-management.sh
│   │   ├── daily-maintenance.sh
│   │   └── install-maintenance-system.sh
│   └── utils/                      # Utility scripts
│       ├── check-before-commit.sh
│       └── test-platform.sh
├── 📚  examples/                   # Examples
├── 📝  docs/                       # Documentation
│   ├── cross-platform-architecture.md  # This document
│   ├── macos-setup.md              # macOS-specific setup
│   ├── linux-setup.md              # Linux-specific setup
│   └── windows-setup.md            # Windows-specific setup
├── ⚙️  config/                     # Configuration
│   ├── defaults.yaml               # Default configuration
│   ├── macos.yaml                  # macOS-specific defaults
│   ├── linux.yaml                  # Linux-specific defaults
│   └── windows.yaml                # Windows-specific defaults
└── 📁 tests/                       # Platform-specific tests
    ├── macos-tests.sh
    ├── linux-tests.sh
    └── windows-tests.ps1
```

## 🔄 Migration Path (Current → Cross-Platform)

### Phase 1: Architecture Preparation (Current)
- ✅ Analyze current platform dependencies
- ✅ Document platform-specific code
- ✅ Create cross-platform design document
- ✅ Add platform detection to existing scripts

### Phase 2: Modularization
- Extract common functions to `scripts/common/`
- Create platform detection module
- Add configuration loading system
- Update main scripts to use modules

### Phase 3: Platform Adapters
- Create `scripts/platform/macos/` with current logic
- Create `scripts/platform/linux/` stubs
- Create `scripts/platform/windows/` stubs
- Update scripts to use platform adapters

### Phase 4: Testing & Validation
- Test on macOS (ensure backward compatibility)
- Test on Linux (virtual machine or CI)
- Test on Windows (WSL or virtual machine)
- Fix platform-specific issues

### Phase 5: Documentation & Release
- Update documentation for all platforms
- Create platform-specific setup guides
- Update SKILL.md with cross-platform information
- Release as new version

## 🛠️ Technical Implementation Details

### 1. **Platform Detection Script** (`scripts/common/platform-detection.sh`)
```bash
#!/bin/bash

detect_platform() {
    local os_name=$(uname -s 2>/dev/null || echo "Unknown")
    local os_version=$(uname -r 2>/dev/null || echo "")
    
    case "$os_name" in
        Darwin*)
            echo "macos"
            ;;
        Linux*)
            # Detect Linux distribution
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                echo "linux-$ID"
            else
                echo "linux"
            fi
            ;;
        CYGWIN*|MINGW*|MSYS*)
            echo "windows"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

get_platform_info() {
    local platform=$(detect_platform)
    echo "Platform: $platform"
    echo "Shell: $SHELL"
    echo "Home: $HOME"
    echo "Temp: $TMPDIR"
    return 0
}
```

### 2. **Path Abstraction** (`scripts/common/paths.sh`)
```bash
#!/bin/bash

get_temp_dir() {
    case "$(detect_platform)" in
        macos|linux*)
            echo "/tmp"
            ;;
        windows)
            echo "$TEMP"
            ;;
        *)
            echo "/tmp"
            ;;
    esac
}

get_openclaw_home() {
    case "$(detect_platform)" in
        macos)
            echo "$HOME/.openclaw"
            ;;
        linux*)
            echo "$HOME/.openclaw"
            ;;
        windows)
            echo "$HOME/OpenClaw"
            ;;
        *)
            echo "$HOME/.openclaw"
            ;;
    esac
}
```

### 3. **Process Detection Abstraction**
```bash
#!/bin/bash

detect_gateway_process() {
    local platform=$(detect_platform)
    
    case "$platform" in
        macos|linux*)
            # Unix/Linux/Mac process detection
            ps aux | grep "openclaw-gateway" | grep -v grep | awk '{print $2}' | head -1
            ;;
        windows)
            # Windows process detection (if using WSL/bash)
            if command -v tasklist >/dev/null 2>&1; then
                tasklist | grep "openclaw-gateway" | awk '{print $2}' | head -1
            else
                # Fallback for WSL
                ps aux | grep "openclaw-gateway" | grep -v grep | awk '{print $2}' | head -1
            fi
            ;;
        *)
            echo ""
            ;;
    esac
}
```

## 📋 Platform Support Matrix

| Feature | macOS | Linux | Windows (WSL) | Windows (Native) |
|---------|-------|-------|---------------|------------------|
| **Core Scripts** | ✅ Full | ✅ Full | ✅ Most | ⚠️ Limited |
| **Process Detection** | ✅ | ✅ | ✅ | ⚠️ Requires adaptation |
| **Service Control** | ✅ launchctl | ✅ systemctl | ⚠️ Limited | ⚠️ sc/tasklist |
| **Cron Scheduling** | ✅ crontab | ✅ crontab | ✅ crontab | ❌ Task Scheduler |
| **Path Compatibility** | ✅ | ✅ | ✅ | ⚠️ Path separator issues |
| **Log Management** | ✅ | ✅ | ✅ | ⚠️ Permission differences |
| **Real-time Monitoring** | ✅ | ✅ | ✅ | ⚠️ Process detection差异 |

## 🚀 Implementation Roadmap

### Short-term (v1.3.0)
1. Add platform detection to existing scripts
2. Create common functions module
3. Document current platform limitations
4. Add configuration system for platform defaults

### Medium-term (v1.4.0)
1. Complete Linux adapter implementation
2. Add Linux-specific testing
3. Update documentation for Linux users
4. Create Linux installation guide

### Long-term (v2.0.0)
1. Complete Windows adapter implementation
2. Add Windows-specific testing
3. Create Windows installation guide
4. Full cross-platform support

## 📝 Documentation Strategy

### For Users:
- **README.md**: Clear platform requirements section
- **SKILL.md**: Platform support matrix
- **Setup Guides**: Platform-specific setup instructions
- **Troubleshooting**: Platform-specific issues and solutions

### For Developers:
- **Architecture Docs**: Cross-platform design principles
- **API Documentation**: Platform abstraction APIs
- **Contribution Guide**: How to add support for new platforms
- **Testing Guide**: Platform-specific testing procedures

## 🔧 Configuration System

### Platform-Specific Defaults
```yaml
# config/defaults.yaml
global:
  log_retention_days: 7
  monitoring_interval: 300
  health_score_threshold: 70

# config/macos.yaml
platform: macos
paths:
  temp_dir: /tmp
  home_dir: /Users
  log_dir: /tmp/openclaw
process_detection:
  command: ps aux | grep
service_control:
  command: launchctl

# config/linux.yaml  
platform: linux
paths:
  temp_dir: /tmp
  home_dir: /home
  log_dir: /var/log/openclaw
process_detection:
  command: pgrep
service_control:
  command: systemctl

# config/windows.yaml
platform: windows
paths:
  temp_dir: ${TEMP}
  home_dir: ${USERPROFILE}
  log_dir: ${TEMP}/openclaw
process_detection:
  command: tasklist
service_control:
  command: sc
```

## 🧪 Testing Strategy

### Platform Testing Matrix
| Test Type | macOS | Linux | Windows |
|-----------|-------|-------|---------|
| Unit Tests | ✅ | ✅ | ✅ |
| Integration Tests | ✅ | ✅ | ⚠️ |
| End-to-End Tests | ✅ | ⚠️ | ❌ |
| CI/CD Pipeline | ✅ | ✅ | ⚠️ |

### Test Environments
1. **macOS**: Local development, GitHub Actions macOS runner
2. **Linux**: Docker containers, GitHub Actions Ubuntu runner
3. **Windows**: GitHub Actions Windows runner, WSL

## 🤝 Community Contribution Guidelines

### Adding New Platform Support
1. **Fork the repository**
2. **Create platform adapter directory**: `scripts/platform/new-platform/`
3. **Implement required interfaces**:
   - Process detection
   - Service control  
   - Path utilities
   - Platform detection
4. **Add platform configuration**: `config/new-platform.yaml`
5. **Write tests**: `tests/new-platform-tests.sh`
6. **Update documentation**: Add platform-specific setup guide
7. **Submit pull request**

### Platform Interface Requirements
```bash
# Required functions for each platform adapter
- detect_process(process_name)
- control_service(service_name, action)
- get_platform_paths()
- check_platform_dependencies()
```

## 📊 Success Metrics

### Technical Metrics
- **Code Modularity**: >80% platform-agnostic code
- **Test Coverage**: >90% for core functions
- **Platform Support**: 3+ platforms with full functionality
- **Documentation Coverage**: All platforms documented

### User Metrics  
- **Installation Success Rate**: >95% across all platforms
- **Issue Resolution Time**: <48 hours for platform-specific issues
- **Community Contributions**: Active contributions for new platforms
- **User Satisfaction**: High ratings for cross-platform support

## 🔮 Future Enhancements

### Advanced Platform Features
1. **Containerized Execution**: Docker support for platform-independent testing
2. **Cloud Platform Support**: AWS, Azure, GCP specific optimizations
3. **Mobile Platforms**: iOS/Android via OpenClaw mobile
4. **Edge Platforms**: Raspberry Pi, IoT devices

### Automation Enhancements
1. **Auto-detection**: Automatic platform detection and configuration
2. **Self-healing**: Automatic fixes for platform-specific issues
3. **Adaptive Behavior**: Scripts adapt to platform capabilities
4. **Performance Optimization**: Platform-specific performance tuning

---

## 🎯 Conclusion

This cross-platform architecture design provides a clear path for making the **system-maintenance** skill compatible with macOS, Linux, and Windows platforms. By following a modular, abstraction-based approach, we can:

1. **Maintain current macOS functionality** while extending to other platforms
2. **Enable community contributions** for platform-specific implementations
3. **Provide clear documentation** for users on all platforms
4. **Ensure long-term maintainability** through clean architecture

The phased implementation approach allows incremental development while ensuring backward compatibility and quality at each step.

**Next Steps**: Begin Phase 1 by adding platform detection to existing scripts and creating the common functions module.