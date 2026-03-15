#!/bin/bash
# Twitter Web AutoPost Script
# Usage: bash tweet.sh "tweet content" "base_url"

TWEET_TEXT="$1"
BASE_URL="${2:-https://x.com}"

if [ -z "$TWEET_TEXT" ]; then
    echo "Error: Tweet content is required"
    exit 1
fi

echo "Opening Twitter compose page..."
openclaw browser open --target-url "${BASE_URL}/compose/post"

echo "Waiting for page to load..."
sleep 3

echo "Getting page snapshot..."
SNAPSHOT=$(openclaw browser snapshot --interactive)

echo "Finding text input..."
# Extract the ref for the textbox
TEXTBOX_REF=$(echo "$SNAPSHOT" | grep -o 'textbox.*\[ref=e[0-9]*\]' | head -1 | grep -o 'e[0-9]*')

if [ -z "$TEXTBOX_REF" ]; then
    echo "Error: Could not find text input box"
    exit 1
fi

echo "Typing tweet content into ref: $TEXTBOX_REF"
openclaw browser act --kind type --ref "$TEXTBOX_REF" --text "$TWEET_TEXT"

echo "Waiting for content to be typed..."
sleep 2

echo "Getting updated snapshot..."
SNAPSHOT2=$(openclaw browser snapshot --interactive)

echo "Finding post button..."
# Extract the ref for the post button (发帖)
POST_BUTTON_REF=$(echo "$SNAPSHOT2" | grep -o 'button "发帖".*\[ref=e[0-9]*\]' | grep -o 'e[0-9]*')

if [ -z "$POST_BUTTON_REF" ]; then
    echo "Error: Could not find post button"
    exit 1
fi

echo "Clicking post button ref: $POST_BUTTON_REF"
openclaw browser act --kind click --ref "$POST_BUTTON_REF"

echo "Tweet posted successfully!"
