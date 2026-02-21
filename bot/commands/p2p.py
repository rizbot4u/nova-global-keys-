"""P2P Trading Commands - REAL Bybit P2P API Integration"""
import threading
import httpx
import json
from datetime import datetime
from telebot import types
from core.redis_client import redis_client

P2P_API_URL = "https://api.bybit.com/v5/p2p"

def register_p2p_commands(bot):
    
    @bot.message_handler(commands=['p2p'])
    def cmd_p2p(message):
        """P2P trading menu"""
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("📊 View Ads", callback_data="p2p_ads_menu")
        btn2 = types.InlineKeyboardButton("📝 My Orders", callback_data="p2p_my_orders")
        btn3 = types.InlineKeyboardButton("➕ Buy Crypto", callback_data="p2p_create_buy")
        btn4 = types.InlineKeyboardButton("➖ Sell Crypto", callback_data="p2p_create_sell")
        markup.add(btn1, btn2, btn3, btn4)
        
        bot.reply_to(message,
            "🔄 *P2P Trading*\n\n"
            "Buy and sell crypto directly with other users.\n\n"
            "Select an option:",
            reply_markup=markup,
            parse_mode="Markdown"
        )
    
    @bot.message_handler(commands=['p2p_ads'])
    def cmd_p2p_ads(message):
        """Fetch real P2P advertisements from Bybit"""
        parts = message.text.split()
        token = parts[1].upper() if len(parts) > 1 else "USDT"
        fiat = parts[2].upper() if len(parts) > 2 else "USD"
        side = parts[3].upper() if len(parts) > 3 else "BUY"
        
        bot.reply_to(message, f"🔄 Fetching P2P {side} ads for {token}/{fiat}...")
        
        def fetch_ads():
            try:
                # Public endpoint - no auth needed
                response = httpx.post(
                    f"{P2P_API_URL}/item/online",
                    json={
                        "tokenId": token,
                        "currencyId": fiat,
                        "side": side,
                        "size": 10,
                        "page": 1
                    },
                    timeout=10,
                    headers={"Content-Type": "application/json"}
                )
                data = response.json()
                
                if data.get('retCode') == 0:
                    items = data.get('result', {}).get('items', [])
                    if not items:
                        bot.send_message(message.chat.id, f"📭 No {side} ads found for {token}/{fiat}")
                        return
                    
                    msg = f"📊 *P2P {side} Ads for {token}/{fiat}*\n\n"
                    for item in items[:5]:
                        price = float(item.get('price', 0))
                        min_amount = float(item.get('minAmount', 0))
                        max_amount = float(item.get('maxAmount', 0))
                        seller = item.get('nickName', 'Unknown')
                        completed = item.get('completedNum', 0)
                        payment = item.get('paymentMethods', ['Bank'])[0]
                        
                        msg += f"• *{seller}* (⭐ {completed} trades)\n"
                        msg += f"  Price: {price:.2f} {fiat}\n"
                        msg += f"  Limits: {min_amount:.0f} - {max_amount:.0f} {fiat}\n"
                        msg += f"  Payment: {payment}\n\n"
                    
                    bot.send_message(message.chat.id, msg, parse_mode="Markdown")
                else:
                    bot.send_message(message.chat.id, 
                        f"❌ Could not fetch ads: {data.get('retMsg', 'Unknown error')}")
                        
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
        
        threading.Thread(target=fetch_ads).start()
    
    @bot.message_handler(commands=['p2p_orders'])
    def cmd_p2p_orders(message):
        """Fetch REAL user P2P orders from Bybit"""
        user_id = str(message.from_user.id)
        keys = redis_client.get_user_keys(user_id)
        
        if not keys:
            bot.reply_to(message, "❌ Please /connect your Bybit account first")
            return
        
        bot.reply_to(message, "🔄 Fetching your REAL P2P orders...")
        
        def fetch_orders():
            try:
                # Get user's Bybit API keys for P2P
                # Note: P2P may require separate API keys with P2P permissions
                api_key = keys.get('api_key')
                api_secret = keys.get('api_secret')
                
                if not api_key:
                    bot.send_message(message.chat.id, "❌ No P2P API keys found")
                    return
                
                # Call Bybit P2P order list endpoint
                timestamp = str(int(datetime.now().timestamp() * 1000))
                recv_window = "5000"
                
                # Generate signature (simplified - use your ThorEngine method)
                import hmac
                import hashlib
                sign_str = f"{timestamp}{api_key}{recv_window}{json.dumps({'size': 10, 'page': 1})}"
                signature = hmac.new(
                    api_secret.encode('utf-8'),
                    sign_str.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
                
                headers = {
                    "X-BAPI-API-KEY": api_key,
                    "X-BAPI-TIMESTAMP": timestamp,
                    "X-BAPI-SIGN": signature,
                    "X-BAPI-RECV-WINDOW": recv_window,
                    "Content-Type": "application/json"
                }
                
                response = httpx.post(
                    f"{P2P_API_URL}/order/list",
                    headers=headers,
                    json={"size": 10, "page": 1},
                    timeout=10
                )
                data = response.json()
                
                if data.get('retCode') == 0:
                    orders = data.get('result', {}).get('list', [])
                    if not orders:
                        bot.send_message(message.chat.id, "📭 No P2P orders found")
                        return
                    
                    msg = "📦 *Your REAL P2P Orders*\n\n"
                    for order in orders:
                        status = order.get('orderStatus', 'UNKNOWN')
                        status_icon = {
                            'PENDING': '⏳',
                            'COMPLETED': '✅',
                            'CANCELLED': '❌',
                            'PAID': '💰',
                            'APPEALED': '⚠️'
                        }.get(status, '❓')
                        
                        msg += f"{status_icon} Order #{order.get('orderId', 'N/A')[:8]}\n"
                        msg += f"  {order.get('side')} {order.get('quantity')} {order.get('tokenId')}\n"
                        msg += f"  Price: {order.get('price')} {order.get('currencyId')}\n"
                        msg += f"  Status: {status}\n"
                        msg += f"  Created: {datetime.fromtimestamp(int(order.get('createdTime', 0))/1000).strftime('%Y-%m-%d %H:%M')}\n\n"
                    
                    bot.send_message(message.chat.id, msg, parse_mode="Markdown")
                    
                else:
                    bot.send_message(message.chat.id, 
                        f"❌ API Error: {data.get('retMsg', 'Unknown error')}")
                
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
        
        threading.Thread(target=fetch_orders).start()
    
    @bot.message_handler(commands=['p2p_buy', 'p2p_sell'])
    def cmd_p2p_create_order(message):
        """Create REAL P2P order"""
        cmd = message.text.split()[0]
        side = "BUY" if "buy" in cmd else "SELL"
        
        parts = message.text.split()
        if len(parts) < 4:
            bot.reply_to(message, f"❌ Usage: {cmd} [token] [amount] [price]\nExample: {cmd} USDT 100 1.01")
            return
        
        token = parts[1].upper()
        try:
            amount = float(parts[2])
            price = float(parts[3])
        except:
            bot.reply_to(message, "❌ Invalid amount or price")
            return
        
        user_id = str(message.from_user.id)
        keys = redis_client.get_user_keys(user_id)
        
        if not keys:
            bot.reply_to(message, "❌ Please /connect your Bybit account first")
            return
        
        bot.reply_to(message, f"🔄 Creating REAL P2P {side} order for {amount} {token} at ${price}...")
        
        def create_order():
            try:
                api_key = keys.get('api_key')
                api_secret = keys.get('api_secret')
                
                # Call Bybit P2P create order endpoint
                timestamp = str(int(datetime.now().timestamp() * 1000))
                recv_window = "5000"
                
                order_data = {
                    "tokenId": token,
                    "currencyId": "USD",
                    "side": side,
                    "quantity": str(amount),
                    "price": str(price)
                }
                
                # Generate signature
                import hmac
                import hashlib
                sign_str = f"{timestamp}{api_key}{recv_window}{json.dumps(order_data)}"
                signature = hmac.new(
                    api_secret.encode('utf-8'),
                    sign_str.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
                
                headers = {
                    "X-BAPI-API-KEY": api_key,
                    "X-BAPI-TIMESTAMP": timestamp,
                    "X-BAPI-SIGN": signature,
                    "X-BAPI-RECV-WINDOW": recv_window,
                    "Content-Type": "application/json"
                }
                
                response = httpx.post(
                    f"{P2P_API_URL}/order/create",
                    headers=headers,
                    json=order_data,
                    timeout=10
                )
                data = response.json()
                
                if data.get('retCode') == 0:
                    order_id = data.get('result', {}).get('orderId', 'N/A')
                    msg = (
                        f"✅ *P2P Order Created Successfully!*\n\n"
                        f"Order ID: `{order_id}`\n"
                        f"Side: {side}\n"
                        f"Token: {token}\n"
                        f"Amount: {amount}\n"
                        f"Price: ${price}\n\n"
                        f"Track your order:\n"
                        f"https://www.bybit.com/p2p/order/{order_id}"
                    )
                    bot.send_message(message.chat.id, msg, parse_mode="Markdown")
                else:
                    bot.send_message(message.chat.id, 
                        f"❌ Order failed: {data.get('retMsg', 'Unknown error')}")
                
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
        
        threading.Thread(target=create_order).start()
    
    # Callback handlers
    @bot.callback_query_handler(func=lambda call: call.data.startswith('p2p_'))
    def handle_p2p_callbacks(call):
        if call.data == "p2p_ads_menu":
            markup = types.InlineKeyboardMarkup(row_width=3)
            currencies = [
                ("USDT/USD", "p2p_ads_USDT_USD_BUY"),
                ("BTC/USD", "p2p_ads_BTC_USD_BUY"),
                ("ETH/USD", "p2p_ads_ETH_USD_BUY"),
                ("USDT/EUR", "p2p_ads_USDT_EUR_BUY"),
                ("USDT/GBP", "p2p_ads_USDT_GBP_BUY"),
                ("USDT/AED", "p2p_ads_USDT_AED_BUY")
            ]
            for label, callback_data in currencies:
                markup.add(types.InlineKeyboardButton(label, callback_data=callback_data))
            
            bot.edit_message_text(
                "📊 *Select Market to View Ads*",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode="Markdown"
            )
        
        elif call.data.startswith("p2p_ads_"):
            parts = call.data.split('_')
            token = parts[2]
            fiat = parts[3]
            side = parts[4] if len(parts) > 4 else "BUY"
            
            class MockMessage:
                def __init__(self, chat, text):
                    self.chat = type('obj', (object,), {'id': chat})
                    self.text = text
            
            mock_msg = MockMessage(call.message.chat.id, f"/p2p_ads {token} {fiat} {side}")
            cmd_p2p_ads(mock_msg)
        
        elif call.data == "p2p_my_orders":
            cmd_p2p_orders(call.message)
        
        elif call.data == "p2p_create_buy":
            bot.send_message(call.message.chat.id,
                "💰 *Create Buy Order*\n\n"
                "Use: `/p2p_buy USDT 100 1.01`\n\n"
                "Parameters:\n"
                "• Token: USDT, BTC, ETH\n"
                "• Amount: How much to buy\n"
                "• Price: Your offer price\n\n"
                "Example: `/p2p_buy USDT 100 1.01`",
                parse_mode="Markdown")
        
        elif call.data == "p2p_create_sell":
            bot.send_message(call.message.chat.id,
                "💸 *Create Sell Order*\n\n"
                "Use: `/p2p_sell USDT 100 1.00`\n\n"
                "Parameters:\n"
                "• Token: USDT, BTC, ETH\n"
                "• Amount: How much to sell\n"
                "• Price: Your asking price\n\n"
                "Example: `/p2p_sell USDT 100 1.00`",
                parse_mode="Markdown")
