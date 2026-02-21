"""MT5 Configuration for Nova Global Keys"""

import os
from pathlib import Path

# MT5 paths
MT5_DATA_PATH = "/root/.wine/drive_c/Program Files/MetaTrader 5"
MT5_TERMINAL_PATH = "/root/.wine/drive_c/Program Files/MetaTrader 5/terminal64.exe"

# MT5 Login credentials (get these from Bybit)
MT5_LOGIN = int(os.getenv("MT5_LOGIN", 0))  # Your MT5 account number
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")  # Your MT5 password
MT5_SERVER = os.getenv("MT5_SERVER", "Bybit-Demo")  # or "Bybit-Live"

# Symbols we want to track
TRADFI_SYMBOLS = {
    "XAUUSD": "Gold",
    "AAPL": "Apple Inc.",
    "TSLA": "Tesla Inc.",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "NAS100": "NASDAQ 100",
    "SP500": "S&P 500",
    "EURUSD": "Euro/US Dollar",
    "BTCUSD": "Bitcoin/USD (CFD)"
}

# Logging
LOG_DIR = Path("/srv/nova-global-keys/mt5/logs")
LOG_DIR.mkdir(exist_ok=True)
