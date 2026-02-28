#!/usr/bin/env python3
import os
import httpx
import asyncio

async def test_circle():
    api_key = os.getenv('CIRCLE_API_KEY', 'TEST_API_KEY:098dcc861cbd439aebd564a161db04e2:40e097c60563e1f3be8c7a96524d738c')
    
    async with httpx.AsyncClient() as client:
        # Test 1: Configuration endpoint
        print("Testing configuration endpoint...")
        resp = await client.get(
            'https://api-sandbox.circle.com/v1/configuration',
            headers={'Authorization': f'Bearer {api_key}'}
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}\n")
        
        if resp.status_code == 200:
            print("✅ Key is valid! Now let's check available wallet sets...")
            
            # Test 2: List wallet sets
            resp = await client.get(
                'https://api-sandbox.circle.com/v1/developer/walletSets',
                headers={'Authorization': f'Bearer {api_key}'}
            )
            print(f"Wallet Sets: {resp.status_code}")
            print(f"Response: {resp.text}")

asyncio.run(test_circle())
