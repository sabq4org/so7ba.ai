#!/bin/bash
# Watch for new messages in Apartment group
CHAT_JID="966564255999-1532266731@g.us"
LAST_FILE="/home/openclaw/.openclaw/workspace/.apartment_last_check"

# Get last check time
if [ -f "$LAST_FILE" ]; then
    AFTER=$(cat "$LAST_FILE")
else
    AFTER=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    echo "$AFTER" > "$LAST_FILE"
fi

# Search for new messages
RESULTS=$(wacli messages search "." --chat "$CHAT_JID" --after "$AFTER" --limit 20 --json 2>/dev/null)

# Update last check
date -u +%Y-%m-%dT%H:%M:%SZ > "$LAST_FILE"

echo "$RESULTS"
