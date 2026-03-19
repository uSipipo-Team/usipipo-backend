# API Documentation

## Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

### Root

```http
GET /
```

**Response:**
```json
{
  "message": "Welcome to uSipipo Backend API"
}
```

## API v1

Los endpoints de la API v1 estarán disponibles bajo el prefijo `/api/v1`.

### Planned Endpoints

- `POST /api/v1/users` - Crear usuario
- `GET /api/v1/users/{id}` - Obtener usuario
- `POST /api/v1/vpn-keys` - Crear clave VPN
- `GET /api/v1/vpn-keys/{id}` - Obtener clave VPN
- `POST /api/v1/payments` - Registrar pago
- `GET /api/v1/payments/{id}` - Obtener pago
