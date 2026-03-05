#!/bin/bash

echo "=== TESTING ALL SERVICES ==="

echo -n "Auth Service (8001): "
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/health && echo " OK" || echo " FAIL"

echo -n "User Service (8002): "
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8002/health && echo " OK" || echo " FAIL"

echo -n "Market Service (8003): "
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8003/health && echo " OK" || echo " FAIL"

echo -n "Market Tickers (8003): "
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8003/tickers/BTCUSDT && echo " OK" || echo " FAIL"

echo -n "Trade Service (8004): "
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8004/health && echo " OK" || echo " FAIL"

echo -n "P2P Service (8005): "
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8005/health && echo " OK" || echo " FAIL"

echo -n "Broker Service (8006): "
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8006/health && echo " OK" || echo " FAIL"

echo -n "Gateway Health (8081): "
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8081/health && echo " OK" || echo " FAIL"

echo -n "Gateway Market (8081): "
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8081/api/market/tickers/BTCUSDT && echo " OK" || echo " FAIL"

echo ""
echo "=== PM2 STATUS ==="
pm2 status

echo ""
echo "=== RECENT ERRORS ==="
tail -n 20 /root/.pm2/logs/nova-market-error.log
