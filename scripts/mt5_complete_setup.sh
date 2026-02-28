#!/bin/bash
# Nova MT5 Integration - Complete Setup Script
# Run this AFTER docker build completes

echo "=========================================="
echo "🚀 NOVA MT5 INTEGRATION - COMPLETE SETUP"
echo "=========================================="
echo ""

# ==========================================
# PART 1: DIRECTORY STRUCTURE
# ==========================================
echo "📁 Creating directory structure..."
cd /srv/nova-global-keys
mkdir -p mt5-docker/{config,scripts,logs,api}
mkdir -p mt5/core mt5/utils mt5/logs
touch mt5/__init__.py
touch mt5/core/__init__.py
touch mt5/utils/__init__.py
echo "✅ Directories created"
echo ""

# ==========================================
# PART 2: DOCKER-COMPOSE.YML
# ==========================================
echo "📝 Creating docker-compose.yml..."
cat > /srv/nova-global-keys/mt5-docker/docker-compose.yml << 'EOF'
version: '3.8'
services:
  mt5-terminal:
    image: ghcr.io/linuxserver/baseimage-kasmvnc:latest
    container_name: nova-mt5-terminal
    restart: unless-stopped
    ports:
      - "3000:3000"  # VNC web interface
      - "8001:8001"  # mt5linux API port
    environment:
      - VNC_USER=nova
      - VNC_PASSWORD=NovaMT5@2026
      - MT5_ACCOUNT=${MT5_ACCOUNT}
      - MT5_PASSWORD=${MT5_PASSWORD}
      - MT5_SERVER=${MT5_SERVER}
    volumes:
      - ./config:/config
      - ./scripts:/scripts
      - ./logs:/var/log/mt5
    networks:
      - nova-mt5-net
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  mt5-api-bridge:
    build:
      context: .
      dockerfile: Dockerfile.api
    container_name: nova-mt5-bridge
    restart: unless-stopped
    ports:
      - "8002:8002"
    depends_on:
      - mt5-terminal
    environment:
      - MT5_HOST=mt5-terminal
      - MT5_PORT=8001
      - REDIS_URL=redis://nova-mt5-redis:6379/0
    networks:
      - nova-mt5-net
    volumes:
      - ./logs:/app/logs

  redis:
    image: redis:7-alpine
    container_name: nova-mt5-redis
    restart: unless-stopped
    ports:
      - "6380:6379"
    networks:
      - nova-mt5-net
    volumes:
      - redis-data:/data

networks:
  nova-mt5-net:
    driver: bridge

volumes:
  redis-data:
EOF
echo "✅ docker-compose.yml created"
echo ""

# ==========================================
# PART 3: DOCKERFILE.API
# ==========================================
echo "📝 Creating Dockerfile.api..."
cat > /srv/nova-global-keys/mt5-docker/Dockerfile.api << 'EOF'
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    redis \
    httpx \
    mt5linux \
    pandas

COPY api_bridge.py .

EXPOSE 8002

CMD ["uvicorn", "api_bridge:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]
EOF
echo "✅ Dockerfile.api created"
echo ""

# ==========================================
# PART 4: API BRIDGE
# ==========================================
echo "📝 Creating API bridge (api_bridge.py)..."
cat > /srv/nova-global-keys/mt5-docker/api_bridge.py << 'EOF'
from fastapi import FastAPI, HTTPException
from mt5linux import MetaTrader5
import redis
import json
import os
from typing import Optional
from datetime import datetime

app = FastAPI(title="Nova MT5 Bridge")

# Redis connection
r = redis.Redis(
    host=os.getenv('REDIS_HOST', 'nova-mt5-redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

# MT5 connection pool
mt5_connection = None

async def get_mt5():
    """Get MT5 connection"""
    global mt5_connection
    
    if mt5_connection:
        return mt5_connection
    
    mt5_host = os.getenv('MT5_HOST', 'mt5-terminal')
    mt5_port = int(os.getenv('MT5_PORT', 8001))
    
    mt5 = MetaTrader5(host=mt5_host, port=mt5_port)
    
    # Check if already initialized
    cached = r.get('mt5:connected')
    if cached == 'true':
        mt5_connection = mt5
        return mt5
    
    # Initialize with credentials
    login = int(os.getenv('MT5_ACCOUNT', 0))
    password = os.getenv('MT5_PASSWORD', '')
    server = os.getenv('MT5_SERVER', 'Bybit-Demo')
    
    if login == 0:
        # Demo mode - don't require login
        mt5_connection = mt5
        return mt5
    
    if not mt5.initialize(login=login, password=password, server=server):
        raise Exception(f"MT5 init failed: {mt5.last_error()}")
    
    r.set('mt5:connected', 'true', ex=300)
    mt5_connection = mt5
    return mt5

@app.get("/api/v1/price/{symbol}")
async def get_price(symbol: str):
    """Get current price for gold/stock"""
    try:
        mt5 = await get_mt5()
        tick = mt5.symbol_info_tick(symbol.upper())
        
        if not tick:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        # Get symbol info for digits
        symbol_info = mt5.symbol_info(symbol.upper())
        
        price_data = {
            'symbol': symbol.upper(),
            'bid': tick.bid,
            'ask': tick.ask,
            'spread': (tick.ask - tick.bid) * (10 ** (symbol_info.digits if symbol_info else 2)),
            'digits': symbol_info.digits if symbol_info else 2,
            'time': datetime.now().isoformat()
        }
        
        # Cache in Redis
        r.setex(f"mt5:price:{symbol}", 5, json.dumps(price_data))
        
        return {
            'success': True,
            'data': price_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/account")
async def get_account():
    """Get MT5 account info"""
    try:
        mt5 = await get_mt5()
        info = mt5.account_info()
        
        if not info:
            return {
                'success': True,
                'demo_mode': True,
                'message': 'Running in demo mode'
            }
        
        return {
            'success': True,
            'balance': info.balance,
            'equity': info.equity,
            'margin': info.margin,
            'free_margin': info.margin_free,
            'margin_level': info.margin_level,
            'leverage': info.leverage,
            'currency': info.currency,
            'server': info.server,
            'login': info.login
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/positions")
async def get_positions():
    """Get open positions"""
    try:
        mt5 = await get_mt5()
        positions = mt5.positions_get()
        
        if not positions:
            return {'success': True, 'positions': []}
        
        result = []
        for pos in positions:
            result.append({
                'ticket': pos.ticket,
                'symbol': pos.symbol,
                'type': 'BUY' if pos.type == 0 else 'SELL',
                'volume': pos.volume,
                'price_open': pos.price_open,
                'price_current': pos.price_current,
                'profit': pos.profit,
                'time': datetime.fromtimestamp(pos.time).isoformat()
            })
        
        return {'success': True, 'positions': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health():
    """Health check"""
    try:
        mt5 = await get_mt5()
        version = mt5.version() if hasattr(mt5, 'version') else "Connected"
        return {
            'status': 'healthy',
            'mt5': 'connected',
            'version': str(version)
        }
    except:
        return {'status': 'degraded', 'mt5': 'disconnected'}

@app.on_event("shutdown")
async def shutdown():
    """Clean shutdown"""
    global mt5_connection
    if mt5_connection:
        try:
            mt5_connection.shutdown()
        except:
            pass
EOF
echo "✅ api_bridge.py created"
echo ""

# ==========================================
# PART 5: ENVIRONMENT FILE
# ==========================================
echo "📝 Creating .env file..."
cat > /srv/nova-global-keys/mt5-docker/.env << 'EOF'
# MT5 Credentials - Get these from Bybit
MT5_ACCOUNT=12345678
MT5_PASSWORD=your_password_here
MT5_SERVER=Bybit-Demo

# VNC Access (for manual login if needed)
VNC_PASSWORD=NovaMT5@2026
EOF
echo "✅ .env created (EDIT WITH YOUR CREDENTIALS)"
echo ""

# ==========================================
# PART 6: TEST SCRIPT (YOUR PROVIDED CODE)
# ==========================================
echo "📝 Creating test script (mt5_test.py)..."
cat > /srv/nova-global-keys/mt5_test.py << 'EOF'
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
EOF
chmod +x /srv/nova-global-keys/mt5_test.py
echo "✅ mt5_test.py created"
echo ""

# ==========================================
# PART 7: THOR ENGINE INTEGRATION
# ==========================================
echo "📝 Creating Thor Engine integration (optional)..."
cat > /srv/nova-global-keys/mt5_thor_integration.py << 'EOF'
"""
Add these endpoints to thor_engine.py
"""

"""
# Add near other imports
import httpx
from fastapi import FastAPI, HTTPException, Depends
"""

# ===== MT5 TRADFI ENDPOINTS =====
"""
@app.get("/api/v1/tradfi/price/{symbol}")
async def get_tradfi_price(symbol: str):
    # Get gold/stock price via MT5 bridge
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"http://localhost:8002/api/v1/price/{symbol}", timeout=10.0)
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MT5 bridge unavailable: {str(e)}")

@app.get("/api/v1/tradfi/account")
async def get_tradfi_account():
    # Get MT5 account info
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8002/api/v1/account", timeout=10.0)
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MT5 bridge unavailable: {str(e)}")

@app.get("/api/v1/tradfi/positions")
async def get_tradfi_positions():
    # Get open gold/stock positions
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8002/api/v1/positions", timeout=10.0)
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MT5 bridge unavailable: {str(e)}")
"""
EOF
echo "✅ mt5_thor_integration.py created (reference file)"
echo ""

# ==========================================
# PART 8: TELEGRAM BOT COMMANDS
# ==========================================
echo "📝 Creating Telegram bot command template..."
cat > /srv/nova-global-keys/mt5_telegram_commands.py << 'EOF'
"""
Add these to your Telegram bot handler
"""

# Add to your message handler:
@bot.message_handler(commands=['tradfi'])
def handle_tradfi(message):
    """Handle /tradfi command - show TradFi menu"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    btn1 = telebot.types.InlineKeyboardButton("🥇 Gold", callback_data="tradfi_XAUUSD")
    btn2 = telebot.types.InlineKeyboardButton("🍎 Apple", callback_data="tradfi_AAPL")
    btn3 = telebot.types.InlineKeyboardButton("🚗 Tesla", callback_data="tradfi_TSLA")
    btn4 = telebot.types.InlineKeyboardButton("📊 NASDAQ", callback_data="tradfi_NAS100")
    btn5 = telebot.types.InlineKeyboardButton("💰 Forex", callback_data="tradfi_EURUSD")
    btn6 = telebot.types.InlineKeyboardButton("📈 All", callback_data="tradfi_all")
    
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    
    bot.reply_to(
        message,
        "🌍 *Nova TradFi - Gold & Stocks*\n\n"
        "Select an asset to check price:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('tradfi_'))
def handle_tradfi_callback(call):
    """Handle TradFi button clicks"""
    symbol = call.data.replace('tradfi_', '')
    
    if symbol == 'all':
        # Fetch all prices
        bot.edit_message_text(
            "🔄 Fetching all TradFi prices...",
            call.message.chat.id,
            call.message.message_id
        )
        # Make API call to your Thor Engine
        # response = requests.get("http://localhost:8080/api/v1/tradfi/prices")
        # Format and send response
        bot.send_message(
            call.message.chat.id,
            "📊 *All TradFi Prices*\n\n"
            "🥇 XAUUSD: $2,345.67 (+0.45%)\n"
            "🍎 AAPL: $175.32 (-0.23%)\n"
            "🚗 TSLA: $245.67 (+1.23%)\n"
            "📊 NAS100: 18,456.78 (+0.67%)\n\n"
            "⚙️ Full integration coming soon!",
            parse_mode="Markdown"
        )
    else:
        # Fetch single symbol
        bot.edit_message_text(
            f"🔄 Fetching {symbol}...",
            call.message.chat.id,
            call.message.message_id
        )
        # Make API call to your Thor Engine
        # response = requests.get(f"http://localhost:8080/api/v1/tradfi/price/{symbol}")
        bot.send_message(
            call.message.chat.id,
            f"📈 *{symbol}*\n\n"
            f"Price: $2,345.67\n"
            f"Change: +0.45%\n\n"
            f"⚙️ Full integration coming soon!",
            parse_mode="Markdown"
        )
EOF
echo "✅ mt5_telegram_commands.py created"
echo ""

# ==========================================
# PART 9: START THE SYSTEM
# ==========================================
echo "🚀 Starting MT5 Docker stack..."
cd /srv/nova-global-keys/mt5-docker

# Check if docker-compose exists
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
else
    docker compose up -d
fi

echo ""
echo "⏳ Waiting 30 seconds for containers to initialize..."
sleep 30

# ==========================================
# PART 10: RUN TEST
# ==========================================
echo ""
echo "🧪 Running MT5 test script..."
cd /srv/nova-global-keys
python mt5_test.py

# ==========================================
# FINAL STATUS
# ==========================================
echo ""
echo "=========================================="
echo "✅ NOVA MT5 INTEGRATION COMPLETE"
echo "=========================================="
echo ""
echo "📊 Access Points:"
echo "   MT5 Bridge API: http://localhost:8002/docs"
echo "   VNC Web Interface: http://localhost:3000 (user: nova, pass: NovaMT5@2026)"
echo "   Thor Engine (your existing): http://localhost:8080/docs"
echo ""
echo "📝 Next Steps:"
echo "   1. Edit .env file with your MT5 credentials:"
echo "      nano /srv/nova-global-keys/mt5-docker/.env"
echo ""
echo "   2. Test manually:"
echo "      curl http://localhost:8002/api/v1/price/XAUUSD"
echo "      curl http://localhost:8002/api/v1/price/AAPL"
echo ""
echo "   3. Add to Thor Engine (see mt5_thor_integration.py)"
echo ""
echo "   4. Add Telegram commands (see mt5_telegram_commands.py)"
echo ""
echo "=========================================="
