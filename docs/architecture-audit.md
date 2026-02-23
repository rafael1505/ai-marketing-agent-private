# Architecture Audit

**Document ID**: `ARCH-AUDIT-001`
**Branch**: `003-architecture-core-and-compliance`
**Spec reference**: `spec/process/architecture-guidelines.speckit.md`
**Created**: 2026-02-23
**Status**: Authoritative — do not edit sections marked CLOSED

---

## How to Read This Document

Each finding entry uses this format:

```
[VIOLATION-ID] Rule violated — description
  File: path/to/file.py, line(s) N
  Evidence: <exact code or quote>
  Remediation task: ARCH-TN
  Status: OPEN | CLOSED
```

Violations are grouped by source file. Cross-file dependencies are called out
explicitly in Section 3.

---

## Section 1 — `app/api/v1/materials.py` (ARCH-T002)

**Audit scope**: All 9 route handlers, module-level helpers, and imports.
**Audited against**: ARCH-LAYER-001, ARCH-LAYER-002, ARCH-LAYER-003,
ARCH-MAT-002, ARCH-MAT-004, and the 50-line handler rule.

---

### 1.1 ARCH-LAYER-002 — Serialization helpers defined in route file

**[MAT-V001]** `ARCH-LAYER-002` — `serialize_material()` defined in route file.

```
File: app/api/v1/materials.py, lines 21–26
Evidence:
  def serialize_material(material: dict) -> dict:
      """Convert MongoDB ObjectId to string for JSON serialization"""
      if material and "_id" in material:
          material["id"] = str(material["_id"])
          del material["_id"]
      return material
```

Remediation task: **ARCH-T003** — move to `app/services/material_service.py`.
Status: **RESOLVED** — moved to `app/services/material_service.py` (commit e8c2a99+)

---

**[MAT-V002]** `ARCH-LAYER-002` — `serialize_materials()` defined in route file.

```
File: app/api/v1/materials.py, lines 28–30
Evidence:
  def serialize_materials(materials: list) -> list:
      """Convert list of MongoDB materials to JSON-serializable format"""
      return [serialize_material(mat.copy()) for mat in materials]
```

Remediation task: **ARCH-T003** — move to `app/services/material_service.py`.
Status: **RESOLVED** — moved to `app/services/material_service.py` (commit e8c2a99+)

---

### 1.2 ARCH-LAYER-001 — DB access and business logic in route handlers

**[MAT-V003]** `ARCH-LAYER-001` — `MaterialDB` instantiated in every route handler.

`MaterialDB` is constructed nine times across the route file, once per handler:

| Handler | Line |
|---------|------|
| `create_material` | 45 |
| `list_materials` | 65 |
| `get_material` | 95 |
| `update_material` | 113 |
| `add_generated_image` | 141 |
| `select_image` | 192 |
| `add_feedback` | 213 |
| `update_stage` | 239 |
| `delete_material` | 262 |

The DB access object (`MaterialDB`) MUST be instantiated inside the service layer,
not in route handlers. Routes receive `mongodb` from `request.app.mongodb` and
pass it into the service; the service is responsible for constructing `MaterialDB`.

Remediation task: **ARCH-T003**.
Status: **OPEN**

---

**[MAT-V004]** `ARCH-LAYER-001` — `get_db_collection()` called in every handler.

`get_db_collection(mongodb, "materials")` is called in the same nine handlers as
MAT-V003 (lines 44, 64, 94, 112, 140, 191, 212, 238, 261). Collection resolution
is infrastructure setup; it belongs in the service initialisation path, not in
route handlers.

Remediation task: **ARCH-T003**.
Status: **OPEN**

---

**[MAT-V005]** `ARCH-LAYER-001` — `delete_material` calls Motor collection directly,
bypassing `MaterialDB`.

```
File: app/api/v1/materials.py, lines 274–283
Evidence:
  result = await materials_collection.delete_one({"_id": ObjectId(material_id)})
  if result.deleted_count == 0:
      raise HTTPException(status_code=404, detail="Material not found")
  ...
  print(f"Error deleting material: {e}")
```

The route holds a raw `Motor` collection reference and executes a MongoDB write
directly. This skips `MaterialDB` entirely and places a DB query inside a route
handler — a double violation of ARCH-LAYER-001.

Remediation task: **ARCH-T003** — add `MaterialDB.delete(material_id)` and call
it from the service.
Status: **OPEN**

---

**[MAT-V006]** `ARCH-LAYER-001` + `ARCH-MCP-001` — AI provider call inside route
handler `add_generated_image`.

```
File: app/api/v1/materials.py, lines 155–165
Evidence:
  if ai_provider == "free-test-provider":
      try:
          from app.ai_providers.free_provider import free_provider
          generated_image = free_provider.generate_image(
              prompt=prompt,
              size=parsed_params.get('size', '1024x1024'),
              style=parsed_params.get('style', 'photorealistic')
          )
          url = generated_image['url']
      except Exception as e:
          pass
```

A route handler is performing provider-identity branching (`if ai_provider ==
"free-test-provider"`), directly importing and calling an AI provider SDK
(`free_provider.generate_image()`), and silently swallowing exceptions.
This violates:
- ARCH-LAYER-001 (business logic in route)
- ARCH-MCP-001 (SDK call bypasses MCPConnector interface)
- ARCH-MCP-002 (provider identity branching instead of registry resolution)

The exception `pass` also means failures are invisible.

Remediation task: **ARCH-T003** (materials side) + **ARCH-T005** (connector side).
Status: **OPEN**

---

**[MAT-V007]** `ARCH-LAYER-001` — `import json` inside handler body.

```
File: app/api/v1/materials.py, line 149
Evidence: import json
```

Module-level imports placed inside a function body are a PEP 8 violation (also
PR-BE-001). Minor, but tracked for completeness.

Remediation task: **ARCH-T003** — move `import json` to module top-level.
Status: **OPEN**

---

### 1.3 ARCH-LAYER-003 — `print()` statements in route file

Six `print()` calls in route handlers (ARCH-LAYER-003 requires `logging.getLogger`):

| Line | Statement |
|------|-----------|
| 39 | `print(f"[CREATE_MATERIAL] Received request from user: ...")` |
| 40 | `print(f"[CREATE_MATERIAL] Material data: ...")` |
| 41 | `print(f"[CREATE_MATERIAL] Stage: {material.stage}, Status: ...")` |
| 68 | `print(f"list_materials called with company_id: ...")` |
| 79 | `print(f"Found {len(materials)} materials")` |
| 282 | `print(f"Error deleting material: {e}")` |

**[MAT-V008]** `ARCH-LAYER-003` — six `print()` calls in `app/api/v1/materials.py`.

Remediation task: **ARCH-T003** — remove all; replace with `logger = logging.getLogger(__name__)`.
Status: **OPEN**

---

> **Note — `app/db/material.py`**: A further 22 `print()` calls exist in
> `app/db/material.py` (lines 39, 40, 48, 53, 57, 70, 78, 80, 85, 138, 155, 168,
> 174, 177, 181, 193, 195, 209, 212, 218 and others). These violate ARCH-LAYER-003
> at the DB layer. Remediation is in scope for ARCH-T003, which will refactor the
> full stack for materials.

---

### 1.4 ARCH-MAT-002 — Stage transition executed in route handler

**[MAT-V009]** `ARCH-MAT-002` — `update_stage` route writes `stage`/`status` to
MongoDB directly from the route via `material_db.update_stage()`.

```
File: app/api/v1/materials.py, lines 230–251
Evidence:
  updated_material = await material_db.update_stage(material_id, stage, status)
```

Stage transitions MUST be performed exclusively in `material_service`. The route
MUST NOT know about `stage` or `status` field names; it calls the service which
applies business rules and writes to the DB layer.

Remediation task: **ARCH-T003** — introduce `material_service.transition_stage()`.
Status: **RESOLVED** — `transition_stage()` implemented in `app/services/material_service.py`; route refactor (Phase 3) will remove the direct DB call from the route.

---

### 1.5 ARCH-MAT-004 — Finalization guard absent

**[MAT-V010]** `ARCH-MAT-004` — `select_image` route triggers `material_db.select_image()`
without verifying that `generated_images` is non-empty.

```
File: app/api/v1/materials.py, lines 182–202
Evidence: no guard on generated_images before calling material_db.select_image()
```

A material with zero generated images MUST NOT reach finalization. The guard MUST
live in `material_service`, not in the route.

Remediation task: **ARCH-T003** — add pre-condition in `material_service.select_image()`:
raise `422 Unprocessable Entity` with `error_details` if `generated_images` is empty.
Status: **RESOLVED** — guard implemented in `material_service.select_image()`; raises
`HTTPException(422, detail={"error_type": "finalization_guard", ...})`; covered by
3 unit tests in `tests/unit/services/test_material_service.py::TestSelectImage`.

---

### 1.6 50-Line Handler Rule (ARCH-LAYER-001)

**[MAT-V011]** `ARCH-LAYER-001` — `add_generated_image` exceeds 50 lines.

```
File: app/api/v1/materials.py, lines 129–180 (52 lines)
```

Excessive length is a symptom of the business logic (MAT-V006) embedded in the
handler. Remediation of MAT-V006 will bring this under the limit.

Remediation task: **ARCH-T003**.
Status: **OPEN**

---

### 1.7 Summary — `materials.py`

| ID | Rule | Line(s) | Severity | Task |
|----|------|---------|----------|------|
| MAT-V001 | ARCH-LAYER-002 | 21–26 | High | ARCH-T003 | **RESOLVED** |
| MAT-V002 | ARCH-LAYER-002 | 28–30 | High | ARCH-T003 | **RESOLVED** |
| MAT-V003 | ARCH-LAYER-001 | 9 sites | High | ARCH-T003 | OPEN (Phase 3) |
| MAT-V004 | ARCH-LAYER-001 | 9 sites | High | ARCH-T003 | OPEN (Phase 3) |
| MAT-V005 | ARCH-LAYER-001 | 274–283 | High | ARCH-T003 | OPEN (Phase 3) |
| MAT-V006 | ARCH-LAYER-001 + ARCH-MCP-001/002 | 155–165 | Critical | ARCH-T003/T005 | OPEN (Phase 3) |
| MAT-V007 | PR-BE-001 (PEP 8) | 149 | Low | ARCH-T003 | OPEN (Phase 3) |
| MAT-V008 | ARCH-LAYER-003 | 39–41, 68, 79, 282 | High | ARCH-T003 | OPEN (Phase 3) |
| MAT-V009 | ARCH-MAT-002 | 230–251 | High | ARCH-T003 | **RESOLVED** |
| MAT-V010 | ARCH-MAT-004 | 182–202 | Critical | ARCH-T003 | **RESOLVED** |
| MAT-V011 | ARCH-LAYER-001 (50-line) | 129–180 | Medium | ARCH-T003 | OPEN (Phase 3) |

**Total violations in `materials.py`: 11** (2 critical, 7 high, 1 medium, 1 low)

---

## Section 2 — `app/api/v1/ai_generation.py` (ARCH-T004)

**Audit scope**: All 4 route handlers and module-level code.
**Audited against**: ARCH-LAYER-001, ARCH-MCP-001, ARCH-MCP-002, ARCH-MCP-005,
and the 50-line handler rule.

---

### 2.1 ARCH-LAYER-001 — Business logic in every route handler

**[GEN-V001]** `ARCH-LAYER-001` — `get_provider_manager()` called in all four handlers.

```
File: app/api/v1/ai_generation.py
  Line 33:  manager = get_provider_manager(database_client=getattr(request.app, 'mongodb', None))
  Line 125: manager = get_provider_manager(database_client=getattr(request.app, 'mongodb', None))
  Line 161: manager = get_provider_manager(database_client=getattr(request.app, 'mongodb', None))
  Line 195: manager = get_provider_manager(database_client=getattr(request.app, 'mongodb', None))
```

Provider manager instantiation/lookup is infrastructure initialisation. It belongs
in the service layer (or app startup), not in route handlers.

Remediation task: **ARCH-T005**.
Status: **OPEN**

---

**[GEN-V002]** `ARCH-LAYER-001` — `manager.refresh_provider_configs()` awaited in
three handlers.

```
File: app/api/v1/ai_generation.py
  Line 36:  await manager.refresh_provider_configs()
  Line 128: await manager.refresh_provider_configs()
  Line 164: await manager.refresh_provider_configs()
  Line 197: await manager.refresh_provider_configs()
```

Config refresh is a service-layer concern. Calling it on every request in the route
adds unnecessary latency and couples the route to the manager's internal API.
The service MUST own this, called only when provider settings change.

Remediation task: **ARCH-T005**.
Status: **OPEN**

---

**[GEN-V003]** `ARCH-LAYER-001` — Parallel vs. single generation decision inside
`generate_image_with_provider`.

```
File: app/api/v1/ai_generation.py, lines 53–58
Evidence:
  if request_body.variations > 1:
      result = await manager.generate_images_parallel(request_body.ai_provider, generation_request)
  else:
      result = await manager.generate_image(request_body.ai_provider, generation_request)
```

The decision of whether to use parallel or sequential generation is business logic.
It MUST live in `ai_generation_service.generate()`, not in the route handler.

Remediation task: **ARCH-T005**.
Status: **OPEN**

---

**[GEN-V004]** `ARCH-LAYER-001` — Result processing (logging image URLs, manual JSON
serialisation check) in route handler.

```
File: app/api/v1/ai_generation.py, lines 64–84
Evidence:
  for i, img_url in enumerate(result.images):
      logger.info(f"Image {i+1} URL length: ...")
      logger.info(f"Image {i+1} URL preview: ...")
  ...
  json_response = json.dumps(response_data)
  logger.info(f"Response successfully serialized to JSON: ...")
```

Iterating over result images, logging per-image diagnostics, and pre-serialising
the response dict to verify JSON compatibility are all business/diagnostic logic.
Route handlers MUST only map service results to HTTP responses.

Remediation task: **ARCH-T005**.
Status: **OPEN**

---

**[GEN-V005]** `ARCH-LAYER-001` — `manager.get_provider_status()` and
`manager.get_recommended_provider()` called directly in route handlers.

```
File: app/api/v1/ai_generation.py
  Lines 166, 201: manager.get_provider_status()
  Line 200:        manager.get_recommended_provider(features)
```

Provider status aggregation and recommendation logic belong in the service layer.

Remediation task: **ARCH-T005**.
Status: **OPEN**

---

### 2.2 ARCH-MCP-001 / ARCH-MCP-002 — No MCPConnector interface; no registry

**[GEN-V006]** `ARCH-MCP-001` + `ARCH-MCP-002` — Routes bypass the `MCPConnector`
Protocol and call `AIProviderManager` methods directly; no registry resolution.

```
File: app/api/v1/ai_generation.py (multiple sites)
Evidence: manager.generate_image(), manager.generate_images_parallel(),
          manager.get_provider_status(), manager.get_recommended_provider()
```

The `AIProviderManager` is not a `MCPConnector`-compliant registry. Routes call
it directly, performing implicit provider selection via the manager's internal
priority list (`get_recommended_provider`) rather than via `registry.get(provider_id)`.
All connector resolution MUST go through `MCPRegistry` as defined in
`docs/mcp-connector-contract.md` Section 4.

Remediation task: **ARCH-T005**.
Status: **OPEN**

---

### 2.3 ARCH-MCP-005 — Missing `error_details` and `correlation_id`

No handler generates a `correlation_id`. Every error path examined below returns
a bare `HTTPException` with a `detail` string, in violation of ARCH-MCP-005 and
`PR-BE-005`.

**[GEN-V007]** `ARCH-MCP-005` — `generate_image_with_provider`: two non-compliant
error paths.

```
File: app/api/v1/ai_generation.py

Path 1 — lines 98–100 (result.error_details is None):
  raise HTTPException(status_code=500, detail=result.error)
  # Missing: error_details dict, correlation_id, user_message i18n key

Path 2 — lines 106–111 (unexpected exception):
  raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")
  # Missing: error_details dict, correlation_id, error_type, http_status
```

Status: **OPEN**

---

**[GEN-V008]** `ARCH-MCP-005` — `generate_multiple_images`: two non-compliant
error paths.

```
File: app/api/v1/ai_generation.py

Path 1 — line 151:
  raise HTTPException(status_code=500, detail=result.error)

Path 2 — lines 153–154:
  raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")
```

Both missing `error_details`, `correlation_id`, `user_message`.
Status: **OPEN**

---

**[GEN-V009]** `ARCH-MCP-005` — `list_available_providers`: non-compliant error path.

```
File: app/api/v1/ai_generation.py, lines 184–185
  raise HTTPException(status_code=500, detail=f"Failed to get provider status: {str(e)}")
```

Status: **OPEN**

---

**[GEN-V010]** `ARCH-MCP-005` — `get_recommended_provider`: non-compliant error path.

```
File: app/api/v1/ai_generation.py, lines 217–218
  raise HTTPException(status_code=500, detail=str(e))
```

Status: **OPEN**

---

**[GEN-V011]** `ARCH-MCP-005` — No `correlation_id` generated at route entry in any
handler; not propagated to service or returned in response headers.

All four handlers are missing:
```python
correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
```

As specified in `docs/mcp-connector-contract.md` Section 6.
Status: **OPEN**

---

### 2.4 Dead Code

**[GEN-V012]** — Unreachable statement after `return` in `get_recommended_provider`.

```
File: app/api/v1/ai_generation.py, line 220
Evidence:
  # This line is after the final return/raise block of get_recommended_provider:
  provider_status = manager.get_provider_status()
```

This assignment on line 220 is unreachable. It indicates the function was edited
without accounting for control flow. A linter (`ruff`) would flag this as dead code.
Remove unconditionally.

Remediation task: **ARCH-T005**.
Status: **OPEN**

---

### 2.5 50-Line Handler Rule (ARCH-LAYER-001)

**[GEN-V013]** `ARCH-LAYER-001` — `generate_image_with_provider` is 87 lines
(lines 26–112), 74% over the 50-line limit.

The excess is caused by GEN-V003 (dispatch logic), GEN-V004 (result processing),
and GEN-V007 (duplicated error branches). Remediating those violations will bring
the handler under the limit.

Remediation task: **ARCH-T005**.
Status: **OPEN**

---

### 2.6 Summary — `ai_generation.py`

| ID | Rule | Line(s) | Severity | Task |
|----|------|---------|----------|------|
| GEN-V001 | ARCH-LAYER-001 | 33, 125, 161, 195 | High | ARCH-T005 |
| GEN-V002 | ARCH-LAYER-001 | 36, 128, 164, 197 | High | ARCH-T005 |
| GEN-V003 | ARCH-LAYER-001 | 53–58 | High | ARCH-T005 |
| GEN-V004 | ARCH-LAYER-001 | 64–84 | Medium | ARCH-T005 |
| GEN-V005 | ARCH-LAYER-001 | 166, 200–201 | High | ARCH-T005 |
| GEN-V006 | ARCH-MCP-001/002 | All handlers | Critical | ARCH-T005 |
| GEN-V007 | ARCH-MCP-005 | 98–100, 106–111 | Critical | ARCH-T005 |
| GEN-V008 | ARCH-MCP-005 | 151, 153–154 | Critical | ARCH-T005 |
| GEN-V009 | ARCH-MCP-005 | 184–185 | Critical | ARCH-T005 |
| GEN-V010 | ARCH-MCP-005 | 217–218 | Critical | ARCH-T005 |
| GEN-V011 | ARCH-MCP-005 | All handlers | Critical | ARCH-T005 |
| GEN-V012 | Dead code | 220 | Low | ARCH-T005 |
| GEN-V013 | ARCH-LAYER-001 (50-line) | 26–112 | Medium | ARCH-T005 |

**Total violations in `ai_generation.py`: 13** (6 critical, 4 high, 2 medium, 1 low)

---

## Section 3 — Cross-File Dependencies and Coupling

This section documents structural dependencies between the two audited files and
across the layer boundary, as required by the `/speckit.clarify` analysis.

---

### 3.1 Materials route → AI provider layer (hidden coupling)

**[CROSS-V001]** `app/api/v1/materials.py` line 158 imports directly from
`app/ai_providers.free_provider`:

```python
from app.ai_providers.free_provider import free_provider
```

This creates an import dependency from the **route layer** into the **AI provider
implementation layer**, skipping both the service layer (`app/services/`) and the
MCP connector contract. The coupling is hidden inside a try/except block, so it
is not visible in the module-level imports.

**Impact on refactoring**: ARCH-T003 cannot be completed cleanly without also
addressing this coupling. The `add_generated_image` service method must call the
AI generation service (ARCH-T005), not the provider SDK directly. This means
ARCH-T003 has a partial dependency on ARCH-T005's service being available, or the
free-provider call must be removed as part of ARCH-T003 and the frontend must be
updated to call `/api/v1/ai-generation/generate-image` separately.

**Recommended resolution**: Remove the inline provider call from
`add_generated_image` entirely. The route `POST /{id}/images` stores an image URL
that was already returned by a prior call to `/generate-image`. It should never
need to generate images itself.

---

### 3.2 Shared violation: no `error_details` on any error path

Both files fail ARCH-MCP-005. Neither constructs `error_details` with
`correlation_id`, `user_message` (i18n key), or `http_status`. This is a
systemic gap — not an isolated oversight. The fix requires:

1. A `correlation_id` generated at each route entry and threaded through.
2. A shared `build_error_response()` utility (in `app/core/` or per service).
3. All `HTTPException` raises replaced with structured `JSONResponse` carrying
   the full `error_details` schema.

---

### 3.3 Shared violation: `MaterialDB` construction pattern repeated 9 times

The boilerplate:
```python
mongodb = request.app.mongodb
materials_collection = get_db_collection(mongodb, "materials")
material_db = MaterialDB(materials_collection)
```

appears verbatim in every `materials.py` handler. This is a copy-paste pattern
that will drift when `MaterialDB`'s constructor signature changes. The service
layer must own this construction — handlers pass `request.app.mongodb` to the
service as a single argument.

---

### 3.4 `ai_generation.py` → `materials.py` implicit contract gap

The two routes participate in a two-step frontend flow:

1. Frontend calls `POST /ai-generation/generate-image` → receives image URLs.
2. Frontend calls `POST /materials/{id}/images` → stores image URLs into the material.

There is no transactional guarantee between these two steps. If Step 2 fails,
the generated images are lost. A future task (not in scope for this branch) should
consider a single `ai_generation_service.generate_and_attach()` method that
performs both operations atomically at the service layer.

This is documented here as a **design debt** item, not a rule violation.

---

## Section 4 — Violations Requiring Action Before ARCH-T003/T005

The following pre-conditions MUST be satisfied before the refactoring tasks begin:

| Pre-condition | Relevant violations | Note |
|---|---|---|
| `app/services/material_service.py` does not yet exist | MAT-V001–V011 | Create in ARCH-T003 |
| `app/services/ai_generation_service.py` does not yet exist | GEN-V001–V013 | Create in ARCH-T005 |
| `MCPRegistry` does not yet exist | GEN-V006 | Wire in ARCH-T005 using contract from ARCH-T001 |
| `MaterialDB.delete()` does not exist | MAT-V005 | Add in ARCH-T003 |
| No `error_details` utility exists | GEN-V007–V011, MAT context | Create in ARCH-T003/T005 |

---

## Section 5 — Combined Violation Count

| File | Critical | High | Medium | Low | Total |
|------|----------|------|--------|-----|-------|
| `app/api/v1/materials.py` | 2 | 7 | 1 | 1 | 11 |
| `app/api/v1/ai_generation.py` | 6 | 4 | 2 | 1 | 13 |
| Cross-file | 0 | 1 | 1 | 0 | 2 |
| **Total** | **8** | **12** | **4** | **2** | **26** |

All 26 violations are **OPEN**. No violation is in scope for debt tracking
(ARCH-T006/T007/T008); all are remediated by ARCH-T003 or ARCH-T005.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-02-23 | Initial audit created for ARCH-T002 (materials.py) and ARCH-T004 (ai_generation.py). 26 violations documented across 2 files plus cross-file coupling analysis. |
| 2026-02-23 | ARCH-T003 Phase 1: DB layer cleaned (material.py, base.py) — print() replaced, test_company seeding removed, cursor simplified. |
| 2026-02-23 | ARCH-T003 Phase 2: material_service.py created. MAT-V001, MAT-V002 (serialisation helpers), MAT-V009 (transition_stage), MAT-V010 (finalization guard) marked RESOLVED. 29 unit tests passing. |
