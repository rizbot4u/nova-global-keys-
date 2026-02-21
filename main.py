#!/usr/bin/env python3
"""
Nova Global Keys - Main Entry Point
Starts both FastAPI server and Telegram bot
"""

import threading
import logging
import uvicorn
from config.settings import settings
from core.utils import setup_logging
from core.redis_client import redis_client
from bot.runner import TelegramBot
from api.server import create_app

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("🚀 NOVA GLOBAL KEYS - STARTING SYSTEM")
    logger.info("=" * 60)
    logger.info(f"Broker: {settings.BROKER_CODE}")
    logger.info(f"Redis: {'✅' if redis_client.ping() else '❌'}")
    logger.info("=" * 60)
    
    # Create FastAPI app
    app = create_app()
    
    # Start Telegram bot in background
    telegram_bot = TelegramBot()
    bot_thread = threading.Thread(target=telegram_bot.run, daemon=True)
    bot_thread.start()
    logger.info("✅ Telegram bot started")
    
    # Start FastAPI server
    logger.info(f"✅ API server starting on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    main()
