#!/bin/bash

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyaXp3YW5fc2FpbUBob3RtYWlsLmNvbSIsImV4cCI6MTc3MjgwOTgzOSwiaWF0IjoxNzcyNzIzNDM5fQ.hQXmNeQN9PbxdpWylIUib62B7g9up7q7LJySfQjnRIc"

echo "🔍 Testing Gateway Health"
curl -s http://127.0.0.1:8081/health | python3 -m json.tool
echo ""

echo "🔍 Testing Trade Service Health"
curl -s http://127.0.0.1:8004/health | python3 -m json.tool
echo ""

echo "🔍 Listing Connected Exchanges"
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8081/api/keys/list | python3 -m json.tool
echo ""

echo "🔍 Testing Bybit Balance (if connected)"
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8081/api/bybit/balance | python3 -m json.tool
echo ""

echo "✅ Done!"
