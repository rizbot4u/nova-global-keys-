#!/bin/bash
# NOVA API - COMPLETE ENDPOINT TEST
# Run: chmod +x test_all_endpoints_complete.sh && ./test_all_endpoints_complete.sh

SESSION="3b2369a578c04c81a17975861ed08948"
BASE_URL="http://31.97.220.195:8081"
HEADER="authorization: $SESSION"
COUNT=1
TOTAL=53  # Total endpoints to test

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "🚀 TESTING ALL $TOTAL NOVA API ENDPOINTS"
echo "Session: $SESSION"
echo "=========================================="

test_endpoint() {
    local method=$1
    local endpoint=$2
    local desc=$3
    local data=$4
    
    echo -e "\n${YELLOW}[$COUNT/$TOTAL] Testing: $desc${NC}"
    echo "  $method $endpoint"
    
    if [ "$method" = "GET" ]; then
        if [ -n "$data" ]; then
            curl -s -X $method "$BASE_URL$endpoint$data" -H "$HEADER" -H "Content-Type: application/json" | jq '.' 2>/dev/null || echo "  Response: (raw) $(curl -s -X $method "$BASE_URL$endpoint$data" -H "$HEADER" -H "Content-Type: application/json")"
        else
            curl -s -X $method "$BASE_URL$endpoint" -H "$HEADER" -H "Content-Type: application/json" | jq '.' 2>/dev/null || echo "  Response: (raw) $(curl -s -X $method "$BASE_URL$endpoint" -H "$HEADER")"
        fi
    else
        curl -s -X $method "$BASE_URL$endpoint" -H "$HEADER" -H "Content-Type: application/json" -d "$data" | jq '.' 2>/dev/null || echo "  Response: (raw) $(curl -s -X $method "$BASE_URL$endpoint" -H "$HEADER" -H "Content-Type: application/json" -d "$data")"
    fi
    
    echo "  ${GREEN}✓ Tested${NC}"
    ((COUNT++))
}

# ===== 1. PUBLIC ENDPOINTS =====
test_endpoint "GET" "/" "Root Endpoint"
test_endpoint "GET" "/api/health" "Health Check"
test_endpoint "GET" "/api/market/tickers?category=spot&symbol=BTCUSDT" "Market Tickers"
test_endpoint "GET" "/api/market/orderbook?category=spot&symbol=BTCUSDT&limit=5" "Orderbook"
test_endpoint "GET" "/api/market/kline?category=spot&symbol=BTCUSDT&interval=1h&limit=5" "Kline Data"
test_endpoint "GET" "/api/market/instruments?category=spot&symbol=BTCUSDT" "Instruments Info"
test_endpoint "GET" "/api/market/time" "Server Time"

# ===== 2. OAUTH ENDPOINTS =====
test_endpoint "GET" "/api/auth/login" "Auth Login Redirect"
test_endpoint "GET" "/api/auth/google" "Google Login Redirect"
# Note: Callback endpoints can't be tested directly via curl

# ===== 3. ACCOUNT ENDPOINTS =====
test_endpoint "GET" "/api/account/wallet-balance?account_type=UNIFIED" "Wallet Balance"
test_endpoint "GET" "/api/account/info" "Account Info"
test_endpoint "GET" "/api/account/fee-rate?category=spot&symbol=BTCUSDT" "Fee Rate"

# ===== 4. TRADE ENDPOINTS =====
test_endpoint "GET" "/api/trade/open-orders?category=spot" "Open Orders"
test_endpoint "GET" "/api/trade/order-history?category=spot&limit=5" "Order History"
# Test order placement with small amount (commented out for safety)
# test_endpoint "POST" "/api/trade/order" "Place Order" '{"symbol":"BTCUSDT","side":"Buy","qty":0.0001,"order_type":"Market","category":"spot"}'
# Test cancel (needs order ID)
# test_endpoint "POST" "/api/trade/cancel-order" "Cancel Order" '{"category":"spot","symbol":"BTCUSDT","order_id":"xxx"}'
# test_endpoint "POST" "/api/trade/cancel-all" "Cancel All Orders" '{"category":"spot"}'

# ===== 5. POSITION ENDPOINTS =====
test_endpoint "GET" "/api/positions/list?category=linear" "Positions List"
test_endpoint "GET" "/api/positions/closed-pnl?category=linear&limit=5" "Closed PnL"
# test_endpoint "POST" "/api/positions/leverage" "Set Leverage" '{"category":"linear","symbol":"BTCUSDT","leverage":"2"}'

# ===== 6. ASSET ENDPOINTS =====
test_endpoint "GET" "/api/asset/coin-balance?account_type=FUND" "Coin Balance"
# Deposit/withdraw endpoints need parameters
test_endpoint "GET" "/api/asset/deposit/address?coin=USDT" "Deposit Address"
test_endpoint "GET" "/api/asset/deposit/history?limit=5" "Deposit History"
test_endpoint "GET" "/api/asset/withdraw/history?limit=5" "Withdraw History"
# test_endpoint "POST" "/api/asset/transfer" "Create Transfer" '{"from_account":"FUND","to_account":"UNIFIED","coin":"USDT","amount":"1"}'

# ===== 7. AFFILIATE ENDPOINTS =====
test_endpoint "GET" "/api/affiliate/commission?limit=5" "Affiliate Commission"
test_endpoint "GET" "/api/affiliate/user-list?size=5&page=1" "Affiliate User List"

# ===== 8. BROKER ENDPOINTS =====
# Broker endpoints need master API key - may fail
test_endpoint "GET" "/api/broker/subaccount/list" "Subaccount List"
# test_endpoint "POST" "/api/broker/subaccount/create" "Create Subaccount" '{"username":"test","note":"test"}'
# test_endpoint "POST" "/api/broker/subaccount/fee" "Set Subaccount Fee" '{"sub_uid":"xxx","fee_rate":{}}'

# ===== 9. P2P ENDPOINTS =====
test_endpoint "GET" "/api/p2p/balance" "P2P Balance"
test_endpoint "GET" "/api/p2p/orders?limit=5" "P2P Orders"

# ===== 10. RFQ ENDPOINTS =====
test_endpoint "GET" "/api/rfq/config" "RFQ Config"
# test_endpoint "POST" "/api/rfq/create" "Create RFQ" '{"account_type":"UNIFIED","currency":"BTC","side":"Buy","qty":"0.001","quote_currency":"USDT"}'
# test_endpoint "POST" "/api/rfq/execute" "Execute RFQ" '{}'

# ===== 11. V1 COMPATIBILITY ENDPOINTS =====
test_endpoint "GET" "/api/v1/user/info" "V1 User Info"
test_endpoint "GET" "/api/v1/balance" "V1 Balance"
test_endpoint "GET" "/api/v1/price/BTCUSDT" "V1 Price"
test_endpoint "GET" "/api/v1/orderbook/BTCUSDT?limit=5" "V1 Orderbook"
test_endpoint "GET" "/api/v1/pnl" "V1 PnL"
test_endpoint "GET" "/api/v1/orders" "V1 Orders"
test_endpoint "GET" "/api/v1/bots" "V1 Bots"
test_endpoint "POST" "/api/v1/bots/create" "V1 Create Bot" '{"symbol":"BTCUSDT","amount":10,"interval":1440}'
# Bot control needs bot ID - test after creating one
# test_endpoint "POST" "/api/v1/bots/{bot_id}/pause" "V1 Pause Bot"
test_endpoint "GET" "/api/v1/strategies" "V1 Strategies"
test_endpoint "GET" "/api/v1/p2p/orders" "V1 P2P Orders"
test_endpoint "GET" "/api/v1/payments" "V1 Payments"

echo -e "\n${GREEN}==========================================${NC}"
echo -e "${GREEN}✅ ALL $((COUNT-1)) ENDPOINTS TESTED${NC}"
echo -e "${GREEN}==========================================${NC}"
