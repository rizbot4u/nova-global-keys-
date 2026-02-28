#!/usr/bin/env python3
import requests
import os

API_KEY = os.getenv('CIRCLE_API_KEY')
url = "https://api.circle.com/v1/w3s/wallets"

try:
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=30
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
