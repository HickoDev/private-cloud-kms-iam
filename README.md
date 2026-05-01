# KMS Mini-IAM for Private Cloud

Academic prototype of a cryptographic Key Management System integrated with a small IAM module for a private cloud scenario.

## Stack

- FastAPI backend
- PostgreSQL database
- SQLAlchemy and Alembic
- React + Vite frontend
- Docker Compose
- JWT authentication
- AES-256-GCM cryptography

## Local Run

Create the local environment file:

```bash
cp .env.example .env
```

Start the full stack:

```bash
docker compose up --build
```

Services:

```text
Frontend: http://localhost:5173
Backend API: http://localhost:8000
Swagger docs: http://localhost:8000/docs
PostgreSQL: localhost:5432
```

## Default Demo User

The seeded admin account will be:

```text
email: admin@example.com
password: admin123
```

This password is for local academic demonstration only.

## Development Phases

1. Project skeleton
2. Database models and seed data
3. Authentication and RBAC
4. KMS key lifecycle and crypto operations
5. Audit logs
6. React dashboard
7. Tests and documentation

