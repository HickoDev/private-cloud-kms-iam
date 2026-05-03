# Architecture

The project uses a simple monolithic architecture for an academic private cloud security prototype.

```text
React dashboard -> FastAPI backend -> PostgreSQL
```

## Components

- **Frontend**: React + Vite dashboard for login, users, keys, crypto operations, and audit logs.
- **Backend**: FastAPI API exposing authentication, IAM, KMS, and audit modules.
- **Database**: PostgreSQL stores users, roles, permissions, key metadata, encrypted key material, and audit logs.

## Backend Modules

- `auth`: login, JWT creation, current user.
- `iam`: users, roles, permissions, role assignment.
- `kms`: key lifecycle, key versions, encryption, decryption, rotation.
- `audit`: security event logging and filtering.
- `core`: configuration, database, security helpers, permission mapping.

## Principle

Users never receive raw cryptographic key material. They call the backend API and the KMS uses the key internally.

