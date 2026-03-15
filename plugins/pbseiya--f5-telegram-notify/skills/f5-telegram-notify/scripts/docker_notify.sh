#!/bin/bash

# Docker Helper Script สำหรับส่ง Telegram Notification เข้า F5-TTS Container
# รันจาก host เพื่อส่งข้อความเข้า container

CONTAINER_NAME="f5-tts"
NOTIFY_PATH="/app/skills/f5-telegram-notify/scripts/notify.sh"

# Config จาก host
export TELEGRAM_BOT_TOKEN="8278258201:AAHo84iDrxo2gPIfVyy7HPxAO8Z5gugd3fY"
export TELEGRAM_CHAT_ID="6729022410"

usage() {
    echo "Usage: $0 <status> <message> [model_name] [checkpoint_path]"
    echo ""
    echo "Status: success | error | start"
    echo ""
    echo "Examples:"
    echo "  $0 start 'เริ่ม training แล้ว' MyModel"
    echo "  $0 success 'Training เสร็จ!' MyModel /app/outputs/checkpoint-1000"
    echo "  $0 error 'CUDA out of memory' MyModel"
    exit 1
}

if [ $# -lt 2 ]; then
    usage
fi

STATUS=$1
MESSAGE=$2
MODEL_NAME=${3:-""}
CHECKPOINT_PATH=${4:-""}

echo "📤 Sending Telegram notification to container: $CONTAINER_NAME"

docker exec -e TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" \
           -e TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID" \
           $CONTAINER_NAME bash "$NOTIFY_PATH" "$STATUS" "$MESSAGE" "$MODEL_NAME" "$CHECKPOINT_PATH"
