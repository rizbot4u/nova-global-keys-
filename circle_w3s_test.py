#!/usr/bin/env python3
"""
Circle W3S (Web3 Services) API Test
Using correct endpoints for Developer-Controlled Wallets
"""

import os
import json
import httpx
import asyncio
import uuid
from datetime import datetime

# Load from environment (your .env file is perfect!)
CIRCLE_API_KEY = os.getenv('CIRCLE_API_KEY')
CIRCLE_CLIENT_KEY = os.getenv('CIRCLE_CLINT_KEY')  # Note: typo in your env
ENTITY_SECRET = os.getenv('ENTITY_SECRET')

# Correct base URL for W3S API
BASE_URL = "https://api-sandbox.circle.com/v1/w3s"

print("=" * 60)
print("🚀 CIRCLE W3S API TEST")
print("=" * 60)
print(f"API Key present: {'✅' if CIRCLE_API_KEY else '❌'}")
print(f"Client Key present: {'✅' if CIRCLE_CLIENT_KEY else '❌'}")
print(f"Entity Secret present: {'✅' if ENTITY_SECRET else '❌'}")
print("=" * 60)

async def test_w3s_connection():
    """Test connection to W3S API"""
    async with httpx.AsyncClient() as client:
        # First, try to get user wallets (requires no special setup)
        print("\n📡 Testing W3S API connection...")
        
        headers = {
            "Authorization": f"Bearer {CIRCLE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Try to list wallet sets (this is a valid W3S endpoint)
        response = await client.get(
            f"{BASE_URL}/developer/walletSets",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Successfully connected to W3S API!")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.text}")
            
            # If 401, the key might not have permissions
            if response.status_code == 401:
                print("\n🔑 Your API key might need these permissions in Circle Console:")
                print("   - Wallets: Read")
                print("   - Wallets: Write")
                print("   - Developer: Read")

async def check_key_permissions():
    """Check what permissions your API key has"""
    async with httpx.AsyncClient() as client:
        print("\n🔍 Checking key permissions...")
        
        # This endpoint returns key info (if available)
        response = await client.get(
            f"https://api-sandbox.circle.com/v1/apiKeys",
            headers={"Authorization": f"Bearer {CIRCLE_API_KEY}"}
        )
        
        if response.status_code == 200:
            print("✅ Key info retrieved:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Could not get key info: {response.status_code}")

async def create_wallet_set_direct():
    """
    Create a wallet set using direct API calls
    Note: This requires entity secret encryption which is complex
    """
    print("\n📦 Creating wallet set (requires entity secret encryption)...")
    print("   For production, use Circle's official SDK which handles encryption")
    print("   Install: pip install circle-developer-controlled-wallets")

async def main():
    # Test basic connection first
    await test_w3s_connection()
    
    # Check key permissions
    await check_key_permissions()
    
    # Info about next steps
    print("\n" + "=" * 60)
    print("📋 NEXT STEPS")
    print("=" * 60)
    print("1️⃣ Install official SDK:")
    print("   pip install circle-developer-controlled-wallets")
    print("\n2️⃣ Use SDK to create wallet sets (handles encryption):")
    print("""
    from circle_developer_sdk import CircleDeveloperClient
    
    client = CircleDeveloperClient(
        api_key=CIRCLE_API_KEY,
        entity_secret=ENTITY_SECRET
    )
    
    # Create wallet set
    wallet_set = await client.create_wallet_set(name="NOVA Wallets")
    """)
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
