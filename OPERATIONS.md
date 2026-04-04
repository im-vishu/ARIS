# ARIS Operations Guide (Phase 3.3)

## 1) Deployment

### Trigger modes
- Manual: GitHub Actions → **Deploy** workflow (`workflow_dispatch`)
- Automatic: push tag matching `v*` (example: `v3.3.0`)

### Required GitHub Environment Secret
- `HEALTHCHECK_URL`  
  Example: `https://api.yourapp.com`

### Post-deploy gate
The workflow checks:
- `GET {HEALTHCHECK_URL}/ready` must return HTTP `200`.

If not healthy after retries, deployment job fails.

---

## 2) Monitoring

## Prometheus
Use `deploy/prometheus.yml` and `deploy/alerts.yml`.

Expected target:
- `aris-api:8000/metrics`

## Grafana
Import:
- `deploy/grafana_dashboard.json`

Dashboard includes:
- Requests/sec
- Errors/sec
- p95 latency

---

## 3) Backup and Restore

## Backup
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\backup_postgres.ps1
```

## Restore
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\restore_postgres.ps1 -BackupFile .\backup_aris_YYYYMMDD_HHMMSS.sql
```

After restore:
1. Run smoke test
2. Validate `/ready`
3. Validate key business endpoints

---

## 4) Runtime recommendations
- Keep at least 2 app replicas in production.
- Use rolling deploys (no downtime).
- Set container restart policy to `unless-stopped` or equivalent.
- Keep `JWT_SECRET` and `OPENAI_API_KEY` only in secret manager / CI secrets.
- Never commit real secrets in repo.