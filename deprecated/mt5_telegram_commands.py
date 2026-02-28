"""
Add these to your Telegram bot handler
"""

# Add to your message handler:
@bot.message_handler(commands=['tradfi'])
def handle_tradfi(message):
    """Handle /tradfi command - show TradFi menu"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    btn1 = telebot.types.InlineKeyboardButton("🥇 Gold", callback_data="tradfi_XAUUSD")
    btn2 = telebot.types.InlineKeyboardButton("🍎 Apple", callback_data="tradfi_AAPL")
    btn3 = telebot.types.InlineKeyboardButton("🚗 Tesla", callback_data="tradfi_TSLA")
    btn4 = telebot.types.InlineKeyboardButton("📊 NASDAQ", callback_data="tradfi_NAS100")
    btn5 = telebot.types.InlineKeyboardButton("💰 Forex", callback_data="tradfi_EURUSD")
    btn6 = telebot.types.InlineKeyboardButton("📈 All", callback_data="tradfi_all")
    
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    
    bot.reply_to(
        message,
        "🌍 *Nova TradFi - Gold & Stocks*\n\n"
        "Select an asset to check price:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('tradfi_'))
def handle_tradfi_callback(call):
    """Handle TradFi button clicks"""
    symbol = call.data.replace('tradfi_', '')
    
    if symbol == 'all':
        # Fetch all prices
        bot.edit_message_text(
            "🔄 Fetching all TradFi prices...",
            call.message.chat.id,
            call.message.message_id
        )
        # Make API call to your Thor Engine
        # response = requests.get("http://localhost:8080/api/v1/tradfi/prices")
        # Format and send response
        bot.send_message(
            call.message.chat.id,
            "📊 *All TradFi Prices*\n\n"
            "🥇 XAUUSD: $2,345.67 (+0.45%)\n"
            "🍎 AAPL: $175.32 (-0.23%)\n"
            "🚗 TSLA: $245.67 (+1.23%)\n"
            "📊 NAS100: 18,456.78 (+0.67%)\n\n"
            "⚙️ Full integration coming soon!",
            parse_mode="Markdown"
        )
    else:
        # Fetch single symbol
        bot.edit_message_text(
            f"🔄 Fetching {symbol}...",
            call.message.chat.id,
            call.message.message_id
        )
        # Make API call to your Thor Engine
        # response = requests.get(f"http://localhost:8080/api/v1/tradfi/price/{symbol}")
        bot.send_message(
            call.message.chat.id,
            f"📈 *{symbol}*\n\n"
            f"Price: $2,345.67\n"
            f"Change: +0.45%\n\n"
            f"⚙️ Full integration coming soon!",
            parse_mode="Markdown"
        )
