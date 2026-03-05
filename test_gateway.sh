#!/bin/bash

# Configuration
BASE_URL="http://127.0.0.1:8081"
ENDPOINTS=(
    "/health"
    "/api/market/tickers/BTCUSDT"
    "/api/auth/status"
    "/api/users/me"
    "/api/bots/active"
)

echo "--- Starting Nova Gateway Health Check ---"

for route in "${ENDPOINTS[@]}"
do
    echo -n "Testing $route... "
    # -s: silent, -o /dev/null: don't show body, -w: output the HTTP status code
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$route")
    
    if [ "$STATUS" -eq 200 ]; then
        echo -e "\e[32m[PASS] ($STATUS)\e[0m"
    elif [ "$STATUS" -eq 401 ] || [ "$STATUS" -eq 404 ]; then
        echo -e "\e[33m[CHECK] ($STATUS - Likely needs Auth or Path is custom)\e[0m"
    else
        echo -e "\e[31m[FAIL] ($STATUS)\e[0m"
    fi
done

echo "--- Check Complete ---"
