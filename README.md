# ARIS — Scalable FastAPI Backend

ARIS is a production-focused backend built with FastAPI, PostgreSQL, Redis, and GitHub Actions CI/CD.  
It follows a clean, modular architecture designed for maintainability, testing, and reliable deployments.

---

## ✨ Key Features

- Fast, async-ready REST API with **FastAPI**
- Secure **JWT authentication** (access + refresh)
- Structured data layer with **SQLAlchemy + Alembic**
- **PostgreSQL** for durable storage
- **Redis** for caching / performance support
- Automated CI pipeline (lint, migrate, test, coverage)
- Deployment health verification with readiness checks
- Secret scanning with Gitleaks

---

## 🧱 Tech Stack

### Backend
- Python 3.12
- FastAPI
- Pydantic
- Uvicorn

### Data
- PostgreSQL 16
- SQLAlchemy 2.x
- Alembic
- psycopg 3 (`postgresql+psycopg://`)

### Caching & Infra
- Redis 7
- Docker service containers in CI

### Quality & DevOps
- Pytest + pytest-cov
- Ruff
- GitHub Actions
- Gitleaks

---

## 🗂️ Project Structure (Improved)

```text
ARIS/
├─ app/
│  ├─ api/                      # Route definitions (versioned endpoints)
│  │  └─ v1/
│  │     ├─ endpoints/          # Feature-specific route modules
│  │     └─ router.py           # v1 API router aggregation
│  ├─ core/                     # Core settings and security
│  │  ├─ config.py              # App configuration / env loading
│  │  ├─ security.py            # JWT, password/hash helpers
│  │  └─ logging.py             # Logging setup
│  ├─ db/                       # Database layer
│  │  ├─ base.py                # SQLAlchemy Base metadata
│  │  ├─ session.py             # Session/engine management
│  │  └─ models/                # ORM models
│  ├─ schemas/                  # Pydantic request/response schemas
│  ├─ services/                 # Business logic layer
│  ├─ repositories/             # Data access abstraction
│  ├─ dependencies/             # Shared FastAPI dependencies
│  ├─ utils/                    # Utility helpers
│  └─ main.py                   # FastAPI app entrypoint
│
├─ alembic/                     # Migration versions and env
│  ├─ versions/
│  └─ env.py
├─ tests/                       # Unit/integration tests
│  ├─ unit/
│  ├─ integration/
│  └─ conftest.py
├─ scripts/                     # Local utility scripts (seed/check/run)
├─ .github/
│  └─ workflows/
│     ├─ ci.yml                 # CI: scan + lint + migrate + tests
│     └─ deploy.yml             # Deploy + readiness healthcheck
├─ requirements.txt
├─ alembic.ini
├─ .env.example                 # Safe env template (no secrets)
├─ README.md
└─ LICENSE
```

> If some folders are not yet present, this is the recommended target layout as the project grows.

---

## ⚙️ Environment Variables

Create `.env` from `.env.example`:

```env
APP_ENV=dev
LOG_LEVEL=INFO

JWT_SECRET=change-this-to-a-long-random-secret
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRE_MIN=30
REFRESH_TOKEN_EXPIRE_MIN=10080

RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

OPENAI_API_KEY=your_openai_key_if_used
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql+psycopg://aris:aris@localhost:5432/aris

CORS_ORIGINS=http://localhost:3000
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 🚀 Quick Start

```bash
git clone https://github.com/im-vishu/ARIS.git
cd ARIS
python -m venv .venv
# activate venv (OS-specific)
python -m pip install --upgrade pip
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs:
- `/docs`
- `/redoc`

---

## ✅ Development Commands

```bash
ruff check .
pytest -q --maxfail=1 --disable-warnings
pytest -q --maxfail=1 --disable-warnings --cov=app --cov-report=term-missing --cov-fail-under=85
```

---

## 🔄 CI/CD

### CI (`.github/workflows/ci.yml`)
- Secret scan (Gitleaks)
- Postgres + Redis service containers
- Migrations (`alembic upgrade head`)
- Lint (`ruff check .`)
- Tests with coverage threshold

### Deploy (`.github/workflows/deploy.yml`)
- Triggered on `main` (or manual dispatch)
- Runs deployment steps
- Performs readiness check with retry:
  - `${HEALTHCHECK_URL}/v1/ready`
  - fallback to `${RENDER_EXTERNAL_URL}`

---

## 🩺 Health Endpoints

- `GET /v1/health` → service alive
- `GET /v1/ready` → dependencies ready

---

## 🔐 Required GitHub Secrets

- `HEALTHCHECK_URL` (recommended)
- `RENDER_EXTERNAL_URL` (optional fallback)
- provider-specific deploy secrets

---

## 🏷️ Versioning

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

Use semantic versioning and increment for each release.

---

## 🤝 Contributing

1. Create a feature branch
2. Keep commits small and clear
3. Open PR to `main`
4. Ensure all CI checks pass

---

## 📄 License

Choose a license (MIT/Apache-2.0) and include `LICENSE`.