# 🚨 ARIS Incident Runbook

This runbook provides a clear process to detect, triage, mitigate, resolve, and review production incidents for ARIS.

---

## 🎯 1) Purpose

Use this document when:

- API is down or unstable
- error rate spikes
- deployment causes regressions
- DB/Redis dependencies fail
- authentication or critical flows break

Goals:

- 🛟 restore service quickly
- 📣 communicate clearly
- 🔍 identify root cause
- ✅ prevent repeat incidents

---

## 🧭 2) Severity Levels

## 🔴 SEV-1 (Critical)
- Full outage or severe customer impact
- Core API unavailable
- Data integrity/security risk

**Target:** immediate response, fastest mitigation

## 🟠 SEV-2 (High)
- Major feature degraded
- Elevated 5xx/latency impacting many users

**Target:** urgent response, mitigation within same window

## 🟡 SEV-3 (Medium)
- Limited impact, workaround exists
- Non-critical degradation

**Target:** resolve in normal priority window

---

## 👥 3) Incident Roles

- **Incident Commander (IC)** 🧑‍✈️  
  Owns coordination, decisions, timeline updates

- **Ops/Infra Lead** ⚙️  
  Handles deploy, rollback, platform/runtime checks

- **App Lead** 🧠  
  Debugs application logic, dependencies, hotfixes

- **Comms Lead** 📣  
  Posts stakeholder/customer updates

> In small teams, one person may hold multiple roles.

---

## ⏱️ 4) Response Timeline

## 0–5 min: Acknowledge & Triage
- confirm incident scope
- assign SEV level
- open incident channel/thread
- assign IC

## 5–15 min: Stabilize
- rollback/mitigate quickly
- disable risky path/feature flag if available
- reduce blast radius

## 15–60 min: Diagnose & Fix
- identify root cause candidate
- apply minimal safe fix
- validate with health/readiness checks

## 60+ min: Recover & Monitor
- ensure metrics stable
- confirm user impact resolved
- prepare postmortem

---

## 🧪 5) First Response Checklist

- [ ] Confirm incident is real (not false alarm)
- [ ] Check latest deployment/workflow status
- [ ] Check `/v1/health` and `/v1/ready`
- [ ] Review app logs for startup/runtime errors
- [ ] Review DB connectivity and migration status
- [ ] Review Redis availability/timeouts
- [ ] Decide mitigate now vs fix forward

---

## 🔍 6) Quick Diagnostic Commands

## Health checks
```bash
curl -i https://<base-url>/v1/health
curl -i https://<base-url>/v1/ready
```

## GitHub Actions
```bash
gh run list
gh run watch
```

## Git status (release context)
```bash
git log --oneline -n 10
git tag -l
```

---

## 🧰 7) Common Incident Playbooks

## 7.1 ❌ `HEALTHCHECK_URL secret is missing`
**Symptoms:** deploy fails in post-deploy check  
**Action:**
1. Add `HEALTHCHECK_URL` in GitHub Actions secrets
2. Re-run deploy workflow
3. Verify readiness endpoint

---

## 7.2 ❌ DB driver mismatch (`psycopg2` vs `psycopg`)
**Symptoms:** import/module errors during boot/migration  
**Action:**
1. Ensure dependency includes `psycopg[binary]`
2. Ensure `DATABASE_URL` uses `postgresql+psycopg://...`
3. Re-run CI/deploy

---

## 7.3 ❌ Migration failure
**Symptoms:** app fails on startup or migration step fails  
**Action:**
1. Run `alembic current` / `alembic history --verbose`
2. Validate DB URL and credentials
3. Check for broken/partial migration
4. Rollback deploy or apply forward-fix migration

---

## 7.4 ❌ Readiness check timeout
**Symptoms:** `/v1/ready` not returning 200  
**Action:**
1. inspect startup logs
2. verify DB/Redis connectivity
3. verify env vars/secrets loaded
4. confirm route path and base URL
5. rollback if unresolved quickly

---

## 7.5 ❌ Elevated 5xx after release
**Symptoms:** error spike immediately post deploy  
**Action:**
1. compare latest release diff
2. rollback to last known good version
3. reproduce issue in staging
4. prepare patch release

---

## 🔄 8) Rollback Procedure (Fast)

1. Roll back to last known stable deployment
2. Validate:
   - `/v1/health` ✅
   - `/v1/ready` ✅
3. Monitor 10–15 minutes:
   - 5xx rate normal
   - latency normal
   - logs clean
4. Communicate rollback completed
5. Open follow-up issue/postmortem

---

## 📣 9) Communication Templates

## Internal update
```text
[INCIDENT][SEV-X] ARIS API degradation detected.
Impact: <what users see>
Start Time: <UTC>
Current Status: Investigating / Mitigating / Resolved
Next Update: <time>
Owner: <name>
```

## Resolved update
```text
[RESOLVED][SEV-X] ARIS incident resolved.
Root Cause: <short summary>
Mitigation: <rollback/hotfix>
User Impact Window: <start-end UTC>
Follow-up: Postmortem and preventive actions in progress.
```

---

## 🧾 10) Postmortem Requirements

For SEV-1/SEV-2 incidents, publish a postmortem within 24–48h including:

- timeline (UTC)
- impact summary
- root cause
- detection gaps
- what worked / what failed
- corrective actions with owners + due dates

---

## ✅ 11) Exit Criteria (Incident Closed)

- [ ] service stable
- [ ] health/readiness green
- [ ] no abnormal error/latency trend
- [ ] stakeholders updated
- [ ] follow-up tasks filed
- [ ] postmortem scheduled/published

---

## 🔐 12) Security Incidents (Special Handling)

If incident involves possible data leak, credential exposure, or unauthorized access:

1. rotate secrets immediately
2. restrict affected access paths
3. preserve forensic logs/evidence
4. escalate to security owner
5. follow legal/compliance notification process

---

## 🗂️ 13) Ownership & Escalation

Maintain an up-to-date section (customize for your team):

- Primary on-call: `<name>`
- Secondary on-call: `<name>`
- Escalation channel: `<Slack/Teams/email>`
- Hosting support link: `<provider support URL>`

---

## 📅 Last Reviewed

`2026-04-04`