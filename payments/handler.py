"""
Nova Global Keys - Payment Handler
Payment processing and management
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from core.redis_client import redis_client

logger = logging.getLogger(__name__)

class PaymentHandler:
    """Handle payments and invoices"""
    
    @staticmethod
    def create_payment(user_id: str, amount: float, currency: str = "USDT") -> Dict:
        """Create a new payment"""
        payment_id = f"PAY_{uuid.uuid4().hex[:8].upper()}"
        
        payment_data = {
            "id": payment_id,
            "user_id": user_id,
            "amount": amount,
            "currency": currency,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
        }
        
        redis_client.store_payment(payment_id, payment_data, 3600)
        logger.info(f"Payment created: {payment_id} for user {user_id}")
        
        return payment_data
    
    @staticmethod
    def get_payment(payment_id: str) -> Optional[Dict]:
        """Get payment details"""
        return redis_client.get_payment(payment_id)
    
    @staticmethod
    def confirm_payment(payment_id: str) -> bool:
        """Confirm payment received"""
        payment = redis_client.get_payment(payment_id)
        if payment and payment['status'] == 'pending':
            payment['status'] = 'completed'
            payment['completed_at'] = datetime.now().isoformat()
            redis_client.store_payment(payment_id, payment, 86400)
            logger.info(f"Payment confirmed: {payment_id}")
            return True
        return False
    
    @staticmethod
    def cancel_payment(payment_id: str) -> bool:
        """Cancel payment"""
        payment = redis_client.get_payment(payment_id)
        if payment and payment['status'] == 'pending':
            payment['status'] = 'cancelled'
            payment['cancelled_at'] = datetime.now().isoformat()
            redis_client.store_payment(payment_id, payment, 3600)
            logger.info(f"Payment cancelled: {payment_id}")
            return True
        return False
