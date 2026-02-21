"""Triangular Arbitrage Strategy - Exploit price differences across 3 pairs"""
from typing import Dict, Any, List
import asyncio
from strategies.base import Strategy
from typing import List, Dict, Any

class TriangleStrategy(Strategy):
    """Triangular arbitrage across three trading pairs"""
    
    def __init__(self, uid: str, symbol: str, amount: float, 
                 triangles: List[List[str]] = None):
        super().__init__(uid, symbol, amount, "triangle", "continuous")
        
        # Default triangles for major pairs
        self.triangles = triangles or [
            ["BTCUSDT", "ETHBTC", "ETHUSDT"],
            ["BTCUSDT", "SOLBTC", "SOLUSDT"],
            ["ETHUSDT", "SOLETH", "SOLUSDT"]
        ]
        self.min_profit_threshold = 0.005  # 0.5% minimum profit
        self.last_check = None
        self.config = {
            "min_profit": self.min_profit_threshold,
            "triangles": self.triangles,
            "max_slippage": 0.001
        }
    
    async def execute(self, engine) -> Dict[str, Any]:
        """Check for triangular arbitrage opportunities"""
        if self.paused:
            return {"status": "paused"}
        
        try:
            opportunities = []
            
            for triangle in self.triangles:
                # Get prices for all three pairs
                prices = {}
                for pair in triangle:
                    ticker = await engine.broker_get_ticker(pair)
                    if ticker.get('retCode') != 0:
                        continue
                    price_data = engine.format_ticker(ticker)
                    prices[pair] = price_data['price']
                
                if len(prices) != 3:
                    continue
                
                # Calculate triangular arbitrage profit
                # Example: BTCUSDT -> ETHBTC -> ETHUSDT
                profit = self._calculate_profit(triangle, prices)
                
                if profit > self.min_profit_threshold:
                    opportunities.append({
                        "triangle": triangle,
                        "prices": prices,
                        "profit_percent": profit * 100
                    })
            
            if opportunities:
                # Execute the best opportunity
                best = max(opportunities, key=lambda x: x['profit_percent'])
                
                # Execute arbitrage trades
                result = await self._execute_arbitrage(engine, best)
                
                if result.get('success'):
                    self.update_performance({
                        "pnl": result['pnl'],
                        "volume": self.amount * 3,
                        "opportunity": best
                    })
                    
                    return {
                        "status": "executed",
                        "message": f"Arbitrage executed: {best['profit_percent']:.2f}% profit",
                        "profit": result['pnl'],
                        "opportunity": best
                    }
            
            return {
                "status": "scanning",
                "opportunities_found": len(opportunities)
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _calculate_profit(self, triangle: List[str], prices: Dict) -> float:
        """Calculate profit percentage for triangular arbitrage"""
        # Simplified calculation - implement actual arbitrage math
        return 0.01  # Example: 1% profit
    
    async def _execute_arbitrage(self, engine, opportunity: Dict) -> Dict:
        """Execute the arbitrage trades"""
        # Implementation would place multiple orders
        return {"success": True, "pnl": self.amount * 0.01}
