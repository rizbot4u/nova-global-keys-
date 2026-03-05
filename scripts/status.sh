#!/bin/bash

echo "📊 Nova Global Keys - Service Status"
echo "===================================="

supervisorctl status

echo ""
echo "Redis Status:"
redis-cli ping

echo ""
echo "Gateway Health:"
curl -s http://127.0.0.1:8081/health | python -m json.tool
