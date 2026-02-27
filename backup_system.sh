#!/bin/bash
# Nova Global Keys - Complete Backup System
BACKUP_DIR="/srv/nova-backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_PATH="$BACKUP_DIR/nova_backup_$TIMESTAMP"

echo "🚀 Starting Nova backup at $TIMESTAMP"

# Create backup directory
mkdir -p "$BACKUP_PATH"

# 1. Backup Redis data
echo "📀 Backing up Redis..."
redis-cli save
cp /var/lib/redis/dump.rdb "$BACKUP_PATH/redis_data.rdb"

# 2. Backup Thor Engine files
echo "⚡ Backing up Thor Engine..."
cp /srv/nova-global-keys/thor_engine.py "$BACKUP_PATH/" 2>/dev/null
cp /srv/nova-global-keys/thor_v2.py "$BACKUP_PATH/" 2>/dev/null

# 3. Backup PM2 process list
echo "📋 Backing up PM2 config..."
pm2 save
cp /root/.pm2/dump.pm2 "$BACKUP_PATH/pm2_dump.json"

# 4. Backup environment config (without secrets)
echo "🔐 Backing up config..."
cp /srv/nova-global-keys/.env "$BACKUP_PATH/.env.backup" 2>/dev/null

# 5. Backup logs
echo "📊 Backing up recent logs..."
mkdir -p "$BACKUP_PATH/logs"
tail -100 /root/.pm2/logs/nova-thor-out.log > "$BACKUP_PATH/logs/thor-out.log" 2>/dev/null
tail -100 /root/.pm2/logs/thor-singleton-out.log > "$BACKUP_PATH/logs/singleton-out.log" 2>/dev/null

# 6. Create backup info
echo "Main API Requests: $(redis-cli get "stats:main_api:total_requests")" > "$BACKUP_PATH/stats.txt"
date > "$BACKUP_PATH/backup_date.txt"

# 7. Compress backup
cd "$BACKUP_DIR"
tar -czf "nova_backup_$TIMESTAMP.tar.gz" "nova_backup_$TIMESTAMP"
rm -rf "$BACKUP_PATH"

# 8. Keep last 7 days
find "$BACKUP_DIR" -name "nova_backup_*.tar.gz" -type f -mtime +7 -delete

# 9. Show result
echo "✅ Backup completed: nova_backup_$TIMESTAMP.tar.gz"
ls -lh "$BACKUP_DIR" | grep "$TIMESTAMP"
