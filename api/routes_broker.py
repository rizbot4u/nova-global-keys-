"""
Nova Global Keys - Broker-Level Routes
Uses Broker credentials for all endpoints
"""

import time
import logging
import traceback
import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/broker", tags=["Broker"])

# Broker credentials
CLIENT_ID = settings.CLIENT_ID
CLIENT_SECRET = settings.CLIENT_SECRET
BROKER_CODE = settings.BROKER_CODE

@router.get("/price/{symbol}")
async def broker_price(symbol: str):
    """Get price using broker credentials"""
    try:
        logger.info(f"Fetching price for {symbol}")
        
        from core.broker_engine import NovaBrokerEngine
        engine = NovaBrokerEngine()
        
        # Use the correct method name - check what's available
        # Try both possibilities
        if hasattr(engine, 'get_ticker_pybit'):
            result = await engine.get_ticker_pybit(symbol)
        elif hasattr(engine, 'get_ticker'):
            result = await engine.get_ticker(symbol)
        else:
            # Fallback to direct method
            result = await engine._broker_request(
                "GET",
                "/v5/market/tickers",
                params={"category": "spot", "symbol": symbol}
            )
        
        logger.info(f"Bybit response: {result}")
        
        if result.get('retCode') == 0:
            ticker = result['result']['list'][0]
            return {
                "success": True,
                "symbol": symbol,
                "price": float(ticker.get('lastPrice', 0)),
                "change": float(ticker.get('price24hPcnt', 0)) * 100,
                "high": float(ticker.get('highPrice24h', 0)),
                "low": float(ticker.get('lowPrice24h', 0)),
                "volume": float(ticker.get('volume24h', 0))
            }
        else:
            error_msg = result.get('retMsg', 'Unknown error')
            logger.error(f"Bybit error: {error_msg} (code: {result.get('retCode')})")
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": error_msg, "code": result.get('retCode')}
            )
            
    except Exception as e:
        logger.error(f"Broker price error: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
@router.get("/balance")
async def broker_balance():
    """Get broker account balance"""
    try:
        logger.info("Fetching broker balance")
        
        from core.broker_engine import NovaBrokerEngine
        engine = NovaBrokerEngine()
        
        # Try using pybit
        result = await engine.get_wallet_balance_pybit()
        logger.info(f"Balance response: {result}")
        
        if result.get('retCode') == 0:
            return JSONResponse(content=result)
        else:
            logger.error(f"Balance error: {result.get('retMsg')}")
            return JSONResponse(
                status_code=400,
                content=result
            )
            
    except Exception as e:
        logger.error(f"Broker balance error: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
