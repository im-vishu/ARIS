# ARIS API Contract (v1)

## Base
- Base path: `/v1`
- Content type: `application/json`
- Auth: `Authorization: Bearer <access_token>`

## Versioning policy
- Breaking changes require a new major path (`/v2`).
- Non-breaking additions (new optional fields/endpoints) stay in `/v1`.

## Standard response envelope

### Success
```json
{
  "data": {},
  "meta": {
    "request_id": "uuid-or-correlation-id"
  }
}