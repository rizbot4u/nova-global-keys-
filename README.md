# Nova Global Keys

**Production crypto trading platform.** Bybit Level 3 Broker (Kr000820). 9 microservices on a self-managed Ubuntu VPS. Real OAuth 2.0 integration, multi-strategy trading engine, and Redis-backed session management.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-async-green)
![Bybit](https://img.shields.io/badge/Bybit-Level%203%20Broker-orange)
![Base](https://img.shields.io/badge/Base-Mainnet-blueviolet)

---

## What This Is

Nova Global Keys is a full-stack trading platform built around **Bybit Level 3 Broker** status. It runs as a 9-service backend behind Nginx, manages user sessions via Redis, and provides both a Telegram bot and a Next.js web interface to end users.

The platform handles:

- **Bybit OAuth 2.0 onboarding** — users connect their exchange account through official broker flow
- **Live market data** — tickers, klines, order books across spot and linear categories
- **Order execution** — signed Bybit V5 API calls with HMAC-SHA256
- **Multi-strategy trading** — DCA, DEX routing, triangle arbitrage, grid trading
- **P2P payment rails** — Easypaisa / JazzCash merchant integration
- **MetaTrader 5 bridge** — Dockerized MT5 for multi-broker support
- **Signal + social automation** — outbound notifications and posting

---

## Architecture

```
                    ┌─────────────────┐
                    │  Telegram Bot   │
                    │  Next.js Web    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Nginx (reverse │
                    │  proxy) :443    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  API Gateway    │
                    │  :8080          │
                    └────────┬────────┘
                             │
    ┌────────────────────────┼────────────────────────┐
    │                        │                        │
┌───▼────┐             ┌─────▼─────┐            ┌─────▼─────┐
│  auth  │             │   trade   │            │   user    │
│ broker │             │   market  │            │   p2p     │
└───┬────┘             └─────┬─────┘            └─────┬─────┘
    │                        │                        │
    └────────────────────────┼────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │      Redis      │
                    │  (sessions,     │
                    │   bot state,    │
                    │   cache)        │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
      ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐
      │ Bybit V5  │    │  Binance  │    │    MT5    │
      │ (OAuth)   │    │   REST    │    │  Bridge   │
      └───────────┘    └───────────┘    └───────────┘
```

---

## Services

| Service | Port | Responsibility |
|---|---|---|
| `api-gateway` | 8080 | Public HTTP entry — routes, auth, rate limits |
| `auth` | internal | OAuth 2.0 flow, JWT issuance, session validation |
| `broker` | internal | Bybit/Binance integration, signed requests |
| `market` | internal | Tickers, klines, order books, rate-limited cache |
| `trade` | internal | Order placement, cancellation, history |
| `user` | internal | Profiles, balances, KYC status, preferences |
| `p2p` | internal | Payment rails (Easypaisa / JazzCash) |
| `telegram` | — | User-facing bot interface |
| `shared` | — | Common utilities, models, error handling |

All services are managed by **PM2** on a single Ubuntu VPS, fronted by **Nginx**, and run as a **systemd** unit (`nova.service`).

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11 · FastAPI · httpx · Pydantic |
| **Frontend** | Next.js · React |
| **State** | Redis (sessions, bots, cache) · SQLite (persistent config) |
| **Infra** | Ubuntu VPS · Nginx · systemd · PM2 · Docker |
| **Scale-out** | Kubernetes manifests included (`k8s/`) |
| **Exchanges** | Bybit V5 · Binance REST |
| **Web3** | ethers.js v6 · Base Mainnet |
| **MT5** | MetaTrader 5 via Docker bridge |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/rizbot4u/nova-global-keys-.git
cd nova-global-keys-

# 2. Configure (fill in your own credentials)
cp .env.example .env
nano .env

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start Redis (if not already running)
redis-server --daemonize yes

# 5. Run the gateway
uvicorn api.main:app --host 0.0.0.0 --port 8080

# 6. Or start everything with PM2 (production mode)
pm2 start config/ecosystem.config.js
```

Docs available at `http://localhost:8080/docs`.

---

## API Surface

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health, Redis status, broker code |
| `GET` | `/api/market/tickers` | Spot/linear ticker data |
| `GET` | `/api/market/kline` | OHLC klines |
| `GET` | `/api/account/wallet-balance` | Unified wallet (signed) |
| `GET` | `/api/account/info` | Account metadata (signed) |
| `GET` | `/api/position/list` | Open positions (signed) |
| `GET` | `/api/trade/open-orders` | Open orders (signed) |
| `GET` | `/api/trade/order-history` | Historical orders (signed) |
| `POST` | `/api/trade/place-order` | Place order (signed) |
| `POST` | `/api/trade/cancel-order` | Cancel order (signed) |
| `GET` | `/api/auth/oauth-url` | Generate Bybit OAuth URL |
| `GET` | `/api/auth/callback/bybit` | OAuth callback handler |
| `GET` | `/api/bots/all` | List user's trading bots |
| `POST` | `/api/bots/start` | Start a strategy bot |
| `POST` | `/api/bots/stop` | Stop a strategy bot |

Full OpenAPI docs at `/docs` when running.

---

## Trading Strategies

| Strategy | File | Description |
|---|---|---|
| **DCA** | `strategies/dca.py` | Dollar-cost averaging with configurable intervals |
| **DEX** | `strategies/dex.py` | On-chain routing via DEX aggregators |
| **Triangle** | `strategies/triangle.py` | Cross-pair arbitrage (A→B→C→A) |
| **Grid** | `strategies/grid.py` | Range-bound grid trading |

Each strategy runs as an independent worker and persists state to Redis (`user:<uid>:bot:<name>`).

---

## Live Proof

The platform is live and has processed real broker-integrated volume:

- **Bybit Broker:** Kr000820 — Level 3 Institutional ([verification](https://www.bybit.com/en/verification/))
- **OAuth Client:** `x9dmxAGkDDoa` (verified against Bybit's official domain)
- **Affiliate ID:** `127146`
- **Recent 30-day trading volume:** $14.8M
- **Supported exchanges:** Bybit V5, Binance

---

## Security Model

- **OAuth 2.0 flow** — users connect exchanges without sharing credentials
- **HMAC-SHA256 signing** — every state-changing Bybit request is signed
- **Redis for sessions** — bound to localhost, password-protected
- **Nginx reverse proxy** — TLS termination, request filtering
- **Per-user isolation** — bot state and API keys namespaced by UID
- **No plaintext secrets in code** — all credentials loaded from `.env`

> ⚠️ **Never commit `.env`.** The `.env.example` file contains placeholder values only.

---

## Repository Structure

```
nova-global-keys-/
├── api/              REST endpoints (auth, broker, health, trade, market)
├── config/           Settings, nginx, PM2 ecosystem, supervisor
├── core/             broker_engine.py, exchange_client.py, redis_client.py
├── services/         9 microservices (auth, broker, gateway, market,
│                     p2p, telegram, trade, user, shared)
├── strategies/       Trading strategies (dca, dex, triangle, grid, base)
├── workers/          Strategy runner
├── frontend/         Next.js application
├── k8s/              Kubernetes manifests
├── mt5/              MetaTrader 5 integration
├── mt5-docker/       Dockerized MT5 bridge
├── remittance/       Compliance + core + templates + webhooks
├── social_bot/       Social media automation
├── signals/          Signal bot + Thor engine
├── scripts/          Operational scripts (backup, launch, debug)
├── tests/            Test suite (15+ files)
└── docs/             Architecture, API reference
```

---

## Status

| Component | Status |
|---|---|
| Bybit broker integration | Live |
| OAuth 2.0 flow | Live |
| Market data (spot, linear) | Live |
| Order execution | Live |
| Redis session management | Live |
| Telegram bot | Live |
| Next.js frontend | Live |
| MT5 bridge | In progress |
| P2P payment rails | Sandbox |
| Kubernetes rollout | Manifests ready |

---

## What I'd Improve Next

- Migrate persistent config from SQLite → PostgreSQL with row-level security
- Move Redis credentials from env → HashiCorp Vault or AWS Secrets Manager
- Add Prometheus + Grafana for service observability
- CI/CD via GitHub Actions (currently manual deploy)
- Integration tests for the OAuth flow end-to-end

---

## Contact

**Rizwan Ali**
Founder · Nova Global Keys

- LinkedIn: [linkedin.com/in/rizwan-ali-974073377](https://www.linkedin.com/in/rizwan-ali-974073377)
- GitHub: [github.com/rizbot4u](https://github.com/rizbot4u)
- Bybit Broker: Kr000820

---

*Built solo. Two years ago I couldn't write a for-loop.*