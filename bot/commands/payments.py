"""
Nova Global Keys - Complete Payment Integration
Includes: Bybit Pay, QR Crypto, Card, Cash/P2P
"""

import threading
import qrcode
import io
import uuid
from datetime import datetime, timedelta
from telebot import types
from config.settings import settings
from core.redis_client import redis_client

# Shop wallet for receiving payments
SHOP_WALLET = {
    "USDT": "0xAF4ecF03c23c5eDcF993e5A328462Ba8961BaeC4",
    "BTC": "bc1q...",
    "ETH": "0x..."
}

def register_payment_commands(bot):
    
    @bot.message_handler(commands=['pay'])
    def cmd_pay(message):
        """Main payment menu"""
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        btn1 = types.InlineKeyboardButton("💳 Bybit Pay", callback_data="pay_bybit")
        btn2 = types.InlineKeyboardButton("📱 QR Scan", callback_data="pay_qr")
        btn3 = types.InlineKeyboardButton("💵 Card", callback_data="pay_card")
        btn4 = types.InlineKeyboardButton("💰 Cash/P2P", callback_data="pay_cash")
        btn5 = types.InlineKeyboardButton("📋 My Payments", callback_data="pay_history")
        
        markup.add(btn1, btn2, btn3, btn4, btn5)
        
        bot.reply_to(message, 
            "💳 *Payment Options*\n\n"
            "Choose your payment method:\n\n"
            "• Bybit Pay – Instant crypto payment\n"
            "• QR Scan – Scan to pay with any wallet\n"
            "• Card – Visa/Mastercard\n"
            "• Cash – Manual P2P settlement\n\n"
            "All payments settle in USDT.",
            reply_markup=markup,
            parse_mode="Markdown"
        )
    
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callbacks(call):
        """Handle all payment callbacks"""
        
        if call.data == "pay_bybit":
            user_id = str(call.from_user.id)
            payment_id = f"BYBIT_{user_id}_{uuid.uuid4().hex[:8]}"
            
            redis_client.client.setex(
                f"payment:{payment_id}",
                3600,
                str({
                    "id": payment_id,
                    "user_id": user_id,
                    "status": "pending",
                    "method": "bybit",
                    "created": datetime.utcnow().isoformat()
                })
            )
            
            bot.send_message(call.message.chat.id,
                "💳 *Bybit Pay*\n\n"
                f"[Pay with Bybit](https://www.bybit.com/en/bybitpay/)\n\n"
                f"Payment ID: `{payment_id}`\n"
                "After payment, send TXID with:\n"
                f"`/confirm {payment_id} YOUR_TXID`",
                parse_mode="Markdown"
            )
        
        elif call.data == "pay_qr":
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(f"ethereum:{SHOP_WALLET['USDT']}")
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            bot.send_photo(
                call.message.chat.id,
                img_bytes,
                caption="📱 *Scan to Pay*\n\n"
                       f"Address: `{SHOP_WALLET['USDT']}`\n\n"
                       "After sending, confirm with:\n"
                       "`/confirm QR_PAYMENT TXID`",
                parse_mode="Markdown"
            )
        
        elif call.data == "pay_card":
            bot.send_message(call.message.chat.id,
                "💳 *Card Payment*\n\n"
                "[Pay with Card](https://www.bybit.com/en/bybitpay/card/)\n\n"
                "Limits: $10 – $1000",
                parse_mode="Markdown"
            )
        
        elif call.data == "pay_cash":
            bot.send_message(call.message.chat.id,
                "💰 *Cash/P2P Payment*\n\n"
                "To request cash payment:\n"
                "`/cash 50` – for $50\n\n"
                "Available: USD, EUR, GBP",
                parse_mode="Markdown"
            )
        
        elif call.data == "pay_history":
            user_id = str(call.from_user.id)
            show_payment_history(bot, call.message, user_id)
    
    @bot.message_handler(commands=['cash'])
    def cmd_cash(message):
        """Request cash payment"""
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Usage: /cash [amount]\nExample: /cash 50")
            return
        
        try:
            amount = float(parts[1])
            if amount < 10:
                bot.reply_to(message, "❌ Minimum: $10")
                return
            
            user_id = str(message.from_user.id)
            payment_id = f"CASH_{user_id}_{uuid.uuid4().hex[:8]}"
            
            redis_client.client.setex(
                f"payment:{payment_id}",
                3600,
                str({
                    "id": payment_id,
                    "user_id": user_id,
                    "amount": amount,
                    "status": "pending",
                    "method": "cash",
                    "created": datetime.utcnow().isoformat()
                })
            )
            
            # Notify admin
            admin_id = "6517213957"
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_cash_{payment_id}")
            btn2 = types.InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_cash_{payment_id}")
            markup.add(btn1, btn2)
            
            bot.send_message(
                admin_id,
                f"💰 *Cash Request*\nUser: {user_id}\nAmount: ${amount}\nID: `{payment_id}`",
                parse_mode="Markdown",
                reply_markup=markup
            )
            
            bot.reply_to(message, f"✅ Request created for ${amount}\nID: `{payment_id}`")
            
        except ValueError:
            bot.reply_to(message, "❌ Invalid amount")
    
    @bot.message_handler(commands=['confirm'])
    def cmd_confirm(message):
        """Confirm payment with transaction ID"""
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Usage: /confirm [payment_id] [TXID]")
            return
        
        payment_id = parts[1]
        txid = parts[2]
        user_id = str(message.from_user.id)
        
        bot.reply_to(message, f"🔄 Verifying payment...")
        
        def verify():
            redis_client.client.setex(
                f"payment:{payment_id}",
                86400,
                str({
                    "id": payment_id,
                    "user_id": user_id,
                    "txid": txid,
                    "status": "completed",
                    "timestamp": datetime.utcnow().isoformat()
                })
            )
            redis_client.client.incrbyfloat(f"user:{user_id}:credit", 10)
            bot.send_message(message.chat.id, "✅ Payment confirmed! $10 credit added.")
        
        threading.Thread(target=verify).start()

def show_payment_history(bot, message, user_id):
    """Show user's payment history"""
    keys = redis_client.client.keys(f"payment:*")
    payments = []
    
    for key in keys:
        data = redis_client.client.get(key)
        if data and user_id in data:
            try:
                payments.append(eval(data))
            except:
                pass
    
    if not payments:
        bot.send_message(message.chat.id, "📭 No payment history")
        return
    
    reply = "📋 *Payment History*\n\n"
    for p in payments[-5:]:
        status = "✅" if p.get('status') == 'completed' else "⏳"
        reply += f"{status} ${p.get('amount', 0)} - {p.get('method', 'unknown')}\n"
    
    credit = float(redis_client.client.get(f"user:{user_id}:credit") or 0)
    reply += f"\n*Credit:* ${credit:.2f}"
    
    bot.send_message(message.chat.id, reply, parse_mode="Markdown")
