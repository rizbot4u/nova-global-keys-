#!/bin/bash

echo "🏗️  Building base image..."
docker build -t nova-base:latest -f Dockerfile.base .

echo "🏗️  Building service images..."
for service in auth user market trade p2p broker gateway telegram; do
    echo "Building $service..."
    docker build -t novaglobal/$service:latest ./services/$service
done

echo "🏗️  Building frontend..."
docker build -t novaglobal/frontend:latest ./frontend

echo "✅ All images built!"
