#!/bin/bash
# Launch all Nova components

cd /srv/nova-global-keys

# Start main Thor engine
echo "🚀 Starting Thor Engine..."
pm2 start thor_engine.py --name "nova-thor" --interpreter python3

# Start strategy worker
echo "🤖 Starting Strategy Worker..."
pm2 start workers/strategy_runner.py --name "strategy-worker" --interpreter python3

# Show status
echo ""
pm2 status
echo ""
echo "✅ All components started!"
