# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Pre-commit hooks for code quality (ruff, mypy, bandit, pytest)
- GitHub Actions CI/CD pipeline
- Development documentation (`docs/DEVELOPMENT.md`)

### Changed
- Updated ruff to v0.15.6 with Python 3.13 support
- Updated pre-commit hooks to latest versions

### Fixed
- Python target version corrected to 3.13
- Mypy configuration for better module handling

---

## [0.2.0] - 2026-03-19

### ✨ Added

#### Authentication
- **POST /api/v1/auth/telegram** - Telegram WebApp authentication endpoint
- JWT token generation and validation
- Telegram initData validation for secure authentication
- User auto-creation on first login

#### VPN Management
- **GET /api/v1/vpn/keys** - List user's VPN keys
- **POST /api/v1/vpn/keys** - Create new VPN key (WireGuard/Outline)
- **GET /api/v1/vpn/keys/{id}** - Get VPN key details
- **PUT /api/v1/vpn/keys/{id}** - Update VPN key
- **DELETE /api/v1/vpn/keys/{id}** - Delete/revoke VPN key
- VPN key limit enforcement (MAX_KEYS_PER_USER)

#### Architecture
- Hexagonal architecture implementation
- Domain-driven design patterns
- Repository pattern for data access
- Service layer for business logic

#### Infrastructure
- SQLAlchemy models for User and VpnKey
- Async database repositories
- Docker Compose configuration (Backend + PostgreSQL + Redis)

#### Security
- JWT-based authentication
- Telegram WebApp signature validation
- Password-less authentication flow
- Role-based access control (admin endpoints)

#### Testing
- Integration tests for auth endpoints
- Integration tests for VPN endpoints
- Pytest fixtures for test database
- Test coverage configuration (80% minimum)

#### Code Quality
- Pre-commit hooks (ruff, mypy, bandit, pytest)
- Ruff for linting and formatting
- Mypy for static type checking
- Bandit for security vulnerability scanning
- GitHub Actions CI/CD pipeline

### 🔧 Changed

#### Project Structure
```
src/
├── core/
│   ├── domain/
│   │   ├── entities/       # Domain entities (from usipipo-commons)
│   │   └── interfaces/     # Repository interfaces
│   └── application/
│       ├── services/       # Application services (business logic)
│       └── exceptions/     # Domain exceptions
├── infrastructure/
│   ├── api/v1/
│   │   ├── routes/         # API route handlers
│   │   └── deps.py         # Dependency injection
│   └── persistence/
│       ├── models/         # SQLAlchemy models
│       └── repositories/   # Repository implementations
└── shared/
    ├── security/           # JWT, Telegram auth
    ├── schemas/            # Pydantic schemas
    └── config.py           # Application settings
```

#### Dependencies
- Added `pyjwt>=2.8.0` for JWT handling
- Added `python-jose[cryptography]>=3.3.0` for cryptographic operations
- Added `aiosqlite>=0.20.0` for SQLite support in tests
- Added `pre-commit>=3.6.0` for git hooks
- Added `bandit>=1.7.0` for security scanning

#### Configuration
- Updated `pyproject.toml` with ruff, pytest, mypy, coverage settings
- Added `mypy.ini` for type checking configuration
- Added `.pre-commit-config.yaml` for git hooks
- Added `.github/workflows/ci.yml` for CI/CD

### 📦 Infrastructure

#### Docker
- `docker-compose.yml` for local development
- Multi-service setup (Backend, PostgreSQL, Redis)
- Health checks for all services
- Volume persistence for databases

#### CI/CD
- Automated linting on every push
- Automated testing with coverage reporting
- Type checking with mypy
- Security scanning with bandit
- Docker image building

### 📝 Documentation

- `docs/DEVELOPMENT.md` - Development guidelines
- `docs/ARCHITECTURE.md` - Architecture overview
- `docs/API.md` - API documentation
- `docs/DEPLOYMENT.md` - Deployment instructions
- `CHANGELOG.md` - This changelog

### 🧪 Testing

- Integration tests for authentication flow
- Integration tests for VPN CRUD operations
- Test fixtures for database isolation
- Coverage reporting (target: 80%)
- Pytest configuration with markers (slow, integration)

### 🔒 Security

- JWT secret key configuration via environment variables
- Telegram Bot Token validation
- HTTPS-only token transmission
- Secure password-less authentication
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy ORM

### 🐛 Fixed

- Python version compatibility (3.13)
- Ruff configuration for latest version
- Mypy module detection issues
- Pre-commit hook performance

---

## [0.1.0] - 2026-03-18

### Added
- Initial project structure
- Base FastAPI application
- Basic health check endpoint
- README.md with project information
- Dockerfile for containerization
- Example environment configuration

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.2.0 | 2026-03-19 | Auth + VPN endpoints + Pre-commit/CI |
| 0.1.0 | 2026-03-18 | Initial project structure |

---

## Upcoming (v0.3.0)

Planned for next release:

- [ ] Payment integration (Stripe/PayPal)
- [ ] Webhook handlers for payment events
- [ ] Subscription management
- [ ] Invoice generation
- [ ] Usage tracking and billing
- [ ] Admin dashboard endpoints

---

[Unreleased]: https://github.com/uSipipo-Team/usipipo-backend/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/uSipipo-Team/usipipo-backend/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/uSipipo-Team/usipipo-backend/releases/tag/v0.1.0
