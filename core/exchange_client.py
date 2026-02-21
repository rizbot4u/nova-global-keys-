import httpx
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class ExchangeClient:
    def __init__(self, api_key: str = None, api_secret: str = None):
        # Fallback to Master keys if user keys aren't provided
        self.api_key = api_key or settings.MASTER_API_KEY
        self.api_secret = api_secret or settings.MASTER_API_SECRET
        self.proxy_url = "http://localhost:8082" 
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _proxy_request(self, method: str, endpoint: str, params: dict = None, data: dict = None):
        """Standardized Proxy Request"""
        url = f"{self.proxy_url}{endpoint}"
        headers = {
            "X-BAPI-API-KEY": self.api_key,
            "X-BAPI-API-SECRET": self.api_secret, # Proxy uses this to sign
            "Content-Type": "application/json"
        }
        
        try:
            if method == "GET":
                r = await self.client.get(url, headers=headers, params=params)
            else:
                r = await self.client.post(url, headers=headers, json=data)
            return r.json()
        except Exception as e:
            return {"retCode": -1, "retMsg": f"Proxy Error: {str(e)}"}

    async def get_ticker(self, symbol: str):
        return await self._proxy_request("GET", "/v5/market/tickers", params={"category": "spot", "symbol": symbol})

    async def place_market_order(self, symbol: str, side: str, qty: str):
        payload = {
            "category": "spot",
            "symbol": symbol,
            "side": side,
            "orderType": "Market",
            "qty": qty,
            "brokerId": settings.BROKER_CODE
        }
        return await self._proxy_request("POST", "/v5/order/create", data=payload)

