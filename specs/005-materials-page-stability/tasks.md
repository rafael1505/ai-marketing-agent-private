# Tasks: Materials Page Stability

**Input**: Design documents from `specs/005-materials-page-stability/`  
**Prerequisites**: plan.md, spec.md  
**Tests**: Not requested in spec; manual verification per plan.

**Organization**: Tasks are grouped by user story (US1 = P1, US2 = P2) to enable independent implementation and verification.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[US1/US2]**: User story (US1 = Open materials page without crashing, US2 = Console and initialization)
- Include exact file paths in descriptions

## Path Conventions

- Frontend: `frontend/src/` (app, components, contexts, lib, services)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify feature context and existing API client capabilities.

- [x] T001 Verify `frontend/src/services/api.ts` exposes Axios instance with baseURL, request interceptor (X-Correlation-ID), and response interceptor (normalizedErrorDetails) per plan.md Technical Context
- [x] T002 [P] Verify `frontend/src/app/[locale]/materials/page.tsx` exists and fetches materials via `getMaterials` from `frontend/src/services/materials.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Ensure API client and materials service are ready so page can show error state and retry without crash.

- [x] T003 Confirm `frontend/src/services/materials.ts` `getMaterials` throws on API failure (no silent swallow) so page catch can set error state and empty list
- [x] T004 Confirm materials page `frontend/src/app/[locale]/materials/page.tsx` has a try/catch around `getMaterials()` that sets error state and empty list and does not rethrow (FR-002)

**Checkpoint**: Materials API failure path is handled; user story implementation can proceed.

---

## Phase 3: User Story 1 — Open Materials Page Without Crashing (Priority: P1) — MVP

**Goal**: User can open the materials page and see either the list or a clear error state with retry; loading state ends within 30s. All API calls on page load (materials, notifications, auth, translations) failing must not crash the page.

**Independent Test**: Navigate to `/en/materials`; page renders with no white screen or unhandled errors. Either materials list or "Unable to load" with empty list and "Try again" button. Clicking Retry re-requests materials without full page reload. After ≤30s, loading ends with content or error state.

### Implementation for User Story 1

- [x] T005 [US1] In `frontend/src/app/[locale]/materials/page.tsx`, ensure Retry button onClick calls `fetchMaterials(true)` and clears error (or sets loading) so the page re-requests materials without `window.location.reload()` (FR-006, Phase 1)
- [x] T006 [US1] In `frontend/src/app/[locale]/materials/page.tsx`, add loading guard: when `fetchMaterials` starts, set a ref to `setTimeout(30_000)`; in callback if still loading set error "Request took too long. Please try again." and set loading false; clear timeout in `finally` of `fetchMaterials` (FR-007, Phase 2)
- [x] T007 [US1] In `frontend/src/services/materials.ts`, pass `timeout: 30000` in the axios config for the materials list request (e.g. `api.get(url, { timeout: 30000 })`) per plan Phase 2 optional (frontend/src/services/materials.ts)
- [x] T008 [US1] In `frontend/src/app/[locale]/materials/page.tsx`, ensure translations load in useEffect with catch that sets fallback `t` and `translationsLoaded = true` so page always renders (FR-005 translations; frontend/src/app/[locale]/materials/page.tsx)
- [x] T009 [US1] Verify `frontend/src/lib/notification-utils.ts` `getUnreadNotificationCount` catches errors and returns 0; verify `frontend/src/components/layouts/navbar.tsx` awaits it in try/catch or equivalent and sets count to 0 on failure so notifications failure does not crash page (FR-005; frontend/src/lib/notification-utils.ts, frontend/src/components/layouts/navbar.tsx)
- [x] T010 [US1] Verify `frontend/src/contexts/auth-context.tsx` and any auth usage on materials route do not throw uncaught exceptions; failures result in "not authenticated" state, not crash (FR-005 auth; frontend/src/contexts/auth-context.tsx)
- [x] T011 [US1] In `frontend/src/app/[locale]/materials/page.tsx`, add defensive checks for `t.nav`, `t.materials`, `t.common` before rendering list/buttons to avoid render throw on missing keys (FR-004; frontend/src/app/[locale]/materials/page.tsx)

**Checkpoint**: User Story 1 complete. Materials page opens without crash; retry works; loading cap 30s; materials, translations, notifications, auth failures do not crash page.

---

## Phase 4: User Story 2 — Console and Initialization Do Not Indicate Crashes (Priority: P2)

**Goal**: Console and initialization show controlled error reporting (user message and correlation ID); no raw unhandled errors or misleading stack traces.

**Independent Test**: Open materials page with dev tools; trigger materials API error (e.g. 500). Console shows controlled message (e.g. user message and correlation_id), not raw error object. No unhandled promise rejection or uncaught exception on page load.

### Implementation for User Story 2

- [x] T012 [US2] In `frontend/src/app/[locale]/materials/page.tsx` and `frontend/src/services/materials.ts`, ensure materials fetch catch blocks use `normalizedErrorDetails` or `getErrorLogContext(error)` and log only user message and correlation_id, never raw error object (FR-003; frontend/src/app/[locale]/materials/page.tsx, frontend/src/services/materials.ts)
- [x] T013 [US2] In `frontend/src/components/layouts/navbar.tsx`, ensure notification count fetch failure is caught and does not surface as unhandled rejection; set notifications count to 0 on error (frontend/src/components/layouts/navbar.tsx)
- [x] T014 [US2] Remove or guard any `console.error(..., error)` that logs raw error objects for materials fetch or materials page load; keep only controlled message + correlation_id (FR-003, FR-004; frontend/src/app/[locale]/materials/page.tsx, frontend/src/services/materials.ts)
- [x] T015 [US2] Verify layout/navbar/auth initialization when navigating to materials route is wrapped so failures are caught and do not propagate as uncaught exceptions (FR-004; frontend/src/app/[locale]/layout.tsx, frontend/src/components/layouts/navbar.tsx)

**Checkpoint**: User Stories 1 and 2 complete. Console and initialization are controlled; no raw unhandled errors.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and final verification before merge.

- [x] T016 [P] Add or update `frontend/ARCHITECTURE.md` with API client standards (UUID correlation IDs, defensive URL normalization) and Materials module use of real backend per specs/005-materials-page-stability plan and api-normalization-layer.md
- [x] T017 [P] Ensure JSDoc/TSDoc in `frontend/src/services/api.ts` documents request interceptor URL normalization and references ARCHITECTURE.md (frontend/src/services/api.ts)
- [x] T018 Run manual verification V1.1, V1.2 (retry), V2.1, V2.2 (loading cap), V3.1–V3.4 (all APIs), V4.1, V4.2 (console) from plan.md Verification Summary
- [x] T019 Complete Final Commit and Merge Checklist in `specs/005-materials-page-stability/plan.md` (C1–C7) before merge

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — verify existing structure.
- **Phase 2 (Foundational)**: Depends on Phase 1 — confirms materials failure path is handled.
- **Phase 3 (US1)**: Depends on Phase 2 — retry, loading cap, all APIs and defensive checks.
- **Phase 4 (US2)**: Depends on Phase 3 — console and initialization hygiene.
- **Phase 5 (Polish)**: Depends on Phase 4 — docs and final verification.

### User Story Dependencies

- **User Story 1 (P1)**: After Phase 2; no dependency on US2.
- **User Story 2 (P2)**: After US1; builds on same files (page, materials service, navbar).

### Within Each User Story

- US1: Retry (T005) and loading guard (T006) first; then timeout (T007); then verification tasks (T008–T011).
- US2: Error logging (T012–T014) then initialization verification (T015).

### Parallel Opportunities

- T001 and T002 can run in parallel (Phase 1).
- T016 and T017 can run in parallel (Phase 5).
- T008, T009, T010 are verification-only and can be done in any order after T005–T007.

---

## Parallel Example: Phase 1

```bash
# Verify API client and materials page exist
T001: Verify frontend/src/services/api.ts (interceptor, correlation ID, normalizedErrorDetails)
T002: Verify frontend/src/app/[locale]/materials/page.tsx and getMaterials usage
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (verify)
2. Complete Phase 2: Foundational (confirm catch path)
3. Complete Phase 3: User Story 1 (retry, loading cap, all APIs, defensive checks)
4. **STOP and VALIDATE**: Manual verification V1.1, V1.2, V2.1, V2.2, V3.1–V3.4
5. Demo: Open materials page with API failing/slow; confirm no crash, retry works, 30s cap

### Incremental Delivery

1. Phase 1 + 2 → foundation ready
2. Phase 3 (US1) → test independently → MVP
3. Phase 4 (US2) → controlled console → test V4.1, V4.2
4. Phase 5 → docs and final checklist → merge

### Suggested MVP Scope

- **MVP**: Phases 1–3 (User Story 1). Delivers: materials page opens without crash, retry without reload, loading state ends within 30s, all APIs on page load handled.

---

## Notes

- [P] tasks = different files or verification-only, no ordering dependency.
- [US1]/[US2] maps task to user story for traceability.
- No automated test tasks; spec and plan require manual verification only.
- Commit after each task or logical group; run plan verification items before merge.
