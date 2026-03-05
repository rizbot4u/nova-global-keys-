#!/bin/bash

# ============================================================================
# NOVA GLOBAL KEYS - MULTI-EXCHANGE SUPPORT SCRIPT
# Adds Binance, KuCoin, OKX support to existing microservices
# ============================================================================

set -e

echo "🚀 Adding Multi-Exchange Support to Nova Global Keys..."
echo "=========================================================="

# ============================================================================
# 1. CREATE EXCHANGE BASE CLASSES
# ============================================================================

echo "📝 Creating exchange base classes..."

mkdir -p /root/nova-global-keys-/services/shared/exchanges

cat > /root/nova-global-keys-/services/shared/exchanges/__init__.py << 'INITEOF'
from .base import BaseExchange
from .bybit import BybitExchange
from .binance import BinanceExchange
from .kucoin import KucoinExchange
from .okx import OkxExchange

EXCHANGE_MAP = {
    'bybit': BybitExchange,
    'binance': BinanceExchange,
    'kucoin': KucoinExchange,
    'okx': OkxExchange,
}

__all__ = ['BaseExchange', 'BybitExchange', 'BinanceExchange', 
           'KucoinExchange', 'OkxExchange', 'EXCHANGE_MAP']
INITEOF

# ============================================================================
# 2. CREATE BASE EXCHANGE INTERFACE
# ============================================================================

cat > /root/nova-global-keys-/services/shared/exchanges/base.py << 'BASEEOF'
"""
Base Exchange Interface - All exchanges must implement these methods
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger("exchange-base")

class BaseExchange(ABC):
    """Unified interface for all exchanges"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.name = self.__class__.__name__.replace('Exchange', '').lower()
    
    @abstractmethod
    async def get_balance(self, account_type: str = "UNIFIED") -> Dict:
        """Get wallet balance"""
        pass
    
    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict:
        """Get current price ticker"""
        pass
    
    @abstractmethod
    async def place_order(self, symbol: str, side: str, order_type: str, 
                          quantity: float, price: float = None) -> Dict:
        """Place an order"""
        pass
    
    @abstractmethod
    async def cancel_order(self, symbol: str, order_id: str) -> Dict:
        """Cancel an order"""
        pass
    
    @abstractmethod
    async def get_open_orders(self, symbol: str = None) -> List:
        """Get open orders"""
        pass
    
    @abstractmethod
    async def get_order_history(self, symbol: str = None, limit: int = 50) -> List:
        """Get order history"""
        pass
    
    @abstractmethod
    async def get_deposit_address(self, coin: str) -> Dict:
        """Get deposit address"""
        pass
    
    @abstractmethod
    async def withdraw(self, coin: str, address: str, amount: float, 
                       network: str = None) -> Dict:
        """Withdraw funds"""
        pass
    
    def format_balance(self, balance_data: Dict) -> Dict:
        """Standardize balance format across exchanges"""
        try:
            balances = {}
            total_usd = 0
            assets = []
            
            # This method should be overridden by each exchange
            # to convert their specific format to standard format
            
            return {
                "success": True,
                "balances": balances,
                "total_usd": total_usd,
                "assets": assets,
                "exchange": self.name
            }
        except Exception as e:
            logger.error(f"Error formatting balance: {e}")
            return {"success": False, "error": str(e), "exchange": self.name}
BASEEOF

# ============================================================================
# 3. CREATE BYBIT EXCHANGE
# ============================================================================

cat > /root/nova-global-keys-/services/shared/exchanges/bybit.py << 'BYBITEOF'
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
BYBITEOF

# ============================================================================
# 4. CREATE BINANCE EXCHANGE
# ============================================================================

cat > /root/nova-global-keys-/services/shared/exchanges/binance.py << 'BINANCEEOF'
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
BINANCEEOF

# ============================================================================
# 5. CREATE KUCOIN EXCHANGE
# ============================================================================

cat > /root/nova-global-keys-/services/shared/exchanges/kucoin.py << 'KUCOINEOF'
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
KUCOINEOF

# ============================================================================
# 6. CREATE OKX EXCHANGE
# ============================================================================

cat > /root/nova-global-keys-/services/shared/exchanges/okx.py << 'OKXEOF'
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
OKXEOF

# ============================================================================
# 7. UPDATE TRADE SERVICE
# ============================================================================

echo "📝 Updating Trade Service..."

cat > /root/nova-global-keys-/services/trade/main.py << 'TRADEEOF'
#!/usr/bin/env python3
"""
NOVA GLOBAL KEYS - Trade Service (Multi-Exchange)
"""

import os
import sys
import logging
import uuid
from datetime import datetime
from typing import Optional, List

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add shared modules to path
sys.path.append("/root/nova-global-keys-/services")
from shared.models.database import SessionLocal, ExchangeKey
from shared.exchanges import EXCHANGE_MAP
from shared.redis.client import redis_client

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trade-service")

app = FastAPI(title="Nova Trade Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

class OrderRequest(BaseModel):
    exchange: str
    symbol: str
    side: str
    order_type: str = "market"
    quantity: float
    price: Optional[float] = None

class OrderResponse(BaseModel):
    order_id: str
    exchange: str
    symbol: str
    side: str
    price: float
    quantity: float
    status: str

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    import jwt
    token = credentials.credentials
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), 
                            algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        db = SessionLocal()
        try:
            from shared.models.database import User
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
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_user_key(user_id: int, exchange_name: str):
    db = SessionLocal()
    try:
        key = db.query(ExchangeKey).filter(
            ExchangeKey.user_id == user_id,
            ExchangeKey.exchange_name == exchange_name,
            ExchangeKey.is_active == True
        ).first()
        
        if not key:
            raise HTTPException(
                status_code=404,
                detail=f"No active {exchange_name} keys found. Connect first at /keys/connect"
            )
        
        return key
    finally:
        db.close()

async def get_exchange(user_id: int, exchange_name: str, testnet: bool = False):
    key = await get_user_key(user_id, exchange_name)
    
    exchange_class = EXCHANGE_MAP.get(exchange_name)
    if not exchange_class:
        raise HTTPException(status_code=400, detail=f"Exchange {exchange_name} not supported")
    
    if exchange_name in ['kucoin', 'okx']:
        exchange = exchange_class(key.api_key, key.api_secret, testnet=testnet)
    else:
        exchange = exchange_class(key.api_key, key.api_secret, testnet=testnet)
    
    db = SessionLocal()
    try:
        key.last_used = datetime.now()
        db.commit()
    finally:
        db.close()
    
    return exchange

@app.get("/health")
async def health():
    return {
        "service": "trade",
        "status": "healthy",
        "redis": redis_client.ping(),
        "supported_exchanges": list(EXCHANGE_MAP.keys()),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/exchanges")
async def get_supported_exchanges():
    return {
        "exchanges": list(EXCHANGE_MAP.keys()),
        "count": len(EXCHANGE_MAP)
    }

@app.post("/order", response_model=OrderResponse)
async def place_order(
    order: OrderRequest,
    current_user: dict = Depends(get_current_user)
):
    exchange = await get_exchange(current_user["user_id"], order.exchange)
    
    try:
        result = await exchange.place_order(
            symbol=order.symbol,
            side=order.side,
            order_type=order.order_type,
            quantity=order.quantity,
            price=order.price
        )
        
        if result.get('success', False) or result.get('retCode') == 0:
            order_id = result.get('data', {}).get('orderId') or \
                      result.get('result', {}).get('orderId') or \
                      str(uuid.uuid4())
            
            return OrderResponse(
                order_id=order_id,
                exchange=order.exchange,
                symbol=order.symbol,
                side=order.side,
                price=order.price or 0,
                quantity=order.quantity,
                status="created"
            )
        else:
            error_msg = result.get('retMsg') or result.get('error') or "Order failed"
            raise HTTPException(status_code=400, detail=error_msg)
    finally:
        await exchange.close()

@app.get("/balance")
async def get_balance(
    exchange: str = Query(..., description="Exchange name"),
    current_user: dict = Depends(get_current_user)
):
    ex = await get_exchange(current_user["user_id"], exchange)
    
    try:
        result = await ex.get_balance()
        formatted = ex.format_balance(result)
        return formatted
    finally:
        await ex.close()

@app.get("/ticker/{symbol}")
async def get_ticker(
    exchange: str,
    symbol: str,
    current_user: dict = Depends(get_current_user)
):
    ex = await get_exchange(current_user["user_id"], exchange)
    
    try:
        result = await ex.get_ticker(symbol)
        return result
    finally:
        await ex.close()

@app.get("/orders/open")
async def get_open_orders(
    exchange: str,
    symbol: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    ex = await get_exchange(current_user["user_id"], exchange)
    
    try:
        orders = await ex.get_open_orders(symbol)
        return {"exchange": exchange, "orders": orders}
    finally:
        await ex.close()

@app.post("/order/cancel")
async def cancel_order(
    exchange: str,
    symbol: str,
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    ex = await get_exchange(current_user["user_id"], exchange)
    
    try:
        result = await ex.cancel_order(symbol, order_id)
        return {"success": True, "exchange": exchange, "result": result}
    finally:
        await ex.close()

@app.get("/deposit/address")
async def get_deposit_address(
    exchange: str,
    coin: str,
    current_user: dict = Depends(get_current_user)
):
    ex = await get_exchange(current_user["user_id"], exchange)
    
    try:
        result = await ex.get_deposit_address(coin)
        return result
    finally:
        await ex.close()

@app.post("/withdraw")
async def withdraw(
    exchange: str,
    coin: str,
    address: str,
    amount: float,
    network: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    ex = await get_exchange(current_user["user_id"], exchange)
    
    try:
        result = await ex.withdraw(coin, address, amount, network)
        return result
    finally:
        await ex.close()

if __name__ == "__main__":
    port = int(os.getenv("TRADE_SERVICE_PORT", 8004))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
TRADEEOF

# ============================================================================
# 8. UPDATE GATEWAY
# ============================================================================

echo "📝 Updating Gateway..."

# Create backup
cp /root/nova-global-keys-/services/gateway/main.py /root/nova-global-keys-/services/gateway/main.py.bak

# Append routes to gateway
cat >> /root/nova-global-keys-/services/gateway/main.py << 'GATEWAYEOF'

# ============================================================================
# MULTI-EXCHANGE ROUTES
# ============================================================================

@app.api_route("/api/bybit/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def bybit_proxy(request: Request, path: str):
    """Proxy to trade service with bybit exchange"""
    redis_client.client.incr("gateway:requests")
    
    query_params = dict(request.query_params)
    query_params['exchange'] = 'bybit'
    
    url = f"/{path}"
    if query_params:
        url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
    
    return await proxy_request(request, "trade", url)

@app.api_route("/api/binance/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def binance_proxy(request: Request, path: str):
    """Proxy to trade service with binance exchange"""
    redis_client.client.incr("gateway:requests")
    
    query_params = dict(request.query_params)
    query_params['exchange'] = 'binance'
    
    url = f"/{path}"
    if query_params:
        url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
    
    return await proxy_request(request, "trade", url)

@app.api_route("/api/kucoin/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def kucoin_proxy(request: Request, path: str):
    """Proxy to trade service with kucoin exchange"""
    redis_client.client.incr("gateway:requests")
    
    query_params = dict(request.query_params)
    query_params['exchange'] = 'kucoin'
    
    url = f"/{path}"
    if query_params:
        url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
    
    return await proxy_request(request, "trade", url)

@app.api_route("/api/okx/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def okx_proxy(request: Request, path: str):
    """Proxy to trade service with okx exchange"""
    redis_client.client.incr("gateway:requests")
    
    query_params = dict(request.query_params)
    query_params['exchange'] = 'okx'
    
    url = f"/{path}"
    if query_params:
        url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
    
    return await proxy_request(request, "trade", url)
GATEWAYEOF

# ============================================================================
# 9. CREATE INSTALLATION SCRIPT
# ============================================================================

cat > /root/nova-global-keys-/install_exchanges.sh << 'INSTALLEOF'
#!/bin/bash

echo "📦 Installing exchange dependencies..."

# Activate virtual environment
source /root/nova-global-keys-/venv/bin/activate

# Install exchange libraries
pip install httpx==0.25.1
pip install python-binance==1.0.19
pip install kucoin-python==2.2.0

echo "✅ Exchange libraries installed!"
INSTALLEOF

chmod +x /root/nova-global-keys-/install_exchanges.sh

# ============================================================================
# 10. CREATE TEST SCRIPT
# ============================================================================

cat > /root/nova-global-keys-/test_exchanges.sh << 'TESTEOF'
#!/bin/bash

echo "🧪 Testing Multi-Exchange Support"
echo "=================================="

echo ""
echo "📊 Supported Exchanges:"
curl -s http://127.0.0.1:8004/health | python3 -m json.tool

echo ""
echo ""
echo "📋 To test each exchange, you need to:"
echo "1. Connect your API keys via the web dashboard"
echo "2. Then run these commands with your JWT token:"
echo ""
echo "   # Bybit"
echo "   curl -H \"Authorization: Bearer YOUR_TOKEN\" http://127.0.0.1:8081/api/bybit/balance"
echo ""
echo "   # Binance"
echo "   curl -H \"Authorization: Bearer YOUR_TOKEN\" http://127.0.0.1:8081/api/binance/balance"
echo ""
echo "   # KuCoin"
echo "   curl -H \"Authorization: Bearer YOUR_TOKEN\" http://127.0.0.1:8081/api/kucoin/balance"
echo ""
echo "   # OKX"
echo "   curl -H \"Authorization: Bearer YOUR_TOKEN\" http://127.0.0.1:8081/api/okx/balance"
TESTEOF

chmod +x /root/nova-global-keys-/test_exchanges.sh

# ============================================================================
# 11. UPDATE ENVIRONMENT FILES
# ============================================================================

echo "📝 Updating environment files..."

cat >> /root/nova-global-keys-/config/env/trade.env << 'ENVEOF'

# Exchange-specific settings
KUCOIN_PASSPHRASE=your_kucoin_api_passphrase_here
OKX_PASSPHRASE=your_okx_api_passphrase_here
ENVEOF

# ============================================================================
# 12. RESTART SERVICES
# ============================================================================

echo "🔄 Restarting services..."

# Stop trade service
pm2 stop nova-trade
pm2 delete nova-trade

# Start trade service with new code
cd /root/nova-global-keys-/services
pm2 start trade/main.py --name nova-trade --interpreter python3

# Restart gateway
pm2 restart nova-gateway

# Wait for services
sleep 5

# ============================================================================
# 13. FINAL MESSAGE
# ============================================================================

echo ""
echo "🎉 MULTI-EXCHANGE SUPPORT ADDED SUCCESSFULLY!"
echo "=============================================="
echo ""
echo "✅ Supported exchanges now:"
echo "   - Bybit (already working)"
echo "   - Binance (added)"
echo "   - KuCoin (added)"
echo "   - OKX (added)"
echo ""
echo "📁 Files created in /services/shared/exchanges/:"
echo "   - base.py"
echo "   - bybit.py"
echo "   - binance.py"
echo "   - kucoin.py"
echo "   - okx.py"
echo "   - __init__.py"
echo ""
echo "📦 To install exchange libraries:"
echo "   ./install_exchanges.sh"
echo ""
echo "🧪 To test:"
echo "   ./test_exchanges.sh"
echo ""
echo "🔌 New API endpoints available:"
echo "   - /api/bybit/*    → Bybit operations"
echo "   - /api/binance/*  → Binance operations"
echo "   - /api/kucoin/*   → KuCoin operations"
echo "   - /api/okx/*      → OKX operations"
echo ""
echo "🚀 All exchanges now use the SAME interface!"
echo "   Same code works for all exchanges!"
echo ""
echo "🎯 Next steps:"
echo "   1. Run: ./install_exchanges.sh"
echo "   2. Edit .env files with exchange passphrases:"
echo "      nano /root/nova-global-keys-/config/env/trade.env"
echo "   3. Test with: ./test_exchanges.sh"
echo "   4. Connect API keys via web dashboard"
echo ""
echo "✨ Your system now supports 4 major exchanges!"
echo ""
echo "📊 Current trade service status:"
pm2 status | grep trade
