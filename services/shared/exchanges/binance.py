"""
Binance Exchange Implementation
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

logger = logging.getLogger("exchange-binance")

class BinanceExchange(BaseExchange):
    """Binance exchange implementation"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        super().__init__(api_key, api_secret, testnet)
        
        if testnet:
            self.base_url = "https://testnet.binance.vision"
        else:
            self.base_url = "https://api.binance.com"
        
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _generate_signature(self, query_string: str) -> str:
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def _request(self, method: str, endpoint: str, 
                       params: dict = None, signed: bool = False) -> Dict:
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        if signed:
            timestamp = int(time.time() * 1000)
            if params is None:
                params = {}
            params['timestamp'] = timestamp
            
            query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
            params['signature'] = self._generate_signature(query_string)
        
        try:
            if method == "GET":
                response = await self.client.get(url, headers=headers, params=params)
            else:
                response = await self.client.post(url, headers=headers, json=params)
            
            result = response.json()
            
            if 'code' in result and result['code'] < 0:
                logger.error(f"Binance error: {result}")
                return {"success": False, "error": result.get('msg', 'Unknown error')}
            
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Binance request error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_balance(self, account_type: str = "SPOT") -> Dict:
        result = await self._request("GET", "/api/v3/account", signed=True)
        return result
    
    async def get_ticker(self, symbol: str) -> Dict:
        params = {"symbol": symbol}
        return await self._request("GET", "/api/v3/ticker/24hr", params=params)
    
    async def place_order(self, symbol: str, side: str, order_type: str,
                         quantity: float, price: float = None) -> Dict:
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": quantity
        }
        
        if price and order_type.upper() == "LIMIT":
            params["price"] = price
            params["timeInForce"] = "GTC"
        
        return await self._request("POST", "/api/v3/order", params=params, signed=True)
    
    async def cancel_order(self, symbol: str, order_id: str) -> Dict:
        params = {
            "symbol": symbol,
            "orderId": order_id
        }
        return await self._request("DELETE", "/api/v3/order", params=params, signed=True)
    
    async def get_open_orders(self, symbol: str = None) -> List:
        params = {}
        if symbol:
            params["symbol"] = symbol
        result = await self._request("GET", "/api/v3/openOrders", params=params, signed=True)
        if result.get('success'):
            return result.get('data', [])
        return []
    
    async def get_order_history(self, symbol: str = None, limit: int = 50) -> List:
        params = {"limit": limit}
        if symbol:
            params["symbol"] = symbol
        result = await self._request("GET", "/api/v3/allOrders", params=params, signed=True)
        if result.get('success'):
            return result.get('data', [])
        return []
    
    async def get_deposit_address(self, coin: str) -> Dict:
        params = {"coin": coin}
        return await self._request("GET", "/sapi/v1/capital/deposit/address", 
                                   params=params, signed=True)
    
    async def withdraw(self, coin: str, address: str, amount: float, 
                       network: str = None) -> Dict:
        params = {
            "coin": coin,
            "address": address,
            "amount": amount
        }
        if network:
            params["network"] = network
        return await self._request("POST", "/sapi/v1/capital/withdraw/apply", 
                                   params=params, signed=True)
    
    async def close(self):
        await self.client.aclose()
    
    def format_balance(self, balance_data: Dict) -> Dict:
        try:
            balances = {}
            total_usd = 0
            assets = []
            
            if balance_data.get('success') and 'data' in balance_data:
                data = balance_data['data']
                for balance in data.get('balances', []):
                    coin_name = balance['asset']
                    free = float(balance['free'])
                    locked = float(balance['locked'])
                    total = free + locked
                    
                    if total > 0:
                        balances[coin_name] = {
                            "balance": total,
                            "free": free,
                            "locked": locked,
                            "usd_value": 0
                        }
                        assets.append({
                            "coin": coin_name,
                            "balance": total,
                            "free": free,
                            "locked": locked
                        })
            
            return {
                "success": True,
                "balances": balances,
                "total_usd": total_usd,
                "assets": assets,
                "exchange": "binance"
            }
        except Exception as e:
            logger.error(f"Error formatting Binance balance: {e}")
            return {"success": False, "error": str(e), "exchange": "binance"}
