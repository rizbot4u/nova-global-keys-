#!/usr/bin/env python3
"""
NOVA GLOBAL KEYS - Trade Service (Multi-Exchange)
"""

import os
import sys
import logging
import uuid
from datetime import datetime
from typing import Optional, List

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add shared modules to path
sys.path.append("/root/nova-global-keys-/services")
from shared.models.database import SessionLocal, ExchangeKey
from shared.exchanges import EXCHANGE_MAP
from shared.redis.client import redis_client

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trade-service")

app = FastAPI(title="Nova Trade Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

class OrderRequest(BaseModel):
    exchange: str
    symbol: str
    side: str
    order_type: str = "market"
    quantity: float
    price: Optional[float] = None

class OrderResponse(BaseModel):
    order_id: str
    exchange: str
    symbol: str
    side: str
    price: float
    quantity: float
    status: str

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    import jwt
    token = credentials.credentials
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), 
                            algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        db = SessionLocal()
        try:
            from shared.models.database import User
            user = db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            return {
                "user_id": user.id,
                "email": user.email,
                "name": user.name
            }
        finally:
            db.close()
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_user_key(user_id: int, exchange_name: str):
    db = SessionLocal()
    try:
        key = db.query(ExchangeKey).filter(
            ExchangeKey.user_id == user_id,
            ExchangeKey.exchange_name == exchange_name,
            ExchangeKey.is_active == True
        ).first()
        
        if not key:
            raise HTTPException(
                status_code=404,
                detail=f"No active {exchange_name} keys found. Connect first at /keys/connect"
            )
        
        return key
    finally:
        db.close()

async def get_exchange(user_id: int, exchange_name: str, testnet: bool = False):
    key = await get_user_key(user_id, exchange_name)
    
    exchange_class = EXCHANGE_MAP.get(exchange_name)
    if not exchange_class:
        raise HTTPException(status_code=400, detail=f"Exchange {exchange_name} not supported")
    
    if exchange_name in ['kucoin', 'okx']:
        exchange = exchange_class(key.api_key, key.api_secret, testnet=testnet)
    else:
        exchange = exchange_class(key.api_key, key.api_secret, testnet=testnet)
    
    db = SessionLocal()
    try:
        key.last_used = datetime.now()
        db.commit()
    finally:
        db.close()
    
    return exchange

@app.get("/health")
async def health():
    return {
        "service": "trade",
        "status": "healthy",
        "redis": redis_client.ping(),
        "supported_exchanges": list(EXCHANGE_MAP.keys()),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/exchanges")
async def get_supported_exchanges():
    return {
        "exchanges": list(EXCHANGE_MAP.keys()),
        "count": len(EXCHANGE_MAP)
    }

@app.post("/order", response_model=OrderResponse)
async def place_order(
    order: OrderRequest,
    current_user: dict = Depends(get_current_user)
):
    exchange = await get_exchange(current_user["user_id"], order.exchange)
    
    try:
        result = await exchange.place_order(
            symbol=order.symbol,
            side=order.side,
            order_type=order.order_type,
            quantity=order.quantity,
            price=order.price
        )
        
        if result.get('success', False) or result.get('retCode') == 0:
            order_id = result.get('data', {}).get('orderId') or \
                      result.get('result', {}).get('orderId') or \
                      str(uuid.uuid4())
            
            return OrderResponse(
                order_id=order_id,
                exchange=order.exchange,
                symbol=order.symbol,
                side=order.side,
                price=order.price or 0,
                quantity=order.quantity,
                status="created"
            )
        else:
            error_msg = result.get('retMsg') or result.get('error') or "Order failed"
            raise HTTPException(status_code=400, detail=error_msg)
    finally:
        await exchange.close()

@app.get("/balance")
async def get_balance(
    exchange: str = Query(..., description="Exchange name"),
    current_user: dict = Depends(get_current_user)
):
    ex = await get_exchange(current_user["user_id"], exchange)
    
    try:
        result = await ex.get_balance()
        formatted = ex.format_balance(result)
        return formatted
    finally:
        await ex.close()

@app.get("/ticker/{symbol}")
async def get_ticker(
    exchange: str,
    symbol: str,
    current_user: dict = Depends(get_current_user)
):
    ex = await get_exchange(current_user["user_id"], exchange)
    
    try:
        result = await ex.get_ticker(symbol)
        return result
    finally:
        await ex.close()

@app.get("/orders/open")
async def get_open_orders(
    exchange: str,
    symbol: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    ex = await get_exchange(current_user["user_id"], exchange)
    
    try:
        orders = await ex.get_open_orders(symbol)
        return {"exchange": exchange, "orders": orders}
    finally:
        await ex.close()

@app.post("/order/cancel")
async def cancel_order(
    exchange: str,
    symbol: str,
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    ex = await get_exchange(current_user["user_id"], exchange)
    
    try:
        result = await ex.cancel_order(symbol, order_id)
        return {"success": True, "exchange": exchange, "result": result}
    finally:
        await ex.close()

@app.get("/deposit/address")
async def get_deposit_address(
    exchange: str,
    coin: str,
    current_user: dict = Depends(get_current_user)
):
    ex = await get_exchange(current_user["user_id"], exchange)
    
    try:
        result = await ex.get_deposit_address(coin)
        return result
    finally:
        await ex.close()

@app.post("/withdraw")
async def withdraw(
    exchange: str,
    coin: str,
    address: str,
    amount: float,
    network: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    ex = await get_exchange(current_user["user_id"], exchange)
    
    try:
        result = await ex.withdraw(coin, address, amount, network)
        return result
    finally:
        await ex.close()

if __name__ == "__main__":
    port = int(os.getenv("TRADE_SERVICE_PORT", 8004))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
