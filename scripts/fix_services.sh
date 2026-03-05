#!/bin/bash

echo "🔧 Fixing Market Service (adding os import)..."
sed -i '1iimport os' /root/nova-global-keys-/services/market/main.py

echo "🔧 Fixing Telegram Bot (removing markdown)..."
sed -i 's/, parse_mode="Markdown"//g' /root/nova-global-keys-/bot/telegram_bot.py

echo "🔧 Adding OAuth callback endpoint..."
cat >> /root/nova-global-keys-/services/auth/main.py << 'EOF2'

@app.get("/callback/bybit")
async def callback_bybit(code: str, state: str):
    return await bybit_callback(code, state)
EOF2

echo "🚀 Restarting all services..."
pm2 restart all

echo "✅ Fixes applied! Waiting 5 seconds..."
sleep 5

echo "📊 Service Status:"
pm2 status

echo "🧪 Testing gateway health:"
curl -s http://127.0.0.1:8081/health | python3 -m json.tool

echo "🧪 Testing market data:"
curl -s http://127.0.0.1:8081/api/market/tickers/BTCUSDT | python3 -m json.tool

echo "✅ Done!"
