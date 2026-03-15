#!/bin/bash

# F5-TTS Training Wrapper with Telegram Notification
# ใช้ script นี้แทนการรัน training โดยตรง เพื่อแจ้งเตือนอัตโนมัติ

set -e

# Config
NOTIFY_SCRIPT="/home/seiya/projects/openclaw/workspace/skills/f5-telegram-notify/scripts/notify.mjs"
MODEL_NAME="${F5_MODEL_NAME:-F5TTS_v1_Base}"
START_TIME=$(date +%s)

echo "🚀 Starting F5-TTS Training..."
echo "   Model: $MODEL_NAME"
echo "   Time: $(date)"

# Send start notification
node "$NOTIFY_SCRIPT" start "🚀 เริ่ม training: $MODEL_NAME" "$MODEL_NAME"

# Run training command (passed as arguments)
# Example: ./train_with_notify.sh accelerate launch src/f5_tts/train/train.py --config-name F5TTS_v1_Base.yaml

if "$@"; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    HOURS=$((DURATION / 3600))
    MINUTES=$(((DURATION % 3600) / 60))
    SECONDS=$((DURATION % 60))
    
    echo ""
    echo "✅ Training completed successfully!"
    echo "   Duration: ${HOURS}h ${MINUTES}m ${SECONDS}s"
    
    # Send success notification
    node "$NOTIFY_SCRIPT" success "✅ Training สำเร็จ!\n⏱ ระยะเวลา: ${HOURS}h ${MINUTES}m ${SECONDS}s" "$MODEL_NAME" "/app/outputs"
else
    EXIT_CODE=$?
    echo ""
    echo "❌ Training failed with exit code: $EXIT_CODE"
    
    # Send error notification
    node "$NOTIFY_SCRIPT" error "❌ Training ล้มเหลว!\nExit code: $EXIT_CODE\nคำสั่ง: $*" "$MODEL_NAME"
    
    exit $EXIT_CODE
fi
