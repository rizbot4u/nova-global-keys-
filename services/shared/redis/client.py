import redis
import json
import logging
from datetime import datetime
import os

logger = logging.getLogger("nova-redis")

class RedisClient:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://default:NovaGlobal2026@localhost:6379/0")
        self.client = redis.Redis.from_url(redis_url, decode_responses=True)
        logger.info(f"✅ Redis connected: {self.client.ping()}")
    
    def ping(self) -> bool:
        try:
            return self.client.ping()
        except:
            return False
    
    # User keys
    def store_user_keys(self, user_id: str, api_key: str, api_secret: str, uid: str = None):
        pipe = self.client.pipeline()
        pipe.set(f"user:{user_id}:api_key", api_key)
        pipe.set(f"user:{user_id}:api_secret", api_secret)
        if uid:
            pipe.set(f"user:{user_id}:uid", uid)
        pipe.execute()
        logger.info(f"✅ Stored keys for user {user_id}")
    
    def get_user_keys(self, user_id: str) -> dict:
        api_key = self.client.get(f"user:{user_id}:api_key")
        api_secret = self.client.get(f"user:{user_id}:api_secret")
        if api_key and api_secret:
            return {
                'api_key': api_key,
                'api_secret': api_secret,
                'uid': self.client.get(f"user:{user_id}:uid")
            }
        return None
    
    # OAuth state
    def store_oauth_state(self, state: str, user_id: str, expiry: int = 600):
        self.client.setex(f"oauth:{state}", expiry, user_id)
    
    def get_oauth_state(self, state: str) -> str:
        return self.client.get(f"oauth:{state}")
    
    def delete_oauth_state(self, state: str):
        self.client.delete(f"oauth:{state}")
    
    # Telegram mappings
    def link_telegram(self, telegram_id: str, user_id: str):
        self.client.set(f"telegram:{telegram_id}:user_id", user_id)
        self.client.set(f"user:{user_id}:telegram_id", telegram_id)
    
    def get_user_by_telegram(self, telegram_id: str) -> str:
        return self.client.get(f"telegram:{telegram_id}:user_id")
    
    # Service registry
    def register_service(self, service_name: str, host: str, port: int):
        self.client.hset("service:registry", service_name, f"{host}:{port}")
        self.client.setex(f"service:heartbeat:{service_name}", 30, datetime.now().isoformat())
    
    def get_service(self, service_name: str) -> str:
        return self.client.hget("service:registry", service_name)
    
    def heartbeat(self, service_name: str):
        self.client.setex(f"service:heartbeat:{service_name}", 30, datetime.now().isoformat())
    
    # Rate limiting
    def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        current = self.client.get(f"ratelimit:{key}")
        if current and int(current) >= limit:
            return False
        self.client.incr(f"ratelimit:{key}")
        self.client.expire(f"ratelimit:{key}", window)
        return True

redis_client = RedisClient()
