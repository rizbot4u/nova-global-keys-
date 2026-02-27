#!/usr/bin/env python3
"""NOVA Remittance API Server"""
import os
import sys
sys.path.append('/srv/nova-global-keys')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from remittance.api.routes import router as remit_router
from remittance.webhooks.circle import router as webhook_router

app = FastAPI(title="NOVA Remittance API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(remit_router)
app.include_router(webhook_router)

@app.get("/")
async def root():
    return {
        "name": "NOVA Remittance",
        "version": "1.0.0",
        "broker": "Kr000820",
        "status": "operational"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "remittance"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8082))
    uvicorn.run(app, host="0.0.0.0", port=port)
