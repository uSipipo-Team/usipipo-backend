# Development Guidelines

## Pre-commit Hooks

Este proyecto utiliza **pre-commit** para mantener la calidad del código. Los hooks se ejecutan automáticamente antes de cada commit.

### Instalación

```bash
# Instalar dependencias de desarrollo
uv sync --dev

# Instalar pre-commit hooks
uv run pre-commit install
```

### Hooks Configurados

| Hook | Propósito |
|------|-----------|
| **ruff check** | Linting (errores, bugs, code smells) |
| **ruff format** | Formatting automático |
| **mypy** | Type checking (solo `src/`, no tests) |
| **pytest** | Tests unitarios rápidos (excluye integration/slows) |
| **trailing-whitespace** | Elimina espacios al final de líneas |
| **end-of-file-fixer** | Asegura newline al final de archivos |
| **check-yaml** | Valida sintaxis YAML |
| **check-json** | Valida sintaxis JSON |
| **check-toml** | Valida sintaxis TOML |
| **check-merge-conflict** | Detecta conflictos de merge no resueltos |
| **detect-private-key** | Detecta claves privadas accidentalmente commitadas |

### Ejecutar Manualmente

```bash
# Ejecutar todos los hooks
uv run pre-commit run --all-files

# Ejecutar un hook específico
uv run pre-commit run ruff --all-files
uv run pre-commit run mypy --all-files
```

### Saltar Hooks (Solo Emergencias)

```bash
# Commit sin hooks (NO recomendado)
git commit --no-verify -m "urgent fix"

# Para un hook específico
SKIP=mypy git commit -m "WIP"
```

---

## Testing

### Ejecutar Tests

```bash
# Todos los tests
uv run pytest

# Solo tests unitarios (rápidos)
uv run pytest -m "not integration and not slow"

# Solo tests de integración
uv run pytest -m integration

# Con coverage
uv run pytest --cov=src --cov-report=html

# Ver coverage en browser
open htmlcov/index.html
```

### Coverage Mínimo

El proyecto requiere **mínimo 80%** de coverage. El CI fallará si no se alcanza.

---

## Type Checking

```bash
# Ejecutar mypy
uv run mypy src/

# Con configuración estricta
uv run mypy src/ --strict
```

### Ignorar Type Errors

```python
# Solo usar cuando sea absolutamente necesario
result = some_function()  # type: ignore[return-value]
```

---

## Linting & Formatting

```bash
# Linting
uv run ruff check src/ tests/

# Auto-fix
uv run ruff check src/ tests/ --fix

# Formatting
uv run ruff format src/ tests/

# Check format (sin modificar)
uv run ruff format src/ tests/ --check
```

---

## CI/CD

El pipeline de GitHub Actions ejecuta:

1. **Lint** - Ruff check + format
2. **Test** - Pytest con coverage (mín 80%)
3. **Type Check** - Mypy estricto
4. **Security** - Bandit security scan
5. **Build** - Docker image build

### Requerimientos para Merge

- ✅ Todos los jobs de CI deben pasar
- ✅ Coverage ≥ 80%
- ✅ Sin errores de tipo
- ✅ Sin problemas de seguridad críticos

---

## Comandos Útiles

```bash
# Sync dependencies
uv sync --dev

# Update lock file
uv lock

# List outdated
uv pip list --outdated

# Clean bytecode
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete

# Run anything in venv
uv run <command>
```
