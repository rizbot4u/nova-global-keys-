#!/bin/bash

echo "🔄 Restarting Nova Global Keys Microservices..."

supervisorctl restart all

echo "✅ All services restarted"
