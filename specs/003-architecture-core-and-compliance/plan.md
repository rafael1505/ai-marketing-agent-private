# Implementation Plan: Architecture Core & Compliance

**Branch**: `003-architecture-core-and-compliance` | **Date**: 2026-02-23 | **Spec**: [spec.md](./spec.md)
**Input**: Legacy `spec/process/architecture-guidelines.speckit.md` + 54-task compliance backlog

---

## Summary

Formalize the architecture governance spec and address the highest-priority
structural violations in the codebase: backup/test files in production source,
live debug endpoints, materials route business logic leakage, and AI generation
route bypassing the service layer. Deliver the MCP Connector contract document
as the foundation for all future AI provider refactoring.

---

## Technical Context

**Language/Version**: Python 3.11 (backend), Node 20 (frontend); Docker Compose V2 for orchestration.
**Primary Dependencies**: FastAPI/uvicorn (backend), Next.js 14 (frontend), Motor (MongoDB async driver).
**Storage**: MongoDB 4.4 (Docker container, port 27017).
**Testing**: pytest (backend); all new service code requires unit tests.
**Target Platform**: Local development on Linux/macOS/WSL; Cursor IDE.
**Project Type**: Architecture compliance + process documentation.

---

## Architectural Guidelines Applied

- **ARCH-LAYER-001**: Three-layer rule — routes → services → DB access.
- **ARCH-LAYER-005**: No backup/fix/test files in source; moved to `debug/`.
- **ARCH-MCP-001–005**: MCP Connector contract defined in `docs/mcp-connector-contract.md`.
- **ARCH-MAT-001–004**: Material 3-stage lifecycle rules formalized.
- **PR-BE-003/004/005**: Service layer ownership, DB access pattern, error_details.

---

## Changes Planned

### Spec Migration
- Replaced legacy 86-line informal `architecture-guidelines.speckit.md` with formal
  Process Spec (ARCH-LAYER, ARCH-MCP, ARCH-MAT, ARCH-ENV rules + 5 critical tasks).

### ARCH-LAYER-005 Cleanup (Commit 1)
- `app/api/v1/api.py`: removed `auth_test` from production router
- `app/api/v1/ai_providers_backup.py`: purged (mock data, not imported)
- `app/api/v1/ai_providers_new.py`: purged (in-memory storage, not imported)
- `app/api/v1/auth_test.py`: moved to `debug/` (was live in production)
- `app/core/auth_fixed.py`: moved to `debug/` (not imported, insecure JWT bypasses)

### ARCH-T001 — MCP Connector Contract (Commit 2)
- Create `docs/mcp-connector-contract.md`

### ARCH-T002+T003 — materials.py Audit + Refactor (Commits 3–4)
- Audit violations → `docs/architecture-audit.md`
- Create `app/services/material_service.py`
- Refactor route to thin controller
- Add pytest unit tests

### ARCH-T004+T005 — ai_generation.py Audit + Refactor (Commits 5–6)
- Audit violations → `docs/architecture-audit.md`
- Create `app/services/ai_generation_service.py`
- Refactor route; wire error_details with correlation_id
- Add pytest unit tests
