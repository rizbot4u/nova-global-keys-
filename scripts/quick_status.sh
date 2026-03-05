#!/bin/bash
echo "📊 Service Status Check"
echo "======================="

check_port() {
    if nc -z localhost $1 2>/dev/null; then
        echo "✅ Port $1 - $2 is RUNNING"
        return 0
    else
        echo "❌ Port $1 - $2 is NOT running"
        return 1
    fi
}

check_port 8001 "Auth Service"
check_port 8002 "User Service"
check_port 8003 "Market Service"
check_port 8004 "Trade Service"
check_port 8005 "P2P Service"
check_port 8006 "Broker Service"
check_port 8081 "Gateway"

echo ""
echo "📋 Gateway Health:"
curl -s http://127.0.0.1:8081/health | python3 -m json.tool
