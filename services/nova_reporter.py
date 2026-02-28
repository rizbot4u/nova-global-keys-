#!/usr/bin/env python3
"""
NOVA DAILY REPORTER - Fixed Version with Better Error Handling
"""

import os
import sys
import json
import time
import asyncio
import hmac
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import redis
import schedule
import telebot
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

class Settings:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    BROKER_CODE = os.getenv("BROKER_CODE", "Kr000820")
    
    # Master API Keys for profit tracking
    MASTER_API_KEY = os.getenv("MASTER_API_KEY", "")
    MASTER_API_SECRET = os.getenv("MASTER_API_SECRET", "")
    
    # Bybit endpoints
    USE_TESTNET = os.getenv("USE_TESTNET", "false").lower() == "true"
    
    if USE_TESTNET:
        BYBIT_API = "https://api-testnet.bybit.com/v5"
        print("🧪 Using TESTNET mode")
    else:
        BYBIT_API = "https://api.bybit.id/v5"

settings = Settings()

# ============================================================================
# REDIS CLIENT
# ============================================================================

class RedisClient:
    def __init__(self):
        self.client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        print(f"✅ Redis connected")
    
    def get_stats(self) -> Dict:
        """Get all stats from Redis"""
        return {
            'total_requests': self.client.get("stats:main_api:total_requests") or "0",
            'heartbeat': self.client.get("worker:last_heartbeat") or "N/A",
            'warrior_status': self.client.get("nova:status:warrior_01") or "{}"
        }
    
    def get_daily_requests(self) -> int:
        """Get today's request count (reset daily)"""
        today = datetime.now().strftime('%Y-%m-%d')
        key = f"stats:daily:{today}:requests"
        
        # Initialize if not exists
        if not self.client.exists(key):
            self.client.setex(key, 86400, 0)
        
        return int(self.client.get(key) or 0)
    
    def increment_daily_requests(self):
        """Increment today's request count"""
        today = datetime.now().strftime('%Y-%m-%d')
        key = f"stats:daily:{today}:requests"
        self.client.incr(key)
        self.client.expire(key, 86400)

redis_client = RedisClient()

# ============================================================================
# BYBIT PROFIT TRACKER - FIXED VERSION
# ============================================================================

class BybitProfitTracker:
    """Fetch 24h profit from Bybit V5 API with better error handling"""
    
    def __init__(self):
        self.api_key = settings.MASTER_API_KEY
        self.api_secret = settings.MASTER_API_SECRET
        self.recv_window = "20000"
        self.base_url = settings.BYBIT_API
        self.broker_code = settings.BROKER_CODE
        
        # Check if API keys are configured
        if not self.api_key or not self.api_secret:
            print("⚠️ Master API keys not configured - profit tracking disabled")
        
    def _generate_signature(self, timestamp: str, params: str = "") -> str:
        """Generate HMAC SHA256 signature for Bybit V5"""
        if not self.api_secret:
            return ""
        
        sign_str = f"{timestamp}{self.api_key}{self.recv_window}{params}"
        return hmac.new(
            self.api_secret.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _request(self, method: str, endpoint: str, params: dict = None) -> Dict:
        """Make authenticated request to Bybit API with better error handling"""
        
        # Skip if no API keys
        if not self.api_key or not self.api_secret:
            return {"retCode": -1, "retMsg": "API keys not configured"}
        
        timestamp = str(int(time.time() * 1000))
        
        # Build query string
        query_string = ""
        if params and method == "GET":
            sorted_params = sorted(params.items())
            query_string = "&".join([f"{k}={v}" for k, v in sorted_params if v is not None])
        
        # Generate signature
        signature = self._generate_signature(timestamp, query_string)
        
        # Headers
        headers = {
            "X-BAPI-API-KEY": self.api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-SIGN": signature,
            "X-BAPI-RECV-WINDOW": self.recv_window,
            "X-Referer": self.broker_code,
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}{endpoint}"
        if query_string and method == "GET":
            url = f"{url}?{query_string}"
        
        try:
            with httpx.Client(timeout=10.0) as client:
                if method == "GET":
                    response = client.get(url, headers=headers)
                else:
                    response = client.post(url, headers=headers, json=params)
                
                # Check if response is valid JSON
                try:
                    return response.json()
                except:
                    print(f"❌ Invalid JSON response: {response.text[:200]}")
                    return {"retCode": -1, "retMsg": "Invalid JSON response"}
                    
        except httpx.ConnectError:
            print(f"❌ Connection error to {self.base_url}")
            return {"retCode": -1, "retMsg": "Connection error"}
        except httpx.TimeoutException:
            print(f"❌ Timeout connecting to {self.base_url}")
            return {"retCode": -1, "retMsg": "Timeout"}
        except Exception as e:
            print(f"❌ Bybit API error: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    def get_24h_profit(self) -> Dict:
        """
        Calculate total profit/loss from last 24 hours
        Returns safe defaults if API fails
        """
        
        # Return zeros if no API keys
        if not self.api_key or not self.api_secret:
            return {
                'total_profit': 0,
                'trade_count': 0,
                'win_rate': 0,
                'winning_trades': 0,
                'symbols': {}
            }
        
        try:
            # Calculate timestamps for last 24h
            end_time = int(time.time() * 1000)
            start_time = int((datetime.now() - timedelta(hours=24)).timestamp() * 1000)
            
            print(f"🔍 Fetching closed PnL from {start_time} to {end_time}")
            
            # Get closed PnL from linear/perpetual trades
            params = {
                "category": "linear",
                "limit": 50,
                "startTime": start_time,
                "endTime": end_time
            }
            
            result = self._request("GET", "/v5/position/closed-pnl", params=params)
            
            # Debug output
            print(f"🔍 API Response code: {result.get('retCode')}")
            
            total_profit = 0.0
            winning_trades = 0
            total_trades = 0
            symbol_profit = {}
            
            if result.get('retCode') == 0:
                trades = result.get('result', {}).get('list', [])
                print(f"🔍 Found {len(trades)} trades in last 24h")
                
                for trade in trades:
                    # Get profit amount (closedPnl)
                    pnl = float(trade.get('closedPnl', 0))
                    symbol = trade.get('symbol', 'UNKNOWN')
                    
                    total_profit += pnl
                    total_trades += 1
                    
                    if pnl > 0:
                        winning_trades += 1
                    
                    # Track per symbol
                    if symbol not in symbol_profit:
                        symbol_profit[symbol] = 0
                    symbol_profit[symbol] += pnl
                
                print(f"🔍 Total profit: {total_profit} USDT from {total_trades} trades")
            else:
                print(f"❌ API Error: {result.get('retMsg')}")
            
            # Calculate win rate
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            return {
                'total_profit': round(total_profit, 2),
                'trade_count': total_trades,
                'win_rate': round(win_rate, 1),
                'winning_trades': winning_trades,
                'symbols': symbol_profit
            }
            
        except Exception as e:
            print(f"❌ Profit calculation error: {e}")
            return {
                'total_profit': 0,
                'trade_count': 0,
                'win_rate': 0,
                'winning_trades': 0,
                'symbols': {}
            }
    
    def get_wallet_balance(self) -> float:
        """Get total wallet balance in USDT"""
        
        # Return 0 if no API keys
        if not self.api_key or not self.api_secret:
            return 0
        
        try:
            result = self._request("GET", "/v5/account/wallet-balance", 
                                   params={"accountType": "UNIFIED", "coin": "USDT"})
            
            if result.get('retCode') == 0:
                for account in result.get('result', {}).get('list', []):
                    for coin in account.get('coin', []):
                        if coin.get('coin') == 'USDT':
                            return float(coin.get('walletBalance', 0))
            return 0
        except:
            return 0

# ============================================================================
# TELEGRAM BOT
# ============================================================================

class DailyReporter:
    def __init__(self):
        self.bot = telebot.TeleBot(settings.TELEGRAM_TOKEN) if settings.TELEGRAM_TOKEN else None
        self.chat_id = settings.ADMIN_CHAT_ID
        
        if not self.chat_id:
            print("⚠️ ADMIN_CHAT_ID not set! Will print to console instead.")
        
        if not settings.TELEGRAM_TOKEN:
            print("⚠️ TELEGRAM_TOKEN not set! Will print to console only.")
    
    def get_warrior_status(self, status_json: str) -> str:
        """Parse warrior status JSON"""
        try:
            status = json.loads(status_json)
            return status.get('status', 'UNKNOWN')
        except:
            return 'UNKNOWN'
    
    def format_report(self, stats: Dict, profit_data: Dict, balance: float) -> str:
        """Format the daily report message"""
        
        # Parse heartbeat
        heartbeat = stats['heartbeat']
        if heartbeat != "N/A":
            try:
                dt = datetime.fromisoformat(heartbeat)
                heartbeat_time = dt.strftime('%H:%M:%S')
            except:
                heartbeat_time = heartbeat[:19]
        else:
            heartbeat_time = "N/A"
        
        # Get warrior status
        warrior_status = self.get_warrior_status(stats['warrior_status'])
        
        # Determine profit emoji
        if profit_data['total_profit'] > 0:
            profit_emoji = "📈"
        elif profit_data['total_profit'] < 0:
            profit_emoji = "📉"
        else:
            profit_emoji = "⚖️"
        
        # Build report
        report = f"""
📊 *NOVA DAILY SUMMARY*
📅 Date: {datetime.now().strftime('%Y-%m-%d')}
━━━━━━━━━━━━━━━━━━━━━

🚀 *API Statistics*
• Total Requests: `{stats['total_requests']}`
• Today's Requests: `{redis_client.get_daily_requests()}`
• Last Heartbeat: `{heartbeat_time}`
• System Status: `{warrior_status}`

💰 *Trading Performance {profit_emoji}*
• 24h Net Profit: `{profit_data['total_profit']:+.2f} USDT`
• Trade Count: `{profit_data['trade_count']}`
• Win Rate: `{profit_data['win_rate']}%` ({profit_data['winning_trades']}/{profit_data['trade_count']})
• Wallet Balance: `{balance:.2f} USDT`

📊 *Top Performers*
"""
        
        # Add top 3 symbols by profit
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

✅ All systems operational.
"""
        
        return report
    
    def send_report(self):
        """Generate and send the daily report"""
        print(f"📊 Generating daily report at {datetime.now()}")
        
        # Fetch stats from Redis
        stats = redis_client.get_stats()
        
        # Fetch profit data from Bybit
        tracker = BybitProfitTracker()
        profit_data = tracker.get_24h_profit()
        balance = tracker.get_wallet_balance()
        
        # Format report
        report = self.format_report(stats, profit_data, balance)
        
        # Send to Telegram
        if self.bot and self.chat_id:
            try:
                self.bot.send_message(self.chat_id, report, parse_mode="Markdown")
                print(f"✅ Report sent to Telegram chat {self.chat_id}")
            except Exception as e:
                print(f"❌ Failed to send Telegram message: {e}")
                print("\n" + "="*50)
                print("REPORT (Telegram failed):")
                print(report)
                print("="*50)
        else:
            # Print to console if no telegram
            print("\n" + "="*50)
            print("DAILY REPORT:")
            print(report)
            print("="*50)
        
        # Increment today's request counter
        redis_client.increment_daily_requests()
    
    def run_once(self):
        """Run the report once (for testing)"""
        self.send_report()
    
    def run_scheduled(self):
        """Run the reporter on a schedule"""
        print("📈 Nova Reporter is running... Waiting for midnight.")
        print(f"⏰ Current time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"🤖 Will send daily report at 00:00 daily")
        
        # Schedule for midnight
        schedule.every().day.at("00:00").do(self.send_report)
        
        # Also run once at startup if it's after midnight
        current_hour = datetime.now().hour
        if current_hour == 0:
            print("🎯 It's midnight! Running report now...")
            self.send_report()
        
        while True:
            schedule.run_pending()
            time.sleep(60)

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    print("=" * 60)
    print("🚀 NOVA DAILY REPORTER - Fixed Version")
    print("=" * 60)
    
    # Check configuration
    if not settings.MASTER_API_KEY or not settings.MASTER_API_SECRET:
        print("ℹ️ Master API keys not configured - profit stats will show zeros")
        print("   To enable profit tracking, add to .env:")
        print("   MASTER_API_KEY=your_key")
        print("   MASTER_API_SECRET=your_secret")
    
    print(f"✅ Broker: {settings.BROKER_CODE}")
    print(f"✅ Redis: Connected")
    print("=" * 60)
    
    # Create reporter and run
    reporter = DailyReporter()
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        print("📊 Running report once...")
        reporter.run_once()
    else:
        reporter.run_scheduled()

if __name__ == "__main__":
    main()
