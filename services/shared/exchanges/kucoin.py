"""
KuCoin Exchange Implementation
"""

import os
import hmac
import hashlib
import time
import base64
import json
import logging
from typing import Dict, List, Optional, Any
import httpx

from .base import BaseExchange

logger = logging.getLogger("exchange-kucoin")

class KucoinExchange(BaseExchange):
    """KuCoin exchange implementation"""
    
    def __init__(self, api_key: str, api_secret: str, passphrase: str = None, 
                 testnet: bool = False):
        super().__init__(api_key, api_secret, testnet)
        self.passphrase = passphrase or os.getenv("KUCOIN_PASSPHRASE", "")
        
        if testnet:
            self.base_url = "https://openapi-sandbox.kucoin.com"
        else:
            self.base_url = "https://api.kucoin.com"
        
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _generate_signature(self, timestamp: str, method: str, 
                            endpoint: str, body: str = "") -> str:
        str_to_sign = timestamp + method + endpoint + body
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            str_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()
    
    async def _request(self, method: str, endpoint: str, 
                       params: dict = None, data: dict = None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        
        timestamp = str(int(time.time() * 1000))
        body = ""
        if data:
            body = json.dumps(data)
        elif params and method == "GET":
            query = '&'.join([f"{k}={v}" for k, v in params.items()])
            endpoint = f"{endpoint}?{query}"
        
        signature = self._generate_signature(timestamp, method, endpoint, body)
        
        headers = {
            "KC-API-KEY": self.api_key,
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": timestamp,
            "KC-API-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json"
        }
        
        try:
            if method == "GET":
                response = await self.client.get(url, headers=headers)
            else:
                response = await self.client.post(url, headers=headers, json=data)
            
            result = response.json()
            
            if result.get('code') != '200000':
                logger.error(f"KuCoin error: {result}")
                return {"success": False, "error": result.get('msg', 'Unknown error')}
            
            return {"success": True, "data": result.get('data')}
        except Exception as e:
            logger.error(f"KuCoin request error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_balance(self, account_type: str = "SPOT") -> Dict:
        return await self._request("GET", "/api/v1/accounts")
    
    async def get_ticker(self, symbol: str) -> Dict:
        return await self._request("GET", f"/api/v1/market/orderbook/level1", 
                                   params={"symbol": symbol})
    
    async def place_order(self, symbol: str, side: str, order_type: str,
                         quantity: float, price: float = None) -> Dict:
        data = {
            "clientOid": str(int(time.time() * 1000)),
            "side": side.lower(),
            "symbol": symbol,
            "type": order_type.lower(),
            "size": str(quantity)
        }
        
        if price and order_type.lower() == "limit":
            data["price"] = str(price)
        
        return await self._request("POST", "/api/v1/orders", data=data)
    
    async def cancel_order(self, symbol: str, order_id: str) -> Dict:
        return await self._request("DELETE", f"/api/v1/orders/{order_id}")
    
    async def get_open_orders(self, symbol: str = None) -> List:
        params = {}
        if symbol:
            params["symbol"] = symbol
        result = await self._request("GET", "/api/v1/orders", params=params)
        if result.get('success'):
            return result.get('data', {}).get('items', [])
        return []
    
    async def get_order_history(self, symbol: str = None, limit: int = 50) -> List:
        params = {"pageSize": limit, "status": "done"}
        if symbol:
            params["symbol"] = symbol
        result = await self._request("GET", "/api/v1/orders", params=params)
        if result.get('success'):
            return result.get('data', {}).get('items', [])
        return []
    
    async def get_deposit_address(self, coin: str) -> Dict:
        params = {"currency": coin}
        return await self._request("GET", "/api/v1/deposit-addresses", params=params)
    
    async def withdraw(self, coin: str, address: str, amount: float, 
                       network: str = None) -> Dict:
        data = {
            "currency": coin,
            "address": address,
            "amount": str(amount)
        }
        if network:
            data["chain"] = network
        return await self._request("POST", "/api/v1/withdrawals", data=data)
    
    async def close(self):
        await self.client.aclose()
    
    def format_balance(self, balance_data: Dict) -> Dict:
        try:
            balances = {}
            total_usd = 0
            assets = []
            
            if balance_data.get('success') and 'data' in balance_data:
                for account in balance_data['data']:
                    coin_name = account['currency']
                    balance = float(account['balance'])
                    available = float(account['available'])
                    holds = float(account['holds'])
                    
                    if balance > 0:
                        balances[coin_name] = {
                            "balance": balance,
                            "available": available,
                            "holds": holds,
                            "usd_value": 0
                        }
                        assets.append({
                            "coin": coin_name,
                            "balance": balance,
                            "available": available,
                            "holds": holds
                        })
            
            return {
                "success": True,
                "balances": balances,
                "total_usd": total_usd,
                "assets": assets,
                "exchange": "kucoin"
            }
        except Exception as e:
            logger.error(f"Error formatting KuCoin balance: {e}")
            return {"success": False, "error": str(e), "exchange": "kucoin"}
