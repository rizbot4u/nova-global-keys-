#!/usr/bin/env python3
"""
NOVA SIGNAL BOT - Real Trading Signals with Telegram Integration
Author: Rizwan Ali | Nova Global Keys
"""

import os
import sys
import time
import json
import asyncio
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

# Add parent directory to path for imports
sys.path.append('/srv/nova-global-keys')
from thor_engine import ThorEngine, settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/srv/nova-global-keys/logs/signal_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('signal-bot')

class SignalBot:
    """Trading Signal Generator with Telegram Integration"""
    
    def __init__(self):
        self.engine = ThorEngine()
        self.pairs = [
            "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
            "ADAUSDT", "DOGEUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT"
        ]
        self.timeframes = {
            '1h': 60,
            '4h': 240,
            '1d': 1440
        }
        self.telegram_token = settings.TELEGRAM_TOKEN
        self.telegram_channel = "@Novaglobalsignals"  # Create this channel
        self.scan_interval = 60  # seconds
        self.last_signals = {}  # Cache to avoid duplicates
        
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI (Relative Strength Index)"""
        if len(prices) < period + 1:
            return 50
        
        deltas = np.diff(prices)
        gain = np.where(deltas > 0, deltas, 0)
        loss = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gain[-period:])
        avg_loss = np.mean(loss[-period:])
        
        if avg_loss == 0:
            return 100
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: List[float]) -> Dict:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(prices) < 26:
            return {'macd': 0, 'signal': 0, 'histogram': 0}
        
        exp12 = pd.Series(prices).ewm(span=12, adjust=False).mean()
        exp26 = pd.Series(prices).ewm(span=26, adjust=False).mean()
        macd = exp12 - exp26
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        
        return {
            'macd': macd.iloc[-1],
            'signal': signal.iloc[-1],
            'histogram': histogram.iloc[-1]
        }
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20) -> Dict:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return {'upper': prices[-1], 'middle': prices[-1], 'lower': prices[-1]}
        
        sma = pd.Series(prices).rolling(window=period).mean().iloc[-1]
        std = pd.Series(prices).rolling(window=period).std().iloc[-1]
        
        return {
            'upper': sma + (std * 2),
            'middle': sma,
            'lower': sma - (std * 2)
        }
    
    async def fetch_historical_prices(self, pair: str, limit: int = 100) -> List[float]:
        """Fetch historical prices for indicator calculation"""
        try:
            result = await self.engine.get_kline(
                category="spot",
                symbol=pair,
                interval="1h",
                limit=limit
            )
            
            if result.get('retCode') == 0:
                prices = []
                for candle in result['result']['list']:
                    prices.append(float(candle[4]))  # Close price
                return prices
            return []
        except Exception as e:
            logger.error(f"Error fetching prices for {pair}: {e}")
            return []
    
    async def scan_pair(self, pair: str) -> Optional[Dict]:
        """Scan a single pair for trading signals"""
        try:
            # Get current price
            ticker = await self.engine.get_tickers(symbol=pair)
            if ticker.get('retCode') != 0:
                return None
            
            current_price = float(ticker['result']['list'][0]['lastPrice'])
            
            # Get historical prices for indicators
            prices = await self.fetch_historical_prices(pair)
            if not prices:
                return None
            
            # Calculate indicators
            rsi = self.calculate_rsi(prices)
            macd = self.calculate_macd(prices)
            bb = self.calculate_bollinger_bands(prices)
            
            # Signal logic
            signals = []
            signal_strength = 0
            
            # RSI signals
            if rsi < 30:
                signals.append("RSI OVERSOLD")
                signal_strength += 2
            elif rsi > 70:
                signals.append("RSI OVERBOUGHT")
                signal_strength -= 2
            
            # MACD signals
            if macd['histogram'] > 0 and macd['histogram'] > macd.get('prev_histogram', 0):
                signals.append("MACD BULLISH")
                signal_strength += 1
            elif macd['histogram'] < 0 and macd['histogram'] < macd.get('prev_histogram', 0):
                signals.append("MACD BEARISH")
                signal_strength -= 1
            
            # Bollinger Bands signals
            if current_price < bb['lower']:
                signals.append("BB OVERSOLD")
                signal_strength += 1
            elif current_price > bb['upper']:
                signals.append("BB OVERBOUGHT")
                signal_strength -= 1
            
            # Generate signal if strong enough
            if abs(signal_strength) >= 2:
                signal_type = "BUY" if signal_strength > 0 else "SELL"
                
                return {
                    'pair': pair,
                    'price': current_price,
                    'signal': signal_type,
                    'strength': abs(signal_strength),
                    'indicators': {
                        'rsi': round(rsi, 2),
                        'macd': round(macd['histogram'], 2),
                        'bb_lower': round(bb['lower'], 2),
                        'bb_upper': round(bb['upper'], 2)
                    },
                    'signals': signals,
                    'timestamp': datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error scanning {pair}: {e}")
            return None
    
    def send_telegram_signal(self, signal: Dict):
        """Send signal to Telegram channel"""
        try:
            # Format message
            message = f"""
🔔 *NOVA TRADING SIGNAL* 🔔

💎 *{signal['pair']}*
💰 *Price:* ${signal['price']:,.2f}
📊 *Signal:* {'🟢 BUY' if signal['signal'] == 'BUY' else '🔴 SELL'}
⚡ *Strength:* {'🔥' * signal['strength']}

📈 *Indicators:*
• RSI: {signal['indicators']['rsi']}
• MACD: {signal['indicators']['macd']}
• BB Lower: ${signal['indicators']['bb_lower']:,.2f}
• BB Upper: ${signal['indicators']['bb_upper']:,.2f}

🎯 *Signals:* {', '.join(signal['signals'])}

⏰ {signal['timestamp']}

🤖 *Powered by Nova Global Keys*
Broker: `Kr000820`
            """
            
            # Send to Telegram
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                "chat_id": self.telegram_channel,
                "text": message,
                "parse_mode": "Markdown"
            }
            requests.post(url, json=data)
            
            logger.info(f"Signal sent: {signal['pair']} {signal['signal']}")
            
        except Exception as e:
            logger.error(f"Error sending Telegram: {e}")
    
    async def scan_market(self):
        """Main scanning loop"""
        logger.info(f"🚀 Signal Bot started - Scanning {len(self.pairs)} pairs")
        
        while True:
            try:
                for pair in self.pairs:
                    signal = await self.scan_pair(pair)
                    
                    if signal:
                        # Check if this is a new signal (avoid duplicates)
                        signal_key = f"{pair}_{signal['signal']}"
                        last_time = self.last_signals.get(signal_key)
                        
                        if not last_time or (datetime.now() - last_time).seconds > 3600:
                            self.send_telegram_signal(signal)
                            self.last_signals[signal_key] = datetime.now()
                    
                    # Small delay between pairs
                    await asyncio.sleep(1)
                
                logger.info(f"Scan cycle complete. Next scan in {self.scan_interval}s")
                await asyncio.sleep(self.scan_interval)
                
            except Exception as e:
                logger.error(f"Scan error: {e}")
                await asyncio.sleep(10)
    
    async def run(self):
        """Run the signal bot"""
        try:
            await self.scan_market()
        except KeyboardInterrupt:
            logger.info("Signal bot stopped by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}")

async def main():
    bot = SignalBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())

