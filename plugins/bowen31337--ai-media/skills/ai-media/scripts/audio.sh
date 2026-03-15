#!/bin/bash
set -euo pipefail

# ai-media audio generation script (Voxtral TTS)
# Usage: ./audio.sh "text to speak" [language] [gender]

TEXT="${1:-This is a test message}"
LANG="${2:-en}"
GENDER="${3:-male}"
SSH_KEY="$HOME/.ssh/${SSH_KEY_NAME:-id_ed25519_gpu}"
GPU_HOST="${GPU_USER:-user}@${GPU_HOST:-localhost}"
VOXTRAL_DIR="/data/ai-stack/whisper"
OUTPUT_DIR="/data/ai-stack/output"

# Generate unique filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="audio_${TIMESTAMP}.wav"

echo "🔊 Generating audio"
echo "💬 Text: '$TEXT'"
echo "🌍 Language: $LANG"
echo "👤 Gender: $GENDER"
echo "🖥️  GPU Server: $GPU_HOST"

# Check SSH connectivity
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=5 "$GPU_HOST" "echo 'SSH OK'" &>/dev/null; then
    echo "❌ Cannot connect to GPU server"
    exit 1
fi

# Create output directory
ssh -i "$SSH_KEY" "$GPU_HOST" "mkdir -p $OUTPUT_DIR"

# Generate audio via Voxtral
echo "🎵 Generating audio with Voxtral..."
ssh -i "$SSH_KEY" "$GPU_HOST" bash <<EOF
set -euo pipefail
cd $VOXTRAL_DIR

# Check if Voxtral is available
if [[ ! -f "whisper.cpp/main" ]]; then
    echo "❌ Voxtral not found at $VOXTRAL_DIR/whisper.cpp"
    exit 1
fi

# For now, use gTTS as Voxtral is primarily for transcription
# TODO: Integrate proper TTS model (e.g., piper, coqui-tts)
cd /data/ai-stack/sadtalker
source .venv/bin/activate

python3 <<PYTHON
from gtts import gTTS
import os

text = "$TEXT"
lang = "$LANG"
output_path = "$OUTPUT_DIR/$OUTPUT_FILE"

# Generate audio
tts = gTTS(text=text, lang=lang, slow=False)
tts.save(output_path)

# Get file size
file_size = os.path.getsize(output_path)
print(f"✅ Audio saved: {output_path}")
print(f"📦 Size: {file_size / 1024:.1f} KB")
PYTHON
EOF

echo ""
echo "✅ Audio generation complete!"
echo "📁 Output: $OUTPUT_DIR/$OUTPUT_FILE"
echo ""
echo "To download:"
echo "  scp -i $SSH_KEY $GPU_HOST:$OUTPUT_DIR/$OUTPUT_FILE ."
echo ""
echo "⚠️  Note: Currently using gTTS. Voxtral integration pending."
echo "    Future: Use whisper.cpp for voice cloning / better TTS"
