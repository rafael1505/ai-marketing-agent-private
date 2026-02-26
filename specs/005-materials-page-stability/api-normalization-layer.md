# API Normalization Layer (005 Documentation)

**Branch**: `005-materials-page-stability`  
**Purpose**: Specify and clarify the defensive API normalization added in `frontend/src/services/api.ts` and the transition to real backend data in the Materials module.

---

## 1. Specify: API Normalization Layer Map

### Location

| Artifact | Path | Responsibility |
|----------|------|----------------|
| API client entry | `frontend/src/services/api.ts` | Axios instance, base URL, interceptors |
| Request interceptor | `frontend/src/services/api.ts` (request use) | X-Correlation-ID injection, **URL path normalization** |
| Base URL | `BASE_URL` in api.ts | Isomorphic base: client `http://localhost:8088/api/v1`, server `http://web:8000/api/v1` |
| Response interceptor | `frontend/src/services/api.ts` (response use) | `normalizedErrorDetails`, timeout/network/4xx handling, 401 redirect |
| Callers | `frontend/src/services/materials.ts`, `frontend/src/lib/notification-utils.ts`, etc. | Pass resource-relative paths (e.g. `materials`, `notifications/unread-count`) or full paths; normalization ensures no duplication |

### Data Flow

1. Caller invokes `api.get(url)` or `apiRequest(url, options)` with `url` that may be:
   - Resource-relative: `materials`, `notifications/unread-count` (preferred).
   - Legacy/full: `/api/v1/materials`, `/api/notifications/unread-count`.
2. Request interceptor runs before the request is sent:
   - Strips leading slashes from `url`, then repeatedly strips `api/v1/` and `api/` prefixes.
   - Injects `X-Correlation-ID` (UUID) and `Authorization` if token present.
3. Axios merges `baseURL` + normalized path → final URL (e.g. `http://localhost:8088/api/v1/materials`).
4. Response interceptor attaches `normalizedErrorDetails` (and optional redirect on 401).

### Out of Scope for This Layer

- Next.js rewrites (`next.config.js`) proxy `/api/:path*` to the backend; the normalization layer operates on the Axios client only.
- Backend route registration (`app/api/v1/api.py`, `app/main.py`) is unchanged by this layer.

---

## 2. Clarify: URL Normalization Logic

### The Problem

The Axios client is configured with `baseURL` set to the API base (e.g. `http://localhost:8088/api/v1`). When callers pass a **full path** instead of a **resource-relative path**, the final request URL can contain a duplicated segment and return 404:

- Caller passes: `"/api/v1/materials"` or `"/api/notifications/unread-count"`.
- Axios combines: `baseURL` + path → `http://localhost:8088/api/v1` + `/api/v1/materials` → `http://localhost:8088/api/v1/api/v1/materials` (or similar, depending on how Axios joins).
- Result: backend receives a path like `/api/v1/api/v1/materials` or `/api/v1/api/notifications/...`, which does not match registered routes (e.g. `GET /api/v1/materials`), so the backend returns **404**.

### The Solution: Defensive Stripping

In the request interceptor we normalize the path **before** Axios builds the final URL:

```ts
let u = config.url.replace(/^\/+/, '');
while (u.startsWith('api/v1/')) u = u.slice(7);
while (u.startsWith('api/'))   u = u.slice(4);
config.url = u;
```

- **Why `while` instead of `if`**: Legacy or misconfigured callers may pass paths like `/api/v1/api/notifications/unread-count`. A single strip of `api/v1/` leaves `api/notifications/...`, which would still duplicate when combined with baseURL. Repeating until no `api/v1/` or `api/` prefix remains ensures the path is always a clean resource path (e.g. `notifications/unread-count`).
- **Why strip `api/v1/` first**: So that `api/v1/api/...` becomes `api/...` then `...` in two passes.
- **Convention for new code**: Callers should pass **resource-relative paths only** (e.g. `materials`, `notifications/unread-count`). The normalization is **defensive** so that existing or accidental full paths do not cause 404s.

### Summary

| Input path (example) | After normalization | Final request URL (with baseURL) |
|----------------------|----------------------|-----------------------------------|
| `materials` | `materials` | `.../api/v1/materials` |
| `/api/notifications/unread-count` | `notifications/unread-count` | `.../api/v1/notifications/unread-count` |
| `/api/v1/api/notifications/unread-count` | `notifications/unread-count` | `.../api/v1/notifications/unread-count` |

This prevents URL duplication and ensures the backend receives the correct path regardless of how callers specify the path.
