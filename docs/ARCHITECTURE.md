# Architecture

## Overview

Backend API principal del ecosistema uSipipo.

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL (asyncpg + SQLAlchemy)
- **Package Manager:** uv
- **Shared Library:** usipipo-commons

## Project Structure

```
src/
├── __init__.py
├── __main__.py
├── main.py          # FastAPI app entry point
├── config/          # Configuration
├── api/             # API routes
├── models/          # SQLAlchemy models
├── schemas/         # Pydantic schemas
├── services/        # Business logic
└── utils/           # Utilities
```

## Dependencies

- `usipipo-commons`: Entidades y schemas compartidos
- `fastapi`: Web framework
- `sqlalchemy`: ORM
- `asyncpg`: PostgreSQL driver
- `alembic`: Database migrations
