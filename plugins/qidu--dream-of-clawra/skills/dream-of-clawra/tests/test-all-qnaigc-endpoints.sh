#!/bin/bash
# Test all QNAIGC endpoints from documentation examples

set -euo pipefail

QNAIGC_KEY="sk-dacbaffa39360db*****"

echo "=== Testing All QNAIGC Endpoints ==="
echo "Using key: ${QNAIGC_KEY:0:10}..."
echo ""

# Test 1: Queue endpoint (from example 1)
echo "Test 1: Queue endpoint (fal-ai/kling-image/o1)..."
curl -s -X POST "https://api.qnaigc.com/queue/fal-ai/kling-image/o1" \
  -H "Authorization: Bearer $QNAIGC_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "一只可爱的橘猫在阳光下打盹",
    "num_images": 2,
    "resolution": "2K",
    "aspect_ratio": "16:9"
  }' | jq .

echo ""

# Test 2: Direct edit endpoint with gemini-2.5-flash-image (from example 2)
echo "Test 2: Direct edit endpoint (gemini-2.5-flash-image)..."
curl -s -X POST "https://api.qnaigc.com/v1/images/edits" \
  -H "Authorization: Bearer $QNAIGC_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.5-flash-image",
    "image": "https://cdn.jsdelivr.net/gh/SumeLabs/clawra@main/assets/clawra.png",
    "prompt": "make this person wearing a santa hat"
  }' | jq .

echo ""

# Test 3: Direct edit endpoint with gemini-3.0-pro-image-preview (from example 3)
echo "Test 3: Direct edit endpoint (gemini-3.0-pro-image-preview)..."
curl -s -X POST "https://api.qnaigc.com/v1/images/edits" \
  -H "Authorization: Bearer $QNAIGC_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3.0-pro-image-preview",
    "image": "https://cdn.jsdelivr.net/gh/SumeLabs/clawra@main/assets/clawra.png",
    "prompt": "make this person wearing a santa hat"
  }' | jq .

echo ""

# Test 4: Test with different authorization header format
echo "Test 4: Testing with 'Key' instead of 'Bearer'..."
curl -s -X POST "https://api.qnaigc.com/v1/images/edits" \
  -H "Authorization: Key $QNAIGC_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.5-flash-image",
    "image": "https://cdn.jsdelivr.net/gh/SumeLabs/clawra@main/assets/clawra.png",
    "prompt": "test"
  }' | jq .

echo ""

# Test 5: Test without authorization header
echo "Test 5: Testing without authorization header..."
curl -s -X POST "https://api.qnaigc.com/v1/images/edits" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.5-flash-image",
    "image": "https://cdn.jsdelivr.net/gh/SumeLabs/clawra@main/assets/clawra.png",
    "prompt": "test"
  }' | jq .

echo ""

# Test 6: Test API status endpoint
echo "Test 6: Testing API status..."
curl -s -X GET "https://api.qnaigc.com/health" \
  -H "Authorization: Bearer $QNAIGC_KEY" | jq .

echo ""

echo "=== Analysis ==="
echo "If all tests return authentication errors, the API key may be:"
echo "1. Invalid/expired"
echo "2. From a different environment (test vs production)"
echo "3. Requires additional account setup"
echo "4. Needs to be activated/whitelisted"
echo ""
echo "Next steps:"
echo "1. Verify the key is valid on QNAIGC dashboard"
echo "2. Check if account has sufficient credits/quota"
echo "3. Contact QNAIGC support for API access"
echo "4. Try generating a new API key"
