#!/bin/bash

echo "📊 NOVA GLOBAL KEYS - COMPLETE SYSTEM STATUS"
echo "============================================="
echo ""

echo "🔍 BACKEND SERVICES (via Gateway):"
echo "-----------------------------------"
curl -s http://127.0.0.1:8081/health | python3 -m json.tool

echo ""
echo "🔍 FRONTEND STATUS:"
echo "-------------------"
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000 | grep -q "200"; then
  echo "✅ Frontend is RUNNING on port 3000"
  echo "   Test: curl -I http://127.0.0.1:3000"
else
  echo "❌ Frontend is NOT running on port 3000"
fi

echo ""
echo "📊 PM2 PROCESS STATUS:"
echo "----------------------"
pm2 status

echo ""
echo "📈 MARKET DATA TEST:"
echo "--------------------"
curl -s http://127.0.0.1:8081/api/market/tickers/BTCUSDT | python3 -m json.tool
