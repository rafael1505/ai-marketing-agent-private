# Implementation Plan: UX & Frontend Compliance

**Branch**: `004-frontend-compliance` | **Date**: 2026-02-24 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/004-frontend-compliance/spec.md` (refined with Clarifications session 2026-02-24).

---

## Summary

Establish frontend architectural compliance with the backend’s structured error model: (1) a global API interceptor that injects UUID correlation IDs via `X-Correlation-ID` and normalizes all errors into a single shape; (2) centralized TypeScript types mirroring the MCP `error_details` contract; (3) an Error Context Provider to avoid prop drilling; (4) refactored `ai-error-display.tsx` consuming that context and a top-level Error Boundary for render/lifecycle failures; (5) a step-by-step migration of existing screens to the new flow with verification at each phase (e.g. trigger 404/500 and confirm correlation ID display).

---

## Technical Context

**Language/Version**: TypeScript (frontend), Node 20; Next.js 14.  
**Primary Dependencies**: Next.js 14, React, axios (API client), shadcn/ui; optional `uuid` or `crypto.randomUUID()` for client-side correlation ID.  
**Storage**: N/A (frontend-only; backend unchanged).  
**Testing**: Manual verification per phase (404/500/timeout triggers); optional Jest/React Testing Library for Provider/boundary.  
**Target Platform**: Browser (client-side API calls); Next.js dev server (port 3001).  
**Project Type**: Web application (frontend compliance within existing `frontend/`).  
**Constraints**: No backend changes; types must mirror `docs/mcp-connector-contract.md` §3; UX-003d/003e/003f, UX-004e, FR-001–FR-007.  
**Scale/Scope**: All API call sites and error display touchpoints; existing pages under `frontend/src/app/[locale]/`.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **UX-003 (Feedback Loops)**: Error display via single component with `correlation_id`; no `alert()`; actionable path after errors — **Satisfied by plan (Error Provider + refactored display + boundary).**
- **UX-004 (i18n)**: `user_message` resolved via i18n; no raw backend strings — **Satisfied by plan (display component uses i18n key).**
- **ARCH-MCP / MCP Contract**: Frontend types and normalizer align with `error_details` schema and correlation ID propagation — **Satisfied by plan (Phase 2 types, Phase 1 interceptor).**
- **Spec Clarifications**: UUID for client-side ID; `X-Correlation-ID` on all requests; Provider for error injection — **Satisfied by plan (Phase 1, Phase 3, Phase 4).**

**Verdict**: PASS. No constitution violations; plan aligns with process specs and clarified spec.

---

## Project Structure

### Documentation (this feature)

```text
specs/004-frontend-compliance/
├── plan.md              # This file
├── spec.md              # Feature spec + Clarifications
├── checklists/
│   └── requirements.md
├── research.md          # (Optional) Phase 0 if unknowns arise
├── data-model.md        # (Optional) Entity/type summary
├── quickstart.md        # (Optional) Dev verification steps
└── tasks.md             # Output of /speckit.tasks (not created by plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/[locale]/           # Pages (migration targets)
│   ├── components/
│   │   └── ui/
│   │       ├── ai-error-display.tsx   # Refactor to consume Context
│   │       └── ...
│   ├── context/                # NEW: Error context + provider
│   │   └── error-context.tsx
│   ├── hooks/                  # Optional: useError(), useApiError()
│   ├── services/
│   │   ├── api.ts              # Interceptor + UUID + normalizer
│   │   └── ai-providers.ts     # Use normalized types
│   └── types/                  # NEW or existing: API/error types
│       └── api-errors.ts        # ErrorDetails, ApiErrorPayload, etc.
└── ...
```

**Structure Decision**: Frontend-only changes under `frontend/src/`. New: `context/error-context.tsx`, `types/api-errors.ts`. Modified: `services/api.ts`, `components/ui/ai-error-display.tsx`, and layout for Error Boundary + Provider. Migration touches `app/[locale]/` pages that currently pass error props manually.

---

## Implementation Phases

### Phase 1 — Core Infrastructure: API Interceptor (UUID + X-Correlation-ID)

**Goal**: Single place that (a) generates a UUID per request and sets `X-Correlation-ID` on every outbound API call, (b) on error (4xx/5xx or client-side timeout/network/DNS), normalizes to the structured `error_details` shape and ensures `correlation_id` is always a UUID (from response or client-generated).

**Tasks**:

1. **UUID generation**  
   - In `frontend/src/services/api.ts` (or a small `api-correlation.ts` helper), generate one UUID per request.  
   - Use `crypto.randomUUID()` if available (modern browsers/Node), else add dependency `uuid` and `v4()`.  
   - Store the ID on the request config (e.g. `config.metadata.correlationId` or header) so the response interceptor can read it.

2. **Request interceptor**  
   - For every request, set header `X-Correlation-ID` to the generated UUID.  
   - Ensure the same ID is reused if the same config is retried (do not overwrite if already set by caller).

3. **Response/error normalizer**  
   - On success: optionally attach correlation ID from response header to the response object for logging.  
   - On error (response with body):  
     - If `response.data?.error_details` exists, normalize it (see Phase 2 type) and ensure `correlation_id` is string (prefer from `error_details`, else from request header).  
     - Attach normalized `error_details` to the error object (e.g. `error.normalizedErrorDetails`) for callers.  
   - On error (no response: timeout, network, DNS):  
     - Build a full `ErrorDetails`-shaped object with: `error_type` (e.g. `timeout`, `network_error`), `user_message` (i18n key, e.g. `errors.ai.timeout`), `provider: 'unknown'`, `correlation_id: <request UUID>`, `http_status` (408 or 503), `details: {}`.  
     - Attach to `error.normalizedErrorDetails` (or equivalent) so callers get one consistent shape.

4. **Replace ad-hoc client IDs**  
   - Remove any `client-${Date.now()}` or similar in `api.ts` and `ai-providers.ts`; use only the UUID from the interceptor.

**Verification**:

- **V1.1** — In browser DevTools Network tab, send any API request (e.g. materials list or AI providers); confirm request header `X-Correlation-ID` is present and UUID-format.  
- **V1.2** — Trigger a 404 or 500 (e.g. request to a non-existent endpoint or mock 500). Confirm the thrown error has a `normalizedErrorDetails` (or equivalent) object with `correlation_id` as UUID and `user_message` / `error_type` set.  
- **V1.3** — Trigger a timeout (e.g. long-running endpoint or short timeout). Confirm client-side error has `correlation_id` as UUID and `error_type: 'timeout'` (or equivalent).

---

### Phase 2 — Type Definitions: Centralized `error_details` Interfaces

**Goal**: One source of truth for API error shapes that mirrors the MCP contract (`docs/mcp-connector-contract.md` §3.2 and §3.3).

**Tasks**:

1. **Create `frontend/src/types/api-errors.ts`** (or under existing `types/`).  
   - Define `ErrorDetails` interface with required fields: `error_type`, `user_message`, `provider`, `correlation_id`, `http_status`; optional: `details?: Record<string, unknown>`.  
   - Optionally export a union type for canonical `error_type` values (e.g. from §3.3: `provider_unavailable`, `timeout`, `rate_limit_exceeded`, …) for stricter typing.  
   - Document that client-only fields (e.g. `suggested_actions`, `timestamp`) are added by the normalizer and are optional for display; keep backend contract as source of truth for API shape.

2. **Export types for API responses**  
   - e.g. `ApiErrorPayload { success: false; error_details: ErrorDetails }` so call sites can type `response.data` or `error.normalizedErrorDetails` without `any`.

3. **Use in interceptor and services**  
   - In `api.ts`, type the normalizer return value as `ErrorDetails`.  
   - In `ai-providers.ts` and any other service that touches `error_details`, import and use `ErrorDetails` (and optional `ApiErrorPayload`).  
   - Ensure `ai-error-display` prop type uses `ErrorDetails` (Phase 4).

**Verification**:

- **V2.1** — TypeScript build passes with no `any` for `error_details` or `normalizedErrorDetails` at the interceptor and error-display call sites.  
- **V2.2** — If a backend response adds a new optional field to `error_details`, the type can be extended in one place (`api-errors.ts`) without breaking existing code.

---

### Phase 3 — Global State: Error Context Provider

**Goal**: Provide error state and setters via React Context so screens can show the shared error UI without prop drilling.

**Tasks**:

1. **Create `frontend/src/context/error-context.tsx`** (or equivalent path).  
   - Define context state: e.g. `errorDetails: ErrorDetails | null`, `setErrorDetails: (d: ErrorDetails | null) => void`, and optionally `clearError: () => void`.  
   - Implement a provider component that holds this state and wraps children.  
   - Export `useError()` (or `useApiError()`) hook that returns `{ errorDetails, setErrorDetails, clearError }`; throw if used outside provider.

2. **Integrate with app layout**  
   - Wrap the app (or locale layout) with `<ErrorProvider>` so all pages under `[locale]` can use the hook.  
   - Ensure Provider is inside any layout that needs i18n (so error display can use `getTranslations()` if needed).

3. **Document usage**  
   - In API-catching code: on normalized error, call `setErrorDetails(normalizedErrorDetails)` so the single error display (rendered once in layout or provider) can show it.  
   - On retry or dismiss, call `clearError()` or `setErrorDetails(null)`.

**Verification**:

- **V3.1** — From a page that performs an API call, trigger a failure and call `setErrorDetails(normalizedErrorDetails)`; confirm the error UI appears (even if the display component is not yet refactored to read from context; e.g. pass context value as prop during transition).  
- **V3.2** — Confirm no prop drilling of `errorDetails` / `setErrorDetails` through multiple levels for the error display (after Phase 4 integration).

---

### Phase 4 — UI Layer: Refactor `ai-error-display.tsx` + Top-Level Error Boundary

**Goal**: (a) Error display component consumes Error Context and uses `ErrorDetails` type; (b) one top-level Error Boundary catches render/lifecycle errors and shows fallback with retry/go home and optional correlation ID.

**Tasks**:

1. **Refactor `frontend/src/components/ui/ai-error-display.tsx`**  
   - Accept props that align with `ErrorDetails` (and optional callback props: `onRetry`, `onSwitchProvider`).  
   - If used with Provider: component can use `useError()` and render when `errorDetails !== null`; props can override or supplement for special cases.  
   - Ensure primary message is always resolved via i18n from `user_message`; never show raw backend string as primary.  
   - Show `correlation_id` in technical details; keep existing UX (severity, suggested actions, buttons).  
   - Type all props with `ErrorDetails` and optional client-only fields from Phase 2.

2. **Render error display from layout or Provider**  
   - In the same layout that wraps with `ErrorProvider`, render a single `<AIErrorDisplay />` (or named export) that reads from context so any page that sets error via context shows it without per-page placement.

3. **Implement top-level Error Boundary**  
   - Create a class component (or use a small library if project allows) that implements `componentDidCatch` / `getDerivedStateFromError` and renders a fallback UI: short message, “Retry” (reset error state and re-render), “Go home” (navigate to locale home).  
   - Optionally capture the last known `correlation_id` from context (if an API error triggered the throw) and display or log it in the fallback.  
   - Wrap the root layout (or the subtree under `ErrorProvider`) with this boundary so any unhandled render error shows the fallback instead of a blank screen.

**Verification**:

- **V4.1** — Trigger an API error and set it via context; confirm the refactored component shows message, correlation ID, and actions.  
- **V4.2** — Intentionally throw in a page component (e.g. `throw new Error('test')` in render). Confirm the Error Boundary fallback appears with Retry/Go home, and no white screen.  
- **V4.3** — (Optional) Trigger an API error that then causes a component to throw; confirm boundary can show or log the same correlation ID.

---

### Phase 5 — Migration Path: Step-by-Step Screen Replacement (Zero-Downtime)

**Goal**: Migrate existing screens from manual error state and inline `<AIErrorDisplay>` usage to the Error Provider + context, without breaking existing behavior during development.

**Tasks**:

1. **Inventory**  
   - List all pages/components that currently use `error_details`, `setAiError`, or `<AIErrorDisplay>` (e.g. `materials/create/page.tsx`, `materials/[id]/edit/page.tsx`, any other call sites from grep).  
   - For each, note: where error state is set, where display is rendered, and what props are passed.

2. **Migration order**  
   - Migrate one screen at a time (e.g. start with materials create, then materials edit).  
   - For each screen:  
     - Remove local error state for API errors (e.g. `aiError`, `setAiError`).  
     - On API failure, call `setErrorDetails(normalizedErrorDetails)` from the interceptor-normalized error (or from the catch block using `error.normalizedErrorDetails`).  
     - Remove inline `<AIErrorDisplay error={...} errorDetails={...} />` from that screen (the single instance in layout/Provider will show it).  
     - Ensure retry/dismiss actions call `clearError()` or `setErrorDetails(null)` and then retry the request or navigate as needed.

3. **Backward compatibility during migration**  
   - Until all screens are migrated, the single error display in layout can coexist with any remaining inline displays (e.g. if a screen still sets both context and local state, prefer context so the global display updates).  
   - After full migration, remove any duplicate error state and display from remaining pages.

4. **Cleanup**  
   - Remove deprecated props or duplicate types from `ai-error-display.tsx` if any.  
   - Ensure all API call paths (including `ai-providers.ts`) use the interceptor and normalized shape; no ad-hoc `error_details` construction outside the normalizer.

**Verification**:

- **V5.1** — For each migrated screen: trigger a 404 or 500 (or timeout) for that screen’s API call; confirm the global error UI appears with correct correlation ID and message; retry/dismiss works.  
- **V5.2** — Full regression: run through main user flows (e.g. create material, edit material, AI generate, providers list); confirm no `alert()`, no missing correlation ID, and no dead-end error screens.  
- **V5.3** — Manual trigger of 404/500 from at least two different screens; verify Correlation ID is visible in the UI and matches request/response (or client-generated UUID when no response).

---

## Verification Summary Table

| Phase | Verification | Pass criteria |
|-------|--------------|----------------|
| 1     | V1.1         | Every API request has `X-Correlation-ID` header (UUID) in Network tab. |
| 1     | V1.2         | 404/500 response produces normalized error with UUID `correlation_id`. |
| 1     | V1.3         | Timeout produces client-side normalized error with UUID `correlation_id`. |
| 2     | V2.1         | TypeScript build clean; no `any` for error payload at interceptor/display. |
| 2     | V2.2         | Single type file; extendable for new backend fields. |
| 3     | V3.1         | Setting error via context shows error UI. |
| 3     | V3.2         | No prop drilling for error display after Phase 4. |
| 4     | V4.1         | API error set via context displays in refactored component with correlation ID. |
| 4     | V4.2         | Render throw → Error Boundary fallback with Retry/Go home. |
| 4     | V4.3         | (Optional) Boundary can show correlation ID when error was API-related. |
| 5     | V5.1         | Per-screen: 404/500/timeout shows global error with correlation ID. |
| 5     | V5.2         | No alert(); no dead-end errors; main flows pass. |
| 5     | V5.3         | 404/500 from two+ screens; correlation ID visible and correct. |

---

## Dependencies and Ordering

- **Phase 1** must be done first (interceptor + normalizer produce the shape and UUID).
- **Phase 2** can be done in parallel with Phase 1 or immediately after; types are needed before Phase 3/4.
- **Phase 3** (Provider) should be in place before Phase 4 so the display can consume context.
- **Phase 4** (display refactor + boundary) depends on Phase 2 types and Phase 3 context.
- **Phase 5** (migration) follows Phase 4; each screen can be migrated incrementally.

---

## Optional Artifacts

- **research.md**: If choosing between `uuid` and `crypto.randomUUID()`, document decision (e.g. use `crypto.randomUUID()` when available, else `uuid` v4 for Node/older browsers).
- **data-model.md**: Short entity summary (ErrorDetails, ErrorProvider state, Boundary props).
- **quickstart.md**: Steps to run frontend, trigger 404/500/timeout, and verify correlation ID in UI and Network tab.

---

## Complexity Tracking

No constitution violations. This section is intentionally left empty.
