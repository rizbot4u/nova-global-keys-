"""MT5 Engine for Nova Global Keys - Gold & Stocks Integration"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import time
import logging
from typing import Dict, List, Optional, Tuple

from mt5.config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER, TRADFI_SYMBOLS
from mt5.logger import setup_logger

logger = setup_logger("mt5_engine")

class MT5Engine:
    """Handles all MT5 operations for gold, stocks, forex"""
    
    def __init__(self):
        self.initialized = False
        self.connected = False
        self.account_info = None
        
    def initialize(self) -> bool:
        """Initialize MT5 connection"""
        try:
            # Initialize MT5 terminal
            if not mt5.initialize():
                error = mt5.last_error()
                logger.error(f"MT5 initialize failed: {error}")
                return False
            
            self.initialized = True
            logger.info("✅ MT5 initialized")
            return True
            
        except Exception as e:
            logger.error(f"MT5 init error: {e}")
            return False
    
    def login(self) -> bool:
        """Login to MT5 account"""
        if not self.initialized:
            if not self.initialize():
                return False
        
        try:
            # Login with credentials
            authorized = mt5.login(
                login=MT5_LOGIN,
                password=MT5_PASSWORD,
                server=MT5_SERVER
            )
            
            if not authorized:
                error = mt5.last_error()
                logger.error(f"MT5 login failed: {error}")
                return False
            
            self.connected = True
            self.account_info = mt5.account_info()
            
            logger.info(f"✅ MT5 logged in - Balance: ${self.account_info.balance:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"MT5 login error: {e}")
            return False
    
    def get_symbol_price(self, symbol: str) -> Optional[Dict]:
        """Get current price for a symbol (gold, stock, forex)"""
        try:
            # Check if symbol exists
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.warning(f"Symbol {symbol} not found")
                return None
            
            # Get tick (current price)
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.warning(f"No tick for {symbol}")
                return None
            
            # Get additional info
            symbol_info = mt5.symbol_info(symbol)
            
            return {
                "symbol": symbol,
                "name": TRADFI_SYMBOLS.get(symbol, symbol),
                "bid": tick.bid,
                "ask": tick.ask,
                "spread": (tick.ask - tick.bid) * (10 ** symbol_info.digits),
                "digits": symbol_info.digits,
                "time": datetime.now().isoformat(),
                "change_24h": self._get_daily_change(symbol)
            }
            
        except Exception as e:
            logger.error(f"Error getting {symbol} price: {e}")
            return None
    
    def _get_daily_change(self, symbol: str) -> float:
        """Calculate 24h change percentage"""
        try:
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 0, 2)
            if rates is not None and len(rates) >= 2:
                prev_close = rates[-2]['close']
                current = rates[-1]['close']
                change = ((current - prev_close) / prev_close) * 100
                return round(change, 2)
        except:
            pass
        return 0.0
    
    def get_all_prices(self) -> List[Dict]:
        """Get prices for all configured symbols"""
        prices = []
        for symbol in TRADFI_SYMBOLS.keys():
            price = self.get_symbol_price(symbol)
            if price:
                prices.append(price)
            time.sleep(0.1)  # Rate limiting
        return prices
    
    def place_order(self, symbol: str, order_type: str, volume: float) -> Dict:
        """Place trade order (buy/sell)"""
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return {"success": False, "error": f"Symbol {symbol} not found"}
            
            # Ensure symbol is selected
            if not symbol_info.visible:
                if not mt5.symbol_select(symbol, True):
                    return {"success": False, "error": f"Cannot select {symbol}"}
            
            # Get current price
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return {"success": False, "error": f"No price for {symbol}"}
            
            # Determine order direction
            if order_type.upper() in ["BUY", "LONG"]:
                order_type_mt5 = mt5.ORDER_TYPE_BUY
                price = tick.ask
                sl_price = price * 0.95  # 5% stop loss example
                tp_price = price * 1.05  # 5% take profit example
            else:  # SELL/SHORT
                order_type_mt5 = mt5.ORDER_TYPE_SELL
                price = tick.bid
                sl_price = price * 1.05
                tp_price = price * 0.95
            
            # Prepare request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": float(volume),
                "type": order_type_mt5,
                "price": price,
                "sl": sl_price,
                "tp": tp_price,
                "deviation": 20,
                "magic": 234000,
                "comment": "Nova Trade",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send order
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return {
                    "success": False,
                    "error": f"Order failed: {result.comment}",
                    "retcode": result.retcode
                }
            
            return {
                "success": True,
                "order_id": result.order,
                "symbol": symbol,
                "type": order_type,
                "volume": volume,
                "price": price,
                "sl": sl_price,
                "tp": tp_price,
                "time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Order error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_positions(self) -> List[Dict]:
        """Get all open positions"""
        try:
            positions = mt5.positions_get()
            if positions is None:
                return []
            
            result = []
            for pos in positions:
                result.append({
                    "ticket": pos.ticket,
                    "symbol": pos.symbol,
                    "type": "BUY" if pos.type == 0 else "SELL",
                    "volume": pos.volume,
                    "price_open": pos.price_open,
                    "price_current": pos.price_current,
                    "profit": pos.profit,
                    "swap": pos.swap,
                    "time": datetime.fromtimestamp(pos.time).isoformat()
                })
            return result
            
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def close_position(self, ticket: int) -> Dict:
        """Close a specific position"""
        try:
            position = mt5.positions_get(ticket=ticket)
            if position is None or len(position) == 0:
                return {"success": False, "error": f"Position {ticket} not found"}
            
            pos = position[0]
            
            # Determine opposite order type
            order_type = mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(pos.symbol).bid if pos.type == 0 else mt5.symbol_info_tick(pos.symbol).ask
            
            # Prepare close request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": order_type,
                "position": pos.ticket,
                "price": price,
                "deviation": 20,
                "magic": 234000,
                "comment": "Close by Nova",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return {
                    "success": False,
                    "error": f"Close failed: {result.comment}",
                    "retcode": result.retcode
                }
            
            return {
                "success": True,
                "order_id": result.order,
                "symbol": pos.symbol,
                "profit": pos.profit,
                "message": f"Position {ticket} closed"
            }
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return {"success": False, "error": str(e)}
    
    def get_account_summary(self) -> Dict:
        """Get account balance and summary"""
        if not self.connected:
            if not self.login():
                return {"success": False, "error": "Not connected"}
        
        try:
            info = mt5.account_info()
            if info is None:
                return {"success": False, "error": "Cannot get account info"}
            
            return {
                "success": True,
                "balance": info.balance,
                "equity": info.equity,
                "margin": info.margin,
                "free_margin": info.margin_free,
                "margin_level": info.margin_level,
                "leverage": info.leverage,
                "currency": info.currency,
                "server": info.server,
                "login": info.login,
                "name": info.name
            }
            
        except Exception as e:
            logger.error(f"Error getting account summary: {e}")
            return {"success": False, "error": str(e)}
    
    def shutdown(self):
        """Shutdown MT5 connection"""
        if self.initialized:
            mt5.shutdown()
            self.initialized = False
            self.connected = False
            logger.info("MT5 shutdown complete")
