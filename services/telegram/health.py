#!/usr/bin/env python3
"""
Simple health check server for telegram bot
"""
from fastapi import FastAPI
import uvicorn
import threading
import os

app = FastAPI(title="Telegram Health")

@app.get("/health")
async def health():
    return {
        "service": "telegram",
        "status": "running",
        "bot": "active"
    }

def run_health():
    uvicorn.run(app, host="127.0.0.1", port=8007)

# Start health server in background
thread = threading.Thread(target=run_health, daemon=True)
thread.start()
