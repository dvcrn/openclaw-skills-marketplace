#!/bin/bash
# Install dependencies for Agent Lottery
# Supports: Linux (x86_64, ARM), macOS, Windows (via WSL or Git Bash)

set -e

OS=$(uname -s)
ARCH=$(uname -m)

echo "=== Installing Agent Lottery Dependencies ==="
echo "OS: $OS | Arch: $ARCH"

# Python dependencies
echo "[1/3] Installing Python packages..."
pip3 install base58 ecdsa --break-system-packages 2>/dev/null || pip3 install base58 ecdsa

# Platform-specific installation
if [[ "$OS" == "Linux" ]]; then
    echo "[2/3] Installing cpulimit (Linux)..."
    sudo apt-get update -qq 2>/dev/null || true
    sudo apt-get install -y cpulimit 2>/dev/null || {
        echo "Note: cpulimit not available in repos, trying alternative..."
        # Try yum/dnf for RHEL-based systems
        sudo yum install -y cpulimit 2>/dev/null || sudo dnf install -y cpulimit 2>/dev/null || {
            echo "Warning: Could not install cpulimit. CPU limiting may not work."
        }
    }
    
elif [[ "$OS" == "Darwin" ]]; then
    echo "[2/3] Installing cpulimit (macOS)..."
    if command -v brew &> /dev/null; then
        brew install cpulimit 2>/dev/null || echo "Note: cpulimit install failed, CPU limiting may not work"
    else
        echo "Homebrew not found. Install with: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        echo "Then run: brew install cpulimit"
    fi
    
else
    echo "[2/3] Skipping cpulimit (not available on $OS)"
    echo "Note: CPU limiting requires manual setup on this platform"
fi

# Install cpuminer-opt
echo "[3/3] Installing cpuminer-opt..."

if command -v cpuminer-opt &> /dev/null; then
    echo "cpuminer-opt already installed: $(cpuminer-opt --version 2>&1 | head -1 || echo 'OK')"
    exit 0
fi

# Linux: Try package manager first, then build from source
if [[ "$OS" == "Linux" ]]; then
    # Try apt
    if sudo apt-get install -y cpuminer-opt 2>/dev/null; then
        echo "cpuminer-opt installed from apt"
        exit 0
    fi
    
    # Build from source
    echo "Building cpuminer-opt from source..."
    sudo apt-get install -y build-essential libcurl4-openssl-dev libssl-dev libjansson-dev automake autotools-dev git 2>/dev/null || true
    
    cd /tmp
    rm -rf cpuminer-opt 2>/dev/null || true
    git clone https://github.com/JayDDee/cpuminer-opt.git
    cd cpuminer-opt
    
    ./build.sh
    ./configure --with-curl --with-ssl
    make -j$(nproc 2>/dev/null || echo 2)
    sudo make install
    
    echo "cpuminer-opt built and installed!"

# macOS: Use Homebrew or build
elif [[ "$OS" == "Darwin" ]]; then
    if command -v brew &> /dev/null; then
        # Try homebrew tap
        brew install cpuminer-opt 2>/dev/null || {
            echo "Building cpuminer-opt from source (macOS)..."
            brew install automake autoconf libtool openssl curl jansson
            
            cd /tmp
            rm -rf cpuminer-opt 2>/dev/null || true
            git clone https://github.com/JayDDee/cpuminer-opt.git
            cd cpuminer-opt
            
            export LDFLAGS="-L$(brew --prefix openssl)/lib -L$(brew --prefix curl)/lib"
            export CPPFLAGS="-I$(brew --prefix openssl)/include -I$(brew --prefix curl)/include"
            export PKG_CONFIG_PATH="$(brew --prefix openssl)/lib/pkgconfig:$(brew --prefix curl)/lib/pkgconfig"
            
            ./build.sh
            ./configure --with-curl --with-ssl
            make -j$(sysctl -n hw.ncpu)
            sudo make install
        }
        echo "cpuminer-opt installed!"
    else
        echo "Homebrew required for macOS installation"
        exit 1
    fi

# Windows (Git Bash / WSL)
elif [[ "$OS" == MINGW* ]] || [[ "$OS" == MSYS* ]] || [[ "$OS" == CYGWIN* ]]; then
    echo ""
    echo "=== Windows Detected ==="
    echo "Option 1: Use WSL (Windows Subsystem for Linux)"
    echo "  wsl --install"
    echo "  Then run this script inside WSL"
    echo ""
    echo "Option 2: Download pre-built cpuminer-opt for Windows"
    echo "  https://github.com/JayDDee/cpuminer-opt/releases"
    echo "  Extract and add to PATH"
    echo ""
    echo "Note: CPU limiting on Windows requires third-party tools like:"
    echo "  - Process Throttler"
    echo "  - BES (Battle Encoder Shirase)"
    exit 0
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "To start mining:"
echo "  python3 scripts/wallet.py --generate"
echo "  python3 scripts/miner.py start --cpu 10"
echo ""
