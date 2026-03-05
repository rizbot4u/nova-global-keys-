#!/usr/bin/env python3
"""
NOVA GLOBAL KEYS - User Service
Manages user profiles, exchange keys, bot settings
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Optional

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
from shared.models.database import SessionLocal, User, ExchangeKey, UserBot
from shared.redis.client import redis_client

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("user-service")

# FastAPI app
app = FastAPI(title="Nova User Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Pydantic models
class ConnectExchangeRequest(BaseModel):
    exchange_name: str
    api_key: str
    api_secret: str
    nickname: Optional[str] = None

class ExchangeKeyResponse(BaseModel):
    id: int
    exchange_name: str
    nickname: Optional[str]
    api_key_masked: str
    is_active: bool
    created_at: str

class BotConfig(BaseModel):
    bot_name: str
    exchange_key_id: int
    strategy: str
    symbol: str
    config: dict

# Helpers
def mask_api_key(api_key: str) -> str:
    if len(api_key) <= 8:
        return "****"
    return api_key[:4] + "..." + api_key[-4:]

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # This would call auth service in production
    # For now, decode JWT locally
    import jwt
    token = credentials.credentials
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        db = SessionLocal()
        try:
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

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health")
async def health():
    return {
        "service": "user",
        "status": "healthy",
        "redis": redis_client.ping(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return current_user

@app.post("/keys/connect")
async def connect_exchange(
    request: ConnectExchangeRequest,
    current_user: dict = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        # Check if keys already exist
        existing = db.query(ExchangeKey).filter(
            ExchangeKey.user_id == current_user["user_id"],
            ExchangeKey.exchange_name == request.exchange_name,
            ExchangeKey.is_active == True
        ).first()
        
        if existing:
            existing.api_key = request.api_key
            existing.api_secret = request.api_secret
            if request.nickname:
                existing.nickname = request.nickname
            existing.last_used = datetime.now()
            message = f"{request.exchange_name} keys updated"
        else:
            new_key = ExchangeKey(
                user_id=current_user["user_id"],
                exchange_name=request.exchange_name,
                api_key=request.api_key,
                api_secret=request.api_secret,
                nickname=request.nickname or f"My {request.exchange_name} Account"
            )
            db.add(new_key)
            message = f"{request.exchange_name} connected successfully"
        
        db.commit()
        logger.info(f"✅ Keys stored for user {current_user['user_id']}")
        
        # Also store in Redis for quick access
        redis_client.store_user_keys(
            str(current_user["user_id"]),
            request.api_key,
            request.api_secret
        )
        
        return {"status": "success", "message": message}
    finally:
        db.close()

@app.get("/keys/list", response_model=List[ExchangeKeyResponse])
async def list_keys(current_user: dict = Depends(get_current_user)):
    db = SessionLocal()
    try:
        keys = db.query(ExchangeKey).filter(
            ExchangeKey.user_id == current_user["user_id"],
            ExchangeKey.is_active == True
        ).all()
        
        return [
            ExchangeKeyResponse(
                id=key.id,
                exchange_name=key.exchange_name,
                nickname=key.nickname,
                api_key_masked=mask_api_key(key.api_key),
                is_active=key.is_active,
                created_at=key.created_at.isoformat()
            )
            for key in keys
        ]
    finally:
        db.close()

@app.delete("/keys/{key_id}")
async def delete_key(key_id: int, current_user: dict = Depends(get_current_user)):
    db = SessionLocal()
    try:
        key = db.query(ExchangeKey).filter(
            ExchangeKey.id == key_id,
            ExchangeKey.user_id == current_user["user_id"]
        ).first()
        
        if not key:
            raise HTTPException(status_code=404, detail="Key not found")
        
        key.is_active = False
        db.commit()
        
        # Remove from Redis
        redis_client.client.delete(f"user:{current_user['user_id']}:api_key")
        redis_client.client.delete(f"user:{current_user['user_id']}:api_secret")
        
        return {"status": "success", "message": "Key removed"}
    finally:
        db.close()

@app.get("/keys/{key_id}/test")
async def test_key(key_id: int, current_user: dict = Depends(get_current_user)):
    db = SessionLocal()
    try:
        key = db.query(ExchangeKey).filter(
            ExchangeKey.id == key_id,
            ExchangeKey.user_id == current_user["user_id"],
            ExchangeKey.is_active == True
        ).first()
        
        if not key:
            raise HTTPException(status_code=404, detail="Active key not found")
        
        # Test connection
        from shared.utils.bybit import ThorEngine
        engine = ThorEngine(key.api_key, key.api_secret)
        test_result = await engine.get_server_time()
        await engine.close()
        
        if test_result.get('retCode') == 0:
            key.last_used = datetime.now()
            db.commit()
            return {"status": "success", "message": "Connection valid"}
        else:
            return {"status": "error", "message": "Connection failed"}
    finally:
        db.close()

@app.post("/bots/create")
async def create_bot(config: BotConfig, current_user: dict = Depends(get_current_user)):
    db = SessionLocal()
    try:
        # Verify key belongs to user
        key = db.query(ExchangeKey).filter(
            ExchangeKey.id == config.exchange_key_id,
            ExchangeKey.user_id == current_user["user_id"],
            ExchangeKey.is_active == True
        ).first()
        
        if not key:
            raise HTTPException(status_code=404, detail="Exchange key not found")
        
        import json
        new_bot = UserBot(
            user_id=current_user["user_id"],
            bot_name=config.bot_name,
            exchange_key_id=config.exchange_key_id,
            strategy=config.strategy,
            symbol=config.symbol,
            config=json.dumps(config.config)
        )
        
        db.add(new_bot)
        db.commit()
        db.refresh(new_bot)
        
        return {
            "status": "success",
            "bot_id": new_bot.id,
            "message": "Bot created"
        }
    finally:
        db.close()

@app.get("/bots/list")
async def list_bots(current_user: dict = Depends(get_current_user)):
    db = SessionLocal()
    try:
        bots = db.query(UserBot).filter(UserBot.user_id == current_user["user_id"]).all()
        
        import json
        result = []
        for bot in bots:
            result.append({
                "id": bot.id,
                "name": bot.bot_name,
                "strategy": bot.strategy,
                "symbol": bot.symbol,
                "status": bot.status,
                "config": json.loads(bot.config) if bot.config else {},
                "created_at": bot.created_at.isoformat()
            })
        
        return result
    finally:
        db.close()

if __name__ == "__main__":
    port = int(os.getenv("USER_SERVICE_PORT", 8002))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
