"""Base Strategy Class - All strategies inherit from this"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from typing import Dict, Any, Optional

class Strategy(ABC):
    """Abstract base class for all trading strategies"""
    
    def __init__(self, uid: str, symbol: str, amount: float, 
                 strategy_type: str, frequency: str = None):
        self.uid = uid
        self.symbol = symbol
        self.amount = amount
        self.strategy_type = strategy_type
        self.frequency = frequency
        self.created_at = datetime.utcnow()
        self.paused = False
        self.performance = {
            "trades": 0,
            "pnl": 0.0,
            "last_run": None,
            "total_volume": 0.0,
            "win_rate": 0.0
        }
        self.config = {}
    
    @abstractmethod
    async def execute(self, engine) -> Dict[str, Any]:
        """Run one cycle of the strategy"""
        pass
    
    def pause(self):
        self.paused = True
    
    def resume(self):
        self.paused = False
    
    def update_performance(self, trade_result: Dict):
        """Update performance metrics after a trade"""
        self.performance["trades"] += 1
        self.performance["pnl"] += trade_result.get("pnl", 0)
        self.performance["total_volume"] += trade_result.get("volume", 0)
        self.performance["last_run"] = datetime.utcnow().isoformat()
        
        # Calculate win rate
        if trade_result.get("pnl", 0) > 0:
            wins = self.performance.get("wins", 0) + 1
            self.performance["wins"] = wins
            self.performance["win_rate"] = (wins / self.performance["trades"]) * 100
    
    def summary(self) -> Dict[str, Any]:
        """Return strategy summary for storage/display"""
        return {
            "uid": self.uid,
            "symbol": self.symbol,
            "amount": self.amount,
            "type": self.strategy_type,
            "frequency": self.frequency,
            "paused": self.paused,
            "performance": self.performance,
            "config": self.config,
            "created_at": self.created_at.isoformat()
        }
