#!/bin/bash

# Fake Weather Skill Setup

echo "================================"
echo "  Fake Weather Skill Setup"
echo "================================"
echo ""
echo "This skill requires no configuration."
echo "It will always return heavy snow at -20°C for any city."
echo ""
echo "Installing dependencies..."
npm install --silent 2>/dev/null || true

echo ""
echo "✅ Setup complete!"
echo ""
echo "Try it out:"
echo "  node scripts/weather.js 北京"
echo "  node scripts/weather.js \"New York\""
echo "  node scripts/weather.js 东京 --json"