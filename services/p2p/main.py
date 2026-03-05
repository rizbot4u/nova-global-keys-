#!/usr/bin/env python3
"""
NOVA GLOBAL KEYS - P2P Service
Handles P2P balances, ads, orders
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add shared modules to path
sys.path.append("/root/nova-global-keys-/services")
from shared.models.database import SessionLocal, ExchangeKey
from shared.utils.bybit import ThorEngine
from shared.redis.client import redis_client

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("p2p-service")

# FastAPI app
app = FastAPI(title="Nova P2P Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Auth helper
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    import jwt
    token = credentials.credentials
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
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
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_user_key(user_id: int):
    db = SessionLocal()
    try:
        key = db.query(ExchangeKey).filter(
            ExchangeKey.user_id == user_id,
            ExchangeKey.exchange_name == "bybit",
            ExchangeKey.is_active == True
        ).first()
        
        if not key:
            raise HTTPException(status_code=404, detail="No active Bybit keys found")
        
        return key
    finally:
        db.close()

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health")
async def health():
    return {
        "service": "p2p",
        "status": "healthy",
        "redis": redis_client.ping(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/balance")
async def get_p2p_balance(
    coin: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    key = await get_user_key(current_user["user_id"])
    
    engine = ThorEngine(key.api_key, key.api_secret)
    try:
        result = await engine.get_p2p_balance(coin=coin)
        
        if result.get('retCode') == 0:
            db = SessionLocal()
            try:
                key.last_used = datetime.now()
                db.commit()
            finally:
                db.close()
        
        return result
    finally:
        await engine.close()

@app.get("/orders")
async def get_p2p_orders(
    side: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    key = await get_user_key(current_user["user_id"])
    
    engine = ThorEngine(key.api_key, key.api_secret)
    try:
        result = await engine.get_p2p_orders(
            side=side,
            status=status,
            limit=limit
        )
        
        if result.get('retCode') == 0:
            db = SessionLocal()
            try:
                key.last_used = datetime.now()
                db.commit()
            finally:
                db.close()
        
        return result
    finally:
        await engine.close()

@app.get("/stats")
async def get_p2p_stats(current_user: dict = Depends(get_current_user)):
    # This would aggregate P2P data
    # For now, return basic info
    return {
        "total_orders": 0,
        "total_volume_usd": 0,
        "active_orders": 0,
        "completed_orders": 0
    }

if __name__ == "__main__":
    port = int(os.getenv("P2P_SERVICE_PORT", 8005))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
