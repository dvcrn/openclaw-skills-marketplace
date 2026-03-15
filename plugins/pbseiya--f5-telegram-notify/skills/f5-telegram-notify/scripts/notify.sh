#!/bin/bash

# F5-TTS Telegram Notification Script (Bash version)
# สำหรับใช้ใน Docker container ที่ไม่มี Node.js

# Telegram config
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-8278258201:AAHo84iDrxo2gPIfVyy7HPxAO8Z5gugd3fY}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-6729022410}"

# Parse arguments
STATUS=$1
MESSAGE=$2
MODEL_NAME=$3
CHECKPOINT_PATH=$4

if [ -z "$STATUS" ] || [ -z "$MESSAGE" ]; then
    echo "Usage: $0 <status> <message> [model_name] [checkpoint_path]"
    echo "Status: success | error | start"
    exit 1
fi

# Validate status
case "$STATUS" in
    success)
        EMOJI="✅"
        STATUS_TEXT="Training สำเร็จ!"
        ;;
    error)
        EMOJI="❌"
        STATUS_TEXT="Training ล้มเหลว!"
        ;;
    start)
        EMOJI="🚀"
        STATUS_TEXT="เริ่ม Training แล้ว"
        ;;
    *)
        echo "Invalid status: $STATUS. Must be: success | error | start"
        exit 1
        ;;
esac

# Build message
TIMESTAMP=$(date -d "Asia/Bangkok" "+%d/%m/%Y %H:%M:%S" 2>/dev/null || date "+%d/%m/%Y %H:%M:%S")

FULL_MESSAGE="<b>${EMOJI} ${STATUS_TEXT}</b>%0A%0A"
FULL_MESSAGE+="<code>${MESSAGE}</code>"

if [ -n "$MODEL_NAME" ]; then
    FULL_MESSAGE+="%0A%0A📦 Model: <code>${MODEL_NAME}</code>"
fi

if [ -n "$CHECKPOINT_PATH" ] && [ "$STATUS" = "success" ]; then
    FULL_MESSAGE+="%0A💾 Checkpoint: <code>${CHECKPOINT_PATH}</code>"
fi

FULL_MESSAGE+="%0A%0A⏰ ${TIMESTAMP}"

# Send to Telegram
URL="https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage"

RESPONSE=$(curl -s -X POST "$URL" \
    -H "Content-Type: application/json" \
    -d "{\"chat_id\": \"${TELEGRAM_CHAT_ID}\", \"text\": \"${FULL_MESSAGE}\", \"parse_mode\": \"HTML\"}")

# Check response
if echo "$RESPONSE" | grep -q '"ok":true'; then
    echo "✅ Sent Telegram notification successfully"
    echo "$RESPONSE" | grep -o '"message_id":[0-9]*' || true
    exit 0
else
    echo "❌ Telegram API error: $RESPONSE"
    exit 1
fi
