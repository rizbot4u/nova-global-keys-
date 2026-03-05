"""
OKX Exchange Implementation
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

logger = logging.getLogger("exchange-okx")

class OkxExchange(BaseExchange):
    """OKX exchange implementation"""
    
    def __init__(self, api_key: str, api_secret: str, passphrase: str = None,
                 testnet: bool = False):
        super().__init__(api_key, api_secret, testnet)
        self.passphrase = passphrase or os.getenv("OKX_PASSPHRASE", "")
        
        if testnet:
            self.base_url = "https://www.okx.com"
        else:
            self.base_url = "https://www.okx.com"
        
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
        
        timestamp = str(time.time())
        body = ""
        if data:
            body = json.dumps(data)
        
        signature = self._generate_signature(timestamp, method, endpoint, body)
        
        headers = {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json"
        }
        
        try:
            if method == "GET" and params:
                query = '&'.join([f"{k}={v}" for k, v in params.items()])
                url = f"{url}?{query}"
            
            if method == "GET":
                response = await self.client.get(url, headers=headers)
            else:
                response = await self.client.post(url, headers=headers, json=data)
            
            result = response.json()
            
            if result.get('code') != '0':
                logger.error(f"OKX error: {result}")
                return {"success": False, "error": result.get('msg', 'Unknown error')}
            
            return {"success": True, "data": result.get('data')}
        except Exception as e:
            logger.error(f"OKX request error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_balance(self, account_type: str = "SPOT") -> Dict:
        return await self._request("GET", "/api/v5/account/balance")
    
    async def get_ticker(self, symbol: str) -> Dict:
        return await self._request("GET", "/api/v5/market/ticker", 
                                   params={"instId": symbol})
    
    async def place_order(self, symbol: str, side: str, order_type: str,
                         quantity: float, price: float = None) -> Dict:
        data = [{
            "instId": symbol,
            "tdMode": "cash",
            "side": side.lower(),
            "ordType": order_type.lower(),
            "sz": str(quantity)
        }]
        
        if price and order_type.lower() == "limit":
            data[0]["px"] = str(price)
        
        return await self._request("POST", "/api/v5/trade/order", data=data)
    
    async def cancel_order(self, symbol: str, order_id: str) -> Dict:
        data = [{
            "instId": symbol,
            "ordId": order_id
        }]
        return await self._request("POST", "/api/v5/trade/cancel-order", data=data)
    
    async def get_open_orders(self, symbol: str = None) -> List:
        params = {}
        if symbol:
            params["instId"] = symbol
        result = await self._request("GET", "/api/v5/trade/orders-pending", params=params)
        if result.get('success'):
            return result.get('data', [])
        return []
    
    async def get_order_history(self, symbol: str = None, limit: int = 50) -> List:
        params = {"limit": limit}
        if symbol:
            params["instId"] = symbol
        result = await self._request("GET", "/api/v5/trade/orders-history", params=params)
        if result.get('success'):
            return result.get('data', [])
        return []
    
    async def get_deposit_address(self, coin: str) -> Dict:
        params = {"ccy": coin}
        return await self._request("GET", "/api/v5/asset/deposit-address", params=params)
    
    async def withdraw(self, coin: str, address: str, amount: float, 
                       network: str = None) -> Dict:
        data = [{
            "ccy": coin,
            "toAddr": address,
            "amt": str(amount)
        }]
        if network:
            data[0]["chain"] = network
        return await self._request("POST", "/api/v5/asset/withdrawal", data=data)
    
    async def close(self):
        await self.client.aclose()
    
    def format_balance(self, balance_data: Dict) -> Dict:
        try:
            balances = {}
            total_usd = 0
            assets = []
            
            if balance_data.get('success') and 'data' in balance_data:
                data = balance_data['data']
                if data and len(data) > 0:
                    for detail in data[0].get('details', []):
                        coin_name = detail['ccy']
                        cash_bal = float(detail.get('cashBal', 0))
                        avail_bal = float(detail.get('availBal', 0))
                        eq_usd = float(detail.get('eqUsd', 0))
                        
                        if cash_bal > 0 or eq_usd > 0:
                            balances[coin_name] = {
                                "balance": cash_bal,
                                "available": avail_bal,
                                "usd_value": eq_usd
                            }
                            total_usd += eq_usd
                            assets.append({
                                "coin": coin_name,
                                "balance": cash_bal,
                                "available": avail_bal,
                                "usd_value": eq_usd
                            })
            
            return {
                "success": True,
                "balances": balances,
                "total_usd": total_usd,
                "assets": assets,
                "exchange": "okx"
            }
        except Exception as e:
            logger.error(f"Error formatting OKX balance: {e}")
            return {"success": False, "error": str(e), "exchange": "okx"}
