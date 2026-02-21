"""
Nova Global Keys - Redis Client Module
Handles all Redis connections and operations
"""

import redis
import json
import logging
from typing import Optional, Any, Dict
from config.settings import settings

logger = logging.getLogger(__name__)

class RedisClient:
    """Redis client wrapper"""
    
    def __init__(self):
        self.client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
    
    def ping(self) -> bool:
        """Check connection"""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    # === User Data ===
    def store_user_keys(self, user_id: str, api_key: str, api_secret: str, uid: str = None):
        """Store user's API keys"""
        pipeline = self.client.pipeline()
        pipeline.set(f"user:{user_id}:api_key", api_key)
        pipeline.set(f"user:{user_id}:api_secret", api_secret)
        if uid:
            pipeline.set(f"user:{user_id}:uid", uid)
        pipeline.execute()
        logger.info(f"Stored keys for user {user_id}")
    
    def get_user_keys(self, user_id: str) -> Optional[Dict[str, str]]:
        """Get user's API keys"""
        api_key = self.client.get(f"user:{user_id}:api_key")
        api_secret = self.client.get(f"user:{user_id}:api_secret")
        
        if api_key and api_secret:
            return {
                'api_key': api_key,
                'api_secret': api_secret,
                'uid': self.client.get(f"user:{user_id}:uid")
            }
        return None
    
    def user_exists(self, user_id: str) -> bool:
        """Check if user exists"""
        return self.client.exists(f"user:{user_id}:api_key") > 0
    
    # === OAuth State ===
    def store_oauth_state(self, state: str, user_id: str, expiry: int = 600):
        """Store OAuth state"""
        self.client.setex(f"oauth:{state}", expiry, user_id)
    
    def get_oauth_state(self, state: str) -> Optional[str]:
        """Get OAuth state"""
        return self.client.get(f"oauth:{state}")
    
    def delete_oauth_state(self, state: str):
        """Delete OAuth state"""
        self.client.delete(f"oauth:{state}")
    
    # === Payments ===
    def store_payment(self, payment_id: str, data: dict, expiry: int = 3600):
        """Store payment data"""
        self.client.setex(
            f"payment:{payment_id}",
            expiry,
            json.dumps(data)
        )
    
    def get_payment(self, payment_id: str) -> Optional[dict]:
        """Get payment data"""
        data = self.client.get(f"payment:{payment_id}")
        return json.loads(data) if data else None
    
    # === Market Data Cache ===
    def cache_price(self, symbol: str, price: float, expiry: int = 30):
        """Cache price data"""
        self.client.setex(f"price:{symbol}", expiry, str(price))
    
    def get_cached_price(self, symbol: str) -> Optional[float]:
        """Get cached price"""
        price = self.client.get(f"price:{symbol}")
        return float(price) if price else None

# Global instance
redis_client = RedisClient()
