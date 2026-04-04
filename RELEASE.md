# ARIS Release & Rollback Guide

## Pre-release checklist
- [ ] `pytest -q` passes locally
- [ ] `ruff check .` passes
- [ ] `docker compose --env-file .env.dev up --build -d` passes
- [ ] `pwsh ./scripts/smoke_test.ps1` passes
- [ ] Secrets set for target env (`JWT_SECRET`, `OPENAI_API_KEY`, DB creds)
- [ ] Database backup taken (production only)

## Release steps
1. Pull latest code on deployment host
2. Build and start:
   - `docker compose --env-file .env.prod up --build -d`
3. Verify:
   - `GET /health` = `ok`
   - `GET /ready` = `ready`
   - smoke test script passes

## Rollback steps
1. Identify previous stable image/tag
2. Deploy previous image/tag
3. Re-run `docker compose up -d`
4. Verify `/health` and `/ready`
5. If schema changed incompatibly, restore DB from pre-release backup

## Operational checks after release
- Error logs are stable (no burst of 5xx)
- `/metrics-lite` errors_total not continuously increasing
- API latency is within expected range