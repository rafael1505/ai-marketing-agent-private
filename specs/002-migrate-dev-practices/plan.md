# Implementation Plan: Process Spec Migration

**Branch**: `002-migrate-dev-practices` | **Date**: 2026-02-23 | **Status**: COMPLETED & MERGED  
**Merged into**: `main` (commit `0e7d9c4`) | **Merge date**: 2026-02-23

---

## Summary

Migrated three legacy informal process documents into high-performance Formal Process
Specs with enforceable rules, acceptance criteria, and changelogs. Resolved all
pre-merge sanity-check debt: port disambiguation, script organization, TypeScript
strict mode alignment, and agent context clarification.

This branch introduced **55 enforceable rules** across three process specs and **4
infrastructure improvements** — all now active on `main`.

---

## Technical Context

**Language/Version**: Python 3.11 (backend), Node 20 (frontend); Docker Compose V2 for orchestration.  
**Primary Dependencies**: FastAPI/uvicorn (backend), Next.js 14 (frontend), shadcn/ui, ruff (linter).  
**Storage**: MongoDB 4.4 (Docker container, port 27017).  
**Testing**: pytest (backend), frontend test framework in `tests/frontend/`.  
**Target Platform**: Local development on Linux/macOS/WSL; Cursor IDE.  
**Project Type**: Process documentation + infrastructure cleanup (no application runtime changes).

---

## Architectural Guidelines Applied

- **Single Source of Truth**: `.cursor/rules/specify-rules.mdc` is the canonical agent
  context file. Updated via `update-agent-context.sh cursor-agent` on each commit and
  enriched with a permanent `MANUAL ADDITIONS` process spec index.
- **Formal Spec Format**: Each migrated spec follows the same structure as
  `specs/001-dev-env-task-audit/spec.md` — purpose, enforceable rules, acceptance
  criteria, changelog.
- **No Runtime Changes**: All changes are documentation, configuration, and script
  organization. Zero changes to `app/` or `frontend/src/`.

---

## Scope of Work

### Spec 1 — Development Best Practices
**File**: `spec/process/development-best-practices.speckit.md`  
**Legacy**: 50 lines, 5 informal sections  
**New**: 175 lines, 7 sections, **26 enforceable rules**

Sections delivered:
1. Technology Stack (Canonical) — PR-STACK-001–004
2. File Organization — PR-ORG-001 + canonical path table
3. Backend Standards (Python 3.11 / FastAPI) — PR-BE-001–006
4. Frontend Standards (Next.js 14 / TypeScript) — PR-FE-001–008
5. Testing Requirements — PR-TEST-001–004
6. Git Protocol — PR-GIT-001–005
7. Agent Context Awareness — PR-AI-001–005 *(new section)*

### Spec 2 — Bug Fixing Workflow
**File**: `spec/process/bug-fixing-workflow.speckit.md`  
**Legacy**: 66 lines, 6-step checklist  
**New**: 191 lines, **3 mandatory core rules + 3 Docker env rules**

Rules delivered:
- BFIX-001: Test-Driven Repair — failing test MUST exist before fix code
- BFIX-002: Root Cause Analysis — cause MUST be documented; AI agents blocked from skipping
- BFIX-003: Regression Check — full `pytest` run; zero new failures; result noted in PR
- BFIX-ENV-001: Host/container test parity required or discrepancy documented
- BFIX-ENV-002: Always test against local MongoDB container (port 27017); never prod/staging
- BFIX-ENV-003: IDE task health check must complete before tests run

### Spec 3 — UX & Frontend Guidelines
**File**: `spec/process/ux-guidelines.speckit.md`  
**Legacy**: 56 lines, 4 loose sections  
**New**: 211 lines, **5 core rules + 5 React arch rules + 4 accessibility rules**

Rules delivered:
- UX-001: Visual Identity — explicit design tokens (typography scale, 5-role color
  palette, spacing values, shadow limits, border radius rules)
- UX-002: Component Consistency — shadcn/ui only; custom CSS forbidden unless 3 conditions met
- UX-003: Feedback Loops — Skeleton/Spinner for every async action; `<AIErrorDisplay>`
  with `correlation_id` for every error; mandatory recovery path (6 sub-rules)
- UX-004: i18n First — no hardcoded strings; `pages.<page>.<element>` key convention;
  both en+pt locale files as merge blocker (6 sub-rules)
- UX-005: Responsiveness — mobile-first; 44px touch targets; 3-breakpoint test requirement
- UX-ARCH-001–005: React architecture rules (hook ordering, functional components,
  custom hooks extraction, layout deduplication)
- UX-A11Y-001–004: WCAG 2.1 AA accessibility baseline

### Infrastructure Improvements (Pre-Merge Debt)
**Commit**: `c1f342b`

| Item | Change |
|------|--------|
| `scripts/start.sh` | Added 7-line port clarification comment (container:8000 → host:8088). Prevents agents from incorrectly patching the Docker binding. |
| `scripts/` → `debug/` | Moved 39 ad-hoc test/verify/fix/diagnose scripts per PR-ORG-001. `scripts/` root now contains only `start.sh` and `start-dev-env.sh`. |
| `.cursor/rules/specify-rules.mdc` | Annotated uvicorn command as "(local run, non-Docker only)". Added permanent MANUAL ADDITIONS index of all three process specs with their key rules. |
| `docker-compose.yml` | `TYPESCRIPT_STRICT` changed from `false` to `true` to enforce PR-FE-002 in the frontend container. |

---

## Commit History

| Commit | Type | Description |
|--------|------|-------------|
| `cba11fb` | docs | migrate development best practices to formal spec format |
| `9dc05be` | docs | formalize bug-fixing workflow with test-driven repair (BFIX-001) |
| `d65a697` | docs | finalize process migration with Apple-inspired UX guidelines |
| `c1f342b` | chore | address pre-merge debt — clarify ports, classify debug scripts, align TS strict |
| `0e7d9c4` | feat | merge commit into main |

---

## Files Changed

| File | Change |
|------|--------|
| `spec/process/development-best-practices.speckit.md` | Replaced (175 lines) |
| `spec/process/bug-fixing-workflow.speckit.md` | Replaced (191 lines) |
| `spec/process/ux-guidelines.speckit.md` | Replaced (211 lines) |
| `.cursor/rules/specify-rules.mdc` | Updated — process spec index in MANUAL ADDITIONS |
| `scripts/start.sh` | Updated — port clarification comment |
| `docker-compose.yml` | Updated — TYPESCRIPT_STRICT=true |
| `specs/002-migrate-dev-practices/plan.md` | Created (this file) |
| `specs/002-migrate-dev-practices/tasks.md` | Created (task completion record) |
| `scripts/*.sh` (39 files) | Renamed → `debug/` |

---

## Success Criteria — Met

- [x] SC-001: Any developer or AI agent can read the specs and unambiguously determine
  the correct language version, port, path, and style convention for any change.
- [x] SC-002: A PR violating any `PR-*`, `BFIX-*`, or `UX-*` rule is identifiable and
  correctable by a team member or AI agent without consulting the author.
- [x] SC-003: AI agent context file (`specify-rules.mdc`) permanently indexes all three
  process specs with rule summaries, making them visible on every agent interaction.
- [x] SC-004: Pre-merge sanity check passed — port disambiguation, script organization,
  TS strict mode, and agent context clarification all addressed before merge.
