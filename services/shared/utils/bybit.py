import os  # <-- ADD THIS IF MISSING
import hmac
import hashlib
import time
import json
import logging
from typing import Dict, Optional
import httpx
logger = logging.getLogger("nova-thor")

class ThorEngine:
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.broker_code = os.getenv("BROKER_CODE", "Kr000820")
        self.affiliate_id = os.getenv("AFFILIATE_ID", "127146")
        self.recv_window = "20000"
        
        if os.getenv("USE_TESTNET", "false").lower() == "true":
            self.base_url = "https://api-testnet.bybit.com"
        else:
            self.base_url = "https://api.bybit.id"
        
        self.client = httpx.AsyncClient(timeout=30.0)
    
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
    
    # Market endpoints
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
    
    # Account endpoints
    async def get_wallet_balance(self, account_type: str = "UNIFIED", coin: str = None):
        params = {"accountType": account_type}
        if coin:
            params["coin"] = coin
        return await self._request("GET", "/v5/account/wallet-balance", params=params)
    
    # Trade endpoints
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
    
    # P2P endpoints
    async def get_p2p_balance(self, coin: str = None):
        params = {}
        if coin:
            params["coin"] = coin
        return await self._request("GET", "/v5/p2p/balance", params=params)
    
    async def get_p2p_orders(self, side: str = None, status: str = None, limit: int = 50):
        params = {"limit": limit}
        if side:
            params["side"] = side
        if status:
            params["status"] = status
        return await self._request("GET", "/v5/p2p/order/list", params=params)
    
    # Broker endpoints
    async def create_subaccount(self, username: str, member_type: int = 1, note: str = ""):
        data = {"username": username, "memberType": member_type, "note": note}
        return await self._request("POST", "/v5/broker/create-sub-member", data=data)
    
    async def get_subaccount_list(self):
        return await self._request("GET", "/v5/broker/sub-member-list")
    
    async def close(self):
        await self.client.aclose()
