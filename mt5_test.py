#!/usr/bin/env python3
"""
Nova MT5 Test Script
Run this to verify MT5 connection and fetch gold/stocks
"""

import sys
import time
from mt5linux import MetaTrader5

def main():
    print("=" * 50)
    print("🚀 NOVA MT5 CONNECTION TEST")
    print("=" * 50)
    
    # Connect to Docker container
    print("\n🔌 Connecting to MT5 container...")
    try:
        mt5 = MetaTrader5(host='localhost', port=8001)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Make sure Docker container is running:")
        print("   cd /srv/nova-global-keys/mt5-docker")
        print("   docker-compose up -d")
        sys.exit(1)
    
    # Initialize (demo mode - no login required for basic price fetch)
    print("📡 Initializing MT5 client...")
    
    # Get gold price
    print("\n🥇 Testing Gold (XAUUSD):")
    tick = mt5.symbol_info_tick("XAUUSD")
    if tick:
        print(f"   ✅ Gold: ${tick.ask:.2f}")
        print(f"   Bid: ${tick.bid:.2f}")
        print(f"   Spread: ${(tick.ask - tick.bid):.2f}")
    else:
        print("   ❌ Could not fetch gold price")
    
    # Get Apple stock
    print("\n🍎 Testing Apple (AAPL):")
    tick = mt5.symbol_info_tick("AAPL")
    if tick:
        print(f"   ✅ Apple: ${tick.ask:.2f}")
        print(f"   Bid: ${tick.bid:.2f}")
    else:
        print("   ❌ Could not fetch AAPL")
    
    # Get Tesla stock
    print("\n🚗 Testing Tesla (TSLA):")
    tick = mt5.symbol_info_tick("TSLA")
    if tick:
        print(f"   ✅ Tesla: ${tick.ask:.2f}")
    else:
        print("   ❌ Could not fetch TSLA")
    
    # Get NASDAQ
    print("\n📊 Testing NASDAQ (NAS100):")
    tick = mt5.symbol_info_tick("NAS100")
    if tick:
        print(f"   ✅ NASDAQ: ${tick.ask:.2f}")
    else:
        print("   ❌ Could not fetch NAS100")
    
    # Try getting multiple symbols at once
    print("\n📈 Fetching multiple symbols...")
    symbols = ["XAUUSD", "AAPL", "TSLA", "MSFT", "AMZN", "GOOGL", "NAS100", "SP500", "EURUSD"]
    
    for symbol in symbols:
        tick = mt5.symbol_info_tick(symbol)
        if tick:
            print(f"   ✅ {symbol}: ${tick.ask:.2f}")
        else:
            print(f"   ❌ {symbol}: Not available")
        time.sleep(0.1)
    
    # Get account info (if logged in)
    print("\n👤 Account Info:")
    account = mt5.account_info()
    if account:
        print(f"   Balance: ${account.balance:.2f}")
        print(f"   Equity: ${account.equity:.2f}")
        print(f"   Leverage: 1:{account.leverage}")
    else:
        print("   ⚠️ Not logged in (demo mode - price fetch only)")
    
    # Cleanup
    mt5.shutdown()
    
    print("\n" + "=" * 50)
    print("✅ Test complete")
    print("=" * 50)

if __name__ == "__main__":
    main()
