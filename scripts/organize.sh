#!/bin/bash
# organize_nova.sh - Clean up and organize Nova Global Keys directory

echo "🚀 Organizing Nova Global Keys Directory..."
cd /root/nova-global-keys-

# Create organized directory structure
mkdir -p {core,services,scripts,config,logs,backups,deprecated,tests,workers,signals,social_bot,api}

# 1. CORE FILES (Main engine files)
echo "📦 Moving core files..."
mv thor_engine.py core/ 2>/dev/null
mv thor_v2.py core/ 2>/dev/null
mv main.py core/ 2>/dev/null

# 2. SERVICES (Running services)
echo "🔧 Moving service files..."
mv nova_reporter.py services/ 2>/dev/null
mv nova_reporter_fixed.py services/ 2>/dev/null
mv signal-bot services/ 2>/dev/null
mv sentiment-bot services/ 2>/dev/null

# 3. SCRIPTS (Startup and utility scripts)
echo "📜 Moving scripts..."
mv *.sh scripts/ 2>/dev/null
mv start_* scripts/ 2>/dev/null
mv run_* scripts/ 2>/dev/null
mv backup_* scripts/ 2>/dev/null
mv create_* scripts/ 2>/dev/null
mv launch_* scripts/ 2>/dev/null
mv setup_* scripts/ 2>/dev/null

# 4. CONFIG FILES
echo "⚙️ Moving config files..."
mv .env config/ 2>/dev/null
mv ecosystem.config.js config/ 2>/dev/null
mv ecosystem.config.js.backup config/ 2>/dev/null
mv requirements.txt config/ 2>/dev/null

# 5. TEST FILES
echo "🧪 Moving test files..."
mv test_* tests/ 2>/dev/null
mv *_test.py tests/ 2>/dev/null
mv check_* tests/ 2>/dev/null

# 6. WORKERS (If directory exists)
echo "👷 Moving worker files..."
if [ -d "workers" ]; then
    mv workers/* workers/ 2>/dev/null
fi

# 7. SIGNALS
echo "📡 Moving signal files..."
if [ -d "signals" ]; then
    mv signals/* signals/ 2>/dev/null
fi

# 8. SOCIAL BOT
echo "🤖 Moving social bot files..."
if [ -d "social_bot" ]; then
    mv social_bot/* social_bot/ 2>/dev/null
fi

# 9. API FILES
echo "🌐 Moving API files..."
if [ -d "api" ]; then
    mv api/* api/ 2>/dev/null
fi

# 10. BACKUP OLD FILES
echo "💾 Moving backup files..."
mkdir -p backups/old
mv *.backup backups/old/ 2>/dev/null
mv *.backup_latest backups/old/ 2>/dev/null
mv *.broken backups/old/ 2>/dev/null
mv *.{",'} backups/old/ 2>/dev/null

# 11. DEPRECATED FILES
echo "🗑️ Moving deprecated files..."
mv mt5* deprecated/ 2>/dev/null
mv circle* deprecated/ 2>/dev/null
mv remittance deprecated/ 2>/dev/null
mv payments deprecated/ 2>/dev/null
mv strategies deprecated/ 2>/dev/null

# 12. LOGS
echo "📊 Moving logs..."
mv logs/* logs/ 2>/dev/null

# 13. Create symlinks for easy access
echo "🔗 Creating symlinks..."
ln -sf /root/nova-global-keys-/core/thor_engine.py /root/nova-global-keys-/thor_engine.py
ln -sf /root/nova-global-keys-/core/thor_v2.py /root/nova-global-keys-/thor_v2.py
ln -sf /root/nova-global-keys-/config/.env /root/nova-global-keys-/.env

# 14. Update PM2 paths
echo "🔄 Updating PM2..."
pm2 delete all
cd /root/nova-global-keys-
pm2 start core/thor_engine.py --name nova-thor --interpreter python3
pm2 start scripts/thor_guardian.sh --name thor-guardian --interpreter bash
pm2 start services/nova_reporter_fixed.py --name nova-reporter --interpreter python3
pm2 start core/thor_v2.py --name thor-singleton --interpreter python3 -- --host 0.0.0.0 --port 8081
pm2 start signals/signal_bot.py --name signal-bot --interpreter python3

# 15. Save PM2 config
pm2 save
pm2 startup

echo "✅ Organization complete!"
echo ""
echo "📁 New structure:"
echo "├── core/           - Main engine files"
echo "├── services/       - Running services"
echo "├── scripts/        - Startup scripts"
echo "├── config/         - Configuration files"
echo "├── tests/          - Test files"
echo "├── workers/        - Worker scripts"
echo "├── signals/        - Signal bot"
echo "├── social_bot/     - Social media bot"
echo "├── api/            - API endpoints"
echo "├── logs/           - Log files"
echo "├── backups/        - Backups"
echo "└── deprecated/     - Old files"
echo ""
echo "🚀 All services restarted with new paths"
