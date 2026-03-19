# usipipo-backend

> Backend API principal del ecosistema uSipipo

## Estado

- [x] En desarrollo
- [ ] Alpha
- [ ] Beta
- [ ] Producción

## Documentación

- [Architecture](docs/ARCHITECTURE.md)
- [API](docs/API.md)
- [Deployment](docs/DEPLOYMENT.md)

## Desarrollo

```bash
# Clonar
git clone https://github.com/uSipipo-Team/usipipo-backend.git
cd usipipo-backend

# Instalar dependencias
uv sync --dev

# Configurar entorno
cp example.env .env

# Ejecutar tests
uv run pytest

# Ejecutar servicio
uv run python -m src
```

## Docker

```bash
# Build
docker build -t usipipo-backend .

# Ejecutar
docker run --env-file .env usipipo-backend
```

## License

MIT © uSipipo
