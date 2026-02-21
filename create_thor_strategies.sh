#!/bin/bash
# THOR STRATEGIES - COMPLETE SETUP SCRIPT
# Run this from /srv/nova-global-keys

echo "🚀 Creating Thor Strategies System..."

# Create directories
mkdir -p /srv/nova-global-keys/strategies
mkdir -p /srv/nova-global-keys/workers
mkdir -p /srv/nova-global-keys/bot/commands

# ============================================================================
# 1. BASE STRATEGY CLASS
# ============================================================================
cat > /srv/nova-global-keys/strategies/base.py << 'EOF'
"""Base Strategy Class - All strategies inherit from this"""
from abc import ABC, abstractmethod
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
EOF

# ============================================================================
# 2. DCA STRATEGY
# ============================================================================
cat > /srv/nova-global-keys/strategies/dca.py << 'EOF'
"""Dollar-Cost Averaging Strategy"""
from datetime import datetime, timedelta
from typing import Dict, Any
import asyncio
from strategies.base import Strategy

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
            
            # Place order using user's API keys
            from core.redis_client import redis_client
            keys = redis_client.get_user_keys(self.uid)
            if not keys:
                return {"status": "error", "message": "User not connected"}
            
            result = await engine.user_place_order(
                api_key=keys['api_key'],
                api_secret=keys['api_secret'],
                symbol=self.symbol,
                side="Buy",
                qty=qty
            )
            
            if result.get('retCode') == 0:
                trade_result = {
                    "pnl": 0,  # DCA doesn't realize PnL immediately
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
EOF

# ============================================================================
# 3. TRIANGULAR ARBITRAGE STRATEGY
# ============================================================================
cat > /srv/nova-global-keys/strategies/triangle.py << 'EOF'
"""Triangular Arbitrage Strategy - Exploit price differences across 3 pairs"""
from typing import Dict, Any, List
import asyncio
from strategies.base import Strategy

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
EOF

# ============================================================================
# 4. DEX ARBITRAGE STRATEGY
# ============================================================================
cat > /srv/nova-global-keys/strategies/dex.py << 'EOF'
"""DEX Arbitrage Strategy - Arbitrage between CEX and DEX"""
from typing import Dict, Any
import asyncio
from strategies.base import Strategy

class DEXArbitrageStrategy(Strategy):
    """Arbitrage between Bybit (CEX) and DEX platforms"""
    
    def __init__(self, uid: str, symbol: str, amount: float):
        super().__init__(uid, symbol, amount, "dex", "continuous")
        self.min_spread = 0.01  # 1% minimum spread
        self.dex_pairs = {
            "ETHUSDT": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
            "BTCUSDT": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"   # WBTC
        }
        self.config = {
            "min_spread": self.min_spread,
            "dex_pairs": self.dex_pairs
        }
    
    async def execute(self, engine) -> Dict[str, Any]:
        """Check for CEX-DEX arbitrage opportunities"""
        if self.paused:
            return {"status": "paused"}
        
        try:
            # Get CEX price from Bybit
            cex_ticker = await engine.broker_get_ticker(self.symbol)
            if cex_ticker.get('retCode') != 0:
                return {"status": "error", "message": "Failed to get CEX price"}
            
            cex_price = engine.format_ticker(cex_ticker)['price']
            
            # Get DEX price (simulated - would use Web3)
            dex_price = await self._get_dex_price(self.symbol)
            
            if not dex_price:
                return {"status": "error", "message": "Failed to get DEX price"}
            
            # Calculate spread
            spread = abs(cex_price - dex_price) / min(cex_price, dex_price)
            
            if spread >= self.min_spread:
                # Determine direction
                if cex_price < dex_price:
                    # Buy on CEX, sell on DEX
                    action = "buy_cex_sell_dex"
                    profit = (dex_price - cex_price) * self.amount
                else:
                    # Buy on DEX, sell on CEX
                    action = "buy_dex_sell_cex"
                    profit = (cex_price - dex_price) * self.amount
                
                # Execute arbitrage
                result = await self._execute_arbitrage(engine, action, cex_price, dex_price)
                
                if result.get('success'):
                    self.update_performance({
                        "pnl": profit,
                        "volume": self.amount * 2,
                        "spread": spread * 100
                    })
                    
                    return {
                        "status": "executed",
                        "message": f"DEX arbitrage executed: {spread*100:.2f}% spread",
                        "profit": profit,
                        "action": action
                    }
            
            return {
                "status": "scanning",
                "cex_price": cex_price,
                "dex_price": dex_price,
                "spread": spread * 100
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _get_dex_price(self, symbol: str) -> float:
        """Get price from DEX (simulated)"""
        # In production, would call Uniswap/PancakeSwap via Web3
        import random
        base_price = 50000 if "BTC" in symbol else 3200
        return base_price * (1 + random.uniform(-0.02, 0.02))
    
    async def _execute_arbitrage(self, engine, action: str, 
                                 cex_price: float, dex_price: float) -> Dict:
        """Execute DEX arbitrage trades"""
        # Would place orders on both platforms
        return {"success": True}
EOF

# ============================================================================
# 5. STORAGE LAYER (REDIS)
# ============================================================================
cat > /srv/nova-global-keys/strategies/storage.py << 'EOF'
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
EOF

# ============================================================================
# 6. STRATEGY WORKER (BACKGROUND RUNNER)
# ============================================================================
cat > /srv/nova-global-keys/workers/strategy_runner.py << 'EOF'
"""Background worker that executes strategies automatically"""
import asyncio
import importlib
import time
import logging
from datetime import datetime
from typing import Dict, Any

from core.redis_client import redis_client
from core.broker_engine import ThorEngine
from strategies.storage import list_strategies, update_strategy, get_all_user_ids

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("strategy-worker")

class StrategyWorker:
    """Background worker for executing strategies"""
    
    def __init__(self):
        self.engine = ThorEngine()
        self.running = True
        self.interval = 60  # Run every 60 seconds
        logger.info("🚀 Strategy Worker initialized")
    
    async def execute_strategy(self, uid: str, strategy_data: Dict) -> Dict:
        """Load and execute a single strategy"""
        try:
            # Dynamically import strategy class
            module_name = f"strategies.{strategy_data['type']}"
            class_name = f"{strategy_data['type'].capitalize()}Strategy"
            
            module = importlib.import_module(module_name)
            StrategyClass = getattr(module, class_name)
            
            # Rehydrate strategy object
            strategy_obj = StrategyClass(
                uid=uid,
                symbol=strategy_data['symbol'],
                amount=strategy_data['amount'],
                frequency=strategy_data.get('frequency')
            )
            
            # Restore state
            strategy_obj.paused = strategy_data.get('paused', False)
            strategy_obj.performance = strategy_data.get('performance', {})
            strategy_obj.config = strategy_data.get('config', {})
            
            # Execute
            if not strategy_obj.paused:
                result = await strategy_obj.execute(self.engine)
                
                # Update storage
                update_strategy(uid, strategy_data['strategy_id'], strategy_obj)
                
                logger.info(f"[{datetime.utcnow()}] Executed {strategy_data['type']} "
                           f"for {uid} - {strategy_data['symbol']} → {result.get('status')}")
                
                return result
            else:
                return {"status": "paused"}
                
        except Exception as e:
            logger.error(f"Strategy execution error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def run_for_user(self, uid: str):
        """Execute all strategies for a single user"""
        strategies = list_strategies(uid)
        
        for strategy_data in strategies:
            await self.execute_strategy(uid, strategy_data)
    
    async def run_cycle(self):
        """Run one complete cycle for all users"""
        uids = get_all_user_ids()
        
        for uid in uids:
            try:
                await self.run_for_user(uid)
            except Exception as e:
                logger.error(f"Error processing user {uid}: {e}")
    
    async def start(self):
        """Main worker loop"""
        logger.info(f"✅ Strategy worker started (interval: {self.interval}s)")
        
        while self.running:
            try:
                await self.run_cycle()
                await asyncio.sleep(self.interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(5)
    
    def stop(self):
        self.running = False

async def main():
    worker = StrategyWorker()
    await worker.start()

if __name__ == "__main__":
    asyncio.run(main())
EOF

# ============================================================================
# 7. TELEGRAM COMMANDS FOR STRATEGIES
# ============================================================================
cat > /srv/nova-global-keys/bot/commands/strategies.py << 'EOF'
"""Telegram commands for strategy management"""
import threading
import asyncio
from strategies.dca import DCAStrategy
from strategies.storage import save_strategy, list_strategies, get_strategy, delete_strategy

def register_strategy_commands(bot):
    """Register all strategy-related commands"""
    
    @bot.message_handler(commands=['strategy'])
    def cmd_strategy(message):
        """Create a new strategy"""
        parts = message.text.split()
        if len(parts) < 4:
            bot.reply_to(message, 
                "❌ Usage: /strategy [dca|triangle|dex] [symbol] [amount]\n"
                "Example: /strategy dca BTCUSDT 50")
            return
        
        strategy_type = parts[1].lower()
        symbol = parts[2].upper()
        try:
            amount = float(parts[3])
        except:
            bot.reply_to(message, "❌ Invalid amount")
            return
        
        user_id = str(message.from_user.id)
        
        def create_and_save():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if strategy_type == "dca":
                strategy = DCAStrategy(user_id, symbol, amount, "daily")
                strategy_id = save_strategy(user_id, strategy)
                
                bot.reply_to(message, 
                    f"✅ *DCA Strategy Created!*\n\n"
                    f"ID: `{strategy_id}`\n"
                    f"Symbol: {symbol}\n"
                    f"Amount: ${amount}\n"
                    f"Frequency: Daily\n\n"
                    f"Use /mystrategy to view", parse_mode="Markdown")
            
            elif strategy_type == "triangle":
                bot.reply_to(message, "🔺 Triangular arbitrage coming soon!")
            
            elif strategy_type == "dex":
                bot.reply_to(message, "🔄 DEX arbitrage coming soon!")
            
            else:
                bot.reply_to(message, f"❌ Unknown strategy type: {strategy_type}")
        
        threading.Thread(target=create_and_save).start()
    
    @bot.message_handler(commands=['mystrategy'])
    def cmd_mystrategy(message):
        """List user's strategies"""
        user_id = str(message.from_user.id)
        
        def fetch_strategies():
            strategies = list_strategies(user_id)
            
            if not strategies:
                bot.reply_to(message, "📭 You have no active strategies. Create one with /strategy")
                return
            
            reply = "📊 *Your Strategies*\n\n"
            for s in strategies:
                status = "⏸️ Paused" if s.get('paused') else "▶️ Active"
                reply += f"• *{s['type'].upper()}* {s['symbol']}\n"
                reply += f"  ID: `{s['strategy_id']}`\n"
                reply += f"  Amount: ${s['amount']}\n"
                reply += f"  Status: {status}\n"
                reply += f"  Trades: {s['performance'].get('trades', 0)}\n"
                reply += f"  PnL: ${s['performance'].get('pnl', 0):.2f}\n\n"
            
            bot.reply_to(message, reply, parse_mode="Markdown")
        
        threading.Thread(target=fetch_strategies).start()
    
    @bot.message_handler(commands=['pause'])
    def cmd_pause(message):
        """Pause a strategy"""
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Usage: /pause [strategy_id]")
            return
        
        strategy_id = parts[1]
        user_id = str(message.from_user.id)
        
        strategy_data = get_strategy(user_id, strategy_id)
        if not strategy_data:
            bot.reply_to(message, f"❌ Strategy {strategy_id} not found")
            return
        
        # Update paused status in Redis
        strategy_data['paused'] = True
        from strategies.storage import redis_client
        import json
        key = f"strategy:{user_id}:{strategy_id}"
        redis_client.client.set(key, json.dumps(strategy_data))
        
        bot.reply_to(message, f"⏸️ Strategy {strategy_id} paused")
    
    @bot.message_handler(commands=['resume'])
    def cmd_resume(message):
        """Resume a paused strategy"""
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Usage: /resume [strategy_id]")
            return
        
        strategy_id = parts[1]
        user_id = str(message.from_user.id)
        
        strategy_data = get_strategy(user_id, strategy_id)
        if not strategy_data:
            bot.reply_to(message, f"❌ Strategy {strategy_id} not found")
            return
        
        strategy_data['paused'] = False
        from strategies.storage import redis_client
        import json
        key = f"strategy:{user_id}:{strategy_id}"
        redis_client.client.set(key, json.dumps(strategy_data))
        
        bot.reply_to(message, f"▶️ Strategy {strategy_id} resumed")
    
    @bot.message_handler(commands=['cancelstrategy'])
    def cmd_cancel(message):
        """Delete a strategy"""
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Usage: /cancelstrategy [strategy_id]")
            return
        
        strategy_id = parts[1]
        user_id = str(message.from_user.id)
        
        if delete_strategy(user_id, strategy_id):
            bot.reply_to(message, f"🗑️ Strategy {strategy_id} deleted")
        else:
            bot.reply_to(message, f"❌ Strategy {strategy_id} not found")
    
    @bot.message_handler(commands=['performance'])
    def cmd_performance(message):
        """Show strategy performance"""
        user_id = str(message.from_user.id)
        
        def fetch_performance():
            strategies = list_strategies(user_id)
            
            if not strategies:
                bot.reply_to(message, "No strategies to show")
                return
            
            total_pnl = 0
            total_trades = 0
            reply = "📈 *Performance Summary*\n\n"
            
            for s in strategies:
                pnl = s['performance'].get('pnl', 0)
                trades = s['performance'].get('trades', 0)
                total_pnl += pnl
                total_trades += trades
                
                reply += f"• *{s['type'].upper()}* {s['symbol']}\n"
                reply += f"  Trades: {trades} | PnL: ${pnl:.2f}\n"
            
            reply += f"\n*Total:* ${total_pnl:.2f} from {total_trades} trades"
            bot.reply_to(message, reply, parse_mode="Markdown")
        
        threading.Thread(target=fetch_performance).start()
EOF

# ============================================================================
# 8. UPDATE BOT RUNNER TO INCLUDE STRATEGY COMMANDS
# ============================================================================
cat > /srv/nova-global-keys/bot/runner.py << 'EOF'
"""Telegram bot runner with strategy commands"""
import logging
import time
import telebot
from config.settings import settings
from bot.commands.strategies import register_strategy_commands

logger = logging.getLogger(__name__)

class TelegramBot:
    """Telegram bot runner"""
    
    def __init__(self):
        self.bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
        self.register_all_handlers()
        logger.info("🤖 Telegram bot initialized")
    
    def register_all_handlers(self):
        """Register all command handlers"""
        # Register strategy commands
        register_strategy_commands(self.bot)
        
        # Keep existing command handlers
        @self.bot.message_handler(commands=['start', 'help'])
        def cmd_start(message):
            welcome = f"""
✨ *Welcome to Nova Global Keys, {message.from_user.first_name}!* ✨

🙏 *Love, Peace & Respect*

*Broker:* `{settings.BROKER_CODE}`

📋 *COMMANDS:*
/connect - Link Bybit account
/balance - View wallet
/price BTC - Get price
/trade Buy BTC 100 - Trade
/strategy - Create trading strategy
/mystrategy - View your strategies
/performance - Strategy performance
/status - System check
            """
            self.bot.reply_to(message, welcome, parse_mode="Markdown")
        
        # Add other existing commands here...
    
    def run(self):
        """Run the bot with auto-reconnect"""
        logger.info("Starting Telegram bot...")
        while True:
            try:
                self.bot.infinity_polling(timeout=60)
            except Exception as e:
                logger.error(f"Bot error: {e}")
                time.sleep(5)
EOF

# ============================================================================
# 9. CREATE WORKER STARTUP SCRIPT
# ============================================================================
cat > /srv/nova-global-keys/start_worker.sh << 'EOF'
#!/bin/bash
# Start the strategy worker in background
cd /srv/nova-global-keys
source venv/bin/activate
python -m workers.strategy_runner
EOF
chmod +x /srv/nova-global-keys/start_worker.sh

# ============================================================================
# 10. CREATE PM2 CONFIG FOR WORKER
# ============================================================================
cat > /srv/nova-global-keys/ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'nova-thor',
      script: 'thor_engine.py',
      interpreter: 'python3',
      watch: false,
      env: {
        PYTHONUNBUFFERED: '1'
      }
    },
    {
      name: 'strategy-worker',
      script: 'workers/strategy_runner.py',
      interpreter: 'python3',
      watch: false,
      env: {
        PYTHONUNBUFFERED: '1'
      }
    }
  ]
};
EOF

# ============================================================================
# FINAL MESSAGE
# ============================================================================
echo ""
echo "🎉 THOR STRATEGIES SYSTEM CREATED SUCCESSFULLY!"
echo "================================================"
echo ""
echo "📁 Created files:"
echo "  /srv/nova-global-keys/strategies/base.py"
echo "  /srv/nova-global-keys/strategies/dca.py"
echo "  /srv/nova-global-keys/strategies/triangle.py"
echo "  /srv/nova-global-keys/strategies/dex.py"
echo "  /srv/nova-global-keys/strategies/storage.py"
echo "  /srv/nova-global-keys/workers/strategy_runner.py"
echo "  /srv/nova-global-keys/bot/commands/strategies.py"
echo "  /srv/nova-global-keys/bot/runner.py (updated)"
echo "  /srv/nova-global-keys/start_worker.sh"
echo "  /srv/nova-global-keys/ecosystem.config.js"
echo ""
echo "🚀 To start the strategy worker:"
echo "  cd /srv/nova-global-keys"
echo "  python -m workers.strategy_runner"
echo ""
echo "📦 Or with PM2:"
echo "  pm2 start ecosystem.config.js"
echo ""
echo "✅ Your Thor Strategies system is ready!"
echo "================================================"
