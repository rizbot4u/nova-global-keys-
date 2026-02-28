#!/bin/bash
echo "🚀 Starting ALL Nova Services"

# Core services (already running)
pm2 start thor_engine.py --name nova-thor --interpreter python3
pm2 start thor_guardian.sh --name thor-guardian --interpreter bash
pm2 start nova_reporter_fixed.py --name nova-reporter --interpreter python3
pm2 start thor_v2.py --name thor-singleton --interpreter python3 -- --host 0.0.0.0 --port 8081

# Optional services (if they exist)
if [ -f "workers/worker.py" ]; then
    pm2 start workers/worker.py --name nova-worker --interpreter python3
fi

if [ -f "sentiment_bot.py" ]; then
    pm2 start sentiment_bot.py --name sentiment-bot --interpreter python3
fi

if [ -f "social_bot.py" ]; then
    pm2 start social_bot.py --name social-bot --interpreter python3
fi

if [ -f "signal_bot.py" ]; then
    pm2 start signal_bot.py --name signal-bot --interpreter python3
fi

echo "✅ All services started"
pm2 status
