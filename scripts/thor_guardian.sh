#!/bin/bash
# thor_guardian.sh - Simple Guardian for Nova Services

export TELEGRAM_TOKEN=$(grep TELEGRAM_TOKEN /root/nova-global-keys-/.env | cut -d= -f2)
export ADMIN_CHAT_ID=$(grep ADMIN_CHAT_ID /root/nova-global-keys-/.env | cut -d= -f2)
REDIS_PASS="NovaGlobal2026"

send_alert() {
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
        -d "chat_id=$ADMIN_CHAT_ID" \
        -d "text=$1" > /dev/null
}

send_alert "🛡️ Thor Guardian Started"

while true; do
    # Check nova-thor
    if ! pm2 list | grep -q "nova-thor.*online"; then
        send_alert "🚨 ALERT: nova-thor crashed! Restarting..."
        cd /root/nova-global-keys-
        pm2 start thor_engine.py --name nova-thor --interpreter python3
        sleep 5
    fi
    
    # Check heartbeat
    heartbeat=$(redis-cli -a "$REDIS_PASS" GET worker:last_heartbeat 2>/dev/null)
    if [ -n "$heartbeat" ]; then
        echo "💓 Heartbeat: $heartbeat"
    else
        send_alert "⚠️ WARNING: No heartbeat from nova-thor"
    fi
    
    sleep 30
done
