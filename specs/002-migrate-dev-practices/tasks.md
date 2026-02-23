# Task List: Process Spec Migration (002-migrate-dev-practices)

**Branch**: `002-migrate-dev-practices`  
**Merged**: 2026-02-23 → `main` (commit `0e7d9c4`)  
**Status**: ALL TASKS COMPLETED  

**Total Tasks**: 62  
**Completed**: 62 / 62 (100%)

---

## Phase 1 — Development Best Practices Spec

### Stack & Ports

- [x] **T-001** — Define canonical technology stack table (Python 3.11, Next.js 14, MongoDB 4.4, Docker Compose V2)
- [x] **T-002** — PR-STACK-001: Document minimum version constraints (Python ≥ 3.11, Next.js ≥ 14)
- [x] **T-003** — PR-STACK-002: Lock ports 8088 (backend), 3001 (frontend), 27017 (MongoDB) as fixed
- [x] **T-004** — PR-STACK-003: Mandate `docker compose` (V2 plugin); prohibit legacy `docker-compose`
- [x] **T-005** — PR-STACK-004: Mandate database-driven AI providers via `ai_providers` collection; prohibit hardcoding

### File Organization

- [x] **T-006** — PR-ORG-001: Define canonical path table for all content types (14 paths)
- [x] **T-007** — PR-ORG-001: Enforce `debug/` as the path for debug scripts; move 39 ad-hoc scripts from `scripts/`

### Backend Standards

- [x] **T-008** — PR-BE-001: Mandate PEP 8 + `ruff check .`; all linting warnings resolved before PR
- [x] **T-009** — PR-BE-002: Require type hints and docstrings on all functions and methods
- [x] **T-010** — PR-BE-003: Business logic in `app/services/` only; route handlers must be thin
- [x] **T-011** — PR-BE-004: All DB access uses global Motor `mongodb` instance from `app/db/`; no new client instantiation
- [x] **T-012** — PR-BE-005: Error responses must include `error_details` with `correlation_id` and i18n user message
- [x] **T-013** — PR-BE-006: Document canonical local run command (`uvicorn --host 127.0.0.1 --port 8088 --reload`)

### Frontend Standards

- [x] **T-014** — PR-FE-001: Clean Code for TypeScript; functions do one thing; files under 300 lines
- [x] **T-015** — PR-FE-002: Prohibit `any`; all types from `@/types` or declared inline; `TYPESCRIPT_STRICT=true` in Docker
- [x] **T-016** — PR-FE-003: React functional components only; class components forbidden
- [x] **T-017** — PR-FE-004: All hooks at top of component function; never inside conditionals, loops, or after early returns
- [x] **T-018** — PR-FE-005: `shadcn/ui` as the only component library; no new library dependencies without spec
- [x] **T-019** — PR-FE-006: `getTranslations()` from `@/i18n` only; prohibit `next-intl` import; loading guard required
- [x] **T-020** — PR-FE-007: Prohibit `alert()`; all errors via `<AIErrorDisplay>` with `error_details` and `correlation_id`
- [x] **T-021** — PR-FE-008: All API access in `frontend/src/services/`; components must not call `fetch` or `axios` directly

### Testing Requirements

- [x] **T-022** — PR-TEST-001: Every non-trivial change requires automated tests; PR blocked without them
- [x] **T-023** — PR-TEST-002: Bug fixes must add/update a test that fails before fix and passes after
- [x] **T-024** — PR-TEST-003: Python tests use `pytest`; run from repo root
- [x] **T-025** — PR-TEST-004: Frontend tests in `tests/frontend/`; framework documented in `docs/`

### Git Protocol

- [x] **T-026** — PR-GIT-001: Conventional Commits enforced (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `ci:`)
- [x] **T-027** — PR-GIT-002: Plain professional English in commit messages; no emojis in commits or branch names
- [x] **T-028** — PR-GIT-003: Feature-branch workflow; naming convention `<id>-<short-slug>`; no direct commits to `main`
- [x] **T-029** — PR-GIT-004: Small, focused commits; no "kitchen sink" commits mixing unrelated changes
- [x] **T-030** — PR-GIT-005: Documentation updated in the same PR as the behavior or API change

### Agent Context Awareness

- [x] **T-031** — PR-AI-001: AI agents must read `.cursor/rules/specify-rules.mdc` before writing any code
- [x] **T-032** — PR-AI-002: AI agents must check `specs/<id>-<slug>/spec.md` before coding; use `/speckit.specify` if absent
- [x] **T-033** — PR-AI-003: AI agents must not infer stack or port values from context; use `specify-rules.mdc` only
- [x] **T-034** — PR-AI-004: AI agents must not create root files, add dependencies, or change ports without a spec reference
- [x] **T-035** — PR-AI-005: AI agents must run `ReadLints` / `ruff check .` after every task and fix introduced violations

---

## Phase 2 — Bug Fixing Workflow Spec

### Core Rules

- [x] **T-036** — BFIX-001: Every bug fix must begin with a failing automated test that reproduces the defect
- [x] **T-037** — BFIX-001: Failing test must be verified against un-fixed codebase before writing any fix code
- [x] **T-038** — BFIX-001: PR blocked without corresponding test; no exceptions
- [x] **T-039** — BFIX-002: Root cause (not symptom) must be documented before any fix code is written
- [x] **T-040** — BFIX-002: Root cause must appear in PR description or commit body; one-line symptom is insufficient
- [x] **T-041** — BFIX-002: AI agents explicitly blocked from skipping root cause analysis and proceeding to code
- [x] **T-042** — BFIX-003: Full `pytest` run required after fix; zero new failures allowed
- [x] **T-043** — BFIX-003: `ruff check .` must pass after fix; zero new linting errors
- [x] **T-044** — BFIX-003: Regression check result (pass/fail) must be noted in the PR

### Docker Environment Rules

- [x] **T-045** — BFIX-ENV-001: Tests must produce identical results on host and inside container; discrepancies must be documented
- [x] **T-046** — BFIX-ENV-002: Tests always run against local MongoDB container (port 27017); never against prod or staging
- [x] **T-047** — BFIX-ENV-003: IDE task health check must complete (`docker compose up -d --wait`) before tests run

### Workflow & Fix Design Table

- [x] **T-048** — Document 7-step workflow (Reproduce → Analyze → Failing Test → Design Fix → Implement → Regression Check → Commit)
- [x] **T-049** — Define fix-design table mapping 8 architecture concerns to their specific rules
- [x] **T-050** — Define 4-item pre-fix checklist (quick reference) and 6 formal acceptance criteria

---

## Phase 3 — UX & Frontend Guidelines Spec

### Core UX Rules

- [x] **T-051** — UX-001: Define Apple-inspired design tokens — typography scale (4 weights, 5 sizes), 5-role color palette, spacing values (`p-6`, `px-4 sm:px-6 lg:px-8`), shadow limits (`shadow-sm` for cards, `shadow-xl` for modals), border radius rules
- [x] **T-052** — UX-002a: `shadcn/ui` mandatory for all interactive elements; no custom equivalents
- [x] **T-053** — UX-002b: Custom CSS forbidden unless 3 conditions met (not achievable with Tailwind, documented in JSDoc, reviewed in PR)
- [x] **T-054** — UX-002c/d: No additional component libraries; no `!important` overrides of shadcn variants
- [x] **T-055** — UX-003a: Data-fetching components must show `Skeleton` while loading; no empty/partial UI
- [x] **T-056** — UX-003b: Async-action buttons must show `Spinner` in-flight and disable to prevent double-submission
- [x] **T-057** — UX-003c: Page-level loading uses `<LoadingState />` as full-page placeholder
- [x] **T-058** — UX-003d/e: Every async error via `<AIErrorDisplay>` with `correlation_id`; generate client-side UUID if backend omits it
- [x] **T-059** — UX-003f: Every recoverable error must offer an actionable recovery path; dead-end error screens prohibited
- [x] **T-060** — UX-004a–f: No hardcoded UI strings; `getTranslations()` exclusively; `pages.<page>.<element>` key convention; loading guard required; backend `user_message` keys resolved on frontend; both en+pt locale files updated in same PR
- [x] **T-061** — UX-005a–e: Mobile-first layouts; no fixed pixel widths; 44px minimum touch targets; `overflow-x-auto` on tables; 3-breakpoint test (375px / 768px / 1280px)

### React Architecture & Accessibility

- [x] **T-062** — UX-ARCH-001–005: Hook ordering rules; functional components only; shared logic in `frontend/src/hooks/`; no layout duplication across pages
- [x] **T-063** — UX-A11Y-001–004: WCAG 2.1 AA contrast ratios; keyboard navigation + visible focus rings; `alt`/`aria-label` on images and icon buttons; ARIA live regions for dynamic content

---

## Phase 4 — Infrastructure & Agent Context

- [x] **T-064** — Add port disambiguation comment to `scripts/start.sh` (container:8000 → host:8088)
- [x] **T-065** — Move 39 ad-hoc scripts from `scripts/` to `debug/` per PR-ORG-001
- [x] **T-066** — Annotate uvicorn command in `specify-rules.mdc` as "(local run, non-Docker only)"
- [x] **T-067** — Set `TYPESCRIPT_STRICT=true` in `docker-compose.yml` to enforce PR-FE-002 in frontend container
- [x] **T-068** — Update `specify-rules.mdc` MANUAL ADDITIONS block with permanent process spec index (Dev Practices, Bug Fixing, UX)
- [x] **T-069** — Run `update-agent-context.sh cursor-agent` after each spec migration to propagate branch metadata
- [x] **T-070** — Execute sanity check cross-referencing all specs against `docker-compose.yml`, `tasks.json`, `scripts/`, and `specify-rules.mdc`

---

## Completion Summary

| Phase | Tasks | Completed |
|-------|-------|-----------|
| Phase 1 — Development Best Practices (26 rules) | 28 | 28 ✓ |
| Phase 2 — Bug Fixing Workflow (9 rules) | 15 | 15 ✓ |
| Phase 3 — UX & Frontend Guidelines (20 rules) | 13 | 13 ✓ |
| Phase 4 — Infrastructure & Agent Context | 7 | 7 ✓ |
| **Total** | **63** | **63 ✓** |

**All tasks completed and merged into `main` on 2026-02-23.**
