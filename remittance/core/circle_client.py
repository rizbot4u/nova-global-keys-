"""Circle API Client - Direct integration"""
import os
import httpx
import logging
from typing import Dict, Optional

logger = logging.getLogger("circle-client")

class CircleClient:
    """Direct Circle API client"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("CIRCLE_API_KEY")
        self.base_url = "https://api-sandbox.circle.com/v1"
        self.client = httpx.AsyncClient(timeout=30.0)
        
        if not self.api_key:
            logger.warning("⚠️ CIRCLE_API_KEY not set")
    
    async def create_wallet(self, user_id: str, blockchain: str = "ETH") -> Dict:
        """Create a new wallet for user"""
        try:
            response = await self.client.post(
                f"{self.base_url}/wallets",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "userId": user_id,
                    "blockchain": blockchain,
                    "description": f"NOVA User Wallet - {user_id}"
                }
            )
            return response.json()
        except Exception as e:
            logger.error(f"Wallet creation failed: {e}")
            return {"error": str(e)}
    
    async def transfer(self, from_wallet_id: str, to_address: str, amount: float,
                      currency: str = "USD", chain: str = "ETH") -> Dict:
        """Transfer funds"""
        try:
            response = await self.client.post(
                f"{self.base_url}/transfers",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "source": {"type": "wallet", "id": from_wallet_id},
                    "destination": {"type": "blockchain", "address": to_address},
                    "amount": {"currency": currency, "amount": str(amount)},
                    "chain": chain
                }
            )
            return response.json()
        except Exception as e:
            logger.error(f"Transfer failed: {e}")
            return {"error": str(e)}
    
    async def get_balance(self, wallet_id: str) -> float:
        """Get wallet balance"""
        try:
            response = await self.client.get(
                f"{self.base_url}/wallets/{wallet_id}",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            data = response.json()
            for balance in data.get("balances", []):
                if balance.get("currency") == "USD":
                    return float(balance.get("amount", 0))
            return 0.0
        except Exception as e:
            logger.error(f"Balance check failed: {e}")
            return 0.0
