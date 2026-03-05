#!/usr/bin/env python3
"""
NOVA GLOBAL KEYS - API Gateway
Single entry point for all frontend and Telegram traffic
Routes requests to appropriate microservices
"""

import os
import sys
import logging
import asyncio
import json
from datetime import datetime
from typing import Optional

import uvicorn
import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.background import BackgroundTask
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add shared modules to path
sys.path.append("/root/nova-global-keys-/services")
from shared.redis.client import redis_client

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway")

# FastAPI app
app = FastAPI(title="Nova API Gateway", version="1.0.0")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.novatradingkeys.com",
        "https://novatradingkeys.com",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Service registry
SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:8001"),
    "user": os.getenv("USER_SERVICE_URL", "http://127.0.0.1:8002"),
    "market": os.getenv("MARKET_SERVICE_URL", "http://127.0.0.1:8003"),
    "trade": os.getenv("TRADE_SERVICE_URL", "http://127.0.0.1:8004"),
    "p2p": os.getenv("P2P_SERVICE_URL", "http://127.0.0.1:8005"),
    "broker": os.getenv("BROKER_SERVICE_URL", "http://127.0.0.1:8006"),
}

# HTTP client with connection pooling
client = httpx.AsyncClient(
    timeout=30.0,
    limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
)

# ============================================================================
# ROUTING FUNCTIONS
# ============================================================================

async def proxy_request(request: Request, service_name: str, path: str):
    """Proxy request to appropriate service"""
    service_url = SERVICES.get(service_name)
    if not service_url:
        raise HTTPException(status_code=503, detail=f"Service {service_name} unavailable")
    
    # Construct target URL
    target_url = f"{service_url}{path}"
    
    # Get request body
    body = await request.body()
    
    # Forward headers (remove host)
    headers = dict(request.headers)
    headers.pop("host", None)
    
    try:
        # Make request to service
        resp = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
            params=request.query_params
        )
        
        # Return response
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=dict(resp.headers)
        )
    except httpx.ConnectError:
        logger.error(f"Connection error to {service_name} service")
        raise HTTPException(status_code=503, detail=f"Service {service_name} unavailable")
    except Exception as e:
        logger.error(f"Proxy error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal gateway error")

# ============================================================================
# HEALTH & METRICS
# ============================================================================

@app.get("/health")
async def health():
    """Gateway health check"""
    # Check all services
    service_status = {}
    
    for name, url in SERVICES.items():
        try:
            resp = await client.get(f"{url}/health", timeout=2.0)
            service_status[name] = resp.status_code == 200
        except:
            service_status[name] = False
    
    return {
        "gateway": "healthy",
        "services": service_status,
        "redis": redis_client.ping(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # Basic metrics
    metrics_text = f"""# HELP nova_gateway_requests_total Total requests
# TYPE nova_gateway_requests_total counter
nova_gateway_requests_total {redis_client.client.get("gateway:requests") or 0}

# HELP nova_gateway_services_up Services up
# TYPE nova_gateway_services_up gauge
"""
    for name in SERVICES.keys():
        status = 1 if redis_client.client.get(f"service:heartbeat:{name}") else 0
        metrics_text += f'nova_gateway_services_up{{service="{name}"}} {status}\n'
    
    return Response(content=metrics_text, media_type="text/plain")

# ============================================================================
# AUTH ROUTES
# ============================================================================

@app.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_proxy(request: Request, path: str):
    """Proxy to auth service"""
    redis_client.client.incr("gateway:requests")
    return await proxy_request(request, "auth", f"/{path}")

# ============================================================================
# USER ROUTES
# ============================================================================

@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def user_proxy(request: Request, path: str):
    """Proxy to user service"""
    redis_client.client.incr("gateway:requests")
    return await proxy_request(request, "user", f"/{path}")

@app.api_route("/api/keys/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def keys_proxy(request: Request, path: str):
    """Proxy to user service (keys endpoints)"""
    redis_client.client.incr("gateway:requests")
    return await proxy_request(request, "user", f"/{path}")

@app.api_route("/api/bots/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def bots_proxy(request: Request, path: str):
    """Proxy to user service (bots endpoints)"""
    redis_client.client.incr("gateway:requests")
    return await proxy_request(request, "user", f"/{path}")

# ============================================================================
# MARKET ROUTES
# ============================================================================

@app.api_route("/api/market/{path:path}", methods=["GET"])
async def market_proxy(request: Request, path: str):
    """Proxy to market service"""
    redis_client.client.incr("gateway:requests")
    return await proxy_request(request, "market", f"/{path}")

@app.api_route("/api/v1/price/{path:path}", methods=["GET"])
async def price_proxy(request: Request, path: str):
    """Proxy to market service (price endpoints)"""
    redis_client.client.incr("gateway:requests")
    return await proxy_request(request, "market", f"/tickers/{path}")

# ============================================================================
# TRADE ROUTES
# ============================================================================

@app.api_route("/api/trade/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def trade_proxy(request: Request, path: str):
    """Proxy to trade service"""
    redis_client.client.incr("gateway:requests")
    return await proxy_request(request, "trade", f"/{path}")

@app.api_route("/api/exchange/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def exchange_proxy(request: Request, path: str):
    """Proxy to trade service (exchange endpoints)"""
    redis_client.client.incr("gateway:requests")
    return await proxy_request(request, "trade", f"/{path}")

# ============================================================================
# P2P ROUTES
# ============================================================================

@app.api_route("/api/p2p/{path:path}", methods=["GET", "POST"])
async def p2p_proxy(request: Request, path: str):
    """Proxy to p2p service"""
    redis_client.client.incr("gateway:requests")
    return await proxy_request(request, "p2p", f"/{path}")

# ============================================================================
# BROKER ROUTES (ADMIN ONLY)
# ============================================================================

@app.api_route("/api/broker/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def broker_proxy(request: Request, path: str):
    """Proxy to broker service"""
    redis_client.client.incr("gateway:requests")
    return await proxy_request(request, "broker", f"/{path}")

# ============================================================================
# LEGACY ROUTES (for backward compatibility)
# ============================================================================

@app.get("/api/health")
async def legacy_health():
    """Legacy health endpoint"""
    return await health()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Nova Global Keys",
        "version": "6.0.0-microservices",
        "broker": os.getenv("BROKER_CODE", "Kr000820"),
        "status": "operational",
        "services": list(SERVICES.keys())
    }

# ============================================================================
# SHUTDOWN
# ============================================================================

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    await client.aclose()

if __name__ == "__main__":
    port = int(os.getenv("GATEWAY_PORT", 8081))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)

# ============================================================================
# MULTI-EXCHANGE ROUTES
# ============================================================================

@app.api_route("/api/bybit/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def bybit_proxy(request: Request, path: str):
    """Proxy to trade service with bybit exchange"""
    redis_client.client.incr("gateway:requests")
    
    query_params = dict(request.query_params)
    query_params['exchange'] = 'bybit'
    
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
