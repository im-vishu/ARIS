# 🚀 ARIS Release Guide

This guide defines the official release process for ARIS so every release is safe, traceable, and repeatable.

---

## 🎯 1) Release Policy

ARIS follows **Semantic Versioning**:

- 💥 `MAJOR` (`vX.0.0`) → breaking changes
- ✨ `MINOR` (`vX.Y.0`) → backward-compatible features
- 🩹 `PATCH` (`vX.Y.Z`) → fixes/improvements

Example: `v5.0.0 → v5.0.1 → v5.0.2`

---

## 🌿 2) Branch Strategy

- `main` = stable and deployable
- feature branches = development work
- merge to `main` only after CI ✅

Recommended branch protection on `main`:

- required PR review
- required passing checks
- block force push

---

## ✅ 3) Release Readiness Checklist

Before release:

- [ ] all target PRs merged to `main`
- [ ] CI workflow passing
- [ ] deploy workflow passing
- [ ] migrations verified
- [ ] `/v1/health` returns 200
- [ ] `/v1/ready` returns 200
- [ ] release notes prepared

---

## 🛠️ 4) Standard Release Steps

## 4.1 Sync with remote

```bash
git checkout main
git pull origin main
```

## 4.2 Verify state

```bash
git status
git log --oneline -n 5
```

## 4.3 Create and push tag

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

If tag already exists, create next version (`vX.Y.(Z+1)`).

---

## 📦 5) Deployment Verification

After release/deploy:

```bash
curl -i https://<base-url>/v1/health
curl -i https://<base-url>/v1/ready
```

Success criteria:

- both endpoints return ✅ `HTTP 200`
- no critical errors in logs
- no 5xx spike
- key APIs respond as expected

---

## 🤖 6) GitHub Actions Validation

Check:

- CI workflow ✅
- Deploy workflow ✅
- Post-deploy healthcheck ✅

With GitHub CLI:

```bash
gh run list
gh run watch
```

---

## 📝 7) Release Notes Format

For each release, record:

- version
- date
- commit SHA
- included changes
- migration impact
- rollback notes

Template:

```markdown
## vX.Y.Z - YYYY-MM-DD
### ✨ Added
- ...

### 🔧 Changed
- ...

### 🐛 Fixed
- ...

### ⚠️ Notes
- Migration required: Yes/No
- Rollback impact: Low/Medium/High
```

---

## 🚑 8) Hotfix Release Process

Use for urgent production fixes:

1. branch from `main`
2. apply minimal fix
3. run CI
4. merge to `main`
5. tag next patch version
6. deploy + verify health endpoints

---

## 🔄 9) Rollback Plan

If a release is unhealthy:

1. rollback to last known good deployment
2. verify:
   - `/v1/health`
   - `/v1/ready`
3. monitor logs and metrics stabilization
4. create follow-up fix release

> Prefer forward-fix when DB rollback is unsafe.

---

## 🏷️ 10) Tag Rules

- do not reuse release tags for different commits
- avoid deleting old release tags unless absolutely necessary
- keep release history auditable

Useful commands:

```bash
git tag -l
git ls-remote --tags origin
```

---

## 🧰 11) Common Release Errors

## ❌ Error: `fatal: tag 'vX.Y.Z' already exists`
**Fix:** create next version tag.

```bash
git tag vX.Y.(Z+1)
git push origin vX.Y.(Z+1)
```

## ❌ Error: `HEALTHCHECK_URL secret is missing`
**Fix:** add `HEALTHCHECK_URL` in GitHub Actions secrets.

## ❌ Error: psycopg driver mismatch
**Fix:**
- install `psycopg[binary]`
- set DB URL to `postgresql+psycopg://...`

---

## 📋 12) Copy/Paste Release Checklist

```markdown
- [ ] main synced
- [ ] all release PRs merged
- [ ] CI green
- [ ] deploy green
- [ ] health checks pass
- [ ] release notes done
- [ ] tag created and pushed
- [ ] release announced
```

---

## 👤 13) Release Owner Responsibilities

Release owner must:

- drive checklist completion
- approve final version/tag
- validate production health
- publish release notes
- coordinate rollback if needed

---

## 📅 Last Updated

`2026-04-04`