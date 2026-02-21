"""Dollar-Cost Averaging Strategy"""
from datetime import datetime, timedelta
from typing import Dict, Any
import asyncio
from strategies.base import Strategy
from core.redis_client import redis_client

class DCAStrategy(Strategy):
    """Dollar-Cost Averaging - Buy fixed amount at regular intervals"""
    
    def __init__(self, uid: str, symbol: str, amount: float, 
                 frequency: str = "daily", interval_hours: int = 24):
        super().__init__(uid, symbol, amount, "dca", frequency)
        self.interval_hours = interval_hours
        self.last_run = None
        self.config = {
            "interval_hours": interval_hours,
            "min_price": None,
            "max_price": None,
            "slippage_tolerance": 0.01
        }
    
    async def execute(self, engine) -> Dict[str, Any]:
        """Execute DCA buy order"""
        if self.paused:
            return {"status": "paused", "message": "Strategy is paused"}
        
        # Check if it's time to run
        now = datetime.utcnow()
        if self.last_run:
            next_run = self.last_run + timedelta(hours=self.interval_hours)
            if now < next_run:
                return {"status": "skipped", "next_run": next_run.isoformat()}
        
        try:
            # Get user's API keys
            keys = redis_client.get_user_keys(self.uid)
            if not keys:
                return {"status": "error", "message": "User not connected"}
            
            # Check user's balance first
            balance_result = await engine.user_get_balance(
                api_key=keys['api_key'],
                api_secret=keys['api_secret']
            )
            
            if balance_result.get('retCode') == 0:
                # Find USDT balance
                usdt_balance = 0
                coins = balance_result.get('result', {}).get('list', [{}])[0].get('coin', [])
                for coin in coins:
                    if coin.get('coin') == 'USDT':
                        usdt_balance = float(coin.get('walletBalance', 0))
                        break
                
                if usdt_balance < self.amount:
                    return {
                        "status": "skipped",
                        "message": f"Insufficient USDT balance: ${usdt_balance:.2f} (need ${self.amount})"
                    }
            
            # Get current price
            ticker = await engine.broker_get_ticker(self.symbol)
            if ticker.get('retCode') != 0:
                return {"status": "error", "message": "Failed to get price"}
            
            price_data = engine.format_ticker(ticker)
            current_price = price_data['price']
            
            # Check price limits
            if self.config["min_price"] and current_price < self.config["min_price"]:
                return {"status": "skipped", "message": f"Price ${current_price} below minimum"}
            if self.config["max_price"] and current_price > self.config["max_price"]:
                return {"status": "skipped", "message": f"Price ${current_price} above maximum"}
            
            # Calculate quantity
            qty = str(round(self.amount / current_price, 4))
            
            # Place order
            result = await engine.user_place_order(
                api_key=keys['api_key'],
                api_secret=keys['api_secret'],
                symbol=self.symbol,
                side="Buy",
                qty=qty
            )
            
            if result.get('retCode') == 0:
                trade_result = {
                    "pnl": 0,
                    "volume": self.amount,
                    "price": current_price,
                    "qty": float(qty),
                    "order_id": result.get('result', {}).get('orderId')
                }
                self.update_performance(trade_result)
                self.last_run = now
                
                return {
                    "status": "executed",
                    "message": f"Bought {qty} {self.symbol} for ${self.amount}",
                    "price": current_price,
                    "performance": self.performance
                }
            else:
                return {"status": "error", "message": result.get('retMsg', 'Order failed')}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
