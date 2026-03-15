#!/bin/bash
# tweet.sh — Open Twitter compose, type tweet, press Cmd+Enter to post
# Usage: bash tweet.sh "tweet content" [base_url]

set -e

TWEET_TEXT="$1"
BASE_URL="${2:-https://x.com}"

if [ -z "$TWEET_TEXT" ]; then
  echo "Usage: bash tweet.sh \"tweet content\" [base_url]"
  exit 1
fi

CLI="openclaw browser"

echo "=== Step 1: Opening compose page ==="
$CLI open "${BASE_URL}/compose/post" 2>/dev/null | grep -E "opened|error" || \
$CLI open "${BASE_URL}/compose/tweet" 2>/dev/null | grep -E "opened|error" || \
{ echo "ERROR: Could not open compose page"; exit 1; }

sleep 3

echo "=== Step 2: Finding textbox ==="
SNAP=$($CLI snapshot 2>/dev/null)
TEXTBOX_REF=$(echo "$SNAP" | grep -i 'textbox' | grep -oE 'ref=e[0-9]+' | head -1 | sed 's/ref=//')

if [ -z "$TEXTBOX_REF" ]; then
  echo "ERROR: Could not find textbox"
  exit 1
fi
echo "Found textbox: $TEXTBOX_REF"

echo "=== Step 3: Typing tweet ==="
$CLI type "$TEXTBOX_REF" "$TWEET_TEXT" 2>/dev/null | grep -E "typed|error"
echo "Content: $TWEET_TEXT"

sleep 1

echo "=== Step 4: Posting (Cmd+Enter) ==="
$CLI press "Meta+Enter" 2>/dev/null | grep -E "pressed|error"

sleep 3

echo "=== Step 5: Verifying ==="
SNAP2=$($CLI snapshot 2>/dev/null)
if echo "$SNAP2" | grep -q "已发布\|Your post was sent\|was sent"; then
  echo "SUCCESS: Tweet posted!"
else
  echo "POSTED: Cmd+Enter sent. Check your Twitter timeline to confirm."
fi

echo ""
echo "=== Done ==="
echo "Tweet: $TWEET_TEXT"
