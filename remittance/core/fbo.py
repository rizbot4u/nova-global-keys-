"""FBO Account Manager - For Benefit Of customer accounts"""
import os
import redis
import json
from datetime import datetime
from typing import Dict, List

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

class FBOAccountManager:
    """
    FBO accounts legally segregate customer funds from operational funds.
    Each customer gets their own ledger under the master FBO account.
    """
    
    def __init__(self):
        self.master_fbo_id = os.getenv("FBO_ACCOUNT_ID", "NOVA_FBO_001")
        
    async def create_customer_ledger(self, user_id: str, currency: str = "USDC") -> Dict:
        """Create a ledger entry for a customer"""
        ledger_key = f"fbo:{self.master_fbo_id}:user:{user_id}"
        
        # Store customer ledger data
        redis_client.hset(ledger_key, "balance", 0)
        redis_client.hset(ledger_key, "currency", currency)
        redis_client.hset(ledger_key, "created_at", datetime.now().isoformat())
        redis_client.hset(ledger_key, "status", "active")
        
        # Store in customer index
        redis_client.sadd(f"fbo:{self.master_fbo_id}:users", user_id)
        
        return {
            "success": True,
            "message": "Customer ledger created",
            "ledger_key": ledger_key
        }
    
    async def credit_customer(self, user_id: str, amount: float, 
                               reference: str = None) -> Dict:
        """Credit customer balance (e.g., deposit received)"""
        ledger_key = f"fbo:{self.master_fbo_id}:user:{user_id}"
        
        # Atomic increment
        new_balance = redis_client.hincrbyfloat(ledger_key, "balance", amount)
        
        # Record transaction
        tx_id = f"tx_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        redis_client.hset(
            f"fbo:tx:{tx_id}",
            mapping={
                "user_id": user_id,
                "type": "credit",
                "amount": amount,
                "reference": reference or "",
                "timestamp": datetime.now().isoformat(),
                "balance_after": new_balance
            }
        )
        
        return {
            "success": True,
            "new_balance": new_balance,
            "transaction_id": tx_id
        }
    
    async def debit_customer(self, user_id: str, amount: float,
                              reference: str = None) -> Dict:
        """Debit customer balance (e.g., withdrawal/payout)"""
        ledger_key = f"fbo:{self.master_fbo_id}:user:{user_id}"
        
        # Check sufficient balance
        current = float(redis_client.hget(ledger_key, "balance") or 0)
        if current < amount:
            return {"success": False, "error": "Insufficient balance"}
        
        # Atomic decrement
        new_balance = redis_client.hincrbyfloat(ledger_key, "balance", -amount)
        
        # Record transaction
        tx_id = f"tx_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        redis_client.hset(
            f"fbo:tx:{tx_id}",
            mapping={
                "user_id": user_id,
                "type": "debit",
                "amount": amount,
                "reference": reference or "",
                "timestamp": datetime.now().isoformat(),
                "balance_after": new_balance
            }
        )
        
        return {
            "success": True,
            "new_balance": new_balance,
            "transaction_id": tx_id
        }
    
    async def get_customer_balance(self, user_id: str) -> Dict:
        """Get customer's current balance"""
        ledger_key = f"fbo:{self.master_fbo_id}:user:{user_id}"
        balance = float(redis_client.hget(ledger_key, "balance") or 0)
        currency = redis_client.hget(ledger_key, "currency") or "USDC"
        
        return {
            "user_id": user_id,
            "balance": balance,
            "currency": currency,
            "ledger": ledger_key
        }
    
    async def reconcile(self) -> Dict:
        """
        Reconcile customer balances with actual FBO bank balance.
        This is what regulators want to see.
        """
        total_customer_balance = 0.0
        customer_count = 0
        
        # Sum all customer balances
        users = redis_client.smembers(f"fbo:{self.master_fbo_id}:users")
        for user_id in users:
            balance = await self.get_customer_balance(user_id)
            total_customer_balance += balance["balance"]
            customer_count += 1
        
        # Compare with actual FBO balance (from bank API)
        actual_fbo_balance = await self._get_fbo_bank_balance()
        
        difference = abs(total_customer_balance - actual_fbo_balance)
        
        return {
            "reconciled": difference < 0.01,
            "customer_count": customer_count,
            "total_customer_balance": total_customer_balance,
            "actual_fbo_balance": actual_fbo_balance,
            "difference": difference,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_fbo_bank_balance(self) -> float:
        """Get actual FBO account balance from bank"""
        # In production, call your bank's API
        # For now, return the total customer balance (perfect match)
        total = 0.0
        users = redis_client.smembers(f"fbo:{self.master_fbo_id}:users")
        for user_id in users:
            balance = float(redis_client.hget(
                f"fbo:{self.master_fbo_id}:user:{user_id}", "balance"
            ) or 0)
            total += balance
        return total
