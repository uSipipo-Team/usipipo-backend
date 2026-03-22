# uSipipo Backend

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue)](https://mypy-lang.org/)

> **Backend API principal del ecosistema uSipipo** — VPN service platform for LATAM community

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Testing](#-testing)
- [Docker Deployment](#-docker-deployment)
- [Environment Variables](#-environment-variables)
- [Database Migrations](#-database-migrations)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌐 Overview

**uSipipo Backend** is a production-ready FastAPI application that serves as the core API for the uSipipo VPN ecosystem. It provides secure VPN key management, payment processing, subscription handling, consumption billing, and user management services for the LATAM community.

### Key Capabilities

- 🔐 **Authentication & Authorization** — JWT-based auth with role management
- 🌐 **VPN Management** — WireGuard and Outline key generation and lifecycle
- 💳 **Payment Processing** — Multiple payment methods including crypto and Telegram Stars
- 📦 **Subscription Plans** — Tiered subscription management with automatic renewal
- 📊 **Consumption Billing** — Pay-per-usage billing for VPN consumption
- 🎁 **Referral System** — Referral bonuses and tracking
- 🎫 **Support Tickets** — Customer support ticketing system
- 💰 **Wallet System** — Balance management and transactions
- 🔗 **Webhooks** — Real-time webhook integration for payments and events

---

## ✨ Features

| Feature | Status | Description |
|---------|--------|-------------|
| **User Management** | ✅ | Complete user CRUD with authentication |
| **VPN Keys** | ✅ | WireGuard + Outline key generation and management |
| **Payments** | ✅ | Multiple payment providers (crypto, Telegram Stars) |
| **Subscriptions** | ✅ | Tiered subscription plans with auto-renewal |
| **Consumption Billing** | 🟡 | Usage-based billing with invoice generation |
| **Data Packages** | ✅ | Prepaid data package system |
| **Referrals** | ✅ | Referral program with bonus tracking |
| **Support Tickets** | ✅ | Customer support ticketing system |
| **Wallet** | ✅ | Balance and transaction management |
| **Admin Panel** | ✅ | Administrative endpoints and monitoring |
| **Webhooks** | ✅ | Crypto and Telegram webhook handlers |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    uSipipo Backend                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐     ┌──────────────┐                │
│  │  Telegram    │     │   Mini App   │                │
│  │     Bot      │     │    (Web)     │                │
│  └──────┬───────┘     └──────┬───────┘                │
│           │                  │                         │
│           └────────┬─────────┘                        │
│                    ▼                                  │
│           ┌───────────────┐                           │
│           │   FastAPI     │                           │
│           │   Backend     │                           │
│           └───────┬───────┘                           │
│                   │                                   │
│           ┌───────▼────────┐                          │
│           │   Application  │                          │
│           │    Services    │                          │
│           └───────┬────────┘                          │
│                   │                                   │
│           ┌───────▼────────┐                          │
│           │  Repositories  │                          │
│           └───────┬────────┘                          │
│                   │                                   │
│           ┌───────▼────────┐                          │
│           │   PostgreSQL   │                          │
│           │    Database    │                          │
│           └────────────────┘                          │
│                                    │                 │
│           ┌───────────────┐                           │
│           │  WireGuard    │                           │
│           │  Outline      │                           │
│           └───────────────┘                           │
└─────────────────────────────────────────────────────────┘
```

### Layered Architecture

```
src/
├── core/
│   ├── domain/              # Business entities and enums
│   ├── application/         # Application services
│   └── ports/               # Interface definitions
├── infrastructure/
│   ├── persistence/         # Database models and repositories
│   ├── api/                 # FastAPI routes and middleware
│   └── vpn_providers/       # VPN provider integrations
└── shared/
    ├── config/              # Configuration management
    └── utils/               # Shared utilities
```

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| **Framework** | FastAPI 0.109+ |
| **Language** | Python 3.13+ |
| **Database** | PostgreSQL 15+ |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Driver** | asyncpg |
| **Migrations** | Alembic |
| **Validation** | Pydantic 2.x |
| **Auth** | PyJWT + python-jose |
| **Package Manager** | uv (astral.sh) |
| **Testing** | pytest + pytest-asyncio |
| **Linting** | ruff + mypy |
| **Caching** | Redis |
| **Container** | Docker + docker-compose |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- PostgreSQL 15+ (or Docker)
- Redis (or Docker)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/uSipipo-Team/usipipo-backend.git
cd usipipo-backend

# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python 3.13
uv python install 3.13

# Install dependencies
uv sync --dev

# Configure environment
cp example.env .env
# Edit .env with your configuration

# Run database migrations
uv run alembic upgrade head

# Start the development server
uv run python -m src
```

The API will be available at `http://localhost:8000`

---

## 📖 API Documentation

### 🌐 GitHub Wiki (Recommended)

Complete API documentation is available on our **GitHub Wiki**:

👉 **[https://github.com/uSipipo-Team/usipipo-backend/wiki](https://github.com/uSipipo-Team/usipipo-backend/wiki)**

**Wiki Pages:**
- **[Home](https://github.com/uSipipo-Team/usipipo-backend/wiki)** - Quick start guide and overview
- **[API Reference](https://github.com/uSipipo-Team/usipipo-backend/wiki/API-Reference)** - Complete endpoint reference (50+ endpoints)
- **[Authentication](https://github.com/uSipipo-Team/usipipo-backend/wiki/Authentication)** - Auth guide with code examples
- **[Error Codes](https://github.com/uSipipo-Team/usipipo-backend/wiki/Error-Codes)** - HTTP error reference

### 📄 Local Documentation

- **[docs/API.md](docs/API.md)** - Comprehensive API documentation with examples
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Architecture overview
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Deployment instructions

### 🧪 Interactive API Docs

Once the server is running, access the interactive API documentation:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## 💻 Development

### Code Quality

```bash
# Run linter
uv run ruff check .

# Fix linting issues
uv run ruff check . --fix

# Run type checker
uv run mypy .

# Run formatter
uv run ruff format .
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run all hooks manually
uv run pre-commit run --all-files
```

### Running in Development Mode

```bash
# With auto-reload
uv run uvicorn src.main:app --reload --env-file .env

# With debug logging
DEBUG=true uv run python -m src
```

---

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_vpn.py

# Run tests by marker
uv run pytest -m "not slow"
uv run pytest -m integration

# Run tests in parallel
uv run pytest -n auto
```

### Test Structure

```
tests/
├── unit/                 # Unit tests
├── integration/          # Integration tests
├── e2e/                  # End-to-end tests
└── conftest.py           # Shared fixtures
```

---

## 🐳 Docker Deployment

### Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

This starts:
- **Backend** on port 8000
- **PostgreSQL** on port 5432
- **Redis** on port 6379

### Manual Docker Build

```bash
# Build image
docker build -t usipipo-backend:latest .

# Run container
docker run -d \
  --name usipipo-backend \
  --env-file .env \
  -p 8000:8000 \
  usipipo-backend:latest
```

### Production Docker

```bash
# Build for production
docker build -t usipipo-backend:production \
  --build-arg APP_ENV=production \
  .

# Run with production settings
docker run -d \
  --name usipipo-backend-prod \
  --env-file .env.production \
  -p 8000:8000 \
  --restart unless-stopped \
  usipipo-backend:production
```

---

## 🔧 Environment Variables

Create a `.env` file based on `example.env`:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Secret key for JWT signing | - | ✅ |
| `DATABASE_URL` | PostgreSQL connection string | - | ✅ |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` | ❌ |
| `APP_ENV` | Environment (development/production) | `development` | ❌ |
| `DEBUG` | Enable debug mode | `false` | ❌ |
| `API_PREFIX` | API route prefix | `/api/v1` | ❌ |
| `TELEGRAM_TOKEN` | Telegram bot token | - | ❌ |
| `JWT_EXPIRY_HOURS` | JWT token expiry hours | `24` | ❌ |
| `WIREGUARD_SERVER` | WireGuard server endpoint | - | ❌ |
| `OUTLINE_API_URL` | Outline API endpoint | - | ❌ |

---

## 🗄️ Database Migrations

```bash
# Generate new migration
uv run alembic revision --autogenerate -m "Description"

# Apply all migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# View migration history
uv run alembic history

# Check current migration
uv run alembic current
```

---

## 📁 Project Structure

```
usipipo-backend/
├── src/
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── domain/          # Business entities and enums
│   │   ├── application/     # Application services
│   │   └── ports/           # Interface definitions
│   ├── infrastructure/
│   │   ├── api/             # FastAPI routes and middleware
│   │   ├── persistence/     # Database models and repositories
│   │   └── vpn_providers/   # VPN provider integrations
│   └── shared/
│       ├── config/          # Configuration and settings
│       └── utils/           # Shared utilities
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── migrations/
│   ├── versions/
│   └── env.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── DEVELOPMENT.md
├── deploy/
├── scripts/
├── .env
├── example.env
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Start for Contributors

```bash
# Fork the repository
git clone https://github.com/YOUR_USERNAME/usipipo-backend.git
cd usipipo-backend

# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes and run tests
uv run pytest

# Commit using conventional commits
git commit -m "feat: add your feature description"

# Push and create PR
git push origin feature/your-feature-name
```

### Code Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints for all function signatures
- Write tests for new features
- Keep functions small and focused
- Document public APIs

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

```
MIT License

Copyright (c) 2026 uSipipo Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🔗 Links

### Documentation
- **[GitHub Wiki](https://github.com/uSipipo-Team/usipipo-backend/wiki)** - Complete API documentation
- **[API Reference](https://github.com/uSipipo-Team/usipipo-backend/wiki/API-Reference)** - 50+ endpoints documented
- **[Authentication Guide](https://github.com/uSipipo-Team/usipipo-backend/wiki/Authentication)** - Auth with examples
- **[Error Codes](https://github.com/uSipipo-Team/usipipo-backend/wiki/Error-Codes)** - HTTP error reference

### Project
- **GitHub Organization:** [uSipipo-Team](https://github.com/uSipipo-Team)
- **Backend Repository:** [usipipo-backend](https://github.com/uSipipo-Team/usipipo-backend)
- **Shared Library:** [usipipo-commons](https://github.com/uSipipo-Team/usipipo-commons)
- **PyPI Package:** [usipipo-commons](https://pypi.org/project/usipipo-commons/)
- **Latest Release:** [v0.4.0](https://github.com/uSipipo-Team/usipipo-backend/releases/tag/v0.4.0)

### Services
- **Telegram Bot:** [@uSipipo_Bot](https://t.me/uSipipo_Bot)
- **Landing Page:** [usipipo.com](https://usipipo.com)

---

## 📞 Support

- **Documentation:** See [docs/](docs/) directory
- **Issues:** [GitHub Issues](https://github.com/uSipipo-Team/usipipo-backend/issues)
- **Email:** dev@usipipo.com

---

<div align="center">

**Made with ❤️ by uSipipo Team**

[Back to top](#usipipo-backend)

</div>
