# ARIS Deprecation Policy

## Scope
This policy governs deprecation/removal of API routes and response fields.

## Current deprecations
Legacy unversioned endpoints are deprecated:

- `/health`
- `/ready`
- `/metrics-lite`
- `/metrics`
- `/auth/token`
- `/auth/refresh`
- `/auth/logout`
- `/chat`
- `/chat/history`

Use `/v1/*` equivalents instead.

## Headers for deprecated routes
Deprecated endpoints return:

- `Deprecation: true`
- `Sunset: Wed, 31 Dec 2026 23:59:59 GMT`
- `Link: </docs/DEPRECATION_POLICY.md>; rel="deprecation"`

## Timeline
1. **Deprecation announced**: now
2. **Migration window**: until sunset date
3. **Removal**: first release after sunset

## Consumer requirements
- Migrate all clients/tests to `/v1/*`.
- Treat any use of deprecated route as technical debt to remove before sunset.

## Backward compatibility promise
- `/v1` contract is stable for this major version.
- Breaking changes require `/v2`.