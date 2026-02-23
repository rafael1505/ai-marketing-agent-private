# Process Specification: Bug Fixing Workflow

**Spec ID**: `002-migrate-bug-fixing-workflow`
**Branch**: `002-migrate-dev-practices`
**Created**: 2026-02-23
**Status**: Active
**Supersedes**: `spec/process/bug-fixing-workflow.speckit.md` (legacy informal doc)
**Applies to**: Any change whose primary goal is to fix a defect — backend, frontend, or infrastructure.

---

## Purpose

Standardize how bugs are diagnosed, fixed, verified, and documented in the
AI Marketing Agent. Any contributor — human or AI agent — MUST follow this
workflow in its entirety before a bug fix is considered complete.

---

## 1. Core Rules (Non-Negotiable)

### BFIX-001 — Test-Driven Repair

Every bug fix MUST begin with a failing automated test that reproduces the defect.

- Write the test **before** writing the fix.
- The test MUST fail in the current codebase and pass after the fix is applied.
- If no existing test file covers the affected area, create one in the correct
  path (`tests/unit/`, `tests/integration/`, or `tests/frontend/`).
- A PR that fixes a bug without a corresponding test will not be approved.

### BFIX-002 — Root Cause Analysis

Before suggesting or writing a fix, the contributor (or AI agent) MUST document
the root cause of the bug.

- Explain **why** the bug occurred — the invariant that was violated, the
  assumption that was wrong, or the edge case that was not handled.
- The root cause MUST appear in the PR description or commit body. A one-line
  symptom description ("it returned null") is not sufficient.
- The analysis MUST trace the failure path from the observed symptom back
  through at least one of: frontend component → service → API endpoint →
  service layer → DB access.
- AI agents MUST NOT skip this step or proceed directly to code changes.

### BFIX-003 — Regression Check

After applying the fix, the full related test suite MUST be executed.

- Run `pytest` for any backend change. All previously passing tests MUST still
  pass.
- For frontend changes, run the frontend test suite under `tests/frontend/`.
- If any pre-existing test starts failing after the fix, the fix is incomplete
  and MUST NOT be merged until those failures are resolved.
- The regression check result (pass/fail) MUST be noted in the PR.

---

## 2. Docker Environment Integration

All testing activities MUST be compatible with the Docker Compose environment
described in `.cursor/rules/specify-rules.mdc`.

**Canonical test commands:**

```bash
# Ensure the environment is running before executing tests
docker compose up -d --wait          # Start all services (or use IDE task)

# Backend tests (inside container or from host with venv active)
pytest                               # Runs all tests from repo root

# Linting (must pass before opening a PR)
ruff check .

# Frontend tests
cd frontend && npm test              # Or the configured test script
```

**Rules:**
- BFIX-ENV-001: Tests MUST produce the same result whether run from the host
  (with the active Python venv) or inside the backend container. If they do not,
  the discrepancy MUST be documented.
- BFIX-ENV-002: Never test against a production or staging database. MongoDB
  MUST be the local container on port 27017.
- BFIX-ENV-003: If the "Start full development environment" IDE task is used to
  bring up the stack, the task MUST complete its health check before tests are run.

---

## 3. Full Workflow

### Step 1 — Reproduce

- Reproduce the bug reliably in the local Docker environment.
- For **backend** issues: capture API logs, `correlation_id`, and full stack trace
  from the container or uvicorn output (port 8088).
- For **frontend** issues: capture browser console errors, network tab failures,
  and the `correlation_id` from any `<AIErrorDisplay>` output (port 3001).
- Document the exact steps to reproduce — "it sometimes fails" is not a
  reproduction.

### Step 2 — Analyze (BFIX-002)

- Trace the failure path from the observed symptom back through the stack:
  - Frontend component (`frontend/src/components/`)
  - Frontend service/API client (`frontend/src/services/`)
  - API endpoint (`app/api/v1/endpoints/`)
  - Service layer (`app/services/`)
  - Database access (`app/db/`)
- Confirm which invariant from the project constitution or a feature spec is
  being violated.
- Document the root cause before writing a single line of fix code.

### Step 3 — Write a Failing Test (BFIX-001)

- Add or update a test in the correct path that reproduces the exact failure.
- Verify the test fails against the un-fixed codebase.
- Commit this test separately if practical (`test: add failing test for <issue>`).

### Step 4 — Design the Fix

The fix MUST respect all of the following:

| Concern             | Rule                                                                  |
|---------------------|-----------------------------------------------------------------------|
| Architecture        | Business logic stays in `app/services/`; routes stay thin.           |
| Database access     | Use global Motor `mongodb` instance in `app/db/` only.               |
| AI providers        | Database-driven via `ai_providers`. Never hardcode.                   |
| Error handling      | Return `error_details` with `correlation_id`; never raw exceptions.  |
| Frontend hooks      | All hooks at top of component; never in conditionals or loops.        |
| Frontend errors     | Use `<AIErrorDisplay>`; never `alert()`.                              |
| i18n                | Use `getTranslations()` from `@/i18n`; always add loading guard.     |
| Material lifecycle  | Never bypass the 3-stage pipeline (idea → refinement → finalization). |

### Step 5 — Implement

- Change only the modules necessary to fix the root cause.
- Do not refactor unrelated code in the same PR as a bug fix.
- Keep changes minimal and auditable.

### Step 6 — Run Regression Check (BFIX-003)

- Run `pytest` from repo root. Zero new failures allowed.
- Run `ruff check .`. Zero new linting errors allowed.
- For frontend fixes, run the frontend test suite.
- Confirm the test that was failing in Step 3 now passes.

### Step 7 — Document and Commit

- Commit message MUST use the `fix:` prefix (Conventional Commits).
- Commit body MUST include the root cause (one sentence minimum).
- If behavior or APIs changed, update `docs/` and the affected spec in the same PR.
- Reference the affected spec ID or constitution rule in the PR description.

---

## 4. Pre-Fix Checklist (Quick Reference)

Before writing any code, confirm all of the following:

- [ ] Bug is reproducible in the local Docker environment.
- [ ] Logs and `correlation_id` captured (backend) or console errors noted (frontend).
- [ ] Root cause identified and written down (BFIX-002).
- [ ] Failing test written and confirmed failing (BFIX-001).
- [ ] Fix design respects architecture, error handling, and i18n rules.

---

## 5. Acceptance Criteria

A bug fix is **complete** when ALL of the following are true:

- AC-001: A failing automated test exists that reproduces the defect (BFIX-001).
- AC-002: The root cause is documented in the PR description or commit body (BFIX-002).
- AC-003: `pytest` passes with zero new failures after the fix (BFIX-003).
- AC-004: `ruff check .` passes with zero new linting errors.
- AC-005: The fix respects all architecture, error handling, and i18n rules from
  the project constitution.
- AC-006: Documentation updated if behavior or APIs changed.

---

## Changelog

| Date       | Change                                                                  |
|------------|-------------------------------------------------------------------------|
| 2026-02-23 | Migrated from legacy informal doc; added BFIX-001 (Test-Driven Repair), |
|            | BFIX-002 (Root Cause Analysis), BFIX-003 (Regression Check), Docker     |
|            | environment integration, and full tabular fix-design rules.             |
