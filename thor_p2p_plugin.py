#!/usr/bin/env python3
"""
NOVA GLOBAL KEYS - P2P ARBITRAGE PLUGIN v2.0 PRODUCTION
Sidecar module for P2P monitoring with anti-scam filters & broker tracking
Author: Nova Global Keys | Broker: Kr000820
"""

import asyncio
import logging
import uuid
from datetime import datetime
import threading
import time

import telebot
from telebot import types

# Import your existing engine components
from thor_engine import ThorEngine, settings, redis_client, SessionLocal, User, ExchangeKey
from thor_engine import get_current_user, get_optional_user

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("nova-p2p")

# Initialize Telegram bot
bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)

# ==============================================================================
# CONFIGURATION - TUNE THESE FOR YOUR CAPITAL
# ==============================================================================

P2P_CONFIG = {
    "MIN_AMOUNT": 500,      # Only alert for deals >= $500 (filter out scam dust)
    "PROFIT_THRESHOLD": 0.98, # Alert when USDT price < $0.98
    "SCAN_INTERVAL": 60,     # Seconds between scans
    "CURRENCY": "USD",       # Change to GBP, EUR, etc. for fiat arbitrage
    "MAX_ADS_TO_CHECK": 5,   # Number of ads to analyze per scan
    "BROKER_ID": "Kr000820"  # Your broker code for affiliate tracking
}

# ==============================================================================
# P2P ARBITRAGE WATCHDOG - With Anti-Scam Filters
# ==============================================================================

async def p2p_arbitrage_scanner():
    """Background task that scans P2P marketplace for REAL profit opportunities"""
    logger.info(f"🚀 P2P Arbitrage Watchdog Started - Scanning every {P2P_CONFIG['SCAN_INTERVAL']} seconds")
    logger.info(f"💼 Min amount: ${P2P_CONFIG['MIN_AMOUNT']} | Threshold: ${P2P_CONFIG['PROFIT_THRESHOLD']}")
    
    # Use master API keys for scanning
    engine = ThorEngine(settings.MASTER_API_KEY, settings.MASTER_API_SECRET)
    
    while True:
        try:
            # ===== SCAN BUY SIDE (We want to buy cheap USDT) =====
            # Side: "0" = Buy (from user perspective), "1" = Sell
            buy_result = await engine._request(
                "GET", 
                "/v5/p2p/item/online", 
                params={
                    "coin": "USDT", 
                    "currency": P2P_CONFIG["CURRENCY"], 
                    "side": "0",  # Buy USDT
                    "amount": str(P2P_CONFIG["MIN_AMOUNT"]),  # FILTER: Only show ads >= $500
                    "size": P2P_CONFIG["MAX_ADS_TO_CHECK"]
                }
            )
            
            if buy_result.get('retCode') == 0 and buy_result['result']['items']:
                items = buy_result['result']['items']
                
                for ad in items:
                    price = float(ad['price'])
                    advertiser = ad['userName']
                    available = float(ad.get('quantity', 0))
                    min_amount = float(ad.get('minAmount', 0))
                    max_amount = float(ad.get('maxAmount', 0))
                    order_count = ad.get('orderCount', 0)
                    finish_rate = ad.get('finishRate', 0)
                    
                    # PROFIT ALERT - Price below threshold
                    if price < P2P_CONFIG["PROFIT_THRESHOLD"] and available >= P2P_CONFIG["MIN_AMOUNT"]:
                        # Calculate potential profit
                        profit_per_usdt = 1.0 - price
                        potential_profit = profit_per_usdt * min(P2P_CONFIG["MIN_AMOUNT"], available)
                        
                        msg = (
                            f"🚨 *P2P PROFIT OPPORTUNITY*\n"
                            f"Price: `${price:.4f}`\n"
                            f"Spread: `+{profit_per_usdt*100:.2f}%`\n"
                            f"Est. Profit: `${potential_profit:.2f}`\n"
                            f"Available: {available:.0f} USDT\n"
                            f"Advertiser: {advertiser}\n"
                            f"Trust: {finish_rate}% ({order_count} orders)\n"
                            f"Min/Max: ${min_amount:.0f}/${max_amount:.0f}"
                        )
                        bot.send_message(settings.ADMIN_CHAT_ID, msg, parse_mode="Markdown")
                        logger.info(f"🔥 PROFIT ALERT: USDT at ${price:.4f} (Profit: ${potential_profit:.2f})")
            
            # ===== SCAN SELL SIDE (We want to sell USDT high) =====
            sell_result = await engine._request(
                "GET", 
                "/v5/p2p/item/online", 
                params={
                    "coin": "USDT", 
                    "currency": P2P_CONFIG["CURRENCY"], 
                    "side": "1",  # Sell USDT
                    "amount": str(P2P_CONFIG["MIN_AMOUNT"]),
                    "size": 3
                }
            )
            
            if sell_result.get('retCode') == 0 and sell_result['result']['items']:
                items = sell_result['result']['items']
                for ad in items:
                    price = float(ad['price'])
                    if price > 1.02:  # Alert if we can sell above $1.02
                        logger.info(f"📈 Sell opportunity: USDT at ${price:.4f}")
            
            logger.debug(f"✅ P2P Scan completed at {datetime.now().isoformat()}")
            
        except Exception as e:
            logger.error(f"❌ P2P Scanner Error: {e}")
        
        await asyncio.sleep(P2P_CONFIG["SCAN_INTERVAL"])  # Respect rate limits!

# ==============================================================================
# P2P TELEGRAM COMMANDS
# ==============================================================================

@bot.message_handler(commands=['p2p'])
def cmd_p2p(message):
    """Main P2P command - shows dashboard"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn1 = types.InlineKeyboardButton("🔍 Scan P2P Ads", callback_data="p2p_scan")
    btn2 = types.InlineKeyboardButton("📋 My Orders", callback_data="p2p_orders")
    btn3 = types.InlineKeyboardButton("💰 Funding Balance", callback_data="p2p_funding")
    btn4 = types.InlineKeyboardButton("🔄 Sync to Trading", callback_data="p2p_sync")
    btn5 = types.InlineKeyboardButton("📊 Active Deals", callback_data="p2p_active")
    btn6 = types.InlineKeyboardButton("⚙️ Settings", callback_data="p2p_settings")
    
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    
    bot.reply_to(
        message, 
        "⚡ *THOR P2P COMMAND CENTER*\n"
        f"Min Amount: `${P2P_CONFIG['MIN_AMOUNT']}` | "
        f"Alert: `<{P2P_CONFIG['PROFIT_THRESHOLD']}`",
        reply_markup=markup, 
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['p2p_sync'])
def cmd_p2p_sync(message):
    """Quick sync command - moves funds from Funding to Trading"""
    user_id = str(message.from_user.id)
    
    keys = redis_client.get_user_keys(user_id)
    
    if not keys:
        bot.reply_to(message, "❌ Please /connect your Bybit account first")
        return
    
    # Show confirmation button
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(
        "🚀 Move ALL Funding → Trading", 
        callback_data=f"p2p_move_all_{user_id}"
    )
    markup.add(btn)
    
    bot.reply_to(
        message,
        "💰 *Funding Balance Detected*\n\n"
        "Click below to move all USDT from Funding to Unified Trading Account\n"
        f"*Broker:* `{P2P_CONFIG['BROKER_ID']}` (rebates enabled)",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# ==============================================================================
# CALLBACK HANDLERS - With Broker Tracking
# ==============================================================================

@bot.callback_query_handler(func=lambda call: call.data.startswith('p2p_'))
def handle_p2p_actions(call):
    """Handle all P2P button clicks"""
    data = call.data
    
    if data == "p2p_scan":
        bot.answer_callback_query(call.id, "Scanning P2P market...")
        asyncio.create_task(manual_scan_and_reply(call.message.chat.id))
        
    elif data == "p2p_orders":
        bot.answer_callback_query(call.id, "Fetching your P2P orders...")
        asyncio.create_task(fetch_p2p_orders(call.message.chat.id, call.from_user.id))
        
    elif data == "p2p_funding":
        bot.answer_callback_query(call.id, "Checking funding balance...")
        asyncio.create_task(check_funding_balance(call.message.chat.id, call.from_user.id))
        
    elif data.startswith("p2p_move_all_"):
        user_id = data.replace("p2p_move_all_", "")
        bot.answer_callback_query(call.id, "Moving funds...")
        asyncio.create_task(move_funds_to_trading(call.message.chat.id, user_id))
        
    elif data == "p2p_active":
        bot.answer_callback_query(call.id, "Fetching active deals...")
        asyncio.create_task(get_active_deals(call.message.chat.id, call.from_user.id))
        
    elif data == "p2p_settings":
        show_settings(call.message)

def show_settings(message):
    """Show current P2P configuration"""
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🔧 Edit Min Amount", callback_data="p2p_edit_min")
    btn2 = types.InlineKeyboardButton("💰 Edit Threshold", callback_data="p2p_edit_thresh")
    btn3 = types.InlineKeyboardButton("💱 Change Currency", callback_data="p2p_edit_curr")
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(
        message.chat.id,
        f"⚙️ *P2P Settings*\n\n"
        f"Min Amount: `${P2P_CONFIG['MIN_AMOUNT']}`\n"
        f"Profit Threshold: `<{P2P_CONFIG['PROFIT_THRESHOLD']}`\n"
        f"Currency: {P2P_CONFIG['CURRENCY']}\n"
        f"Scan Interval: {P2P_CONFIG['SCAN_INTERVAL']}s\n"
        f"Broker ID: `{P2P_CONFIG['BROKER_ID']}`",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# ==============================================================================
# ASYNC HELPER FUNCTIONS
# ==============================================================================

async def manual_scan_and_reply(chat_id):
    """Perform manual P2P scan with filters"""
    engine = ThorEngine(settings.MASTER_API_KEY, settings.MASTER_API_SECRET)
    
    try:
        result = await engine._request(
            "GET", 
            "/v5/p2p/item/online", 
            params={
                "coin": "USDT", 
                "currency": P2P_CONFIG["CURRENCY"], 
                "side": "0",
                "amount": str(P2P_CONFIG["MIN_AMOUNT"]),
                "size": 5
            }
        )
        
        if result.get('retCode') == 0 and result['result']['items']:
            items = result['result']['items']
            msg = f"🔍 *P2P MARKET SCAN (${P2P_CONFIG['MIN_AMOUNT']}+)*\n\n"
            
            for i, ad in enumerate(items[:5]):
                price = float(ad['price'])
                advertiser = ad['userName'][:10] + "..." if len(ad['userName']) > 10 else ad['userName']
                available = float(ad.get('quantity', 0))
                finish_rate = ad.get('finishRate', 0)
                
                profit = (1.0 - price) * min(available, P2P_CONFIG["MIN_AMOUNT"])
                
                msg += f"{i+1}. `${price:.4f}` | Profit: `${profit:.2f}`\n"
                msg += f"   {advertiser} ({finish_rate}%) - {available:.0f} USDT\n"
            
            bot.send_message(chat_id, msg, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, f"❌ No P2P ads ≥ ${P2P_CONFIG['MIN_AMOUNT']}")
            
    except Exception as e:
        bot.send_message(chat_id, f"❌ Scan failed: {str(e)[:50]}")

async def fetch_p2p_orders(chat_id, telegram_user_id):
    """Fetch user's P2P pending orders"""
    user_id = str(telegram_user_id)
    keys = redis_client.get_user_keys(user_id)
    
    if not keys:
        bot.send_message(chat_id, "❌ Please /connect your Bybit account first")
        return
    
    engine = ThorEngine(keys['api_key'], keys['api_secret'])
    
    try:
        result = await engine._request("GET", "/v5/p2p/order/pending/simplifyList", params={"size": 5})
        
        if result.get('retCode') == 0 and result['result']['items']:
            items = result['result']['items']
            msg = "📋 *Your P2P Orders*\n\n"
            
            for order in items:
                order_id = order.get('orderId', 'N/A')[:8]
                status = order.get('orderStatus', 'N/A')
                amount = order.get('amount', 'N/A')
                coin = order.get('coin', 'USDT')
                msg += f"• `{order_id}`: {status} - {amount} {coin}\n"
            
            bot.send_message(chat_id, msg, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "✅ No pending P2P orders")
            
    except Exception as e:
        bot.send_message(chat_id, f"❌ Failed: {str(e)[:50]}")

async def check_funding_balance(chat_id, telegram_user_id):
    """Check funding account balance"""
    user_id = str(telegram_user_id)
    keys = redis_client.get_user_keys(user_id)
    
    if not keys:
        bot.send_message(chat_id, "❌ Please /connect your Bybit account first")
        return
    
    engine = ThorEngine(keys['api_key'], keys['api_secret'])
    
    try:
        result = await engine._request(
            "GET", 
            "/v5/asset/transfer/query-account-coins-balance", 
            params={"accountType": "FUND"}
        )
        
        if result.get('retCode') == 0 and result['result']['balance']:
            balances = result['result']['balance']
            msg = "💰 *Funding Account Balance*\n\n"
            total = 0
            
            for coin in balances:
                coin_name = coin.get('coin', 'N/A')
                amount = float(coin.get('walletBalance', 0))
                if amount > 0:
                    msg += f"• {coin_name}: {amount:.4f}\n"
                    if coin_name == "USDT":
                        total += amount
            
            msg += f"\n*Total USDT:* {total:.2f}"
            bot.send_message(chat_id, msg, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "💰 Funding balance: $0.00")
            
    except Exception as e:
        bot.send_message(chat_id, f"❌ Failed: {str(e)[:50]}")

async def move_funds_to_trading(chat_id, telegram_user_id):
    """Move all USDT from Funding to Unified Trading with broker tracking"""
    user_id = str(telegram_user_id)
    keys = redis_client.get_user_keys(user_id)
    
    if not keys:
        bot.send_message(chat_id, "❌ Please /connect your Bybit account first")
        return
    
    engine = ThorEngine(keys['api_key'], keys['api_secret'])
    
    try:
        # Check funding balance
        balance_result = await engine._request(
            "GET", 
            "/v5/asset/transfer/query-account-coins-balance", 
            params={"accountType": "FUND", "coin": "USDT"}
        )
        
        usdt_amount = 0
        if balance_result.get('retCode') == 0 and balance_result['result']['balance']:
            for coin in balance_result['result']['balance']:
                if coin.get('coin') == 'USDT':
                    usdt_amount = float(coin.get('walletBalance', 0))
                    break
        
        if usdt_amount <= 0:
            bot.send_message(chat_id, "💰 No USDT found in Funding account")
            return
        
        # Create transfer with broker ID tracking
        transfer_id = f"p2p_{P2P_CONFIG['BROKER_ID']}_{uuid.uuid4().hex[:8]}"
        transfer_result = await engine._request(
            "POST",
            "/v5/asset/transfer/universal-transfer",
            data={
                "transferId": transfer_id,
                "coin": "USDT",
                "amount": str(round(usdt_amount, 2)),
                "fromAccountType": "FUND",
                "toAccountType": "UNIFIED"
            }
        )
        
        if transfer_result.get('retCode') == 0:
            bot.send_message(
                chat_id, 
                f"✅ *Transfer Complete*\n"
                f"Moved `{usdt_amount:.2f} USDT`\n"
                f"Funding → Unified\n"
                f"*Broker:* {P2P_CONFIG['BROKER_ID']}\n"
                f"*Tx ID:* `{transfer_id[:12]}...`",
                parse_mode="Markdown"
            )
            logger.info(f"💰 Transfer: {usdt_amount:.2f} USDT for user {telegram_user_id}")
        else:
            bot.send_message(chat_id, f"❌ Transfer failed: {transfer_result.get('retMsg', 'Unknown error')}")
            
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error: {str(e)[:50]}")

async def get_active_deals(chat_id, telegram_user_id):
    """Get user's active P2P deals"""
    user_id = str(telegram_user_id)
    keys = redis_client.get_user_keys(user_id)
    
    if not keys:
        bot.send_message(chat_id, "❌ Please /connect your Bybit account first")
        return
    
    engine = ThorEngine(keys['api_key'], keys['api_secret'])
    
    try:
        result = await engine._request(
            "GET", 
            "/v5/p2p/order/list", 
            params={"status": "IN_PROGRESS", "limit": 5}
        )
        
        if result.get('retCode') == 0 and result['result']['items']:
            items = result['result']['items']
            msg = "📊 *Active P2P Deals*\n\n"
            
            for deal in items:
                order_id = deal.get('orderId', 'N/A')[:8]
                price = deal.get('price', 'N/A')
                amount = deal.get('amount', 'N/A')
                side = "🔴 Buy" if deal.get('side') == 0 else "🟢 Sell"
                status = deal.get('orderStatus', 'Active')
                
                msg += f"{side}: {amount} USDT @ `${price}`\n"
                msg += f"   ID: `{order_id}` | {status}\n\n"
            
            bot.send_message(chat_id, msg, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "✅ No active P2P deals")
            
    except Exception as e:
        bot.send_message(chat_id, f"❌ Failed: {str(e)[:50]}")

# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    """Start the P2P plugin with scanner and Telegram bot"""
    logger.info("=" * 60)
    logger.info("🚀 NOVA GLOBAL KEYS - P2P ARBITRAGE PLUGIN v2.0 PRODUCTION")
    logger.info("=" * 60)
    logger.info(f"Broker: {P2P_CONFIG['BROKER_ID']}")
    logger.info(f"Min Amount: ${P2P_CONFIG['MIN_AMOUNT']}")
    logger.info(f"Profit Threshold: ${P2P_CONFIG['PROFIT_THRESHOLD']}")
    logger.info(f"Currency: {P2P_CONFIG['CURRENCY']}")
    logger.info("=" * 60)
    
    # Create async loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Start background scanner
    loop.create_task(p2p_arbitrage_scanner())
    logger.info("✅ P2P Arbitrage Scanner started")
    
    # Start Telegram bot in thread
    def run_bot():
        logger.info("🤖 Telegram P2P Bot listening...")
        bot.infinity_polling()
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Run forever
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("🛑 P2P Plugin shutting down...")
    finally:
        loop.close()

if __name__ == "__main__":
    main()
