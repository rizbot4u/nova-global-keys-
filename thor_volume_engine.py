#!/usr/bin/env python3
"""
NOVA GLOBAL KEYS - VOLUME ENGINE v1.0
High-frequency trading engine with slippage protection & broker rebates
Author: Nova Global Keys | Broker: Kr000820
"""

import asyncio
import logging
import uuid
import time
from datetime import datetime
import threading

import telebot
from telebot import types

from thor_engine import ThorEngine, settings, redis_client

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("nova-volume")

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)

# ==============================================================================
# SLIPPAGE-AWARE ORDER SIZER - CRITICAL FOR VOLUME GENERATION
# ==============================================================================

class SlippageProtection:
    """Calculates safe order sizes based on orderbook depth"""
    
    @staticmethod
    async def get_safe_volume_size(engine: ThorEngine, symbol: str = "BTCUSDT", max_slippage: float = 0.001, side: str = "buy"):
        """
        Calculate maximum order size that won't exceed slippage threshold
        max_slippage: 0.001 = 0.1% price impact
        """
        try:
            # Get current orderbook
            ob = await engine.get_orderbook(category="spot", symbol=symbol, limit=50)
            
            if ob.get('retCode') != 0:
                logger.error(f"Failed to get orderbook: {ob}")
                return 0
            
            # For buy orders, look at asks (sell side)
            # For sell orders, look at bids (buy side)
            if side.lower() == "buy":
                orders = ob['result']['a']  # asks
                best_price = float(orders[0][0])
                max_price = best_price * (1 + max_slippage)
            else:
                orders = ob['result']['b']  # bids
                best_price = float(orders[0][0])
                max_price = best_price * (1 - max_slippage)  # Lower price for sells
            
            safe_qty = 0
            qty_reached = 0
            
            for price_str, qty_str in orders:
                price = float(price_str)
                
                # Stop if we exceed slippage threshold
                if side.lower() == "buy" and price > max_price:
                    break
                if side.lower() == "sell" and price < max_price:
                    break
                
                qty = float(qty_str)
                safe_qty += qty
                qty_reached += 1
                
                # Safety: Don't look at too many levels
                if qty_reached >= 20:
                    break
            
            # STEALTH MODE: Only use 20% of available depth to avoid detection
            stealth_qty = safe_qty * 0.20
            
            logger.info(f"📊 {symbol} {side.capitalize()} - Safe: {safe_qty:.4f} | Stealth: {stealth_qty:.4f} @ {max_slippage*100:.2f}% slippage")
            
            return stealth_qty
            
        except Exception as e:
            logger.error(f"Slippage calculation error: {e}")
            return 0

# ==============================================================================
# VOLUME GENERATION ENGINE - FOR BROKER REBATES
# ==============================================================================

async def volume_generator():
    """Generates volume for broker rebates while managing risk"""
    logger.info("🚀 Volume Generator Started - Earning rebates for Kr000820")
    
    engine = ThorEngine(settings.MASTER_API_KEY, settings.MASTER_API_SECRET)
    slippage = SlippageProtection()
    
    # Track volume
    total_volume = 0
    trade_count = 0
    start_time = time.time()
    
    while True:
        try:
            # 1. Get safe order size for BTCUSDT
            btc_qty = await slippage.get_safe_volume_size(engine, "BTCUSDT", max_slippage=0.0005, side="buy")
            
            if btc_qty < 0.0001:  # Too small, try ETH
                eth_qty = await slippage.get_safe_volume_size(engine, "ETHUSDT", max_slippage=0.0005, side="buy")
                
                if eth_qty < 0.001:
                    logger.warning("⚠️ Market too thin, waiting...")
                    await asyncio.sleep(30)
                    continue
                
                # Place ETH trade
                order = await engine.place_order(
                    category="spot",
                    symbol="ETHUSDT",
                    side="Buy",
                    order_type="Market",
                    qty=str(round(eth_qty, 4))
                )
                
                if order.get('retCode') == 0:
                    # Sell immediately for volume (round trip)
                    await asyncio.sleep(2)  # Brief pause
                    sell_order = await engine.place_order(
                        category="spot",
                        symbol="ETHUSDT",
                        side="Sell",
                        order_type="Market",
                        qty=str(round(eth_qty, 4))
                    )
                    
                    if sell_order.get('retCode') == 0:
                        volume = eth_qty * 2000  # Approx ETH price
                        total_volume += volume
                        trade_count += 2
                        logger.info(f"✅ ETH Trade: {eth_qty:.4f} ETH | Volume: ${volume:.2f}")
                        
            else:
                # Place BTC trade
                order = await engine.place_order(
                    category="spot",
                    symbol="BTCUSDT",
                    side="Buy",
                    order_type="Market",
                    qty=str(round(btc_qty, 4))
                )
                
                if order.get('retCode') == 0:
                    # Sell immediately
                    await asyncio.sleep(2)
                    sell_order = await engine.place_order(
                        category="spot",
                        symbol="BTCUSDT",
                        side="Sell",
                        order_type="Market",
                        qty=str(round(btc_qty, 4))
                    )
                    
                    if sell_order.get('retCode') == 0:
                        volume = btc_qty * 60000  # BTC price
                        total_volume += volume
                        trade_count += 2
                        logger.info(f"✅ BTC Trade: {btc_qty:.4f} BTC | Volume: ${volume:.2f}")
            
            # Report stats every 10 trades
            if trade_count >= 10:
                elapsed = time.time() - start_time
                volume_per_hour = (total_volume / elapsed) * 3600
                
                logger.info("=" * 60)
                logger.info(f"📈 VOLUME STATS - Broker: Kr000820")
                logger.info(f"   Total Volume: ${total_volume:,.2f}")
                logger.info(f"   Trades: {trade_count}")
                logger.info(f"   Run Time: {elapsed/60:.1f} minutes")
                logger.info(f"   Projected Hourly: ${volume_per_hour:,.2f}")
                logger.info("=" * 60)
                
                # Reset counters
                trade_count = 0
            
            # Random delay to avoid patterns (20-40 seconds)
            delay = 20 + (hash(str(time.time())) % 20)
            await asyncio.sleep(delay)
            
        except Exception as e:
            logger.error(f"Volume generator error: {e}")
            await asyncio.sleep(60)

# ==============================================================================
# TELEGRAM COMMANDS
# ==============================================================================

@bot.message_handler(commands=['volume'])
def cmd_volume(message):
    """Check volume stats and broker rebates"""
    user_id = str(message.from_user.id)
    keys = redis_client.get_user_keys(user_id)
    
    if not keys:
        bot.reply_to(message, "❌ Please /connect your Bybit account first")
        return
    
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🚀 Start Volume Bot", callback_data="vol_start")
    btn2 = types.InlineKeyboardButton("📊 Stats", callback_data="vol_stats")
    btn3 = types.InlineKeyboardButton("💰 Broker Rebates", callback_data="vol_rebates")
    markup.add(btn1, btn2, btn3)
    
    bot.reply_to(
        message,
        "⚡ *THOR VOLUME ENGINE*\n\n"
        "Generate volume and earn broker rebates with slippage protection.\n"
        f"*Broker:* `Kr000820`\n"
        f"*Max Slippage:* 0.05% (stealth mode)",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['p2p'])
def cmd_p2p_manual(message):
    """P2P assistance (manual only - no scraping)"""
    bot.reply_to(
        message,
        "🤝 *P2P TRADING ASSISTANT*\n\n"
        "Due to Bybit's API restrictions, automated P2P scraping is not available.\n\n"
        "*Available Commands:*\n"
        "• `/p2p_balance` - Check funding balance\n"
        "• `/p2p_orders` - View your P2P orders\n"
        "• `/p2p_sync` - Move funds to trading\n\n"
        "For P2P ads, please use the Bybit app manually.\n"
        "[Open Bybit P2P](https://www.bybit.com/fiat)",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

@bot.message_handler(commands=['p2p_balance'])
def cmd_p2p_balance(message):
    """Check funding balance"""
    user_id = str(message.from_user.id)
    keys = redis_client.get_user_keys(user_id)
    
    if not keys:
        bot.reply_to(message, "❌ Please /connect your Bybit account first")
        return
    
    bot.reply_to(message, "🔄 Checking funding balance...")
    
    async def check_balance():
        engine = ThorEngine(keys['api_key'], keys['api_secret'])
        try:
            result = await engine._request(
                "GET",
                "/v5/asset/transfer/query-account-coins-balance",
                params={"accountType": "FUND"}
            )
            
            if result.get('retCode') == 0 and result['result']['balance']:
                balances = result['result']['balance']
                msg = "💰 *Funding Balance*\n\n"
                total = 0
                
                for coin in balances:
                    coin_name = coin.get('coin', '')
                    amount = float(coin.get('walletBalance', 0))
                    if amount > 0:
                        msg += f"• {coin_name}: {amount:.4f}\n"
                        if coin_name == "USDT":
                            total += amount
                
                msg += f"\n*Total USDT:* `${total:.2f}`"
                bot.send_message(message.chat.id, msg, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "💰 Funding balance: $0.00")
                
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {str(e)[:50]}")
    
    asyncio.create_task(check_balance())

# ==============================================================================
# CALLBACK HANDLERS
# ==============================================================================

@bot.callback_query_handler(func=lambda call: call.data.startswith('vol_'))
def handle_volume_actions(call):
    data = call.data
    
    if data == "vol_start":
        bot.answer_callback_query(call.id, "Volume bot running in background")
        bot.send_message(
            call.message.chat.id,
            "🚀 *Volume Bot Started*\n\n"
            "The engine is now generating volume with 0.05% slippage protection.\n"
            "Check `/volume` for stats.",
            parse_mode="Markdown"
        )
        # Volume generator runs continuously, no need to start again
        
    elif data == "vol_stats":
        bot.answer_callback_query(call.id, "Fetching stats...")
        # Stats are logged, could implement Redis storage for persistent stats
        
    elif data == "vol_rebates":
        bot.answer_callback_query(call.id, "Checking rebates...")
        bot.send_message(
            call.message.chat.id,
            f"💰 *Broker Rebates*\n\n"
            f"Broker ID: `Kr000820`\n"
            f"Rebates are tracked by Bybit and credited monthly.\n\n"
            f"Check your [Affiliate Dashboard](https://www.bybit.com/user/affiliate)",
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    logger.info("=" * 60)
    logger.info("🚀 NOVA GLOBAL KEYS - VOLUME ENGINE v1.0")
    logger.info("=" * 60)
    logger.info(f"Broker: Kr000820")
    logger.info(f"Strategy: Slippage-Protected Round Trips")
    logger.info(f"Max Slippage: 0.05% (stealth mode)")
    logger.info("=" * 60)
    
    # Create async loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Start volume generator
    loop.create_task(volume_generator())
    logger.info("✅ Volume Generator started")
    
    # Start Telegram bot
    def run_bot():
        logger.info("🤖 Telegram Volume Bot listening...")
        bot.infinity_polling()
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Volume Engine shutting down...")
    finally:
        loop.close()

if __name__ == "__main__":
    main()
