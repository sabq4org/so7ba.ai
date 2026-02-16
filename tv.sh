#!/bin/bash
# TradingView remote control helper
# Usage: tv.sh screenshot|timeframe|ticker [args]

NODE="root@157.230.137.138"
REMOTE_SCRIPT="/opt/tv.js"

# Ensure Chrome is running
ssh $NODE "systemctl is-active tradingview-chrome > /dev/null 2>&1 || systemctl start tradingview-chrome && sleep 5" 2>/dev/null

# Ensure SSH tunnel for devtools is up
if ! ss -tlnp 2>/dev/null | grep -q ":9222"; then
  ssh -f -N -L 9222:127.0.0.1:9222 $NODE 2>/dev/null
fi

# Run command
ssh $NODE "node $REMOTE_SCRIPT $@" 2>&1

# If screenshot, copy it
if [ "$1" = "screenshot" ]; then
  REMOTE_PATH="${2:-/tmp/tv_shot.png}"
  LOCAL_PATH="/tmp/tv_shot.png"
  scp $NODE:$REMOTE_PATH $LOCAL_PATH 2>/dev/null
  echo "local: $LOCAL_PATH"
fi
