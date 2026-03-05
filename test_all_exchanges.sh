#!/bin/bash

TOKEN="REDACTED"

echo "========================================="
echo "🔍 NOVA GLOBAL KEYS - MULTI-EXCHANGE TEST"
echo "========================================="
echo ""

echo "📊 Gateway Health:"
curl -s http://127.0.0.1:8081/health | python3 -m json.tool
echo ""

echo "📊 Trade Service Health:"
curl -s http://127.0.0.1:8004/health | python3 -m json.tool
echo ""

echo "🔑 Your Connected Exchanges:"
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8081/api/keys/list | python3 -m json.tool
echo ""

echo "💰 Testing Each Exchange (if connected):"
echo "----------------------------------------"

echo "1️⃣  Bybit Balance:"
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8081/api/bybit/balance | python3 -m json.tool 2>/dev/null || echo "   Not connected or error"
echo ""

echo "2️⃣  Binance Balance:"
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8081/api/binance/balance | python3 -m json.tool 2>/dev/null || echo "   Not connected or error"
echo ""

echo "3️⃣  KuCoin Balance:"
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8081/api/kucoin/balance | python3 -m json.tool 2>/dev/null || echo "   Not connected or error"
echo ""

echo "4️⃣  OKX Balance:"
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8081/api/okx/balance | python3 -m json.tool 2>/dev/null || echo "   Not connected or error"
echo ""

echo "✅ Test Complete!"
