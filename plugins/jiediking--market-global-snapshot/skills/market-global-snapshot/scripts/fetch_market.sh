#!/bin/bash
# market-global-snapshot helper script
# Usage: ./fetch_market.sh <ticker> [exchange]
# Example: ./fetch_market.sh ^GSPC

TICKER=$1
EXCHANGE=${2:-"yahoo"}

if [ -z "$TICKER" ]; then
    echo "Usage: $0 <ticker> [exchange]"
    exit 1
fi

# Yahoo Finance (Primary)
fetch_yahoo() {
    local ticker=$1
    response=$(curl -s "https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=1d&range=5d" \
        -H "User-Agent: Mozilla/5.0")
    
    if [ -n "$response" ] && echo "$response" | grep -q "close"; then
        echo "$response"
        return 0
    fi
    return 1
}

# Trading Economics (Fallback)
fetch_trading_economics() {
    local url=$1
    response=$(curl -s "$url" -H "User-Agent: Mozilla/5.0")
    
    if [ -n "$response" ]; then
        echo "$response"
        return 0
    fi
    return 1
}

# Sina Finance (STAR Market fallback)
fetch_sina() {
    local ticker=$1
    # Convert ticker to Sina format (e.g., 000001.SS -> sh000001)
    local sinajs="http://hq.sinajs.cn/list="
    
    case "$ticker" in
        000001.SS) sinajs="${sinajs}sh000001" ;;
        399001.SZ) sinajs="${sinajs}sz399001" ;;
        000680.SS) sinajs="${sinajs}sh000680" ;;
        *) return 1 ;;
    esac
    
    response=$(curl -s "$sinajs" -H "Referer: https://finance.sina.com.cn")
    
    if [ -n "$response" ]; then
        echo "$response"
        return 0
    fi
    return 1
}

# Main logic
case "$EXCHANGE" in
    yahoo)
        fetch_yahoo "$TICKER" || echo "ERROR: Yahoo Finance failed"
        ;;
    sina)
        fetch_sina "$TICKER" || echo "ERROR: Sina Finance failed"
        ;;
    te)
        # Trading Economics requires URL mapping
        echo "ERROR: TE requires full URL"
        ;;
    *)
        echo "ERROR: Unknown exchange: $EXCHANGE"
        ;;
esac
