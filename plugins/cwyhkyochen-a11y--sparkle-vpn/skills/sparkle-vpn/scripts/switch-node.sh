#!/bin/bash
# Switch Sparkle VPN node
# Usage: switch-node.sh <node_name>

API_URL="http://127.0.0.1:9090"
NODE_NAME="$1"

if [ -z "$NODE_NAME" ]; then
    echo "❌ 错误: 请提供节点名称"
    echo "用法: switch-node.sh <节点名称>"
    echo ""
    echo "常用节点:"
    echo "  自动选择"
    echo "  故障转移" 
    echo "  香港-HKG-01-VL"
    echo "  香港-HKG-02-VL"
    echo "  香港-HKT-01-VL"
    echo "  新加坡-SIN-01-VL"
    echo "  日本-TYO-01-VL"
    echo "  美国-SJC-01-VL"
    exit 1
fi

# Check if mihomo is running
if ! pgrep -f "mihomo" > /dev/null; then
    echo "❌ VPN 未运行，请先启动 VPN"
    exit 1
fi

# URL encode the node name (handle Chinese characters)
ENCODED_NAME=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$NODE_NAME'''))")

echo "🔄 正在切换到节点: $NODE_NAME"

# Send switch request
RESPONSE=$(curl -s -X PUT "${API_URL}/proxies/DirectACCESS" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$NODE_NAME\"}")

if [ -z "$RESPONSE" ]; then
    echo "✅ 已切换到: $NODE_NAME"
    
    # Show current status
    echo ""
    curl -s "${API_URL}/proxies/DirectACCESS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    current = data.get('now', '未知')
    print(f'当前节点: {current}')
except:
    pass
"
else
    echo "⚠️ 响应: $RESPONSE"
fi
