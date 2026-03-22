# uSipipo Backend API Documentation

Documentación completa de todos los endpoints de la API del backend uSipipo.

**Base URL:** `http://localhost:8001`

**API Version:** `v1`

**Autenticación:** La mayoría de endpoints requieren autenticación JWT via header `Authorization: Bearer <token>`

---

## Tabla de Contenidos

1. [Health & Root](#health--root)
2. [Authentication](#authentication)
3. [VPN Keys](#vpn-keys)
4. [Subscriptions](#subscriptions)
5. [Payments](#payments)
6. [Referrals](#referrals)
7. [Data Packages](#data-packages)
8. [Wallets](#wallets)
9. [Tickets](#tickets)
10. [Billing](#billing)
11. [Consumption Invoices](#consumption-invoices)
12. [Admin](#admin)

---

## Health & Root

### GET /health

Verifica el estado del servidor.

**Auth:** No requerida

**Response:**
```json
{
  "status": "healthy"
}
```

---

### GET /

Información básica de la API.

**Auth:** No requerida

**Response:**
```json
{
  "message": "Welcome to uSipipo Backend API",
  "docs": "/docs",
  "health": "/health"
}
```

---

## Authentication

### POST /api/v1/auth/telegram

Autentica usuario con Telegram WebApp initData y retorna JWT token.

**Auth:** No requerida

**Request:**
```json
{
  "init_data": "user=%7B%22id%22%3A...&auth_date=...&hash=..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user_id": "369a4d7f-e8ef-4d81-84f1-483363f81d00"
}
```

**Errors:**
- `401` - Invalid Telegram initData

---

## VPN Keys

### GET /api/v1/vpn/keys

Lista todas las claves VPN del usuario autenticado.

**Auth:** Requerida

**Response:** `200 OK`
```json
[
  {
    "id": "e5a748a6-a04a-4cb9-a929-70cf8a487c28",
    "user_id": "369a4d7f-e8ef-4d81-84f1-483363f81d00",
    "name": "My VPN Key",
    "key_type": "wireguard",
    "status": "active",
    "config": "[Interface]...",
    "created_at": "2026-03-22T02:16:03.281396Z",
    "expires_at": "2026-04-21T02:16:03.281396Z",
    "last_used_at": null,
    "data_used_gb": 0.0,
    "data_limit_gb": 5.0,
    "vpn_type": "wireguard"
  }
]
```

---

### POST /api/v1/vpn/keys

Crea una nueva clave VPN.

**Auth:** Requerida

**Request:**
```json
{
  "name": "My VPN Key",
  "vpn_type": "wireguard",
  "data_limit_gb": 5
}
```

**Response:** `201 Created`
```json
{
  "id": "88f97191-91e3-40c1-a213-8bb43861af4e",
  "user_id": "369a4d7f-e8ef-4d81-84f1-483363f81d00",
  "name": "My VPN Key",
  "key_type": "wireguard",
  "status": "active",
  "config": "[Interface]...",
  "created_at": "2026-03-22T02:16:03.281396Z",
  "expires_at": "2026-04-21T02:16:03.281396Z",
  "last_used_at": null,
  "data_used_gb": 0.0,
  "data_limit_gb": 5.0,
  "vpn_type": "wireguard"
}
```

**Errors:**
- `400` - Error en la creación
- `500` - Error interno del servidor

---

### GET /api/v1/vpn/keys/{key_id}

Obtiene detalles de una clave VPN específica.

**Auth:** Requerida

**Response:** `200 OK`
```json
{
  "id": "88f97191-91e3-40c1-a213-8bb43861af4e",
  "user_id": "369a4d7f-e8ef-4d81-84f1-483363f81d00",
  "name": "My VPN Key",
  "key_type": "wireguard",
  "status": "active",
  "config": "[Interface]...",
  "created_at": "2026-03-22T02:16:03.281396Z",
  "expires_at": "2026-04-21T02:16:03.281396Z",
  "last_used_at": null,
  "data_used_gb": 0.0,
  "data_limit_gb": 5.0,
  "vpn_type": "wireguard"
}
```

**Errors:**
- `404` - Key not found
- `403` - Not authorized to access this key

---

### PUT /api/v1/vpn/keys/{key_id}

Actualiza una clave VPN.

**Auth:** Requerida

**Request:**
```json
{
  "name": "Updated Name",
  "data_limit_gb": 10
}
```

**Response:** `200 OK`
```json
{
  "id": "88f97191-91e3-40c1-a213-8bb43861af4e",
  "user_id": "369a4d7f-e8ef-4d81-84f1-483363f81d00",
  "name": "Updated Name",
  "key_type": "wireguard",
  "status": "active",
  "config": "[Interface]...",
  "created_at": "2026-03-22T02:16:03.281396Z",
  "expires_at": "2026-04-21T02:16:03.281396Z",
  "last_used_at": null,
  "data_used_gb": 0.0,
  "data_limit_gb": 10.0,
  "vpn_type": "wireguard"
}
```

**Errors:**
- `404` - Key not found
- `403` - Not authorized to update this key

---

### DELETE /api/v1/vpn/keys/{key_id}

Elimina una clave VPN.

**Auth:** Requerida

**Response:** `204 No Content`

**Errors:**
- `404` - Key not found
- `403` - Not authorized to delete this key

---

## Subscriptions

### GET /api/v1/subscriptions/plans

Lista todos los planes de suscripción disponibles.

**Auth:** No requerida (endpoint público)

**Response:** `200 OK`
```json
[
  {
    "name": "1 Month",
    "plan_type": "monthly",
    "duration_months": 1,
    "stars": 360,
    "usdt": 7.2,
    "data_limit": 10,
    "bonus_percent": 0
  },
  {
    "name": "3 Months",
    "plan_type": "quarterly",
    "duration_months": 3,
    "stars": 960,
    "usdt": 19.2,
    "data_limit": 30,
    "bonus_percent": 10
  },
  {
    "name": "6 Months",
    "plan_type": "semiannual",
    "duration_months": 6,
    "stars": 1560,
    "usdt": 31.2,
    "data_limit": 60,
    "bonus_percent": 20
  }
]
```

---

### POST /api/v1/subscriptions/activate

Activa una nueva suscripción para el usuario autenticado.

**Auth:** Requerida

**Request:**
```json
{
  "plan_type": "monthly",
  "payment_id": "payment-uuid-here"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "subscription_id": "subscription-uuid",
  "plan_type": "monthly",
  "expires_at": "2026-04-21T02:16:03.281396Z",
  "message": "Subscription activated: monthly"
}
```

**Errors:**
- `400` - Error en la activación

---

### GET /api/v1/subscriptions/me

Obtiene la suscripción actual del usuario autenticado.

**Auth:** Requerida

**Response:** `200 OK` o `null`
```json
{
  "id": "subscription-uuid",
  "user_id": 1058749165,
  "plan_type": "monthly",
  "stars_paid": 360,
  "payment_id": "payment-uuid",
  "starts_at": "2026-03-22T02:16:03.281396Z",
  "expires_at": "2026-04-21T02:16:03.281396Z",
  "is_active": true,
  "created_at": "2026-03-22T02:16:03.281396Z",
  "updated_at": "2026-03-22T02:16:03.281396Z",
  "days_remaining": 30,
  "is_expiring_soon": false,
  "is_expired": false
}
```

---

## Payments

### POST /api/v1/payments/crypto

Crea un pago con criptomonedas (USDT).

**Auth:** Requerida

**Request:**
```json
{
  "amount_usd": 10.0,
  "gb_purchased": 50,
  "network": "BSC"
}
```

**Response:** `201 Created`
```json
{
  "id": "payment-uuid",
  "user_id": "user-uuid",
  "amount_usd": 10.0,
  "gb_purchased": 50,
  "method": "crypto_usdt",
  "status": "pending",
  "crypto_address": "0x...",
  "crypto_network": "BSC",
  "expires_at": "2026-03-22T03:16:03.281396Z",
  "created_at": "2026-03-22T02:16:03.281396Z"
}
```

**Errors:**
- `400` - Invalid payment request
- `500` - Failed to create payment

---

### POST /api/v1/payments/stars

Crea un pago con Telegram Stars.

**Auth:** Requerida

**Request:**
```json
{
  "amount_usd": 10.0,
  "gb_purchased": 50
}
```

**Response:** `201 Created`
```json
{
  "id": "payment-uuid",
  "user_id": "user-uuid",
  "amount_usd": 10.0,
  "gb_purchased": 50,
  "method": "telegram_stars",
  "status": "pending",
  "telegram_star_invoice_id": "invoice_link",
  "expires_at": "2026-03-22T02:31:03.281396Z",
  "created_at": "2026-03-22T02:16:03.281396Z"
}
```

---

### GET /api/v1/payments/history

Obtiene el historial de pagos del usuario.

**Auth:** Requerida

**Response:** `200 OK`
```json
[
  {
    "id": "payment-uuid",
    "user_id": "user-uuid",
    "amount_usd": 10.0,
    "gb_purchased": 50,
    "method": "crypto_usdt",
    "status": "completed",
    "created_at": "2026-03-22T02:16:03.281396Z"
  }
]
```

---

### GET /api/v1/payments/{payment_id}

Obtiene detalles de un pago específico.

**Auth:** Requerida

**Response:** `200 OK`
```json
{
  "id": "payment-uuid",
  "user_id": "user-uuid",
  "amount_usd": 10.0,
  "gb_purchased": 50,
  "method": "crypto_usdt",
  "status": "completed",
  "created_at": "2026-03-22T02:16:03.281396Z"
}
```

**Errors:**
- `404` - Payment not found
- `403` - Not authorized

---

## Referrals

### GET /api/v1/referrals/me

Obtiene las estadísticas de referidos del usuario actual.

**Auth:** Requerida

**Response:** `200 OK`
```json
{
  "referral_code": "ref_3a04ed656fb64cfb",
  "credits": 0,
  "referral_count": 0,
  "total_earned_gb": 0
}
```

---

### POST /api/v1/referrals/apply

Aplica un código de referido al usuario actual.

**Auth:** Requerida

**Request:**
```json
{
  "referral_code": "ref_3a04ed656fb64cfb"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Referral code applied successfully",
  "data": {...}
}
```

**Errors:**
- `404` - Referral code not found
- `400` - Cannot refer yourself / Already have a referrer

---

### POST /api/v1/referrals/redeem

Canjea créditos de referido por datos (GB).

**Auth:** Requerida

**Request:**
```json
{
  "credits": 100
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Successfully redeemed 100 credits for 1GB",
  "data": {...}
}
```

**Errors:**
- `400` - Insufficient referral credits

---

## Data Packages

### GET /api/v1/data-packages/options

Obtiene las opciones de paquetes de datos disponibles.

**Auth:** Requerida

**Response:** `200 OK`
```json
[
  {
    "package_type": "basic",
    "name": "Básico",
    "data_gb": 10,
    "stars": 100,
    "usdt": 2
  },
  {
    "package_type": "standard",
    "name": "Estándar",
    "data_gb": 30,
    "stars": 250,
    "usdt": 5
  }
]
```

---

### GET /api/v1/data-packages/slots/options

Obtiene las opciones de slots de claves disponibles.

**Auth:** Requerida

**Response:** `200 OK`
```json
[
  {
    "slot_type": "extra",
    "name": "Slot Extra",
    "stars": 50,
    "usdt": 1
  }
]
```

---

### GET /api/v1/data-packages/me

Obtiene los paquetes de datos del usuario actual.

**Auth:** Requerida

**Response:** `200 OK`
```json
{
  "packages": [
    {
      "id": "package-uuid",
      "user_id": 1058749165,
      "package_type": "basic",
      "data_gb": 10,
      "data_used_gb": 2.5,
      "is_active": true,
      "expires_at": "2026-04-21T02:16:03.281396Z",
      "created_at": "2026-03-22T02:16:03.281396Z"
    }
  ],
  "total_count": 1
}
```

---

### POST /api/v1/data-packages/purchase

Compra un nuevo paquete de datos.

**Auth:** Requerida

**Request:**
```json
{
  "package_type": "basic",
  "telegram_payment_id": "telegram-payment-uuid",
  "is_referred_first_purchase": false
}
```

**Response:** `201 Created`
```json
{
  "package": {
    "id": "package-uuid",
    "user_id": 1058749165,
    "package_type": "basic",
    "data_gb": 10,
    "is_active": true
  },
  "bonuses": {
    "referral_bonus_gb": 0,
    "first_purchase_bonus_gb": 0
  }
}
```

---

## Wallets

### GET /api/v1/wallets/me

Obtiene la wallet del usuario autenticado.

**Auth:** Requerida

**Response:** `200 OK` o `null`
```json
{
  "id": "wallet-uuid",
  "user_id": "user-uuid",
  "address": "0x1234567890abcdef1234567890abcdef12345678",
  "label": "My Wallet",
  "status": "active",
  "balance_usdt": 10.5,
  "created_at": "2026-03-22T02:16:03.281396Z",
  "updated_at": "2026-03-22T02:16:03.281396Z",
  "last_used_at": null,
  "total_received_usdt": 50.0,
  "transaction_count": 5
}
```

---

### GET /api/v1/wallets/{wallet_id}

Obtiene una wallet por ID.

**Auth:** Requerida

**Response:** `200 OK`
```json
{
  "id": "wallet-uuid",
  "user_id": "user-uuid",
  "address": "0x1234567890abcdef1234567890abcdef12345678",
  "label": "My Wallet",
  "status": "active",
  "balance_usdt": 10.5,
  "created_at": "2026-03-22T02:16:03.281396Z",
  "updated_at": "2026-03-22T02:16:03.281396Z",
  "last_used_at": null,
  "total_received_usdt": 50.0,
  "transaction_count": 5
}
```

**Errors:**
- `404` - Wallet not found
- `403` - Not authorized

---

### POST /api/v1/wallets

Crea/asigna una nueva wallet al usuario.

**Auth:** Requerida

**Request:**
```json
{
  "label": "My New Wallet"
}
```

**Response:** `201 Created`
```json
{
  "id": "wallet-uuid",
  "user_id": "user-uuid",
  "address": "0x1234567890abcdef1234567890abcdef12345678",
  "label": "My New Wallet",
  "status": "active",
  "balance_usdt": 0.0,
  "created_at": "2026-03-22T02:16:03.281396Z",
  "updated_at": "2026-03-22T02:16:03.281396Z",
  "last_used_at": null,
  "total_received_usdt": 0.0,
  "transaction_count": 0
}
```

---

### PATCH /api/v1/wallets/{wallet_id}

Actualiza una wallet existente.

**Auth:** Requerida

**Request:**
```json
{
  "label": "Updated Label",
  "status": "inactive"
}
```

**Response:** `200 OK`
```json
{
  "id": "wallet-uuid",
  "user_id": "user-uuid",
  "address": "0x1234567890abcdef1234567890abcdef12345678",
  "label": "Updated Label",
  "status": "inactive",
  "balance_usdt": 10.5,
  "created_at": "2026-03-22T02:16:03.281396Z",
  "updated_at": "2026-03-22T02:16:03.281396Z",
  "last_used_at": null,
  "total_received_usdt": 50.0,
  "transaction_count": 5
}
```

---

### POST /api/v1/wallets/{wallet_id}/deposit

Deposita fondos en una wallet.

**Auth:** Requerida

**Request:**
```json
{
  "amount_usdt": 10.0
}
```

**Response:** `200 OK`
```json
{
  "id": "wallet-uuid",
  "user_id": "user-uuid",
  "address": "0x1234567890abcdef1234567890abcdef12345678",
  "label": "My Wallet",
  "status": "active",
  "balance_usdt": 20.5,
  "created_at": "2026-03-22T02:16:03.281396Z",
  "updated_at": "2026-03-22T02:16:03.281396Z",
  "last_used_at": null,
  "total_received_usdt": 60.0,
  "transaction_count": 6
}
```

---

### POST /api/v1/wallets/{wallet_id}/withdraw

Retira fondos de una wallet.

**Auth:** Requerida

**Request:**
```json
{
  "amount_usdt": 5.0
}
```

**Response:** `200 OK`
```json
{
  "id": "wallet-uuid",
  "user_id": "user-uuid",
  "address": "0x1234567890abcdef1234567890abcdef12345678",
  "label": "My Wallet",
  "status": "active",
  "balance_usdt": 15.5,
  "created_at": "2026-03-22T02:16:03.281396Z",
  "updated_at": "2026-03-22T02:16:03.281396Z",
  "last_used_at": null,
  "total_received_usdt": 60.0,
  "transaction_count": 6
}
```

**Errors:**
- `400` - Insufficient balance

---

### GET /api/v1/wallets/pool/stats

Obtiene estadísticas del pool de wallets (admin only).

**Auth:** Requerida (admin)

**Response:** `200 OK`
```json
{
  "total_wallets": 100,
  "available_wallets": 50,
  "expired_wallets": 30,
  "in_use_wallets": 20
}
```

**Errors:**
- `403` - Admin access required

---

### GET /api/v1/wallets/pool

Obtiene todas las wallets del pool (admin only).

**Auth:** Requerida (admin)

**Response:** `200 OK`
```json
[
  {
    "id": "wallet-uuid",
    "address": "0x...",
    "status": "available",
    "expires_at": "2026-04-21T02:16:03.281396Z",
    "assigned_to": null
  }
]
```

**Errors:**
- `403` - Admin access required

---

## Tickets

### POST /api/v1/tickets

Crea un nuevo ticket de soporte.

**Auth:** Requerida

**Request:**
```json
{
  "category": "technical",
  "subject": "VPN not connecting",
  "message": "I cannot connect to the VPN server"
}
```

**Response:** `201 Created`
```json
{
  "id": "ticket-uuid",
  "ticket_number": "TKT-12345",
  "user_id": 1058749165,
  "category": "technical",
  "priority": "medium",
  "status": "open",
  "subject": "VPN not connecting",
  "created_at": "2026-03-22T02:16:03.281396Z",
  "updated_at": "2026-03-22T02:16:03.281396Z",
  "resolved_at": null,
  "resolved_by": null,
  "admin_notes": null
}
```

---

### GET /api/v1/tickets

Obtiene todos los tickets del usuario.

**Auth:** Requerida

**Response:** `200 OK`
```json
[
  {
    "id": "ticket-uuid",
    "ticket_number": "TKT-12345",
    "user_id": 1058749165,
    "category": "technical",
    "priority": "medium",
    "status": "open",
    "subject": "VPN not connecting",
    "created_at": "2026-03-22T02:16:03.281396Z",
    "updated_at": "2026-03-22T02:16:03.281396Z",
    "resolved_at": null,
    "resolved_by": null,
    "admin_notes": null
  }
]
```

---

### GET /api/v1/tickets/{ticket_id}

Obtiene un ticket específico con todos sus mensajes.

**Auth:** Requerida

**Response:** `200 OK`
```json
{
  "id": "ticket-uuid",
  "ticket_number": "TKT-12345",
  "user_id": 1058749165,
  "category": "technical",
  "priority": "medium",
  "status": "open",
  "subject": "VPN not connecting",
  "created_at": "2026-03-22T02:16:03.281396Z",
  "updated_at": "2026-03-22T02:16:03.281396Z",
  "resolved_at": null,
  "resolved_by": null,
  "admin_notes": null,
  "messages": [
    {
      "id": "message-uuid",
      "ticket_id": "ticket-uuid",
      "from_user_id": 1058749165,
      "message": "I cannot connect",
      "from_admin": false,
      "created_at": "2026-03-22T02:16:03.281396Z"
    }
  ]
}
```

---

### POST /api/v1/tickets/{ticket_id}/messages

Agrega un mensaje a un ticket.

**Auth:** Requerida

**Request:**
```json
{
  "message": "Update: Still not working"
}
```

**Response:** `201 Created`
```json
{
  "message": "Message added successfully"
}
```

---

### POST /api/v1/tickets/{ticket_id}/resolve

Resuelve un ticket (admin only).

**Auth:** Requerida (admin)

**Request:**
```json
{
  "notes": "Issue resolved by restarting server"
}
```

**Response:** `200 OK`
```json
{
  "id": "ticket-uuid",
  "ticket_number": "TKT-12345",
  "user_id": 1058749165,
  "category": "technical",
  "priority": "medium",
  "status": "resolved",
  "subject": "VPN not connecting",
  "created_at": "2026-03-22T02:16:03.281396Z",
  "updated_at": "2026-03-22T02:16:03.281396Z",
  "resolved_at": "2026-03-22T03:16:03.281396Z",
  "resolved_by": 999999,
  "admin_notes": "Issue resolved by restarting server"
}
```

**Errors:**
- `403` - Admin access required
- `404` - Ticket not found

---

### POST /api/v1/tickets/{ticket_id}/close

Cierra un ticket.

**Auth:** Requerida

**Response:** `200 OK`
```json
{
  "id": "ticket-uuid",
  "ticket_number": "TKT-12345",
  "user_id": 1058749165,
  "category": "technical",
  "priority": "medium",
  "status": "closed",
  "subject": "VPN not connecting",
  "created_at": "2026-03-22T02:16:03.281396Z",
  "updated_at": "2026-03-22T02:16:03.281396Z",
  "resolved_at": "2026-03-22T03:16:03.281396Z",
  "resolved_by": 999999,
  "admin_notes": null
}
```

---

### GET /api/v1/tickets/admin/pending

Obtiene todos los tickets pendientes (admin only).

**Auth:** Requerida (admin)

**Response:** `200 OK`
```json
[
  {
    "id": "ticket-uuid",
    "ticket_number": "TKT-12345",
    "user_id": 1058749165,
    "category": "technical",
    "priority": "medium",
    "status": "open",
    "subject": "VPN not connecting",
    "created_at": "2026-03-22T02:16:03.281396Z",
    "updated_at": "2026-03-22T02:16:03.281396Z",
    "resolved_at": null,
    "resolved_by": null,
    "admin_notes": null
  }
]
```

**Errors:**
- `403` - Admin access required

---

### GET /api/v1/tickets/admin/stats

Obtiene estadísticas de tickets (admin only).

**Auth:** Requerida (admin)

**Response:** `200 OK`
```json
{
  "open_count": 5,
  "responded_count": 3,
  "resolved_count": 10,
  "closed_count": 2
}
```

**Errors:**
- `403` - Admin access required

---

## Billing

### GET /api/v1/billing/usage

Obtiene el uso de datos del usuario actual.

**Auth:** Requerida

**Response:** `200 OK`
```json
{
  "balance_gb": 5.0,
  "total_purchased_gb": 0.0,
  "keys_count": 3,
  "data_used_gb": 0.0,
  "data_limit_gb": 15.0,
  "usage_percentage": 0.0
}
```

---

### GET /api/v1/billing/usage/{key_id}

Obtiene el uso de datos de una clave específica.

**Auth:** Requerida

**Response:** `200 OK`
```json
{
  "key_id": "key-uuid",
  "name": "My VPN Key",
  "data_used_gb": 2.5,
  "data_limit_gb": 5.0,
  "usage_percentage": 50.0,
  "expires_at": "2026-04-21T02:16:03.281396Z"
}
```

**Errors:**
- `403` - Not authorized
- `404` - Key not found

---

## Consumption Invoices

### POST /api/v1/invoices

Crea una nueva factura de consumo.

**Auth:** Requerida

**Request:**
```json
{
  "billing_id": "billing-uuid",
  "user_id": 1058749165,
  "amount_usd": 5.0,
  "payment_method": "crypto"
}
```

**Response:** `201 Created`
```json
{
  "id": "invoice-uuid",
  "billing_id": "billing-uuid",
  "user_id": 1058749165,
  "amount_usd": 5.0,
  "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
  "payment_method": "crypto",
  "status": "pending",
  "expires_at": "2026-03-22T02:46:03.281396Z",
  "paid_at": null,
  "transaction_hash": null,
  "telegram_payment_id": null,
  "created_at": "2026-03-22T02:16:03.281396Z",
  "time_remaining_seconds": 1800,
  "is_expired": false
}
```

---

### GET /api/v1/invoices/{invoice_id}

Obtiene una factura por ID.

**Auth:** Requerida

**Response:** `200 OK`
```json
{
  "id": "invoice-uuid",
  "billing_id": "billing-uuid",
  "user_id": 1058749165,
  "amount_usd": 5.0,
  "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
  "payment_method": "crypto",
  "status": "pending",
  "expires_at": "2026-03-22T02:46:03.281396Z",
  "paid_at": null,
  "transaction_hash": null,
  "telegram_payment_id": null,
  "created_at": "2026-03-22T02:16:03.281396Z",
  "time_remaining_seconds": 1800,
  "is_expired": false
}
```

---

### GET /api/v1/invoices/user/{user_id}

Obtiene todas las facturas de un usuario.

**Auth:** Requerida

**Response:** `200 OK`
```json
{
  "invoices": [...],
  "total": 5,
  "pending_count": 2,
  "paid_count": 2,
  "expired_count": 1
}
```

---

### GET /api/v1/invoices/user/{user_id}/pending

Obtiene la factura pendiente de un usuario (máximo 1 activa).

**Auth:** Requerida

**Response:** `200 OK` o `null`
```json
{
  "id": "invoice-uuid",
  "billing_id": "billing-uuid",
  "user_id": 1058749165,
  "amount_usd": 5.0,
  "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
  "payment_method": "crypto",
  "status": "pending",
  "expires_at": "2026-03-22T02:46:03.281396Z",
  "paid_at": null,
  "transaction_hash": null,
  "telegram_payment_id": null,
  "created_at": "2026-03-22T02:16:03.281396Z",
  "time_remaining_seconds": 1800,
  "is_expired": false
}
```

---

### GET /api/v1/invoices/billing/{billing_id}

Obtiene todas las facturas de un ciclo de facturación.

**Auth:** Requerida

**Response:** `200 OK`
```json
[
  {
    "id": "invoice-uuid",
    "billing_id": "billing-uuid",
    "user_id": 1058749165,
    "amount_usd": 5.0,
    "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
    "payment_method": "crypto",
    "status": "pending",
    "expires_at": "2026-03-22T02:46:03.281396Z",
    "paid_at": null,
    "transaction_hash": null,
    "telegram_payment_id": null,
    "created_at": "2026-03-22T02:16:03.281396Z",
    "time_remaining_seconds": 1800,
    "is_expired": false
  }
]
```

---

### POST /api/v1/invoices/{invoice_id}/pay

Marca una factura como pagada.

**Auth:** Requerida

**Request:**
```json
{
  "transaction_hash": "0xabc123..."
}
```

**Response:** `200 OK`
```json
{
  "id": "invoice-uuid",
  "billing_id": "billing-uuid",
  "user_id": 1058749165,
  "amount_usd": 5.0,
  "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
  "payment_method": "crypto",
  "status": "paid",
  "expires_at": "2026-03-22T02:46:03.281396Z",
  "paid_at": "2026-03-22T02:20:03.281396Z",
  "transaction_hash": "0xabc123...",
  "telegram_payment_id": null,
  "created_at": "2026-03-22T02:16:03.281396Z",
  "time_remaining_seconds": 0,
  "is_expired": false
}
```

**Errors:**
- `400` - Invoice is not pending / Invoice has expired
- `404` - Invoice not found

---

### POST /api/v1/invoices/{invoice_id}/expire

Marca una factura como expirada.

**Auth:** Requerida

**Response:** `200 OK`
```json
{
  "id": "invoice-uuid",
  "billing_id": "billing-uuid",
  "user_id": 1058749165,
  "amount_usd": 5.0,
  "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
  "payment_method": "crypto",
  "status": "expired",
  "expires_at": "2026-03-22T02:46:03.281396Z",
  "paid_at": null,
  "transaction_hash": null,
  "telegram_payment_id": null,
  "created_at": "2026-03-22T02:16:03.281396Z",
  "time_remaining_seconds": 0,
  "is_expired": true
}
```

**Errors:**
- `400` - Cannot expire a paid invoice
- `404` - Invoice not found

---

### POST /api/v1/invoices/{invoice_id}/status

Actualiza el estado de una factura.

**Auth:** Requerida

**Request:**
```json
{
  "status": "paid"
}
```

**Response:** `200 OK`
```json
{
  "id": "invoice-uuid",
  "billing_id": "billing-uuid",
  "user_id": 1058749165,
  "amount_usd": 5.0,
  "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
  "payment_method": "crypto",
  "status": "paid",
  "expires_at": "2026-03-22T02:46:03.281396Z",
  "paid_at": "2026-03-22T02:20:03.281396Z",
  "transaction_hash": "0xabc123...",
  "telegram_payment_id": null,
  "created_at": "2026-03-22T02:16:03.281396Z",
  "time_remaining_seconds": 0,
  "is_expired": false
}
```

**Errors:**
- `400` - Invalid status
- `404` - Invoice not found

---

### DELETE /api/v1/invoices/{invoice_id}

Elimina una factura de consumo.

**Auth:** Requerida

**Response:** `204 No Content`

**Errors:**
- `404` - Invoice not found

---

### GET /api/v1/invoices/status/{invoice_status}

Obtiene facturas por estado.

**Auth:** Requerida

**Request:** `invoice_status` = `pending`, `paid`, o `expired`

**Response:** `200 OK`
```json
[
  {
    "id": "invoice-uuid",
    "billing_id": "billing-uuid",
    "user_id": 1058749165,
    "amount_usd": 5.0,
    "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
    "payment_method": "crypto",
    "status": "pending",
    "expires_at": "2026-03-22T02:46:03.281396Z",
    "paid_at": null,
    "transaction_hash": null,
    "telegram_payment_id": null,
    "created_at": "2026-03-22T02:16:03.281396Z",
    "time_remaining_seconds": 1800,
    "is_expired": false
  }
]
```

**Errors:**
- `400` - Invalid status

---

### GET /api/v1/invoices/expired/pending

Obtiene facturas pendientes expiradas.

**Auth:** Requerida

**Response:** `200 OK`
```json
[
  {
    "id": "invoice-uuid",
    "billing_id": "billing-uuid",
    "user_id": 1058749165,
    "amount_usd": 5.0,
    "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
    "payment_method": "crypto",
    "status": "pending",
    "expires_at": "2026-03-22T02:46:03.281396Z",
    "paid_at": null,
    "transaction_hash": null,
    "telegram_payment_id": null,
    "created_at": "2026-03-22T02:16:03.281396Z",
    "time_remaining_seconds": 0,
    "is_expired": true
  }
]
```

---

## Admin

Los endpoints de admin están bajo `/api/v1/admin/` y requieren autenticación de administrador.

### Dashboard & Stats

- `GET /api/v1/admin/dashboard/stats` - Estadísticas del dashboard

### User Management

- `GET /api/v1/admin/users` - Lista todos los usuarios
- `GET /api/v1/admin/users/paginated` - Lista paginada de usuarios
- `POST /api/v1/admin/users/{user_id}/status` - Actualiza estado del usuario
- `POST /api/v1/admin/users/{user_id}/role` - Asigna rol al usuario
- `POST /api/v1/admin/users/{user_id}/block` - Bloquea usuario
- `POST /api/v1/admin/users/{user_id}/unblock` - Desbloquea usuario
- `DELETE /api/v1/admin/users/{user_id}` - Elimina usuario

### VPN Key Management

- `GET /api/v1/admin/keys` - Lista todas las claves VPN
- `GET /api/v1/admin/users/{user_id}/keys` - Lista claves de un usuario
- `POST /api/v1/admin/keys/{key_id}/toggle` - Activa/desactiva clave
- `DELETE /api/v1/admin/keys/{key_id}` - Elimina clave

### Server Management

- `GET /api/v1/admin/servers/status` - Estado de servidores
- `GET /api/v1/admin/servers/stats` - Estadísticas de servidores

---

## Códigos de Error

| Código | Descripción |
|--------|-------------|
| `200` | OK - Operación exitosa |
| `201` | Created - Recurso creado exitosamente |
| `204` | No Content - Operación exitosa sin contenido |
| `400` | Bad Request - Solicitud inválida |
| `401` | Unauthorized - Token inválido o expirado |
| `403` | Forbidden - No autorizado para esta acción |
| `404` | Not Found - Recurso no encontrado |
| `500` | Internal Server Error - Error interno del servidor |

---

## Autenticación

Para autenticarte, primero obtén un token JWT:

```bash
curl -X POST http://localhost:8001/api/v1/auth/telegram \
  -H "Content-Type: application/json" \
  -d '{"init_data": "..."}'
```

Luego usa el token en las solicitudes:

```bash
curl -X GET http://localhost:8001/api/v1/vpn/keys \
  -H "Authorization: Bearer <tu-token>"
```

---

**Documentación generada:** 2026-03-22
**Versión del Backend:** 0.2.0
