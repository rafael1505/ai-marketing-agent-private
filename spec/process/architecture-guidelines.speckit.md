# Process Specification: Architecture & System Design Guidelines

**Spec ID**: `003-architecture-core-and-compliance`
**Branch**: `003-architecture-core-and-compliance`
**Created**: 2026-02-23
**Status**: Active
**Supersedes**: `spec/process/architecture-guidelines.speckit.md` (legacy informal doc)
**Applies to**: Any structural change, new feature, API modification, or
infrastructure-level work in `ai-marketing-agent-private`.

---

## Purpose

Define the authoritative, enforceable architecture rules for the AI Marketing Agent.
These rules govern how layers communicate, how external connections are managed, and
how the material lifecycle is protected. Any contributor — human or AI agent — MUST
satisfy every rule in this spec before a structural change is considered mergeable.

Cross-references: `PR-BE-003`, `PR-BE-004`, `PR-BE-005` (Development Best Practices);
`BFIX-002` (Bug Fixing Workflow); `UX-003d/003e` (UX Guidelines).

---

## 1. Mandatory Layering

### ARCH-LAYER-001 — The Three-Layer Rule

All backend request handling MUST flow through exactly three layers in order:

```
Request → Route Handler (app/api/v1/)
              ↓
          Service (app/services/)
              ↓
          DB Access (app/db/)
              ↓
          MongoDB (port 27017)
```

No layer may skip another. Specifically:

- **Route handlers** (`app/api/v1/`) MUST NOT contain business logic, data
  transformations, or direct database queries. They may only:
  1. Validate the incoming request (Pydantic models).
  2. Call one or more service methods.
  3. Map the service result to an HTTP response.
  4. A route handler that exceeds 50 lines of non-Pydantic code is a violation.

- **Services** (`app/services/`) contain ALL business logic. Services MUST be
  pure Python — no FastAPI `Request`, `Response`, or `Depends` objects as
  parameters. Services are testable without an HTTP context.

- **DB Access** (`app/db/`) contains all MongoDB queries. Callers MUST use
  the global Motor instance `request.app.mongodb` passed into services by the
  route. Never instantiate a new Motor client anywhere outside `app/db/`.

### ARCH-LAYER-002 — Serialization Helpers Belong in Services

Helper functions that transform data for responses (e.g. `serialize_material`,
`serialize_materials`, `ObjectId` → `str` conversion) MUST live in the relevant
service or a shared utility module (`app/core/`), not in route files.

> **Live violation**: `app/api/v1/materials.py` defines `serialize_material()`
> and `serialize_materials()` directly in the route file. These must be moved to
> `app/services/material_service.py` or `app/core/db_utils.py` (ARCH-T002/T003).

### ARCH-LAYER-003 — No Debug Output in Route Handlers

`print()` statements MUST NOT exist in route handlers or services in any
committed code. Use `logging.getLogger(__name__)` at the appropriate level.

> **Live violation**: `app/api/v1/materials.py` lines 39–42 contain `print()`
> debug statements in the `create_material` handler (ARCH-T002/T003).

### ARCH-LAYER-004 — Canonical Route Path

All route files MUST live in `app/api/v1/`. No route files may exist outside
this path.

> **Tracked debt**: `app/routes/ai_providers.py` exists outside the canonical
> path and must be consolidated or removed in a future task.

### ARCH-LAYER-005 — No Backup, Fix, or Test Files in Source

Files named `*_backup.py`, `*_new.py`, `*_fix.py`, or `*_test.py` MUST NOT
exist in `app/api/v1/` or `app/services/`. These are `debug/` artefacts.

**Resolved in this branch:**
- `app/api/v1/ai_providers_backup.py` — purged (pure mock, no production value)
- `app/api/v1/ai_providers_new.py` — purged (in-memory storage, violates PR-STACK-004)
- `app/api/v1/auth_test.py` — removed from production router + moved to `debug/`
- `app/core/auth_fixed.py` — moved to `debug/`

**Tracked debt (ARCH-T006):**
- `app/api/v1/auth_fix.py` — currently imported by production `companies.py` and
  `auth_handler.py`. Rename/delete requires first migrating its `get_admin_user_formdata`
  and `get_current_user_flexible` dependencies into `app/api/v1/deps.py`.

---

## 2. MCP Connector Contract

### ARCH-MCP-001 — Shared Connector Interface

Every external connection (AI provider, future third-party integration) MUST
implement the following interface. No route or service may call an external
provider SDK directly.

```python
class MCPConnector(Protocol):
    async def connect(self) -> None:
        """Establish and validate the connection."""

    async def disconnect(self) -> None:
        """Tear down the connection cleanly."""

    async def validate(self) -> bool:
        """Validate credentials and configuration. Returns True if ready."""

    async def execute(self, action: str, params: dict) -> dict:
        """Execute a domain action (e.g. generate_image). Returns result dict."""

    async def health_check(self) -> bool:
        """Returns True if the connector is available and responsive."""
```

The interface definition MUST be documented in `docs/mcp-connector-contract.md`
and referenced from this spec.

### ARCH-MCP-002 — Registry / Factory Pattern

A central MCP registry MUST resolve connectors by `provider_id`. Route handlers
and services MUST NOT branch on provider identity (e.g. `if provider == "openai"`).
All resolution is via registry lookup.

```python
connector = registry.get(provider_id)   # only valid resolution pattern
result = await connector.execute("generate_image", params)
```

> **Live violation**: `app/api/v1/ai_generation.py` calls `get_provider_manager()`
> directly in the route handler, bypassing the service layer and performing
> provider selection logic inside the route (ARCH-T004/T005).

### ARCH-MCP-003 — Data-Driven Configuration

Connector configuration (API keys, model names, capabilities, enabled status)
MUST come from the `ai_providers` MongoDB collection. Never hardcode. The registry
reads configuration from the DB on startup and on `refresh_provider_configs()`.

### ARCH-MCP-004 — Add/Remove Protocol

- **Adding a connector**: implement the `MCPConnector` interface → register in
  registry → add DB configuration record. Zero route or frontend code changes.
- **Removing a connector**: unregister from registry → mark disabled in DB.
  Keep API contracts stable for all unaffected providers. Zero route rewrites.

### ARCH-MCP-005 — Standard Connector Error Model

All connector errors MUST surface as an `error_details` dict with the following
fields (per `PR-BE-005`):

```python
{
    "error_type": str,       # e.g. "provider_unavailable"
    "user_message": str,     # i18n key, e.g. "errors.provider.unavailable"
    "provider": str,         # provider_id
    "correlation_id": str,   # UUID, generated at route entry if absent
    "http_status": int,
    "details": dict          # optional, provider-specific diagnostic data
}
```

Never surface raw provider SDK exceptions or stack traces to the HTTP response.

> **Live violation**: `app/api/v1/ai_generation.py` error paths do not return
> `error_details` with `correlation_id` (ARCH-T004/T005).

---

## 3. Material 3-Stage Lifecycle

### ARCH-MAT-001 — Pipeline Integrity

The material creation pipeline has exactly three stages. No feature or fix may
bypass, reorder, or merge stages.

| Stage | `stage` value | `status` value | Entry condition |
|-------|--------------|----------------|-----------------|
| 1 — Idea | `"idea"` | `"draft"` | Material created by user |
| 2 — Refinement | `"idea"` | `"draft"` | AI image generation requested |
| 3 — Finalization | `"finalization"` | `"completed"` | User selects final image |

### ARCH-MAT-002 — Stage Transitions via Service Only

Stage transitions MUST be performed exclusively in `app/services/material_service.py`.
No route handler may directly write `stage` or `status` fields to MongoDB.

### ARCH-MAT-003 — Generated Images Metadata

Images produced during Stage 2 MUST be stored in `material.generated_images[]`
with full metadata (URL, provider, model, generation parameters, timestamp).
The route MUST NOT return raw provider image URLs without this metadata.

### ARCH-MAT-004 — Finalization Guard

Stage 3 transition MUST validate that `generated_images` is non-empty before
setting `stage = "finalization"`. A material with no generated images MUST NOT
reach finalization. This check lives in `material_service`, not in the route.

---

## 4. Frontend Architecture (Reference)

*(Detailed rules in `spec/process/ux-guidelines.speckit.md`. Summary for backend
engineers and AI agents working across the stack.)*

- Pages: `frontend/src/app/[locale]/` — no API calls directly; use services layer.
- Components: `frontend/src/components/` — receive data via props; no direct `fetch`.
- API clients: `frontend/src/services/` — all Axios wrappers; attach `correlation_id`.
- CORS: configured for `localhost:3001` in `app/main.py`. Never widen to `*` in
  production without a security review.

---

## 5. Environment & Port Rules

- ARCH-ENV-001: Backend MUST run on port 8088 (host). Container binds to 8000
  internally; `docker-compose.yml` maps `8088:8000`. Do not change either value.
- ARCH-ENV-002: Frontend MUST run on port 3001. `NEXT_PUBLIC_API_URL` MUST be
  `http://localhost:8088/api/v1`.
- ARCH-ENV-003: MongoDB MUST run on port 27017. All connection strings use
  `mongodb://mongo:27017` (container) or `mongodb://localhost:27017` (host).
- ARCH-ENV-004: Never debug port issues by changing ports. Diagnose the root
  cause per `BFIX-002`.

---

## 6. Top 5 Critical Tasks for Branch 003

These tasks are drawn from `spec/tasks/architecture-compliance-tasks.md`
(Tasks 1.0.1, 1.1.1, 1.1.8, 1.1.2, 1.1.9) and sequenced for this branch.

### ARCH-T001 — Define MCP Connector Contract *(Task 1.0.1)*
**Priority**: Critical — blocks all AI provider refactoring
**Output**: `docs/mcp-connector-contract.md` with the `MCPConnector` Protocol,
standard error model, and add/remove runbook.
**Acceptance**: Contract reviewed and referenced from this spec.

### ARCH-T002 — Audit `app/api/v1/materials.py` *(Task 1.1.1)*
**Priority**: Critical
**Pre-confirmed violations**:
- `serialize_material` / `serialize_materials` helpers in route file (ARCH-LAYER-002)
- `MaterialDB` instantiated directly via `get_db_collection` in route (ARCH-LAYER-001)
- `print()` debug statements in `create_material` (ARCH-LAYER-003)
- No `app/services/material_service.py` exists yet

**Output**: Violations documented in `docs/architecture-audit.md`.

### ARCH-T003 — Refactor `app/api/v1/materials.py` *(Task 1.1.8)*
**Priority**: Critical — depends on ARCH-T002
**Actions**:
1. Create `app/services/material_service.py` with all business logic methods.
2. Move `serialize_material`, stage-transition logic, and `MaterialDB` usage into
   the service.
3. Remove all `print()` statements; replace with `logger`.
4. Route handlers become: validate → call service → return.
5. Add `pytest` unit tests for `material_service.py` (BFIX-001 / PR-TEST-001).

**Acceptance**: Route handlers ≤ 50 lines; `pytest` green; `ruff check .` clean.

### ARCH-T004 — Audit `app/api/v1/ai_generation.py` *(Task 1.1.2)*
**Priority**: Critical
**Pre-confirmed violations**:
- `get_provider_manager()` called directly in route handler (ARCH-LAYER-001, ARCH-MCP-002)
- `manager.refresh_provider_configs()` called in route (ARCH-LAYER-001)
- Parallel vs single generation decision in route (ARCH-LAYER-001)
- No `error_details` with `correlation_id` in error responses (ARCH-MCP-005, PR-BE-005)

**Output**: Violations documented in `docs/architecture-audit.md`.

### ARCH-T005 — Refactor `app/api/v1/ai_generation.py` *(Task 1.1.9)*
**Priority**: Critical — depends on ARCH-T001 and ARCH-T004
**Actions**:
1. Create `app/services/ai_generation_service.py`.
2. Move provider selection, `refresh_provider_configs()`, parallel/single
   generation decision, and result processing into the service.
3. Service calls MCP registry for connector resolution (ARCH-MCP-002).
4. Route handler: validate → call `ai_generation_service.generate()` → return.
5. All errors return `error_details` with `correlation_id` (ARCH-MCP-005).
6. Add `pytest` unit tests for `ai_generation_service.py` (BFIX-001 / PR-TEST-001).

**Acceptance**: Route handler ≤ 50 lines; `error_details` on all error paths;
`pytest` green; `ruff check .` clean.

---

## 7. Tracked Debt (Out of Scope for Branch 003)

| ID | Item | Blocker |
|----|------|---------|
| ARCH-T006 | Migrate `app/api/v1/auth_fix.py` functions into `app/api/v1/deps.py`; update `companies.py` and `auth_handler.py` | Requires audit of FormData auth usage across all routes |
| ARCH-T007 | Remove `app/routes/ai_providers.py` (orphan route outside canonical path) | Requires confirming it is not mounted anywhere |
| ARCH-T008 | Remove hardcoded token bypasses in `app/api/v1/deps.py` (lines 22–88) | Requires real auth token flow validation end-to-end |

---

## 8. Acceptance Criteria

A structural change is **complete** when ALL of the following are true:

| ID | Criterion |
|----|-----------|
| AC-001 | Route handlers contain only validation, service calls, and HTTP mapping (ARCH-LAYER-001). |
| AC-002 | No helper functions, DB access, or business logic defined in route files (ARCH-LAYER-001/002). |
| AC-003 | No `print()` statements in `app/api/v1/` or `app/services/` (ARCH-LAYER-003). |
| AC-004 | All route files live in `app/api/v1/`; no backup/fix/test files in source (ARCH-LAYER-004/005). |
| AC-005 | External connections resolved via MCP registry by `provider_id`; no provider branching in routes (ARCH-MCP-001/002). |
| AC-006 | All errors return `error_details` with `correlation_id`, `user_message` i18n key, and `http_status` (ARCH-MCP-005). |
| AC-007 | Material stage transitions performed only in `material_service`; finalization guard enforced (ARCH-MAT-001–004). |
| AC-008 | `pytest` passes with zero new failures; `ruff check .` passes with zero new errors (PR-TEST-001, BFIX-003). |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-02-23 | Migrated from legacy informal doc; added mandatory layering rules (ARCH-LAYER-001–005) with live violation citations, MCP Connector contract (ARCH-MCP-001–005), Material lifecycle rules (ARCH-MAT-001–004), Top 5 Critical task definitions (ARCH-T001–T005), and Tracked Debt table (ARCH-T006–T008). |
