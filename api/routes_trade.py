"""
Nova Global Keys - Trading Routes
Uses NovaBrokerEngine for all operations
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from core.broker_engine import NovaBrokerEngine
from core.redis_client import redis_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Trading"])

# Global engine instance
engine = NovaBrokerEngine()

class OrderRequest(BaseModel):
    uid: str
    symbol: str
    side: str
    qty: float
    order_type: str = "Market"

@router.get("/price/{symbol}")
async def get_price(symbol: str):
    """Get current price using broker credentials"""
    try:
        from core.broker_engine import NovaBrokerEngine
        engine = NovaBrokerEngine()
        
        # Use pybit SDK through engine
        result = await engine.get_ticker_pybit(symbol)
        
        if result.get('retCode') == 0:
            ticker = result['result']['list'][0]
            return {
                "success": True,
                "symbol": symbol,
                "price": float(ticker['lastPrice']),
                "change_24h": float(ticker.get('price24hPcnt', 0)) * 100
            }
        else:
            logger.error(f"Bybit error: {result.get('retMsg')}")
            raise HTTPException(status_code=500, detail="Failed to fetch price")
            
    except Exception as e:
        logger.exception(f"Price error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch price")
@router.get("/balance/{uid}")
async def get_balance(uid: str):
    """Get user's balance - uses user's API keys"""
    try:
        keys = redis_client.get_user_keys(uid)
        if not keys:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "User not connected"}
            )
        
        result = await engine.user_get_balance(
            keys['api_key'], 
            keys['api_secret']
        )
        
        if result.get('retCode') == 0:
            formatted = engine.format_balance(result)
            return JSONResponse(content=formatted)
        else:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": result.get('retMsg', 'Unknown error')}
            )
    except Exception as e:
        logger.error(f"Balance error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@router.post("/order")
async def place_order(order: OrderRequest):
    """Place order for user"""
    try:
        keys = redis_client.get_user_keys(order.uid)
        if not keys:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "User not connected"}
            )
        
        # Get current price for amount calculation
        ticker = await engine.get_ticker(order.symbol)
        price_data = engine.format_price(ticker)
        
        if not price_data.get('success'):
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Could not fetch price"}
            )
        
        current_price = price_data['price']
        qty = str(round(order.qty / current_price, 4))
        
        result = await engine.user_place_order(
            keys['api_key'],
            keys['api_secret'],
            order.symbol,
            order.side,
            qty,
            order.order_type
        )
        
        if result.get('retCode') == 0:
            order_id = result.get('result', {}).get('orderId')
            return JSONResponse(content={
                "success": True,
                "order_id": order_id,
                "symbol": order.symbol,
                "side": order.side,
                "amount_usd": order.qty,
                "quantity": float(qty),
                "price": current_price
            })
        else:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": result.get('retMsg', 'Order failed')}
            )
    except Exception as e:
        logger.error(f"Order error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
