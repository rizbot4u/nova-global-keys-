"""
Nova Global Keys - Configuration Module
Loads and validates all environment variables
Author: Nova Global Keys | Broker: Kr000820
Version: 3.0.0
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class Settings:
    """Complete application settings for Nova Global Keys"""
    
    # ===== BROKER CONFIGURATION (CRITICAL FOR REBATES) =====
    BROKER_UID: str = os.getenv('BROKER_UID', '128827007')        # Your Bybit account ID
    BROKER_CODE: str = os.getenv('BROKER_CODE', 'Kr000820')       # Your rebate code - use in Referer header
    AFFILIATE_ID: str = os.getenv('AFFILIATE_ID', '127146')       # Your affiliate ID
    CLIENT_ID: str = os.getenv('CLIENT_ID', 'x9dmxAGkDDoa')       # OAuth client ID
    CLIENT_SECRET: str = os.getenv('CLIENT_SECRET', '')           # OAuth client secret
    
    # ===== BYBIT API ENDPOINTS =====
    BYBIT_V5: str = os.getenv('BYBIT_V5', 'https://api.bybit.id/v5')           # Indonesia endpoint
    BYBIT_OAUTH: str = os.getenv('BYBIT_OAUTH', 'https://api2.bybit.com')      # OAuth endpoint
    BYBIT_TESTNET: str = os.getenv('BYBIT_TESTNET', 'https://api-testnet.bybit.com/v5')
    
    # ===== P2P MERCHANT CONFIGURATION =====
    P2P_API_KEY: str = os.getenv('P2P_API_KEY', '')               # Your P2P API key
    P2P_API_SECRET: str = os.getenv('P2P_API_SECRET', '')         # Your P2P API secret
    P2P_MERCHANT_ID: str = os.getenv('P2P_MERCHANT_ID', 'Kr000820')  # Your P2P merchant ID
    
    # P2P Trading Defaults
    P2P_DEFAULT_FIAT: str = os.getenv('P2P_DEFAULT_FIAT', 'USD')
    P2P_DEFAULT_TOKEN: str = os.getenv('P2P_DEFAULT_TOKEN', 'USDT')
    P2P_MIN_TRADE: float = float(os.getenv('P2P_MIN_TRADE', '10'))
    P2P_MAX_TRADE: float = float(os.getenv('P2P_MAX_TRADE', '10000'))
    
    # P2P Fee Structure (percentage)
    P2P_TRADE_FEE: float = float(os.getenv('P2P_TRADE_FEE', '0.5'))        # 0.5% fee per trade
    P2P_MERCHANT_FEE: float = float(os.getenv('P2P_MERCHANT_FEE', '20'))   # 20% from sub-merchants
    P2P_PREMIUM_FEE: float = float(os.getenv('P2P_PREMIUM_FEE', '0.25'))   # 0.25% for premium users
    
    # ===== GOOGLE OAUTH CONFIGURATION =====
    GOOGLE_CLIENT_ID: str = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET: str = os.getenv('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_REDIRECT_URI: str = os.getenv('GOOGLE_REDIRECT_URI', '')
    GOOGLE_PROJECT_ID: str = os.getenv('GOOGLE_PROJECT_ID', '')
    GOOGLE_AUTH_URI: str = os.getenv('GOOGLE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth')
    GOOGLE_TOKEN_URI: str = os.getenv('GOOGLE_TOKEN_URI', 'https://oauth2.googleapis.com/token')
    GOOGLE_CERT_URL: str = os.getenv('GOOGLE_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs')
    GOOGLE_JS_ORIGIN: str = os.getenv('GOOGLE_JS_ORIGIN', '')
    
    # ===== URL CONFIGURATION =====
    REDIRECT_URI: str = os.getenv('REDIRECT_URI', 'https://novatradingkeys.com/api/auth/callback/bybit')
    FRONTEND_URL: str = os.getenv('FRONTEND_URL', 'https://www.novatradingkeys.com')
    
    # ===== TELEGRAM BOT =====
    TELEGRAM_TOKEN: str = os.getenv('TELEGRAM_TOKEN', '')
    
    # ===== REDIS DATABASE =====
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # ===== MASTER API KEYS (For broker-level operations) =====
    MASTER_API_KEY: str = os.getenv('MASTER_API_KEY', '')
    MASTER_API_SECRET: str = os.getenv('MASTER_API_SECRET', '')
    
    # ===== SERVER CONFIGURATION =====
    PORT: int = int(os.getenv('PORT', '8080'))
    HOST: str = os.getenv('HOST', '0.0.0.0')
    
    # ===== LOGGING =====
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', '/srv/nova-global-keys/logs/app.log')
    
    # ===== FEATURE FLAGS =====
    USE_TESTNET: bool = os.getenv('USE_TESTNET', 'false').lower() == 'true'
    MOCK_TRADING: bool = os.getenv('MOCK_TRADING', 'false').lower() == 'true'
    
    def validate(self) -> bool:
        """Validate required settings"""
        required = [
            'CLIENT_SECRET',
            'REDIRECT_URI',
            'TELEGRAM_TOKEN'
        ]
        
        # Check if any P2P keys are partially set
        if self.P2P_API_KEY and not self.P2P_API_SECRET:
            raise ValueError("P2P_API_KEY set but P2P_API_SECRET missing")
        if self.P2P_API_SECRET and not self.P2P_API_KEY:
            raise ValueError("P2P_API_SECRET set but P2P_API_KEY missing")
        
        # Validate numeric ranges
        if self.P2P_MIN_TRADE < 1:
            raise ValueError("P2P_MIN_TRADE must be at least 1")
        if self.P2P_MAX_TRADE < self.P2P_MIN_TRADE:
            raise ValueError("P2P_MAX_TRADE must be >= P2P_MIN_TRADE")
        
        missing = [req for req in required if not getattr(self, req)]
        if missing:
            raise ValueError(f"Missing required settings: {missing}")
        
        return True
    
    def get_broker_headers(self) -> dict:
        """Get headers with broker code for API requests"""
        return {
            "X-BAPI-PARTNER-ID": self.BROKER_CODE,
            "Referer": self.BROKER_CODE
        }
    
    def get_p2p_headers(self) -> dict:
        """Get headers with P2P merchant ID for P2P requests"""
        return {
            "X-BAPI-MERCHANT-ID": self.P2P_MERCHANT_ID,
            "X-BAPI-PARTNER-ID": self.BROKER_CODE
        }

# Global settings instance
settings = Settings()
settings.validate()

# Export for easy import
__all__ = ['settings']
