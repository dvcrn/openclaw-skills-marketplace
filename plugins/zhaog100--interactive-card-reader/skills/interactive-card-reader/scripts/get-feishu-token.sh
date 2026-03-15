#!/bin/bash

# 获取飞书tenant_access_token
# 功能：自动获取并缓存Token

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$SKILL_DIR/config/feishu-config.json"
CACHE_FILE="$SKILL_DIR/data/token-cache.json"

# 创建数据目录
mkdir -p "$(dirname "$CACHE_FILE")"

# 读取配置
APP_ID=$(jq -r '.app_id // empty' "$CONFIG_FILE" 2>/dev/null)
APP_SECRET=$(jq -r '.app_secret // empty' "$CONFIG_FILE" 2>/dev/null)

if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ]; then
    echo '{"error": "缺少app_id或app_secret配置"}'
    exit 1
fi

# 检查缓存的Token
if [ -f "$CACHE_FILE" ]; then
    CACHED_TOKEN=$(jq -r '.token // empty' "$CACHE_FILE" 2>/dev/null)
    EXPIRE_TIME=$(jq -r '.expire_time // 0' "$CACHE_FILE" 2>/dev/null)
    CURRENT_TIME=$(date +%s)

    # 如果Token还在有效期内（提前5分钟刷新）
    if [ -n "$CACHED_TOKEN" ] && [ "$EXPIRE_TIME" -gt $((CURRENT_TIME + 300)) ]; then
        echo "{\"token\": \"$CACHED_TOKEN\", \"from_cache\": true}"
        exit 0
    fi
fi

# 获取新Token
RESPONSE=$(curl -s -X POST \
  "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{
    \"app_id\": \"$APP_ID\",
    \"app_secret\": \"$APP_SECRET\"
  }")

# 检查响应
CODE=$(echo "$RESPONSE" | jq -r '.code // -1')
if [ "$CODE" != "0" ]; then
    echo "{\"error\": \"获取Token失败\", \"response\": $RESPONSE}"
    exit 1
fi

# 提取Token
TOKEN=$(echo "$RESPONSE" | jq -r '.tenant_access_token')
EXPIRE=$(echo "$RESPONSE" | jq -r '.expire')

# 计算过期时间
CURRENT_TIME=$(date +%s)
EXPIRE_TIME=$((CURRENT_TIME + EXPIRE))

# 缓存Token
cat > "$CACHE_FILE" <<EOF
{
  "token": "$TOKEN",
  "expire": $EXPIRE,
  "expire_time": $EXPIRE_TIME,
  "created_at": $(date -Iseconds | jq -R .)
}
EOF

echo "{\"token\": \"$TOKEN\", \"from_cache\": false, \"expire\": $EXPIRE}"
