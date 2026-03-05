"""
Base Exchange Interface - All exchanges must implement these methods
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger("exchange-base")

class BaseExchange(ABC):
    """Unified interface for all exchanges"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.name = self.__class__.__name__.replace('Exchange', '').lower()
    
    @abstractmethod
    async def get_balance(self, account_type: str = "UNIFIED") -> Dict:
        """Get wallet balance"""
        pass
    
    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict:
        """Get current price ticker"""
        pass
    
    @abstractmethod
    async def place_order(self, symbol: str, side: str, order_type: str, 
                          quantity: float, price: float = None) -> Dict:
        """Place an order"""
        pass
    
    @abstractmethod
    async def cancel_order(self, symbol: str, order_id: str) -> Dict:
        """Cancel an order"""
        pass
    
    @abstractmethod
    async def get_open_orders(self, symbol: str = None) -> List:
        """Get open orders"""
        pass
    
    @abstractmethod
    async def get_order_history(self, symbol: str = None, limit: int = 50) -> List:
        """Get order history"""
        pass
    
    @abstractmethod
    async def get_deposit_address(self, coin: str) -> Dict:
        """Get deposit address"""
        pass
    
    @abstractmethod
    async def withdraw(self, coin: str, address: str, amount: float, 
                       network: str = None) -> Dict:
        """Withdraw funds"""
        pass
    
    def format_balance(self, balance_data: Dict) -> Dict:
        """Standardize balance format across exchanges"""
        try:
            balances = {}
            total_usd = 0
            assets = []
            
            # This method should be overridden by each exchange
            # to convert their specific format to standard format
            
            return {
                "success": True,
                "balances": balances,
                "total_usd": total_usd,
                "assets": assets,
                "exchange": self.name
            }
        except Exception as e:
            logger.error(f"Error formatting balance: {e}")
            return {"success": False, "error": str(e), "exchange": self.name}
