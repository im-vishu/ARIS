# ARIS — Production-Ready FastAPI Backend

ARIS is a scalable backend service built with FastAPI, PostgreSQL, Redis, and GitHub Actions CI/CD.  
It is designed for reliability, clean architecture, secure auth, and deployment readiness.

---

## ✨ Highlights

- ⚡ High-performance API with **FastAPI**
- 🔐 **JWT Authentication** (access + refresh token flow)
- 🗄️ **PostgreSQL + SQLAlchemy + Alembic** for robust data management
- 🚀 **Redis** for caching and performance support
- ✅ **Automated CI** with linting, migrations, tests, and coverage gate
- 🛡️ **Secret scanning** with Gitleaks
- 📦 Deployment workflow with post-deploy readiness checks
- 🩺 Health endpoints for monitoring (`/v1/health`, `/v1/ready`)

---

## 🧱 Tech Stack

### Core Backend
- **Python 3.12**
- **FastAPI** — async-ready, OpenAPI-native web framework
- **Pydantic** — data validation and settings management
- **Uvicorn** — ASGI server for local/prod runtime

### Data Layer
- **PostgreSQL 16** — primary relational database
- **SQLAlchemy 2.x** — ORM / database abstraction
- **Alembic** — schema versioning and migrations
- **psycopg 3** (`postgresql+psycopg://`) — PostgreSQL driver

### Performance & Infra
- **Redis 7** — cache / throttling / ephemeral state
- **Docker-based service containers in CI** (Postgres + Redis)

### Quality & Testing
- **Pytest** — unit/integration testing
- **pytest-cov** — coverage reporting with quality threshold
- **Ruff** — fast linting + code quality checks

### DevSecOps / CI-CD
- **GitHub Actions** — CI/CD pipelines
- **Gitleaks** — secrets detection
- Readiness-based deploy validation with retry strategy

---

## 📁 Project Structure

```text
ARIS/
├─ app/                          # Main application package
├─ alembic/                      # Migration scripts
├─ alembic.ini
├─ requirements.txt
├─ .github/
│  └─ workflows/
│     ├─ ci.yml                  # Lint + migrate + test + coverage + secret scan
│     └─ deploy.yml              # Deployment + health checks
└─ README.md
```

---

## ⚙️ Environment Configuration

Create `.env` (or configure platform secrets):

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

> Important: Use **psycopg v3 URL format**: `postgresql+psycopg://...`

---

## 🚀 Local Setup

### 1) Clone repository
```bash
git clone https://github.com/im-vishu/ARIS.git
cd ARIS
```

### 2) Create virtual environment

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/macOS**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4) Run DB migrations
```bash
alembic upgrade head
```

### 5) Start server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📚 API Documentation

When server is running:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## ✅ Quality Commands

```bash
# Lint
ruff check .

# Tests
pytest -q --maxfail=1 --disable-warnings

# Coverage gate
pytest -q --maxfail=1 --disable-warnings --cov=app --cov-report=term-missing --cov-fail-under=85
```

---

## 🔄 CI/CD Overview

### CI (`ci.yml`)
On `push` + `pull_request`:
1. Secret scan (Gitleaks)
2. Test job with Redis + Postgres services
3. Dependencies install
4. Alembic migration check
5. Ruff lint
6. Pytest + coverage threshold

### Deploy (`deploy.yml`)
- Trigger: push to `main` or manual dispatch
- Executes deployment step(s)
- Runs post-deploy readiness check:
  - `${HEALTHCHECK_URL}/v1/ready`
  - fallback to `${RENDER_EXTERNAL_URL}` if configured
- Retries before marking failure

---

## 🔐 Required GitHub Secrets

Set in **Settings → Secrets and variables → Actions**:

- `HEALTHCHECK_URL` (e.g., `https://your-api-domain.com`)
- `RENDER_EXTERNAL_URL` (optional fallback)
- Any provider-specific deploy secrets

---

## 🩺 Health Checks

- `GET /v1/health` → liveness probe
- `GET /v1/ready` → readiness probe (for deploy verification)

---

## 🏷️ Release Flow

```bash
git checkout main
git pull origin main
git tag vX.Y.Z
git push origin vX.Y.Z
```

If tag exists, increment version (`vX.Y.(Z+1)`).

---

## 🧯 Troubleshooting

### `HEALTHCHECK_URL secret is missing`
Add `HEALTHCHECK_URL` in repository GitHub Actions secrets.

### `ModuleNotFoundError: psycopg2`
Use psycopg v3 setup:
- Dependency: `psycopg[binary]`
- URL: `postgresql+psycopg://...`

### PowerShell script errors for `for ... do`
Those are bash commands. Use PowerShell syntax instead.

---

## 🤝 Contributing

1. Fork / create branch
2. Commit focused changes
3. Open PR
4. Ensure all CI checks pass

---

## 📄 License

Add `LICENSE` file (MIT/Apache-2.0/etc.) and update this section.