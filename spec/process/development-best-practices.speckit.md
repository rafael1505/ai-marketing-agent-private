# Process Specification: Development Best Practices

**Spec ID**: `002-migrate-dev-practices`
**Branch**: `002-migrate-dev-practices`
**Created**: 2026-02-23
**Status**: Active
**Supersedes**: `spec/process/development-best-practices.speckit.md` (legacy informal doc)
**Applies to**: All code changes (features, refactors, bug fixes) in `ai-marketing-agent-private`

---

## Purpose

Define the authoritative, enforceable development standards for all work in this
repository. Any contributor — human or AI agent — MUST follow these standards
before writing, reviewing, or merging code.

---

## 1. Technology Stack (Canonical)

| Layer         | Technology                          | Port  |
|---------------|-------------------------------------|-------|
| Backend API   | Python 3.11, FastAPI, uvicorn       | 8088  |
| Frontend      | Node 20, Next.js 14, TypeScript     | 3001  |
| Database      | MongoDB 4.4 (Docker container)      | 27017 |
| Orchestration | Docker Compose V2 (`docker compose`)| —     |
| AI Providers  | Database-driven via `ai_providers`  | —     |

**Rules:**
- PR-STACK-001: Never use Python < 3.11 or Next.js < 14 in this project.
- PR-STACK-002: Ports 8088, 3001, and 27017 are fixed. Never change them without a
  constitution-level decision and a corresponding spec update.
- PR-STACK-003: Always use `docker compose` (V2 plugin). Never use legacy `docker-compose`.
- PR-STACK-004: AI provider credentials and model selection MUST come from the
  `ai_providers` MongoDB collection. Never hardcode API keys or model names.

---

## 2. File Organization

**Rule PR-ORG-001**: Never create files at the project root unless they are top-level
config files (e.g. `docker-compose.yml`, `pyproject.toml`).

| Content type           | Canonical path                            |
|------------------------|-------------------------------------------|
| Backend business logic | `app/services/`                           |
| Backend route handlers | `app/api/v1/endpoints/`                   |
| Backend DB access      | `app/db/`                                 |
| Frontend pages         | `frontend/src/app/[locale]/`              |
| Frontend components    | `frontend/src/components/`                |
| Frontend API clients   | `frontend/src/services/`                  |
| i18n translations      | `frontend/src/i18n/locales/` (en, pt)     |
| Backend unit tests     | `tests/unit/`                             |
| Integration tests      | `tests/integration/`                      |
| Frontend tests/tools   | `tests/frontend/`                         |
| Documentation          | `docs/`                                   |
| Debug scripts          | `debug/`                                  |
| Process specs          | `spec/process/`                           |
| Feature specs          | `specs/<id>-<slug>/`                      |

---

## 3. Backend Standards (Python 3.11 / FastAPI)

- PR-BE-001: Follow PEP 8. Use `ruff check .` as the linter; all linting warnings
  MUST be resolved before a PR is opened.
- PR-BE-002: All functions and methods MUST have type hints and docstrings.
- PR-BE-003: Business logic lives in `app/services/`. Route handlers in
  `app/api/v1/endpoints/` MUST be thin — orchestrate, do not implement.
- PR-BE-004: All database access uses the global Motor `mongodb` instance defined
  in `app/db/`. Never instantiate a new Motor client outside of `app/db/`.
- PR-BE-005: Error responses MUST include an `error_details` object with a
  `correlation_id` and an i18n-ready user message. Never return raw exception
  strings to the client.
- PR-BE-006: `uvicorn app.main:api_app --host 127.0.0.1 --port 8088 --reload` is
  the canonical local run command. Do not change the host or port without a spec.

---

## 4. Frontend Standards (Next.js 14 / TypeScript)

- PR-FE-001: Clean Code principles apply to all TypeScript. Functions do one thing,
  names are self-documenting, and files stay under 300 lines.
- PR-FE-002: Never use `any`. All types MUST be imported from `@/types` or declared
  inline as specific interfaces/types.
- PR-FE-003: Use React functional components only. Class components are forbidden.
- PR-FE-004: All hooks (`useState`, `useEffect`, etc.) MUST be declared at the top
  of the component function — never inside conditionals, loops, or after early returns.
- PR-FE-005: Use `shadcn/ui` as the component library. Follow Apple-inspired look &
  feel. Do not introduce additional component library dependencies without a spec.
- PR-FE-006: i18n translations use `getTranslations()` from `@/i18n`. Never import
  from `next-intl` directly. Always add a loading guard:
  `if (loading || !t.pages) return <LoadingState />;`
- PR-FE-007: Never use `alert()`. All errors MUST be surfaced via `<AIErrorDisplay>`
  with `error_details` and `correlation_id`.
- PR-FE-008: All API access lives in `frontend/src/services/` (Axios wrappers).
  Components MUST NOT call `fetch` or `axios` directly.

---

## 5. Testing Requirements

- PR-TEST-001: Every non-trivial change MUST have automated tests. PRs without tests
  for new or changed behavior will not be approved.
- PR-TEST-002: Bug fixes MUST add or update a test that fails before the fix and
  passes after. No exceptions.
- PR-TEST-003: Python tests use `pytest`. Run with `pytest` from the repo root.
- PR-TEST-004: Frontend tests live under `tests/frontend/` or the designated TS test
  framework. The framework MUST be documented in `docs/`.

---

## 6. Git Protocol

- PR-GIT-001: Use Conventional Commits for all commit messages:
  `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `ci:`.
- PR-GIT-002: Commit messages MUST be plain professional English. No emojis in
  commit messages or branch names.
- PR-GIT-003: Use a feature-branch workflow. Branch naming convention:
  `<id>-<short-slug>` (e.g. `002-migrate-dev-practices`). Never commit directly to
  `main`.
- PR-GIT-004: Keep commits small and focused on a single logical change. Avoid
  "kitchen sink" commits that mix unrelated changes.
- PR-GIT-005: Update documentation (`docs/`, relevant spec files) in the same PR
  as the behavior or API change that necessitates it. Documentation debt is not
  acceptable.

---

## 7. Agent Context Awareness

This section governs how AI coding agents (e.g. Cursor, GitHub Copilot, any
LLM-powered assistant) MUST operate in this repository.

- PR-AI-001: Before writing or suggesting any code, an AI agent MUST read and
  internalize `.cursor/rules/specify-rules.mdc`. This file is the single source of
  truth for active technologies, canonical ports, project structure, commands, and
  code style.
- PR-AI-002: Before starting work on a spec, an AI agent MUST check `specs/` for
  the relevant feature spec directory (e.g. `specs/002-<slug>/`). If the spec exists,
  its `spec.md` defines the requirements. If it does not exist, use `/speckit.specify`
  to generate one before coding.
- PR-AI-003: An AI agent MUST NOT infer stack or port values from filenames, imports,
  or partial context. All canonical values come from `.cursor/rules/specify-rules.mdc`
  only.
- PR-AI-004: An AI agent MUST NOT create files at the project root, introduce new
  dependencies, or change canonical ports/commands without an explicit user instruction
  that references a spec ID.
- PR-AI-005: After completing a task, an AI agent MUST check for linter errors in
  all edited files using the ReadLints tool (or `ruff check .` for Python) and fix
  any introduced violations before presenting the result.

---

## Success Criteria

- SC-001: Any developer or AI agent new to the project can read this spec and
  unambiguously determine the correct language version, port, path, and style
  convention for any change.
- SC-002: A PR that violates any `PR-*` rule in this spec is identifiable and
  correctable by another team member or an AI agent without consulting the author.
- SC-003: AI agent interactions that reference this spec produce code that matches
  the canonical stack, passes `ruff check .`, and uses correct ports on the first
  attempt, without requiring manual correction.

---

## Changelog

| Date       | Change                                                                |
|------------|-----------------------------------------------------------------------|
| 2026-02-23 | Migrated from legacy informal doc; added formal rules, stack table,   |
|            | Git Protocol, and Agent Context Awareness section (PR-AI-001–005).   |
