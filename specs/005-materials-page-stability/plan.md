# Implementation Plan: Materials Page Stability

**Branch**: `005-materials-page-stability` | **Date**: 2026-02-25 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/005-materials-page-stability/spec.md` (with Clarifications session 2026-02-25).

---

## Summary

Ensure the materials page opens without crashing under all API failure modes: (1) add a **retry control** that re-requests materials without full page reload; (2) enforce a **maximum loading time** (e.g. 30 seconds) so the user never sees an indefinite spinner; (3) ensure **all API calls** made while the materials page is loading (materials list, notifications, auth, translations) are handled so that a failure in any of them does not crash the page; (4) keep **console reporting** controlled (user message and correlation ID, no raw error objects). 4xx, 5xx, and backend-unreachable are treated the same in the UI (error state with retry).

---

## Technical Context

**Language/Version**: TypeScript, Node 20; Next.js 14.  
**Primary Dependencies**: Next.js 14, React, axios (API client), existing `frontend/src/services/api.ts` (interceptor with `normalizedErrorDetails`, `X-Correlation-ID`).  
**Storage**: N/A.  
**Testing**: Manual verification (open materials page with API failing/slow; confirm no crash, retry works, loading cap); optional E2E for retry and timeout.  
**Target Platform**: Browser; Next.js dev/server (e.g. port 3001).  
**Project Type**: Web application (frontend-only changes under `frontend/`).  
**Constraints**: No backend contract changes; align with FR-001–FR-007 and clarified spec (all APIs on page load, retry, 30s cap, same handling for unreachable/5xx).  
**Scale/Scope**: Materials page and any layout/navbar code that runs when the materials route loads.

---

## Constitution Check

*GATE: Must pass before implementation. Re-check after design.*

- The project constitution (`.specify/memory/constitution.md`) is a placeholder with no project-specific gates. No constitution violations identified for this feature.
- **Verdict**: PASS. Plan is scoped to frontend stability only and does not introduce new architectural principles.

---

## Project Structure

### Documentation (this feature)

```text
specs/005-materials-page-stability/
├── plan.md              # This file
├── spec.md              # Feature spec + Clarifications
├── checklists/
│   └── requirements.md
└── tasks.md             # Output of /speckit.task (not created by plan)
```

### Source Code (relevant paths)

```text
frontend/
├── src/
│   ├── app/[locale]/
│   │   ├── layout.tsx           # AuthProvider wraps children
│   │   └── materials/
│   │       ├── page.tsx         # Materials list UI, loading, error, retry
│   │       └── layout.tsx
│   ├── components/
│   │   └── layouts/
│   │       └── navbar.tsx       # Calls getUnreadNotificationCount, useAuth
│   ├── contexts/
│   │   └── auth-context.tsx     # Auth state; must not throw and crash page
│   ├── lib/
│   │   └── notification-utils.ts # getUnreadNotificationCount (already catches, returns 0)
│   ├── services/
│   │   ├── api.ts               # Interceptor, timeout, normalizedErrorDetails
│   │   └── materials.ts         # getMaterials (cache, dev fallback, throw on error)
│   └── i18n/                    # getTranslations (materials page uses)
└── ...
```

**Structure Decision**: All implementation is under `frontend/src/`. Primary touchpoints: `app/[locale]/materials/page.tsx`, `services/materials.ts`; verification only for `lib/notification-utils.ts`, `contexts/auth-context.tsx`, and `components/layouts/navbar.tsx`.

---

## Implementation Phases

### Phase 1 — Retry Control (FR-006)

**Goal**: When the materials list fails, the user sees an error state with a retry control that **re-requests materials without reloading the page** (no `window.location.reload()`).

**Tasks**:

1. **Retry button behavior**  
   - In `frontend/src/app/[locale]/materials/page.tsx`, in the error-state block where the "Retry" button is rendered, change the button’s `onClick` from `window.location.reload()` to a handler that calls `fetchMaterials(true)` (and clears `error` before or inside the call so the UI returns to loading then content/error).  
   - Ensure the button is not disabled indefinitely (e.g. only disable while `isRefreshing` if the retry path uses the same refresh flow).

2. **Optional: i18n**  
   - Use existing `t.common.retry` (or equivalent) for the button label if present; no new keys required for this phase.

**Verification**:

- **V1.1** — Open materials page with backend returning 500 (or offline). See error state with Retry button. Click Retry; the page re-requests materials (loading then content or error again) without full page reload.  
- **V1.2** — When materials load successfully after retry, the list is shown and error message is cleared.

---

### Phase 2 — Maximum Loading Time (FR-007, SC-004)

**Goal**: The materials page leaves the loading state within a defined maximum (e.g. 30 seconds). After that, the user sees either content or a clear error state with retry, never an indefinite spinner.

**Tasks**:

1. **Loading guard on the materials page**  
   - In `frontend/src/app/[locale]/materials/page.tsx`, when entering loading state for the initial materials fetch (e.g. when `fetchMaterials` is called and `isLoading` is set), start a timer (e.g. `setTimeout` 30 seconds).  
   - If the timer fires while still in loading state (e.g. `isLoading === true` and no successful data yet), set an error state (e.g. "Request took too long. Please try again.") and set `isLoading` to false so the error UI with retry is shown.  
   - Clear the timer when the request completes (success or failure) so the guard does not fire after a late response. Use a ref to hold the timer ID and clear it in the `finally` of `fetchMaterials` (or equivalent).

2. **Optional: request-level timeout**  
   - Optionally, ensure the materials request itself has a timeout of at most 30 seconds (e.g. pass `timeout: 30000` in the axios config for the materials request in `services/materials.ts`) so the server cannot hold the loading state longer than the cap. This is complementary to the client-side guard.

**Verification**:

- **V2.1** — Simulate a very slow or hanging materials request (e.g. backend delay > 30s or mock that never resolves). Within 30 seconds the page must leave the loading state and show an error state with retry.  
- **V2.2** — Normal request that completes in &lt; 30s: loading state ends when the request completes, no spurious timeout error.

---

### Phase 3 — All APIs on Page Load Do Not Crash the Page (FR-005)

**Goal**: Confirm that every API call made while the materials page is loading is handled so that a failure in any of them does not crash the page. The page must still render and show materials or a clear, stable error state.

**Tasks**:

1. **Materials list API**  
   - Already handled: `getMaterials` throws on failure when not in dev fallback; the materials page `catch` sets error state and empty list. No crash. Ensure no unhandled rejection (current code path is already caught).

2. **Translations**  
   - Materials page loads translations in `useEffect`; the `loadTranslations` catch sets fallback `t` and still sets `translationsLoaded` to true so the page renders. Confirm this path does not throw and that missing keys do not cause a render throw (defensive checks for `t.nav`, `t.materials`, `t.common` already exist). No change required if verified.

3. **Notifications**  
   - `getUnreadNotificationCount` (used from navbar) is called from layout/navbar; it already catches errors and returns 0. Document that this satisfies “notifications failure must not crash the page” or add a try/catch in the navbar around the call that sets a safe default (e.g. count = 0) and does not rethrow. Current implementation already returns 0 on error; ensure the navbar does not throw if the function rejects (it’s async—verify caller awaits in try/catch or equivalent).

4. **Auth**  
   - Layout wraps with `AuthProvider`; materials page may consume auth via context indirectly (e.g. navbar). Ensure `AuthProvider` and any auth checks used when rendering the materials route do not throw uncaught exceptions (e.g. missing token or API failure for auth should result in “not authenticated” state, not a crash). If there is an auth API call on layout/materials load, it must be in try/catch or equivalent so failure does not crash the page.

**Verification**:

- **V3.1** — Materials API fails: page shows error state with retry (no crash).  
- **V3.2** — Notifications API fails (e.g. force 500 for `/api/notifications/unread-count`): materials page still loads and shows materials or materials error state; no white screen.  
- **V3.3** — Translations failure: page still renders with fallback text; no crash.  
- **V3.4** — If auth is used on materials load: force auth failure; page must not crash (show materials or login/redirect per existing behavior).

---

### Phase 4 — Console and Initialization (FR-003, FR-004)

**Goal**: Console error reporting for materials (and where relevant other) API failures is controlled (user message and correlation ID); no raw unhandled errors indicating a crash. Initialization failures that affect the materials page do not crash it.

**Tasks**:

1. **Materials API errors**  
   - Already implemented in `services/materials.ts` and materials `page.tsx`: catch block reads `normalizedErrorDetails` or `config.headers['X-Correlation-ID']` and logs a string (message + correlation_id), never the raw error object. Confirm no other code path on the materials page or materials service logs the raw error for materials fetch. Remove or guard any `console.error(..., error)` for materials fetch if still present.

2. **Other callers**  
   - Notifications: `notification-utils.ts` already catches and logs with `console.warn`; no need to log correlation ID for this feature. Auth: ensure any auth-related API error in context is caught and does not surface as unhandled; log in a controlled way if needed.

3. **Initialization**  
   - Ensure that any initialization that runs when the user navigates to the materials route (layout, navbar, auth context) is wrapped so that failures are caught and do not propagate as uncaught exceptions. This is largely verification; document any missing try/catch and add minimal handling.

**Verification**:

- **V4.1** — Trigger materials 500; console shows a controlled message (e.g. user message and correlation_id), not a raw error object or “Q”.  
- **V4.2** — No unhandled promise rejection or uncaught exception when opening the materials page with one or more APIs failing.

---

## Verification Summary

| Criterion | Phase | Verification |
|-----------|--------|--------------|
| Retry re-requests without reload | 1 | V1.1, V1.2 |
| Loading state ends within 30s | 2 | V2.1, V2.2 |
| Materials API failure does not crash | 3 | V3.1 |
| Notifications failure does not crash | 3 | V3.2 |
| Translations failure does not crash | 3 | V3.3 |
| Auth failure does not crash | 3 | V3.4 |
| Controlled console for materials errors | 4 | V4.1 |
| No unhandled errors on page load | 4 | V4.2 |

---

## Dependencies and Ordering

- **Phase 1** (retry control) can be done first and is independent.  
- **Phase 2** (loading cap) can be done in parallel or after Phase 1.  
- **Phase 3** (all APIs) is mostly verification and small defensive changes; can follow Phase 1 and 2.  
- **Phase 4** (console/initialization) is verification and cleanup; can be done last.

Recommended order: **Phase 1 → Phase 2 → Phase 3 → Phase 4**.

---

## Final Commit and Merge Checklist

Before committing and merging branch `005-materials-page-stability`:

- [x] **C1** — All verification items (V1.1–V4.2) have been run and pass; materials page opens without crash under API failure, retry works, loading cap respected.
- [x] **C2** — No debug artifacts: `api.ts` has no `console.log` / `console.count` / `[AXIOS DEBUG]`; materials page has no verbose debug logs.
- [x] **C3** — API normalization layer is documented: `frontend/ARCHITECTURE.md` and `specs/005-materials-page-stability/api-normalization-layer.md` describe UUID correlation IDs, defensive URL stripping, and the Materials shift to real API.
- [x] **C4** — JSDoc/TSDoc in `frontend/src/services/api.ts` reflects architectural decisions (module-level and request interceptor).
- [x] **C5** — Materials module uses real backend only: no localStorage or demo-data fallbacks in `frontend/src/services/materials.ts` or materials list page.
- [x] **C6** — Backend `GET /api/v1/materials` is confirmed to query MongoDB `materials` collection (route and service docstring in place).
- [ ] **C7** — Optional: run full regression (e.g. materials list, create, edit, delete, notifications count) in dev and Docker before merge.

---

## Out of Scope

- Backend fix for materials API 500 (spec assumption).  
- Changing backend contract or adding new backend endpoints.  
- Distinct UI copy or treatment for “backend unreachable” vs “5xx” (same handling per clarification).  
- E2E test automation (optional; manual verification is in scope).
