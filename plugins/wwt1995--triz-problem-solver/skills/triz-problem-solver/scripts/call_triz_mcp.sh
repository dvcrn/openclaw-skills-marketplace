#!/bin/bash
# TRIZ MCP service invocation script

MCP_URL="https://qa-eureka-service.zhihuiya.com/eureka-rd-agent-mcp/rd-agent-mcp-triz-mind/mcp"

if [ -z "$1" ]; then
    echo "Usage: ./call_triz_mcp.sh \"your problem description\""
    exit 1
fi

PROBLEM="$1"

curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 1,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"auto_run_triz_mind\",
      \"arguments\": {
        \"message\": \"$PROBLEM\"
      }
    }
  }"