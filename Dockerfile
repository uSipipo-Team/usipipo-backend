# Multi-stage Dockerfile for production optimization
FROM python:3.13-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install uv package manager
FROM base AS uv-installer
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Development stage with all dependencies
FROM uv-installer AS dev
COPY pyproject.toml uv.lock ./
RUN uv sync --dev
COPY . .

# Production stage with minimal dependencies
FROM base AS production
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install runtime dependencies only
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY src/ ./src/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=5)" || exit 1

# Run application
CMD ["uv", "run", "python", "-m", "src"]
