"""Telegram bot runner with all commands"""
import logging
import time
import telebot
from config.settings import settings

logger = logging.getLogger(__name__)

class TelegramBot:
    """Telegram bot runner"""
    
    def __init__(self):
        self.bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
        self.register_all_handlers()
        logger.info("🤖 Telegram bot initialized")
    
    def register_all_handlers(self):
        """Register all command handlers"""
        
        # Try to import and register strategy commands
        try:
            from bot.commands.strategies import register_strategy_commands
            register_strategy_commands(self.bot)
            logger.info("✅ Strategy commands registered")
        except Exception as e:
            logger.warning(f"⚠️ Strategy commands not available: {e}")
        
        # Try to import and register payment commands
        try:
            from bot.commands.payments import register_payment_commands
            register_payment_commands(self.bot)
            logger.info("✅ Payment commands registered")
        except Exception as e:
            logger.warning(f"⚠️ Payment commands not available: {e}")
        
        # Try to import and register p2p commands
        try:
            from bot.commands.p2p import register_p2p_commands
            register_p2p_commands(self.bot)
            logger.info("✅ P2P commands registered")
        except Exception as e:
            logger.warning(f"⚠️ P2P commands not available: {e}")
        
        @self.bot.message_handler(commands=['start', 'help'])
        def cmd_start(message):
            welcome = f"""
✨ *Welcome to Nova Global Keys, {message.from_user.first_name}!* ✨

🙏 *Love, Peace & Respect*

*Broker:* `{settings.BROKER_CODE}`

📋 *BASIC COMMANDS:*
/connect - Link Bybit account
/balance - View wallet
/price BTC - Get price
/status - System check
/trade - Place a trade

📊 *STRATEGY COMMANDS:*
/strategy dca BTCUSDT 50 - Create DCA strategy
/mystrategy - View strategies
/performance - View performance

💰 *PAYMENT COMMANDS:*
/pay - Payment options
/cash 50 - Request cash payment
/confirm ID TXID - Confirm payment

🔄 *P2P COMMANDS:*
/p2p - P2P trading menu

*Type any command to get started!*
            """
            self.bot.reply_to(message, welcome, parse_mode="Markdown")
        
        @self.bot.message_handler(commands=['connect'])
        def cmd_connect(message):
            user_id = str(message.from_user.id)
            import uuid
            state = f"tg_{user_id}_{uuid.uuid4().hex[:8]}"
            
            from core.redis_client import redis_client
            redis_client.store_oauth_state(state, user_id)
            
            url = f"https://www.bybit.com/en/oauth?client_id={settings.CLIENT_ID}&response_type=code&scope=openapi&state={state}&redirect_uri={settings.REDIRECT_URI}&affiliate_id={settings.AFFILIATE_ID}"
            
            msg = f"""
🔐 *Connect Your Bybit Account*

[Click here to connect]({url})

⚠️ You'll be redirected automatically
            """
            self.bot.reply_to(message, msg, parse_mode="Markdown", disable_web_page_preview=False)
        
        @self.bot.message_handler(commands=['price'])
        def cmd_price(message):
            parts = message.text.split()
            symbol = parts[1].upper() if len(parts) > 1 else "BTCUSDT"
            
            self.bot.reply_to(message, f"🔄 Fetching {symbol}...")
            
            def fetch_and_reply():
                import httpx
                try:
                    response = httpx.get(f"http://localhost:{settings.PORT}/api/v1/price/{symbol}", timeout=10)
                    data = response.json()
                    
                    if data.get('success'):
                        reply = f"""
📊 *{data['symbol']}*
💰 Price: ${data['price']:,.2f}
📈 24h: {data['change_24h']:+.2f}%
📊 High: ${data['high_24h']:,.2f}
📉 Low: ${data['low_24h']:,.2f}
                        """
                        self.bot.reply_to(message, reply, parse_mode="Markdown")
                    else:
                        self.bot.reply_to(message, f"❌ Could not fetch {symbol}")
                except Exception as e:
                    self.bot.reply_to(message, f"❌ Error: {str(e)}")
            
            threading.Thread(target=fetch_and_reply).start()
        
        @self.bot.message_handler(commands=['balance'])
        def cmd_balance(message):
            user_id = str(message.from_user.id)
            from core.redis_client import redis_client
            keys = redis_client.get_user_keys(user_id)
            
            if not keys:
                self.bot.reply_to(message, "❌ Please /connect first")
                return
            
            self.bot.reply_to(message, "🔄 Fetching your balance...")
            
            def fetch_and_reply():
                import httpx
                try:
                    response = httpx.get(
                        f"http://localhost:{settings.PORT}/api/v1/balance",
                        headers={"Authorization": user_id},
                        timeout=10
                    )
                    data = response.json()
                    
                    if data.get('success'):
                        reply = "💰 *Your Portfolio*\n\n"
                        for coin, details in data['balances'].items():
                            reply += f"• *{coin}:* {details['balance']:.4f} (${details['usd_value']:,.2f})\n"
                        
                        credit = float(redis_client.client.get(f"user:{user_id}:credit") or 0)
                        if credit > 0:
                            reply += f"\n*Shop Credit:* ${credit:.2f}"
                        
                        self.bot.reply_to(message, reply, parse_mode="Markdown")
                    else:
                        self.bot.reply_to(message, "❌ Could not fetch balance")
                except Exception as e:
                    self.bot.reply_to(message, f"❌ Error: {str(e)}")
            
            threading.Thread(target=fetch_and_reply).start()
        
        @self.bot.message_handler(commands=['status'])
        def cmd_status(message):
            user_id = str(message.from_user.id)
            from core.redis_client import redis_client
            is_connected = redis_client.user_exists(user_id)
            
            heartbeat = redis_client.client.get("worker:last_heartbeat")
            worker_status = "❌ Not responding"
            if heartbeat:
                try:
                    from datetime import datetime, timedelta, timezone
                    last = datetime.fromisoformat(heartbeat)
                    if datetime.now(timezone.utc) - last < timedelta(minutes=2):
                        worker_status = "✅ Running"
                except:
                    pass
            
            status = f"""
🟢 *System Status*

*Broker:* `{settings.BROKER_CODE}`
*Your Account:* {'✅ Connected' if is_connected else '❌ Not connected'}
*Redis:* ✅ Connected
*Worker:* {worker_status}
            """
            self.bot.reply_to(message, status, parse_mode="Markdown")
    
    def run(self):
        """Run the bot with auto-reconnect"""
        logger.info("Starting Telegram bot...")
        while True:
            try:
                self.bot.infinity_polling(timeout=60)
            except Exception as e:
                logger.error(f"Bot error: {e}")
                time.sleep(5)
