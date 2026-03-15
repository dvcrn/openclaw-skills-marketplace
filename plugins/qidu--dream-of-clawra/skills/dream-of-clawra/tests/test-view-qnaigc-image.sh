#!/bin/bash
# Test QNAIGC image generation and view the result

set -euo pipefail

export QNAIGC_KEY="sk-dacbaffa393****"

echo "=== Testing QNAIGC Image Generation ==="
echo ""

# Create a simple test that saves the image without cleanup
TEMP_FILE=$(mktemp /tmp/test-qnaigc-image-XXXXXX.png)

echo "Generating image with prompt: 'person wearing a santa hat'..."
echo ""

# Direct API call to QNAIGC
RESPONSE=$(curl -s -X POST "https://api.qnaigc.com/v1/images/edits" \
  -H "Authorization: Bearer $QNAIGC_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.5-flash-image",
    "image": "https://cdn.jsdelivr.net/gh/SumeLabs/clawra@main/assets/clawra.png",
    "prompt": "person wearing a santa hat, christmas theme"
  }')

echo "Response received (truncated):"
echo "$RESPONSE" | jq 'del(.data[0].b64_json) | .' 2>/dev/null || echo "$RESPONSE" | head -200

echo ""
echo "Extracting base64 data..."

B64_DATA=$(echo "$RESPONSE" | jq -r '.data[0].b64_json // empty')

if [ -z "$B64_DATA" ]; then
    echo "ERROR: No base64 data found in response"
    exit 1
fi

echo "Base64 data length: ${#B64_DATA} characters"
echo ""

echo "Decoding base64 to file: $TEMP_FILE"
echo "$B64_DATA" | base64 -d > "$TEMP_FILE" 2>/dev/null

if [ $? -ne 0 ] || [ ! -s "$TEMP_FILE" ]; then
    echo "ERROR: Failed to decode base64 image data"
    rm -f "$TEMP_FILE"
    exit 1
fi

echo ""
echo "=== Image File Details ==="
echo "File: $TEMP_FILE"
echo "Size: $(stat -c%s "$TEMP_FILE") bytes"
echo "Type: $(file "$TEMP_FILE" | cut -d: -f2-)"
echo ""

# Try to get image dimensions if possible
if command -v identify &> /dev/null; then
    echo "Image dimensions:"
    identify "$TEMP_FILE" 2>/dev/null || echo "Could not determine dimensions (ImageMagick not available)"
elif command -v ffprobe &> /dev/null; then
    echo "Image dimensions:"
    ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$TEMP_FILE" 2>/dev/null || echo "Could not determine dimensions"
else
    echo "Install ImageMagick or ffmpeg to view image dimensions"
fi

echo ""
echo "=== File Information ==="
ls -la "$TEMP_FILE"

echo ""
echo "=== Next Steps ==="
echo "1. The image is saved at: $TEMP_FILE"
echo "2. You can view it with an image viewer"
echo "3. The file will NOT be automatically deleted"
echo "4. Clean up manually with: rm '$TEMP_FILE'"
echo ""

# Check if we can provide a simple ASCII preview
if command -v chafa &> /dev/null; then
    echo "ASCII preview:"
    chafa --size=40 "$TEMP_FILE"
elif command -v img2txt &> /dev/null; then
    echo "ASCII preview:"
    img2txt "$TEMP_FILE" -W 60 -H 20
else
    echo "Install 'chafa' or 'img2txt' for ASCII preview"
fi
