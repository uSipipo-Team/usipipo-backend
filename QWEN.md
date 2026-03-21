# uSipipo Backend - Project Context

## 📋 Overview

**usipipo-backend** is the main FastAPI backend for the uSipipo VPN ecosystem. It provides REST APIs for user management, VPN key generation, payments, subscriptions, and consumption billing.

**Current Version:** v0.2.0
**Status:** In Development
**Migration Progress:** 52% complete (5.2/10 features)

---

## 🏗️ Architecture

### Clean Architecture Layers

```
src/
├── core/
│   ├── domain/
│   │   ├── entities/         # Business entities (from usipipo-commons)
│   │   └── interfaces/       # Repository interfaces (IUserRepository, etc.)
│   └── application/
│       └── services/         # Application services (UserService, VpnService, etc.)
├── infrastructure/
│   ├── api/
│   │   ├── routes/           # FastAPI routers (v1, v2)
│   │   ├── deps/             # Dependencies (get_db, get_current_user)
│   │   └── middleware/       # Custom middleware (auth, logging)
│   ├── persistence/
│   │   ├── models/           # SQLAlchemy models
│   │   └── repositories/     # Repository implementations
│   ├── vpn_providers/
│   │   ├── wireguard_client.py   # Native wg commands
│   │   └── outline_client.py     # Shadowbox API
│   ├── payment_gateways/
│   │   ├── stripe_client.py
│   │   ├── telegram_stars_client.py
│   │   └── trondealer_client.py
│   ├── cache/
│   │   └── redis_client.py
│   └── jobs/
│       ├── key_cleanup_job.py      # Daily cleanup
│       └── usage_sync_job.py       # Every 30 min sync
├── shared/
│   ├── config/
│   │   └── settings.py       # Pydantic settings
│   └── exceptions/
│       └── handlers.py       # Global exception handlers
├── __init__.py
├── __main__.py               # Entry point (uvicorn)
└── main.py                   # FastAPI app instance
```

### Service Layer Pattern

```
┌─────────────────────────────────────────┐
│         API Routes (FastAPI)            │
├─────────────────────────────────────────┤
│      Application Services               │
│  (UserService, VpnService, etc.)        │
├─────────────────────────────────────────┤
│     Domain Entities + Repositories      │
│  (from usipipo-commons + interfaces)    │
├─────────────────────────────────────────┤
│   Infrastructure (SQLAlchemy, VPN)      │
└─────────────────────────────────────────┘
```

---

## 🚀 Building and Running

### Prerequisites

- Python 3.13+
- uv package manager
- PostgreSQL 15+
- Docker (optional)

### Local Development

```bash
cd usipipo-backend

# Install dependencies
uv sync --dev

# Configure environment
cp example.env .env
# Edit .env with your settings

# Run database migrations
uv run alembic upgrade head

# Run tests
uv run pytest

# Start development server
uv run python -m src

# Or with auto-reload
uv run uvicorn src.main:app --reload --env-file .env
```

### Docker

```bash
# Build
docker build -t usipipo-backend .

# Run with environment
docker run --env-file .env -p 8000:8000 usipipo-backend

# Docker Compose
docker-compose up -d
```

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | JWT secret key | ✅ | - |
| `DATABASE_URL` | PostgreSQL connection | ✅ | - |
| `APP_ENV` | Environment (development/production) | ❌ | development |
| `DEBUG` | Enable debug mode | ❌ | false |
| `API_PREFIX` | API path prefix | ❌ | /api/v1 |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | ❌ | - |
| `STRIPE_SECRET_KEY` | Stripe API key | ❌ | - |
| `TRONDEALER_API_KEY` | TronDealer API key | ❌ | - |

---

## 🧪 Testing

### Run Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=html

# Specific test file
uv run pytest tests/integration/test_vpn_infrastructure.py -v

# Specific test marker
uv run pytest -m "not slow"
uv run pytest -m integration
```

### Test Structure

```
tests/
├── unit/
│   ├── test_services/
│   ├── test_entities/
│   └── test_utils/
├── integration/
│   ├── test_vpn_infrastructure.py
│   ├── test_payment_endpoints.py
│   └── test_subscription_endpoints.py
└── conftest.py
```

### Test Markers

- `@pytest.mark.asyncio` - Async tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow tests (can be skipped)

---

## 📦 Implemented Features

### ✅ Feature 1: Payments (100%)

**Services:**
- `PaymentService` - Create, complete, expire payments

**Endpoints:**
- `POST /api/v1/payments` - Create payment
- `GET /api/v1/payments/{id}` - Get payment status
- `POST /api/v1/webhooks/trondealer` - Crypto webhook
- `POST /api/v1/webhooks/telegram-stars` - Stars webhook

**Tests:** 18 passing

---

### ✅ Feature 2: VPN Management (100%)

**Services:**
- `VpnService` - CRUD operations
- `VpnInfrastructureService` - Server coordination
- `ConsumptionVpnIntegrationService` - Billing integration

**Jobs:**
- `KeyCleanupJob` - Daily cleanup
- `UsageSyncJob` - Every 30 min sync

**Endpoints:**
- `GET /api/v1/vpn-keys` - List keys
- `POST /api/v1/vpn-keys` - Create key
- `DELETE /api/v1/vpn-keys/{id}` - Delete key
- `PUT /api/v1/vpn-keys/{id}` - Update key

**Tests:** 9 integration tests passing

---

### ✅ Feature 3: Subscriptions (100%)

**Services:**
- `SubscriptionService` - Activate, cancel, check
- `SubscriptionPaymentService` - Stars + Crypto

**Repositories:**
- `ISubscriptionRepository`
- `ISubscriptionTransactionRepository`

**Endpoints:**
- `GET /api/v1/subscriptions/plans` - List plans
- `POST /api/v1/subscriptions/activate` - Activate subscription
- `GET /api/v1/subscriptions/me` - User subscription status

**Tests:** 148 tests passing

---

### 🟡 Feature 4: Consumption Billing (60%)

**Services:**
- `ConsumptionBillingService` - Facade
- `ConsumptionActivationService` - Mode switching
- `ConsumptionCycleService` - Usage tracking

**Pending:**
- Repository implementations
- Endpoints
- Invoice service

**Tests:** 46 unit tests passing

---

### ✅ Feature 10: User Management (100%)

**Services:**
- `UserService` - CRUD operations

**Endpoints:**
- `POST /api/v1/users` - Create user
- `GET /api/v1/users/{id}` - Get user
- `POST /api/v1/auth/telegram` - Telegram auth

---

## 📊 Migration Progress

| Feature | Entities | Services | Repos | Endpoints | Tests | Status |
|---------|----------|----------|-------|-----------|-------|--------|
| 1. Payments | ✅ | ✅ | ✅ | ✅ | ✅ | 100% |
| 2. VPN Management | ✅ | ✅ | ✅ | ✅ | ✅ | 100% |
| 3. Subscriptions | ✅ | ✅ | ✅ | ✅ | ✅ | 100% |
| 4. Consumption Billing | ✅ | ✅ | ⏳ | ⏳ | ✅ | 60% |
| 5. Tickets/Support | ✅ | ❌ | ❌ | ❌ | ❌ | 20% |
| 6. Referrals | ❌ | ❌ | ❌ | ❌ | ❌ | 0% |
| 7. Admin Panel | ✅ | ❌ | ❌ | ❌ | ❌ | 20% |
| 8. Wallet Management | ❌ | ❌ | ❌ | ❌ | ❌ | 0% |
| 9. Data Packages | ✅ | ❌ | ❌ | ❌ | ❌ | 20% |
| 10. User Management | ✅ | ✅ | ✅ | ✅ | ✅ | 100% |

**Overall:** 52% complete

---

## 🔧 Development Conventions

### Code Style

- **Line Length:** 100 characters
- **Quote Style:** Double quotes
- **Indent:** 4 spaces
- **Imports:** Sorted by ruff (isort)
- **Type Hints:** Required for all public functions

### Linting

```bash
# Run ruff
uv run ruff check .

# Run mypy
uv run mypy .

# Format code
uv run ruff format .
```

### Git Workflow

- **Main Branch:** `main` (protected)
- **Feature Branches:** `feature/<name>`
- **Bug Fixes:** `fix/<name>`
- **PR Required:** Yes, with status checks

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `src/main.py` | FastAPI app instance |
| `src/__main__.py` | Entry point for `python -m src` |
| `src/core/application/services/` | Business logic |
| `src/infrastructure/persistence/` | Database layer |
| `src/infrastructure/vpn_providers/` | VPN server clients |
| `src/infrastructure/jobs/` | Scheduled jobs |
| `pyproject.toml` | Project configuration |
| `.env` | Environment variables (gitignored) |
| `docker-compose.yml` | Local development stack |

---

## 🔗 Dependencies

### Runtime

- `usipipo-commons @ file:///home/mowgli/usipipo/usipipo-commons`
- `fastapi>=0.109.0`
- `uvicorn[standard]>=0.27.0`
- `pydantic-settings>=2.0.0`
- `sqlalchemy[asyncio]>=2.0.0`
- `asyncpg>=0.29.0`
- `alembic>=1.13.0`
- `pyjwt>=2.8.0`
- `python-jose[cryptography]>=3.3.0`
- `aiosqlite>=0.20.0`
- `httpx>=0.27.0`

### Development

- `pytest>=8.0.0`
- `pytest-asyncio>=0.23.0`
- `pytest-cov>=4.0.0`
- `mypy>=1.0.0`
- `ruff>=0.1.0`
- `pre-commit>=3.6.0`
- `bandit>=1.7.0`

---

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API](docs/API.md)
- [Deployment](docs/DEPLOYMENT.md)

---

## 🔗 Links

- **GitHub:** https://github.com/uSipipo-Team/usipipo-backend
- **PyPI (commons):** https://pypi.org/project/usipipo-commons/
- **Migration Tracker:** ../plans/MIGRATION-PROGRESS.md

---

**Last Updated:** 2026-03-21
**Maintained By:** uSipipo Team <dev@usipipo.com>
