"""NOVA Remittance Core Engine"""
import os
import json
import hmac
import hashlib
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("nova-remit")

class RemittanceEngine:
    """Core remittance processing engine"""
    
    def __init__(self):
        self.circle_api_key = os.getenv("CIRCLE_API_KEY")
        self.circle_url = "https://api.circle.com/v1"
        self.fbo_account_id = os.getenv("FBO_ACCOUNT_ID")
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def create_wallet(self, user_id: str, blockchain: str = "ETH") -> Dict:
        """Create a Circle wallet for user (functions like a bank account)"""
        try:
            response = await self.client.post(
                f"{self.circle_url}/wallets",
                headers={"Authorization": f"Bearer {self.circle_api_key}"},
                json={
                    "userId": user_id,
                    "blockchain": blockchain,
                    "type": "smart:circle"
                }
            )
            wallet = response.json()
            logger.info(f"✅ Created wallet for user {user_id}")
            return {"success": True, "wallet": wallet}
        except Exception as e:
            logger.error(f"❌ Wallet creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_cross_chain(self, sender_id: str, recipient_address: str, 
                               amount: float, source_chain: str, dest_chain: str) -> Dict:
        """Send USDC across different blockchains using CCTP"""
        try:
            # Atomic batch transaction = either all succeed or all fail
            response = await self.client.post(
                f"{self.circle_url}/transfers",
                headers={"Authorization": f"Bearer {self.circle_api_key}"},
                json={
                    "source": {"walletId": sender_id, "chain": source_chain},
                    "destination": {"address": recipient_address, "chain": dest_chain},
                    "amount": {"currency": "USD", "value": str(amount)},
                    "atomic": True
                }
            )
            tx = response.json()
            logger.info(f"✅ Cross-chain transfer: {amount} USDC")
            return {"success": True, "transaction": tx}
        except Exception as e:
            logger.error(f"❌ Transfer failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def batch_payout(self, recipients: List[Dict]) -> Dict:
        """Pay multiple people in one atomic transaction"""
        try:
            # Encode all transfers into one batch
            encoded_txs = []
            for r in recipients:
                tx = {
                    "address": r["address"],
                    "chain": r.get("chain", "ETH"),
                    "amount": r["amount"],
                    "currency": "USDC"
                }
                encoded_txs.append(tx)
            
            response = await self.client.post(
                f"{self.circle_url}/atomic-batch",
                headers={"Authorization": f"Bearer {self.circle_api_key}"},
                json={"transactions": encoded_txs}
            )
            result = response.json()
            logger.info(f"✅ Batch payout: {len(recipients)} recipients")
            return {"success": True, "batch_id": result.get("batchId")}
        except Exception as e:
            logger.error(f"❌ Batch payout failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_transaction_status(self, tx_id: str) -> Dict:
        """Track transaction in real-time"""
        try:
            response = await self.client.get(
                f"{self.circle_url}/transfers/{tx_id}",
                headers={"Authorization": f"Bearer {self.circle_api_key}"}
            )
            return {"success": True, "status": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
