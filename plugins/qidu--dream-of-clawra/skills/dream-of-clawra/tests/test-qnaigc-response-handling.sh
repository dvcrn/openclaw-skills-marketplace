#!/bin/bash
# Test QNAIGC response handling for base64 images

set -euo pipefail

echo "=== Testing QNAIGC Response Handling ==="
echo ""

# Create a mock QNAIGC response
MOCK_RESPONSE='{
  "created": 1234567890,
  "data": [
    {
      "b64_json": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    }
  ],
  "output_format": "png",
  "usage": {
    "total_tokens": 5234,
    "input_tokens": 1234,
    "output_tokens": 4000,
    "input_tokens_details": {
      "text_tokens": 234,
      "image_tokens": 1000
    }
  }
}'

echo "Mock QNAIGC response:"
echo "$MOCK_RESPONSE" | jq .
echo ""

# Test extracting base64 data
echo "Extracting base64 data:"
B64_DATA=$(echo "$MOCK_RESPONSE" | jq -r '.data[0].b64_json // empty')
if [ -n "$B64_DATA" ]; then
    echo "✓ Base64 data extracted (length: ${#B64_DATA} chars)"

    # Convert base64 to temporary file
    echo "$B64_DATA" | base64 -d > /tmp/test-qnaigc-image.png 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✓ Base64 decoded successfully"
        echo "  File saved to: /tmp/test-qnaigc-image.png"
        echo "  File size: $(stat -c%s /tmp/test-qnaigc-image.png) bytes"
    else
        echo "✗ Failed to decode base64"
    fi
else
    echo "✗ No base64 data found"
fi

echo ""
echo "=== Testing script updates needed ==="
echo ""

# Check current script response handling
echo "Current bash script response path:"
if grep -q "RESPONSE_IMAGE_PATH" /home/teric/win/e/dev/bot/clawra/skill/scripts/clawra-selfie.sh; then
    grep "RESPONSE_IMAGE_PATH" /home/teric/win/e/dev/bot/clawra/skill/scripts/clawra-selfie.sh
fi

echo ""
echo "Current TypeScript response handling:"
if grep -n "imageResult.data\|imageResult.images\|imageResult.result\|imageResult.output" /home/teric/win/e/dev/bot/clawra/skill/scripts/clawra-selfie.ts; then
    echo "Found response handling in TypeScript"
fi

echo ""
echo "=== Recommendations ==="
echo "1. QNAIGC returns base64 data, not URLs"
echo "2. Need to handle base64 -> file conversion"
echo "3. Need to upload file to a CDN or use local file"
echo "4. OpenClaw may need file path instead of URL"