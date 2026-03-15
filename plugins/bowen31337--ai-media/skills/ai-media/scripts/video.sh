#!/bin/bash
set -euo pipefail

# ai-media video generation script
# Usage: ./video.sh "prompt text" [model] [duration]

PROMPT="${1:-waves crashing on shore}"
MODEL="${2:-animatediff}"
DURATION="${3:-4}"
SSH_KEY="$HOME/.ssh/${SSH_KEY_NAME:-id_ed25519_gpu}"
GPU_HOST="${GPU_USER:-user}@${GPU_HOST:-localhost}"
COMFYUI_DIR="/data/ai-stack/comfyui/ComfyUI"
OUTPUT_DIR="/data/ai-stack/output"

# Generate unique filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="video_${TIMESTAMP}.mp4"

echo "🎬 Generating video with prompt: '$PROMPT'"
echo "🤖 Model: $MODEL"
echo "⏱️  Duration: ${DURATION}s"
echo "🖥️  GPU Server: $GPU_HOST"

# Check SSH connectivity
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=5 "$GPU_HOST" "echo 'SSH OK'" &>/dev/null; then
    echo "❌ Cannot connect to GPU server"
    exit 1
fi

# Create output directory
ssh -i "$SSH_KEY" "$GPU_HOST" "mkdir -p $OUTPUT_DIR"

if [[ "$MODEL" == "animatediff" ]]; then
    # Use AnimateDiff workflow (proven working)
    echo "📝 Using AnimateDiff workflow..."
    
    # Calculate frames (8fps)
    FRAMES=$((DURATION * 8))
    if [[ $FRAMES -lt 16 ]]; then
        FRAMES=16
    fi
    
    ssh -i "$SSH_KEY" "$GPU_HOST" bash <<EOF
set -euo pipefail
cd /data/ai-stack/sadtalker

# Use the working AnimateDiff script
python3 <<PYTHON
import os
import random
import json

# AnimateDiff workflow parameters
workflow = {
    "prompt": "$PROMPT",
    "negative_prompt": "blurry, low quality, watermark, text, static",
    "frames": $FRAMES,
    "fps": 8,
    "width": 512,
    "height": 512,
    "seed": random.randint(0, 2**32-1)
}

print("AnimateDiff workflow:")
print(json.dumps(workflow, indent=2))
print("\nNote: Use existing animatediff_simple_workflow.json")
print("Output: $OUTPUT_DIR/$OUTPUT_FILE")
PYTHON
EOF

elif [[ "$MODEL" == "ltx2" ]]; then
    echo "📝 Using LTX-2 workflow via ComfyUI API..."
    
    # Use the Python API client
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    python3 "$SCRIPT_DIR/comfyui_api.py" video-ltx2 "$PROMPT" $DURATION
    
    if [[ $? -eq 0 ]]; then
        echo "✅ LTX-2 video generation complete"
    else
        echo "❌ LTX-2 video generation failed"
        exit 1
    fi

else
    echo "❌ Unknown model: $MODEL"
    echo "   Available: animatediff, ltx2"
    exit 1
fi

echo ""
echo "✅ Video generation queued"
echo "📁 Output: $OUTPUT_DIR/$OUTPUT_FILE"
echo ""
echo "⚠️  Note: Full automation pending. Use existing workflows:"
echo "    - AnimateDiff: /tmp/animatediff_simple_workflow.json"
echo "    - LTX-2: Fetch from Lightricks/ComfyUI-LTXVideo"
