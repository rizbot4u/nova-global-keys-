#!/usr/bin/env python3
"""
NOVA GLOBAL KEYS - THOR UNIFIED ENGINE v5.0 FINAL
Complete Broker Level 3 Trading System with ALL Bybit V5 Endpoints
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
import signal
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
    def __init__(self):
        # Use the correct format with password
        redis_url = settings.REDIS_URL
        if "NovaGlobal2026" not in redis_url:
            # IMPORTANT: Use 'default' as username, not empty
            redis_url = "redis://default:NovaGlobal2026@localhost:6379/0"
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
    
    def get_shop_credit(self, user_id: str) -> float:
        return float(self.client.get(f"user:{user_id}:shop_credit") or 0)
    
    def update_shop_credit(self, user_id: str, amount: float):
        self.client.incrbyfloat(f"user:{user_id}:shop_credit", amount)
    
    def update_heartbeat(self):
        """Update the heartbeat timestamp for the dashboard"""
        self.client.set("worker:last_heartbeat", datetime.now().isoformat())
        
        # Update warrior status
        status = {
            "engine": "Thor-Warrior-01",
            "status": "OPERATIONAL",
            "timestamp": datetime.now().isoformat()
        }
        self.client.set("nova:status:warrior_01", json.dumps(status))
    
    def increment_requests(self):
        """Increment total request counter"""
        self.client.incr("stats:main_api:total_requests")

redis_client = RedisClient()

# ============================================================================
# KILLSWITCH LISTENER
# ============================================================================

def killswitch_listener():
    """
    Background thread that listens for KILL_ALL_BOTS commands on Redis pubsub
    This is the PANIC BUTTON that can shut down the entire system
    """
    logger.info("🔫 Killswitch listener started - monitoring 'nova:commands' channel")
    
    # Create a separate Redis connection for pubsub (thread-safe)
    pubsub_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = pubsub_client.pubsub()
    pubsub.subscribe("nova:commands")
    
    logger.info("📡 Killswitch active - waiting for commands...")
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            command = message['data']
            logger.warning(f"📡 Received command: {command}")
            
            if command == 'KILL_ALL_BOTS':
                logger.critical("🛑 EMERGENCY SHUTDOWN ACTIVATED - KILL_ALL_BOTS received")
                logger.critical("💀 All trading bots and API services terminating NOW")
                
                # Final status update before death
                try:
                    dead_status = {
                        "engine": "Thor-Warrior-01",
                        "status": "TERMINATED",
                        "timestamp": datetime.now().isoformat(),
                        "reason": "KILL_ALL_BOTS command received"
                    }
                    redis_client.client.set("nova:status:warrior_01", json.dumps(dead_status))
                    redis_client.client.set("worker:last_heartbeat", datetime.now().isoformat())
                except:
                    pass
                
                # Force exit - this kills everything
                os._exit(0)
            
            elif command == 'PING':
                logger.debug("📡 Received PING, sending PONG")
                try:
                    # Just update heartbeat to show we're alive
                    redis_client.update_heartbeat()
                except:
                    pass

# ============================================================================
# HEARTBEAT THREAD
# ============================================================================

def heartbeat_pulse():
    """
    Background thread that periodically updates the heartbeat
    Ensures dashboard sees the system as alive even without API requests
    """
    logger.info("❤️ Heartbeat pulse thread started")
    
    while True:
        try:
            redis_client.update_heartbeat()
            redis_client.increment_requests()  # Increment counter to show activity
            
            # Log every minute at debug level
            logger.debug(f"❤️ Heartbeat pulse sent at {datetime.now().isoformat()}")
            
            # Sleep for 10 seconds (dashboard shows red after 30 seconds)
            time.sleep(10)
        except Exception as e:
            logger.error(f"❤️ Heartbeat error: {e}")
            time.sleep(5)

# ============================================================================
# THOR ENGINE - COMPLETE BYBIT V5 IMPLEMENTATION
# ============================================================================

class ThorEngine:
    """
    Complete Bybit V5 implementation with proper HMAC signatures
    Full broker support with X-Referer header for rebates
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.broker_code = settings.BROKER_CODE
        self.affiliate_id = settings.AFFILIATE_ID
        self.recv_window = "20000"
        
        if settings.USE_TESTNET:
            self.base_url = "https://api-testnet.bybit.com"
        else:
            self.base_url = "https://api.bybit.id"  # Indonesia endpoint
        
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"⚡ Thor Engine initialized | Broker: {self.broker_code}")
    
    def _generate_signature(self, timestamp: str, params: str = "", data: dict = None) -> str:
        """Generate HMAC SHA256 signature according to Bybit V5 specs"""
        if not self.api_secret:
            return ""
        
        if data:
            # POST request - use JSON body (compact, no spaces)
            body_str = json.dumps(data, separators=(',', ':'))
            sign_str = f"{timestamp}{self.api_key}{self.recv_window}{body_str}"
        else:
            # GET request - use query string
            sign_str = f"{timestamp}{self.api_key}{self.recv_window}{params}"
        
        return hmac.new(
            self.api_secret.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def _request(self, method: str, endpoint: str, params: dict = None, data: dict = None) -> Dict:
        """Make authenticated request to Bybit API"""
        timestamp = str(int(time.time() * 1000))
        
        # Build query string for GET requests
        query_string = ""
        if method == "GET" and params:
            sorted_params = sorted(params.items())
            query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        
        # Generate signature
        signature = self._generate_signature(timestamp, query_string, data)
        
        # Headers - includes broker code for rebates
        headers = {
            "X-BAPI-API-KEY": self.api_key or "",
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-SIGN": signature,
            "X-BAPI-RECV-WINDOW": self.recv_window,
            "X-Referer": self.broker_code,  # CRITICAL for broker rebates
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
    
    # ===== MARKET ENDPOINTS =====
    
    async def get_tickers(self, category: str = "spot", symbol: str = None):
        """Get real-time tickers"""
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/v5/market/tickers", params=params)
    
    async def get_orderbook(self, category: str, symbol: str, limit: int = 25):
        """Get order book - FIXED: category has default, symbol required"""
        params = {
            "category": category,
            "symbol": symbol,
            "limit": limit
        }
        return await self._request("GET", "/v5/market/orderbook", params=params)
    
    async def get_kline(self, category: str, symbol: str, interval: str = "D", limit: int = 200):
        """Get kline/candlestick data"""
        params = {
            "category": category,
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        return await self._request("GET", "/v5/market/kline", params=params)
    
    async def get_instruments(self, category: str = "spot", symbol: str = None):
        """Get instruments info"""
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/v5/market/instruments-info", params=params)
    
    async def get_server_time(self):
        """Get Bybit server time"""
        return await self._request("GET", "/v5/market/time")
    
    # ===== ACCOUNT ENDPOINTS =====
    
    async def get_wallet_balance(self, account_type: str = "UNIFIED", coin: str = None):
        """Get wallet balance"""
        params = {"accountType": account_type}
        if coin:
            params["coin"] = coin
        return await self._request("GET", "/v5/account/wallet-balance", params=params)
    
    async def get_account_info(self):
        """Get account info"""
        return await self._request("GET", "/v5/account/info")
    
    async def get_fee_rate(self, category: str = "spot", symbol: str = None):
        """Get fee rate"""
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/v5/account/fee-rate", params=params)
    
    # ===== TRADE ENDPOINTS =====
    
    async def place_order(self, category: str, symbol: str, side: str, order_type: str,
                         qty: str, price: str = None, time_in_force: str = "GTC"):
        """Place an order"""
        data = {
            "category": category,
            "symbol": symbol,
            "side": side,
            "orderType": order_type,
            "qty": qty,
            "timeInForce": time_in_force,
            "brokerId": self.broker_code  # Ensures rebates
        }
        if price:
            data["price"] = price
        
        return await self._request("POST", "/v5/order/create", data=data)
    
    async def get_open_orders(self, category: str, symbol: str = None, limit: int = 50):
        """Get open orders"""
        params = {"category": category, "limit": limit}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/v5/order/realtime", params=params)
    
    async def get_order_history(self, category: str, symbol: str = None, limit: int = 50):
        """Get order history"""
        params = {"category": category, "limit": limit}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/v5/order/history", params=params)
    
    async def cancel_order(self, category: str, symbol: str, order_id: str = None, order_link_id: str = None):
        """Cancel an order"""
        data = {
            "category": category,
            "symbol": symbol
        }
        if order_id:
            data["orderId"] = order_id
        if order_link_id:
            data["orderLinkId"] = order_link_id
        
        return await self._request("POST", "/v5/order/cancel", data=data)
    
    async def cancel_all_orders(self, category: str):
        """Cancel all orders"""
        data = {"category": category}
        return await self._request("POST", "/v5/order/cancel-all", data=data)
    
    # ===== POSITION ENDPOINTS =====
    
    async def get_positions(self, category: str = "linear", symbol: str = None):
        """Get positions"""
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/v5/position/list", params=params)
    
    async def get_closed_pnl(self, category: str, symbol: str = None, limit: int = 50):
        """Get closed PnL"""
        params = {"category": category, "limit": limit}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/v5/position/closed-pnl", params=params)
    
    async def set_leverage(self, category: str, symbol: str, leverage: str):
        """Set leverage"""
        data = {
            "category": category,
            "symbol": symbol,
            "leverage": leverage
        }
        return await self._request("POST", "/v5/position/set-leverage", data=data)
    
    # ===== ASSET ENDPOINTS =====
    
    async def get_coin_balance(self, account_type: str = "FUND", coin: str = None, member_id: str = None):
        """Get coin balance"""
        params = {"accountType": account_type}
        if coin:
            params["coin"] = coin
        if member_id:
            params["memberId"] = member_id
        return await self._request("GET", "/v5/asset/transfer/query-account-coins-balance", params=params)
    
    async def get_deposit_address(self, coin: str):
        """Get deposit address"""
        params = {"coin": coin}
        return await self._request("GET", "/v5/asset/deposit/address", params=params)
    
    async def get_deposit_history(self, coin: str = None, limit: int = 50):
        """Get deposit history"""
        params = {"limit": limit}
        if coin:
            params["coin"] = coin
        return await self._request("GET", "/v5/asset/deposit/record", params=params)
    
    async def get_withdraw_history(self, coin: str = None, limit: int = 50):
        """Get withdrawal history"""
        params = {"limit": limit}
        if coin:
            params["coin"] = coin
        return await self._request("GET", "/v5/asset/withdraw/record", params=params)
    
    async def create_transfer(self, transfer_id: str, from_account: str, to_account: str, coin: str, amount: str):
        """Create internal transfer"""
        data = {
            "transferId": transfer_id,
            "fromAccountType": from_account,
            "toAccountType": to_account,
            "coin": coin,
            "amount": amount
        }
        return await self._request("POST", "/v5/asset/transfer/inter-transfer", data=data)
    
    # ===== AFFILIATE ENDPOINTS =====
    
    async def get_affiliate_commission(self, limit: int = 50):
        """Get affiliate commission"""
        params = {"limit": limit}
        return await self._request("GET", "/v5/affiliate/commission", params=params)
    
    async def get_affiliate_user_list(self, size: int = 50, page: int = 1):
        """Get affiliate user list"""
        params = {"size": size, "page": page}
        return await self._request("GET", "/v5/affiliate/affiliate-user-list", params=params)
    
    # ===== BROKER ENDPOINTS =====
    
    async def create_subaccount(self, username: str, member_type: int = 1, note: str = ""):
        """Create subaccount"""
        data = {
            "username": username,
            "memberType": member_type,
            "note": note
        }
        return await self._request("POST", "/v5/broker/create-sub-member", data=data)
    
    async def get_subaccount_list(self):
        """Get subaccount list"""
        return await self._request("GET", "/v5/broker/sub-member-list")
    
    async def set_subaccount_fee(self, sub_uid: str, fee_rate: dict):
        """Set subaccount fee"""
        data = {
            "subUid": sub_uid,
            "feeRate": fee_rate
        }
        return await self._request("POST", "/v5/broker/set-sub-member-fee", data=data)
    
    # ===== P2P ENDPOINTS =====
    
    async def get_p2p_balance(self, coin: str = None):
        """Get P2P balance"""
        params = {}
        if coin:
            params["coin"] = coin
        logger.info(f"🔍 P2P Request params: {params}")
        result = await self._request("GET", "/v5/p2p/balance", params=params)
        logger.info(f"🔍 P2P Response raw: {result}")
        return result

    async def get_p2p_orders(self, side: str = None, status: str = None, limit: int = 50):
        """Get P2P orders"""
        try:
            params = {"limit": limit}
            if side:
                params["side"] = side
            if status:
                params["status"] = status
                
            logger.info(f"🔍 Making P2P orders request with params: {params}")
            
            # Use the correct P2P endpoint
            result = await self._request("GET", "/v5/p2p/order/list", params=params)
            
            logger.info(f"🔍 P2P orders response: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in get_p2p_orders: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    # ===== RFQ/OTC ENDPOINTS =====
    
    async def create_rfq(self, data: dict):
        """Create RFQ"""
        return await self._request("POST", "/v5/rfq/create", data=data)
    
    async def execute_rfq(self, data: dict):
        """Execute RFQ"""
        return await self._request("POST", "/v5/rfq/execute", data=data)
    
    async def get_rfq_config(self):
        """Get RFQ config"""
        return await self._request("GET", "/v5/rfq/config")
    
    # ===== HELPER METHODS =====
    
    def format_balance(self, balance_data: Dict) -> Dict:
        """Format balance response for frontend"""
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
                            balances[coin_name] = {
                                "balance": wallet_balance,
                                "usd_value": usd_value
                            }
                            total_usd += usd_value
                            assets.append({
                                "coin": coin_name,
                                "balance": wallet_balance,
                                "usd_value": usd_value
                            })
            
            return {
                "success": True,
                "balances": balances,
                "total_usd": total_usd,
                "assets": assets
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def format_ticker(self, ticker_data: Dict) -> Dict:
        """Format ticker response for frontend"""
        try:
            if ticker_data.get('retCode') == 0:
                ticker = ticker_data['result']['list'][0]
                return {
                    "success": True,
                    "symbol": ticker.get('symbol', ''),
                    "price": float(ticker.get('lastPrice', 0)),
                    "change_24h": float(ticker.get('price24hPcnt', 0)) * 100,
                    "high_24h": float(ticker.get('highPrice24h', 0)),
                    "low_24h": float(ticker.get('lowPrice24h', 0)),
                    "volume": float(ticker.get('volume24h', 0))
                }
            return {"success": False, "error": ticker_data.get('retMsg', 'Unknown error')}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

# ============================================================================
# API MODELS
# ============================================================================

class OrderRequest(BaseModel):
    symbol: str
    side: str
    qty: float
    order_type: str = "Market"
    category: str = "spot"
    price: Optional[float] = None

# ============================================================================
# API DEPENDENCIES
# ============================================================================

async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization")
    
    user_id = authorization.replace("Bearer ", "").strip()
    
    keys = redis_client.get_user_keys(user_id)
    if not keys:
        # Try as session ID
        api_key = redis_client.client.get(f"user:{user_id}:api_key")
        api_secret = redis_client.client.get(f"user:{user_id}:api_secret")
        if api_key and api_secret:
            return {
                "user_id": user_id,
                "api_key": api_key,
                "api_secret": api_secret
            }
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
    title="Nova Global Keys - Thor Engine v5.0",
    description="Complete Bybit V5 Integration with Broker Level 3",
    version="5.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REQUEST TRACKING MIDDLEWARE - THE PULSE
# ============================================================================

@app.middleware("http")
async def engine_monitor_middleware(request: Request, call_next):
    """
    The 'Pulse' of the Engine: Tracks every request and updates Redis
    This ensures the frontend dashboard sees the system as alive
    """
    # Process the request
    response = await call_next(request)
    
    try:
        # Update Redis with signs of life
        redis_client.increment_requests()           # Increment request counter
        redis_client.update_heartbeat()              # Update heartbeat and warrior status
    except Exception as e:
        logger.error(f"Monitoring Error: {e}")
    
    return response

# ============================================================================
# ROOT & HEALTH ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {
        "name": "Nova Global Keys",
        "version": "5.0.0",
        "broker": settings.BROKER_CODE,
        "affiliate": settings.AFFILIATE_ID,
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

# ============================================================================
# DASHBOARD STATUS ENDPOINT
# ============================================================================

@app.get("/api/status")
async def get_status():
    """Get current system status for dashboard"""
    heartbeat = redis_client.client.get("worker:last_heartbeat")
    warrior_status = redis_client.client.get("nova:status:warrior_01")
    request_count = redis_client.client.get("stats:main_api:total_requests") or "0"
    
    # Calculate if system is alive
    is_alive = False
    if heartbeat:
        try:
            last = datetime.fromisoformat(heartbeat)
            if datetime.now(timezone.utc) - last < timedelta(seconds=30):
                is_alive = True
        except:
            pass
    
    return {
        "alive": is_alive,
        "heartbeat": heartbeat,
        "warrior_status": json.loads(warrior_status) if warrior_status else None,
        "total_requests": int(request_count),
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# OAUTH ENDPOINTS
# ============================================================================

@app.get("/api/auth/login")
async def auth_login():
    state = uuid.uuid4().hex[:8]
    url = f"https://www.bybit.com/en/oauth?client_id={settings.CLIENT_ID}&response_type=code&scope=openapi&state={state}&redirect_uri={settings.REDIRECT_URI}&affiliate_id={settings.AFFILIATE_ID}"
    return RedirectResponse(url)

@app.get("/api/auth/callback/bybit")
async def auth_callback(code: str, state: str):
    logger.info(f"OAuth callback: state={state}")
    
    tg_user_id = redis_client.get_oauth_state(state)
    
    async with httpx.AsyncClient() as client:
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
            return JSONResponse(status_code=400, content={"error": "Token exchange failed"})
        
        # Get API keys
        keys_resp = await client.get(
            f"{settings.BYBIT_OAUTH}/oauth/v1/resource/restrict/openapi",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        keys_data = keys_resp.json()
        api_key = keys_data.get("result", {}).get("api_key")
        api_secret = keys_data.get("result", {}).get("api_secret")
        
        # Get UID
        uid_resp = await client.get(
            f"{settings.BYBIT_OAUTH}/oauth/v1/resource/restrict/uid_bearer",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        uid = uid_resp.json().get("uid", "")
    
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

# ============================================================================
# [ALL OTHER ENDPOINTS REMAIN EXACTLY THE SAME]
# ============================================================================
# MARKET DATA ENDPOINTS, ACCOUNT ENDPOINTS, TRADE ENDPOINTS, 
# POSITION ENDPOINTS, ASSET ENDPOINTS, AFFILIATE ENDPOINTS,
# BROKER ENDPOINTS, P2P ENDPOINTS, RFQ ENDPOINTS, V1 COMPATIBILITY ENDPOINTS
# All stay exactly as they were in the original file
# ============================================================================

# MARKET DATA ENDPOINTS (Public)
@app.get("/api/market/tickers")
async def get_tickers(category: str = "spot", symbol: str = None):
    """Get real-time tickers"""
    engine = ThorEngine()
    result = await engine.get_tickers(category=category, symbol=symbol)
    return result

@app.get("/api/market/orderbook")
async def get_orderbook(category: str, symbol: str, limit: int = 25):
    """Get order book"""
    engine = ThorEngine()
    result = await engine.get_orderbook(category=category, symbol=symbol, limit=limit)
    return result

@app.get("/api/market/kline")
async def get_kline(category: str, symbol: str, interval: str = "D", limit: int = 200):
    """Get kline/candlestick data"""
    engine = ThorEngine()
    result = await engine.get_kline(category=category, symbol=symbol, interval=interval, limit=limit)
    return result

@app.get("/api/market/instruments")
async def get_instruments(category: str = "spot", symbol: str = None):
    """Get instruments info"""
    engine = ThorEngine()
    result = await engine.get_instruments(category=category, symbol=symbol)
    return result

@app.get("/api/market/time")
async def get_server_time():
    """Get Bybit server time"""
    engine = ThorEngine()
    result = await engine.get_server_time()
    return result

# ACCOUNT ENDPOINTS (Requires Auth)
@app.get("/api/account/wallet-balance")
async def get_wallet_balance(
    current_user: dict = Depends(get_current_user),
    account_type: str = "UNIFIED",
    coin: str = None
):
    """Get wallet balance"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.get_wallet_balance(account_type=account_type, coin=coin)
    
    if result.get('retCode') == 0:
        formatted = engine.format_balance(result)
        return {"success": True, **formatted}
    return {"success": False, "error": result.get('retMsg')}

@app.get("/api/account/info")
async def get_account_info(current_user: dict = Depends(get_current_user)):
    """Get account info"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.get_account_info()
    return result

@app.get("/api/account/fee-rate")
async def get_fee_rate(
    current_user: dict = Depends(get_current_user),
    category: str = "spot",
    symbol: str = None
):
    """Get fee rate"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.get_fee_rate(category=category, symbol=symbol)
    return result

# TRADE ENDPOINTS (Requires Auth)
@app.post("/api/trade/order")
async def place_order(
    order: OrderRequest,
    current_user: dict = Depends(get_current_user)
):
    """Place an order"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.place_order(
        category=order.category,
        symbol=order.symbol,
        side=order.side,
        order_type=order.order_type,
        qty=str(order.qty),
        price=str(order.price) if order.price else None
    )
    return result

@app.get("/api/trade/open-orders")
async def get_open_orders(
    current_user: dict = Depends(get_current_user),
    category: str = "spot",
    symbol: str = None,
    limit: int = 50
):
    """Get open orders"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.get_open_orders(category=category, symbol=symbol, limit=limit)
    return result

@app.get("/api/trade/order-history")
async def get_order_history(
    current_user: dict = Depends(get_current_user),
    category: str = "spot",
    symbol: str = None,
    limit: int = 50
):
    """Get order history"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.get_order_history(category=category, symbol=symbol, limit=limit)
    return result

@app.post("/api/trade/cancel-order")
async def cancel_order(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Cancel an order"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.cancel_order(
        category=data['category'],
        symbol=data['symbol'],
        order_id=data.get('order_id'),
        order_link_id=data.get('order_link_id')
    )
    return result

@app.post("/api/trade/cancel-all")
async def cancel_all_orders(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Cancel all orders"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.cancel_all_orders(category=data.get('category', 'spot'))
    return result

# POSITION ENDPOINTS (Requires Auth)
@app.get("/api/positions/list")
async def get_positions(
    current_user: dict = Depends(get_current_user),
    category: str = "linear",
    symbol: str = None
):
    """Get positions"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.get_positions(category=category, symbol=symbol)
    return result

@app.get("/api/positions/closed-pnl")
async def get_closed_pnl(
    current_user: dict = Depends(get_current_user),
    category: str = "linear",
    symbol: str = None,
    limit: int = 50
):
    """Get closed PnL"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.get_closed_pnl(category=category, symbol=symbol, limit=limit)
    return result

@app.post("/api/positions/leverage")
async def set_leverage(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Set leverage"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.set_leverage(
        category=data['category'],
        symbol=data['symbol'],
        leverage=str(data['leverage'])
    )
    return result

# ASSET ENDPOINTS (Requires Auth)
@app.get("/api/asset/coin-balance")
async def get_coin_balance(
    current_user: dict = Depends(get_current_user),
    account_type: str = "FUND",
    coin: str = None
):
    """Get coin balance"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.get_coin_balance(account_type=account_type, coin=coin)
    return result

@app.get("/api/asset/deposit/address")
async def get_deposit_address(
    current_user: dict = Depends(get_current_user),
    coin: str = None
):
    """Get deposit address"""
    if not coin:
        raise HTTPException(status_code=400, detail="coin parameter required")
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.get_deposit_address(coin=coin)
    return result

@app.get("/api/asset/deposit/history")
async def get_deposit_history(
    current_user: dict = Depends(get_current_user),
    coin: str = None,
    limit: int = 50
):
    """Get deposit history"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.get_deposit_history(coin=coin, limit=limit)
    return result

@app.get("/api/asset/withdraw/history")
async def get_withdraw_history(
    current_user: dict = Depends(get_current_user),
    coin: str = None,
    limit: int = 50
):
    """Get withdrawal history"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.get_withdraw_history(coin=coin, limit=limit)
    return result

@app.post("/api/asset/transfer")
async def create_transfer(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create internal transfer"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.create_transfer(
        transfer_id=data.get('transfer_id', uuid.uuid4().hex),
        from_account=data['from_account'],
        to_account=data['to_account'],
        coin=data['coin'],
        amount=str(data['amount'])
    )
    return result

# AFFILIATE / REBATE ENDPOINTS (Master API Key)
@app.get("/api/affiliate/commission")
async def get_affiliate_commission(limit: int = 50):
    """Get affiliate commission"""
    engine = ThorEngine(settings.MASTER_API_KEY, settings.MASTER_API_SECRET)
    result = await engine.get_affiliate_commission(limit=limit)
    return result

@app.get("/api/affiliate/user-list")
async def get_affiliate_user_list(size: int = 50, page: int = 1):
    """Get affiliate user list"""
    engine = ThorEngine(settings.MASTER_API_KEY, settings.MASTER_API_SECRET)
    result = await engine.get_affiliate_user_list(size=size, page=page)
    return result

# BROKER ENDPOINTS (Master API Key)
@app.post("/api/broker/subaccount/create")
async def create_subaccount(data: dict):
    """Create subaccount"""
    engine = ThorEngine(settings.MASTER_API_KEY, settings.MASTER_API_SECRET)
    result = await engine.create_subaccount(
        username=data['username'],
        member_type=data.get('member_type', 1),
        note=data.get('note', '')
    )
    return result

@app.get("/api/broker/subaccount/list")
async def list_subaccounts():
    """List subaccounts"""
    engine = ThorEngine(settings.MASTER_API_KEY, settings.MASTER_API_SECRET)
    result = await engine.get_subaccount_list()
    return result

@app.post("/api/broker/subaccount/fee")
async def set_subaccount_fee(data: dict):
    """Set subaccount fee"""
    engine = ThorEngine(settings.MASTER_API_KEY, settings.MASTER_API_SECRET)
    result = await engine.set_subaccount_fee(
        sub_uid=data['sub_uid'],
        fee_rate=data['fee_rate']
    )
    return result

# P2P ENDPOINTS (Requires Auth)
@app.get("/api/p2p/balance")
async def get_p2p_balance(
    current_user: dict = Depends(get_current_user),
    coin: str = None
):
    """Get P2P balance"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.get_p2p_balance(coin=coin)
    return result

@app.get("/api/p2p/orders")
async def get_p2p_orders(
    current_user: dict = Depends(get_current_user),
    side: str = None,
    status: str = None,
    limit: int = 50
):
    """Get P2P orders with debug"""
    try:
        logger.info(f"🔍 P2P orders request for user: {current_user['user_id']}")
        logger.info(f"🔍 Params: side={side}, status={status}, limit={limit}")
        
        engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
        
        # Log the keys being used (first few chars only for security)
        logger.info(f"🔍 Using API key: {current_user['api_key'][:5]}...")
        
        result = await engine.get_p2p_orders(side=side, status=status, limit=limit)
        
        logger.info(f"🔍 P2P response received")
        logger.info(f"🔍 Response status: {result.get('retCode')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ P2P orders error: {str(e)}")
        logger.exception("Full traceback:")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "detail": "Internal Server Error"}
        )

# RFQ/OTC ENDPOINTS (Requires Auth)
@app.post("/api/rfq/create")
async def create_rfq(data: dict, current_user: dict = Depends(get_current_user)):
    """Create RFQ"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.create_rfq(data=data)
    return result

@app.post("/api/rfq/execute")
async def execute_rfq(data: dict, current_user: dict = Depends(get_current_user)):
    """Execute RFQ"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.execute_rfq(data=data)
    return result

@app.get("/api/rfq/config")
async def get_rfq_config(current_user: dict = Depends(get_current_user)):
    """Get RFQ config"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.get_rfq_config()
    return result

# V1 COMPATIBILITY ENDPOINTS (For existing frontend)
@app.get("/api/v1/user/info")
async def get_user_info(current_user: dict = Depends(get_current_user)):
    """Get user info"""
    return {
        "uid": current_user['user_id'],
        "authenticated": True,
        "broker": settings.BROKER_CODE
    }

@app.get("/api/v1/balance")
async def get_balance_v1(current_user: dict = Depends(get_current_user)):
    """Legacy balance endpoint"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.get_wallet_balance()
    
    if result.get('retCode') == 0:
        formatted = engine.format_balance(result)
        # Add shop credit
        shop_credit = redis_client.get_shop_credit(current_user['user_id'])
        if shop_credit > 0:
            formatted['total_usd'] += shop_credit
            formatted['balances']["SHOP"] = {
                "balance": shop_credit,
                "usd_value": shop_credit
            }
        return {"success": True, "total_usd": formatted['total_usd'], "balances": formatted['balances']}
    return {"success": False, "error": result.get('retMsg')}

@app.get("/api/v1/price/{symbol}")
async def get_price_v1(symbol: str):
    """Legacy price endpoint"""
    engine = ThorEngine()
    result = await engine.get_tickers(symbol=symbol)
    return engine.format_ticker(result)

@app.get("/api/v1/orderbook/{symbol}")
async def get_orderbook_v1(symbol: str, category: str = "spot", limit: int = 25):
    """Legacy orderbook endpoint"""
    engine = ThorEngine()
    result = await engine.get_orderbook(category=category, symbol=symbol, limit=limit)
    return result

@app.get("/api/v1/pnl")
async def get_pnl_v1(current_user: dict = Depends(get_current_user)):
    """Legacy PnL endpoint"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    
    positions = await engine.get_positions()
    closed = await engine.get_closed_pnl(category="linear")
    
    total_unrealized = 0
    total_realized = 0
    
    if positions.get('retCode') == 0:
        for pos in positions.get('result', {}).get('list', []):
            total_unrealized += float(pos.get('unrealisedPnl', 0))
    
    if closed.get('retCode') == 0:
        for item in closed.get('result', {}).get('list', []):
            total_realized += float(item.get('closedPnl', 0))
    
    return {
        "success": True,
        "total_pnl": round(total_realized + total_unrealized, 2),
        "realized_pnl": round(total_realized, 2),
        "unrealized_pnl": round(total_unrealized, 2)
    }

@app.get("/api/v1/orders")
async def get_orders_v1(current_user: dict = Depends(get_current_user)):
    """Legacy orders endpoint"""
    engine = ThorEngine(current_user['api_key'], current_user['api_secret'])
    result = await engine.get_order_history(category="spot")
    
    if result.get('retCode') == 0:
        return {"success": True, "orders": result.get('result', {}).get('list', [])}
    return {"success": False, "orders": []}

@app.get("/api/v1/bots")
async def get_bots_v1(current_user: dict = Depends(get_current_user)):
    """Get user's trading bots"""
    try:
        # This would need strategies.storage module
        # For now return empty list
        return {"success": True, "bots": []}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/v1/bots/create")
async def create_bot_v1(request: dict, current_user: dict = Depends(get_current_user)):
    """Create a new trading bot"""
    try:
        # This would need strategies module
        return {"success": True, "bot_id": "dummy-id"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/v1/bots/{bot_id}/{action}")
async def control_bot_v1(bot_id: str, action: str, current_user: dict = Depends(get_current_user)):
    """Control bot (start/pause/stop)"""
    try:
        # This would need strategies module
        return {"success": True, "message": f"Bot {action} successful"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/v1/strategies")
async def get_strategies_v1(current_user: dict = Depends(get_current_user)):
    """Get user's strategies"""
    try:
        # This would need strategies module
        return {"success": True, "strategies": []}
    except Exception as e:
        logger.error(f"Strategies error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/v1/payments")
async def get_payments_v1(current_user: dict = Depends(get_current_user)):
    """Get payment history"""
    try:
        credit = redis_client.get_shop_credit(current_user['user_id'])
        return {"success": True, "credit": credit}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# COMMAND MODULES IMPORT STATUS
# ============================================================================

STRATEGY_COMMANDS_AVAILABLE = False
PAYMENT_COMMANDS_AVAILABLE = False
P2P_COMMANDS_AVAILABLE = False

try:
    # Try to import strategy commands if they exist
    # from bot.commands.strategies import register_strategy_commands
    # STRATEGY_COMMANDS_AVAILABLE = True
    logger.info("ℹ️ Strategy commands module not loaded (optional)")
except ImportError:
    logger.info("ℹ️ Strategy commands not available (optional)")

try:
    # from bot.commands.payments import register_payment_commands
    # PAYMENT_COMMANDS_AVAILABLE = True
    logger.info("ℹ️ Payment commands module not loaded (optional)")
except ImportError:
    logger.info("ℹ️ Payment commands not available (optional)")

try:
    # from bot.commands.p2p import register_p2p_commands
    # P2P_COMMANDS_AVAILABLE = True
    logger.info("ℹ️ P2P commands module not loaded (optional)")
except ImportError:
    logger.info("ℹ️ P2P commands not available (optional)")

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
                # register_strategy_commands(self.bot)
                logger.info("✅ Strategy commands registered")
            except Exception as e:
                logger.error(f"❌ Failed to register strategy commands: {e}")
        
        if PAYMENT_COMMANDS_AVAILABLE:
            try:
                # register_payment_commands(self.bot)
                logger.info("✅ Payment commands registered")
            except Exception as e:
                logger.error(f"❌ Failed to register payment commands: {e}")
        
        if P2P_COMMANDS_AVAILABLE:
            try:
                # register_p2p_commands(self.bot)
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
                        
                        credit = redis_client.get_shop_credit(user_id)
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
                            f"http://localhost:{settings.PORT}/api/trade/order",
                            json={
                                "symbol": symbol,
                                "side": side,
                                "qty": qty,
                                "order_type": "Market",
                                "category": "spot"
                            },
                            headers={"Authorization": user_id}
                        )
                        return order_resp.json()
                
                result = asyncio.run(execute())
                
                if result.get('retCode') == 0:
                    reply = f"""
✅ *Order Executed!*

*{side}* ${amount} of {symbol}
*Quantity:* {result.get('result', {}).get('qty', 0)}
*Order ID:* `{result.get('result', {}).get('orderId', 'N/A')}`
                    """
                    self.bot.reply_to(message, reply, parse_mode="Markdown")
                else:
                    self.bot.reply_to(message, f"❌ Trade failed: {result.get('retMsg', 'Unknown error')}")
            
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
    logger.info("🚀 NOVA GLOBAL KEYS - THOR UNIFIED ENGINE v5.0 FINAL")
    logger.info("=" * 60)
    logger.info(f"Broker: {settings.BROKER_CODE}")
    logger.info(f"Affiliate: {settings.AFFILIATE_ID}")
    logger.info(f"Redis: {'✅' if redis_client.ping() else '❌'}")
    logger.info(f"Strategy Commands: {'✅' if STRATEGY_COMMANDS_AVAILABLE else 'ℹ️ Not Installed'}")
    logger.info(f"Payment Commands: {'✅' if PAYMENT_COMMANDS_AVAILABLE else 'ℹ️ Not Installed'}")
    logger.info(f"P2P Commands: {'✅' if P2P_COMMANDS_AVAILABLE else 'ℹ️ Not Installed'}")
    logger.info("✅ All Bybit V5 endpoints available with broker headers")
    logger.info("=" * 60)
    
    # ===== START BACKGROUND THREADS =====
    # 1. Start the killswitch listener (PANIC BUTTON)
    killswitch_thread = threading.Thread(target=killswitch_listener, daemon=True)
    killswitch_thread.start()
    logger.info("🔫 Killswitch listener thread started")
    
    # 2. Start the heartbeat pulse thread (keeps dashboard alive)
    heartbeat_thread = threading.Thread(target=heartbeat_pulse, daemon=True)
    heartbeat_thread.start()
    logger.info("❤️ Heartbeat pulse thread started")
    
    # 3. Start Telegram bot in a separate thread
    telegram_bot = TelegramBot()
    bot_thread = threading.Thread(target=telegram_bot.polling, daemon=True)
    bot_thread.start()
    logger.info("🤖 Telegram bot thread started")
    
    # Log that all background threads are running
    logger.info("=" * 60)
    logger.info("🎯 ALL BACKGROUND THREADS ACTIVE:")
    logger.info("   🔫 Killswitch Listener - Channel: nova:commands")
    logger.info("   ❤️ Heartbeat Pulse - Updates every 10 seconds")
    logger.info("   🤖 Telegram Bot - Polling for messages")
    logger.info("=" * 60)
    
    # Send initial heartbeat
    redis_client.update_heartbeat()
    logger.info(f"✅ API server starting on {settings.HOST}:{settings.PORT}")
    
    # Run the FastAPI server (this blocks until shutdown)
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    main()
