import requests
import time
import random

BASE_URL = "http://31.97.220.195:8080"
SESSION = "3b2369a578c04c81a17975861ed08948"
HEADERS = {"authorization": SESSION}

endpoints = [
    "/api/health",
    "/api/market/time",
    "/api/market/tickers?symbol=BTCUSDT",
    "/api/v1/price/BTCUSDT",
    "/api/v1/user/info",
    "/api/v1/balance",
]

count = 0
while True:
    for ep in endpoints:
        try:
            r = requests.get(BASE_URL + ep, headers=HEADERS)
            print(f"[{count}] {ep} - {r.status_code}")
            count += 1
            time.sleep(0.1)  # 10 requests per second
        except:
            pass
