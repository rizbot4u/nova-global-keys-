#!/bin/bash

echo "🔧 Fixing Market Service (adding os import)..."
# Add os import if missing
if ! grep -q "^import os" /root/nova-global-keys-/services/market/main.py; then
    sed -i '1iimport os' /root/nova-global-keys-/services/market/main.py
fi

echo "🔧 Fixing Telegram Bot (restoring original)..."
# Let's restore a working version of the telegram bot
cat > /root/nova-global-keys-/bot/telegram_bot.py << 'TELEGRAM'
#!/usr/bin/env python3
"""
NOVA GLOBAL KEYS - Telegram Bot
Chat-based interface for trading, remittance, and agent management
"""

import os
import sys
import logging
import asyncio
import json
from datetime import datetime
from typing import Optional

import telebot
import httpx
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add shared modules to path
sys.path.append("/root/nova-global-keys-/services")
from shared.redis.client import redis_client

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://127.0.0.1:8081")
BROKER_CODE = os.getenv("BROKER_CODE", "Kr000820")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("telegram-bot")

# Initialize bot
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN not set")
    sys.exit(1)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# HTTP client for API calls
client = httpx.AsyncClient(timeout=30.0)

# ============================================================================
# COMMAND HANDLERS
# ============================================================================

@bot.message_handler(commands=['start', 'help'])
def cmd_start(message):
    """Welcome message"""
    welcome = f"""
✨ Welcome to Nova Global Keys ✨

Broker: {BROKER_CODE}

Commands:
/connect - Link your Bybit account
/balance - View your wallet balance
/price BTC - Get current price
/order - Place an order
/orders - View open orders
/p2p - P2P balance and orders
/status - System check
/login - Get web login link
/help - Show this message

Example: /price BTC
    """
    bot.reply_to(message, welcome)

@bot.message_handler(commands=['status'])
def cmd_status(message):
    """System status"""
    bot.reply_to(message, "🔄 Checking system status...")
    
    # Run async fetch
    asyncio.run_coroutine_threadsafe(
        check_status(message.chat.id),
        asyncio.new_event_loop()
    )

async def check_status(chat_id: int):
    """Async status check"""
    try:
        resp = await client.get(f"{GATEWAY_URL}/health")
        
        if resp.status_code == 200:
            data = resp.json()
            services = data.get('services', {})
            
            reply = "✅ *System Status*\n\n"
            for service, status in services.items():
                emoji = "✅" if status else "❌"
                reply += f"{emoji} {service.capitalize()}\n"
            
            reply += f"\nRedis: {'✅' if data.get('redis') else '❌'}"
            bot.send_message(chat_id, reply)
        else:
            bot.send_message(chat_id, f"❌ Gateway Error: {resp.status_code}")
    except Exception as e:
        logger.error(f"Status check error: {e}")
        bot.send_message(chat_id, "❌ Could not reach gateway")

@bot.message_handler(commands=['price'])
def cmd_price(message):
    """Get current price"""
    try:
        # Extract symbol from message
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Usage: /price SYMBOL\nExample: /price BTC")
            return
        
        symbol = parts[1].upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        bot.reply_to(message, f"🔄 Fetching {symbol} price...")
        
        # Run async fetch
        asyncio.run_coroutine_threadsafe(
            fetch_price(symbol, message.chat.id),
            asyncio.new_event_loop()
        )
    except Exception as e:
        logger.error(f"Price command error: {e}")
        bot.reply_to(message, "❌ Error processing command")

async def fetch_price(symbol: str, chat_id: int):
    """Async price fetch"""
    try:
        resp = await client.get(
            f"{GATEWAY_URL}/api/market/tickers/{symbol}"
        )
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                reply = f"💰 {symbol}\n\n"
                reply += f"Price: ${data['price']:.4f}\n"
                reply += f"24h Change: {data['change_24h']:.2f}%\n"
                reply += f"24h High: ${data['high_24h']:.4f}\n"
                reply += f"24h Low: ${data['low_24h']:.4f}\n"
                reply += f"Volume: {data['volume']:.2f}"
                bot.send_message(chat_id, reply)
            else:
                bot.send_message(chat_id, f"❌ Could not fetch price for {symbol}")
        else:
            bot.send_message(chat_id, f"❌ API Error: {resp.status_code}")
    except Exception as e:
        logger.error(f"Price fetch error: {e}")
        bot.send_message(chat_id, "❌ Error fetching price")

# ============================================================================
# MAIN
# ============================================================================

def main():
    logger.info("=" * 50)
    logger.info("🚀 Nova Telegram Bot Starting")
    logger.info("=" * 50)
    logger.info(f"Gateway: {GATEWAY_URL}")
    logger.info(f"Broker: {BROKER_CODE}")
    logger.info("=" * 50)
    
    # Start bot
    bot.infinity_polling()

if __name__ == "__main__":
    main()
TELEGRAM

echo "🚀 Restarting all services..."
pm2 restart all

echo "⏳ Waiting 5 seconds for services to start..."
sleep 5

echo "📊 Service Status:"
pm2 status

echo "🧪 Testing gateway health:"
curl -s http://127.0.0.1:8081/health | python3 -m json.tool || echo "Gateway not responding yet"

echo "🧪 Testing market data:"
curl -s http://127.0.0.1:8081/api/market/tickers/BTCUSDT | python3 -m json.tool || echo "Market not responding yet"

echo "✅ Fixes applied!"
