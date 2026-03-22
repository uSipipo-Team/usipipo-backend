# 🤖 AI Agent Instructions - uSipipo Backend

> **Guide for AI agents working on the uSipipo Backend API**

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Project Overview](#-project-overview)
- [Architecture](#-architecture)
- [Development Workflow](#-development-workflow)
- [Code Quality Rules](#-code-quality-rules)
- [Testing Guidelines](#-testing-guidelines)
- [Git & Commits](#-git--commits)
- [Common Tasks](#-common-tasks)
- [Troubleshooting](#-troubleshooting)
- [Resources](#-resources)

---

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/uSipipo-Team/usipipo-backend.git
cd usipipo-backend

# 2. Install dependencies (uv package manager)
uv sync --dev

# 3. Configure environment
cp example.env .env
# Edit .env with your configuration

# 4. Run database migrations
uv run alembic upgrade head

# 5. Run tests (verify setup)
uv run pytest

# 6. Start development server
uv run python -m src
```

**API available at:** `http://localhost:8000`

---

## 🌐 Project Overview

**uSipipo Backend** is a FastAPI application serving as the core API for the uSipipo VPN ecosystem targeting the LATAM community.

### Key Features

| Feature | Status | Description |
|---------|--------|-------------|
| **Authentication** | ✅ | JWT-based auth with role management |
| **VPN Management** | ✅ | WireGuard + Outline key lifecycle |
| **Payments** | ✅ | Crypto + Telegram Stars integration |
| **Subscriptions** | ✅ | Tiered plans with auto-renewal |
| **Consumption Billing** | 🟡 | Usage-based billing |
| **Referrals** | ✅ | Bonus tracking system |
| **Support Tickets** | ✅ | Customer support system |
| **Wallet** | ✅ | Balance & transactions |

### Ecosystem Context

```
┌──────────────┐     ┌──────────────┐
│  Telegram    │     │   Mini App   │
│     Bot      │     │    (Web)     │
└──────┬───────┘     └──────┬───────┘
       │                   │
       └────────┬──────────┘
                ▼
       ┌────────────────┐
       │  THIS BACKEND  │
       │   (FastAPI)    │
       └───────┬────────┘
               │
       ┌───────▼────────┐
       │  PostgreSQL    │
       │   Database     │
       └────────────────┘
```

### Related Repositories

- **usipipo-commons**: Shared library (PyPI) - `from usipipo_commons import ...`
- **usipipo-telegram-bot**: Telegram bot client
- **usipipo-miniapp-web**: Telegram Mini App (Flask)
- **usipipo-landing**: Marketing site
- **usipipo-vpn-android**: Android VPN app (Flutter)

---

## 🏗️ Architecture

### Project Structure

```
src/
├── __init__.py
├── __main__.py
├── main.py              # FastAPI app entry point
├── core/
│   ├── domain/          # Business entities (from commons)
│   ├── application/     # Application services
│   └── ports/           # Interface definitions
├── infrastructure/
│   ├── api/             # FastAPI routes + middleware
│   ├── persistence/     # SQLAlchemy models + repos
│   └── vpn_providers/   # WireGuard + Outline clients
└── shared/
    ├── config/          # Settings (pydantic-settings)
    └── utils/           # Shared utilities

tests/
├── unit/                # Unit tests
├── integration/         # Integration tests
└── conftest.py          # Fixtures

migrations/
├── versions/            # Alembic migrations
└── env.py
```

### Tech Stack

| Category | Technology |
|----------|------------|
| **Framework** | FastAPI 0.109+ |
| **Language** | Python 3.13+ |
| **Database** | PostgreSQL 15+ (asyncpg + SQLAlchemy 2.0) |
| **Migrations** | Alembic |
| **Validation** | Pydantic 2.x |
| **Auth** | PyJWT + python-jose |
| **Package Manager** | uv (astral.sh) |
| **Testing** | pytest + pytest-asyncio |
| **Linting** | ruff + mypy |
| **Caching** | Redis |
| **Container** | Docker + docker-compose |

---

## 💻 Development Workflow

### 1. Before Coding

```bash
# Ensure you're on main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name
```

### 2. During Development

```bash
# Run linter (auto-fix)
uv run ruff check . --fix

# Run formatter
uv run ruff format .

# Run type checker
uv run mypy .

# Run tests
uv run pytest
```

### 3. Before Commit

```bash
# Run all pre-commit hooks
uv run pre-commit run --all-files

# Verify tests pass
uv run pytest --cov=src

# Check coverage (>80% required)
uv run pytest --cov=src --cov-report=term-missing
```

### 4. Environment Setup

**Required environment variables in `.env`:**

```bash
# Required
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/usipipo

# Optional (defaults provided)
APP_ENV=development
DEBUG=true
API_PREFIX=/api/v1
REDIS_URL=redis://localhost:6379/0
```

---

## 📏 Code Quality Rules

### The 7 Rules (Linus Torvalds Inspired)

| # | Rule | Principle |
|---|------|-----------|
| 01 | **KISS Principle** | Keep it simple, stupid |
| 02 | **Delete Code Fearlessly** | Remove useless code |
| 03 | **Code Not Comments** | Self-explanatory code |
| 04 | **Atomic Commits** | One purpose per commit |
| 05 | **Explain Simply** | 30-second explanation test |
| 06 | **Make It Work First** | Function before optimization |
| 07 | **Small Commits** | <200 lines per commit |

### Pre-Commit Checklist

Before each commit, verify:

```
□ Regla 01: Is this the simplest solution?
□ Regla 02: Is there dead code to remove?
□ Regla 03: Is the code self-explanatory?
□ Regla 04: Does the commit have one purpose?
□ Regla 05: Can you explain it in 30 seconds?
□ Regla 06: Does it work first (no premature optimization)?
□ Regla 07: Is the commit <200 lines?
```

### Code Style

```python
# ✅ GOOD: Type hints, docstring, simple
from usipipo_commons.domain.entities import User


async def create_user(
    user_id: int,
    username: str,
    telegram_id: str,
) -> User:
    """
    Create a new user with the given information.

    Args:
        user_id: Unique user identifier
        username: User's chosen username
        telegram_id: Telegram user ID

    Returns:
        Created User entity

    Raises:
        ValueError: If telegram_id is invalid
    """
    if not telegram_id.startswith("tg_"):
        raise ValueError("Invalid Telegram ID format")

    return User(id=user_id, username=username, telegram_id=telegram_id)


# ❌ BAD: No type hints, no docstring, complex
def create_user(user_id, username, telegram_id):
    # Check if telegram id is valid
    if not telegram_id.startswith("tg_"):
        raise Exception("Invalid")  # What is invalid?
    user = User(id=user_id, username=username, telegram_id=telegram_id)
    return user
```

### Naming Conventions

```python
# Classes: PascalCase
class VpnKeyManager: ...

# Functions/variables: snake_case
def create_vpn_key(): ...
user_id = 123

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
JWT_SECRET_KEY = "..."

# Private: _prefix
_internal_cache = {}
def _helper_function(): ...
```

### Error Handling

```python
# ✅ GOOD: Specific exceptions with context
try:
    await db.execute(query, params)
except DatabaseError as e:
    logger.error(f"Database error: {e}", extra={"query": query})
    raise DatabaseConnectionError(f"Failed to execute query: {e}") from e

# ❌ BAD: Generic exceptions
try:
    await db.execute(query, params)
except Exception:
    raise Exception("Error")
```

---

## 🧪 Testing Guidelines

### Test Structure (AAA Pattern)

```python
import pytest
from src.core.domain.entities import User


class TestUserCreation:
    """Test user creation functionality."""

    def test_create_user_with_valid_data(self):
        """Should create user with valid data."""
        # Arrange
        user_id = 123
        username = "test_user"

        # Act
        user = User(id=user_id, username=username)

        # Assert
        assert user.id == user_id
        assert user.username == username
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_create_user_in_database(self, async_session):
        """Should persist user to database."""
        # Arrange
        user = User(id=123, username="test_user")

        # Act
        async_session.add(user)
        await async_session.commit()

        # Assert
        result = await async_session.get(User, 123)
        assert result is not None
        assert result.username == "test_user"
```

### Test Naming Convention

```python
# Pattern: test_<method>_<scenario>_<expected>
def test_create_user_with_valid_data_returns_user(): ...
def test_create_user_with_duplicate_email_raises_error(): ...
def test_deactivate_user_when_already_inactive_returns_false(): ...
```

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=html

# Specific file
uv run pytest tests/unit/test_user.py

# Specific function
uv run pytest tests/unit/test_user.py::test_create_user

# By marker
uv run pytest -m "not slow"
uv run pytest -m integration

# Parallel execution
uv run pytest -n auto
```

### Coverage Requirements

- **Minimum**: 80%
- **Critical paths**: 100% (auth, payments, VPN keys)
- **Test types**:
  - Unit tests for business logic
  - Integration tests for database/external services
  - E2E tests for critical workflows

---

## 📝 Git & Commits

### Conventional Commits

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style (formatting, semicolons) |
| `refactor` | Code refactoring (no feature change) |
| `perf` | Performance improvements |
| `test` | Adding/updating tests |
| `chore` | Maintenance tasks, dependencies |

### Examples

```bash
# Feature
git commit -m "feat(auth): add JWT token refresh endpoint"

# Bug fix
git commit -m "fix(vpn): resolve WireGuard key generation race condition"

# Documentation
git commit -m "docs: update API documentation with new endpoints"

# Refactor
git commit -m "refactor(billing): simplify invoice calculation logic"

# Test
git commit -m "test(subscriptions): add unit tests for plan activation"
```

### Commit Message Rules

- ✅ Use imperative mood ("add" not "added")
- ✅ Limit subject to 50 characters
- ✅ Capitalize subject line
- ✅ No period at end of subject
- ✅ Blank line between subject and body
- ✅ Explain **what** and **why**, not **how**

### Branch Naming

```bash
# Feature branches
feature/add-payment-method
feature/user-profile-page

# Bug fixes
fix/login-error-handling
fix/vpn-key-expiry

# Releases
release/v0.3.0
release/v0.3.1-hotfix
```

---

## 🔧 Common Tasks

### Add New API Endpoint

```python
# 1. Create route file: src/infrastructure/api/v1/routes/your_feature.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...deps.database import get_db
from ...services.your_service import YourService

router = APIRouter(prefix="/your-feature", tags=["Your Feature"])


@router.get("/{item_id}")
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Get item by ID."""
    service = YourService(db)
    item = await service.get_by_id(item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


# 2. Register in main.py
app.include_router(router, prefix=settings.API_PREFIX)
```

### Create Database Model

```python
# src/infrastructure/persistence/models/your_model.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func

from .base import Base


class YourModel(Base):
    """Your model description."""

    __tablename__ = "your_table"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Create Migration

```bash
# Generate migration
uv run alembic revision --autogenerate -m "Add your_table"

# Review migration file in migrations/versions/

# Apply migration
uv run alembic upgrade head

# Verify
uv run alembic current
```

### Add New Dependency

```bash
# Add to project
uv add package-name

# Add dev dependency
uv add --dev package-name

# Update lock file
uv sync
```

### Use usipipo-commons

```python
# Import entities
from usipipo_commons.domain.entities import User, VpnKey, Payment
from usipipo_commons.schemas import CreateVpnKeyRequest
from usipipo_commons.enums import VpnType, KeyStatus
from usipipo_commons.constants import FREE_GB, REFERRAL_BONUS_GB
from usipipo_commons.utils import validate_telegram_id, format_bytes
```

---

## 🐛 Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps

# Verify connection string in .env
echo $DATABASE_URL

# Test connection
uv run python -c "from src.infrastructure.persistence.database import engine; print('OK')"
```

### Migration Issues

```bash
# Check current migration
uv run alembic current

# View migration history
uv run alembic history

# Rollback one migration
uv run alembic downgrade -1

# Fix: Clear and reapply (DEV ONLY)
uv run alembic downgrade base
uv run alembic upgrade head
```

### Test Failures

```bash
# Run specific failing test
uv run pytest tests/path/to/test.py -v

# Run with more info
uv run pytest -vvv --tb=long

# Run without cache
uv run pytest --cache-clear
```

### Import Errors

```bash
# Ensure dependencies are installed
uv sync --dev

# Check Python version
python --version  # Should be 3.13+

# Clear cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete
```

### Docker Issues

```bash
# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# View logs
docker-compose logs -f backend

# Access container
docker-compose exec backend bash
```

---

## 📚 Resources

### Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Contributing Guide](CONTRIBUTING.md)

### Code Quality Rules

- [01 - KISS Principle](.github/CODE_QUALITY_RULES/01-kiss-principle.md)
- [02 - Delete Code Fearlessly](.github/CODE_QUALITY_RULES/02-delete-code-fearlessly.md)
- [03 - Code Not Comments](.github/CODE_QUALITY_RULES/03-code-not-comments.md)
- [04 - Atomic Commits](.github/CODE_QUALITY_RULES/04-atomic-commits.md)
- [05 - Explain Simply](.github/CODE_QUALITY_RULES/05-explain-simply.md)
- [06 - Make It Work First](.github/CODE_QUALITY_RULES/06-make-it-work-first.md)
- [07 - Small Commits](.github/CODE_QUALITY_RULES/07-small-commits.md)

### External References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [Pydantic 2.x](https://docs.pydantic.dev/latest/)
- [pytest](https://docs.pytest.org/)
- [ruff](https://docs.astral.sh/ruff/)
- [uv](https://docs.astral.sh/uv/)

### uSipipo Links

- **GitHub Organization**: [uSipipo-Team](https://github.com/uSipipo-Team)
- **Shared Library**: [usipipo-commons](https://github.com/uSipipo-Team/usipipo-commons)
- **PyPI Package**: [usipipo-commons](https://pypi.org/project/usipipo-commons/)
- **Telegram Bot**: [@uSipipo_Bot](https://t.me/uSipipo_Bot)
- **Landing Page**: [usipipo.com](https://usipipo.com)

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/uSipipo-Team/usipipo-backend/issues)
- **Discussions**: [GitHub Discussions](https://github.com/uSipipo-Team/usipipo-backend/discussions)
- **Email**: dev@usipipo.com

---

<div align="center">

**Made with ❤️ by uSipipo Team**

*Last updated: 2026-03-21*

</div>
