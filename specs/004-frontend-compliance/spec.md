# Feature Specification: UX & Frontend Compliance

**Feature Branch**: `004-frontend-compliance`  
**Created**: 2026-02-24  
**Status**: Draft  
**Input**: Establish architectural compliance in the Frontend (Next.js/TypeScript): robust Error Boundaries, rigorous TypeScript interfaces that mirror backend (Pydantic) contracts, and a global error-handling strategy that leverages the new backend correlation IDs.

## Context & Dependencies

- **Backend (Feature 003)**: API now delivers structured `error_details` and `correlation_id` via the Service Layer. All error paths return a consistent schema (see `docs/mcp-connector-contract.md`).
- **Branch**: `004-frontend-compliance` created from a clean main. No application code changes until after specify → clarify → plan → task cycle.

## Clarifications

### Session 2026-02-24

- **Q: Client-Side ID Generation** — In case of local network failure (e.g., DNS error or timeout), should the interceptor use a library like `uuid` to generate a client-side `correlation_id` so the UI always displays one?  
  **A:** Yes. The interceptor MUST generate a client-side correlation ID using a UUID (e.g. via a `uuid` library or `crypto.randomUUID()`) whenever the backend did not return one (e.g. timeout, network/DNS error). This ensures a consistent format (UUID) with the backend and guarantees the UI always has a displayable, traceable ID.

- **Q: Header Strategy** — Should the correlation ID be injected into request headers (e.g. `X-Correlation-ID`) by default for all API calls to facilitate end-to-end tracing?  
  **A:** Yes. The correlation ID MUST be injected by default into request headers (e.g. `X-Correlation-ID`) for all API calls so the backend can log and return the same ID, enabling end-to-end tracing without per-call opt-in.

- **Q: Component Refactoring** — For the migration of the error display component, should we follow a wrapper approach (HOC or Provider) to inject error handling logic without manual prop drilling in every screen?  
  **A:** Yes. Use a Provider (or equivalent wrapper) to inject error handling logic so screens do not need to manually pass error state and display props through every level. Prefer a context-based Provider for flexibility and to avoid prop drilling; HOC is an acceptable alternative where it fits the codebase. The single error display component remains the canonical UI; the Provider/wrapper supplies the structured error payload and recovery callbacks.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consistent Error Display with Backend Traceability (Priority: P1)

When any API call fails, the user sees a single, consistent error experience: a clear message (from i18n), optional suggested actions, and a correlation ID they or support can use to trace the failure end-to-end. Errors never appear as raw alerts or unhandled blank screens.

**Why this priority**: Ensures the value of the backend’s structured errors (and correlation IDs) is realized in the UI and that UX-003d/003e are satisfied.

**Independent Test**: Trigger an API failure (e.g. provider unavailable or timeout); confirm the UI shows the standard error component with a correlation ID, no `alert()`, and that the same ID can be correlated with backend logs if available.

**Acceptance Scenarios**:

1. **Given** the backend returns a response with `error_details` (including `correlation_id`, `user_message`, `error_type`, `provider`, `http_status`, `details`), **When** the frontend receives it, **Then** the error is displayed using the designated error component, with the user message resolved via i18n and the correlation ID visible (e.g. in technical details).
2. **Given** an API request fails before a response (e.g. network error or timeout), **When** the client handles the failure, **Then** the frontend builds a conforming error payload that includes a client-generated correlation ID and displays it in the same standard error component.
3. **Given** any error path, **When** the user sees the error, **Then** they are never shown a browser `alert()` or a dead-end screen without an actionable path (retry, switch provider, or support message).

---

### User Story 2 - Contract-Aligned Type Safety (Priority: P1)

The frontend uses TypeScript types that faithfully reflect the backend’s error and success contracts. Compile-time checks prevent mismatches (e.g. missing or misspelled fields), and a single source of truth defines the shape of API error payloads consumed by the UI.

**Why this priority**: Prevents drift between backend and frontend and reduces runtime bugs from shape mismatches.

**Independent Test**: After defining interfaces that mirror the backend `error_details` schema and relevant API response shapes, verify that all call sites that pass data into the error display (and API client) use these types; TypeScript build passes with no `any` for these structures.

**Acceptance Scenarios**:

1. **Given** the backend’s canonical `error_details` schema (error_type, user_message, provider, correlation_id, http_status, details), **When** the frontend defines types for API responses, **Then** there exists a single TypeScript interface (or type) that mirrors this schema and is used wherever error details are consumed or displayed.
2. **Given** any API response that carries `error_details`, **When** the response is parsed and passed to the error display component, **Then** the types enforce presence of required fields (e.g. correlation_id, user_message) and optional fields (e.g. details) so that missing or malformed data is caught at compile time where possible.
3. **Given** new backend fields added to `error_details` in the future, **When** the contract document is updated, **Then** the frontend types are updated in one place and the UI (e.g. technical details section) can be extended without ad-hoc type assertions.

---

### User Story 3 - Application Resilience via Error Boundaries (Priority: P2)

When a React component tree throws an unhandled exception (e.g. during render or in a lifecycle method), the application does not show a blank screen or crash the entire app. A boundary catches the error and shows a fallback UI that offers recovery (e.g. retry or go home) and, where appropriate, reports a correlation ID for support.

**Why this priority**: Completes the resilience story beyond API errors and protects users from unrecoverable white screens.

**Independent Test**: Introduce a deliberate render-time error in a page component; confirm an error boundary catches it and displays the fallback UI. Optionally verify that the boundary can display or log a correlation ID when the error is associated with a failed request.

**Acceptance Scenarios**:

1. **Given** any page or section of the app, **When** an unhandled JavaScript error occurs in that subtree, **Then** an error boundary catches it and displays a user-friendly fallback (e.g. message, retry, link to home) instead of a blank or broken page.
2. **Given** the error boundary fallback is visible, **When** the failure was triggered by or related to an API call, **Then** the fallback can show or log the same correlation ID that the backend uses, so support can trace the issue.
3. **Given** the user sees the fallback, **When** they choose “Retry” or “Go home”, **Then** the application recovers (e.g. re-renders or navigates) without requiring a full page reload where feasible.

---

### User Story 4 - Global API Error Interceptor Strategy (Priority: P2)

All outbound API requests use a single, centralized mechanism that (a) attaches a correlation ID to the request (e.g. header), (b) on error, normalizes the response or client-side failure into the same structured error shape expected by the UI, and (c) ensures that correlation ID from the response (or a client-generated one) is always available for display and logging.

**Why this priority**: Ensures every API error path—including timeouts and network failures—is handled consistently and supports the same UX and traceability as backend-returned errors.

**Independent Test**: Call multiple endpoints (e.g. AI generation, materials, providers); trigger success and failure (including timeout and network error). Confirm request header carries correlation ID and that every error path produces a single structured shape with correlation_id and that the UI receives it.

**Acceptance Scenarios**:

1. **Given** any API request, **When** the request is sent, **Then** a correlation ID is set (e.g. in a request header); if the backend returns one in the response, that same ID is preferred for display and logging.
2. **Given** an API response with status 4xx/5xx and a body containing `error_details`, **When** the interceptor processes the response, **Then** it exposes a normalized error object (including correlation_id and user_message) to the caller so the UI can pass it directly to the error display component.
3. **Given** a request that fails without a response (timeout, network error, or CORS), **When** the interceptor handles the failure, **Then** it builds a structured error object that includes a client-generated correlation ID and a sensible user_message key (e.g. timeout or network) so the same error component can render it.

---

### Edge Cases

- **Malformed or partial `error_details` from backend**: Frontend MUST validate or normalize so that required fields (e.g. correlation_id, user_message) have fallbacks (e.g. client-generated ID, generic i18n key) rather than crashing or showing raw undefined values.
- **Multiple rapid failures**: Correlation IDs MUST remain distinct per request so that logs and support can distinguish concurrent failures.
- **Error boundary and API error both fire**: If an API error triggers a component to throw, the error boundary catches the throw; the boundary fallback SHOULD still be able to show or log the correlation ID from the API error if it was captured before the throw.
- **Server-side rendering (SSR)**: Error handling and correlation ID strategy MUST work for client-side API calls; any SSR-specific failures (e.g. during getServerSideProps or server components) SHOULD be documented so that future SSR error handling can reuse the same correlation and display patterns.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The frontend MUST display all API-driven errors through a single, designated error display component. That component MUST accept a structured error payload that includes at least: a user-facing message (or i18n key), a correlation ID, and optional provider/type/details. It MUST NOT use `alert()` or raw `console.error()` as the only user feedback (UX-003d).
- **FR-002**: Every structured error shown to the user MUST include a correlation ID. If the backend did not return one, the frontend MUST generate a client-side ID (UUID format, e.g. via a `uuid` library or `crypto.randomUUID()`) and attach it before display (UX-003e).
- **FR-003**: TypeScript interfaces MUST mirror the backend’s canonical `error_details` schema. Required fields: error_type, user_message, provider, correlation_id, http_status. Optional: details. Any extra client-only fields (e.g. timestamp, suggested_actions) MUST be documented and added in a single place (e.g. API client or normalizer) so that backend contract remains the source of truth for API shape.
- **FR-004**: A global API client (or interceptor) MUST add a correlation ID (UUID) to every outbound request by default, via a request header (e.g. `X-Correlation-ID`). On error, it MUST normalize both backend-returned `error_details` and client-side failures (timeout, network/DNS) into one consistent shape consumed by the error display component; for client-side-only failures it MUST generate a UUID as correlation_id.
- **FR-005**: The application MUST use at least one error boundary that catches unhandled React errors in the component tree and displays a fallback UI with recovery options (e.g. retry, go home). Where the error is tied to an API call, the fallback SHOULD surface or log the same correlation ID.
- **FR-006**: After any recoverable error, the user MUST have an actionable path forward (retry, switch provider, or support message). Dead-end error screens are not acceptable (UX-003f).
- **FR-007**: User-visible error messages MUST be resolved via the application’s i18n mechanism using the `user_message` key from the backend (or an equivalent key for client-generated errors). Raw backend strings MUST NOT be shown as the primary message (UX-004e).

### Key Entities

- **Structured error payload (error_details)**: The canonical shape of an error as produced by the backend (and normalized on the frontend). Fields: error_type, user_message, provider, correlation_id, http_status, details (optional). This is the contract that frontend types must mirror.
- **Correlation ID**: A unique identifier (e.g. UUID) generated at the request boundary (backend or client). Used in request/response headers and in error payloads so that support and logs can trace a single request across frontend and backend.
- **Error display component**: The single UI component responsible for rendering errors (e.g. card with message, correlation ID in technical details, retry/switch provider/support actions). Must accept the structured error payload and i18n context. Error handling logic (state and display) SHOULD be injected via a Provider or equivalent wrapper so screens do not rely on manual prop drilling.
- **Error boundary**: A React component that catches JavaScript errors in its child tree and renders a fallback UI instead of a blank or crashed page.
- **API error interceptor**: The centralized logic that runs on every API request/response (or equivalent). It MUST inject a correlation ID (UUID) into every request via a header (e.g. `X-Correlation-ID`) by default, and MUST normalize all error responses and client-side failures (timeout, network/DNS) into the structured error payload, generating a UUID when the backend did not return one.

## Assumptions

- The backend continues to return `error_details` and to send or accept correlation ID via headers as defined in the MCP connector contract and Feature 003. No backend changes are required for this feature.
- The existing error display component (e.g. AIErrorDisplay) will be refined to accept the contract-aligned type and to never show raw backend strings as the primary message; suggested_actions and other client-side enrichments can remain where they add value.
- Error boundaries are implemented in the frontend framework in use (e.g. React Error Boundaries). No specific third-party library is assumed; the spec requires a fallback UI and recovery options.
- i18n keys for new client-side error cases (e.g. timeout, network error) already exist or will be added in the same scope as this feature (both en and pt per UX-004f).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every API error path (backend-returned and client-side timeout/network) results in the same error component being used, with a correlation ID visible in the UI (e.g. in technical details), and no use of `alert()` for error reporting.
- **SC-002**: Static type checking passes for all call sites that pass error payloads into the error display or API normalizer; a single type definition mirrors the backend error_details schema (no untyped or loosely typed error structures at those call sites).
- **SC-003**: Triggering an unhandled render error in a key page results in an error boundary fallback being shown (with retry or navigation option), not a blank or crashed screen.
- **SC-004**: Outbound API requests include a correlation ID (e.g. in a header); when a request fails, the normalized error object always contains a correlation_id and is consumable by the error display component without ad-hoc mapping.
- **SC-005**: All user-facing error messages are resolved via i18n using the `user_message` key (or equivalent for client-generated errors); no raw backend error strings are shown as the primary message.

---

## Notes for Planning

- **Backend contract reference**: `docs/mcp-connector-contract.md` — Section 3 (Standard Error Model), Section 6 (Correlation ID Propagation).
- **Process specs**: `spec/process/ux-guidelines.speckit.md` (UX-003, UX-004), `spec/process/architecture-guidelines.speckit.md` (ARCH-MCP, cross-ref to UX).
- **Existing frontend**: `frontend/src/components/ui/ai-error-display.tsx`, `frontend/src/services/api.ts`, `frontend/src/services/ai-providers.ts` — types and interceptor to be aligned with this spec.
- **Clarified implementation details**: (1) Client-side correlation ID MUST be UUID (e.g. `uuid` or `crypto.randomUUID()`). (2) Correlation ID MUST be sent by default on all API requests via header (e.g. `X-Correlation-ID`). (3) Use a Provider (or HOC) to inject error handling so screens avoid manual prop drilling; single error display component remains canonical.
