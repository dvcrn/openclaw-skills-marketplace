#!/bin/bash
cmd_connections() { echo "=== Active Connections ==="; ss -tunapl 2>/dev/null | head -30 || netstat -tunapl 2>/dev/null | head -30 || echo "ss/netstat not available"; }
cmd_listening() { echo "=== Listening Ports ==="; ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null || echo "Not available"; }
cmd_stats() { echo "=== Connection States ==="; ss -s 2>/dev/null || echo "ss not available"; }
cmd_interfaces() { echo "=== Network Interfaces ==="; ip -brief addr show 2>/dev/null || ifconfig 2>/dev/null | grep -A1 'flags' || echo "Not available"; }
cmd_routes() { echo "=== Routing Table ==="; ip route show 2>/dev/null || route -n 2>/dev/null || echo "Not available"; }
cmd_help() { echo "NetStat - Network Statistics"; echo "Commands: connections | listening | stats | interfaces | routes | help"; }
cmd_info() { echo "NetStat v1.0.0 | Powered by BytesAgain"; }
case "$1" in connections) cmd_connections;; listening) cmd_listening;; stats) cmd_stats;; interfaces) cmd_interfaces;; routes) cmd_routes;; info) cmd_info;; help|"") cmd_help;; *) cmd_help; exit 1;; esac
