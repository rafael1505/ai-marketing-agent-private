# AI Marketing Agent – Project Constitution

## Purpose

Single source of truth for non‑negotiable rules, architecture constraints, and global development standards for the AI Marketing Agent.

## Instruction Hierarchy

1. This Spec Kit constitution and specs in `spec/`.
2. Process and feature specs under `spec/process/` and `spec/features/`.
3. Legacy instruction files under `.github/` and `docs/` (historical reference only).

## Architecture & Environment

- Backend: FastAPI (Python) on port **8088**.
- Frontend: Next.js 14 (React + TypeScript) on port **3001**.
- Database: MongoDB (Docker) on port **27017**.
- AI providers are **database‑driven** via the `ai_providers` collection; providers must never be hardcoded.

## Clean Architecture

- Business logic: `app/services/` (not in route handlers).
- API routes: `app/api/v1/endpoints/` as thin controllers.
- Database access: `app/db/` using the global Motor instance `app.db.mongodb`.
- Frontend:
  - Pages: `frontend/src/app/[locale]/`
  - Components: `frontend/src/components/`
  - API client: `frontend/src/services/`
  - i18n: `frontend/src/i18n/locales/`

## Global Development Rules

- Never create files at project root; always use the appropriate subdirectory.
- No `any` in TypeScript; use proper types from `@/types`.
- All non‑trivial changes require tests (`tests/unit`, `tests/integration`, `tests/frontend`).
- Commit messages follow Conventional Commits (`fix:`, `feat:`, `docs:`, `refactor:`, etc.).
- Backend Python code follows PEP 8 and uses type hints and docstrings.

## UX & Error Handling

- React hooks must be at the top of components; never inside conditionals, loops, or after early returns.
- Use the custom `@/i18n` `getTranslations()` pattern, not `next-intl`.
- Always guard translations: `if (loading || !t.pages) return <LoadingState />;`.
- Never use `alert()` for errors; use `<AIErrorDisplay>` with correlation IDs.
- Backend errors return enriched `error_details` including `error_type`, `user_message` (i18n key), `provider`, `correlation_id`, `http_status`, and `details`.

## Material Creation Workflow

The material lifecycle always follows this 3‑stage pipeline:

1. **Idea** – create material with `stage = "idea"`, `status = "draft"`.
2. **Refinement** – generate AI images via `/api/v1/ai/generate-image`, store them in `material.generated_images[]` with metadata.
3. **Finalization** – user selects the final image; material moves to `stage = "finalization"`, `status = "completed"`.

No feature or change may bypass or break this 3‑stage workflow.