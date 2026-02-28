#!/usr/bin/env python3
import os
import httpx
import asyncio
import uuid

async def test_circle():
    api_key = os.getenv('CIRCLE_API_KEY', 'TEST_API_KEY:098dcc861cbd439aebd564a161db04e2:40e097c60563e1f3be8c7a96524d738c')
    
    async with httpx.AsyncClient() as client:
        # Test 1: List wallets (should work with correct endpoint)
        print("📋 Listing wallets...")
        resp = await client.get(
            'https://api-sandbox.circle.com/v1/w3s/user/wallets',
            headers={'Authorization': f'Bearer {api_key}'}
        )
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"✅ Success! Response: {resp.text}")
        else:
            print(f"❌ Error: {resp.text}")
        
        # Test 2: Create a wallet
        print("\n🆕 Creating test wallet...")
        idempotency_key = str(uuid.uuid4())
        resp = await client.post(
            'https://api-sandbox.circle.com/v1/w3s/user/wallets',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                "idempotencyKey": idempotency_key,
                "blockchains": ["ETH-SEPOLIA"],
                "metadata": [{"name": "NOVA Test Wallet"}]
            }
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")

asyncio.run(test_circle())
