#!/bin/bash

# 模型切换脚本
# 功能：切换到指定模型

MODEL_ID="$1"

if [ -z "$MODEL_ID" ]; then
    echo "用法: switch-model.sh <model_id>"
    echo "示例: switch-model.sh bailian/kimi-k2.5"
    exit 1
fi

# 方法1：通过环境变量（临时方案）
export OPENCLAW_MODEL="$MODEL_ID"
echo "✅ 已设置模型环境变量：$MODEL_ID"

# 方法2：写入配置文件（持久化方案）
CONFIG_FILE="$HOME/.openclaw/config.json"
if [ -f "$CONFIG_FILE" ]; then
    temp_file=$(mktemp)
    jq --arg model "$MODEL_ID" '.model = $model' "$CONFIG_FILE" > "$temp_file"
    mv "$temp_file" "$CONFIG_FILE"
    echo "✅ 已更新配置文件：$CONFIG_FILE"
fi

# 方法3：通知OpenClaw（需要API支持）
# 这里是预留接口，实际需要OpenClaw支持
NOTIFICATION_FILE="$HOME/.openclaw/model-switch-requests/$(date +%s).json"
mkdir -p "$(dirname "$NOTIFICATION_FILE")"
cat > "$NOTIFICATION_FILE" << EOF
{
  "requested_model": "$MODEL_ID",
  "timestamp": "$(date -Iseconds)",
  "session": "$OPENCLAW_SESSION_KEY"
}
EOF

echo "✅ 模型切换请求已提交：$MODEL_ID"
echo "ℹ️  新模型将在下次对话时生效"
