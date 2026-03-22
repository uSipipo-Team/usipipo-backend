# Contributing to uSipipo Backend

Thank you for your interest in contributing to uSipipo Backend! This document provides guidelines and instructions for contributing to this project.

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Development Workflow](#-development-workflow)
- [Commit Guidelines](#-commit-guidelines)
- [Pull Request Process](#-pull-request-process)
- [Coding Standards](#-coding-standards)
- [Testing Requirements](#-testing-requirements)
- [Documentation](#-documentation)

---

## 🤝 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Keep discussions professional and on-topic

---

## 🚀 Getting Started

### 1. Fork the Repository

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/usipipo-backend.git
cd usipipo-backend

# Add upstream remote
git remote add upstream https://github.com/uSipipo-Team/usipipo-backend.git
```

### 2. Set Up Development Environment

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python 3.13
uv python install 3.13

# Install dependencies
uv sync --dev

# Configure environment
cp example.env .env
# Edit .env with your configuration

# Install pre-commit hooks
uv run pre-commit install
```

### 3. Create a Branch

```bash
# Always branch from main
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

---

## 💻 Development Workflow

### Making Changes

1. **Make your changes** following the coding standards
2. **Run tests** to ensure nothing is broken
3. **Run linters** to ensure code quality
4. **Update documentation** if needed
5. **Commit** using conventional commits

### Quality Checks

```bash
# Run all checks
uv run pre-commit run --all-files

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run linter
uv run ruff check .

# Run type checker
uv run mypy .

# Run formatter check
uv run ruff format --check .
```

---

## 📝 Commit Guidelines

### Conventional Commits

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, semicolons, etc.)
- `refactor`: Code refactoring without feature change
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependencies

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

### Commit Message Guidelines

- Use imperative mood in the subject line ("add" not "added")
- Limit subject line to 50 characters
- Capitalize the subject line
- Do not end the subject line with a period
- Separate subject from body with a blank line
- Use the body to explain **what** and **why**, not **how**
- Wrap body at 72 characters

---

## 🔀 Pull Request Process

### Before Submitting

1. **Update your branch** with latest main:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all quality checks**:
   ```bash
   uv run pre-commit run --all-files
   uv run pytest --cov=src
   ```

3. **Ensure tests pass** with good coverage (>80%)

4. **Update documentation** if you changed functionality

5. **Squash commits** if needed:
   ```bash
   git rebase -i upstream/main
   ```

### PR Template

When creating a PR, please include:

- **Title**: Clear and descriptive (following conventional commits)
- **Description**: What changes and why
- **Related Issues**: Link to any related issues
- **Testing Done**: How you tested the changes
- **Screenshots**: If UI changes (for API responses if relevant)
- **Breaking Changes**: Note any breaking changes

### Review Process

1. **CI checks must pass** (tests, linting, type checking)
2. **At least one approval** from a maintainer
3. **Address all review comments**
4. **Resolve conversations** after addressing them
5. **Maintainer will merge** when ready

---

## 📏 Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use [ruff](https://github.com/astral-sh/ruff) for linting
- Use [mypy](https://mypy-lang.org/) for type checking
- Line length: 100 characters
- Use double quotes for strings
- Use 4 spaces for indentation

### Type Hints

**All public functions must have type hints:**

```python
# ✅ Good
def create_user(user_id: int, username: str) -> User:
    """Create a new user."""
    return User(id=user_id, username=username)

# ❌ Bad
def create_user(user_id, username):
    return User(id=user_id, username=username)
```

### Documentation

**Use docstrings for all public functions, classes, and modules:**

```python
def calculate_vpn_cost(hours: float, vpn_type: VpnType) -> float:
    """
    Calculate the cost of VPN usage based on hours and type.

    Args:
        hours: Number of hours of VPN usage
        vpn_type: Type of VPN (WireGuard or Outline)

    Returns:
        Total cost in USD

    Raises:
        ValueError: If hours is negative
    """
    if hours < 0:
        raise ValueError("Hours cannot be negative")

    rate = WIREGUARD_RATE if vpn_type == VpnType.WIREGUARD else OUTLINE_RATE
    return hours * rate
```

### Error Handling

**Use specific exceptions and provide context:**

```python
# ✅ Good
try:
    await db.execute(query, params)
except DatabaseError as e:
    logger.error(f"Database error: {e}", extra={"query": query})
    raise DatabaseConnectionError(f"Failed to execute query: {e}") from e

# ❌ Bad
try:
    await db.execute(query, params)
except Exception:
    raise Exception("Error")
```

### Naming Conventions

```python
# Classes: PascalCase
class VpnKeyManager: ...

# Functions and variables: snake_case
def create_vpn_key(): ...
user_id = 123

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATtempts = 3
JWT_SECRET_KEY = "..."

# Private methods/variables: _prefix
_internal_cache = {}
def _helper_function(): ...
```

---

## 🧪 Testing Requirements

### Test Structure

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

### Test Coverage

- **Minimum coverage**: 80%
- **Critical paths**: 100% (auth, payments, VPN key generation)
- **Test categories**:
  - Unit tests for business logic
  - Integration tests for database and external services
  - End-to-end tests for critical workflows

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=html

# Specific test file
uv run pytest tests/unit/test_user.py

# Specific test function
uv run pytest tests/unit/test_user.py::test_create_user

# With markers
uv run pytest -m "not slow"
uv run pytest -m integration
```

---

## 📚 Documentation

### Code Documentation

- **Docstrings**: All public APIs must have docstrings
- **Type hints**: All functions must have type hints
- **Comments**: Explain **why**, not **what**

### Documentation Files

Update relevant documentation in `docs/` directory:

- `docs/ARCHITECTURE.md`: Architecture decisions
- `docs/API.md`: API endpoint documentation
- `docs/DEPLOYMENT.md`: Deployment instructions
- `docs/DEVELOPMENT.md`: Development guidelines

### README Updates

Update `README.md` if you:

- Add new features
- Change environment variables
- Modify API endpoints
- Add new dependencies

---

## 🎯 Areas Needing Contribution

### Good First Issues

Look for issues labeled:
- `good first issue`
- `help wanted`
- `beginner-friendly`

### Priority Areas

- **Tests**: Increase test coverage
- **Documentation**: Improve API docs and examples
- **Performance**: Optimize database queries
- **Error Handling**: Improve error messages and recovery
- **Monitoring**: Add metrics and logging

---

## 📞 Getting Help

- **Documentation**: Check [docs/](docs/) directory
- **Existing Issues**: Search [GitHub Issues](https://github.com/uSipipo-Team/usipipo-backend/issues)
- **Discussions**: Use [GitHub Discussions](https://github.com/uSipipo-Team/usipipo-backend/discussions)
- **Email**: dev@usipipo.com

---

## 🙏 Thank You

Every contribution, no matter how small, helps make uSipipo better!

<div align="center">

**Made with ❤️ by uSipipo Team**

[Back to top](#contributing-to-usipipo-backend)

</div>
