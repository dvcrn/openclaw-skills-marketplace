#!/bin/bash
# Test QNAIGC API endpoints

set -euo pipefail

QNAIGC_KEY="sk-dacbaffa39360db****"

echo "=== Testing QNAIGC API Endpoints ==="
echo ""

# Test 1: Check API base
echo "Test 1: Testing API base endpoint..."
curl -s -X GET "https://api.qnaigc.com/" \
  -H "Authorization: Bearer $QNAIGC_KEY" \
  -H "Content-Type: application/json" | jq .

echo ""

# Test 2: Test /v1/ endpoint
echo "Test 2: Testing /v1/ endpoint..."
curl -s -X GET "https://api.qnaigc.com/v1/" \
  -H "Authorization: Bearer $QNAIGC_KEY" \
  -H "Content-Type: application/json" | jq .

echo ""

# Test 3: Test /v1/images endpoint
echo "Test 3: Testing /v1/images endpoint..."
curl -s -X GET "https://api.qnaigc.com/v1/images" \
  -H "Authorization: Bearer $QNAIGC_KEY" \
  -H "Content-Type: application/json" | jq .

echo ""

# Test 4: Test with different HTTP methods
echo "Test 4: Testing POST to /v1/images..."
curl -s -X POST "https://api.qnaigc.com/v1/images" \
  -H "Authorization: Bearer $QNAIGC_KEY" \
  -H "Content-Type: application/json" \
  -d '{}' | jq .

echo ""

# Test 5: Test with correct endpoint from documentation
echo "Test 5: Testing with image edit payload..."
curl -s -X POST "https://api.qnaigc.com/v1/images/edit" \
  -H "Authorization: Bearer $QNAIGC_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://cdn.jsdelivr.net/gh/SumeLabs/clawra@main/assets/clawra.png",
    "prompt": "make this person wearing a santa hat",
    "num_images": 1,
    "output_format": "jpeg",
    "model": "image-edit-v1"
  }' | jq .

echo ""

# Test 6: Test with simpler payload
echo "Test 6: Testing with minimal payload..."
curl -s -X POST "https://api.qnaigc.com/v1/images/edit" \
  -H "Authorization: Bearer $QNAIGC_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://cdn.jsdelivr.net/gh/SumeLabs/clawra@main/assets/clawra.png",
    "prompt": "test edit"
  }' | jq .

echo ""

echo "=== Testing complete ==="
echo "If endpoints return 404, the API structure may be different than expected."
echo "Check the actual API documentation at the provided URLs."
