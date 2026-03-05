#!/bin/bash

TOKEN="REDACTED"

echo "🔍 Testing Gateway Health"
curl -s http://127.0.0.1:8081/health | python3 -m json.tool
echo ""

echo "🔍 Testing Trade Service Health"
curl -s http://127.0.0.1:8004/health | python3 -m json.tool
echo ""

echo "🔍 Connected Exchanges"
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8081/api/keys/list | python3 -m json.tool
echo ""

echo "💰 Binance Balance"
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8081/api/binance/balance | python3 -m json.tool
echo ""

echo "📊 Binance BTC Ticker"
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8081/api/binance/ticker/BTCUSDT | python3 -m json.tool
echo ""

echo "✅ Done!"
