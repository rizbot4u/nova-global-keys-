from fastapi import FastAPI
from mt5linux import MetaTrader5
import uvicorn
import os
import time

app = FastAPI(title="Nova MT5 Bridge")

mt5_host = os.getenv('MT5_HOST', 'mt5-terminal')
mt5_port = int(os.getenv('MT5_PORT', 8001))

@app.get("/api/v1/price/{symbol}")
async def get_price(symbol: str):
    try:
        mt5 = MetaTrader5(host=mt5_host, port=mt5_port)
        tick = mt5.symbol_info_tick(symbol.upper())
        return {
            "success": True,
            "symbol": symbol.upper(),
            "bid": tick.bid,
            "ask": tick.ask,
            "time": tick.time
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "service": "mt5-bridge"}

if __name__ == "__main__":
    # Wait for MT5 terminal to be ready
    time.sleep(10)
    uvicorn.run(app, host="0.0.0.0", port=8002)
