#!/bin/bash
# tv_price.sh — جلب سعر من TradingView عبر المتصفح على الماك
# Usage: bash tv_price.sh [TICKER]
# Default: US500 (S&P 500)

TICKER="${1:-US500}"
NODE="ac72d1155c8313ca8a0fa0804af83ed634d97f737bca6d6c5018bc47996710d1"

# Get snapshot and extract OHLCV data
openclaw browser snapshot \
  --browser-profile openclaw \
  --json \
  --timeout 15000 \
  2>/dev/null | grep -oP '(?:O |H |L |C |Vol )[0-9,.]+'
