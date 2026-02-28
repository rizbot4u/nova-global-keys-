#!/bin/bash
# start_all.sh - Clean startup for all Nova services

echo "🚀 Starting Nova Global Keys Services"
echo "====================================="

# Kill any existing processes
pm2 kill

# Wait a moment
sleep 2

# Start Thor Engine (main API on port 8080)
echo "📡 Starting Thor Engine (port 8080)..."
cd /root/nova-global-keys-
pm2 start thor_engine.py --name nova-thor --interpreter python3

# Wait for Thor to initialize
sleep 5

# Start Frontend (if exists)
if [ -d "/root/nova-global-keys-/frontend" ]; then
    echo "🌐 Starting Frontend (port 3000)..."
    cd /root/nova-global-keys-/frontend
    pm2 start npm --name nova-frontend -- start
fi

# Start Guardian
echo "🛡️ Starting Thor Guardian..."
cd /root/nova-global-keys-
pm2 start ./thor_guardian.sh --name thor-guardian --interpreter bash

# Start Daily Reporter (optional)
echo "📊 Starting Daily Reporter..."
pm2 start nova_reporter_fixed.py --name nova-reporter --interpreter python3

echo "====================================="
echo "✅ All services started!"
pm2 status
