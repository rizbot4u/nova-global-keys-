#!/usr/bin/env python3
"""
NOVA GLOBAL KEYS - THOR UNIFIED ENGINE v3.0 FINAL
Complete Broker Level 3 Trading System with Strategies, Payments & P2P
Author: Nova Global Keys | Broker: Kr000820
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
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from enum import Enum

import httpx
import redis
import uvicorn
import telebot
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# ============================================================================
# CONFIGURATION
# ============================================================================

load_dotenv()

class Settings:
    """Application settings from environment"""
    BROKER_CODE = os.getenv("BROKER_CODE", "Kr000820")
    AFFILIATE_ID = os.getenv("AFFILIATE_ID", "127146")
    CLIENT_ID = os.getenv("CLIENT_ID", "x9dmxAGkDDoa")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
    REDIRECT_URI = os.getenv("REDIRECT_URI", "https://novatradingkeys.com/api/auth/callback/bybit")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://31.97.220.195:3000")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    MASTER_API_KEY = os.getenv("MASTER_API_KEY", "")
    MASTER_API_SECRET = os.getenv("MASTER_API_SECRET", "")
    PORT = int(os.getenv("PORT", 8080))
    HOST = os.getenv("HOST", "0.0.0.0")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    USE_TESTNET = os.getenv("USE_TESTNET", "false").lower() == "true"
    
    # API Endpoints
    BYBIT_V5 = "https://api.bybit.id/v5"
    BYBIT_OAUTH = "https://api2.bybit.com"
    BYBIT_TESTNET = "https://api-testnet.bybit.com/v5"

settings = Settings()

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("nova-thor")

# ============================================================================
# REDIS CLIENT
# ============================================================================

class RedisClient:
    """Redis client for user data storage"""
    
    def __init__(self):
        self.client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
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
            return {
                'api_key': api_key,
                'api_secret': api_secret,
                'uid': self.client.get(f"user:{user_id}:uid")
            }
        return None
    
    def user_exists(self, user_id: str) -> bool:
        return self.client.exists(f"user:{user_id}:api_key") > 0
    
    def store_oauth_state(self, state: str, user_id: str, expiry: int = 600):
        self.client.setex(f"oauth:{state}", expiry, user_id)
    
    def get_oauth_state(self, state: str) -> Optional[str]:
        return self.client.get(f"oauth:{state}")
    
    def delete_oauth_state(self, state: str):
        self.client.delete(f"oauth:{state}")

redis_client = RedisClient()

# ============================================================================
# THOR UNIFIED ENGINE - THE HEART OF THE SYSTEM
# ============================================================================

class ThorEngine:
    """
    Unified trading engine supporting both:
    - Broker-level operations (using CLIENT_ID/CLIENT_SECRET)
    - User-level operations (using user's API keys)
    - Automatic endpoint selection (Indonesia/Testnet)
    """
    
    def __init__(self, use_testnet: bool = False):
        self.client_id = settings.CLIENT_ID
        self.client_secret = settings.CLIENT_SECRET
        self.broker_code = settings.BROKER_CODE
        self.recv_window = "20000"
        
        if use_testnet:
            self.base_url = settings.BYBIT_TESTNET
        else:
            self.base_url = settings.BYBIT_V5
        
        self.oauth_url = settings.BYBIT_OAUTH
        self.client = httpx.AsyncClient(timeout=30.0)
        
        logger.info(f"⚡ Thor Engine initialized | Broker: {self.broker_code} | Endpoint: {self.base_url}")
    
    def _generate_signature(self, api_key: str, api_secret: str, timestamp: str, params: str = "") -> str:
        sign_str = f"{timestamp}{api_key}{self.recv_window}{params}"
        return hmac.new(
            api_secret.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def _broker_request(self, method: str, endpoint: str, params: dict = None, data: dict = None) -> Dict:
        timestamp = str(int(time.time() * 1000))
        
        if method == "GET" and params:
            param_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
            signature = self._generate_signature(self.client_id, self.client_secret, timestamp, param_str)
            url = f"{self.base_url}{endpoint}"
            headers = {
                "X-BAPI-API-KEY": self.client_id,
                "X-BAPI-TIMESTAMP": timestamp,
                "X-BAPI-SIGN": signature,
                "X-BAPI-RECV-WINDOW": self.recv_window,
                "X-BAPI-PARTNER-ID": self.broker_code,
                "Content-Type": "application/json"
            }
            response = await self.client.get(url, headers=headers, params=params)
            
        elif data:
            body_str = json.dumps(data)
            signature = self._generate_signature(self.client_id, self.client_secret, timestamp, body_str)
            url = f"{self.base_url}{endpoint}"
            headers = {
                "X-BAPI-API-KEY": self.client_id,
                "X-BAPI-TIMESTAMP": timestamp,
                "X-BAPI-SIGN": signature,
                "X-BAPI-RECV-WINDOW": self.recv_window,
                "X-BAPI-PARTNER-ID": self.broker_code,
                "Content-Type": "application/json"
            }
            response = await self.client.post(url, headers=headers, json=data)
        else:
            url = f"{self.base_url}{endpoint}"
            if method == "GET":
                response = await self.client.get(url, params=params)
            else:
                response = await self.client.post(url, json=data)
        
        return response.json()
    
    async def broker_get_ticker(self, symbol: str = "BTCUSDT", category: str = "spot") -> Dict:
        return await self._broker_request(
            "GET",
            "/market/tickers",
            params={"category": category, "symbol": symbol}
        )
    
    async def broker_get_balance(self, account_type: str = "UNIFIED") -> Dict:
        return await self._broker_request(
            "GET",
            "/account/wallet-balance",
            params={"accountType": account_type}
        )
    
    async def _user_request(self, api_key: str, api_secret: str, method: str, 
                           endpoint: str, params: dict = None, data: dict = None) -> Dict:
        timestamp = str(int(time.time() * 1000))
        
        if method == "GET" and params:
            param_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
            signature = self._generate_signature(api_key, api_secret, timestamp, param_str)
            url = f"{self.base_url}{endpoint}"
            headers = {
                "X-BAPI-API-KEY": api_key,
                "X-BAPI-TIMESTAMP": timestamp,
                "X-BAPI-SIGN": signature,
                "X-BAPI-RECV-WINDOW": self.recv_window,
                "X-BAPI-PARTNER-ID": self.broker_code,
                "Content-Type": "application/json"
            }
            response = await self.client.get(url, headers=headers, params=params)
            
        elif data:
            body_str = json.dumps(data)
            signature = self._generate_signature(api_key, api_secret, timestamp, body_str)
            url = f"{self.base_url}{endpoint}"
            headers = {
                "X-BAPI-API-KEY": api_key,
                "X-BAPI-TIMESTAMP": timestamp,
                "X-BAPI-SIGN": signature,
                "X-BAPI-RECV-WINDOW": self.recv_window,
                "X-BAPI-PARTNER-ID": self.broker_code,
                "Content-Type": "application/json"
            }
            response = await self.client.post(url, headers=headers, json=data)
        else:
            return {"retCode": -1, "retMsg": "Invalid request"}
        
        return response.json()
    
    async def user_get_balance(self, api_key: str, api_secret: str, account_type: str = "UNIFIED") -> Dict:
        return await self._user_request(
            api_key, api_secret,
            "GET",
            "/account/wallet-balance",
            params={"accountType": account_type}
        )
    
    async def user_place_order(self, api_key: str, api_secret: str, symbol: str, side: str, 
                              qty: str, order_type: str = "Market", category: str = "spot") -> Dict:
        data = {
            "category": category,
            "symbol": symbol,
            "side": side,
            "orderType": order_type,
            "qty": qty,
            "timeInForce": "GTC",
            "brokerId": self.broker_code
        }
        return await self._user_request(api_key, api_secret, "POST", "/order/create", data=data)
    
    async def exchange_code(self, code: str) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.oauth_url}/oauth/v1/public/access_token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": settings.REDIRECT_URI
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Referer": "https://novatradingkeys.com"
                }
            )
            return response.json()
    
    async def get_user_uid(self, access_token: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.oauth_url}/oauth/v1/resource/restrict/uid_bearer",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            data = response.json()
            return str(data.get("uid", ""))
    
    async def get_user_api_keys(self, access_token: str) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.oauth_url}/oauth/v1/resource/restrict/openapi",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            return response.json()
    
    def format_balance(self, balance_data: Dict) -> Dict:
        try:
            coins = balance_data.get('result', {}).get('list', [{}])[0].get('coin', [])
            balances = {}
            total_usd = 0
            
            for coin in coins:
                name = coin.get('coin', '')
                balance = float(coin.get('walletBalance', '0'))
                usd_value = float(coin.get('usdValue', '0'))
                
                if balance > 0:
                    balances[name] = {
                        "balance": balance,
                        "usd_value": usd_value
                    }
                    total_usd += usd_value
            
            return {
                "success": True,
                "balances": balances,
                "total_usd": total_usd
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def format_ticker(self, ticker_data: Dict) -> Dict:
        try:
            ticker = ticker_data.get('result', {}).get('list', [{}])[0]
            return {
                "success": True,
                "symbol": ticker.get('symbol', ''),
                "price": float(ticker.get('lastPrice', 0)),
                "change_24h": float(ticker.get('price24hPcnt', 0)) * 100,
                "high_24h": float(ticker.get('highPrice24h', 0)),
                "low_24h": float(ticker.get('lowPrice24h', 0)),
                "volume": float(ticker.get('volume24h', 0))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def close(self):
        await self.client.aclose()

# ============================================================================
# API MODELS
# ============================================================================

class OrderRequest(BaseModel):
    symbol: str
    side: str
    qty: float
    order_type: str = "Market"

class BalanceResponse(BaseModel):
    success: bool
    balances: Dict
    total_usd: float

# ============================================================================
# API DEPENDENCIES
# ============================================================================

async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization")
    
    if authorization.startswith("Bearer "):
        user_id = authorization.replace("Bearer ", "")
    else:
        user_id = authorization.strip()
    
    keys = redis_client.get_user_keys(user_id)
    if not keys:
        raise HTTPException(status_code=401, detail="Invalid user session")
    
    return {
        "user_id": user_id,
        "api_key": keys['api_key'],
        "api_secret": keys['api_secret']
    }

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Nova Global Keys - Thor Engine",
    description="Complete Broker Level 3 Trading Platform",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# API ROUTES
# ============================================================================

@app.get("/")
async def root():
    return {
        "name": "Nova Global Keys",
        "version": "3.0.0",
        "broker": settings.BROKER_CODE,
        "status": "operational"
    }

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "broker": settings.BROKER_CODE,
        "redis": redis_client.ping(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/auth/login")
async def auth_login():
    state = uuid.uuid4().hex[:8]
    url = f"https://www.bybit.com/en/oauth?client_id={settings.CLIENT_ID}&response_type=code&scope=openapi&state={state}&redirect_uri={settings.REDIRECT_URI}&affiliate_id={settings.AFFILIATE_ID}"
    return RedirectResponse(url)

@app.get("/api/auth/callback/bybit")
async def auth_callback(code: str, state: str):
    logger.info(f"OAuth callback: state={state}")
    
    tg_user_id = redis_client.get_oauth_state(state)
    
    engine = ThorEngine()
    token_data = await engine.exchange_code(code)
    access_token = token_data.get('access_token')
    
    if not access_token:
        return JSONResponse(status_code=400, content={"error": "Token exchange failed"})
    
    keys_data = await engine.get_user_api_keys(access_token)
    result = keys_data.get("result", {})
    api_key = result.get("api_key")
    api_secret = result.get("api_secret")
    uid = await engine.get_user_uid(access_token)
    
    if tg_user_id:
        redis_client.store_user_keys(tg_user_id, api_key, api_secret, uid)
        redis_client.delete_oauth_state(state)
        return JSONResponse(content={
            "success": True,
            "message": "Account connected to Telegram!",
            "uid": uid
        })
    else:
        session_id = uuid.uuid4().hex
        redis_client.store_user_keys(session_id, api_key, api_secret, uid)
        return RedirectResponse(f"{settings.FRONTEND_URL}/dashboard?session={session_id}")
# ===== DASHBOARD API ENDPOINTS =====

@app.get("/api/v1/user/info")
async def get_user_info(current_user: dict = Depends(get_current_user)):
    """Get basic user info for header"""
    return {
        "uid": current_user['user_id'],
        "authenticated": True
    }

@app.post("/api/v1/bots/{bot_id}/{action}")
async def control_bot(bot_id: str, action: str, current_user: dict = Depends(get_current_user)):
    """Control bot (start/pause/stop)"""
    from strategies.storage import get_strategy, update_strategy
    
    strategy_data = get_strategy(current_user['user_id'], bot_id)
    if not strategy_data:
        return {"success": False, "error": "Bot not found"}
    
    if action == 'pause':
        strategy_data['paused'] = True
    elif action == 'start':
        strategy_data['paused'] = False
    elif action == 'stop':
        from strategies.storage import delete_strategy
        delete_strategy(current_user['user_id'], bot_id)
        return {"success": True, "message": "Bot stopped"}
    
    update_strategy(current_user['user_id'], bot_id, strategy_data)
    return {"success": True}
@app.get("/api/v1/strategies")
async def get_strategies(current_user: dict = Depends(get_current_user)):
    """Get user's active strategies"""
    try:
        from strategies.storage import list_strategies
        strategies = list_strategies(current_user['user_id'])
        return {"success": True, "strategies": strategies}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/v1/p2p/orders")
async def get_p2p_orders(current_user: dict = Depends(get_current_user)):
    """Get user's P2P orders"""
    try:
        # Fetch from Redis - in production, would call Bybit P2P API
        keys = redis_client.client.keys(f"p2p_order:{current_user['user_id']}:*")
        orders = []
        for key in keys:
            data = redis_client.client.get(key)
            if data:
                try:
                    orders.append(eval(data))
                except:
                    pass
        return {"success": True, "orders": orders}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/v1/payments")
async def get_payments(current_user: dict = Depends(get_current_user)):
    """Get user's payment history"""
    try:
        keys = redis_client.client.keys(f"payment:*")
        payments = []
        for key in keys:
            data = redis_client.client.get(key)
            if data and current_user['user_id'] in data:
                try:
                    payments.append(eval(data))
                except:
                    pass
        
        credit = float(redis_client.client.get(f"user:{current_user['user_id']}:credit") or 0)
        return {"success": True, "payments": payments[-10:], "credit": credit}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/v1/performance")
async def get_performance(current_user: dict = Depends(get_current_user)):
    """Get user's trading performance"""
    try:
        from strategies.storage import list_strategies
        strategies = list_strategies(current_user['user_id'])
        
        total_trades = 0
        total_pnl = 0.0
        
        for s in strategies:
            total_trades += s.get('trades', 0)
            total_pnl += s.get('pnl', 0.0)
        
        return {
            "success": True,
            "total_trades": total_trades,
            "total_pnl": total_pnl,
            "strategies": strategies
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
@app.get("/api/v1/leaderboard")
async def get_leaderboard():
    """Get global leaderboard"""
    try:
        # Example: fetch top 10 from Redis sorted set
        leaders = redis_client.client.zrevrange("leaderboard:pnl", 0, 9, withscores=True)
        return {"success": True, "leaders": [
            {"user": u.decode(), "pnl": score} for u, score in leaders
        ]}
    except Exception as e:
        return {"success": False, "error": str(e)}
# ===== BOT MANAGEMENT ENDPOINTS =====

@app.get("/api/v1/bots")
async def get_bots(current_user: dict = Depends(get_current_user)):
    """Get user's trading bots"""
    try:
        from strategies.storage import list_strategies
        strategies = list_strategies(current_user['user_id'])
        
        # Format for frontend
        bots = []
        for s in strategies:
            bots.append({
                "id": s.get('strategy_id', ''),
                "type": s.get('type', 'dca'),
                "symbol": s.get('symbol', 'BTCUSDT'),
                "amount": s.get('amount', 0),
                "status": "running" if not s.get('paused', False) else "paused",
                "trades": s.get('performance', {}).get('trades', 0),
                "pnl": s.get('performance', {}).get('pnl', 0),
                "interval": s.get('config', {}).get('interval_hours', 24) * 60
            })
        
        return {"success": True, "bots": bots}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/v1/orders")
async def get_orders(current_user: dict = Depends(get_current_user)):
    """Get user's recent orders"""
    try:
        # For now, return empty list (will be populated by real trades)
        return {"success": True, "orders": []}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/v1/bots/create")
async def create_bot(request: dict, current_user: dict = Depends(get_current_user)):
    """Create a new trading bot"""
    try:
        from strategies.dca import DCAStrategy
        from strategies.storage import save_strategy
        
        bot_type = request.get('type', 'dca')
        symbol = request.get('symbol', 'BTCUSDT')
        amount = float(request.get('amount', 100))
        interval = int(request.get('interval', 60))
        
        strategy = DCAStrategy(
            uid=current_user['user_id'],
            symbol=symbol,
            amount=amount,
            interval_hours=interval / 60
        )
        
        strategy_id = save_strategy(current_user['user_id'], strategy)
        return {"success": True, "bot_id": strategy_id}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/v1/bots/{bot_id}/{action}")
async def control_bot(bot_id: str, action: str, current_user: dict = Depends(get_current_user)):
    """Control bot (start/pause/stop)"""
    try:
        from strategies.storage import get_strategy, update_strategy, delete_strategy
        
        strategy_data = get_strategy(current_user['user_id'], bot_id)
        if not strategy_data:
            return {"success": False, "error": "Bot not found"}
        
        if action == 'pause':
            strategy_data['paused'] = True
            update_strategy(current_user['user_id'], bot_id, strategy_data)
            return {"success": True, "message": "Bot paused"}
        elif action == 'start':
            strategy_data['paused'] = False
            update_strategy(current_user['user_id'], bot_id, strategy_data)
            return {"success": True, "message": "Bot started"}
        elif action == 'stop':
            delete_strategy(current_user['user_id'], bot_id)
            return {"success": True, "message": "Bot stopped"}
        else:
            return {"success": False, "error": "Invalid action"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== GOOGLE OAUTH ROUTES =====

@app.get("/api/auth/google")
async def google_login():
    """Redirect to Google OAuth"""
    state = uuid.uuid4().hex[:8]
    # Store state in Redis to verify later
    redis_client.client.setex(f"google_oauth:{state}", 600, "pending")
    
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?client_id=650988179236-k55rkljpmg3m1gaak4sjmojsm8psv798.apps.googleusercontent.com"
        "&response_type=code"
        "&scope=email%20profile"
        "&redirect_uri=https://novatradingkeys.com/api/auth/callback/google"
        f"&state={state}"
    )
    return RedirectResponse(url)

@app.get("/api/auth/callback/google")
async def google_callback(code: str, state: str = None):  # Make state optional
    logger.info(f"Google OAuth callback received")
    
    # Optional: verify state if provided
    if state and not redis_client.client.get(f"google_oauth:{state}"):
        logger.warning(f"Invalid state: {state}")
    elif state:
        redis_client.client.delete(f"google_oauth:{state}")
    
    # Continue with token exchange...
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": "650988179236-k55rkljpmg3m1gaak4sjmojsm8psv798.apps.googleusercontent.com",
                "client_secret": "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",
                "redirect_uri": "https://novatradingkeys.com/api/auth/callback/google",
                "grant_type": "authorization_code"
            }
        )
        # ... rest of the code
        
        if token_resp.status_code != 200:
            return JSONResponse(status_code=400, content={"error": "Token exchange failed"})
        
        token_data = token_resp.json()
        access_token = token_data.get('access_token')
        
        # Get user info
        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        user_data = user_resp.json()
        uid = user_data.get('id')
        email = user_data.get('email')
        name = user_data.get('name')
        
        # Check if from Telegram (you can implement this)
        tg_user_id = None  # Implement if needed
        
        if tg_user_id:
            # Store for Telegram user
            redis_client.store_user_keys(tg_user_id, "google", access_token, uid)
            return JSONResponse(content={
                "success": True,
                "message": "Google account connected to Telegram!",
                "uid": uid,
                "email": email
            })
        else:
            # Web user - generate session
            session_id = uuid.uuid4().hex
            redis_client.client.setex(
                f"session:{session_id}", 
                86400, 
                str({"uid": uid, "email": email, "name": name, "provider": "google"})
            )
            return RedirectResponse(f"{settings.FRONTEND_URL}/dashboard?session={session_id}&provider=google")
@app.get("/api/v1/price/{symbol}")
async def get_price(symbol: str):
    engine = ThorEngine()
    result = await engine.broker_get_ticker(symbol)
    
    if result.get('retCode') == 0:
        formatted = engine.format_ticker(result)
        return formatted
    else:
        raise HTTPException(status_code=400, detail=result.get('retMsg', 'Unknown error'))

@app.get("/api/v1/balance")
async def get_balance(current_user: dict = Depends(get_current_user)):
    engine = ThorEngine()
    result = await engine.user_get_balance(
        current_user['api_key'],
        current_user['api_secret']
    )
    
    if result.get('retCode') == 0:
        formatted = engine.format_balance(result)
        return {
            "success": True,
            "user_id": current_user['user_id'],
            "balances": formatted['balances'],
            "total_usd": formatted['total_usd']
        }
    else:
        raise HTTPException(status_code=400, detail=result.get('retMsg', 'Unknown error'))

@app.post("/api/v1/order")
async def place_order(order: OrderRequest, current_user: dict = Depends(get_current_user)):
    engine = ThorEngine()
    
    ticker = await engine.broker_get_ticker(order.symbol)
    if ticker.get('retCode') != 0:
        raise HTTPException(status_code=400, detail="Could not fetch price")
    
    price_data = engine.format_ticker(ticker)
    if not price_data['success']:
        raise HTTPException(status_code=400, detail="Invalid price data")
    
    qty = str(round(order.qty / price_data['price'], 4))
    
    result = await engine.user_place_order(
        current_user['api_key'],
        current_user['api_secret'],
        order.symbol,
        order.side,
        qty,
        order.order_type
    )
    
    if result.get('retCode') == 0:
        return {
            "success": True,
            "order_id": result.get('result', {}).get('orderId'),
            "symbol": order.symbol,
            "side": order.side,
            "amount_usd": order.qty,
            "quantity": float(qty),
            "price": price_data['price'],
            "user_id": current_user['user_id']
        }
    else:
        raise HTTPException(status_code=400, detail=result.get('retMsg', 'Order failed'))

# ============================================================================
# COMMAND MODULES IMPORT STATUS
# ============================================================================

STRATEGY_COMMANDS_AVAILABLE = False
PAYMENT_COMMANDS_AVAILABLE = False
P2P_COMMANDS_AVAILABLE = False

try:
    from bot.commands.strategies import register_strategy_commands
    STRATEGY_COMMANDS_AVAILABLE = True
    logger.info("✅ Strategy commands module loaded")
except ImportError:
    logger.warning("⚠️ Strategy commands not available")

try:
    from bot.commands.payments import register_payment_commands
    PAYMENT_COMMANDS_AVAILABLE = True
    logger.info("✅ Payment commands module loaded")
except ImportError:
    logger.warning("⚠️ Payment commands not available")

try:
    from bot.commands.p2p import register_p2p_commands
    P2P_COMMANDS_AVAILABLE = True
    logger.info("✅ P2P commands module loaded")
except ImportError:
    logger.warning("⚠️ P2P commands not available")

# ============================================================================
# TELEGRAM BOT
# ============================================================================

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)

class TelegramBot:
    """Telegram bot runner"""
    
    def __init__(self):
        self.bot = bot
        self.register_handlers()
        logger.info("🤖 Telegram bot initialized")
    
    def register_handlers(self):
        """Register all command handlers"""
        
        if STRATEGY_COMMANDS_AVAILABLE:
            try:
                register_strategy_commands(self.bot)
                logger.info("✅ Strategy commands registered")
            except Exception as e:
                logger.error(f"❌ Failed to register strategy commands: {e}")
        
        if PAYMENT_COMMANDS_AVAILABLE:
            try:
                register_payment_commands(self.bot)
                logger.info("✅ Payment commands registered")
            except Exception as e:
                logger.error(f"❌ Failed to register payment commands: {e}")
        
        if P2P_COMMANDS_AVAILABLE:
            try:
                register_p2p_commands(self.bot)
                logger.info("✅ P2P commands registered")
            except Exception as e:
                logger.error(f"❌ Failed to register P2P commands: {e}")
        
        @self.bot.message_handler(commands=['start', 'help'])
        def cmd_start(message):
            welcome = f"""
✨ *Welcome to Nova Global Keys, {message.from_user.first_name}!* ✨

🙏 *Love, Peace & Respect*

*Broker:* `{settings.BROKER_CODE}`

📋 *BASIC COMMANDS:*
/connect - Link Bybit account
/balance - View wallet
/price BTC - Get price
/status - System check
/trade - Place a trade

📊 *STRATEGY COMMANDS:*
/strategy dca BTCUSDT 50 - Create DCA strategy
/mystrategy - View strategies
/performance - View performance

💰 *PAYMENT COMMANDS:*
/pay - Payment options
/cash 50 - Request cash payment
/confirm ID TXID - Confirm payment

🔄 *P2P COMMANDS:*
/p2p - P2P trading menu

*Type any command to get started!*
            """
            self.bot.reply_to(message, welcome, parse_mode="Markdown")
        
        @self.bot.message_handler(commands=['connect'])
        def cmd_connect(message):
            user_id = str(message.from_user.id)
            state = f"tg_{user_id}_{uuid.uuid4().hex[:8]}"
            redis_client.store_oauth_state(state, user_id)
            
            url = f"https://www.bybit.com/en/oauth?client_id={settings.CLIENT_ID}&response_type=code&scope=openapi&state={state}&redirect_uri={settings.REDIRECT_URI}&affiliate_id={settings.AFFILIATE_ID}"
            
            msg = f"""
🔐 *Connect Your Bybit Account*

[Click here to connect]({url})

⚠️ You'll be redirected automatically
            """
            self.bot.reply_to(message, msg, parse_mode="Markdown", disable_web_page_preview=False)
        
        @self.bot.message_handler(commands=['price'])
        def cmd_price(message):
            parts = message.text.split()
            symbol = parts[1].upper() if len(parts) > 1 else "BTCUSDT"
            
            self.bot.reply_to(message, f"🔄 Fetching {symbol}...")
            
            def fetch_and_reply():
                import httpx
                try:
                    response = httpx.get(f"http://localhost:{settings.PORT}/api/v1/price/{symbol}", timeout=10)
                    data = response.json()
                    
                    if data.get('success'):
                        reply = f"""
📊 *{data['symbol']}*
💰 Price: ${data['price']:,.2f}
📈 24h: {data['change_24h']:+.2f}%
📊 High: ${data['high_24h']:,.2f}
📉 Low: ${data['low_24h']:,.2f}
                        """
                        self.bot.reply_to(message, reply, parse_mode="Markdown")
                    else:
                        self.bot.reply_to(message, f"❌ Could not fetch {symbol}")
                except Exception as e:
                    self.bot.reply_to(message, f"❌ Error: {str(e)}")
            
            threading.Thread(target=fetch_and_reply).start()
        
        @self.bot.message_handler(commands=['balance'])
        def cmd_balance(message):
            user_id = str(message.from_user.id)
            keys = redis_client.get_user_keys(user_id)
            
            if not keys:
                self.bot.reply_to(message, "❌ Please /connect first")
                return
            
            self.bot.reply_to(message, "🔄 Fetching your balance...")
            
            def fetch_and_reply():
                import httpx
                try:
                    response = httpx.get(
                        f"http://localhost:{settings.PORT}/api/v1/balance",
                        headers={"Authorization": user_id},
                        timeout=10
                    )
                    data = response.json()
                    
                    if data.get('success'):
                        reply = "💰 *Your Portfolio*\n\n"
                        for coin, details in data['balances'].items():
                            reply += f"• *{coin}:* {details['balance']:.4f} (${details['usd_value']:,.2f})\n"
                        
                        credit = float(redis_client.client.get(f"user:{user_id}:credit") or 0)
                        if credit > 0:
                            reply += f"\n*Shop Credit:* ${credit:.2f}"
                        
                        self.bot.reply_to(message, reply, parse_mode="Markdown")
                    else:
                        self.bot.reply_to(message, "❌ Could not fetch balance")
                except Exception as e:
                    self.bot.reply_to(message, f"❌ Error: {str(e)}")
            
            threading.Thread(target=fetch_and_reply).start()
        
        @self.bot.message_handler(commands=['trade'])
        def cmd_trade(message):
            parts = message.text.split()
            if len(parts) < 4:
                self.bot.reply_to(message, 
                    "❌ Usage: /trade [Buy/Sell] [Symbol] [Amount]\n"
                    "Example: /trade Buy BTCUSDT 100")
                return
            
            side = parts[1].capitalize()
            symbol = parts[2].upper()
            try:
                amount = float(parts[3])
            except:
                self.bot.reply_to(message, "❌ Invalid amount")
                return
            
            user_id = str(message.from_user.id)
            keys = redis_client.get_user_keys(user_id)
            
            if not keys:
                self.bot.reply_to(message, "❌ Please /connect first")
                return
            
            self.bot.reply_to(message, f"🔄 Placing {side} order for ${amount} of {symbol}...")
            
            def execute_and_reply():
                import httpx
                import asyncio
                
                async def execute():
                    async with httpx.AsyncClient() as client:
                        price_resp = await client.get(f"http://localhost:{settings.PORT}/api/v1/price/{symbol}")
                        price_data = price_resp.json()
                        
                        if not price_data.get('success'):
                            return {"error": "Could not fetch price"}
                        
                        current_price = price_data['price']
                        qty = round(amount / current_price, 4)
                        
                        order_resp = await client.post(
                            f"http://localhost:{settings.PORT}/api/v1/order",
                            json={
                                "symbol": symbol,
                                "side": side,
                                "qty": qty,
                                "order_type": "Market"
                            },
                            headers={"Authorization": user_id}
                        )
                        return order_resp.json()
                
                result = asyncio.run(execute())
                
                if result.get('success'):
                    reply = f"""
✅ *Order Executed!*

*{side}* ${amount} of {symbol}
*Quantity:* {result.get('quantity', 0):.4f}
*Price:* ${result.get('price', 0):,.2f}
*Order ID:* `{result.get('order_id', 'N/A')}`
                    """
                    self.bot.reply_to(message, reply, parse_mode="Markdown")
                else:
                    self.bot.reply_to(message, f"❌ Trade failed: {result.get('error', 'Unknown error')}")
            
            threading.Thread(target=execute_and_reply).start()

        @self.bot.message_handler(commands=['status'])
        def cmd_status(message):
            user_id = str(message.from_user.id)
            is_connected = redis_client.user_exists(user_id)
            
            heartbeat = redis_client.client.get("worker:last_heartbeat")
            worker_status = "❌ Not responding"
            if heartbeat:
                try:
                    last = datetime.fromisoformat(heartbeat)
                    if datetime.now(timezone.utc) - last < timedelta(minutes=2):
                        worker_status = "✅ Running"
                    else:
                        worker_status = "⚠️ Stale"
                except:
                    worker_status = "⚠️ Invalid"
            
            status = f"""
🟢 *System Status*

*Broker:* `{settings.BROKER_CODE}`
*Your Account:* {'✅ Connected' if is_connected else '❌ Not connected'}
*Redis:* ✅ Connected
*Worker:* {worker_status}
            """
            self.bot.reply_to(message, status, parse_mode="Markdown")
    
    def polling(self):
        """Run the bot with auto-reconnect"""
        while True:
            try:
                self.bot.infinity_polling(timeout=60)
            except Exception as e:
                logger.error(f"Bot error: {e}")
                time.sleep(5)

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    logger.info("=" * 60)
    logger.info("🚀 NOVA GLOBAL KEYS - THOR UNIFIED ENGINE v3.0 FINAL")
    logger.info("=" * 60)
    logger.info(f"Broker: {settings.BROKER_CODE}")
    logger.info(f"Endpoint: {settings.BYBIT_V5}")
    logger.info(f"Redis: {'✅' if redis_client.ping() else '❌'}")
    logger.info(f"Strategy Commands: {'✅' if STRATEGY_COMMANDS_AVAILABLE else '❌'}")
    logger.info(f"Payment Commands: {'✅' if PAYMENT_COMMANDS_AVAILABLE else '❌'}")
    logger.info(f"P2P Commands: {'✅' if P2P_COMMANDS_AVAILABLE else '❌'}")
    logger.info("=" * 60)
    
    telegram_bot = TelegramBot()
    bot_thread = threading.Thread(target=telegram_bot.polling, daemon=True)
    bot_thread.start()
    logger.info("✅ Telegram bot started")
    
    logger.info(f"✅ API server starting on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    main()
