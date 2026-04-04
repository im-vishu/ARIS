# 📘 ARIS API Contract

This document defines the API contract for ARIS to ensure consistent behavior between backend and clients.

> Base URL examples:  
> - Local: `http://localhost:8000`  
> - Production: `https://api.example.com`

---

## 🧭 1) Versioning & Base Path

- Current version: **v1**
- Base path: `/v1`
- Contract stability: non-breaking changes within major version

---

## 🔐 2) Authentication Contract

ARIS uses JWT-based authentication for protected endpoints.

### Auth scheme
- Type: `Bearer`
- Header format:
  ```http
  Authorization: Bearer <access_token>
  ```

### Token behavior
- Access token: short-lived
- Refresh token: longer-lived
- Expired/invalid token returns `401 Unauthorized`

---

## 📦 3) Standard Request Rules

- Content type for JSON endpoints:
  - `Content-Type: application/json`
- UTF-8 encoded payloads
- Unknown fields may be ignored or rejected (endpoint-specific)
- Validation errors return `422 Unprocessable Entity`

---

## 📤 4) Standard Response Rules

### Success envelope (recommended pattern)
```json
{
  "success": true,
  "data": {}
}
```

### Error envelope
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
```

> If your current implementation uses a different shape, keep implementation and docs aligned.

---

## 🚦 5) Health & Readiness Endpoints

## `GET /v1/health`
### Purpose
Liveness probe (service process is up)

### Success Response
- `200 OK`

Example:
```json
{
  "status": "ok"
}
```

---

## `GET /v1/ready`
### Purpose
Readiness probe (dependencies available: DB/Redis/etc.)

### Success Response
- `200 OK`

Example:
```json
{
  "status": "ready"
}
```

### Failure Response
- `503 Service Unavailable` (recommended)

Example:
```json
{
  "status": "not_ready",
  "dependencies": {
    "database": "down",
    "redis": "up"
  }
}
```

---

## ⚠️ 6) HTTP Status Code Contract

Common response codes:

- `200 OK` → success
- `201 Created` → resource created
- `204 No Content` → success without body
- `400 Bad Request` → malformed request
- `401 Unauthorized` → missing/invalid auth
- `403 Forbidden` → authenticated but not allowed
- `404 Not Found` → resource missing
- `409 Conflict` → duplicate/state conflict
- `422 Unprocessable Entity` → validation failure
- `429 Too Many Requests` → rate-limited
- `500 Internal Server Error` → server error
- `503 Service Unavailable` → dependency/unavailable service

---

## 🧾 7) Error Code Conventions

Use stable, machine-readable `error.code` values (examples):

- `AUTH_INVALID_TOKEN`
- `AUTH_TOKEN_EXPIRED`
- `VALIDATION_ERROR`
- `RESOURCE_NOT_FOUND`
- `CONFLICT`
- `RATE_LIMIT_EXCEEDED`
- `INTERNAL_ERROR`
- `SERVICE_UNAVAILABLE`

Clients should rely on `error.code` (not only text message).

---

## ⏱️ 8) Timeout, Retry, and Idempotency

- Clients should set request timeouts
- Safe retry for idempotent methods (`GET`, `PUT`, `DELETE`) when appropriate
- For `POST` create operations, use idempotency strategy where supported
- On `429/503`, retry with exponential backoff

---

## 🧮 9) Pagination Contract (for list endpoints)

Recommended query parameters:

- `page` (default: 1)
- `page_size` (default: 20, max: 100)
- `sort` (e.g. `created_at`, `-created_at`)

Recommended response fields:

```json
{
  "success": true,
  "data": [],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 125,
    "total_pages": 7
  }
}
```

---

## 🔎 10) Filtering & Searching (recommended)

For list endpoints, support:

- exact match: `?status=active`
- search query: `?q=keyword`
- date range: `?created_from=...&created_to=...`

All filters should be documented per endpoint.

---

## 🧷 11) Headers Contract

### Request headers
- `Authorization: Bearer <token>` (protected endpoints)
- `Content-Type: application/json`
- `X-Request-ID` (optional, recommended for tracing)

### Response headers (recommended)
- `X-Request-ID` for correlation
- `Deprecation` and `Sunset` for deprecated endpoints

---

## 🛡️ 12) Security Contract

- JWT tokens must be signed with configured algorithm
- Sensitive values must never be returned in responses
- Secrets must never appear in logs
- CORS policy should be environment-specific and restrictive in production
- Rate limiting behavior should return `429`

---

## 🔄 13) Backward Compatibility Rules

Within v1:

- ✅ allowed:
  - add optional response fields
  - add new endpoints
  - improve error messages (without changing `error.code` semantics)

- ❌ not allowed:
  - remove required fields
  - change field types
  - alter endpoint semantics unexpectedly

Breaking changes require new major API version.

---

## 📣 14) Deprecation Contract

When deprecating endpoint/field:

- announce with timeline
- provide replacement path
- preserve behavior during deprecation window
- include deprecation metadata when possible

See: `DEPRECATION_POLICY.md`

---

## 🧪 15) Contract Testing Requirements

For each endpoint, maintain tests for:

- success path
- auth failure path
- validation error path
- not-found/conflict path (where applicable)
- contract schema consistency

Recommended in CI:

- schema validation tests
- snapshot tests for critical responses

---

## 🧱 16) OpenAPI as Source of Truth

- Runtime OpenAPI docs available at:
  - `/docs`
  - `/openapi.json`
- Keep this file aligned with generated OpenAPI schema
- If mismatch occurs, OpenAPI + tested behavior wins, then update this file

---

## ✅ 17) Change Control for Contract Updates

Any contract change must include:

- PR with clear change summary
- impact assessment (clients affected)
- migration notes (if needed)
- updated tests/docs in same PR

---

## 📅 Last Updated

`2026-04-04`