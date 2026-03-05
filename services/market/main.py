#!/usr/bin/env python3
"""
NOVA GLOBAL KEYS - Market Service
Fetches tickers, orderbook, kline data from exchanges
"""

import os  # <-- THIS MUST BE HERE
import sys
import logging
from datetime import datetime
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment
load_dotenv()
# Add shared modules to path
sys.path.append("/root/nova-global-keys-/services")
from shared.utils.bybit import ThorEngine
from shared.redis.client import redis_client

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("market-service")

# FastAPI app
app = FastAPI(title="Nova Market Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache TTL (seconds)
CACHE_TTL = 5  # 5 seconds for orderbook, 30 for tickers

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health")
async def health():
    return {
        "service": "market",
        "status": "healthy",
        "redis": redis_client.ping(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/tickers/{symbol}")
async def get_ticker(symbol: str, category: str = "spot"):
    # Check cache first
    cache_key = f"market:ticker:{category}:{symbol}"
    cached = redis_client.client.get(cache_key)
    if cached:
        import json
        return json.loads(cached)
    
    engine = ThorEngine()
    try:
        result = await engine.get_tickers(category=category, symbol=symbol)
        
        if result.get('retCode') == 0 and result.get('result', {}).get('list'):
            ticker = result['result']['list'][0]
            formatted = {
                "success": True,
                "symbol": ticker.get('symbol', ''),
                "price": float(ticker.get('lastPrice', 0)),
                "change_24h": float(ticker.get('price24hPcnt', 0)) * 100,
                "high_24h": float(ticker.get('highPrice24h', 0)),
                "low_24h": float(ticker.get('lowPrice24h', 0)),
                "volume": float(ticker.get('volume24h', 0))
            }
            
            # Cache for 30 seconds
            import json
            redis_client.client.setex(cache_key, 30, json.dumps(formatted))
            
            return formatted
        
        return {"success": False, "error": "Could not fetch price"}
    finally:
        await engine.close()

@app.get("/tickers")
async def get_all_tickers(category: str = "spot"):
    cache_key = f"market:tickers:{category}"
    cached = redis_client.client.get(cache_key)
    if cached:
        import json
        return json.loads(cached)
    
    engine = ThorEngine()
    try:
        result = await engine.get_tickers(category=category)
        
        if result.get('retCode') == 0:
            # Cache for 30 seconds
            import json
            redis_client.client.setex(cache_key, 30, json.dumps(result))
        
        return result
    finally:
        await engine.close()

@app.get("/orderbook/{symbol}")
async def get_orderbook(symbol: str, category: str = "spot", limit: int = 25):
    cache_key = f"market:orderbook:{category}:{symbol}:{limit}"
    cached = redis_client.client.get(cache_key)
    if cached:
        import json
        return json.loads(cached)
    
    engine = ThorEngine()
    try:
        result = await engine.get_orderbook(category=category, symbol=symbol, limit=limit)
        
        if result.get('retCode') == 0:
            # Cache for 5 seconds
            import json
            redis_client.client.setex(cache_key, CACHE_TTL, json.dumps(result))
        
        return result
    finally:
        await engine.close()

@app.get("/kline/{symbol}")
async def get_kline(
    symbol: str,
    category: str = "spot",
    interval: str = "D",
    limit: int = 200
):
    cache_key = f"market:kline:{category}:{symbol}:{interval}:{limit}"
    cached = redis_client.client.get(cache_key)
    if cached:
        import json
        return json.loads(cached)
    
    engine = ThorEngine()
    try:
        result = await engine.get_kline(
            category=category,
            symbol=symbol,
            interval=interval,
            limit=limit
        )
        
        if result.get('retCode') == 0:
            # Cache for 60 seconds (kline changes slower)
            import json
            redis_client.client.setex(cache_key, 60, json.dumps(result))
        
        return result
    finally:
        await engine.close()

@app.get("/instruments")
async def get_instruments(category: str = "spot", symbol: Optional[str] = None):
    cache_key = f"market:instruments:{category}:{symbol or 'all'}"
    cached = redis_client.client.get(cache_key)
    if cached:
        import json
        return json.loads(cached)
    
    engine = ThorEngine()
    try:
        result = await engine.get_instruments(category=category, symbol=symbol)
        
        if result.get('retCode') == 0:
            # Cache for 1 hour (instruments change rarely)
            import json
            redis_client.client.setex(cache_key, 3600, json.dumps(result))
        
        return result
    finally:
        await engine.close()

@app.get("/time")
async def get_server_time():
    engine = ThorEngine()
    try:
        return await engine.get_server_time()
    finally:
        await engine.close()

if __name__ == "__main__":
    port = int(os.getenv("MARKET_SERVICE_PORT", 8003))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
