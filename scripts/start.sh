#!/bin/bash

echo "🚀 Starting Nova Global Keys Microservices..."

# Load environment variables
set -a
source /root/nova-global-keys-/config/env/gateway.env
source /root/nova-global-keys-/config/env/auth.env
source /root/nova-global-keys-/config/env/user.env
source /root/nova-global-keys-/config/env/market.env
source /root/nova-global-keys-/config/env/trade.env
source /root/nova-global-keys-/config/env/p2p.env
source /root/nova-global-keys-/config/env/broker.env
source /root/nova-global-keys-/config/env/telegram.env
set +a

# Start Redis if not running
if ! pgrep redis-server > /dev/null; then
    echo "Starting Redis..."
    redis-server /etc/redis/redis.conf --daemonize yes
    sleep 2
fi

# Start all services via supervisor
echo "Starting services via supervisor..."
supervisorctl reread
supervisorctl update
supervisorctl start all

echo "✅ All services started"
echo "Gateway: http://127.0.0.1:8081"
echo "Telegram Bot: Running"
