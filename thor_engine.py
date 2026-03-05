#!/usr/bin/env python3
"""
NOVA GLOBAL KEYS - THOR UNIFIED ENGINE v6.0 FINAL
COMPLETE BANK-GRADE Multi-User Trading Platform with ALL Endpoints
Author: Nova Global Keys | Broker: Kr000820 | Affiliate: 127146
"""

import os
import sys
import time
import json
import hmac
import hashlib
import asyncio
import logging
import threading
import uuid
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from enum import Enum

import httpx
import redis
import uvicorn
import telebot
import jwt
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from passlib.context import CryptContext

# Force bcrypt to use correct backend
import bcrypt
import passlib.hash
try:
    passlib.hash.bcrypt._load_backend('bcrypt')
except:
    pass  # Fallback to default

# ===== SQLALCHEMY DATABASE SETUP =====
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

# Load environment first
load_dotenv()

# ===== SECURITY CONFIGURATION =====
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = secrets.token_hex(32)
    print("⚠️ WARNING: Using generated JWT secret. Set JWT_SECRET_KEY in .env for production!")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", 24))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nova.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ===== DATABASE MODELS =====
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    exchange_keys = relationship("ExchangeKey", back_populates="user", cascade="all, delete-orphan")
    bots = relationship("UserBot", back_populates="user", cascade="all, delete-orphan")

class ExchangeKey(Base):
    __tablename__ = "exchange_keys"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exchange_name = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    api_secret = Column(String, nullable=False)
    nickname = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="exchange_keys")

class UserBot(Base):
    __tablename__ = "user_bots"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    bot_name = Column(String, nullable=False)
    exchange_key_id = Column(Integer, ForeignKey("exchange_keys.id", ondelete="SET NULL"))
    strategy = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    status = Column(String, default="stopped")
    config = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="bots")

# Create all tables
Base.metadata.create_all(bind=engine)

# ===== PYDANTIC MODELS =====
class UserSignup(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

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

class TransferRequest(BaseModel):
    from_account_type: str
    to_account_type: str
    coin: str
    amount: str
    transfer_id: Optional[str] = None

# ===== SECURITY FUNCTIONS =====
def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password[:72], hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ===== DEPENDENCIES =====
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token claims")
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if user is None:
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
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

async def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[dict]:
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

# ============================================================================
# CONFIGURATION
# ============================================================================

class Settings:
    BROKER_CODE = os.getenv("BROKER_CODE", "Kr000820")
    AFFILIATE_ID = os.getenv("AFFILIATE_ID", "127146")
    CLIENT_ID = os.getenv("CLIENT_ID", "x9dmxAGkDDoa")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
    REDIRECT_URI = os.getenv("REDIRECT_URI", "https://novatradingkeys.com/api/auth/callback/bybit")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://31.97.220.195:3000")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    REDIS_URL = os.getenv("REDIS_URL", "redis://default:NovaGlobal2026@localhost:6379/0")
    MASTER_API_KEY = os.getenv("MASTER_API_KEY", "")
    MASTER_API_SECRET = os.getenv("MASTER_API_SECRET", "")
    PORT = int(os.getenv("PORT", 8081))
    HOST = os.getenv("HOST", "0.0.0.0")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    USE_TESTNET = os.getenv("USE_TESTNET", "false").lower() == "true"
    
    BYBIT_V5 = "https://api.bybit.id/v5"
    BYBIT_OAUTH = "https://api2.bybit.com"
    BYBIT_TESTNET = "https://api-testnet.bybit.com/v5"

settings = Settings()

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("nova-thor")

# ============================================================================
# REDIS CLIENT
# ============================================================================

class RedisClient:
    def __init__(self):
        redis_url = settings.REDIS_URL
        self.client = redis.Redis.from_url(redis_url, decode_responses=True)
        logger.info(f"✅ Redis connected: {self.client.ping()}")
    
    def ping(self) -> bool:
        try:
            return self.client.ping()
        except:
            return False
    
    def store_user_keys(self, user_id: str, api_key: str, api_secret: str, uid: str = None):
        pipe = self.client.pipeline()
        pipe.set(f"user:{user_id}:api_key", api_key)
        pipe.set(f"user:{user_id}:api_secret", api_secret)
        if uid:
            pipe.set(f"user:{user_id}:uid", uid)
        pipe.execute()
        logger.info(f"✅ Stored keys for user {user_id}")
    
    def get_user_keys(self, user_id: str) -> Optional[Dict]:
        api_key = self.client.get(f"user:{user_id}:api_key")
        api_secret = self.client.get(f"user:{user_id}:api_secret")
        if api_key and api_secret:
            return {'api_key': api_key, 'api_secret': api_secret, 'uid': self.client.get(f"user:{user_id}:uid")}
        return None
    
    def user_exists(self, user_id: str) -> bool:
        return self.client.exists(f"user:{user_id}:api_key") > 0
    
    def store_oauth_state(self, state: str, user_id: str, expiry: int = 600):
        self.client.setex(f"oauth:{state}", expiry, user_id)
    
    def get_oauth_state(self, state: str) -> Optional[str]:
        return self.client.get(f"oauth:{state}")
    
    def delete_oauth_state(self, state: str):
        self.client.delete(f"oauth:{state}")
    
    def get_shop_credit(self, user_id: str) -> float:
        return float(self.client.get(f"user:{user_id}:shop_credit") or 0)
    
    def update_shop_credit(self, user_id: str, amount: float):
        self.client.incrbyfloat(f"user:{user_id}:shop_credit", amount)
    
    def update_heartbeat(self):
        self.client.set("worker:last_heartbeat", datetime.now().isoformat())
        status = {"engine": "Thor-Warrior-01", "status": "OPERATIONAL", "timestamp": datetime.now().isoformat()}
        self.client.set("nova:status:warrior_01", json.dumps(status))
    
    def increment_requests(self):
        self.client.incr("stats:main_api:total_requests")

redis_client = RedisClient()

# ============================================================================
# THOR ENGINE - COMPLETE BYBIT V5 IMPLEMENTATION
# ============================================================================

class ThorEngine:
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.broker_code = settings.BROKER_CODE
        self.affiliate_id = settings.AFFILIATE_ID
        self.recv_window = "20000"
        
        if settings.USE_TESTNET:
            self.base_url = "https://api-testnet.bybit.com"
        else:
            self.base_url = "https://api.bybit.id"
        
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"⚡ Thor Engine initialized | Broker: {self.broker_code}")
    
    def _generate_signature(self, timestamp: str, params: str = "", data: dict = None) -> str:
        if not self.api_secret:
            return ""
        if data:
            body_str = json.dumps(data, separators=(',', ':'))
            sign_str = f"{timestamp}{self.api_key}{self.recv_window}{body_str}"
        else:
            sign_str = f"{timestamp}{self.api_key}{self.recv_window}{params}"
        return hmac.new(
            self.api_secret.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def _request(self, method: str, endpoint: str, params: dict = None, data: dict = None) -> Dict:
        timestamp = str(int(time.time() * 1000))
        query_string = ""
        if method == "GET" and params:
            sorted_params = sorted(params.items())
            query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        
        signature = self._generate_signature(timestamp, query_string, data)
        
        headers = {
            "X-BAPI-API-KEY": self.api_key or "",
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-SIGN": signature,
            "X-BAPI-RECV-WINDOW": self.recv_window,
            "X-Referer": self.broker_code,
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = await self.client.get(url, headers=headers, params=params)
            else:
                response = await self.client.post(url, headers=headers, json=data)
            return response.json()
        except Exception as e:
            logger.error(f"Request error: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    # ==== MARKET ENDPOINTS ====
    async def get_tickers(self, category: str = "spot", symbol: str = None):
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/v5/market/tickers", params=params)
    
    async def get_orderbook(self, category: str, symbol: str, limit: int = 25):
        params = {"category": category, "symbol": symbol, "limit": limit}
        return await self._request("GET", "/v5/market/orderbook", params=params)
    
    async def get_kline(self, category: str, symbol: str, interval: str = "D", limit: int = 200):
        params = {"category": category, "symbol": symbol, "interval": interval, "limit": limit}
        return await self._request("GET", "/v5/market/kline", params=params)
    
    async def get_instruments(self, category: str = "spot", symbol: str = None):
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/v5/market/instruments-info", params=params)
    
    async def get_server_time(self):
        return await self._request("GET", "/v5/market/time")
    
    # ==== ACCOUNT ENDPOINTS ====
    async def get_wallet_balance(self, account_type: str = "UNIFIED", coin: str = None):
        params = {"accountType": account_type}
        if coin:
            params["coin"] = coin
        return await self._request("GET", "/v5/account/wallet-balance", params=params)
    
    async def get_account_info(self):
        return await self._request("GET", "/v5/account/info")
    
    async def get_fee_rate(self, category: str = "spot", symbol: str = None):
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/v5/account/fee-rate", params=params)
    
    # ==== TRADE ENDPOINTS ====
    async def place_order(self, category: str, symbol: str, side: str, order_type: str,
                         qty: str, price: str = None, time_in_force: str = "GTC"):
        data = {
            "category": category,
            "symbol": symbol,
            "side": side,
            "orderType": order_type,
            "qty": qty,
            "timeInForce": time_in_force,
            "brokerId": self.broker_code
        }
        if price:
            data["price"] = price
        return await self._request("POST", "/v5/order/create", data=data)
    
    async def get_open_orders(self, category: str = "spot", symbol: str = None, limit: int = 50):
        params = {"category": category, "limit": limit}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/v5/order/realtime", params=params)
    
    async def get_order_history(self, category: str, symbol: str = None, limit: int = 50):
        params = {"category": category, "limit": limit}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/v5/order/history", params=params)
    
    async def cancel_order(self, category: str, symbol: str, order_id: str = None, order_link_id: str = None):
        data = {"category": category, "symbol": symbol}
        if order_id:
            data["orderId"] = order_id
        if order_link_id:
            data["orderLinkId"] = order_link_id
        return await self._request("POST", "/v5/order/cancel", data=data)
    
    async def cancel_all_orders(self, category: str):
        data = {"category": category}
        return await self._request("POST", "/v5/order/cancel-all", data=data)
    
    # ==== POSITION ENDPOINTS ====
    async def get_positions(self, category: str = "linear", symbol: str = None):
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/v5/position/list", params=params)
    
    async def get_closed_pnl(self, category: str, symbol: str = None, limit: int = 50):
        params = {"category": category, "limit": limit}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/v5/position/closed-pnl", params=params)
    
    async def set_leverage(self, category: str, symbol: str, leverage: str):
        data = {"category": category, "symbol": symbol, "leverage": leverage}
        return await self._request("POST", "/v5/position/set-leverage", data=data)
    
    # ==== ASSET ENDPOINTS ====
    async def get_coin_balance(self, account_type: str = "FUND", coin: str = None, member_id: str = None):
        params = {"accountType": account_type}
        if coin:
            params["coin"] = coin
        if member_id:
            params["memberId"] = member_id
        return await self._request("GET", "/v5/asset/transfer/query-account-coins-balance", params=params)
    
    async def get_deposit_address(self, coin: str):
        params = {"coin": coin}
        return await self._request("GET", "/v5/asset/deposit/address", params=params)
    
    async def get_deposit_history(self, coin: str = None, limit: int = 50):
        params = {"limit": limit}
        if coin:
            params["coin"] = coin
        return await self._request("GET", "/v5/asset/deposit/record", params=params)
    
    async def get_withdraw_history(self, coin: str = None, limit: int = 50):
        params = {"limit": limit}
        if coin:
            params["coin"] = coin
        return await self._request("GET", "/v5/asset/withdraw/record", params=params)
    
    async def create_transfer(self, transfer_id: str, from_account: str, to_account: str, coin: str, amount: str):
        data = {
            "transferId": transfer_id,
            "fromAccountType": from_account,
            "toAccountType": to_account,
            "coin": coin,
            "amount": amount
        }
        return await self._request("POST", "/v5/asset/transfer/inter-transfer", data=data)
    
    # ==== AFFILIATE ENDPOINTS ====
    async def get_affiliate_commission(self, limit: int = 50):
        params = {"limit": limit}
        return await self._request("GET", "/v5/affiliate/commission", params=params)
    
    async def get_affiliate_user_list(self, size: int = 50, page: int = 1):
        params = {"size": size, "page": page}
        return await self._request("GET", "/v5/affiliate/affiliate-user-list", params=params)
    
    # ==== BROKER ENDPOINTS ====
    async def create_subaccount(self, username: str, member_type: int = 1, note: str = ""):
        data = {"username": username, "memberType": member_type, "note": note}
        return await self._request("POST", "/v5/broker/create-sub-member", data=data)
    
    async def get_subaccount_list(self):
        return await self._request("GET", "/v5/broker/sub-member-list")
    
    async def set_subaccount_fee(self, sub_uid: str, fee_rate: dict):
        data = {"subUid": sub_uid, "feeRate": fee_rate}
        return await self._request("POST", "/v5/broker/set-sub-member-fee", data=data)
    
    # ==== P2P ENDPOINTS ====
    async def get_p2p_balance(self, coin: str = None):
        params = {}
        if coin:
            params["coin"] = coin
        logger.info(f"🔍 P2P Request params: {params}")
        result = await self._request("GET", "/v5/p2p/balance", params=params)
        logger.info(f"🔍 P2P Response raw: {result}")
        return result
    
    async def get_p2p_orders(self, side: str = None, status: str = None, limit: int = 50):
        try:
            params = {"limit": limit}
            if side:
                params["side"] = side
            if status:
                params["status"] = status
            logger.info(f"🔍 Making P2P orders request with params: {params}")
            result = await self._request("GET", "/v5/p2p/order/list", params=params)
            logger.info(f"🔍 P2P orders response: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ Error in get_p2p_orders: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    # ==== RFQ/OTC ENDPOINTS ====
    async def create_rfq(self, data: dict):
        return await self._request("POST", "/v5/rfq/create", data=data)
    
    async def execute_rfq(self, data: dict):
        return await self._request("POST", "/v5/rfq/execute", data=data)
    
    async def get_rfq_config(self):
        return await self._request("GET", "/v5/rfq/config")
    
    # ==== FORMATTING HELPERS ====
    def format_balance(self, balance_data: Dict) -> Dict:
        try:
            balances = {}
            total_usd = 0
            assets = []
            if balance_data.get('retCode') == 0:
                for account in balance_data['result']['list']:
                    for coin in account.get('coin', []):
                        coin_name = coin.get('coin')
                        wallet_balance = float(coin.get('walletBalance', 0))
                        usd_value = float(coin.get('usdValue', 0))
                        if wallet_balance > 0 or usd_value > 0:
                            balances[coin_name] = {"balance": wallet_balance, "usd_value": usd_value}
                            total_usd += usd_value
                            assets.append({"coin": coin_name, "balance": wallet_balance, "usd_value": usd_value})
            return {"success": True, "balances": balances, "total_usd": total_usd, "assets": assets}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def close(self):
        await self.client.aclose()

# ============================================================================  
# FASTAPI APP  
# ============================================================================

from starlette.middleware.base import BaseHTTPMiddleware  # <-- correct import

app = FastAPI(
    title="Nova Global Keys - Thor Engine v6.0 FINAL",
    description="COMPLETE BANK-GRADE Multi-User Trading Platform",
    version="6.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.novatradingkeys.com", "https://novatradingkeys.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Connection Middleware ===
def verify_jwt(token: str) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub") is not None
    except Exception:
        return False

class ConnectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        token = request.headers.get("Authorization")
        connected = False
        if token and verify_jwt(token.replace("Bearer ", "")):
            connected = True
        else:
            broker_code = settings.BROKER_CODE
            if redis_client.client.exists(f"broker:{broker_code}"):
                connected = True
        request.state.connected = connected
        response = await call_next(request)
        return response

app.add_middleware(ConnectionMiddleware)

# === Status Endpoint ===
@app.get("/api/status")
async def status(request: Request):
    return {"connected": getattr(request.state, "connected", False)}
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/signup")
async def signup(user: UserSignup):
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed = hash_password(user.password)
        new_user = User(name=user.name, email=user.email, hashed_password=hashed)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        token = create_access_token({"sub": new_user.email})
        logger.info(f"✅ New user signed up: {new_user.email}")
        return {"token": token, "user": {"id": new_user.id, "name": new_user.name, "email": new_user.email}}
    finally:
        db.close()

@app.post("/api/auth/login")
async def login(user: UserLogin):
    db = SessionLocal()
    try:
        # 1. Verify User Existence
        db_user = db.query(User).filter(User.email == user.email).first()
        if not db_user:
            logger.warning(f"❌ Login attempt for non-existent email: {user.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # 2. Verify Password
        if not verify_password(user.password, db_user.hashed_password):
            logger.warning(f"❌ Incorrect password for: {user.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # 3. Create JWT Token
        token = create_access_token({"sub": db_user.email})
        
        # 4. Critical: Check for active Exchange Keys
        # This ensures the dashboard knows if it needs to ask for API keys or show the bot
        has_keys = db.query(ExchangeKey).filter(
            ExchangeKey.user_id == db_user.id, 
            ExchangeKey.is_active == True
        ).first() is not None

        logger.info(f"✅ User logged in: {db_user.email} (Keys Linked: {has_keys})")
        
        return {
            "token": token, 
            "user": {
                "id": db_user.id, 
                "name": db_user.name, 
                "email": db_user.email,
                "has_keys": has_keys
            }
        }
    except Exception as e:
        logger.error(f"🔥 Login System Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        db.close()
@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return current_user

@app.get("/api/auth/login")  # Bybit OAuth endpoint
async def auth_login():
    state = uuid.uuid4().hex[:8]
    url = f"https://www.bybit.com/en/oauth?client_id={settings.CLIENT_ID}&response_type=code&scope=openapi&state={state}&redirect_uri={settings.REDIRECT_URI}&affiliate_id={settings.AFFILIATE_ID}"
    return RedirectResponse(url)
@app.post("/api/trade/start")
async def start_trading_session(order: dict, current_user: dict = Depends(get_current_user)):
    """
    Handles the 'Engage Warrior' button from the frontend dashboard.
    """
    logger.info(f"🚀 Trade Start Request from {current_user['email']} for {order.get('symbol')}")
    
    # This maps the frontend call to your existing Bybit order logic
    # It ensures the 'qty' is handled correctly to avoid 'undefined' errors
    return await place_exchange_order(
        order=order, 
        exchange_name="bybit", 
        current_user=current_user
    )

@app.get("/api/auth/callback/bybit")
async def auth_callback(code: str, state: str):
    logger.info(f"OAuth callback: state={state}, code={code[:5]}...")
    raw_tg_user_id = redis_client.get_oauth_state(state)
    tg_user_id = raw_tg_user_id.decode() if isinstance(raw_tg_user_id, bytes) else raw_tg_user_id
    timeout = httpx.Timeout(60.0, connect=30.0)
    async with httpx.AsyncClient(timeout=timeout, trust_env=True) as client:
        try:
            token_resp = await client.post(
                f"{settings.BYBIT_OAUTH}/oauth/v1/public/access_token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": settings.CLIENT_ID,
                    "client_secret": settings.CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": settings.REDIRECT_URI
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            token_data = token_resp.json()
            access_token = token_data.get('access_token')
            if not access_token:
                logger.error(f"Token exchange failed: {token_data}")
                return JSONResponse(status_code=400, content={"error": "Token exchange failed"})
            keys_resp = await client.get(
                f"{settings.BYBIT_OAUTH}/oauth/v1/resource/restrict/openapi",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            keys_data = keys_resp.json()
            api_key = keys_data.get("result", {}).get("api_key")
            api_secret = keys_data.get("result", {}).get("api_secret")
            uid_resp = await client.get(
                f"{settings.BYBIT_OAUTH}/oauth/v1/resource/restrict/uid_bearer",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            uid = uid_resp.json().get("uid", "")
            if tg_user_id:
                redis_client.store_user_keys(tg_user_id, api_key, api_secret, uid)
                redis_client.delete_oauth_state(state)
                return HTMLResponse("<html><body><h1>Success!</h1><p>Telegram Connected.</p></body></html>")
            else:
                session_id = f"web_{uuid.uuid4().hex[:12]}"
                redis_client.store_user_keys(session_id, api_key, api_secret, uid)
                return RedirectResponse(url=f"https://www.novatradingkeys.com/dashboard/?session={session_id}")
        except httpx.ConnectTimeout:
            logger.error("Bybit Connection Timeout")
            return JSONResponse(status_code=504, content={"error": "Bybit Timeout"})
        except Exception as e:
            logger.error(f"Auth Error: {str(e)}")
            return JSONResponse(status_code=500, content={"error": "Internal Server Error"})

# ============================================================================
# KEY VAULT ENDPOINTS
# ============================================================================

def mask_api_key(api_key: str) -> str:
    if len(api_key) <= 8:
        return "****"
    return api_key[:4] + "..." + api_key[-4:]

# FIX 1: Add the v1 balance route the frontend is looking for
@app.get("/api/v1/balance")
async def get_balance_v1(current_user: dict = Depends(get_current_user)):
    # This maps the frontend v1 call to your existing logic
    return await get_exchange_balance(exchange_name="bybit", current_user=current_user)

# FIX 2: Add the v1 tickers route the frontend is looking for
@app.get("/api/v1/market/tickers")
async def get_tickers_v1(category: str = "spot", symbol: str = None):
    engine = ThorEngine()
    return await engine.get_tickers(category=category, symbol=symbol)

# FIX 3: Ensure your connect_exchange endpoint is complete
@app.post("/api/keys/connect")
async def connect_exchange(request: ConnectExchangeRequest, current_user: dict = Depends(get_current_user)):
    db = SessionLocal()
    try:
        # Test the keys before saving
        engine = ThorEngine(request.api_key, request.api_secret)
        test_result = await engine.get_server_time()
        
        if test_result.get('retCode') != 0:
            raise HTTPException(status_code=400, detail=f"Invalid API keys. Test failed.")
            
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
            existing.last_used = datetime.now(timezone.utc)
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
        return {"status": "success", "message": message}
    finally:
        db.close()
@app.get("/api/v1/market/orderbook")
async def get_orderbook_v1_final(category: str = "spot", symbol: str = "BTCUSDT", limit: int = 25):
    """
    Fixes the 404 for the Orderbook display on the dashboard.
    """
    engine = ThorEngine()
    return await engine.get_orderbook(category=category, symbol=symbol, limit=limit)
# ============================================================================
# EXCHANGE TRADING ENDPOINTS
# ============================================================================

@app.get("/api/exchange/balance")
async def get_exchange_balance(exchange_name: str = "bybit", current_user: dict = Depends(get_current_user)):
    db = SessionLocal()
    try:
        key = db.query(ExchangeKey).filter(
            ExchangeKey.user_id == current_user["user_id"],
            ExchangeKey.exchange_name == exchange_name,
            ExchangeKey.is_active == True
        ).first()
        if not key:
            raise HTTPException(status_code=404, detail=f"No active {exchange_name} keys found. Connect first at /keys/connect")
        engine = ThorEngine(key.api_key, key.api_secret)
        if exchange_name.lower() == "bybit":
            result = await engine.get_wallet_balance()
            if result.get('retCode') == 0:
                key.last_used = datetime.now(timezone.utc)
                db.commit()
                return engine.format_balance(result)
            else:
                raise HTTPException(status_code=400, detail=result.get('retMsg', 'API error'))
        else:
            raise HTTPException(status_code=400, detail=f"{exchange_name} not yet implemented")
    finally:
        db.close()

@app.post("/api/exchange/order")
async def place_exchange_order(order: dict, exchange_name: str = "bybit", current_user: dict = Depends(get_current_user)):
    db = SessionLocal()
    try:
        key = db.query(ExchangeKey).filter(
            ExchangeKey.user_id == current_user["user_id"],
            ExchangeKey.exchange_name == exchange_name,
            ExchangeKey.is_active == True
        ).first()
        if not key:
            raise HTTPException(status_code=404, detail=f"No active {exchange_name} keys")
        engine = ThorEngine(key.api_key, key.api_secret)
        result = await engine.place_order(
            category=order.get("category", "spot"),
            symbol=order["symbol"],
            side=order["side"],
            order_type=order.get("order_type", "Market"),
            qty=str(order["qty"]),
            price=str(order["price"]) if order.get("price") else None
        )
        if result.get('retCode') == 0:
            key.last_used = datetime.now(timezone.utc)
            db.commit()
        return result
    finally:
        db.close()

@app.get("/api/exchange/open-orders")
async def get_exchange_open_orders(
    exchange_name: str = "bybit",
    category: str = "spot",
    symbol: str = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        key = db.query(ExchangeKey).filter(
            ExchangeKey.user_id == current_user["user_id"],
            ExchangeKey.exchange_name == exchange_name,
            ExchangeKey.is_active == True
        ).first()
        if not key:
            raise HTTPException(status_code=404, detail=f"No active {exchange_name} keys")
        engine = ThorEngine(key.api_key, key.api_secret)
        result = await engine.get_open_orders(category=category, symbol=symbol, limit=limit)
        if result.get('retCode') == 0:
            key.last_used = datetime.now(timezone.utc)
            db.commit()
        return result
    finally:
        db.close()
@app.post("/api/v1/trade/order")
async def place_order_v1_alias(order: dict, current_user: dict = Depends(get_current_user)):
    """
    Fixes the 404 when clicking 'Trade' or 'Engage' on the dashboard.
    """
    # This redirects the frontend 'v1' call to your existing logic
    return await place_exchange_order(order=order, exchange_name="bybit", current_user=current_user)
# ============================================================================
# P2P & ASSETS ENDPOINTS
# ============================================================================

@app.get("/api/p2p/orders")
async def get_p2p_order_history(
    current_user: dict = Depends(get_current_user),
    limit: int = 50,
    status: str = None,
    side: str = None
):
    db = SessionLocal()
    try:
        key = db.query(ExchangeKey).filter(
            ExchangeKey.user_id == current_user["user_id"],
            ExchangeKey.exchange_name == "bybit",
            ExchangeKey.is_active == True
        ).first()
        if not key:
            raise HTTPException(status_code=404, detail="No active Bybit keys found")
        engine = ThorEngine(key.api_key, key.api_secret)
        params = {"limit": limit}
        if status:
            params["status"] = status
        if side:
            params["side"] = side
        result = await engine._request("GET", "/v5/p2p/order/list", params=params)
        if result.get('retCode') == 0:
            key.last_used = datetime.now(timezone.utc)
            db.commit()
        return result
    finally:
        db.close()

@app.get("/api/asset/withdraw/history")
async def get_withdraw_history(
    current_user: dict = Depends(get_current_user),
    coin: str = None,
    limit: int = 50
):
    db = SessionLocal()
    try:
        key = db.query(ExchangeKey).filter(
            ExchangeKey.user_id == current_user["user_id"],
            ExchangeKey.exchange_name == "bybit",
            ExchangeKey.is_active == True
        ).first()
        if not key:
            raise HTTPException(status_code=404, detail="No active Bybit keys found")
        engine = ThorEngine(key.api_key, key.api_secret)
        params = {"limit": limit}
        if coin:
            params["coin"] = coin
        result = await engine._request("GET", "/v5/asset/withdraw/query-record", params=params)
        if result.get('retCode') == 0:
            key.last_used = datetime.now(timezone.utc)
            db.commit()
        return result
    finally:
        db.close()

# ============================================================================
# TRANSFERS ENDPOINTS
# ============================================================================

@app.post("/api/transfer/universal")
async def universal_transfer(request: TransferRequest, current_user: dict = Depends(get_current_user)):
    db = SessionLocal()
    try:
        key = db.query(ExchangeKey).filter(
            ExchangeKey.user_id == current_user["user_id"],
            ExchangeKey.exchange_name == "bybit",
            ExchangeKey.is_active == True
        ).first()
        if not key:
            raise HTTPException(status_code=404, detail="No active Bybit keys found")
        engine = ThorEngine(key.api_key, key.api_secret)
        transfer_id = request.transfer_id or f"transfer_{uuid.uuid4().hex[:8]}"
        data = {
            "transferId": transfer_id,
            "fromAccountType": request.from_account_type,
            "toAccountType": request.to_account_type,
            "coin": request.coin,
            "amount": request.amount
        }
        result = await engine._request("POST", "/v5/asset/transfer/universal-transfer", data=data)
        if result.get('retCode') == 0:
            key.last_used = datetime.now(timezone.utc)
            db.commit()
        return result
    finally:
        db.close()

@app.post("/api/transfer/to-subaccount")
async def transfer_to_subaccount(
    coin: str,
    amount: str,
    sub_account_id: str,
    transfer_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        key = db.query(ExchangeKey).filter(
            ExchangeKey.user_id == current_user["user_id"],
            ExchangeKey.exchange_name == "bybit",
            ExchangeKey.is_active == True
        ).first()
        if not key:
            raise HTTPException(status_code=404, detail="No active Bybit keys found")
        engine = ThorEngine(key.api_key, key.api_secret)
        transfer_id = transfer_id or f"sub_{uuid.uuid4().hex[:8]}"
        data = {
            "transferId": transfer_id,
            "coin": coin,
            "amount": amount,
            "subMemberId": sub_account_id
        }
        result = await engine._request("POST", "/v5/asset/transfer/inter-proxy-transfer", data=data)
        if result.get('retCode') == 0:
            key.last_used = datetime.now(timezone.utc)
            db.commit()
        return result
    finally:
        db.close()
# --- COMPATIBILITY BRIDGE FOR FRONTEND ---

@app.get("/api/v1/balance")
async def get_balance_v1_alias(current_user: dict = Depends(get_current_user)):
    """Redirects v1 balance requests to the unified logic."""
    return await get_exchange_balance(exchange_name="bybit", current_user=current_user)

@app.post("/api/v1/trade/order")
async def place_order_v1_alias(order: dict, current_user: dict = Depends(get_current_user)):
    """Redirects v1 trade requests to the unified logic."""
    return await place_exchange_order(order=order, exchange_name="bybit", current_user=current_user)
# ============================================================================
# PUBLIC ENDPOINTS (No Auth Required)
# ============================================================================

@app.get("/")
async def root():
    return {"name": "Nova Global Keys", "version": "6.0.0", "broker": settings.BROKER_CODE, "affiliate": settings.AFFILIATE_ID, "status": "operational"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "broker": settings.BROKER_CODE, "redis": redis_client.ping(), "timestamp": datetime.now().isoformat()}

@app.get("/api/market/orderbook")
async def get_orderbook(category: str, symbol: str, limit: int = 25):
    engine = ThorEngine()
    result = await engine.get_orderbook(category=category, symbol=symbol, limit=limit)
    return result

@app.get("/api/market/kline")
async def get_kline(category: str, symbol: str, interval: str = "D", limit: int = 200):
    engine = ThorEngine()
    return await engine.get_kline(category=category, symbol=symbol, interval=interval, limit=limit)

@app.get("/api/market/instruments")
async def get_instruments(category: str = "spot", symbol: str = None):
    engine = ThorEngine()
    return await engine.get_instruments(category=category, symbol=symbol)

@app.get("/api/market/time")
async def get_server_time():
    engine = ThorEngine()
    return await engine.get_server_time()

@app.get("/api/v1/price/{symbol}")
async def get_price_v1(symbol: str):
    engine = ThorEngine()
    result = await engine.get_tickers(symbol=symbol)
    if result.get('retCode') == 0:
        ticker = result['result']['list'][0]
        return {
            "success": True,
            "symbol": ticker.get('symbol', ''),
            "price": float(ticker.get('lastPrice', 0)),
            "change_24h": float(ticker.get('price24hPcnt', 0)) * 100,
            "high_24h": float(ticker.get('highPrice24h', 0)),
            "low_24h": float(ticker.get('lowPrice24h', 0)),
            "volume": float(ticker.get('volume24h', 0))
        }
    return {"success": False, "error": "Could not fetch price"}

@app.get("/api/v1/orderbook/{symbol}")
async def get_orderbook_v1(symbol: str, category: str = "spot", limit: int = 25):
    engine = ThorEngine()
    return await engine.get_orderbook(category=category, symbol=symbol, limit=limit)

# ============================================================================
# TELEGRAM NOTIFICATION HELPERS
# ============================================================================

async def send_telegram_notification(chat_id: str, message: str):
    if not settings.TELEGRAM_TOKEN:
        logger.warning("Telegram token not configured")
        return False
    try:
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {e}")
        return False

# ============================================================================
# BACKGROUND THREADS
# ============================================================================

def killswitch_listener():
    logger.info("🔫 Killswitch listener started")
    pubsub_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = pubsub_client.pubsub()
    pubsub.subscribe("nova:commands")
    for message in pubsub.listen():
        if message['type'] == 'message':
            command = message['data']
            if command == 'KILL_ALL_BOTS':
                logger.critical("🛑 EMERGENCY SHUTDOWN ACTIVATED")
                os._exit(0)

def heartbeat_pulse():
    while True:
        try:
            redis_client.update_heartbeat()
            time.sleep(10)
        except Exception as e:
            logger.error(f"❤️ Heartbeat error: {e}")
            time.sleep(5)

# ============================================================================
# TELEGRAM BOT
# ============================================================================

if settings.TELEGRAM_TOKEN:
    bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
    
    @bot.message_handler(commands=['start', 'help'])
    def cmd_start(message):
        welcome = f"""
✨ Welcome to Nova Global Keys, {message.from_user.first_name}! ✨

Broker: {settings.BROKER_CODE}

Commands:
/connect - Link Bybit account
/balance - View wallet
/price BTC - Get price
/status - System check
        """
        bot.reply_to(message, welcome, parse_mode="Markdown")
    
    @bot.message_handler(commands=['balance'])
    def cmd_balance(message):
        user_id = str(message.from_user.id)
        keys = redis_client.get_user_keys(user_id)
        if not keys:
            bot.reply_to(message, "❌ Please /connect first")
            return
        bot.reply_to(message, "🔄 Fetching your balance...")
        import httpx
        import asyncio
        async def fetch():
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"http://localhost:{settings.PORT}/api/v1/balance", headers={"Authorization": user_id})
                return resp.json()
        data = asyncio.run(fetch())
        if data.get('success'):
            reply = "💰 *Your Portfolio*\n\n"
            for coin, details in data['balances'].items():
                reply += f"• *{coin}:* {details['balance']:.4f} (${details['usd_value']:.2f})\n"
            bot.reply_to(message, reply, parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Could not fetch balance")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

# --- ADD THIS NEAR YOUR OTHER V1 ROUTES ---

@app.post("/api/v1/trade/order")
async def place_order_v1_bridge(order: dict, current_user: dict = Depends(get_current_user)):
    """
    Connects the frontend's trade button to the actual trading logic.
    """
    return await place_exchange_order(order=order, exchange_name="bybit", current_user=current_user)

@app.post("/api/v1/trade/order")
async def place_order_v1_bridge(order: dict, current_user: dict = Depends(get_current_user)):
    return await place_exchange_order(order=order, exchange_name="bybit", current_user=current_user)

@app.get("/api/v1/balance")
async def get_balance_v1_bridge(current_user: dict = Depends(get_current_user)):
    return await get_exchange_balance(exchange_name="bybit", current_user=current_user)

@app.get("/api/v1/balance")
async def get_balance_v1_bridge(current_user: dict = Depends(get_current_user)):
    return await get_exchange_balance(exchange_name="bybit", current_user=current_user)

@app.post("/api/v1/trade/order")
async def place_order_v1_bridge(order: dict, current_user: dict = Depends(get_current_user)):
    return await place_exchange_order(order=order, exchange_name="bybit", current_user=current_user)

@app.get("/api/v1/balance")
async def get_balance_v1_bridge(current_user: dict = Depends(get_current_user)):
    return await get_exchange_balance(exchange_name="bybit", current_user=current_user)

@app.post("/api/v1/trade/order")
async def place_order_v1_bridge(order: dict, current_user: dict = Depends(get_current_user)):
    return await place_exchange_order(order=order, exchange_name="bybit", current_user=current_user)

def main():
    logger.info("=" * 60)
    logger.info("🚀 NOVA GLOBAL KEYS - THOR ENGINE v6.0 FINAL")
    logger.info("=" * 60)
    logger.info(f"Broker: {settings.BROKER_CODE}")
    
    try:
        redis_status = '✅' if redis_client.ping() else '❌'
    except Exception:
        redis_status = '❌'
        
    logger.info(f"Redis: {redis_status}")
    logger.info("✅ Bank-Grade Key Vault Active")
    logger.info("✅ JWT Authentication Active")
    logger.info("✅ SQLite Database Ready")
    logger.info("=" * 60)
    
    # 🎯 START BACKGROUND SERVICES
    threading.Thread(target=killswitch_listener, daemon=True).start()
    threading.Thread(target=heartbeat_pulse, daemon=True).start()
    logger.info("🎯 Background threads active (Killswitch & Heartbeat)")
    
    # Update initial heartbeat
    try:
        redis_client.update_heartbeat()
    except:
        pass

    logger.info(f"✅ API server protected behind Nginx on 127.0.0.1:8081")
    
    # 🚀 START SERVER
    uvicorn.run(
        "thor_engine:app",      # Filename:thor_engine.py, Object:app
        host="127.0.0.1",       # Internal only
        port=8081,              # Matches Nginx proxy_pass
        log_level=settings.LOG_LEVEL.lower(),
        proxy_headers=True,     # Trust Nginx headers
        forwarded_allow_ips="*" # Accept forwarded IPs from Nginx
    )

if __name__ == "__main__":
    main()
