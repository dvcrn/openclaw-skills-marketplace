# AetherCore v3.3.2 Installation Guide

## 🚀 Quick Installation

### Method 1: Simple Installation (Recommended)
```bash
# Clone the repository
git clone https://github.com/AetherClawAI/AetherCore.git
cd AetherCore

# Run the installation script
./install.sh
```

### Method 2: Manual Installation
```bash
# Install Python dependencies
pip3 install orjson ujson python-rapidjson

# Clone the repository
git clone https://github.com/AetherClawAI/AetherCore.git
cd AetherCore

# Verify installation
python3 src/core/json_performance_engine.py --test
```

### Method 3: ClawHub Installation
```bash
# When available on ClawHub
clawhub install aethercore
```

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **Memory**: 2GB RAM
- **Storage**: 100MB free space
- **Operating System**: macOS 10.15+, Ubuntu 20.04+, Windows 10+

### Recommended Requirements
- **Python**: 3.9 or higher
- **Memory**: 4GB RAM
- **Storage**: 500MB free space
- **Network**: Internet connection for dependency installation

## 🔧 Installation Steps

### Step 1: Prerequisites Check
```bash
# Check Python version
python3 --version

# Check pip version
pip3 --version

# Check git
git --version
```

### Step 2: Clone Repository
```bash
# Clone the repository
git clone https://github.com/AetherClawAI/AetherCore.git
cd AetherCore
```

### Step 3: Run Installation
```bash
# Make install.sh executable
chmod +x install.sh

# Run installation
./install.sh
```

### Step 4: Verify Installation
```bash
# Check if AetherCore is installed
python3 src/core/json_performance_engine.py --test

# Run simple tests
python3 run_simple_tests.py
```

## 🐍 Python Dependencies

### Core Dependencies
```bash
# Install core JSON libraries
pip3 install orjson ujson python-rapidjson
```

### Optional Dependencies
```bash
# For additional features
pip3 install psutil  # System monitoring
pip3 install tqdm    # Progress bars
```

## 🖥️ Platform-Specific Instructions

### macOS
```bash
# Install Python 3.9+ from python.org or using existing Python
# Check if Python is installed
python3 --version

# If Python 3.9+ is not installed, download from python.org
# https://www.python.org/downloads/macos/

# Install dependencies
pip3 install orjson ujson python-rapidjson
```

### Ubuntu/Debian Linux
```bash
# Update package list (requires sudo)
sudo apt update

# Install Python 3.9+ (requires sudo)
sudo apt install python3.9 python3-pip

# Install dependencies (no sudo required)
pip3 install orjson ujson python-rapidjson

# Alternative: Use --user flag if you don't have sudo access
# pip3 install --user orjson ujson python-rapidjson
```

### Windows
```bash
# Install Python from python.org
# Download and install Python 3.9+

# Install dependencies
pip install orjson ujson python-rapidjson
```

## 🧪 Post-Installation Testing

### Basic Functionality Test
```bash
# Test JSON performance engine
python3 src/core/json_performance_engine.py --test

# Test CLI interface
python3 src/aethercore_cli.py version
python3 src/aethercore_cli.py help
```

### Comprehensive Testing
```bash
# Run all tests
python3 run_simple_tests.py

# Run honest benchmark
python3 honest_benchmark.py
```

## 🔍 Troubleshooting

### Common Issues

#### Issue 1: Python version too old
```bash
# Check Python version
python3 --version

# If < 3.8, upgrade Python
# macOS: brew upgrade python@3.9
# Ubuntu: sudo apt install python3.9
```

#### Issue 2: Missing dependencies
```bash
# Install missing dependencies
pip3 install orjson ujson python-rapidjson

# If pip not found, install pip
python3 -m ensurepip --upgrade
```

#### Issue 3: Permission denied
```bash
# Make scripts executable
chmod +x install.sh

# Run with appropriate permissions
./install.sh
```

#### Issue 4: Network issues
```bash
# Install only required dependency
pip3 install orjson>=3.9.0
```

## 📊 Installation Verification

### Verification Steps
1. **Check installation**: `python3 src/core/json_performance_engine.py --test`
2. **Check CLI**: `python3 src/aethercore_cli.py version`
3. **Run tests**: `python3 run_simple_tests.py`
4. **Check dependencies**: `pip3 list | grep -E "orjson|ujson|rapidjson"`

### Expected Output
```
✅ AetherCore v3.3.2 installed successfully
✅ JSON performance engine working
✅ CLI interface available
✅ All tests passing
```

## 🎯 Next Steps

### 1. Explore Features
```bash
# Learn about available commands
python3 src/aethercore_cli.py help

# Run performance benchmark
python3 src/core/json_performance_engine.py --test

# Try smart indexing
python3 src/indexing/smart_index_engine.py --help
```

### 2. Read Documentation
- Read `README.md` for overview
- Read `SKILL.md` for detailed usage
- Read `CHANGELOG.md` for version history

### 3. Join Community
- GitHub: https://github.com/AetherClawAI/AetherCore
- Issues: https://github.com/AetherClawAI/AetherCore/issues
- Discussions: GitHub Discussions

## 📝 Notes

### Security Considerations
- AetherCore v3.3.2 is security-focused
- No automatic system modifications
- No controversial scripts
- No external code execution

### Performance Considerations
- JSON parsing: 0.022ms (45,305 ops/sec)
- Data query: 0.003ms (361,064 ops/sec)
- Overall performance: 115,912 ops/sec

### Support
For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue on GitHub

---

**Last Updated**: 2026-03-10 22:55 GMT+8  
**Version**: 3.3.2  
**Status**: Ready for use