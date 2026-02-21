"""
Nova Global Keys - Utility Functions
Shared helpers for logging, formatting, etc.
"""

import logging
import sys
from typing import Any, Dict
from datetime import datetime
from config.settings import settings

def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(settings.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )

def format_balance(coins: list) -> str:
    """Format balance data for display"""
    lines = []
    total_usd = 0
    
    for coin in coins:
        name = coin.get('coin', '')
        balance = float(coin.get('walletBalance', '0'))
        usd_value = float(coin.get('usdValue', '0'))
        
        if balance > 0:
            lines.append(f"• {name}: {balance:.4f} (${usd_value:.2f})")
            total_usd += usd_value
    
    return "\n".join(lines), total_usd

def format_price(ticker: Dict) -> str:
    """Format ticker data for display"""
    try:
        price = float(ticker.get('lastPrice', 0))
        change = float(ticker.get('price24hPcnt', 0)) * 100
        high = float(ticker.get('highPrice24h', 0))
        low = float(ticker.get('lowPrice24h', 0))
        volume = float(ticker.get('volume24h', 0))
        
        return f"""
📊 Price: ${price:,.2f}
📈 24h: {change:+.2f}%
📊 High: ${high:,.2f}
📉 Low: ${low:,.2f}
📦 Volume: {volume:.2f}
        """
    except:
        return "Price data unavailable"
