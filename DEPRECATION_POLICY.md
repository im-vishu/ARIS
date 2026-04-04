# 🗓️ ARIS Deprecation Policy

This policy defines how ARIS deprecates APIs, features, and behaviors safely without breaking users unexpectedly.

---

## 🎯 1) Purpose

Goals of this policy:

- 🛡️ protect consumers from sudden breakage
- 📣 communicate change clearly and early
- 🔄 provide migration path with predictable timelines
- ✅ remove old behavior in a controlled way

---

## 📦 2) Scope

This policy applies to:

- REST API endpoints (`/v1/...`)
- request/response fields
- authentication behaviors
- configuration keys/environment variables
- SDK/client integration contracts (if applicable)

---

## 🧭 3) Versioning Principles

ARIS follows **Semantic Versioning**:

- 💥 **MAJOR**: breaking changes
- ✨ **MINOR**: backward-compatible additions
- 🩹 **PATCH**: bug fixes and non-breaking improvements

### Rule of thumb
- Deprecation starts in a **minor** release
- Removal happens in a **future major** release (preferred), or after policy timeline

---

## ⏳ 4) Standard Deprecation Timeline

Default timeline (unless security/legal urgency requires shorter):

1. **Announce Deprecation** 📣  
   - in release notes/changelog/docs
   - include replacement and migration steps

2. **Deprecation Active** ⚠️ (minimum 90 days)
   - old behavior still works
   - warnings returned/logged

3. **Sunset / Removal** 🧹
   - old behavior removed on announced date/version
   - support docs updated

> Recommended minimum notice: **90 days** for public API changes.

---

## 🧾 5) Communication Requirements

Every deprecation must include:

- what is deprecated
- why it is deprecated
- replacement path
- effective date
- removal date/version
- migration examples
- support contact/channel

Communication channels:

- release notes
- README/API docs
- changelog
- issue/announcement (if high impact)

---

## 🌐 6) API Deprecation Rules

## 6.1 Endpoint Deprecation
When deprecating an endpoint:

- keep endpoint functional during deprecation window
- add clear warnings in docs
- if possible, return deprecation headers:
  - `Deprecation: true`
  - `Sunset: <RFC-1123 date>`
  - `Link: <migration-doc-url>; rel="deprecation"`

## 6.2 Field Deprecation
For request/response field deprecations:

- do not remove immediately
- mark field as deprecated in OpenAPI/docs
- support old + new fields during transition
- define exact removal release/date

## 6.3 Behavior Changes
For semantic behavior changes:

- ship opt-in toggle/flag first when possible
- document before/after behavior
- provide test examples for migration

---

## 🔐 7) Urgent Exceptions

A shorter deprecation window may be used only for:

- active security vulnerabilities
- legal/compliance requirements
- critical reliability risks

In such cases:

- announce reason explicitly
- provide mitigation steps
- prioritize customer communication

---

## 🧪 8) Implementation Checklist

Before announcing deprecation:

- [ ] replacement exists and is documented
- [ ] migration guide drafted
- [ ] timeline approved
- [ ] telemetry exists to measure usage of old path
- [ ] support team informed

Before removal:

- [ ] usage of deprecated feature reviewed
- [ ] reminders sent
- [ ] final release note prepared
- [ ] rollback strategy confirmed

---

## 📊 9) Monitoring During Deprecation

Track:

- deprecated endpoint hit count
- deprecated field usage percentage
- errors after migration
- top affected clients

Removal should proceed only when usage is sufficiently low or timeline is reached.

---

## 🛠️ 10) Example Deprecation Notice Template

```markdown
## ⚠️ Deprecation Notice: `GET /v1/old-endpoint`

- **Deprecated on:** 2026-04-04
- **Sunset on:** 2026-07-04
- **Replacement:** `GET /v1/new-endpoint`
- **Why:** Improved performance and consistent response schema.
- **Migration guide:** https://<your-docs>/migrations/old-to-new
```

---

## 🔄 11) Removal Procedure

On removal date/version:

1. remove deprecated code path
2. update OpenAPI/docs/examples
3. update tests and CI references
4. publish release notes with removal summary
5. monitor error rates and client feedback closely

---

## 👥 12) Roles & Responsibilities

- **API Owner**: proposes and drives deprecation
- **Engineering Lead**: approves timeline and risk
- **DevOps/Ops**: monitors impact during rollout
- **Support/Comms**: handles user notifications and migration support

---

## ✅ 13) Policy Compliance

No breaking API removal should occur unless:

- notice period completed **or** urgent exception documented
- migration path provided
- communication obligations fulfilled
- approval recorded by engineering owner

---

## 📅 Last Updated

`2026-04-04`