#!/bin/bash

# F5-TTS Finetuning Script สำหรับ Docker (Version 4 - Low Memory)
# Optimized สำหรับ GPU 6GB

set -e

CONTAINER_NAME="f5-tts"
NOTIFY_SCRIPT="/app/skills/f5-telegram-notify/scripts/notify.sh"

# Config - Low memory settings
MODEL_NAME="${F5_MODEL_NAME:-F5TTS_v1_Base}"
BATCH_SIZE="${F5_BATCH_SIZE:-256}"  # ต่ำมากสำหรับ 6GB GPU
LEARNING_RATE="${F5_LEARNING_RATE:-1e-5}"
EPOCHS="${F5_EPOCHS:-50}"
DATASET_PATH="/data/chinabanchorn/chant_dataset"
GRAD_ACCUM="${F5_GRAD_ACCUM:-8}"  # Gradient accumulation เพื่อชดเชย batch size ต่ำ

echo "🚀 Starting F5-TTS Finetuning in Docker..."
echo "   Container: $CONTAINER_NAME"
echo "   Model: $MODEL_NAME"
echo "   Dataset Path: $DATASET_PATH"
echo "   Batch Size: $BATCH_SIZE (accum: $GRAD_ACCUM)"
echo "   Learning Rate: $LEARNING_RATE"
echo "   Epochs: $EPOCHS"
echo ""

# Send start notification
docker exec $CONTAINER_NAME bash "$NOTIFY_SCRIPT" start "🚀 เริ่ม finetuning: $MODEL_NAME\n📊 Dataset: chant_dataset\n⚙️ Batch: $BATCH_SIZE (x$GRAD_ACCUM) | LR: $LEARNING_RATE" "$MODEL_NAME"

# Run finetuning with low memory settings
docker exec $CONTAINER_NAME bash -c "
    export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
    cd /app/src && \
    python f5_tts/train/finetune_cli.py \
        --exp_name $MODEL_NAME \
        --dataset_name chinabanchorn \
        --batch_size_per_gpu $BATCH_SIZE \
        --batch_size_type sample \
        --learning_rate $LEARNING_RATE \
        --epochs $EPOCHS \
        --grad_accumulation_steps $GRAD_ACCUM \
        --finetune \
        --tokenizer char \
        > /app/outputs/finetuning.log 2>&1 &
    echo \$!
" > /tmp/train_pid.txt

TRAIN_PID=$(cat /tmp/train_pid.txt)
echo "Finetuning started with PID: $TRAIN_PID inside container"
echo "Logs: /app/outputs/finetuning.log"

# Monitor
START_TIME=$(date +%s)
echo "Monitoring finetuning progress..."
sleep 5

while true; do
    if ! docker exec $CONTAINER_NAME bash -c "ps aux | grep -v grep | grep 'finetune_cli.py' | grep -q '$TRAIN_PID'" 2>/dev/null; then
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        HOURS=$((DURATION / 3600))
        MINUTES=$(((DURATION % 3600) / 60))
        SECONDS=$((DURATION % 60))
        
        LAST_LOG=$(docker exec $CONTAINER_NAME tail -50 /app/outputs/finetuning.log 2>/dev/null || echo "")
        
        if echo "$LAST_LOG" | grep -qi "error\|exception\|failed\|traceback"; then
            echo ""
            echo "❌ Finetuning failed!"
            echo "Duration: ${HOURS}h ${MINUTES}m ${SECONDS}s"
            docker exec $CONTAINER_NAME bash "$NOTIFY_SCRIPT" error "❌ Finetuning ล้มเหลว!\n⏱ ระยะเวลา: ${HOURS}h ${MINUTES}m ${SECONDS}s\n\n$LAST_LOG" "$MODEL_NAME"
            exit 1
        else
            echo ""
            echo "✅ Finetuning completed successfully!"
            echo "Duration: ${HOURS}h ${MINUTES}m ${SECONDS}s"
            docker exec $CONTAINER_NAME bash "$NOTIFY_SCRIPT" success "✅ Finetuning สำเร็จ!\n⏱ ระยะเวลา: ${HOURS}h ${MINUTES}m ${SECONDS}s" "$MODEL_NAME" "/app/outputs"
            exit 0
        fi
    fi
    
    echo -n "."
    sleep 30
done
