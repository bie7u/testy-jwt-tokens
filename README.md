# JWT HTTP-Only Cookies Authentication Demo

A full-stack demo application demonstrating JWT access + refresh token authentication using HTTP-only cookies.

## Architecture

```
backend/              Django 3.1.3 + djangorestframework-simplejwt 4.8.0  (port 8000)
frontend-intranet/    React – Staff / Intranet portal                      (port 3001)
frontend-customer/    React – Customer portal                              (port 3002)
```

### Key features
- **HTTP-only cookies** — access and refresh tokens are stored in HTTP-only cookies (not `localStorage`), preventing XSS token theft.
- **Token rotation** — on every refresh request a new access token is issued; refresh token rotation is configurable.
- **Staff-only intranet** — `require_staff=true` query parameter enforces staff login on the intranet frontend.
- **Diagnostic login** — a staff user can open a new browser tab logged in as any customer for diagnostic / support purposes, while retaining both identities server-side for audit logging.
- **One-time exchange codes** — diagnostic sessions use short-lived (60 s) single-use codes to transfer the customer JWT into the customer frontend; they are never exposed in logs or stored client-side.

---

## Quick Start (without Docker)

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_users   # creates test users
python manage.py runserver    # starts on port 8000
```

### 2. Frontend – Intranet (port 3001)

```bash
cd frontend-intranet
npm install
npm start   # PORT=3001
```

### 3. Frontend – Customer (port 3002)

```bash
cd frontend-customer
npm install
npm start   # PORT=3002
```

---

## Quick Start (Docker Compose)

```bash
docker-compose up --build
```

This will:
1. Start the Django backend on port 8000 (runs migrations + seed automatically).
2. Start the Intranet frontend on port 3001.
3. Start the Customer frontend on port 3002.

---

## Test Users (created by `seed_users`)

### Staff / Intranet users
| Username  | Password   | Role              |
|-----------|------------|-------------------|
| `admin`   | `admin123` | Superuser + staff |
| `staff1`  | `staff123` | Staff             |
| `staff2`  | `staff123` | Staff             |

### Customer users
| Username    | Password      |
|-------------|---------------|
| `customer1` | `customer123` |
| `customer2` | `customer123` |
| `customer3` | `customer123` |

---

## API Endpoints

All endpoints are under `http://localhost:8000/api/auth/`.

| Method | Path                 | Auth required | Description |
|--------|----------------------|---------------|-------------|
| POST   | `login/`             | No            | Login. Accepts `?require_staff=true` to enforce staff-only. Sets `access_token` + `refresh_token` HTTP-only cookies. |
| POST   | `logout/`            | Yes           | Clears JWT cookies. |
| POST   | `refresh/`           | No            | Uses `refresh_token` cookie to issue a new access token. |
| GET    | `me/`                | Yes           | Returns the current user's info. |
| GET    | `users/`             | Staff only    | Lists all active non-staff (customer) users. |
| POST   | `diagnostic-login/`  | Staff only    | Body: `{"customer_id": <id>}`. Creates a one-time exchange code. |
| POST   | `exchange/`          | No            | Body: `{"code": "<uuid>"}`. Exchanges a diagnostic code for customer JWT cookies + returns both user objects. |

---

## Diagnostic Login Flow

```
[Intranet (3001)]           [Backend (8000)]         [Customer Portal (3002)]
       |                           |                           |
       | POST /diagnostic-login/   |                           |
       |  { customer_id: 4 }       |                           |
       |-------------------------->|                           |
       |                           | create DiagnosticExchangeCode (TTL 60s, single-use)
       |<-- { code, customer } ----|                           |
       |                           |                           |
       | window.open("http://localhost:3002/?code=<uuid>")     |
       |------------------------------------------------------>|
       |                           |<-- POST /exchange/        |
       |                           |    { code: "<uuid>" }     |
       |                           |                           |
       |                           | mark code used            |
       |                           | set customer cookies      |
       |                           |-- { customer, staff, diagnostic:true } -->|
       |                           |                           |
       |                           |                  Show dashboard +
       |                           |                  diagnostic banner
```

Both the **customer token** and the **staff member's identity** are tracked during a diagnostic session, enabling full audit logging of which staff member performed which actions on behalf of which customer.

---

## Cookie Details

| Cookie          | HttpOnly | SameSite | Lifetime   |
|-----------------|----------|----------|------------|
| `access_token`  | ✅       | Lax      | 15 minutes |
| `refresh_token` | ✅       | Lax      | 7 days     |

Set `COOKIE_SECURE = True` and `COOKIE_SAMESITE = 'Strict'` in `backend/backend/settings.py` for production HTTPS deployments.

---

## Security Notes

### Django version

This project uses **Django 4.2.26** (the latest patched Django 4.2 LTS release).

`djangorestframework-simplejwt==4.8.0` has no upper-bound Django version constraint and is
fully compatible with Django 4.2.x — all 15 unit tests pass on this version.

### Other production hardening

- Set `COOKIE_SECURE = True` (HTTPS only)
- Set `COOKIE_SAMESITE = 'Strict'` (if single-domain)
- Replace `ALLOWED_HOSTS = ['*']` with your specific domain
- Rotate `SECRET_KEY` and store it in an environment variable
