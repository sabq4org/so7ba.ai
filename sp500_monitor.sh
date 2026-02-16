#!/bin/bash
# S&P 500 Monitor Script

get_sp500() {
    curl -s "https://www.google.com/finance/quote/.INX:INDEXSP" -H "User-Agent: Mozilla/5.0" 2>/dev/null | grep -oP 'data-last-price="\K[^"]+' | head -1
}

get_change() {
    curl -s "https://www.google.com/finance/quote/.INX:INDEXSP" -H "User-Agent: Mozilla/5.0" 2>/dev/null | grep -oP 'data-change-percent="\K[^"]+' | head -1
}

PRICE=$(get_sp500)
CHANGE=$(get_change)

if [ -z "$PRICE" ]; then
    echo "⚠️ تعذر جلب البيانات"
    exit 1
fi

echo "📊 **S&P 500 Update**"
echo ""
echo "السعر: **$PRICE**"
echo "التغير: **${CHANGE}%**"
