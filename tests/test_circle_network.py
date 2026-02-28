#!/usr/bin/env python3
import socket
import ssl
import httpx
import asyncio

async def test_connection():
    print("🔍 Testing Circle API connectivity...")
    
    # Test 1: DNS resolution
    try:
        ip = socket.gethostbyname('api-sandbox.circle.com')
        print(f"✅ DNS resolved: {ip}")
    except Exception as e:
        print(f"❌ DNS failed: {e}")
    
    # Test 2: TCP connection
    try:
        reader, writer = await asyncio.open_connection('api-sandbox.circle.com', 443)
        print("✅ TCP connection successful")
        writer.close()
        await writer.wait_closed()
    except Exception as e:
        print(f"❌ TCP connection failed: {e}")
    
    # Test 3: HTTPX with timeout
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get('https://api-sandbox.circle.com/ping')
            print(f"✅ HTTP request successful: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ HTTP request failed: {e}")

asyncio.run(test_connection())
