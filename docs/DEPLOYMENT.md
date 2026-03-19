# Deployment

## Local Development

```bash
# Clonar repositorio
git clone https://github.com/uSipipo-Team/usipipo-backend.git
cd usipipo-backend

# Instalar dependencias
uv sync --dev

# Configurar entorno
cp example.env .env
# Editar .env con las credenciales locales

# Ejecutar
uv run python -m src
```

## Docker

```bash
# Build
docker build -t usipipo-backend .

# Ejecutar
docker run --env-file .env -p 8000:8000 usipipo-backend
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Secret key for JWT | Required |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `APP_ENV` | Environment (development/production) | development |
| `DEBUG` | Enable debug mode | false |
| `API_PREFIX` | API prefix | /api/v1 |

## Production Deployment

TBD
