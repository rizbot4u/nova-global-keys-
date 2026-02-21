"""
Nova Global Keys - Health Routes
System health and status endpoints
"""

import logging
from datetime import datetime
from fastapi import APIRouter
from config.settings import settings
from core.redis_client import redis_client

logger = logging.getLogger(__name__)
router = APIRouter(tags=["System"])

@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Nova Global Keys",
        "version": "1.0.0",
        "broker": settings.BROKER_CODE,
        "status": "operational"
    }

@router.get("/api/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "broker": settings.BROKER_CODE,
        "redis": "connected" if redis_client.ping() else "disconnected",
        "timestamp": datetime.now().isoformat()
    }
