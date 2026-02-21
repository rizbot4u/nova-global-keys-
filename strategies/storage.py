"""Strategy Storage - Redis persistence layer"""
import json
import uuid
from typing import List, Dict, Any, Optional
from core.redis_client import redis_client

def save_strategy(uid: str, strategy_obj) -> str:
    """Save a strategy instance to Redis"""
    strategy_id = str(uuid.uuid4())[:8]
    key = f"strategy:{uid}:{strategy_id}"
    
    data = strategy_obj.summary()
    data['strategy_id'] = strategy_id
    
    redis_client.client.set(key, json.dumps(data))
    return strategy_id

def get_strategy(uid: str, strategy_id: str) -> Optional[Dict]:
    """Retrieve a strategy by ID"""
    key = f"strategy:{uid}:{strategy_id}"
    data = redis_client.client.get(key)
    if not data:
        return None
    return json.loads(data)

def list_strategies(uid: str) -> List[Dict]:
    """List all strategies for a user"""
    keys = redis_client.client.keys(f"strategy:{uid}:*")
    strategies = []
    for key in keys:
        data = redis_client.client.get(key)
        if data:
            strategy = json.loads(data)
            strategy['strategy_id'] = key.split(':')[-1]
            strategies.append(strategy)
    return strategies

def update_strategy(uid: str, strategy_id: str, strategy_obj) -> bool:
    """Update an existing strategy"""
    key = f"strategy:{uid}:{strategy_id}"
    data = strategy_obj.summary()
    data['strategy_id'] = strategy_id
    redis_client.client.set(key, json.dumps(data))
    return True

def delete_strategy(uid: str, strategy_id: str) -> bool:
    """Delete a strategy"""
    key = f"strategy:{uid}:{strategy_id}"
    return bool(redis_client.client.delete(key))

def get_all_user_ids() -> List[str]:
    """Get all unique user IDs that have strategies"""
    keys = redis_client.client.keys("strategy:*")
    uids = set()
    for key in keys:
        parts = key.split(':')
        if len(parts) >= 2:
            uids.add(parts[1])
    return list(uids)
