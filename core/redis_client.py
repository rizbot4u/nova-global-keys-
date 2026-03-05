"""Redis client module for Nova Global Keys"""
import os
import json
from typing import Optional, Dict

# Try to import redis, but don't crash if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ Redis module not installed - using mock client")

REDIS_URL = os.getenv("REDIS_URL", "redis://default:NovaGlobal2026@localhost:6379/0")

class RedisClient:
    def __init__(self):
        self.client = None
        if REDIS_AVAILABLE:
            try:
                self.client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
                self.client.ping()
                print("✅ Redis connected")
            except:
                print("⚠️ Redis connection failed - using mock client")
                self.client = None
        else:
            print("⚠️ Redis module not available - using mock client")
    
    def get(self, key, default=None):
        if self.client:
            try:
                value = self.client.get(key)
                return value if value is not None else default
            except:
                return default
        return default
    
    def set(self, key, value):
        if self.client:
            try:
                return self.client.set(key, value)
            except:
                return False
        return False
    
    def ping(self):
        if self.client:
            try:
                return self.client.ping()
            except:
                return False
        return False

    # >>>>>>> MOVE THIS METHOD INSIDE THE CLASS <<<<<<<
    def store_user_keys(self, user_id: str, api_key: str, api_secret: str, uid: str = None):
        try:
            import logging
            logger = logging.getLogger("nova-thor")
            logger.info(f"📝 Storing keys for user: {user_id}")
            logger.info(f"API Key length: {len(api_key) if api_key else 0}")
            logger.info(f"API Secret length: {len(api_secret) if api_secret else 0}")
            
            pipe = self.client.pipeline()
            pipe.set(f"user:{user_id}:api_key", api_key)
            pipe.set(f"user:{user_id}:api_secret", api_secret)
            if uid:
                pipe.set(f"user:{user_id}:uid", uid)
            result = pipe.execute()
            
            logger.info(f"✅ Redis pipeline result: {result}")
            logger.info(f"✅ Stored keys for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to store keys: {e}")
            raise

# Singleton instance
redis_client = RedisClient()
