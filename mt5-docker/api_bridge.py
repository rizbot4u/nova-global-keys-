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
