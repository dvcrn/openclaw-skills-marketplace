#!/bin/bash
# Nova Act Usability Testing Skill - Quick Setup Script

set -e

echo ""
echo "🦅 Nova Act Usability Testing Skill - Quick Setup"
echo "============================================================"
echo ""

# Find Python
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ Python not found. Please install Python 3.8 or newer."
    exit 1
fi

echo "✅ Found Python: $($PYTHON --version)"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "📂 Skill directory: $SCRIPT_DIR"
echo ""

# Run Python setup script
echo "🔧 Running setup..."
echo ""
$PYTHON "$SCRIPT_DIR/setup.py"

exit $?
