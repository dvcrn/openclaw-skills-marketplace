#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/lib"

echo "Testing library loading..."
echo "Script dir: $SCRIPT_DIR"
echo "Lib dir: $LIB_DIR"

# Test loading config_parser
echo "Testing config_parser.sh..."
if [[ -f "$LIB_DIR/config_parser.sh" ]]; then
    echo "config_parser.sh exists"
    if source "$LIB_DIR/config_parser.sh"; then
        echo "config_parser.sh loaded successfully"
        if command -v config_parser_get >/dev/null 2>&1; then
            echo "config_parser_get command available"
            config_parser_get "help"
        else
            echo "config_parser_get command NOT available"
        fi
    else
        echo "FAILED to load config_parser.sh"
    fi
else
    echo "config_parser.sh NOT FOUND"
fi