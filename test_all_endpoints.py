#!/usr/bin/env python3
"""
Nova API Test Script - Tests all endpoints with cookie authentication
Run: python3 test_all_endpoints.py
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://31.97.220.195:8080"
SESSION_ID = "269e4e01cb0e42c19c3563e5613f6c3f"  # Your session ID
HEADERS = {
    "Cookie": f"session={SESSION_ID}",
    "Content-Type": "application/json"
}

def print_result(name, response, show_data=True):
    """Pretty print API results"""
    status = "✅" if response.status_code == 200 else "❌"
    print(f"\n{status} {name} - Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text[:200]}")
    elif show_data:
        try:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)[:500]}...")
        except:
            print(f"   Raw: {response.text[:200]}")

def test_all_endpoints():
    """Test every API endpoint"""
    print("="*60)
    print(f"🚀 TESTING NOVA API - {datetime.now().isoformat()}")
    print(f"Session: {SESSION_ID}")
    print("="*60)

    # 1. PUBLIC ENDPOINTS (No auth needed)
    print("\n📡 PUBLIC ENDPOINTS")
    
    # Root
    r = requests.get(f"{BASE_URL}/")
    print_result("GET /", r, False)
    
    # Health
    r = requests.get(f"{BASE_URL}/api/health")
    print_result("GET /api/health", r, False)
    
    # Market tickers
    r = requests.get(f"{BASE_URL}/api/market/tickers?category=spot&symbol=BTCUSDT")
    print_result("GET /api/market/tickers", r)
    
    # Market orderbook
    r = requests.get(f"{BASE_URL}/api/market/orderbook?category=spot&symbol=BTCUSDT&limit=5")
    print_result("GET /api/market/orderbook", r)
    
    # Market kline
    r = requests.get(f"{BASE_URL}/api/market/kline?category=spot&symbol=BTCUSDT&interval=1h&limit=5")
    print_result("GET /api/market/kline", r)
    
    # Market time
    r = requests.get(f"{BASE_URL}/api/market/time")
    print_result("GET /api/market/time", r)

    # 2. AUTHENTICATED ENDPOINTS (Need session)
    print("\n🔐 AUTHENTICATED ENDPOINTS")

    # V1 Balance (legacy)
    r = requests.get(f"{BASE_URL}/api/v1/balance", headers=HEADERS)
    print_result("GET /api/v1/balance", r)

    # V1 User Info
    r = requests.get(f"{BASE_URL}/api/v1/user/info", headers=HEADERS)
    print_result("GET /api/v1/user/info", r)

    # V1 Strategies
    r = requests.get(f"{BASE_URL}/api/v1/strategies", headers=HEADERS)
    print_result("GET /api/v1/strategies", r)

    # V1 Bots
    r = requests.get(f"{BASE_URL}/api/v1/bots", headers=HEADERS)
    print_result("GET /api/v1/bots", r)

    # V1 Orders
    r = requests.get(f"{BASE_URL}/api/v1/orders", headers=HEADERS)
    print_result("GET /api/v1/orders", r)

    # V1 PnL
    r = requests.get(f"{BASE_URL}/api/v1/pnl", headers=HEADERS)
    print_result("GET /api/v1/pnl", r)

    # Account wallet balance
    r = requests.get(f"{BASE_URL}/api/account/wallet-balance?account_type=UNIFIED", headers=HEADERS)
    print_result("GET /api/account/wallet-balance", r)

    # Account info
    r = requests.get(f"{BASE_URL}/api/account/info", headers=HEADERS)
    print_result("GET /api/account/info", r)

    # Trade open orders
    r = requests.get(f"{BASE_URL}/api/trade/open-orders?category=spot", headers=HEADERS)
    print_result("GET /api/trade/open-orders", r)

    # Trade order history
    r = requests.get(f"{BASE_URL}/api/trade/order-history?category=spot&limit=5", headers=HEADERS)
    print_result("GET /api/trade/order-history", r)

    # Positions list
    r = requests.get(f"{BASE_URL}/api/positions/list?category=linear", headers=HEADERS)
    print_result("GET /api/positions/list", r)

    # Positions closed PnL
    r = requests.get(f"{BASE_URL}/api/positions/closed-pnl?category=linear&limit=5", headers=HEADERS)
    print_result("GET /api/positions/closed-pnl", r)

    # Asset coin balance
    r = requests.get(f"{BASE_URL}/api/asset/coin-balance?account_type=FUND", headers=HEADERS)
    print_result("GET /api/asset/coin-balance", r)

    # P2P balance
    r = requests.get(f"{BASE_URL}/api/p2p/balance", headers=HEADERS)
    print_result("GET /api/p2p/balance", r)

    # P2P orders
    r = requests.get(f"{BASE_URL}/api/p2p/orders", headers=HEADERS)
    print_result("GET /api/p2p/orders", r)

    # 3. TEST TRADE (Use small amount!)
    print("\n💰 TEST TRADE (small amount)")
    
    trade_data = {
        "symbol": "BTCUSDT",
        "side": "Buy",
        "qty": 0.0001,  # Very small amount
        "order_type": "Market",
        "category": "spot"
    }
    
    r = requests.post(
        f"{BASE_URL}/api/trade/order",
        headers=HEADERS,
        json=trade_data
    )
    print_result("POST /api/trade/order", r)

    # 4. TEST CREATE BOT
    print("\n🤖 TEST CREATE BOT")
    
    bot_data = {
        "type": "dca",
        "symbol": "BTCUSDT",
        "amount": 10,
        "interval": 1440  # Daily
    }
    
    r = requests.post(
        f"{BASE_URL}/api/v1/bots/create",
        headers=HEADERS,
        json=bot_data
    )
    print_result("POST /api/v1/bots/create", r)

    print("\n" + "="*60)
    print("✅ TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_all_endpoints()
