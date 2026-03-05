# Add these to gateway/main.py

# Multi-exchange routes
@app.api_route("/api/bybit/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def bybit_proxy(request: Request, path: str):
    """Proxy to trade service with bybit exchange"""
    redis_client.client.incr("gateway:requests")
    
    # Add exchange parameter to query
    query_params = dict(request.query_params)
    query_params['exchange'] = 'bybit'
    
    # Rebuild URL with new params
    url = f"/{path}"
    if query_params:
        url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
    
    return await proxy_request(request, "trade", url)

@app.api_route("/api/binance/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def binance_proxy(request: Request, path: str):
    """Proxy to trade service with binance exchange"""
    redis_client.client.incr("gateway:requests")
    
    query_params = dict(request.query_params)
    query_params['exchange'] = 'binance'
    
    url = f"/{path}"
    if query_params:
        url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
    
    return await proxy_request(request, "trade", url)

@app.api_route("/api/kucoin/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def kucoin_proxy(request: Request, path: str):
    """Proxy to trade service with kucoin exchange"""
    redis_client.client.incr("gateway:requests")
    
    query_params = dict(request.query_params)
    query_params['exchange'] = 'kucoin'
    
    url = f"/{path}"
    if query_params:
        url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
    
    return await proxy_request(request, "trade", url)

@app.api_route("/api/okx/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def okx_proxy(request: Request, path: str):
    """Proxy to trade service with okx exchange"""
    redis_client.client.incr("gateway:requests")
    
    query_params = dict(request.query_params)
    query_params['exchange'] = 'okx'
    
    url = f"/{path}"
    if query_params:
        url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
    
    return await proxy_request(request, "trade", url)

# Also update the health endpoint to show supported exchanges
# Add this to the health endpoint in gateway/main.py
"""
# In the health endpoint, add:
"supported_exchanges": ["bybit", "binance", "kucoin", "okx"]
"""
