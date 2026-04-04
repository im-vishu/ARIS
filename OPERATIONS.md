# ⚙️ ARIS Operations Runbook

This runbook explains how to operate ARIS safely across development, staging, and production.

---

## 🎯 1) Scope

Use this document for:

- 🚀 Deployment steps
- ✅ Post-deploy verification
- 📊 Monitoring expectations
- 🛟 Incident response
- 🔄 Rollback and recovery
- 🧰 Common failure playbooks

---

## 🧩 2) Service Overview

**ARIS** is a FastAPI backend with:

- 🗄️ **PostgreSQL** (primary datastore)
- ⚡ **Redis** (cache / transient state)
- 🔁 **Alembic** (migrations)
- 🤖 **GitHub Actions** (CI/CD)

Health endpoints:

- `GET /v1/health` → liveness
- `GET /v1/ready` → readiness

---

## 🌍 3) Environments

Recommended isolation model:

- 🧪 **dev** — local development
- 🧭 **staging** — pre-production validation
- 🏭 **prod** — live traffic

Each environment should have separate:

- Database
- Redis
- Secrets
- Base URL

---

## 🔐 4) Required Configuration

## 4.1 GitHub Actions Secrets

Repository → **Settings → Secrets and variables → Actions**

### ✅ Required
- `HEALTHCHECK_URL` (example: `https://api.example.com`)

### ➕ Optional fallback
- `RENDER_EXTERNAL_URL`

### 🔑 Platform-specific
- Any deploy provider tokens/keys

## 4.2 App Environment Variables

- `APP_ENV`
- `LOG_LEVEL`
- `DATABASE_URL` (`postgresql+psycopg://...`)
- `REDIS_URL`
- `JWT_SECRET`
- `JWT_ALG`
- `ACCESS_TOKEN_EXPIRE_MIN`
- `REFRESH_TOKEN_EXPIRE_MIN`
- `RATE_LIMIT_ENABLED`
- `RATE_LIMIT_PER_MINUTE`
- `CORS_ORIGINS`
- `ALLOWED_HOSTS`

---

## 🚀 5) Standard Deployment Procedure

## 5.1 Pre-Deploy Checklist

- [ ] `main` is stable and up to date
- [ ] CI checks are green
- [ ] migrations reviewed
- [ ] required secrets available
- [ ] rollback strategy ready

## 5.2 Deploy

Auto deploy on push to `main`:

```bash
git checkout main
git pull origin main
git push origin main
```

Manual deploy (GitHub CLI):

```bash
gh workflow run deploy.yml --ref main
```

## 5.3 Post-Deploy Verification

```bash
curl -i https://<base-url>/v1/health
curl -i https://<base-url>/v1/ready
```

Expected result: ✅ `HTTP 200` for both.

Also verify:

- no startup exceptions
- DB/Redis connections healthy
- error rate unchanged

---

## 🗃️ 6) Database Migration Operations

Apply migrations:

```bash
alembic upgrade head
```

Inspect state:

```bash
alembic current
alembic history --verbose
```

Rules:

- ⚠️ avoid destructive migrations without backup plan
- 🧪 test migration runtime in staging
- 🔁 keep releases backward compatible when possible

---

## 📈 7) Monitoring & Alerting Baseline

Track at minimum:

- API availability
- `/v1/ready` success rate
- 5xx errors
- latency (p95/p99)
- DB connection errors
- Redis timeout/errors
- auth failure spikes

Alert priorities:

- 🔴 **Critical**: service down, readiness failing, sustained 5xx spike
- 🟠 **High**: major degradation
- 🟡 **Medium**: non-critical job failures

---

## 🛟 8) Incident Response

## 8.1 Severity

- **SEV-1**: full outage / severe business impact
- **SEV-2**: major feature degradation
- **SEV-3**: minor degradation with workaround

## 8.2 Response Flow

1. 🧭 Acknowledge incident
2. 🧯 Stabilize service (rollback/mitigation)
3. 🔍 Find root cause
4. 🛠️ Fix + validate
5. 📝 Publish summary and action items

---

## 🔄 9) Rollback Procedure

If release is unhealthy:

1. Roll back to last known good deployment
2. Recheck:
   - `/v1/health`
   - `/v1/ready`
3. Confirm logs/metrics normalize
4. Pause further deploys until fix is ready

> Prefer forward-fix if DB rollback is unsafe.

---

## 🧰 10) CI/CD Failure Playbooks

## 10.1 `HEALTHCHECK_URL secret is missing`
**Cause:** missing secret  
**Fix:** add `HEALTHCHECK_URL` in Actions secrets

## 10.2 `ModuleNotFoundError: psycopg2`
**Cause:** psycopg driver mismatch  
**Fix:**
- dependency: `psycopg[binary]`
- URL: `postgresql+psycopg://...`

## 10.3 Migration step fails
Check:

- DB service readiness
- migration script validity
- correct `DATABASE_URL`
- schema drift

## 10.4 Readiness check times out
Check:

- app startup logs
- DB/Redis connectivity
- base URL correctness
- DNS/network/SSL setup

---

## 💻 11) Command Reference

### Git

```bash
git status
git pull origin main
git push origin main
git tag -l
git ls-remote --tags origin
```

### GitHub Actions (CLI)

```bash
gh run list
gh run watch
gh workflow run ci.yml --ref main
gh workflow run deploy.yml --ref main
```

### Health

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://<base-url>/v1/health
curl -s -o /dev/null -w "%{http_code}\n" https://<base-url>/v1/ready
```

---

## 🔒 12) Security Operations

- rotate secrets periodically
- never commit plaintext credentials
- keep secret scanning enabled
- enforce least-privilege access to prod secrets
- require PR review + passing CI on `main`

---

## 🧾 13) Change Management

For every production change:

- link PR/issue
- include migration impact
- include rollback note
- record deployed tag + commit SHA + timestamp
- verify health checks after deployment

---

## 👥 14) Ownership & Escalation

Maintain:

- primary on-call
- backup on-call
- escalation channel (Slack/Teams/email)
- hosting provider support route

---

## 🔁 15) Runbook Maintenance

Update this file whenever:

- deploy process changes
- secrets/config change
- health endpoint behavior changes
- incidents reveal missing procedures

---

**📅 Last reviewed:** `2026-04-04`