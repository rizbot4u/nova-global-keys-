#!/bin/bash

echo "☸️  Deploying to Kubernetes..."

# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets
kubectl apply -f k8s/secrets.yaml

# Deploy services in order
kubectl apply -f k8s/redis.yaml

echo "⏳ Waiting for Redis..."
kubectl wait --for=condition=available --timeout=60s deployment/redis -n nova

kubectl apply -f k8s/auth.yaml
kubectl apply -f k8s/user.yaml
kubectl apply -f k8s/market.yaml
kubectl apply -f k8s/trade.yaml
kubectl apply -f k8s/p2p.yaml
kubectl apply -f k8s/broker.yaml

echo "⏳ Waiting for services..."
sleep 30

kubectl apply -f k8s/gateway.yaml
kubectl apply -f k8s/telegram.yaml

echo "📊 Pod status:"
kubectl get pods -n nova

echo "📊 Service status:"
kubectl get services -n nova

echo "📊 Ingress status:"
kubectl get ingress -n nova
