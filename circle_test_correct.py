#!/usr/bin/env python3
"""
Circle API Test - Using correct endpoint from docs
"""

import os
import httpx
import asyncio

# Load from environment
CIRCLE_API_KEY = os.getenv('CIRCLE_API_KEY')

# CORRECT endpoint from Circle docs
BASE_URL = "https://api.circle.com/v1/w3s"

async def test_circle():
    print("=" * 60)
    print("🚀 CIRCLE API TEST (Correct Endpoint)")
    print("=" * 60)
    print(f"API Key: {CIRCLE_API_KEY[:30]}...")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test wallets endpoint (from docs)
        print("\n📡 Testing /w3s/wallets...")
        response = await client.get(
            f"{BASE_URL}/wallets",
            headers={"Authorization": f"Bearer {CIRCLE_API_KEY}"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # If successful, a 200 with empty wallets is GOOD!
        # {"data":{"wallets":[]}} means you're authenticated!

asyncio.run(test_circle())
