#!/bin/bash

echo "🛑 Stopping Nova Global Keys Microservices..."

supervisorctl stop all

echo "✅ All services stopped"
