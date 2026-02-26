# Frontend Architecture

This document describes key architectural decisions for the AI Marketing Agent frontend, including the API client layer and the Materials module.

---

## API Client Standards

### UUID Correlation IDs

- Every request sent through the shared Axios instance (`frontend/src/services/api.ts`) receives a **correlation ID** (UUID v4) via the `X-Correlation-ID` header.
- The response interceptor attaches **normalized error details** to rejected errors, including `correlation_id` and `user_message`, so that UI and logs can report failures in a consistent way without logging raw error objects.
- Use `getErrorLogContext(error)` from `@/services/api` when handling API errors to get `correlation_id` and `user_message` for logging or user-facing messages.

### Base URL (Isomorphic)

- **Client (browser)**: `baseURL` is `http://localhost:8088/api/v1` so the user’s browser talks to the backend on the host machine.
- **Server (SSR / Docker)**: `baseURL` is `http://web:8000/api/v1` so the Next.js container talks to the backend over the Docker network.
- There is no trailing slash on `baseURL`; callers use resource-relative paths (e.g. `materials`, `notifications/unread-count`).

---

## Defensive URL Stripping (API Normalization Layer)

To avoid **path duplication** and 404s, the request interceptor in `api.ts` normalizes the request path before Axios builds the final URL:

- **Problem**: If a caller passes a full path (e.g. `/api/v1/materials` or `/api/notifications/unread-count`) while `baseURL` is already `.../api/v1`, the combined URL can become `.../api/v1/api/v1/...` or `.../api/v1/api/...`, which the backend does not register.
- **Solution**: The interceptor strips leading slashes, then repeatedly strips the prefixes `api/v1/` and `api/` from the path. The result is always a resource-relative path (e.g. `materials`, `notifications/unread-count`), so the final request is `baseURL + '/' + path` → e.g. `http://localhost:8088/api/v1/materials`.
- **Convention**: New code should pass **resource-relative paths only**. The stripping is defensive so that legacy or mistaken full paths still produce correct URLs.

See `specs/005-materials-page-stability/api-normalization-layer.md` for the full specify/clarify documentation.

---

## Materials Module: Real Backend API (No LocalStorage Mocks)

- The Materials list and all material operations (get, create, update, delete, images, feedback, stage) use the **real backend API** via the shared Axios client.
- **No demo data or localStorage fallback**: `frontend/src/services/materials.ts` no longer uses in-memory demo materials or localStorage; it calls `GET /api/v1/materials` (and related endpoints) and throws on failure so the UI can show loading and error states with retry.
- The materials list page (`app/[locale]/materials/page.tsx`) shows loading state, error state with retry, or the list from the API; it does not render mock or cached demo materials from localStorage.
- A short-lived **in-memory cache** (e.g. 30s TTL) may be used for the list response only to avoid redundant requests; it is invalidated on create/update/delete and is not persisted to localStorage.

---

## Related Docs

- `specs/005-materials-page-stability/spec.md` — Feature spec (materials page stability).
- `specs/005-materials-page-stability/plan.md` — Implementation plan and verification.
- `specs/005-materials-page-stability/api-normalization-layer.md` — API Normalization Layer specify/clarify.
