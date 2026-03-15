#!/bin/bash
# 飞书日历管理器 - 自动配置
# 首次运行时自动从 openclaw.json 读取配置

set -e

CONFIG_FILE="${HOME}/.feishu-config.json"
OPENCLAW_CONFIG="${HOME}/.openclaw/openclaw.json"

echo "=== 飞书日历管理器 - 配置检查 ==="
echo ""

# 检查配置是否已存在
if [ -f "$CONFIG_FILE" ]; then
  echo "✅ 配置文件已存在: $CONFIG_FILE"
  echo ""
  # 验证配置
  APP_ID=$(jq -r '.app_id' "$CONFIG_FILE" 2>/dev/null)
  if [ -n "$APP_ID" ] && [ "$APP_ID" != "null" ]; then
    echo "配置有效，无需重新配置"
    exit 0
  else
    echo "⚠️  配置文件无效，将重新配置"
  fi
fi

echo "正在自动配置..."
echo ""

# 尝试从 openclaw.json 读取
if [ -f "$OPENCLAW_CONFIG" ]; then
  echo "📖 从 openclaw.json 读取配置..."

  # 读取 default 账户的配置
  APP_ID=$(jq -r '.channels.feishu.accounts.default.appId' "$OPENCLAW_CONFIG" 2>/dev/null)
  APP_SECRET=$(jq -r '.channels.feishu.accounts.default.appSecret' "$OPENCLAW_CONFIG" 2>/dev/null)

  if [ -n "$APP_ID" ] && [ "$APP_ID" != "null" ] && [ "$APP_ID" != "cli_a90e0f08efb89cd5" ]; then
    echo "✅ 找到 App ID"

    # 获取 tenant_access_token 以便查询日历 ID 和用户 ID
    echo "🔍 正在查询日历和用户信息..."
    TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
      -H "Content-Type: application/json" \
      -d "{\"app_id\": \"$APP_ID\", \"app_secret\": \"$APP_SECRET\"}" | jq -r '.tenant_access_token')

    # 查询日历列表
    CALENDARS=$(curl -s -X GET "https://open.feishu.cn/open-apis/calendar/v4/calendars" \
      -H "Authorization: Bearer $TOKEN" 2>/dev/null)

    # 获取主日历 ID
    CALENDAR_ID=$(echo "$CALENDARS" | jq -r '.data.calendar_list[] | select(.type=="primary") | .calendar_id' 2>/dev/null)

    if [ -n "$CALENDAR_ID" ] && [ "$CALENDAR_ID" != "null" ]; then
      echo "✅ 找到主日历 ID: $CALENDAR_ID"
    else
      echo "⚠️  无法自动获取日历 ID"
      read -p "请输入日历 ID: " CALENDAR_ID
    fi

    # 获取用户 ID（从环境变量或配置）
    if [ -n "$FEISHU_USER_ID" ]; then
      DEFAULT_USER_ID="$FEISHU_USER_ID"
    else
      echo "⚠️  无法自动获取用户 Open ID"
      echo "请输入你的飞书 Open ID（可在飞书客户端 → 个人信息中查看）"
      read -p "Open ID: " DEFAULT_USER_ID
    fi

    # 创建配置文件
    cat > "$CONFIG_FILE" << EOF
{
  "app_id": "$APP_ID",
  "app_secret": "$APP_SECRET",
  "calendar_id": "$CALENDAR_ID",
  "default_user_id": "$DEFAULT_USER_ID"
}
EOF

    chmod 600 "$CONFIG_FILE"
    echo ""
    echo "✅ 配置文件已创建: $CONFIG_FILE"
    echo "✅ 配置完成！现在可以使用飞书日历管理器了。"
    exit 0

  else
    echo "⚠️  无法从 openclaw.json 读取配置"
  fi
fi

# 如果自动配置失败，使用手动配置向导
echo ""
echo "请手动输入配置信息："
echo "💡 提示："
echo "  - App ID 和 App Secret: https://open.feishu.cn/ → 应用凭证"
echo "  - 日历 ID: 飞书日历 → 右键主日历 → 设置"
echo "  - Open ID: 飞书客户端 → 点击头像 → 个人信息"
echo ""

read -p "App ID: " APP_ID
read -p "App Secret: " APP_SECRET
read -p "日历 ID: " CALENDAR_ID
read -p "Open ID: " DEFAULT_USER_ID

if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ] || [ -z "$CALENDAR_ID" ] || [ -z "$DEFAULT_USER_ID" ]; then
  echo "❌ 所有字段都必须填写！"
  exit 1
fi

# 创建配置文件
cat > "$CONFIG_FILE" << EOF
{
  "app_id": "$APP_ID",
  "app_secret": "$APP_SECRET",
  "calendar_id": "$CALENDAR_ID",
  "default_user_id": "$DEFAULT_USER_ID"
}
EOF

chmod 600 "$CONFIG_FILE"

echo ""
echo "✅ 配置完成！现在可以使用飞书日历管理器了。"
