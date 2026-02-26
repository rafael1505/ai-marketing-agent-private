# Tasks: UX & Frontend Compliance (004-frontend-compliance)

**Branch**: `004-frontend-compliance`  
**Input**: [plan.md](./plan.md), [spec.md](./spec.md)  
**Organization**: Tasks grouped by the 5 implementation phases from the approved plan. Each task includes a **Verification** sub-item mapping to plan criteria V1.x–V5.x.

---

## Format

- **Checkbox**: `- [ ]` (markdown checkbox)
- **Task ID**: T001, T002, … in execution order
- **[P]**: Optional — task is parallelizable (different files, no dependency on incomplete tasks)
- **Description**: Action with exact file path(s)
- **Verification**: Sub-item referencing plan pass criteria (V1.1–V5.3)

---

## Phase 1: Core Infrastructure (Interceptor, UUID, Headers)

**Goal**: API interceptor generates UUID per request, sets `X-Correlation-ID` on every call, and normalizes all errors (4xx/5xx, timeout, network/DNS) into a single `ErrorDetails`-shaped object with `correlation_id` always set (UUID).

- [x] **T001** Add UUID generation helper in `frontend/src/services/api.ts` (use `crypto.randomUUID()` when available, else add `uuid` and `v4()`); generate one UUID per request and store on request config (e.g. `config.metadata.correlationId` or header) for response interceptor.
  - **Verification**: V1.1 — Every API request has `X-Correlation-ID` header (UUID) in Network tab.

- [x] **T002** [P] In `frontend/src/services/api.ts`, request interceptor: set header `X-Correlation-ID` to the generated UUID for every request; do not overwrite if caller already set it; reuse same ID on retry.
  - **Verification**: V1.1 — Request header present and UUID-format.

- [x] **T003** In `frontend/src/services/api.ts`, response/error normalizer: on error with `response.data?.error_details`, normalize to `ErrorDetails` (ensure `correlation_id` from body or request header); attach as `error.normalizedErrorDetails` (or equivalent) for callers.
  - **Verification**: V1.2 — 404/500 response produces normalized error with UUID `correlation_id` and `user_message` / `error_type` set.

- [x] **T004** In `frontend/src/services/api.ts`, for errors with no response (timeout, network, DNS): build full `ErrorDetails`-shaped object (`error_type`: e.g. `timeout` / `network_error`, `user_message`: i18n key, `provider: 'unknown'`, `correlation_id`: request UUID, `http_status`: 408 or 503, `details: {}`); attach to `error.normalizedErrorDetails`.
  - **Verification**: V1.3 — Timeout produces client-side normalized error with UUID `correlation_id` and `error_type: 'timeout'` (or equivalent).

- [x] **T005** Remove ad-hoc client IDs in `frontend/src/services/api.ts` and `frontend/src/services/ai-providers.ts` (e.g. `client-${Date.now()}`); use only UUID from interceptor.
  - **Verification**: V1.1, V1.2, V1.3 — No non-UUID correlation IDs.

- [ ] **T006** Run Phase 1 verification: (V1.1) DevTools Network — confirm `X-Correlation-ID` on a request; (V1.2) trigger 404/500 and confirm `normalizedErrorDetails` with UUID; (V1.3) trigger timeout and confirm client UUID and `error_type`.
  - **Verification**: V1.1, V1.2, V1.3 — All pass.

---

## Phase 2: Type Definitions (TypeScript Interfaces mirroring MCP)

**Goal**: Single source of truth for API error shapes mirroring `docs/mcp-connector-contract.md` §3.2 and §3.3.

- [x] **T007** [P] Create `frontend/src/types/api-errors.ts`: define `ErrorDetails` with required `error_type`, `user_message`, `provider`, `correlation_id`, `http_status` and optional `details?: Record<string, unknown>`; optionally export union for canonical `error_type` values from §3.3; document client-only fields (e.g. `suggested_actions`, `timestamp`) as optional for display.
  - **Verification**: V2.2 — Single type file; extendable for new backend fields.

- [x] **T008** In `frontend/src/types/api-errors.ts`, export `ApiErrorPayload` (e.g. `{ success: false; error_details: ErrorDetails }`) for typing `response.data` / `error.normalizedErrorDetails`.
  - **Verification**: V2.1 — Types available for call sites.

- [x] **T009** In `frontend/src/services/api.ts`, type normalizer return as `ErrorDetails`; ensure no `any` for `error_details` or `normalizedErrorDetails` at interceptor.
  - **Verification**: V2.1 — TypeScript build passes; no `any` at interceptor.

- [x] **T010** In `frontend/src/services/ai-providers.ts` (and any other service touching `error_details`), import and use `ErrorDetails` / `ApiErrorPayload`; remove loose typing.
  - **Verification**: V2.1 — No `any` for error payload at services.

- [ ] **T011** Run Phase 2 verification: `npm run build` (or `tsc`) in frontend; confirm no `any` for error payload at interceptor and error-display call sites.
  - **Verification**: V2.1, V2.2 — Build clean; single place to extend types.

---

## Phase 3: Global State (ErrorProvider & Context)

**Goal**: Error state and setters via React Context so screens avoid prop drilling.

- [ ] **T012** Create `frontend/src/context/error-context.tsx`: context state `errorDetails: ErrorDetails | null`, `setErrorDetails: (d: ErrorDetails | null) => void`, `clearError: () => void`; implement Provider component; export `useError()` (or `useApiError()`) returning `{ errorDetails, setErrorDetails, clearError }`; throw if used outside provider.
  - **Verification**: V3.1 — Hook available; state can be set from any child.

- [ ] **T013** Wrap app (or locale layout) with `<ErrorProvider>` in the appropriate layout under `frontend/src/app/[locale]/` so all pages can use the hook; keep Provider inside i18n layout if error display needs `getTranslations()`.
  - **Verification**: V3.1 — Setting error from a page shows error UI (once display reads context in Phase 4).

- [ ] **T014** Document usage: in API catch blocks call `setErrorDetails(normalizedErrorDetails)`; on retry/dismiss call `clearError()` or `setErrorDetails(null)` (e.g. in quickstart.md or code comments).
  - **Verification**: V3.2 — Pattern clear for migration (Phase 5).

- [ ] **T015** Run Phase 3 verification: from a page, trigger an API failure and call `setErrorDetails(normalizedErrorDetails)`; confirm error UI appears (e.g. by temporarily passing context value to display or after T018).
  - **Verification**: V3.1, V3.2 — Error from context visible; no prop drilling for display after Phase 4.

---

## Phase 4: UI Layer (Refactoring ai-error-display & Error Boundary)

**Goal**: Error display consumes Context and `ErrorDetails`; top-level Error Boundary catches render/lifecycle errors with fallback (Retry / Go home).

- [ ] **T016** Refactor `frontend/src/components/ui/ai-error-display.tsx`: accept props aligned with `ErrorDetails` and optional `onRetry`, `onSwitchProvider`; use `useError()` and render when `errorDetails !== null`; resolve primary message via i18n from `user_message` only; show `correlation_id` in technical details; type all props with `ErrorDetails` and optional client-only fields.
  - **Verification**: V4.1 — API error set via context displays with message and correlation ID.

- [ ] **T017** In layout that wraps with `ErrorProvider`, render a single `<AIErrorDisplay />` that reads from context so any page that sets error via context shows it without per-page placement.
  - **Verification**: V4.1 — Single global display; no inline display needed per page.

- [ ] **T018** Implement top-level Error Boundary: create class component (or use allowed library) with `componentDidCatch` / `getDerivedStateFromError`; fallback UI with short message, "Retry" (reset error state / re-render), "Go home" (navigate to locale home); optionally show or log last `correlation_id` from context when error was API-related.
  - **Verification**: V4.2 — Render throw → fallback with Retry/Go home; no white screen.

- [ ] **T019** Wrap root layout (or subtree under `ErrorProvider`) with the Error Boundary so unhandled render errors show fallback instead of blank screen.
  - **Verification**: V4.2, V4.3 — Boundary active; optional correlation ID in fallback when API-related.

- [ ] **T020** Run Phase 4 verification: (V4.1) Trigger API error via context → refactored component shows message and correlation ID; (V4.2) throw in a page render → boundary fallback with Retry/Go home; (V4.3) optional: API error then throw → boundary shows/logs correlation ID.
  - **Verification**: V4.1, V4.2, V4.3 — All pass.

---

## Phase 5: Migration & Cleanup (Incremental Screen Updates)

**Goal**: Migrate existing screens from manual error state and inline `<AIErrorDisplay>` to Error Provider + context; zero-downtime during development.

- [ ] **T021** Inventory: list all pages/components using `error_details`, `setAiError`, or `<AIErrorDisplay>` (e.g. `frontend/src/app/[locale]/materials/create/page.tsx`, `frontend/src/app/[locale]/materials/[id]/edit/page.tsx`); for each note where error state is set, where display is rendered, and what props are passed.
  - **Verification**: V5.1 — Migration list complete for T022–T024.

- [ ] **T022** Migrate materials create screen: in `frontend/src/app/[locale]/materials/create/page.tsx`, remove local `aiError` / `setAiError`; on API failure use `error.normalizedErrorDetails` and call `setErrorDetails(...)`; remove inline `<AIErrorDisplay ... />`; retry/dismiss call `clearError()` then retry or navigate.
  - **Verification**: V5.1 — Create screen: 404/500/timeout shows global error with correlation ID; retry/dismiss works.

- [ ] **T023** Migrate materials edit screen: in `frontend/src/app/[locale]/materials/[id]/edit/page.tsx`, same as T022 — remove local error state, use `setErrorDetails(normalizedErrorDetails)`, remove inline error display, wire retry/dismiss to `clearError()`.
  - **Verification**: V5.1 — Edit screen: 404/500/timeout shows global error with correlation ID; retry/dismiss works.

- [ ] **T024** Migrate any remaining screens from inventory (T021): apply same pattern (remove local error state, set context on failure, remove inline `<AIErrorDisplay>`, wire clear on retry/dismiss).
  - **Verification**: V5.1 — All migrated screens show global error with correlation ID.

- [ ] **T025** Cleanup: remove deprecated props or duplicate types from `frontend/src/components/ui/ai-error-display.tsx` if any; ensure all API paths (including `frontend/src/services/ai-providers.ts`) use interceptor and normalized shape only; no ad-hoc `error_details` construction outside normalizer.
  - **Verification**: V5.2 — No alert(); no dead-end errors; main flows pass.

- [ ] **T026** Run Phase 5 verification: (V5.1) Per migrated screen trigger 404/500 or timeout → global error UI with correct correlation ID; (V5.2) full regression — create material, edit material, AI generate, providers list — no alert(), no missing correlation ID, no dead-end screens; (V5.3) trigger 404/500 from at least two screens and confirm Correlation ID visible in UI and matches request/response or client UUID.
  - **Verification**: V5.1, V5.2, V5.3 — All pass.

---

## Dependencies & Execution Order

| Phase   | Depends on   | Blocks        |
|---------|--------------|---------------|
| Phase 1 | —            | Phases 2–5    |
| Phase 2 | — (can run parallel to Phase 1) | Phase 3, 4   |
| Phase 3 | Phase 1, 2   | Phase 4, 5    |
| Phase 4 | Phase 2, 3   | Phase 5       |
| Phase 5 | Phase 4      | —             |

- **Phase 1** must be done first (interceptor + normalizer produce shape and UUID).
- **Phase 2** can be done in parallel with Phase 1 or right after; types needed before Phase 3/4.
- **Phase 3** before Phase 4 so display can consume context.
- **Phase 4** depends on Phase 2 types and Phase 3 context.
- **Phase 5** after Phase 4; screens can be migrated incrementally (T022 → T023 → T024).

---

## Verification Reference (from plan)

| ID   | Criteria |
|------|----------|
| V1.1 | Every API request has `X-Correlation-ID` header (UUID) in Network tab. |
| V1.2 | 404/500 response produces normalized error with UUID `correlation_id`. |
| V1.3 | Timeout produces client-side normalized error with UUID `correlation_id`. |
| V2.1 | TypeScript build clean; no `any` for error payload at interceptor/display. |
| V2.2 | Single type file; extendable for new backend fields. |
| V3.1 | Setting error via context shows error UI. |
| V3.2 | No prop drilling for error display after Phase 4. |
| V4.1 | API error set via context displays in refactored component with correlation ID. |
| V4.2 | Render throw → Error Boundary fallback with Retry/Go home. |
| V4.3 | (Optional) Boundary can show correlation ID when error was API-related. |
| V5.1 | Per-screen: 404/500/timeout shows global error with correlation ID. |
| V5.2 | No alert(); no dead-end errors; main flows pass. |
| V5.3 | 404/500 from two+ screens; correlation ID visible and correct. |

---

## Summary

| Phase | Tasks    | Verification keys   |
|-------|----------|----------------------|
| Phase 1 — Core Infrastructure | T001–T006 | V1.1, V1.2, V1.3 |
| Phase 2 — Type Definitions    | T007–T011 | V2.1, V2.2        |
| Phase 3 — Global State        | T012–T015 | V3.1, V3.2        |
| Phase 4 — UI Layer            | T016–T020 | V4.1, V4.2, V4.3 |
| Phase 5 — Migration & Cleanup | T021–T026 | V5.1, V5.2, V5.3 |
| **Total**                     | **26**   | —                 |

**Suggested next step**: Run implementation phase-by-phase; after each phase run the listed Verification steps before proceeding.
