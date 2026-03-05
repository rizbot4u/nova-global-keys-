#!/bin/bash

echo "📊 NOVA GLOBAL KEYS - ALL SERVICES STATUS"
echo "=========================================="
echo ""

# Show PM2 status
pm2 status

echo ""
echo "🔍 PORT CHECK:"
echo "=============="

check_port() {
  if nc -z localhost $1 2>/dev/null; then
    echo "✅ Port $1 - $2 is RUNNING"
  else
    echo "❌ Port $1 - $2 is NOT running"
  fi
}

check_port 3000 "Frontend"
check_port 8001 "Auth Service"
check_port 8002 "User Service"
check_port 8003 "Market Service"
check_port 8004 "Trade Service"
check_port 8005 "P2P Service"
check_port 8006 "Broker Service"
check_port 8081 "Gateway"

echo ""
echo "🌐 GATEWAY HEALTH:"
echo "=================="
curl -s http://127.0.0.1:8081/health | python3 -m json.tool

echo ""
echo "📈 MARKET DATA TEST:"
echo "===================="
curl -s http://127.0.0.1:8081/api/market/tickers/BTCUSDT | python3 -m json.tool

echo ""
echo "🖥️  FRONTEND TEST:"
echo "=================="
curl -s -o /dev/null -w "Frontend HTTP Status: %{http_code}\n" http://127.0.0.1:3000
