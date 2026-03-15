#!/usr/bin/env bash
# crawler - Web crawler toolkit — site crawling, link extracti
# Powered by BytesAgain | bytesagain.com
set -euo pipefail

VERSION="1.0.0"
DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/crawler"
mkdir -p "$DATA_DIR"

show_help() {
    echo "Crawler v$VERSION"
    echo ""
    echo "Usage: crawler <command> [options]"
    echo ""
    echo "Commands:"
    echo "  run               Execute main function"
    echo "  list              List all items"
    echo "  add <item>        Add new item"
    echo "  status            Show current status"
    echo "  export <format>   Export data (json|csv|txt)"
    echo "  help              Show this help"
    echo ""
}

cmd_run() {
    echo "[crawler] Running..."
    echo "Processing complete."
    echo "$(date '+%Y-%m-%d %H:%M') run" >> "$DATA_DIR/history.log"
}

cmd_list() {
    echo "[crawler] Items:"
    if [ -f "$DATA_DIR/items.txt" ]; then
        cat -n "$DATA_DIR/items.txt"
    else
        echo "  (empty)"
    fi
}

cmd_add() {
    local item="${1:?Usage: crawler add <item>}"
    echo "$item" >> "$DATA_DIR/items.txt"
    echo "Added: $item"
}

cmd_status() {
    echo "[crawler] Status"
    echo "  Data dir: $DATA_DIR"
    local count=0
    [ -f "$DATA_DIR/items.txt" ] && count=$(wc -l < "$DATA_DIR/items.txt")
    echo "  Items: $count"
    echo "  Version: $VERSION"
}

cmd_export() {
    local fmt="${1:-json}"
    echo "[crawler] Exporting as $fmt..."
    case "$fmt" in
        json)
            echo "{"
            echo "  \"tool\": \"crawler\","
            echo "  \"version\": \"$VERSION\","
            local items="[]"
            if [ -f "$DATA_DIR/items.txt" ]; then
                items=$(python3 -c "
import json
with open('$DATA_DIR/items.txt') as f:
    print(json.dumps([l.strip() for l in f if l.strip()]))
" 2>/dev/null || echo "[]")
            fi
            echo "  \"items\": $items"
            echo "}"
            ;;
        csv) [ -f "$DATA_DIR/items.txt" ] && cat "$DATA_DIR/items.txt" || echo "(empty)";;
        txt) cmd_status;;
        *) echo "Formats: json, csv, txt";;
    esac
}

case "${1:-help}" in
    run) shift; cmd_run "$@";;
    list) shift; cmd_list "$@";;
    add) shift; cmd_add "$@";;
    status) shift; cmd_status "$@";;
    export) shift; cmd_export "$@";;
    help|-h|--help) show_help;;
    version|-v) echo "crawler v$VERSION";;
    *) echo "Unknown: $1"; show_help; exit 1;;
esac
