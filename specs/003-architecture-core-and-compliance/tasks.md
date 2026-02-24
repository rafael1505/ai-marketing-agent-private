# Task List: Architecture Core & Compliance (003)

**Branch**: `003-architecture-core-and-compliance`
**Date completed**: 2026-02-23
**Status**: ALL TASKS COMPLETED

**Total Tasks**: 111
**Completed**: 111 / 111 (100%)

---

## Phase 0 — Spec Formalization & Legacy Cleanup

### Architecture Spec Migration

- [x] **T-001** — Replace 86-line informal `architecture-guidelines.speckit.md` with formal Process Spec
- [x] **T-002** — ARCH-LAYER-001: Define Three-Layer Rule (routes → services → DB access); document violations
- [x] **T-003** — ARCH-LAYER-002: Serialisation helpers must live in services or `app/core/`, not route files
- [x] **T-004** — ARCH-LAYER-003: Prohibit `print()` in route handlers or services; mandate `logging.getLogger`
- [x] **T-005** — ARCH-LAYER-004: All route files must live in `app/api/v1/`
- [x] **T-006** — ARCH-LAYER-005: No backup/fix/test files in `app/api/v1/` or `app/services/`
- [x] **T-007** — ARCH-MCP-001–005: Document MCP Connector contract rules (interface, registry, config, add/remove, errors)
- [x] **T-008** — ARCH-MAT-001–004: Document material 3-stage lifecycle rules (pipeline, transitions, metadata, guard)
- [x] **T-009** — ARCH-ENV-001–004: Lock port rules (8088/3001/27017); prohibit port changes as debugging method
- [x] **T-010** — Define ARCH-T001–T005 as formal critical tasks with acceptance criteria
- [x] **T-011** — Define ARCH-T006–T008 as tracked debt items (out of scope for branch 003)

### ARCH-LAYER-005 File Cleanup

- [x] **T-012** — Delete `app/api/v1/ai_providers_backup.py` (pure mock data, never imported)
- [x] **T-013** — Delete `app/api/v1/ai_providers_new.py` (in-memory storage, violates PR-STACK-004)
- [x] **T-014** — Remove `auth_test` router entry from `app/api/v1/api.py`
- [x] **T-015** — Move `app/api/v1/auth_test.py` → `debug/` (was live in production router)
- [x] **T-016** — Move `app/core/auth_fixed.py` → `debug/` (insecure JWT bypasses, not imported)

---

## ARCH-T001 — MCP Connector Contract

- [x] **T-017** — Create `docs/mcp-connector-contract.md` with `MCPConnector` Protocol definition (5 async methods)
- [x] **T-018** — Document `MCPConnectorError` dataclass with `error_details` property schema
- [x] **T-019** — Document Registry/Factory pattern — `registry.get(provider_id)` as sole resolution point
- [x] **T-020** — Document Add/Remove runbook (zero route or frontend changes for new providers)
- [x] **T-021** — Document Correlation ID propagation rules
- [x] **T-022** — Document 8-item compliance checklist

---

## ARCH-T002 — Audit `app/api/v1/materials.py`

- [x] **T-023** — Create `docs/architecture-audit.md`
- [x] **T-024** — Document MAT-V001: `serialize_material()` defined in route file (ARCH-LAYER-002)
- [x] **T-025** — Document MAT-V002: `serialize_materials()` defined in route file (ARCH-LAYER-002)
- [x] **T-026** — Document MAT-V003/V004: `MaterialDB` and `get_db_collection` instantiated in 9 handlers
- [x] **T-027** — Document MAT-V005: `delete_material` calls `collection.delete_one()` directly
- [x] **T-028** — Document MAT-V006: `add_generated_image` embeds inline AI generation call (CROSS-V001)
- [x] **T-029** — Document MAT-V007: `import json` inside handler body
- [x] **T-030** — Document MAT-V008: 6 `print()` calls in route handlers
- [x] **T-031** — Document MAT-V009: `update_stage` calls `material_db.update_stage()` directly from route
- [x] **T-032** — Document MAT-V010: `select_image` lacks finalization guard
- [x] **T-033** — Document MAT-V011: `add_generated_image` handler is 52 lines (exceeds 50-line limit)

---

## ARCH-T004 — Audit `app/api/v1/ai_generation.py`

- [x] **T-034** — Document GEN-V001: `get_provider_manager()` called in all 4 handlers
- [x] **T-035** — Document GEN-V002: `manager.refresh_provider_configs()` called in 3 handlers
- [x] **T-036** — Document GEN-V003: Parallel vs. single generation decision in route handler
- [x] **T-037** — Document GEN-V004: Result processing block (lines 60–87) in route handler
- [x] **T-038** — Document GEN-V005: `get_provider_status()` and `get_recommended_provider()` in routes
- [x] **T-039** — Document GEN-V006: Routes bypass MCPConnector contract, call `AIProviderManager` directly
- [x] **T-040** — Document GEN-V007–V011: All error paths missing `error_details` and `correlation_id`
- [x] **T-041** — Document GEN-V012: Unreachable code at line 220
- [x] **T-042** — Document GEN-V013: `generate_image_with_provider` handler is 87 lines
- [x] **T-043** — Document 2 cross-file coupling violations (materials → AI layer hidden coupling)

---

## ARCH-T003 Phase 1 — DB Layer Cleanup

- [x] **T-044** — `app/db/material.py`: add `import logging` and `logger = logging.getLogger(__name__)`
- [x] **T-045** — `app/db/material.py`: remove 97-line `test_company` mock-data seeding block
- [x] **T-046** — `app/db/material.py`: simplify cursor handling to `.to_list(length=limit)` throughout
- [x] **T-047** — `app/db/material.py`: replace all 22 `print()` calls with `logger.debug()`
- [x] **T-048** — `app/db/material.py`: add `delete(material_id)` method
- [x] **T-049** — `app/db/material.py`: remove unused `MaterialUpdate` import
- [x] **T-050** — `app/db/base.py`: replace 4 `print()` calls with `logger.debug()` / `logger.warning()`
- [x] **T-051** — `app/db/base.py`: remove unused imports (`Type`, `BaseModel`, `TYPE_CHECKING`, `AsyncIOMotorCollection`)
- [x] **T-052** — Verify `ruff check app/db/material.py app/db/base.py` — All checks passed

---

## ARCH-T003 Phase 2 — Material Service & Unit Tests

- [x] **T-053** — Create `app/services/__init__.py` (package init)
- [x] **T-054** — Create `app/services/material_service.py` — `serialize_material()` and `serialize_materials()` helpers
- [x] **T-055** — Implement `material_service._make_db()` — single `MaterialDB` construction point
- [x] **T-056** — Implement `material_service.create()`, `get()`, `list_materials()`, `update()`, `delete()`
- [x] **T-057** — Implement `material_service.add_generated_image()`, `add_feedback()`
- [x] **T-058** — Implement `material_service.select_image()` with ARCH-MAT-004 finalization guard (HTTP 422)
- [x] **T-059** — Implement `material_service.transition_stage()` as exclusive stage-transition entry point (ARCH-MAT-002)
- [x] **T-060** — Create `tests/__init__.py`, `tests/unit/__init__.py`, `tests/unit/services/__init__.py`
- [x] **T-061** — Add `pytest>=7.4.0` and `pytest-asyncio>=0.21.0` to `requirements.txt`
- [x] **T-062** — Create `tests/unit/services/test_material_service.py` — 29 unit tests
- [x] **T-063** — Test: `serialize_material` and `serialize_materials` (4 tests)
- [x] **T-064** — Test: `create`, `get`, `list_materials`, `update`, `delete` — success + 404/403 paths (15 tests)
- [x] **T-065** — Test: `add_generated_image`, `add_feedback`, `transition_stage` (6 tests)
- [x] **T-066** — Test: `select_image` finalization guard — 422 on empty list, 422 on absent key, success (3 tests)
- [x] **T-067** — Verify `pytest tests/unit/services/test_material_service.py` — 29 passed
- [x] **T-068** — Update `docs/architecture-audit.md` — mark MAT-V001, V002, V009, V010 RESOLVED

---

## ARCH-T003 Phase 3 — Materials Route Thinning

- [x] **T-069** — Remove module-level `serialize_material` / `serialize_materials` from route
- [x] **T-070** — Remove all 9 `MaterialDB(get_db_collection(...))` instantiation sites from handlers
- [x] **T-071** — Replace `add_generated_image` query-param signature with `GeneratedImageInput` Pydantic body model
- [x] **T-072** — Remove inline `free_provider.generate_image()` call and provider-identity branch (CROSS-V001)
- [x] **T-073** — Remove `import json` inside handler body and all `json.loads()` calls
- [x] **T-074** — Remove `materials_collection.delete_one()` direct call; delegate to `material_service.delete()`
- [x] **T-075** — Remove all 6 `print()` calls from route handlers
- [x] **T-076** — Rewrite all 9 handlers as: `db = request.app.mongodb` → `return await material_service.method(...)`
- [x] **T-077** — Verify no `print`, `MaterialDB`, `get_db_collection`, `free_provider`, `serialize_material` remain
- [x] **T-078** — Verify `ruff check app/api/v1/materials.py` — All checks passed
- [x] **T-079** — Update `docs/architecture-audit.md` — mark MAT-V003–V008, V011 RESOLVED

---

## ARCH-T005 Phase 1 — AI Generation Service & Unit Tests

- [x] **T-080** — Create `app/services/ai_generation_service.py` — `_error_details()` helper (ARCH-MCP-005)
- [x] **T-081** — Create `_normalise_error_details()` — backfills schema gaps from older provider code paths
- [x] **T-082** — Create `_refreshed_manager(db)` — wraps `get_provider_manager()` + `refresh_provider_configs()`
- [x] **T-083** — Implement `generate_image()` — parallel/single decision, correlation_id propagation, error schema
- [x] **T-084** — Implement `get_available_providers()` — delegates to registry; no static provider lists
- [x] **T-085** — Implement `get_recommended_provider()` — registry resolution; fallback to test provider
- [x] **T-086** — Implement `refresh_configs()` — explicit config refresh for use after settings updates
- [x] **T-087** — Create `tests/unit/services/test_ai_generation_service.py` — 24 unit tests
- [x] **T-088** — Test: `_error_details` and `_normalise_error_details` helpers (5 tests)
- [x] **T-089** — Test: `generate_image` — single success, parallel path, provider failure, null error_details,
  exception, auto-cid, refresh invariant, cost/model fields (9 tests)
- [x] **T-090** — Test: `get_available_providers` — success, all fields, exception path (3 tests)
- [x] **T-091** — Test: `get_recommended_provider` — known provider, fallback, exception, auto-cid (4 tests)
- [x] **T-092** — Test: `refresh_configs` — success, exception path (2 tests)
- [x] **T-093** — Verify `pytest tests/unit/services/test_ai_generation_service.py` — 24 passed
- [x] **T-094** — Update `docs/architecture-audit.md` — mark GEN-V001–V011 PARTIAL, GEN-V012/V013 OPEN

---

## ARCH-T005 Phase 2 — AI Generation Route Thinning

- [x] **T-095** — Add `_cid(request)` helper — extracts `X-Correlation-ID` header or generates UUID
- [x] **T-096** — Rewrite `generate_image_with_provider` — `_cid` + `db` + `ai_generation_service.generate_image()`
- [x] **T-097** — Rewrite `generate_multiple_images` — delegates to `ai_generation_service.generate_image()`
- [x] **T-098** — Rewrite `list_available_providers` — delegates to `ai_generation_service.get_available_providers()`
- [x] **T-099** — Rewrite `get_recommended_provider` — delegates to `ai_generation_service.get_recommended_provider()`
- [x] **T-100** — Remove unreachable dead code (former line 220: `provider_status = manager.get_provider_status()`)
- [x] **T-101** — Remove all direct `AIProviderManager` access, `get_provider_manager`, `refresh_provider_configs`,
  `traceback`, `import json` (inline), `HTTPException`, `Body`, `Depends`
- [x] **T-102** — Verify largest handler is ≤ 50 lines (generate_image_with_provider: 15 lines)
- [x] **T-103** — Verify `ruff check app/api/v1/ai_generation.py` — All checks passed
- [x] **T-104** — Verify `pytest tests/unit/services/` — 53 passed (24 AI generation + 29 materials)
- [x] **T-105** — Update `docs/architecture-audit.md` — mark GEN-V001–V013 all RESOLVED
- [x] **T-106** — Update `specs/003-architecture-core-and-compliance/plan.md` — final historical record
- [x] **T-107** — Create `specs/003-architecture-core-and-compliance/tasks.md` — this file

---

## Phase 9 — Infrastructure Refinement

- [x] **T-108** — Define `@runtime_checkable` MCPConnector Protocol (`app/services/mcp_connector.py`)
- [x] **T-109** — Implement MCPRegistry with provider resolution logic (`app/core/mcp_registry.py`)
- [x] **T-110** — Inject MCPRegistry into ai_generation_service (`_get_registry(db)`, `registry.get_underlying_manager()`)
- [x] **T-111** — Validate unit tests (24/24 AI generation tests passed with Registry injection)

---

## Completion Summary

| Phase | Tasks | Completed |
|-------|-------|-----------|
| Phase 0 — Spec Formalization + Legacy Cleanup (16 tasks) | 16 | 16 ✓ |
| ARCH-T001 — MCP Connector Contract (6 tasks) | 6 | 6 ✓ |
| ARCH-T002 — Audit materials.py (11 tasks) | 11 | 11 ✓ |
| ARCH-T004 — Audit ai_generation.py (10 tasks) | 10 | 10 ✓ |
| ARCH-T003 Phase 1 — DB Layer Cleanup (9 tasks) | 9 | 9 ✓ |
| ARCH-T003 Phase 2 — Material Service + Tests (16 tasks) | 16 | 16 ✓ |
| ARCH-T003 Phase 3 — Materials Route Thinning (11 tasks) | 11 | 11 ✓ |
| ARCH-T005 Phase 1 — AI Generation Service + Tests (15 tasks) | 15 | 15 ✓ |
| ARCH-T005 Phase 2 — AI Generation Route Thinning (13 tasks) | 13 | 13 ✓ |
| Phase 9 — Infrastructure Refinement (4 tasks) | 4 | 4 ✓ |
| **Total** | **111** | **111 ✓** |

**All tasks completed on branch `003-architecture-core-and-compliance`, 2026-02-23 (Phase 9: 2026-02-24).**
