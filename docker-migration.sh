#!/bin/bash

# ============================================================================
# NOVA GLOBAL KEYS - DOCKER + KUBERNETES MIGRATION SCRIPT
# ============================================================================

set -e

echo "🚀 Starting Docker/Kubernetes migration..."

# ============================================================================
# 1. CREATE DOCKERFILES FOR EACH SERVICE
# ============================================================================

echo "📝 Creating Dockerfiles..."

# Base Python image for all services
cat > /root/nova-global-keys-/Dockerfile.base << 'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY services/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/shared ./shared
EOF

# Auth Service
cat > /root/nova-global-keys-/services/auth/Dockerfile << 'EOF'
FROM nova-base:latest

COPY auth/ ./auth/

CMD ["uvicorn", "auth.main:app", "--host", "0.0.0.0", "--port", "8001"]
EOF

# User Service
cat > /root/nova-global-keys-/services/user/Dockerfile << 'EOF'
FROM nova-base:latest

COPY user/ ./user/

CMD ["uvicorn", "user.main:app", "--host", "0.0.0.0", "--port", "8002"]
EOF

# Market Service
cat > /root/nova-global-keys-/services/market/Dockerfile << 'EOF'
FROM nova-base:latest

COPY market/ ./market/

CMD ["uvicorn", "market.main:app", "--host", "0.0.0.0", "--port", "8003"]
EOF

# Trade Service
cat > /root/nova-global-keys-/services/trade/Dockerfile << 'EOF'
FROM nova-base:latest

COPY trade/ ./trade/

CMD ["uvicorn", "trade.main:app", "--host", "0.0.0.0", "--port", "8004"]
EOF

# P2P Service
cat > /root/nova-global-keys-/services/p2p/Dockerfile << 'EOF'
FROM nova-base:latest

COPY p2p/ ./p2p/

CMD ["uvicorn", "p2p.main:app", "--host", "0.0.0.0", "--port", "8005"]
EOF

# Broker Service
cat > /root/nova-global-keys-/services/broker/Dockerfile << 'EOF'
FROM nova-base:latest

COPY broker/ ./broker/

CMD ["uvicorn", "broker.main:app", "--host", "0.0.0.0", "--port", "8006"]
EOF

# Gateway Service
cat > /root/nova-global-keys-/services/gateway/Dockerfile << 'EOF'
FROM nova-base:latest

COPY gateway/ ./gateway/

CMD ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8081"]
EOF

# Telegram Bot
cat > /root/nova-global-keys-/services/telegram/Dockerfile << 'EOF'
FROM nova-base:latest

COPY telegram/ ./telegram/

CMD ["python", "-m", "telegram.main"]
EOF

# Frontend
cat > /root/nova-global-keys-/frontend/Dockerfile << 'EOF'
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3000
CMD ["npm", "start"]
EOF

# ============================================================================
# 2. CREATE DOCKER-COMPOSE FILE
# ============================================================================

echo "📝 Creating docker-compose.yml..."

cat > /root/nova-global-keys-/docker-compose.yml << 'EOF'
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: nova-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - nova-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  auth:
    build: ./services/auth
    container_name: nova-auth
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - BROKER_CODE=${BROKER_CODE}
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - nova-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  user:
    build: ./services/user
    container_name: nova-user
    restart: unless-stopped
    ports:
      - "8002:8002"
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - nova-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  market:
    build: ./services/market
    container_name: nova-market
    restart: unless-stopped
    ports:
      - "8003:8003"
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - BROKER_CODE=${BROKER_CODE}
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - nova-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  trade:
    build: ./services/trade
    container_name: nova-trade
    restart: unless-stopped
    ports:
      - "8004:8004"
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - BROKER_CODE=${BROKER_CODE}
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - nova-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8004/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  p2p:
    build: ./services/p2p
    container_name: nova-p2p
    restart: unless-stopped
    ports:
      - "8005:8005"
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - nova-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8005/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  broker:
    build: ./services/broker
    container_name: nova-broker
    restart: unless-stopped
    ports:
      - "8006:8006"
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - MASTER_API_KEY=${MASTER_API_KEY}
      - MASTER_API_SECRET=${MASTER_API_SECRET}
      - BROKER_CODE=${BROKER_CODE}
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - nova-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8006/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  gateway:
    build: ./services/gateway
    container_name: nova-gateway
    restart: unless-stopped
    ports:
      - "8081:8081"
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - AUTH_SERVICE_URL=http://auth:8001
      - USER_SERVICE_URL=http://user:8002
      - MARKET_SERVICE_URL=http://market:8003
      - TRADE_SERVICE_URL=http://trade:8004
      - P2P_SERVICE_URL=http://p2p:8005
      - BROKER_SERVICE_URL=http://broker:8006
    depends_on:
      auth:
        condition: service_healthy
      user:
        condition: service_healthy
      market:
        condition: service_healthy
      trade:
        condition: service_healthy
      p2p:
        condition: service_healthy
      broker:
        condition: service_healthy
    networks:
      - nova-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  telegram:
    build: ./services/telegram
    container_name: nova-telegram
    restart: unless-stopped
    environment:
      - GATEWAY_URL=http://gateway:8081
      - TELEGRAM_TOKEN=${TELEGRAM_TOKEN}
      - BROKER_CODE=${BROKER_CODE}
    depends_on:
      gateway:
        condition: service_healthy
    networks:
      - nova-network

  frontend:
    build: ./frontend
    container_name: nova-frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://gateway:8081
    depends_on:
      gateway:
        condition: service_healthy
    networks:
      - nova-network

networks:
  nova-network:
    driver: bridge

volumes:
  redis-data:
EOF

# ============================================================================
# 3. CREATE KUBERNETES MANIFESTS
# ============================================================================

echo "📝 Creating Kubernetes manifests..."

mkdir -p /root/nova-global-keys-/k8s

# Redis
cat > /root/nova-global-keys-/k8s/redis.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: nova
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: nova
spec:
  ports:
  - port: 6379
    targetPort: 6379
  selector:
    app: redis
EOF

# Auth Service
cat > /root/nova-global-keys-/k8s/auth.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth
  namespace: nova
spec:
  replicas: 2
  selector:
    matchLabels:
      app: auth
  template:
    metadata:
      labels:
        app: auth
    spec:
      containers:
      - name: auth
        image: novaglobal/auth:latest
        ports:
        - containerPort: 8001
        env:
        - name: REDIS_HOST
          value: redis
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: nova-secrets
              key: jwt-secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: auth
  namespace: nova
spec:
  ports:
  - port: 8001
    targetPort: 8001
  selector:
    app: auth
EOF

# Gateway
cat > /root/nova-global-keys-/k8s/gateway.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gateway
  namespace: nova
spec:
  replicas: 2
  selector:
    matchLabels:
      app: gateway
  template:
    metadata:
      labels:
        app: gateway
    spec:
      containers:
      - name: gateway
        image: novaglobal/gateway:latest
        ports:
        - containerPort: 8081
        env:
        - name: REDIS_HOST
          value: redis
        - name: AUTH_SERVICE_URL
          value: http://auth:8001
        - name: USER_SERVICE_URL
          value: http://user:8002
        - name: MARKET_SERVICE_URL
          value: http://market:8003
        - name: TRADE_SERVICE_URL
          value: http://trade:8004
        - name: P2P_SERVICE_URL
          value: http://p2p:8005
        - name: BROKER_SERVICE_URL
          value: http://broker:8006
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8081
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: gateway
  namespace: nova
spec:
  ports:
  - port: 8081
    targetPort: 8081
  selector:
    app: gateway
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nova-ingress
  namespace: nova
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: api.novatradingkeys.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: gateway
            port:
              number: 8081
EOF

# Secrets
cat > /root/nova-global-keys-/k8s/secrets.yaml << 'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: nova-secrets
  namespace: nova
type: Opaque
stringData:
  jwt-secret: "your-256-bit-secret-here-change-in-production"
  broker-code: "Kr000820"
  affiliate-id: "127146"
  telegram-token: "your-telegram-token-here"
  master-api-key: "your-master-key-here"
  master-api-secret: "your-master-secret-here"
EOF

# Namespace
cat > /root/nova-global-keys-/k8s/namespace.yaml << 'EOF'
apiVersion: v1
kind: Namespace
metadata:
  name: nova
EOF

# ============================================================================
# 4. CREATE DEPLOYMENT SCRIPTS
# ============================================================================

echo "📝 Creating deployment scripts..."

# Docker build script
cat > /root/nova-global-keys-/docker-build.sh << 'EOF'
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
EOF

# Docker run script
cat > /root/nova-global-keys-/docker-up.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting services with Docker Compose..."
docker-compose up -d

echo "📊 Container status:"
docker-compose ps

echo "📝 Logs:"
docker-compose logs -f
EOF

# Kubernetes deploy script
cat > /root/nova-global-keys-/k8s-deploy.sh << 'EOF'
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
EOF

# ============================================================================
# 5. CREATE .ENV TEMPLATE
# ============================================================================

cat > /root/nova-global-keys-/.env.docker << 'EOF'
# JWT Configuration
JWT_SECRET_KEY=your-256-bit-secret-here-change-in-production

# Bybit Configuration
BROKER_CODE=Kr000820
AFFILIATE_ID=127146
MASTER_API_KEY=your-master-key-here
MASTER_API_SECRET=your-master-secret-here

# Telegram
TELEGRAM_TOKEN=your-telegram-token-here

# Redis
REDIS_PASSWORD=your-redis-password
EOF

# ============================================================================
# 6. CREATE MIGRATION GUIDE
# ============================================================================

cat > /root/nova-global-keys-/MIGRATION.md << 'EOF'
# 🚀 Migration Guide: PM2 → Docker/Kubernetes

## 📋 Prerequisites
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt-get install docker-compose-plugin

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
mv kubectl /usr/local/bin/

# Install minikube (for local testing)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
install minikube-linux-amd64 /usr/local/bin/minikube
