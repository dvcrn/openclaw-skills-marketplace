#!/bin/bash
# spraay-health-check.sh
# Quick health check for the Spraay x402 gateway

GATEWAY="${SPRAAY_GATEWAY_URL:-https://gateway.spraay.app}"

echo "💧 Spraay Gateway Health Check"
echo "================================"
echo "Gateway: $GATEWAY"
echo ""

# Health check
echo "1. Health endpoint..."
HEALTH=$(curl -s -w "\n%{http_code}" "$GATEWAY/api/health" 2>/dev/null)
HTTP_CODE=$(echo "$HEALTH" | tail -1)
BODY=$(echo "$HEALTH" | head -1)
if [ "$HTTP_CODE" = "200" ]; then
  echo "   ✅ Gateway is healthy"
  echo "   $BODY"
else
  echo "   ❌ Gateway returned HTTP $HTTP_CODE"
  echo "   $BODY"
fi
echo ""

# Chains
echo "2. Supported chains..."
CHAINS=$(curl -s "$GATEWAY/api/chains" 2>/dev/null)
echo "   $CHAINS"
echo ""

# Price check (free)
echo "3. ETH price (free endpoint)..."
PRICE=$(curl -s "$GATEWAY/api/price?symbol=ETH" 2>/dev/null)
echo "   $PRICE"
echo ""

# Endpoint count
echo "4. Available endpoints..."
ENDPOINTS=$(curl -s "$GATEWAY/api/endpoints" 2>/dev/null)
COUNT=$(echo "$ENDPOINTS" | jq '.endpoints | length' 2>/dev/null || echo "unknown")
echo "   Total endpoints: $COUNT"
echo ""

echo "================================"
echo "💧 Health check complete"
