#!/bin/bash
# Nova API Complete Test Script
# Run: chmod +x test_api.sh && ./test_api.sh

SESSION="3b2369a578c04c81a17975861ed08948"
BASE_URL="http://31.97.220.195:8080"
HEADER="authorization: $SESSION"

echo "==================================="
echo "🚀 TESTING NOVA API ENDPOINTS"
echo "Session: $SESSION"
echo "==================================="

# 1. PUBLIC ENDPOINTS
echo -e "\n📡 PUBLIC ENDPOINTS"
curl -s "$BASE_URL/" | jq '.' 2>/dev/null || echo "Root: OK"
curl -s "$BASE_URL/api/health" | jq '.' 2>/dev/null || echo "Health: OK"
curl -s "$BASE_URL/api/market/time" | jq '.' 2>/dev/null || echo "Market time: OK"

# 2. USER INFO
echo -e "\n👤 USER INFO"
curl -s -H "$HEADER" "$BASE_URL/api/v1/user/info" | jq '.'

# 3. BALANCE
echo -e "\n💰 BALANCE"
curl -s -H "$HEADER" "$BASE_URL/api/v1/balance" | jq '{total_usd, assets_count: (.assets | length)}'

# 4. ACCOUNT
echo -e "\n🏦 ACCOUNT"
curl -s -H "$HEADER" "$BASE_URL/api/account/wallet-balance?account_type=UNIFIED" | jq '{retCode, total: (.result.list[0].totalEquity)}'

# 5. TRADING
echo -e "\n📊 TRADING"
curl -s -H "$HEADER" "$BASE_URL/api/trade/open-orders?category=spot" | jq '{retCode, count: (.result.list | length)}'
curl -s -H "$HEADER" "$BASE_URL/api/trade/order-history?category=spot&limit=5" | jq '{retCode, count: (.result.list | length)}'

# 6. POSITIONS
echo -e "\n📈 POSITIONS"
curl -s -H "$HEADER" "$BASE_URL/api/positions/list?category=linear" | jq '{retCode, count: (.result.list | length)}'
curl -s -H "$HEADER" "$BASE_URL/api/positions/closed-pnl?category=linear&limit=5" | jq '{retCode, count: (.result.list | length)}'

# 7. PnL
echo -e "\n📉 PNL"
curl -s -H "$HEADER" "$BASE_URL/api/v1/pnl" | jq '.'

# 8. STRATEGIES & BOTS
echo -e "\n🤖 STRATEGIES"
curl -s -H "$HEADER" "$BASE_URL/api/v1/strategies" | jq '.'
curl -s -H "$HEADER" "$BASE_URL/api/v1/bots" | jq '.'

# 9. ORDERS
echo -e "\n📋 ORDERS"
curl -s -H "$HEADER" "$BASE_URL/api/v1/orders" | jq '.'

# 10. ASSET
echo -e "\n💎 ASSET"
curl -s -H "$HEADER" "$BASE_URL/api/asset/coin-balance?account_type=FUND" | jq '{retCode}'

# 11. P2P
echo -e "\n🤝 P2P"
curl -s -H "$HEADER" "$BASE_URL/api/p2p/balance" | jq '{retCode}'
curl -s -H "$HEADER" "$BASE_URL/api/p2p/orders" | jq '{retCode}'

# 12. TEST TRADE (optional - commented out)
# echo -e "\n💰 TEST TRADE"
# curl -s -X POST -H "$HEADER" -H "Content-Type: application/json" \
#   -d '{"symbol":"BTCUSDT","side":"Buy","qty":0.0001,"order_type":"Market","category":"spot"}' \
#   "$BASE_URL/api/trade/order" | jq '.'

echo -e "\n==================================="
echo "✅ TEST COMPLETE"
echo "==================================="
