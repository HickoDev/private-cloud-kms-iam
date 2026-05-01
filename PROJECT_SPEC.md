# Project Specification

# Gestionnaire de cles cryptographiques (KMS) integre a un mini-IAM pour cloud prive

## 1. Project Idea

Build a simple academic prototype of a **Key Management System (KMS)** integrated with a small **Identity and Access Management (Mini-IAM)** module.

The goal is not to clone AWS KMS, Vault, Keycloak, or a production cloud platform. The goal is to demonstrate the important cybersecurity concepts clearly:

- user authentication
- role-based access control
- cryptographic key lifecycle
- encryption and decryption through an API
- key rotation
- audit logs
- separation of duties between admin, key manager, key user, and auditor

## 2. Recommended Scope

My recommendation is to keep the project as a clean monolithic web application:

```text
React dashboard -> FastAPI backend -> PostgreSQL database
```

Do not use microservices, Kubernetes, Keycloak, HSM, OAuth server, SIEM, or advanced policy engines for the first version. These can be mentioned as future improvements in the report.

The best academic version is:

- simple enough to finish
- secure enough to defend in a presentation
- visual enough to demo
- structured enough to look professional

## 3. Main Users and Roles

Use four fixed roles. Roles are seeded in the database and do not need a complex role editor in the MVP.

| Role | Purpose |
|---|---|
| `ADMIN` | Manage users, assign roles, view everything |
| `KEY_MANAGER` | Create, disable, and rotate keys |
| `KEY_USER` | Encrypt and decrypt data using active keys |
| `AUDITOR` | Read audit logs and key metadata |

Recommended simplification:

- Store roles and permissions in the database for demonstration.
- Enforce permissions in backend code using dependencies/decorators.
- In the frontend, only show pages/actions allowed for the logged-in user's roles.

## 4. Minimum Viable Product

The first complete version must include:

- Login with email and password
- JWT authentication
- Seeded admin user
- User list and user creation
- Role assignment to users
- Key creation
- Key listing
- Key disable
- Key rotation
- Encrypt text with an active key
- Decrypt text with the correct key version
- Audit log table
- React dashboard
- Docker Compose for local execution
- Swagger/OpenAPI documentation

This is enough for a strong university demo.

## 5. Recommended Tech Stack

```text
Backend: FastAPI
Database: PostgreSQL
ORM: SQLAlchemy
Migrations: Alembic
Authentication: JWT
Password hashing: bcrypt/passlib
Cryptography: Python cryptography package
Frontend: React + Vite
Styling: simple CSS or Tailwind CSS
Deployment: Docker Compose
Tests: Pytest
```

Why this stack:

- FastAPI gives automatic Swagger documentation.
- PostgreSQL looks realistic for a private cloud backend.
- React is enough for a clean dashboard.
- Docker Compose makes the project easy to run during the demo.
- Pytest allows basic security and API tests.

## 6. Architecture

```text
                 +----------------------+
                 |   React Frontend     |
                 |   localhost:5173     |
                 +----------+-----------+
                            |
                            | HTTP + JWT
                            |
                 +----------v-----------+
                 |   FastAPI Backend    |
                 |   localhost:8000     |
                 +----------+-----------+
                            |
                            | SQLAlchemy
                            |
                 +----------v-----------+
                 |    PostgreSQL DB     |
                 |    localhost:5432    |
                 +----------------------+
```

Backend modules:

- `auth`: login, current user, JWT validation
- `iam`: users, roles, permissions
- `kms`: keys, key versions, encryption, decryption, rotation
- `audit`: security event logging
- `core`: config, database, security helpers, permission checks

## 7. Suggested Project Structure

Keep the repository smaller than a production system.

```text
kms-mini-iam-private-cloud/
  README.md
  PROJECT_SPEC.md
  docker-compose.yml
  .env.example
  .gitignore

  backend/
    Dockerfile
    requirements.txt
    alembic.ini
    app/
      main.py
      core/
        config.py
        database.py
        security.py
        permissions.py
      auth/
        router.py
        service.py
        schemas.py
      iam/
        router.py
        service.py
        models.py
        schemas.py
      kms/
        router.py
        service.py
        crypto.py
        models.py
        schemas.py
      audit/
        router.py
        service.py
        models.py
        schemas.py
      seed.py
    tests/
      test_auth.py
      test_permissions.py
      test_kms.py

  frontend/
    Dockerfile
    package.json
    src/
      main.jsx
      App.jsx
      services/api.js
      pages/
        LoginPage.jsx
        DashboardPage.jsx
        UsersPage.jsx
        KeysPage.jsx
        CryptoPage.jsx
        AuditLogsPage.jsx
      components/
        Layout.jsx
        ProtectedRoute.jsx
        DataTable.jsx
        Modal.jsx

  docs/
    architecture.md
    security-model.md
    demo-scenario.md
```

This structure is easier to implement than many tiny modules, but still clean.

## 8. Database Model

### users

```text
id
username
email
password_hash
is_active
created_at
updated_at
```

### roles

```text
id
name
description
created_at
```

Seed values:

```text
ADMIN
KEY_MANAGER
KEY_USER
AUDITOR
```

### permissions

```text
id
name
description
created_at
```

Recommended permissions:

```text
USER_READ
USER_CREATE
USER_UPDATE
ROLE_ASSIGN
KEY_READ
KEY_CREATE
KEY_DISABLE
KEY_ROTATE
DATA_ENCRYPT
DATA_DECRYPT
AUDIT_READ
```

### user_roles

```text
user_id
role_id
```

### role_permissions

```text
role_id
permission_id
```

### kms_keys

Stores key metadata only. It must never expose raw key material.

```text
id
name
description
algorithm
status
owner_id
created_at
updated_at
disabled_at
```

Example values:

```text
algorithm = AES-256-GCM
status = ACTIVE | DISABLED | DELETED
```

### key_versions

Stores encrypted key material.

```text
id
key_id
version_number
encrypted_key_material
key_material_nonce
is_active
created_at
rotated_at
```

Rules:

- Only one version is active for new encryption.
- Old versions stay available for decryption.
- Raw key material is encrypted using the application `MASTER_KEY`.
- Raw key material is never returned by the API.

### audit_logs

```text
id
user_id
action
resource_type
resource_id
status
ip_address
details
created_at
```

Example actions:

```text
LOGIN_SUCCESS
LOGIN_FAILED
USER_CREATED
ROLE_ASSIGNED
KEY_CREATED
KEY_DISABLED
KEY_ROTATED
DATA_ENCRYPTED
DATA_DECRYPTED
ACCESS_DENIED
```

## 9. API Endpoints

### Authentication

```http
POST /api/auth/login
GET  /api/auth/me
```

### Users and IAM

```http
GET  /api/users
POST /api/users
GET  /api/users/{id}
PUT  /api/users/{id}
POST /api/users/{id}/roles
GET  /api/roles
GET  /api/permissions
```

For the MVP, role creation is optional. Fixed seeded roles are enough.

### KMS

```http
GET  /api/keys
POST /api/keys
GET  /api/keys/{id}
POST /api/keys/{id}/disable
POST /api/keys/{id}/rotate
GET  /api/keys/{id}/versions
POST /api/keys/{id}/encrypt
POST /api/keys/{id}/decrypt
```

### Audit

```http
GET /api/audit-logs
GET /api/audit-logs?action=KEY_CREATED
GET /api/audit-logs?status=FAILED
GET /api/audit-logs?user_id=1
```

## 10. Authorization Matrix

| Feature | ADMIN | KEY_MANAGER | KEY_USER | AUDITOR |
|---|---:|---:|---:|---:|
| View dashboard | yes | yes | yes | yes |
| View users | yes | no | no | no |
| Create users | yes | no | no | no |
| Assign roles | yes | no | no | no |
| View keys | yes | yes | yes | yes |
| Create keys | yes | yes | no | no |
| Disable keys | yes | yes | no | no |
| Rotate keys | yes | yes | no | no |
| Encrypt data | yes | no | yes | no |
| Decrypt data | yes | no | yes | no |
| View audit logs | yes | no | no | yes |

## 11. Cryptography Design

Use AES-256-GCM for encryption and decryption.

Two levels of encryption are used:

1. **KMS key material protection**
   - Generate a 256-bit random data key.
   - Encrypt that data key with `MASTER_KEY` from `.env`.
   - Store only encrypted key material in `key_versions`.

2. **User data encryption**
   - User sends plaintext to `/encrypt`.
   - Backend loads the active key version.
   - Backend decrypts key material in memory.
   - Backend encrypts plaintext with AES-256-GCM.
   - Backend returns `ciphertext`, `nonce`, `key_id`, and `key_version`.

Important rules:

- Never reuse a nonce with the same key.
- Never return raw key material.
- Never store plaintext user data.
- Disabled keys cannot encrypt new data.
- Old key versions can decrypt old ciphertext.

Example encrypt response:

```json
{
  "key_id": 1,
  "key_version": 2,
  "algorithm": "AES-256-GCM",
  "ciphertext": "base64...",
  "nonce": "base64..."
}
```

## 12. Environment Variables

Create `.env.example`:

```env
APP_NAME=KMS Mini IAM
APP_ENV=development

DATABASE_URL=postgresql://kms_user:kms_password@postgres:5432/kms_db

JWT_SECRET_KEY=change_me_to_a_long_random_secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

MASTER_KEY=base64_encoded_32_byte_key_here

BACKEND_PORT=8000
FRONTEND_PORT=5173
```

Security notes:

- `.env` must not be committed.
- `MASTER_KEY` protects encrypted key material.
- In a real system, the master key would be stored in an HSM or a vault.

## 13. Frontend Pages

### Login Page

- email
- password
- login button
- error state for invalid credentials

### Dashboard Page

Show simple statistics:

- total users
- total keys
- active keys
- audit log count

### Users Page

Admin only:

- list users
- create user
- activate/deactivate user
- assign roles

### Keys Page

Admin and key manager:

- list keys
- create key
- disable key
- rotate key
- view versions

Auditor can view key metadata only.

### Crypto Page

Admin and key user:

- select key
- enter plaintext
- encrypt
- paste ciphertext and nonce
- decrypt

### Audit Logs Page

Admin and auditor:

- table of logs
- filter by action
- filter by status
- filter by user

## 14. Implementation Plan

### Phase 1: Project Skeleton

Deliver:

- repository structure
- Docker Compose with backend, frontend, postgres
- FastAPI app running
- React app running
- `.env.example`
- README with run instructions

### Phase 2: Database and Seed Data

Deliver:

- SQLAlchemy models
- Alembic migration
- seed script
- default roles and permissions
- default admin user

Default admin:

```text
email: admin@example.com
password: admin123
role: ADMIN
```

### Phase 3: Authentication and IAM

Deliver:

- password hashing
- login endpoint
- JWT generation and validation
- current user endpoint
- permission dependency
- user creation
- role assignment

### Phase 4: KMS Core

Deliver:

- create key
- list keys
- disable key
- rotate key
- key version table
- AES-256-GCM crypto helper
- encrypt endpoint
- decrypt endpoint

### Phase 5: Audit Logs

Deliver:

- reusable audit service
- log successful actions
- log failed login
- log access denied attempts
- audit log filters

### Phase 6: Frontend Dashboard

Deliver:

- login flow
- protected routes
- sidebar/menu
- users page
- keys page
- crypto page
- audit logs page
- role-based UI visibility

### Phase 7: Tests and Documentation

Deliver:

- auth tests
- permission tests
- KMS encrypt/decrypt tests
- key rotation test
- README
- architecture document
- security model document
- screenshots for final report

## 15. Recommended Test Cases

Minimum tests:

- valid login returns JWT
- invalid login fails
- request without token fails
- non-admin cannot create user
- admin can create user
- key user cannot create key
- key manager can create key
- key user can encrypt and decrypt
- disabled key cannot encrypt
- key rotation creates a new active version
- old ciphertext can still be decrypted with old key version
- sensitive actions create audit logs

## 16. Final Demo Scenario

Use this scenario during the presentation:

1. Start the project with `docker compose up --build`.
2. Open the frontend.
3. Login as `admin@example.com`.
4. Create a user `user@example.com`.
5. Assign `KEY_USER` role to that user.
6. Create a key named `customer-data-key`.
7. Login as `user@example.com`.
8. Encrypt a message.
9. Decrypt the message.
10. Login again as admin.
11. View audit logs.
12. Rotate the key.
13. Encrypt a new message.
14. Show that old ciphertext still decrypts with the previous version.

This scenario proves IAM, KMS, rotation, and auditability.

## 17. Out of Scope

Do not implement these in the academic version:

- real HSM
- HashiCorp Vault integration
- Keycloak integration
- Kubernetes deployment
- microservices
- real OAuth2/OIDC server
- multi-region cloud
- certificate authority
- production compliance
- advanced ABAC policy engine
- MFA
- refresh token rotation

Mention them as future improvements only.

## 18. Future Improvements

Possible extensions:

- per-key access policies
- service accounts for cloud applications
- refresh tokens
- MFA
- API rate limiting
- Prometheus/Grafana monitoring
- HashiCorp Vault integration
- SoftHSM integration
- Keycloak integration
- Kubernetes deployment

## 19. Main Deliverables

Final project should include:

- source code
- backend API
- frontend dashboard
- database migrations
- seed data
- Docker Compose setup
- Swagger documentation
- README
- screenshots
- short security model report
- test results

## 20. First Codex Prompt

Use this prompt to start implementation:

```md
We are building an academic project named `kms-mini-iam-private-cloud`.

Read `PROJECT_SPEC.md` and create the initial clean project skeleton.

Use:
- FastAPI backend
- PostgreSQL database
- SQLAlchemy and Alembic
- React + Vite frontend
- Docker Compose
- JWT authentication
- role-based access control
- AES-256-GCM with Python cryptography

Start with:
1. repository structure
2. backend FastAPI skeleton
3. database configuration
4. SQLAlchemy models for users, roles, permissions, KMS keys, key versions, and audit logs
5. basic routers for auth, IAM, KMS, and audit
6. `.env.example`
7. `docker-compose.yml`
8. basic README

Keep the first step runnable but minimal. Do not implement the full application in one pass.
```
