"""NOVA Compliance Engine - KYC/AML built from day one"""
import os
import json
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

class ComplianceEngine:
    """
    Built into your app from day one, not added later.
    Handles KYC verification, AML screening, and transaction monitoring.
    """
    
    def __init__(self):
        self.sanctions_list = self._load_sanctions_list()
        self.risk_threshold = 0.7  # Flag transactions above this risk score
        
    def _load_sanctions_list(self):
        """Load OFAC/UN sanctions lists (simplified version)"""
        # In production, use API from sanctions screening provider
        return ["IRAN", "NORTH KOREA", "SYRIA", "CRIMEA"]
    
    async def kyc_check(self, user_data: Dict) -> Dict:
        """
        Verify user identity with OCR + biometric
        """
        user_id = user_data.get("user_id")
        full_name = user_data.get("full_name", "")
        document_number = user_data.get("document_number", "")
        
        # Store KYC data
        kyc_key = f"kyc:user:{user_id}"
        redis_client.hset(kyc_key, "full_name", full_name)
        redis_client.hset(kyc_key, "document_number", 
                          hashlib.sha256(document_number.encode()).hexdigest())
        redis_client.hset(kyc_key, "status", "pending")
        redis_client.hset(kyc_key, "submitted_at", datetime.now().isoformat())
        
        # In production, integrate with OCR service here
        
        return {
            "success": True,
            "user_id": user_id,
            "status": "pending",
            "message": "KYC documents received, processing..."
        }
    
    async def approve_kyc(self, user_id: str) -> Dict:
        """Approve user after KYC verification"""
        kyc_key = f"kyc:user:{user_id}"
        redis_client.hset(kyc_key, "status", "approved")
        redis_client.hset(kyc_key, "approved_at", datetime.now().isoformat())
        
        return {"success": True, "user_id": user_id, "status": "approved"}
    
    async def aml_screen(self, transaction: Dict) -> Dict:
        """
        Screen transaction against sanctions lists and risk patterns
        """
        risk_score = 0.0
        flags = []
        
        # Check recipient country against sanctions
        recipient_country = transaction.get("recipient_country", "")
        if recipient_country in self.sanctions_list:
            flags.append(f"Sanctioned country: {recipient_country}")
            risk_score += 0.8
        
        # Check amount against thresholds
        amount = float(transaction.get("amount", 0))
        if amount > 10000:
            flags.append(f"High value transaction: ${amount}")
            risk_score += 0.3
        
        # Check for rapid successive transactions
        user_id = transaction.get("user_id")
        recent_txs = self._get_recent_transactions(user_id, minutes=10)
        if len(recent_txs) > 3:
            total_recent = sum(recent_txs)
            if total_recent > 20000:
                flags.append(f"Unusual velocity: {len(recent_txs)} txs in 10min")
                risk_score += 0.4
        
        # Store screening result
        tx_id = transaction.get("tx_id")
        redis_client.hset(f"aml:tx:{tx_id}", "risk_score", risk_score)
        redis_client.hset(f"aml:tx:{tx_id}", "flags", json.dumps(flags))
        
        needs_review = risk_score > self.risk_threshold
        
        return {
            "success": True,
            "tx_id": tx_id,
            "risk_score": risk_score,
            "flags": flags,
            "needs_review": needs_review,
            "action": "flag_for_review" if needs_review else "approved"
        }
    
    def _get_recent_transactions(self, user_id: str, minutes: int = 10) -> List[float]:
        """Get user's transactions in last N minutes"""
        amounts = []
        # In production, query from transaction database
        # This is a simplified version
        return amounts
    
    async def transaction_monitoring(self):
        """24/7 monitoring of all transactions"""
        while True:
            # In production, this would run continuously
            # monitoring new transactions in real-time
            await asyncio.sleep(60)  # Check every minute
