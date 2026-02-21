import hmac
import hashlib
import time
import json
import logging
import asyncio
import httpx
from typing import Optional, Dict, Any
from config.settings import settings

logger = logging.getLogger(__name__)

class NovaBrokerEngine:
    def __init__(self, use_testnet: bool = False):
        self.client_id = settings.CLIENT_ID
        self.client_secret = settings.CLIENT_SECRET
        self.broker_code = settings.BROKER_CODE
        self.recv_window = "20000"

        # Indonesia Endpoint Logic
        if use_testnet:
            self.api_url = "https://api-testnet.bybit.com"
        else:
            # Primary for Indonesia. Fallback to .com if needed in _request
            self.api_url = "https://api.bybit.id" 

        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"✅ Broker Engine Initialized: {self.broker_code} on {self.api_url}")

    def _generate_signature(self, api_key: str, api_secret: str, timestamp: str, params: str = "") -> str:
        """Universal V5 Signature Generator"""
        sign_str = f"{timestamp}{api_key}{self.recv_window}{params}"
        return hmac.new(
            api_secret.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    async def user_get_balance(self, api_key: str, api_secret: str) -> Dict:
        """Fetch balance using User's Oauth Keys"""
        timestamp = str(int(time.time() * 1000))
        params = "accountType=UNIFIED"
        signature = self._generate_signature(api_key, api_secret, timestamp, params)
        
        headers = {
            "X-BAPI-API-KEY": api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-SIGN": signature,
            "X-BAPI-RECV-WINDOW": self.recv_window,
            "Content-Type": "application/json"
        }
        
        try:
            r = await self.client.get(
                f"{self.api_url}/v5/account/wallet-balance?{params}", 
                headers=headers
            )
            return r.json()
        except Exception as e:
            logger.error(f"Balance request failed: {e}")
            return {"retCode": -1, "retMsg": str(e)}

    async def close(self):
        await self.client.aclose()

