# Implementation Plan: Migrate Development Best Practices to Formal Spec

**Branch**: `002-migrate-dev-practices` | **Date**: 2026-02-23 | **Spec**: [spec.md](./spec.md)  
**Input**: Legacy `spec/process/development-best-practices.speckit.md`

---

## Summary

Rewrite the existing informal development best-practices document as a formal
Process Specification, incorporating canonical stack standards, strict port
definitions, professional Git protocol, and a new Agent Context Awareness section
(PR-AI-001–005) that mandates AI agents consult `.cursor/rules/specify-rules.mdc`
before writing any code.

---

## Technical Context

**Language/Version**: Python 3.11 (backend), Node 20 (frontend); Docker Compose V2 for orchestration.  
**Primary Dependencies**: FastAPI/uvicorn (backend), Next.js 14 (frontend), shadcn/ui, ruff (linter).  
**Storage**: MongoDB 4.4 (Docker container, port 27017).  
**Testing**: pytest (backend), frontend test framework in `tests/frontend/`.  
**Target Platform**: Local development on Linux/macOS/WSL; Cursor IDE.  
**Project Type**: Process documentation (no runtime changes).  

---

## Changes

- Replaced legacy informal doc with formal Process Spec (7 sections, 26 enforceable rules).
- Added Section 7: Agent Context Awareness (PR-AI-001 through PR-AI-005).
- Updated agent context file (`.cursor/rules/specify-rules.mdc`) via update-agent-context script.
