#!/usr/bin/env bash
# snap_and_praise.sh - 拍一张照片并用 AI 夸奖
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H-%M)
HOUR_MIN=$(date +%H:%M)
DIR="${DIARY_DIR}/$DATE"

mkdir -p "$DIR"

# ── 时间段判断 ────────────────────────────────────────────
# 将 HH:MM 转为分钟数方便比较
to_minutes() {
  local t="$1"
  local h="${t%%:*}"
  local m="${t##*:}"
  echo $(( 10#$h * 60 + 10#$m ))
}

NOW_MIN=$(to_minutes "$HOUR_MIN")
WORK_START_MIN=$(to_minutes "$WORK_START")
LUNCH_START_MIN=$(to_minutes "$LUNCH_START")
LUNCH_END_MIN=$(to_minutes "$LUNCH_END")
WORK_END_MIN=$(to_minutes "$WORK_END")

# 周末判断（WORK_DAYS 变量，默认 1-5 即周一到周五）
WORK_DAYS="${WORK_DAYS:-1,2,3,4,5}"
TODAY_DOW=$(date +%u)  # 1=周一 ... 7=周日
if ! echo ",$WORK_DAYS," | grep -q ",$TODAY_DOW,"; then
  exit 0  # 非工作日，静默跳过
fi

# 工作时间判断：< WORK_START 跳过；> WORK_END 跳过；= WORK_END 允许（拍最后一张）
if [ "$NOW_MIN" -lt "$WORK_START_MIN" ] || [ "$NOW_MIN" -gt "$WORK_END_MIN" ]; then
  exit 0  # 非工作时间，静默跳过
fi

# 午休时间跳过
if [ "$NOW_MIN" -ge "$LUNCH_START_MIN" ] && [ "$NOW_MIN" -lt "$LUNCH_END_MIN" ]; then
  exit 0  # 午休时间，静默跳过
fi

# ── 拍照 ──────────────────────────────────────────────────
PHOTO="$DIR/$TIME.jpg"

if command -v imagesnap &>/dev/null; then
  if [ -n "$CAMERA_DEVICE" ]; then
    imagesnap -q -d "$CAMERA_DEVICE" "$PHOTO"
  else
    imagesnap -q "$PHOTO"
  fi
else
  echo "[ERROR] imagesnap not found. Run: brew install imagesnap" >&2
  exit 1
fi

echo "📸 拍照完成: $PHOTO"

# ── 读取 API Key ──────────────────────────────────────────
API_KEY=$(python3 -c "
import sys, json
with open('${HOME}/.openclaw/openclaw.json') as f:
    d = json.load(f)
providers = d.get('models', {}).get('providers', {})
for v in providers.values():
    k = v.get('apiKey', '')
    if k:
        print(k)
        break
" 2>/dev/null || true)

if [ -z "$API_KEY" ]; then
  echo "[ERROR] 无法读取 API Key" >&2
  exit 1
fi

# ── base64 编码并调用视觉模型 ─────────────────────────────
B64=$(base64 -i "$PHOTO")

RESULT=$(curl -s "$BASE_URL/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d "{
    \"model\": \"$MODEL\",
    \"max_tokens\": 300,
    \"messages\": [{
      \"role\": \"user\",
      \"content\": [{
        \"type\": \"image_url\",
        \"image_url\": {\"url\": \"data:image/jpeg;base64,$B64\"}
      }, {
        \"type\": \"text\",
        \"text\": \"$PRAISE_PROMPT\"
      }]
    }]
  }" 2>/dev/null \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('choices',[{}])[0].get('message',{}).get('content',''))" 2>/dev/null \
  || true)

if [ -z "$RESULT" ]; then
  RESULT="（照片已记录，分析暂时不可用）"
fi

# ── 写入日志 ──────────────────────────────────────────────
LOG="$DIR/log.md"
{
  echo ""
  echo "## $(date +%H:%M)"
  echo "$RESULT"
} >> "$LOG"

echo "✅ 分析完成，已写入 $LOG"
echo "$RESULT"
