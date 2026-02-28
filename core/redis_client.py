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
                self.client.ping()  # Test connection
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

# Singleton instance
redis_client = RedisClient()
