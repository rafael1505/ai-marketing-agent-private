# Architecture Guidelines Implementation Plan

**Generated from**: `spec/process/architecture-guidelines.speckit.md`  
**Date**: February 19, 2026  
**Status**: Implementation Plan

---

## Executive Summary

This plan ensures the AI Marketing Agent codebase fully complies with the architecture guidelines defined in `spec/process/architecture-guidelines.speckit.md`. The plan identifies current compliance status, gaps, and concrete steps to achieve full architectural alignment.

---

## Current Compliance Assessment

### ✅ **Compliant Areas**

1. **Layered Architecture**
   - ✅ API Layer: Routes properly located in `app/api/v1/endpoints/`
   - ✅ Service Layer: Business logic in `app/services/` (e.g., `ai_provider_service.py`)
   - ✅ Data Access Layer: Database operations in `app/db/mongodb.py` using Motor
   - ✅ Frontend Structure: Pages in `frontend/src/app/[locale]/`, components in `frontend/src/components/`

2. **AI Provider Architecture**
   - ✅ Database-driven: Providers loaded from `mongodb.ai_providers` collection
   - ✅ No hardcoding: Frontend fetches via `/api/v1/ai-providers` endpoint
   - ✅ Service pattern: `AIProviderService` handles provider management

3. **Material Creation Workflow**
   - ✅ 3-stage pipeline implemented (Idea → Refinement → Finalization)
   - ✅ Stage tracking via `stage` and `status` fields

4. **Environment & Ports**
   - ✅ Backend on port 8088 (configured in `app/main.py`)
   - ✅ Frontend on port 3001 (configured in `next.config.js`)
   - ✅ MongoDB on port 27017 (Docker)

---

## Gaps & Improvements Needed

### 🔴 **Critical: Standardize All External Connections on MCP**

**Issue**: External integrations must consistently use MCP connectors with a shared contract and registry to make adding/removing connections low-friction.

**Action Items**:
1. **Define MCP Connection Contract**
   - Create a shared interface for connector lifecycle operations (connect, validate, execute, health-check, disconnect).
   - Ensure connector implementations are swappable and testable.
2. **Implement/Enforce Registry Pattern**
   - Centralize connector resolution (by provider/integration ID).
   - Remove direct provider branching from route layer.
3. **Support Easy Add/Remove Workflow**
   - Adding a connection = implement connector + register + config.
   - Removing a connection = unregister/disable + cleanup config, without route rewrites.

**Files to Review**:
- `app/services/ai_provider_service.py`
- `app/ai_providers/provider_manager.py`
- `app/api/v1/ai_generation.py`
- `app/api/v1/ai_providers.py`

---

### 🔴 **Critical: Verify Thin Controllers**

**Issue**: Need to audit API route handlers to ensure they're thin (validation + service calls only).

**Action Items**:
1. **Audit API Routes** (`app/api/v1/endpoints/`)
   - Review each route handler for business logic leakage
   - Ensure all business logic delegates to `app/services/` modules
   - Document any violations found

2. **Create Validation Checklist**
   - Route handlers should only:
     - Validate request data (Pydantic models)
     - Call service methods
     - Map service results to HTTP responses
     - Handle HTTP-specific concerns (status codes, headers)

**Files to Review**:
- `app/api/v1/materials.py`
- `app/api/v1/ai_generation.py`
- `app/api/v1/companies.py`
- `app/api/v1/users.py`
- `app/api/v1/auth.py`

---

### 🟡 **Moderate: Frontend Service Layer Consistency**

**Issue**: Need to ensure all frontend API calls go through centralized service layer.

**Action Items**:
1. **Audit Frontend API Calls**
   - Verify all API calls use `frontend/src/services/` modules
   - Check for direct `fetch()` or `axios` calls in components/pages
   - Ensure consistent error handling via `AIErrorDisplay`

2. **Standardize API Client Pattern**
   - All API calls should use `apiRequest()` from `frontend/src/services/api.ts`
   - Ensure correlation IDs are attached to all requests
   - Verify timeout handling (60s for AI generation)

**Files to Review**:
- `frontend/src/app/[locale]/materials/**/*.tsx`
- `frontend/src/app/[locale]/settings/**/*.tsx`
- `frontend/src/components/**/*.tsx`

---

### 🟡 **Moderate: Database Index Strategy**

**Issue**: Need to verify MongoDB indexes are properly defined and maintained.

**Action Items**:
1. **Review Index Definitions**
   - Check `app/db/mongodb.py` for `create_indexes()` method
   - Verify indexes exist for:
     - `materials`: `user_id`, `company_id`, `stage`, `status`
     - `ai_providers`: `user_id`, `id`
     - `companies`: `user_id`
     - `users`: `email` (unique)

2. **Document Index Strategy**
   - Create or update `docs/MONGODB_ARCHITECTURE.md` with index documentation
   - Ensure indexes align with query patterns

---

### 🟢 **Low Priority: Architecture Documentation**

**Issue**: Architecture guidelines should be reflected in codebase documentation.

**Action Items**:
1. **Update Architecture Docs**
   - Ensure `docs/MONGODB_ARCHITECTURE.md` reflects current architecture
   - Add architecture diagram showing layers (API → Service → DB)
   - Document AI provider integration flow

2. **Create Architecture Decision Records (ADRs)**
   - Document why database-driven providers were chosen
   - Document why 3-stage material workflow is required
   - Document port configuration rationale

---

## Implementation Tasks

### Phase 1: Compliance Verification (Week 1)

#### Task 1.0: Define MCP Connection Contract & Registry Baseline
- [ ] Create architecture note for MCP connector contract (required methods and error model)
- [ ] Document registry responsibilities (resolve connector, validate availability, lifecycle management)
- [ ] Map current integrations to MCP connectors and identify non-compliant direct integrations
- [ ] Define add/remove runbook for connections (add = register/configure, remove = unregister/cleanup)

**Acceptance Criteria**:
- One shared MCP connector contract is defined and approved.
- Registry pattern is documented and referenced by integration services.
- A compliance matrix exists for all active connections.

---

#### Task 1.1: Audit API Route Handlers
- [ ] Review `app/api/v1/materials.py` for business logic in routes
- [ ] Review `app/api/v1/ai_generation.py` for business logic in routes
- [ ] Review `app/api/v1/companies.py` for business logic in routes
- [ ] Review `app/api/v1/users.py` for business logic in routes
- [ ] Review `app/api/v1/auth.py` for business logic in routes
- [ ] Document violations (if any) in `docs/architecture-audit.md`
- [ ] Refactor any routes that contain business logic to delegate to services

**Acceptance Criteria**:
- All route handlers are < 50 lines (excluding validation models)
- All business logic calls service methods
- No database queries directly in route handlers

---

#### Task 1.2: Verify Service Layer Coverage
- [ ] Ensure `app/services/` contains all business logic
- [ ] Verify services are properly imported and used by routes
- [ ] Check for duplicate business logic across routes

**Acceptance Criteria**:
- Every route handler delegates to a service method
- Services are testable (no direct HTTP dependencies)
- Business logic is not duplicated across routes

---

### Phase 2: Frontend Architecture Alignment (Week 2)

#### Task 2.1: Audit Frontend API Calls
- [ ] Search for direct `fetch()` calls in components/pages
- [ ] Search for direct `axios` imports (should use `apiRequest` wrapper)
- [ ] Verify all API calls use `frontend/src/services/` modules
- [ ] Ensure error handling uses `AIErrorDisplay` component

**Acceptance Criteria**:
- No direct `fetch()` or `axios` calls in components/pages
- All API calls go through service layer (`frontend/src/services/`)
- All errors displayed via `AIErrorDisplay` with correlation IDs

---

#### Task 2.2: Standardize API Client Usage
- [ ] Ensure `apiRequest()` is used consistently
- [ ] Verify correlation IDs are attached to all requests
- [ ] Check timeout configuration (60s for AI generation)
- [ ] Ensure error enrichment (timeout detection, correlation IDs)

**Acceptance Criteria**:
- All API calls use `apiRequest()` wrapper
- Correlation IDs present in all requests
- Timeout handling consistent across API calls

---

#### Task 2.3: Enforce MCP-Backed Integration Endpoints
- [ ] Verify frontend never couples to provider-specific behavior beyond metadata and capabilities
- [ ] Ensure backend endpoints expose provider/integration-agnostic contracts where possible
- [ ] Confirm enabling/disabling a connector does not require frontend code changes

**Acceptance Criteria**:
- Frontend behavior remains stable when connectors are added/removed via config.
- Backend endpoint contracts are MCP-oriented, not provider-hardcoded.

---

### Phase 3: Database & Infrastructure (Week 3)

#### Task 3.1: Verify MongoDB Indexes
- [ ] Review `app/db/mongodb.py` for index creation
- [ ] Verify indexes match query patterns
- [ ] Document index strategy in `docs/MONGODB_ARCHITECTURE.md`

**Acceptance Criteria**:
- Indexes exist for all frequently queried fields
- Index creation runs on application startup
- Index strategy documented

---

#### Task 3.2: Verify AI Provider Database Integration
- [ ] Confirm all provider loading goes through `mongodb.ai_providers`
- [ ] Verify no hardcoded provider lists in code
- [ ] Check frontend fallback behavior (should fail gracefully, not use localStorage)
- [ ] Verify all provider execution paths use MCP connectors (no direct SDK calls from route layer)

**Acceptance Criteria**:
- No hardcoded provider arrays in code
- All providers loaded from database
- Frontend handles database unavailability gracefully
- Provider execution is fully MCP-mediated

---

### Phase 4: Documentation & Validation (Week 4)

#### Task 4.1: Update Architecture Documentation
- [ ] Update `docs/MONGODB_ARCHITECTURE.md` with current architecture
- [ ] Create architecture diagram (API → Service → DB layers)
- [ ] Document AI provider integration flow

**Acceptance Criteria**:
- Architecture docs reflect current implementation
- Diagrams show layer separation
- Integration flows documented

---

#### Task 4.2: Create Architecture Validation Tests
- [ ] Create tests that verify route handlers don't contain business logic
- [ ] Create tests that verify services don't have HTTP dependencies
- [ ] Create tests that verify database-driven providers (no hardcoding)

**Acceptance Criteria**:
- Tests exist to validate architecture compliance
- Tests run in CI/CD pipeline
- Violations fail tests

---

## Success Metrics

### Compliance Metrics
- **API Route Thinness**: 100% of routes delegate to services
- **Service Layer Coverage**: 100% of business logic in services
- **Frontend Service Usage**: 100% of API calls through service layer
- **Database-Driven Providers**: 0 hardcoded provider lists
- **MCP Integration Coverage**: 100% of external connections use MCP connector contract + registry

### Quality Metrics
- **Test Coverage**: >80% for service layer
- **Documentation**: Architecture docs up-to-date
- **Code Review**: Architecture violations caught in PR reviews

---

## Risk Mitigation

### Risk 1: Breaking Changes During Refactoring
- **Mitigation**: Refactor incrementally, one module at a time
- **Testing**: Run full test suite after each refactor
- **Rollback**: Keep git history clean for easy rollback

### Risk 2: Performance Impact from Service Layer
- **Mitigation**: Profile service calls, optimize if needed
- **Monitoring**: Add performance metrics to service calls

### Risk 3: Frontend Breaking Changes
- **Mitigation**: Test frontend thoroughly after API changes
- **Validation**: Ensure error handling still works

---

## Next Steps

1. **Immediate**: Start Phase 1, Task 1.0 (Define MCP Connection Contract & Registry Baseline)
2. **This Week**: Complete Phase 1 compliance verification
3. **Next Week**: Begin Phase 2 frontend alignment
4. **Ongoing**: Use Spec Kit `/speckit.tasks` to generate detailed task lists for each phase

---

## References

- **Constitution**: `spec/constitution/project-constitution.speckit.md`
- **Architecture Guidelines**: `spec/process/architecture-guidelines.speckit.md`
- **Development Best Practices**: `spec/process/development-best-practices.speckit.md`
- **MongoDB Architecture**: `docs/MONGODB_ARCHITECTURE.md`
