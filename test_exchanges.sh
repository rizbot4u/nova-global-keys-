#!/bin/bash

echo "🧪 Testing Multi-Exchange Support"
echo "=================================="

echo ""
echo "📊 Supported Exchanges:"
curl -s http://127.0.0.1:8004/health | python3 -m json.tool

echo ""
echo ""
echo "📋 To test each exchange, you need to:"
echo "1. Connect your API keys via the web dashboard"
echo "2. Then run these commands with your JWT token:"
echo ""
echo "   # Bybit"
echo "   curl -H \"Authorization: Bearer YOUR_TOKEN\" http://127.0.0.1:8081/api/bybit/balance"
echo ""
echo "   # Binance"
echo "   curl -H \"Authorization: Bearer YOUR_TOKEN\" http://127.0.0.1:8081/api/binance/balance"
echo ""
echo "   # KuCoin"
echo "   curl -H \"Authorization: Bearer YOUR_TOKEN\" http://127.0.0.1:8081/api/kucoin/balance"
echo ""
echo "   # OKX"
echo "   curl -H \"Authorization: Bearer YOUR_TOKEN\" http://127.0.0.1:8081/api/okx/balance"
