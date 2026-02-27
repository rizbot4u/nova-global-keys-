#!/usr/bin/env python3
"""
Circle Developer Wallets Setup
Based on official Circle documentation
"""

import os
import json
import httpx
import asyncio
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64
import uuid

# Your API key from Circle Developer Console (W3S product)
API_KEY = os.getenv('CIRCLE_API_KEY', 'YOUR_API_KEY_HERE')
ENTITY_SECRET = os.getenv('ENTITY_SECRET', 'YOUR_32_BYTE_HEX_SECRET')  # From openssl command
BASE_URL = "https://api-sandbox.circle.com/v1/developer"

def encrypt_entity_secret(entity_secret_hex: str, public_key: str) -> str:
    """
    Encrypt entity secret with Circle's public key
    This is required by Circle's API
    """
    # This is a simplified version - Circle's SDK handles this automatically
    # For now, we'll use the SDK which does this internally
    pass

async def create_wallet_set():
    """Step 1: Create a Wallet Set"""
    async with httpx.AsyncClient() as client:
        # Create wallet set
        response = await client.post(
            f"{BASE_URL}/walletSets",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "name": "NOVA Remittance Wallet Set",
                # Note: entitySecretCiphertext is handled by SDK
                # For direct API, you need to encrypt with Circle's public key first
            }
        )
        
        print(f"Wallet Set Creation Status: {response.status_code}")
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            wallet_set_id = data.get('data', {}).get('walletSet', {}).get('id')
            print(f"✅ Wallet Set Created: {wallet_set_id}")
            return wallet_set_id
        else:
            print(f"❌ Error: {response.text}")
            return None

async def create_wallets(wallet_set_id: str, blockchain: str = "MATIC-AMOY"):
    """Step 2: Create Wallets in the set"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/wallets",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "walletSetId": wallet_set_id,
                "blockchains": [blockchain],
                "count": 2,  # Create 2 wallets as per example
                "accountType": "SCA"  # Smart Contract Account for EVM chains
            }
        )
        
        print(f"Wallet Creation Status: {response.status_code}")
        if response.status_code == 200 or response.status_code == 201:
            wallets = response.json().get('data', {}).get('wallets', [])
            print(f"✅ Created {len(wallets)} wallets:")
            for wallet in wallets:
                print(f"   - {wallet['blockchain']}: {wallet['address']} (ID: {wallet['id']})")
            return wallets
        else:
            print(f"❌ Error: {response.text}")
            return []

async def main():
    print("🚀 Setting up Circle Developer Wallets")
    print("=" * 50)
    
    # Step 1: Create Wallet Set
    wallet_set_id = await create_wallet_set()
    if not wallet_set_id:
        print("❌ Failed to create wallet set. Exiting.")
        return
    
    # Step 2: Create Wallets on different chains
    print("\n📦 Creating wallets on Polygon Amoy...")
    await create_wallets(wallet_set_id, "MATIC-AMOY")
    
    print("\n📦 Creating wallets on Solana Devnet...")
    await create_wallets(wallet_set_id, "SOL-DEVNET")

if __name__ == "__main__":
    asyncio.run(main())
