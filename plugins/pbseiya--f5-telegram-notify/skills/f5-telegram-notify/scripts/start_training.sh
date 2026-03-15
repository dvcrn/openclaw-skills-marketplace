#!/bin/bash

# F5-TTS Training Controller Script
# ใช้สำหรับเริ่ม/หยุด training โดยหยุด Gradio ก่อน

set -e

CONTAINER_NAME="f5-tts"
COMPOSE_DIR="/mnt/storage/ada_projects/F5-TTS"
NOTIFY_SCRIPT="/app/skills/f5-telegram-notify/scripts/notify.sh"

# Config
MODEL_NAME="${F5_MODEL_NAME:-F5TTS_v1_Base}"
BATCH_SIZE="${F5_BATCH_SIZE:-256}"
LEARNING_RATE="${F5_LEARNING_RATE:-1e-5}"
EPOCHS="${F5_EPOCHS:-50}"
GRAD_ACCUM="${F5_GRAD_ACCUM:-8}"

usage() {
    echo "Usage: $0 <start|stop|status>"
    echo ""
    echo "Commands:"
    echo "  start   - เริ่ม training (หยุด Gradio ก่อน)"
    echo "  stop    - หยุด training และเริ่ม Gradio ใหม่"
    echo "  status  - แสดงสถานะ"
    exit 1
}

if [ $# -lt 1 ]; then
    usage
fi

COMMAND=$1

case "$COMMAND" in
    start)
        echo "🛑 Stopping Gradio..."
        cd "$COMPOSE_DIR" && docker compose stop f5-tts
        
        echo "🚀 Starting training..."
        docker compose up -d f5-tts
        sleep 5
        
        # Send start notification
        docker exec $CONTAINER_NAME bash "$NOTIFY_SCRIPT" start "🚀 เริ่ม finetuning: $MODEL_NAME\n📊 Dataset: chant_dataset\n⚙️ Batch: $BATCH_SIZE (x$GRAD_ACCUM) | LR: $LEARNING_RATE" "$MODEL_NAME"
        
        # Start training in background
        docker exec $CONTAINER_NAME bash -c "
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
        echo "✅ Training started with PID: $TRAIN_PID"
        echo "📄 Logs: /app/outputs/finetuning.log"
        echo ""
        echo "Monitor with: docker exec f5-tts tail -f /app/outputs/finetuning.log"
        ;;
        
    stop)
        echo "🛑 Stopping training..."
        docker exec $CONTAINER_NAME bash -c "pkill -f finetune_cli.py || true"
        
        echo "🚀 Starting Gradio..."
        cd "$COMPOSE_DIR" && docker compose up -d f5-tts
        
        echo "✅ Done!"
        ;;
        
    status)
        echo "📊 Container Status:"
        docker ps --filter name=$CONTAINER_NAME --format "table {{.Names}}\t{{.Status}}"
        
        echo ""
        echo "📊 GPU Usage:"
        nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader | grep -v gnome || echo "No GPU processes"
        
        echo ""
        echo "📊 Training Process:"
        docker exec $CONTAINER_NAME bash -c "ps aux | grep finetune_cli | grep -v grep" || echo "No training process"
        
        echo ""
        echo "📊 Last 10 lines of log:"
        docker exec $CONTAINER_NAME tail -10 /app/outputs/finetuning.log 2>/dev/null || echo "No log file"
        ;;
        
    *)
        usage
        ;;
esac
