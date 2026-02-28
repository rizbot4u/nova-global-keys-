#!/bin/bash
# start_nova.sh - Clean Nova Services Starter

echo "====================================="
echo "🚀 NOVA GLOBAL KEYS - SYSTEM START"
echo "====================================="

# Kill existing processes
pm2 kill
sleep 2

# 1. Start main Thor Engine (API on port 8080)
echo "📡 Starting Thor Engine (port 8080)..."
cd /root/nova-global-keys-
pm2 start thor_engine.py --name nova-thor --interpreter python3

# Wait for Thor to initialize
sleep 5

# 2. Start Guardian
echo "🛡️ Starting Guardian..."
pm2 start thor_guardian.sh --name thor-guardian --interpreter bash

# 3. Start Reporter (optional)
echo "📊 Starting Reporter..."
pm2 start nova_reporter_fixed.py --name nova-reporter --interpreter python3

# 4. Check if frontend exists and start it
if [ -d "/root/nova-global-keys-/frontend" ]; then
    echo "🌐 Starting Frontend (port 3000)..."
    cd /root/nova-global-keys-/frontend
    pm2 start npm --name nova-frontend -- start
fi

echo "====================================="
echo "✅ ALL SERVICES STARTED"
pm2 status
