#!/bin/bash

echo "🚀 Starting ALL Nova Global Keys Services..."

# Start backend services
cd /root/nova-global-keys-/services

echo "Starting Auth Service..."
pm2 start auth/main.py --name nova-auth --interpreter python3

echo "Starting User Service..."
pm2 start user/main.py --name nova-user --interpreter python3

echo "Starting Market Service..."
pm2 start market/main.py --name nova-market --interpreter python3

echo "Starting Trade Service..."
pm2 start trade/main.py --name nova-trade --interpreter python3

echo "Starting P2P Service..."
pm2 start p2p/main.py --name nova-p2p --interpreter python3

echo "Starting Broker Service..."
pm2 start broker/main.py --name nova-broker --interpreter python3

echo "Starting Gateway Service..."
pm2 start gateway/main.py --name nova-gateway --interpreter python3

echo "Starting Telegram Service..."
pm2 start telegram/main.py --name nova-telegram --interpreter python3

# Start frontend
cd /root/nova-global-keys-/frontend
echo "Starting Frontend (Next.js)..."
pm2 start npm --name nova-frontend -- start

echo "✅ All services started!"
echo ""
echo "📊 Service Status:"
pm2 status
