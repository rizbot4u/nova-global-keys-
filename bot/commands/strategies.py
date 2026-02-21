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
