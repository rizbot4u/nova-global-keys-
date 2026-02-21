"""
Nova Global Keys - FastAPI Server
Main server setup and route registration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from api import routes_auth, routes_trade, routes_health

# Try to import broker routes if they exist
try:
    from api import routes_broker
    HAS_BROKER = True
except ImportError:
    HAS_BROKER = False
    print("⚠️ Broker routes not found - skipping")

def create_app() -> FastAPI:
    """Create and configure FastAPI app"""
    
    app = FastAPI(
        title="Nova Global Keys API",
        description="Complete Trading Platform",
        version="1.0.0"
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routers
    app.include_router(routes_auth.router)
    app.include_router(routes_trade.router)
    app.include_router(routes_health.router)
    
    # Register broker routes if available
    if HAS_BROKER:
        app.include_router(routes_broker.router)
        print("✅ Broker routes registered")
    
    return app
