#!/bin/bash
# Check if Thor is responding
if ! curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/api/health | grep -q "200"; then
    echo "$(date): ⚠️ Thor unresponsive - restarting..." >> /srv/nova-backups/thor_guardian.log
    pm2 restart nova-thor
fi
