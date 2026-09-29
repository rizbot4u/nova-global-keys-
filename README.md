Nova Global Keys is a production-grade crypto trading platform built around Bybit Level 3 Broker status (Kr000820). It runs as a 9-microservice backend on a self-managed Ubuntu VPS, with a Next.js frontend, Redis-backed session management, Kubernetes manifests for horizontal scale, and live Bybit V5 API integration.

The platform supports:

· Bybit OAuth 2.0 — users connect their exchange account via official broker flow
· Multi-strategy trading — DCA, DEX, triangle arbitrage, grid trading
· P2P payments — Easypaisa/JazzCash merchant rails
· Telegram bot — full user-facing interface
· MetaTrader 5 bridge — Dockerized MT5 integration
· Remittance & compliance module
· Signal bot — automated trading signals
· Social bot — multi-platform posting automation

Tech stack: Python · FastAPI · Node.js · Redis · PostgreSQL · SQLite · Nginx · systemd · PM2 · Docker · Kubernetes · Next.js · ethers.js · Bybit V5 · Binance · MT5.