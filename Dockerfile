FROM python:3.13-slim

WORKDIR /app

# Instalar uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copiar dependencias
COPY pyproject.toml uv.lock ./

# Instalar dependencias
RUN uv sync --frozen --no-dev

# Copiar código
COPY src/ ./src/

# Exponer puerto
EXPOSE 8000

# Comando
CMD ["uv", "run", "python", "-m", "src"]
