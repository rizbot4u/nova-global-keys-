"""Helper utilities for MT5 operations"""

import time
from typing import Dict, List
from datetime import datetime, timedelta

def format_price(price: float, symbol: str = "XAUUSD") -> str:
    """Format price based on symbol digits"""
    if symbol.startswith("XAU"):  # Gold
        return f"${price:,.2f}"
    elif symbol.startswith("AAPL") or symbol.startswith("TSLA"):  # Stocks
        return f"${price:,.2f}"
    elif symbol.startswith("NAS") or symbol.startswith("SP"):  # Indices
        return f"{price:,.2f}"
    else:
        return f"{price:,.4f}"

def calculate_pips(entry: float, exit: float, symbol: str) -> float:
    """Calculate pips for forex/gold"""
    if "JPY" in symbol:
        return (exit - entry) * 100
    elif "XAU" in symbol:
        return (exit - entry) / 0.01  # Gold pips = $0.01
    else:
        return (exit - entry) * 10000

def risk_percentage(balance: float, risk_pct: float, stop_loss_pips: float, pip_value: float) -> float:
    """Calculate position size based on risk percentage"""
    risk_amount = balance * (risk_pct / 100)
    position_size = risk_amount / (stop_loss_pips * pip_value)
    return round(position_size, 2)

def get_market_session() -> str:
    """Determine current market session"""
    now = datetime.utcnow()
    hour = now.hour
    
    if 0 <= hour < 8:
        return "Asia"
    elif 8 <= hour < 13:
        return "London"
    elif 13 <= hour < 22:
        return "New York"
    else:
        return "Asia"

def is_market_open(symbol: str) -> bool:
    """Check if market is open for given symbol"""
    now = datetime.utcnow()
    weekday = now.weekday()  # 0-4 = Mon-Fri
    
    if weekday >= 5:  # Weekend
        return False
    
    hour = now.hour
    
    # Forex: 24/5
    if symbol in ["EURUSD", "GBPUSD", "USDJPY"]:
        return True
    
    # Gold: 24/5 (but less liquid on weekends)
    if symbol == "XAUUSD":
        return True
    
    # Stocks: 13:30-20:00 UTC (9:30-16:00 NY time)
    if symbol in ["AAPL", "TSLA", "MSFT", "AMZN"]:
        return 13 <= hour < 20
    
    return True

