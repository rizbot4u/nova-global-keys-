#!/bin/bash
# Nova Redis Guardian - Protecting Your Sessions 24/7
LOG_FILE="/srv/nova-backups/guardian.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

if ! redis-cli ping > /dev/null 2>&1; then
    log "⚠️ Redis DOWN - Attempting recovery"
    systemctl restart redis-server
    sleep 5
    
    if redis-cli ping > /dev/null 2>&1; then
        SESSIONS=$(redis-cli keys "user:*:api_key" | wc -l)
        log "✅ Redis recovered - $SESSIONS sessions restored"
    else
        log "❌ Redis recovery FAILED"
    fi
else
    # Optional: Log memory every hour instead of every minute
    MINUTE=$(date +%M)
    if [ "$MINUTE" == "00" ]; then
        MEMORY=$(redis-cli INFO memory | grep used_memory_human | cut -d: -f2)
        log "📊 Memory usage: $MEMORY"
    fi
fi
