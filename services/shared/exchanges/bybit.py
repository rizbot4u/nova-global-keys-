"""
Bybit Exchange Implementation
"""

import os
import hmac
import hashlib
import time
import json
import logging
from typing import Dict, List, Optional, Any
import httpx

from .base import BaseExchange

logger = logging.getLogger("exchange-bybit")

class BybitExchange(BaseExchange):
    """Bybit exchange implementation using ThorEngine"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        super().__init__(api_key, api_secret, testnet)
        self.broker_code = os.getenv("BROKER_CODE", "Kr000820")
        self.affiliate_id = os.getenv("AFFILIATE_ID", "127146")
        self.recv_window = "20000"
        
        if testnet:
            self.base_url = "https://api-testnet.bybit.com"
        else:
            self.base_url = "https://api.bybit.com"
        
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _generate_signature(self, timestamp: str, params: str = "", data: dict = None) -> str:
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
    
    async def _request(self, method: str, endpoint: str, 
                       params: dict = None, data: dict = None) -> Dict:
        timestamp = str(int(time.time() * 1000))
        query_string = ""
        if method == "GET" and params:
            sorted_params = sorted(params.items())
            query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        
        signature = self._generate_signature(timestamp, query_string, data)
        
        headers = {
            "X-BAPI-API-KEY": self.api_key,
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
            logger.error(f"Bybit request error: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    async def get_balance(self, account_type: str = "UNIFIED") -> Dict:
        params = {"accountType": account_type}
        return await self._request("GET", "/v5/account/wallet-balance", params=params)
    
    async def get_ticker(self, symbol: str) -> Dict:
        params = {"category": "spot", "symbol": symbol}
        return await self._request("GET", "/v5/market/tickers", params=params)
    
    async def place_order(self, symbol: str, side: str, order_type: str,
                         quantity: float, price: float = None) -> Dict:
        data = {
            "category": "spot",
            "symbol": symbol,
            "side": side.capitalize(),
            "orderType": order_type.capitalize(),
            "qty": str(quantity),
            "timeInForce": "GTC",
            "brokerId": self.broker_code
        }
        if price:
            data["price"] = str(price)
        return await self._request("POST", "/v5/order/create", data=data)
    
    async def cancel_order(self, symbol: str, order_id: str) -> Dict:
        data = {
            "category": "spot",
            "symbol": symbol,
            "orderId": order_id
        }
        return await self._request("POST", "/v5/order/cancel", data=data)
    
    async def get_open_orders(self, symbol: str = None) -> List:
        params = {"category": "spot", "limit": 50}
        if symbol:
            params["symbol"] = symbol
        result = await self._request("GET", "/v5/order/realtime", params=params)
        return result.get('result', {}).get('list', [])
    
    async def get_order_history(self, symbol: str = None, limit: int = 50) -> List:
        params = {"category": "spot", "limit": limit}
        if symbol:
            params["symbol"] = symbol
        result = await self._request("GET", "/v5/order/history", params=params)
        return result.get('result', {}).get('list', [])
    
    async def get_deposit_address(self, coin: str) -> Dict:
        params = {"coin": coin}
        return await self._request("GET", "/v5/asset/deposit/address", params=params)
    
    async def withdraw(self, coin: str, address: str, amount: float, 
                       network: str = None) -> Dict:
        data = {
            "coin": coin,
            "address": address,
            "amount": str(amount)
        }
        if network:
            data["network"] = network
        return await self._request("POST", "/v5/asset/withdraw/create", data=data)
    
    async def close(self):
        await self.client.aclose()
    
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
                "assets": assets,
                "exchange": "bybit"
            }
        except Exception as e:
            logger.error(f"Error formatting Bybit balance: {e}")
            return {"success": False, "error": str(e), "exchange": "bybit"}
