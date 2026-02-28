#!/usr/bin/env python3
"""
NOVA DAILY REPORTER - Fixed with correct Bybit endpoints
"""

import os
import sys
import json
import time
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Dict
import redis
import telebot
import httpx
from dotenv import load_dotenv

load_dotenv()

class Settings:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    BROKER_CODE = os.getenv("BROKER_CODE", "Kr000820")
    MASTER_API_KEY = os.getenv("MASTER_API_KEY", "")
    MASTER_API_SECRET = os.getenv("MASTER_API_SECRET", "")
    BYBIT_API = "https://api.bybit.id/v5"

settings = Settings()

class RedisClient:
    def __init__(self):
        self.client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        print(f"✅ Redis connected")
    
    def get_stats(self) -> Dict:
        return {
            'total_requests': self.client.get("stats:main_api:total_requests") or "0",
            'heartbeat': self.client.get("worker:last_heartbeat") or "N/A",
            'warrior_status': self.client.get("nova:status:warrior_01") or "{}"
        }

redis_client = RedisClient()

class BybitProfitTracker:
    def __init__(self):
        self.api_key = settings.MASTER_API_KEY
        self.api_secret = settings.MASTER_API_SECRET
        self.recv_window = "20000"
        self.base_url = settings.BYBIT_API
        self.broker_code = settings.BROKER_CODE
    
    def _generate_signature(self, timestamp: str, params: str = "") -> str:
        if not self.api_secret:
            return ""
        sign_str = f"{timestamp}{self.api_key}{self.recv_window}{params}"
        return hmac.new(
            self.api_secret.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _request(self, method: str, endpoint: str, params: dict = None) -> Dict:
        if not self.api_key or not self.api_secret:
            return {"retCode": -1, "retMsg": "No API keys"}
        
        timestamp = str(int(time.time() * 1000))
        
        query_string = ""
        if params and method == "GET":
            query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items()) if v])
        
        signature = self._generate_signature(timestamp, query_string)
        
        headers = {
            "X-BAPI-API-KEY": self.api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-SIGN": signature,
            "X-BAPI-RECV-WINDOW": self.recv_window,
            "X-Referer": self.broker_code,
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}{endpoint}"
        if query_string:
            url = f"{url}?{query_string}"
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, headers=headers)
                return response.json()
        except Exception as e:
            print(f"❌ API Error: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    def get_24h_profit(self) -> Dict:
        try:
            end_time = int(time.time() * 1000)
            start_time = int((datetime.now() - timedelta(hours=24)).timestamp() * 1000)
            
            print(f"🔍 Fetching closed PnL...")
            
            # First try with spot category
            params = {
                "category": "spot",
                "limit": 50,
                "startTime": start_time,
                "endTime": end_time
            }
            
            result = self._request("GET", "/v5/position/closed-pnl", params=params)
            
            # If spot fails, try linear
            if result.get('retCode') != 0:
                print("🔍 Spot failed, trying linear...")
                params["category"] = "linear"
                result = self._request("GET", "/v5/position/closed-pnl", params=params)
            
            # If both fail, try getting current positions
            if result.get('retCode') != 0:
                print("🔍 No closed trades, checking current positions...")
                pos_params = {
                    "category": "linear",
                    "limit": 50
                }
                pos_result = self._request("GET", "/v5/position/list", params=pos_params)
                
                if pos_result.get('retCode') == 0:
                    positions = pos_result.get('result', {}).get('list', [])
                    total_profit = 0.0
                    winning_trades = 0
                    total_trades = 0
                    symbol_profit = {}
                    
                    for pos in positions:
                        if float(pos.get('size', 0)) > 0:
                            pnl = float(pos.get('unrealisedPnl', 0))
                            symbol = pos.get('symbol', 'UNKNOWN')
                            
                            if pnl != 0:
                                total_profit += pnl
                                total_trades += 1
                                if pnl > 0:
                                    winning_trades += 1
                                symbol_profit[symbol] = symbol_profit.get(symbol, 0) + pnl
                    
                    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                    
                    return {
                        'total_profit': round(total_profit, 2),
                        'trade_count': total_trades,
                        'win_rate': round(win_rate, 1),
                        'winning_trades': winning_trades,
                        'symbols': symbol_profit
                    }
            
            # Process closed PnL results
            total_profit = 0.0
            winning_trades = 0
            total_trades = 0
            symbol_profit = {}
            
            if result.get('retCode') == 0:
                trades = result.get('result', {}).get('list', [])
                print(f"🔍 Found {len(trades)} trades")
                
                for trade in trades:
                    pnl = float(trade.get('closedPnl', 0))
                    symbol = trade.get('symbol', 'UNKNOWN')
                    
                    total_profit += pnl
                    total_trades += 1
                    
                    if pnl > 0:
                        winning_trades += 1
                    
                    symbol_profit[symbol] = symbol_profit.get(symbol, 0) + pnl
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            return {
                'total_profit': round(total_profit, 2),
                'trade_count': total_trades,
                'win_rate': round(win_rate, 1),
                'winning_trades': winning_trades,
                'symbols': symbol_profit
            }
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {
                'total_profit': 0,
                'trade_count': 0,
                'win_rate': 0,
                'winning_trades': 0,
                'symbols': {}
            }

class DailyReporter:
    def __init__(self):
        self.bot = telebot.TeleBot(settings.TELEGRAM_TOKEN) if settings.TELEGRAM_TOKEN else None
        self.chat_id = settings.ADMIN_CHAT_ID
    
    def send_report(self):
        print(f"📊 Generating daily report...")
        
        stats = redis_client.get_stats()
        tracker = BybitProfitTracker()
        profit_data = tracker.get_24h_profit()
        
        heartbeat = stats['heartbeat']
        if heartbeat != "N/A":
            try:
                heartbeat_time = datetime.fromisoformat(heartbeat).strftime('%H:%M:%S')
            except:
                heartbeat_time = heartbeat[:19]
        else:
            heartbeat_time = "N/A"
        
        profit_emoji = "📈" if profit_data['total_profit'] > 0 else "📉" if profit_data['total_profit'] < 0 else "⚖️"
        
        report = f"""
📊 *NOVA DAILY SUMMARY*
📅 Date: {datetime.now().strftime('%Y-%m-%d')}
━━━━━━━━━━━━━━━━━━━━━

🚀 *API Statistics*
• Total Requests: `{stats['total_requests']}`
• Last Heartbeat: `{heartbeat_time}`
• System Status: `OPERATIONAL`

💰 *Trading Performance {profit_emoji}*
• 24h Net Profit: `{profit_data['total_profit']:+.2f} USDT`
• Trade Count: `{profit_data['trade_count']}`
• Win Rate: `{profit_data['win_rate']}%`

📊 *Top Performers*
"""
        
        # Add top 3 symbols
        sorted_symbols = sorted(profit_data['symbols'].items(), key=lambda x: x[1], reverse=True)[:3]
        if sorted_symbols:
            for symbol, pnl in sorted_symbols:
                report += f"• {symbol}: `{pnl:+.2f} USDT`\n"
        else:
            report += "• No trades in last 24h\n"
        
        report += f"""
━━━━━━━━━━━━━━━━━━━━━
🛡️ *Broker:* `{settings.BROKER_CODE}`
⏰ Generated: {datetime.now().strftime('%H:%M:%S')}
"""
        
        if self.bot and self.chat_id:
            try:
                self.bot.send_message(self.chat_id, report, parse_mode="Markdown")
                print("✅ Report sent to Telegram")
            except Exception as e:
                print(f"❌ Telegram error: {e}")
                print(report)
        else:
            print(report)
        
        return report

def main():
    print("="*60)
    print("🚀 NOVA DAILY REPORTER")
    print("="*60)
    
    reporter = DailyReporter()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        reporter.send_report()
    else:
        import schedule
        schedule.every().day.at("00:00").do(reporter.send_report)
        print("📈 Waiting for midnight...")
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    main()
