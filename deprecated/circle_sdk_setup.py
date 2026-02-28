#!/usr/bin/env python3
"""
Circle Developer Wallets SDK Setup
Uses official Circle Python SDK
"""

import os
from circle_developer_sdk import CircleDeveloperClient
import asyncio

# Your API key from Circle Developer Console
API_KEY = os.getenv('CIRCLE_API_KEY', 'YOUR_API_KEY_HERE')
# Your entity secret (from openssl rand -hex 32)
ENTITY_SECRET = os.getenv('ENTITY_SECRET', 'YOUR_32_BYTE_HEX_SECRET')

async def main():
    print("🚀 Setting up Circle Developer Wallets with SDK")
    print("=" * 50)
    
    # Initialize the SDK client
    client = CircleDeveloperClient(
        api_key=API_KEY,
        entity_secret=ENTITY_SECRET,
        base_url="https://api-sandbox.circle.com"
    )
    
    # Step 1: Create Wallet Set
    print("\n1️⃣ Creating Wallet Set...")
    wallet_set = await client.create_wallet_set(
        name="NOVA Remittance Wallet Set"
    )
    wallet_set_id = wallet_set['data']['walletSet']['id']
    print(f"✅ Wallet Set created: {wallet_set_id}")
    
    # Step 2: Create Wallets on Polygon
    print("\n2️⃣ Creating wallets on Polygon Amoy...")
    wallets = await client.create_wallets(
        wallet_set_id=wallet_set_id,
        blockchains=["MATIC-AMOY"],
        count=2,
        account_type="SCA"
    )
    
    for wallet in wallets['data']['wallets']:
        print(f"✅ Wallet: {wallet['address']} (ID: {wallet['id']})")
    
    # Step 3: Create wallets on Solana
    print("\n3️⃣ Creating wallets on Solana Devnet...")
    sol_wallets = await client.create_wallets(
        wallet_set_id=wallet_set_id,
        blockchains=["SOL-DEVNET"],
        count=1,
        account_type="EOA"
    )
    
    for wallet in sol_wallets['data']['wallets']:
        print(f"✅ Solana Wallet: {wallet['address']} (ID: {wallet['id']})")
    
    print("\n🎉 Wallet setup complete!")
    print(f"Wallet Set ID: {wallet_set_id}")
    print("Save this ID for future reference")

if __name__ == "__main__":
    asyncio.run(main())
