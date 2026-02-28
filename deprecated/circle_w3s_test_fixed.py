#!/usr/bin/env python3
"""
Circle W3S API Test - With proper .env loading
"""

import os
import json
import httpx
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

CIRCLE_API_KEY = os.getenv('CIRCLE_API_KEY')
CIRCLE_CLIENT_KEY = os.getenv('CIRCLE_CLIENT_KEY')
ENTITY_SECRET = os.getenv('ENTITY_SECRET')

BASE_URL = "https://api-sandbox.circle.com/v1/w3s"

print("=" * 60)
print("🚀 CIRCLE W3S API TEST")
print("=" * 60)
print(f"API Key present: {'✅' if CIRCLE_API_KEY else '❌'}")
print(f"Client Key present: {'✅' if CIRCLE_CLIENT_KEY else '❌'}")
print(f"Entity Secret present: {'✅' if ENTITY_SECRET else '❌'}")
print("=" * 60)

async def test_w3s_connection():
    async with httpx.AsyncClient() as client:
        print("\n📡 Testing W3S API connection...")
        
        headers = {
            "Authorization": f"Bearer {CIRCLE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = await client.get(
            f"{BASE_URL}/developer/walletSets",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

async def main():
    await test_w3s_connection()

if __name__ == "__main__":
    asyncio.run(main())
