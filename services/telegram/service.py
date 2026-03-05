#!/usr/bin/env python3
"""
NOVA GLOBAL KEYS - Telegram Service
Official Telegram bot as a microservice
"""

import os
import sys
import logging
import time
import json
import requests
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment
load_dotenv()

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://127.0.0.1:8081")
BROKER_CODE = os.getenv("BROKER_CODE", "Kr000820")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("telegram-service")

if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN not set")
    sys.exit(1)

try:
    import telebot
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
except Exception as e:
    logger.error(f"Failed to initialize bot: {e}")
    sys.exit(1)

# ============================================================================
# COMMAND HANDLERS
# ============================================================================

@bot.message_handler(commands=['start', 'help'])
def cmd_start(message):
    """Welcome message"""
    welcome = f"""
*** Welcome to Nova Global Keys ***

Broker: {BROKER_CODE}

Commands:
/connect - Link your Bybit account
/balance - View your wallet balance
/price BTC - Get current price
/status - System check
/login - Get web login link
/help - Show this message

Example: /price BTC
    """
    bot.reply_to(message, welcome)

@bot.message_handler(commands=['status'])
def cmd_status(message):
    """System status"""
    try:
        response = requests.get(f"{GATEWAY_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            services = data.get('services', {})
            
            reply = "* System Status *\n\n"
            for service, status in services.items():
                emoji = "✅" if status else "❌"
                reply += f"{emoji} {service.capitalize()}\n"
            
            reply += f"\nRedis: {'✅' if data.get('redis') else '❌'}"
            bot.send_message(message.chat.id, reply)
        else:
            bot.send_message(message.chat.id, f"Error: Gateway returned {response.status_code}")
    except Exception as e:
        logger.error(f"Status check error: {e}")
        bot.send_message(message.chat.id, "Could not reach gateway")

@bot.message_handler(commands=['price'])
def cmd_price(message):
    """Get current price"""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /price SYMBOL\nExample: /price BTC")
            return
        
        symbol = parts[1].upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        bot.reply_to(message, f"Fetching {symbol} price...")
        
        response = requests.get(f"{GATEWAY_URL}/api/market/tickers/{symbol}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                reply = f"💰 {symbol}\n\n"
                reply += f"Price: ${data['price']:.4f}\n"
                reply += f"24h Change: {data['change_24h']:.2f}%\n"
                reply += f"24h High: ${data['high_24h']:.4f}\n"
                reply += f"24h Low: ${data['low_24h']:.4f}\n"
                reply += f"Volume: {data['volume']:.2f}"
                bot.send_message(message.chat.id, reply)
            else:
                bot.send_message(message.chat.id, f"Could not fetch price for {symbol}")
        else:
            bot.send_message(message.chat.id, f"API Error: {response.status_code}")
    except Exception as e:
        logger.error(f"Price command error: {e}")
        bot.reply_to(message, "Error fetching price")

@bot.message_handler(commands=['connect'])
def cmd_connect(message):
    """Connect Bybit account"""
    bot.reply_to(message, "Visit https://www.novatradingkeys.com to connect your Bybit account")

@bot.message_handler(commands=['login'])
def cmd_login(message):
    """Get web login link"""
    telegram_id = str(message.from_user.id)
    login_url = f"https://www.novatradingkeys.com/login?telegram={telegram_id}"
    bot.reply_to(message, f"Login to web dashboard:\n{login_url}")

@bot.message_handler(commands=['balance'])
def cmd_balance(message):
    """Get wallet balance"""
    bot.reply_to(message, "Please /connect your Bybit account first")

# ============================================================================
# HEALTH CHECK (to make it work like other microservices)
# ============================================================================

from fastapi import FastAPI
import uvicorn
from threading import Thread

# Create a small FastAPI app for health checks
health_app = FastAPI(title="Telegram Service")

@health_app.get("/health")
async def health():
    return {
        "service": "telegram",
        "status": "healthy",
        "bot_running": True,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

def run_health_server():
    """Run the health check server"""
    uvicorn.run(health_app, host="127.0.0.1", port=8007)

def run_bot():
    """Run the telegram bot"""
    logger.info("=" * 50)
    logger.info("Telegram Service Starting")
    logger.info("=" * 50)
    logger.info(f"Gateway: {GATEWAY_URL}")
    logger.info(f"Broker: {BROKER_CODE}")
    logger.info("=" * 50)
    
    # Start bot with retry logic
    retry_count = 0
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as e:
            retry_count += 1
            logger.error(f"Bot polling error (attempt {retry_count}): {e}")
            time.sleep(5)

if __name__ == "__main__":
    # Start health server in a thread
    health_thread = Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Run bot in main thread
    run_bot()
