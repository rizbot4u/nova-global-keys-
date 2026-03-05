#!/bin/bash

echo "🚀 Starting services with Docker Compose..."
docker-compose up -d

echo "📊 Container status:"
docker-compose ps

echo "📝 Logs:"
docker-compose logs -f
