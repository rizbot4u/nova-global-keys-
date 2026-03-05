#!/usr/bin/env python3
"""
NOVA GLOBAL KEYS - Auth Service
Handles user authentication, JWT issuance, OAuth with Bybit
"""

import os
import sys
import uuid
import logging
from datetime import datetime
from typing import Optional

import uvicorn
import httpx
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add shared modules to path
sys.path.append("/root/nova-global-keys-/services")
from shared.models.database import SessionLocal, User
from shared.utils.security import hash_password, verify_password, create_access_token
from shared.redis.client import redis_client

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auth-service")

# FastAPI app
app = FastAPI(title="Nova Auth Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Pydantic models
class UserSignup(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class TelegramLink(BaseModel):
    telegram_id: str

# Configuration
CLIENT_ID = os.getenv("CLIENT_ID", "x9dmxAGkDDoa")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("REDIRECT_URI", "https://novatradingkeys.com/api/auth/callback/bybit")
AFFILIATE_ID = os.getenv("AFFILIATE_ID", "127146")

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health")
async def health():
    return {
        "service": "auth",
        "status": "healthy",
        "redis": redis_client.ping(),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/signup")
async def signup(user: UserSignup):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == user.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed = hash_password(user.password)
        new_user = User(name=user.name, email=user.email, hashed_password=hashed)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        token = create_access_token({"sub": new_user.email})
        logger.info(f"✅ New user: {new_user.email}")
        
        return {
            "token": token,
            "user": {
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email
            }
        }
    finally:
        db.close()

@app.post("/login")
async def login(user: UserLogin):
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        if not db_user or not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = create_access_token({"sub": db_user.email})
        logger.info(f"✅ Login: {db_user.email}")
        
        return {
            "token": token,
            "user": {
                "id": db_user.id,
                "name": db_user.name,
                "email": db_user.email
            }
        }
    finally:
        db.close()

@app.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    import jwt
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
                "name": user.name,
                "telegram_id": user.telegram_id
            }
        finally:
            db.close()
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/telegram/link")
async def link_telegram(
    link: TelegramLink,
    current_user: dict = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == current_user["user_id"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.telegram_id = link.telegram_id
        db.commit()
        
        # Store in Redis for quick lookup
        redis_client.link_telegram(link.telegram_id, str(current_user["user_id"]))
        
        return {"status": "success", "message": "Telegram linked"}
    finally:
        db.close()

@app.get("/telegram/{telegram_id}")
async def get_user_by_telegram(telegram_id: str):
    user_id = redis_client.get_user_by_telegram(telegram_id)
    if not user_id:
        raise HTTPException(status_code=404, detail="Telegram not linked")
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "user_id": user.id,
            "name": user.name,
            "email": user.email
        }
    finally:
        db.close()

@app.get("/bybit/login")
async def bybit_login():
    state = uuid.uuid4().hex[:8]
    url = f"https://www.bybit.com/en/oauth?client_id={CLIENT_ID}&response_type=code&scope=openapi&state={state}&redirect_uri={REDIRECT_URI}&affiliate_id={AFFILIATE_ID}"
    return RedirectResponse(url)

@app.get("/bybit/callback")
async def bybit_callback(code: str, state: str, telegram_id: Optional[str] = None):
    logger.info(f"OAuth callback: state={state}")
    
    timeout = httpx.Timeout(120.0, connect=60.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            # Exchange code for token
            token_resp = await client.post(
                "https://api2.bybit.com/oauth/v1/public/access_token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": REDIRECT_URI
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            token_data = token_resp.json()
            access_token = token_data.get('access_token')
            
            if not access_token:
                logger.error(f"Token exchange failed: {token_data}")
                return JSONResponse(status_code=400, content={"error": "Token exchange failed"})
            
            # Get API keys
            keys_resp = await client.get(
                "https://api2.bybit.com/oauth/v1/resource/restrict/openapi",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            keys_data = keys_resp.json()
            api_key = keys_data.get("result", {}).get("api_key")
            api_secret = keys_data.get("result", {}).get("api_secret")
            
            # Get UID
            uid_resp = await client.get(
                "https://api2.bybit.com/oauth/v1/resource/restrict/uid_bearer",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            uid = uid_resp.json().get("uid", "")
            
            # Store in Redis
            if telegram_id:
                user_id = redis_client.get_user_by_telegram(telegram_id)
                if user_id:
                    redis_client.store_user_keys(user_id, api_key, api_secret, uid)
                    return HTMLResponse("<html><body><h1>Success!</h1><p>Bybit account connected.</p></body></html>")
            
            # Web flow
            session_id = f"web_{uuid.uuid4().hex[:12]}"
            redis_client.store_user_keys(session_id, api_key, api_secret, uid)
            return RedirectResponse(url=f"https://www.novatradingkeys.com/dashboard/?session={session_id}")
            
        except httpx.ConnectTimeout:
            logger.error("Bybit Connection Timeout")
            return JSONResponse(status_code=504, content={"error": "Bybit Timeout"})
        except Exception as e:
            logger.error(f"Auth Error: {str(e)}")
            return JSONResponse(status_code=500, content={"error": "Internal Server Error"})

if __name__ == "__main__":
    port = int(os.getenv("AUTH_SERVICE_PORT", 8001))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)

@app.get("/callback/bybit")
async def callback_bybit(code: str, state: str):
    return await bybit_callback(code, state)
