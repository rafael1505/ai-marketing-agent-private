# Development Best Practices – Process Spec

## Purpose

Define day‑to‑day coding standards and file‑organization rules for backend and frontend work in the AI Marketing Agent.

## Scope

Applies to any code change (backend or frontend), including features, refactors, and bug fixes.

## Backend (Python – FastAPI)

- Follow PEP 8 for style.
- All functions have type hints and docstrings.
- Business logic stays in `app/services/`, not in route handlers.
- Database access stays in `app/db/`, using the global Motor `mongodb` instance.
- Error responses include enriched `error_details` with correlation IDs and i18n user messages.

## Frontend (Next.js + TypeScript)

- Use React functional components only.
- Never use `any`; import types from `@/types`.
- All hooks (`useState`, `useEffect`, etc.) are at the top of the component function, never inside conditionals, loops, or after early returns.
- Use shadcn/ui as the component library and follow Apple‑inspired look & feel.
- API access lives in `frontend/src/services/` (e.g. Axios wrappers).

## File Organization

- Do not create files at the project root.
- Use:
  - Backend code → `app/`
  - Frontend pages → `frontend/src/app/[locale]/`
  - Frontend components → `frontend/src/components/`
  - Frontend services → `frontend/src/services/`
  - Tests → `tests/unit/`, `tests/integration/`, `tests/frontend/`
  - Docs → `docs/`
  - Debug scripts → `debug/`

## Testing Requirements

- Every non‑trivial change has automated tests.
- Bug fixes must add or update tests that would fail before the fix and pass after.
- Python tests use `pytest`.
- Frontend tests live under `tests/frontend/` or the chosen TS test framework.

## Commit & Collaboration

- Use Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, etc.).
- Keep changes small and focused.
- Update documentation when behavior or APIs change.