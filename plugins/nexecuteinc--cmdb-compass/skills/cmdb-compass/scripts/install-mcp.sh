#!/usr/bin/env bash
set -e

echo "Installing CMDB Compass MCP server..."

# Check Python 3.10+
PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
  echo "Error: Python 3 is required. Install it from https://python.org" >&2
  exit 1
fi

PY_VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$($PYTHON -c "import sys; print(sys.version_info.major)")
PY_MINOR=$($PYTHON -c "import sys; print(sys.version_info.minor)")

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
  echo "Error: Python 3.10+ is required. Found: $PY_VERSION" >&2
  exit 1
fi

echo "Python $PY_VERSION found."

# Install from PyPI
echo "Installing cmdb-compass from PyPI..."
$PYTHON -m pip install --upgrade cmdb-compass

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Set your ServiceNow credentials:"
echo "     export SERVICENOW_INSTANCE_URL=https://your-instance.service-now.com"
echo "     export SERVICENOW_USERNAME=your_username"
echo "     export SERVICENOW_PASSWORD=your_password"
echo ""
echo "  2. Add to Claude Desktop config (~/.config/claude/config.json):"
echo '     {'
echo '       "mcpServers": {'
echo '         "cmdb-compass": {'
echo '           "command": "python",'
echo '           "args": ["-m", "servicenow_mcp.server"],'
echo '           "env": {'
echo '             "SERVICENOW_INSTANCE_URL": "https://your-instance.service-now.com",'
echo '             "SERVICENOW_USERNAME": "your_username",'
echo '             "SERVICENOW_PASSWORD": "your_password"'
echo '           }'
echo '         }'
echo '       }'
echo '     }'
echo ""
echo "  3. Restart Claude Desktop and ask: 'Calculate CMDB health score for cmdb_ci_server'"
