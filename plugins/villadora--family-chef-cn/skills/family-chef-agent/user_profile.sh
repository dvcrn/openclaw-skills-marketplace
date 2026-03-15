#!/bin/bash

# 用户信息管理脚本
# 存储和管理用户的家庭厨师配置

SCRIPT_DIR="$(dirname "$0")"
DATA_DIR="$SCRIPT_DIR/../data"
PROFILE_FILE="$DATA_DIR/user_profile.json"

mkdir -p "$DATA_DIR"

# 初始化默认配置
init_profile() {
  cat > "$PROFILE_FILE" << 'EOF'
{
  "family_size": null,
  "meals_per_day": 1,
  "budget": null,
  "city": null,
  "preferences": [],
  "dietary_constraints": [],
  "existing_ingredients": [],
  "created_at": null,
  "updated_at": null
}
EOF
}

# 显示用户信息
show_profile() {
  if [ ! -f "$PROFILE_FILE" ]; then
    echo "尚未配置用户信息"
    return
  fi

  echo "=== 家庭厨师配置 ==="
  cat "$PROFILE_FILE" | grep -o '"[^"]*": [^,]*' | sed 's/"/g' | while read -r line; do
    key=$(echo "$line" | cut -d':' -f1)
    value=$(echo "$line" | cut -d':' -f2-)
    echo "$key: $value"
  done
}

# 更新字段
update_field() {
  field="$1"
  value="$2"

  if [ ! -f "$PROFILE_FILE" ]; then
    init_profile
  fi

  # 使用 sed 更新 JSON（简单处理）
  sed -i '' "s/\"$field\": null/\"$field\": \"$value\"/g" "$PROFILE_FILE"
  sed -i '' "s/\"$field\": \[\]/\"$field\": [\"$value\"]/g" "$PROFILE_FILE"

  # 更新时间戳
  now=$(date -Iseconds)
  sed -i '' "s/\"updated_at\": null/\"updated_at\": \"$now\"/g" "$PROFILE_FILE"
}

case "$1" in
  show)
    show_profile
    ;;
  init)
    init_profile
    ;;
  update)
    update_field "$2" "$3"
    ;;
  *)
    echo "用法: $0 {show|init|update <字段> <值>}"
    ;;
esac
