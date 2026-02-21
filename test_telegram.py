#!/usr/bin/env python3
"""
Test Telegram Bot Connection
"""
import telebot
import time

TOKEN = "8589207540:AAFFeNYGWfadLna4yrUEfRgj4m8xnFanVZs"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "✅ Bot is working! Test successful.")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, f"You said: {message.text}")

print("🤖 Test bot starting...")
print("Send /start to @Novaglobalkeysbot")
bot.infinity_polling()
