# ARIS Incident Runbook v1

## Severity
- **SEV-1**: Full outage / data loss risk
- **SEV-2**: Major degradation
- **SEV-3**: Partial issue / workaround exists

## First 10 minutes checklist
1. Confirm alert validity (`/v1/ready`, logs, metrics).
2. Identify blast radius (all users vs subset).
3. Assign incident commander.
4. Stabilize:
   - rollback recent deploy if correlated
   - scale up service if resource saturation
5. Communicate status update.

## Diagnostics
- Health: `GET /v1/health`
- Readiness: `GET /v1/ready`
- Metrics: `GET /v1/metrics`
- Logs: filter by `x-request-id` / `request_id`

## Recovery actions
- Restart unhealthy pods/containers
- Rollback to last known good image tag
- Restore DB backup if corruption confirmed (last resort)

## Closure
- Declare resolved
- Create postmortem within 24h:
  - timeline
  - root cause
  - impact
  - action items with owners/dates