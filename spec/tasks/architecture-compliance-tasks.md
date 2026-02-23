# Architecture Compliance - Detailed Task List

**Generated from**: `spec/process/architecture-guidelines-implementation-plan.md`  
**Date**: February 19, 2026  
**Last Updated**: February 19, 2026 (MCP alignment)  
**Status**: Ready for Execution

---

## Task Summary

**Total Tasks**: 54  
**Critical Priority**: 16 tasks  
**Moderate Priority**: 24 tasks  
**Low Priority**: 14 tasks

---

## Phase 1: Compliance Verification (Week 1)

### 🔴 Task 1.0.1: Create MCP Connector Contract (Architecture Note)
**Priority**: Critical  
**Estimated Time**: 2 hours  
**Assignee**: TBD

**Steps**:
1. [ ] Create architecture note (e.g. `docs/mcp-connector-contract.md` or section in `docs/ARCHITECTURE.md`)
2. [ ] Define shared MCP connector interface with required methods:
   - `connect` / `disconnect` (lifecycle)
   - `validate` (e.g. API key / config validation)
   - `execute` (domain action, e.g. generate image)
   - `health_check` (availability)
3. [ ] Define standard error model for connectors (error_type, user_message, correlation_id, etc.)
4. [ ] Ensure contract allows swappable, testable connector implementations
5. [ ] Get review/approval from maintainer

**Acceptance Criteria**:
- One shared MCP connector contract is defined and documented
- Required methods and error model are explicit
- Contract is approved for use by integration services

**Files to Create/Update**:
- `docs/mcp-connector-contract.md` or `docs/ARCHITECTURE.md`

---

### 🔴 Task 1.0.2: Document MCP Registry Responsibilities
**Priority**: Critical  
**Estimated Time**: 1 hour  
**Assignee**: TBD  
**Depends on**: Task 1.0.1

**Steps**:
1. [ ] Document registry responsibilities:
   - Resolve connector by provider/integration ID
   - Validate connector availability (enabled/disabled)
   - Lifecycle management (register, unregister, enable, disable)
2. [ ] Document that route layer must not branch on provider ID; resolution is via registry only
3. [ ] Add registry pattern to architecture docs and reference from `spec/process/architecture-guidelines.speckit.md`

**Acceptance Criteria**:
- Registry responsibilities documented
- Pattern is referenced by integration services

---

### 🔴 Task 1.0.3: Map Integrations to MCP Connectors & Compliance Matrix
**Priority**: Critical  
**Estimated Time**: 2 hours  
**Assignee**: TBD  
**Depends on**: Task 1.0.1

**Steps**:
1. [ ] List all current external integrations (AI providers, future third-party)
2. [ ] For each integration, document:
   - Current implementation (direct SDK vs service vs MCP)
   - Whether it implements the MCP connector contract
   - Whether it is resolved via registry
3. [ ] Create compliance matrix in `docs/architecture-audit.md` or `docs/mcp-compliance.md`:
   - Integration name | MCP contract | Registry | Route-layer branching
4. [ ] Identify non-compliant direct integrations and list refactoring steps

**Acceptance Criteria**:
- Compliance matrix exists for all active connections
- Non-compliant integrations clearly identified

**Files to Review**:
- `app/services/ai_provider_service.py`
- `app/ai_providers/provider_manager.py`
- `app/api/v1/ai_generation.py`
- `app/api/v1/ai_providers.py`

---

### 🔴 Task 1.0.4: Define Add/Remove Runbook for Connections
**Priority**: Critical  
**Estimated Time**: 1 hour  
**Assignee**: TBD  
**Depends on**: Task 1.0.1, Task 1.0.2

**Steps**:
1. [ ] Document **Adding a connection**:
   - Implement connector that satisfies MCP contract
   - Register connector in registry
   - Add/update configuration (e.g. DB or config store)
   - No route-layer or frontend code changes required for new provider
2. [ ] Document **Removing a connection**:
   - Unregister or disable connector in registry
   - Clean up connection configuration in storage
   - Keep API contracts stable for unaffected providers
3. [ ] Add runbook to `docs/` and link from architecture guidelines

**Acceptance Criteria**:
- Add/remove runbook is written and linked
- Runbook makes clear that route rewrites are not needed for add/remove

---

### 🔴 Task 1.1.1: Audit `app/api/v1/materials.py`
**Priority**: Critical  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] Open `app/api/v1/materials.py`
2. [ ] Review each route handler (`@router.get`, `@router.post`, `@router.put`, `@router.delete`)
3. [ ] For each handler, check:
   - Does it contain business logic? (if/else decisions, calculations, data transformations beyond mapping)
   - Does it directly query MongoDB? (should use service layer)
   - Is it > 50 lines? (excluding Pydantic models)
4. [ ] Document violations in `docs/architecture-audit.md`:
   - Route name
   - Line numbers
   - Type of violation (business logic, direct DB access, too long)
   - Suggested refactoring approach
5. [ ] Count total violations found

**Acceptance Criteria**:
- All route handlers documented
- Violations clearly identified with line numbers
- Refactoring suggestions provided

**Files to Create/Update**:
- `docs/architecture-audit.md` (create if doesn't exist)

---

### 🔴 Task 1.1.2: Audit `app/api/v1/ai_generation.py`
**Priority**: Critical  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] Open `app/api/v1/ai_generation.py`
2. [ ] Review route handlers (especially `/api/v1/ai/generate-image`)
3. [ ] Check for:
   - Business logic (provider selection, image processing, error handling logic)
   - Direct MongoDB queries
   - Direct AI provider API calls (should go through service layer and MCP connectors, not direct SDK)
4. [ ] Document violations in `docs/architecture-audit.md`
5. [ ] Verify error handling returns enriched `error_details` with correlation IDs
6. [ ] Note any provider-specific branching that should move to MCP registry resolution

**Acceptance Criteria**:
- All handlers audited
- Violations documented
- Error handling pattern verified

---

### 🔴 Task 1.1.3: Audit `app/api/v1/companies.py`
**Priority**: Critical  
**Estimated Time**: 45 minutes  
**Assignee**: TBD

**Steps**:
1. [ ] Open `app/api/v1/companies.py`
2. [ ] Review all route handlers
3. [ ] Check for business logic (company validation, user association logic)
4. [ ] Verify database access goes through service layer
5. [ ] Document violations

**Acceptance Criteria**:
- Audit complete
- Violations documented

---

### 🔴 Task 1.1.4: Audit `app/api/v1/users.py`
**Priority**: Critical  
**Estimated Time**: 45 minutes  
**Assignee**: TBD

**Steps**:
1. [ ] Open `app/api/v1/users.py`
2. [ ] Review route handlers (create, read, update, delete)
3. [ ] Check for business logic (password hashing, validation rules)
4. [ ] Verify uses `UserDB` or service layer (not direct MongoDB)
5. [ ] Document violations

**Acceptance Criteria**:
- Audit complete
- Violations documented

---

### 🔴 Task 1.1.5: Audit `app/api/v1/auth.py`
**Priority**: Critical  
**Estimated Time**: 45 minutes  
**Assignee**: TBD

**Steps**:
1. [ ] Open `app/api/v1/auth.py`
2. [ ] Review login/token endpoints
3. [ ] Check for business logic (authentication logic, token generation logic)
4. [ ] Verify uses auth service or `UserDB` (not direct DB access)
5. [ ] Document violations

**Acceptance Criteria**:
- Audit complete
- Violations documented

---

### 🔴 Task 1.1.6: Audit `app/api/v1/ai_providers.py`
**Priority**: Critical  
**Estimated Time**: 30 minutes  
**Assignee**: TBD

**Steps**:
1. [ ] Open `app/api/v1/ai_providers.py`
2. [ ] Verify uses `AIProviderService` (not direct DB access)
3. [ ] Check for business logic in routes
4. [ ] Document violations

**Acceptance Criteria**:
- Audit complete
- Uses service layer verified

---

### 🟡 Task 1.1.7: Create Architecture Audit Report
**Priority**: Moderate  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] Consolidate all audit findings from Tasks 1.1.1-1.1.6
2. [ ] Create `docs/architecture-audit.md` with:
   - Summary table of violations by file
   - Detailed findings per route handler
   - Priority ranking (Critical, High, Medium, Low)
   - Refactoring recommendations
3. [ ] Include metrics:
   - Total routes audited
   - Total violations found
   - Routes compliant vs non-compliant
4. [ ] Add visual diagram showing current vs target architecture

**Acceptance Criteria**:
- Comprehensive audit report created
- Violations prioritized
- Refactoring plan outlined

---

### 🔴 Task 1.1.8: Refactor `app/api/v1/materials.py` (if violations found)
**Priority**: Critical (if violations exist)  
**Estimated Time**: 2-4 hours  
**Assignee**: TBD  
**Depends on**: Task 1.1.1

**Steps**:
1. [ ] Review audit findings for `materials.py`
2. [ ] Create or update `app/services/material_service.py`:
   - Move business logic from routes to service methods
   - Ensure service methods are pure (no HTTP dependencies)
   - Add type hints and docstrings
3. [ ] Refactor route handlers:
   - Keep only validation and HTTP mapping
   - Call service methods
   - Map service results to HTTP responses
4. [ ] Update tests:
   - Add tests for service layer
   - Update route handler tests
5. [ ] Verify no regressions:
   - Run existing tests
   - Manual testing of material creation workflow

**Acceptance Criteria**:
- All business logic moved to service layer
- Route handlers are < 50 lines each
- Tests pass
- No functionality broken

---

### 🔴 Task 1.1.9: Refactor `app/api/v1/ai_generation.py` (if violations found)
**Priority**: Critical (if violations exist)  
**Estimated Time**: 3-5 hours  
**Assignee**: TBD  
**Depends on**: Task 1.1.2

**Steps**:
1. [ ] Review audit findings for `ai_generation.py`
2. [ ] Create or update `app/services/ai_generation_service.py`:
   - Move provider selection logic
   - Move image generation orchestration
   - Move error handling logic (keep HTTP mapping in routes)
3. [ ] Refactor route handlers to be thin
4. [ ] Ensure error handling returns enriched `error_details`
5. [ ] Update tests
6. [ ] Verify AI image generation still works

**Acceptance Criteria**:
- Business logic in service layer
- Routes are thin controllers
- Error handling with correlation IDs works
- Tests pass

---

### 🟡 Task 1.1.10: Refactor Other Routes (if violations found)
**Priority**: Moderate (if violations exist)  
**Estimated Time**: 2-3 hours per file  
**Assignee**: TBD  
**Depends on**: Tasks 1.1.3, 1.1.4, 1.1.5, 1.1.6

**Steps**:
1. [ ] For each file with violations (`companies.py`, `users.py`, `auth.py`, `ai_providers.py`):
   - Create/update corresponding service
   - Move business logic to service
   - Refactor routes to be thin
   - Update tests
2. [ ] Verify no regressions

**Acceptance Criteria**:
- All routes refactored
- Services created/updated
- Tests pass

---

### 🟡 Task 1.2.1: Verify Service Layer Coverage
**Priority**: Moderate  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] List all services in `app/services/`:
   - `ai_provider_service.py`
   - `material_service.py` (if exists)
   - `ai_generation_service.py` (if exists)
   - Others?
2. [ ] For each API route file, verify:
   - Does a corresponding service exist?
   - Are services imported and used?
3. [ ] Document missing services
4. [ ] Check for duplicate business logic across routes

**Acceptance Criteria**:
- Service coverage documented
- Missing services identified
- Duplicate logic identified

---

### 🟡 Task 1.2.2: Create Missing Services
**Priority**: Moderate  
**Estimated Time**: 2-4 hours per service  
**Assignee**: TBD  
**Depends on**: Task 1.2.1

**Steps**:
1. [ ] For each missing service identified:
   - Create service file in `app/services/`
   - Extract business logic from routes
   - Add type hints and docstrings
   - Add unit tests
2. [ ] Update routes to use new services
3. [ ] Run tests

**Acceptance Criteria**:
- All services created
- Routes updated
- Tests pass

---

### 🟡 Task 1.2.3: Verify Service Testability
**Priority**: Moderate  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] For each service in `app/services/`:
   - Check for HTTP dependencies (Request, Response objects)
   - Check for FastAPI dependencies
   - Verify services can be tested without HTTP context
2. [ ] Document services with HTTP dependencies
3. [ ] Refactor if needed to remove HTTP dependencies

**Acceptance Criteria**:
- All services are testable without HTTP context
- No HTTP dependencies in service layer

---

## Phase 2: Frontend Architecture Alignment (Week 2)

### 🟡 Task 2.1.1: Search for Direct `fetch()` Calls
**Priority**: Moderate  
**Estimated Time**: 30 minutes  
**Assignee**: TBD

**Steps**:
1. [ ] Run search: `grep -r "fetch(" frontend/src/ --include="*.tsx" --include="*.ts"`
2. [ ] List all files containing `fetch()` calls
3. [ ] Document in `docs/frontend-api-audit.md`:
   - File path
   - Line number
   - Context (component/page)
   - Suggested refactoring (use service layer)

**Acceptance Criteria**:
- All `fetch()` calls identified
- Documented with locations

---

### 🟡 Task 2.1.2: Search for Direct `axios` Imports
**Priority**: Moderate  
**Estimated Time**: 30 minutes  
**Assignee**: TBD

**Steps**:
1. [ ] Run search: `grep -r "import.*axios" frontend/src/ --include="*.tsx" --include="*.ts"`
2. [ ] List all files importing `axios` directly
3. [ ] Verify if they use `apiRequest()` wrapper or direct `axios`
4. [ ] Document violations

**Acceptance Criteria**:
- All direct `axios` usage identified
- Documented

---

### 🟡 Task 2.1.3: Audit Material Pages API Calls
**Priority**: Moderate  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] Review `frontend/src/app/[locale]/materials/**/*.tsx`
2. [ ] For each file:
   - Check API calls (should use `frontend/src/services/` modules)
   - Verify error handling uses `AIErrorDisplay`
   - Check for correlation IDs
3. [ ] Document violations

**Acceptance Criteria**:
- All material pages audited
- Violations documented

---

### 🟡 Task 2.1.4: Audit Settings Pages API Calls
**Priority**: Moderate  
**Estimated Time**: 45 minutes  
**Assignee**: TBD

**Steps**:
1. [ ] Review `frontend/src/app/[locale]/settings/**/*.tsx`
2. [ ] Check API calls use service layer
3. [ ] Verify error handling
4. [ ] Document violations

**Acceptance Criteria**:
- Settings pages audited
- Violations documented

---

### 🟡 Task 2.1.5: Audit Components API Calls
**Priority**: Moderate  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] Review `frontend/src/components/**/*.tsx`
2. [ ] Check for API calls in components (should be minimal)
3. [ ] Verify components receive data via props (not direct API calls)
4. [ ] Document violations

**Acceptance Criteria**:
- Components audited
- Violations documented

---

### 🟡 Task 2.1.6: Create Frontend API Audit Report
**Priority**: Moderate  
**Estimated Time**: 1 hour  
**Assignee**: TBD  
**Depends on**: Tasks 2.1.1-2.1.5

**Steps**:
1. [ ] Consolidate findings from Tasks 2.1.1-2.1.5
2. [ ] Create `docs/frontend-api-audit.md`:
   - Summary of violations
   - Files needing refactoring
   - Priority ranking
3. [ ] Add metrics:
   - Total API calls found
   - Calls using service layer vs direct
   - Error handling compliance

**Acceptance Criteria**:
- Comprehensive audit report
- Violations prioritized

---

### 🟡 Task 2.1.7: Refactor Direct `fetch()` Calls
**Priority**: Moderate  
**Estimated Time**: 1-2 hours per file  
**Assignee**: TBD  
**Depends on**: Task 2.1.1

**Steps**:
1. [ ] For each file with direct `fetch()`:
   - Create/update service function in `frontend/src/services/`
   - Replace `fetch()` with service call
   - Update error handling to use `AIErrorDisplay`
   - Add correlation ID support
2. [ ] Test each refactored file
3. [ ] Verify no regressions

**Acceptance Criteria**:
- All `fetch()` calls replaced
- Service layer used
- Tests pass

---

### 🟡 Task 2.1.8: Refactor Direct `axios` Usage
**Priority**: Moderate  
**Estimated Time**: 30 minutes per file  
**Assignee**: TBD  
**Depends on**: Task 2.1.2

**Steps**:
1. [ ] For each file with direct `axios`:
   - Replace with `apiRequest()` from `frontend/src/services/api.ts`
   - Remove `axios` import
2. [ ] Test each file
3. [ ] Verify no regressions

**Acceptance Criteria**:
- All direct `axios` replaced with `apiRequest()`
- Tests pass

---

### 🟡 Task 2.2.1: Verify `apiRequest()` Usage Consistency
**Priority**: Moderate  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] Review `frontend/src/services/api.ts`:
   - Verify `apiRequest()` function exists
   - Check correlation ID attachment
   - Verify error enrichment
2. [ ] Search for all `apiRequest()` usages
3. [ ] Verify consistent usage pattern
4. [ ] Document inconsistencies

**Acceptance Criteria**:
- `apiRequest()` usage verified
- Inconsistencies documented

---

### 🟡 Task 2.2.2: Verify Correlation IDs on All Requests
**Priority**: Moderate  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] Review `frontend/src/services/api.ts`:
   - Check if correlation IDs are automatically added
   - Verify `X-Correlation-ID` header is set
2. [ ] Test a few API calls:
   - Check network tab for correlation ID header
   - Verify backend receives correlation ID
3. [ ] Document any missing correlation IDs

**Acceptance Criteria**:
- Correlation IDs verified on all requests
- Missing IDs documented

---

### 🟡 Task 2.2.3: Verify Timeout Configuration
**Priority**: Moderate  
**Estimated Time**: 30 minutes  
**Assignee**: TBD

**Steps**:
1. [ ] Review `frontend/src/services/api.ts`:
   - Check timeout configuration
   - Verify 60s timeout for AI generation endpoints
   - Verify shorter timeout for other endpoints
2. [ ] Test timeout behavior:
   - Simulate slow API response
   - Verify timeout error handling
3. [ ] Document timeout configuration

**Acceptance Criteria**:
- Timeout configuration verified
- 60s for AI generation confirmed

---

### 🟡 Task 2.2.4: Verify Error Enrichment
**Priority**: Moderate  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] Review `frontend/src/services/api.ts`:
   - Check axios interceptor for error enrichment
   - Verify timeout detection (`ECONNABORTED`)
   - Verify error_details extraction
2. [ ] Test error scenarios:
   - Timeout error
   - Network error
   - API error with `error_details`
3. [ ] Verify `AIErrorDisplay` receives enriched errors

**Acceptance Criteria**:
- Error enrichment verified
- All error types handled

---

### 🟡 Task 2.3.1: Verify Frontend Does Not Couple to Provider-Specific Behavior
**Priority**: Moderate  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] Review material/settings pages and components that use AI providers
2. [ ] Check for provider-specific UI branches (e.g. different forms per provider) that could be driven by metadata/capabilities instead
3. [ ] Ensure frontend only uses provider metadata and capabilities returned by API (e.g. from MCP-backed endpoints)
4. [ ] Document any coupling that would require frontend changes when adding/removing a connector

**Acceptance Criteria**:
- Frontend does not hardcode provider-specific behavior beyond metadata/capabilities
- Adding/removing a connector does not require frontend code changes for standard flows

---

### 🟡 Task 2.3.2: Ensure Backend Endpoints Are Provider-Agnostic (MCP-Oriented)
**Priority**: Moderate  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] Review `/api/v1/ai-providers` and `/api/v1/ai/generate-image` (and related) contracts
2. [ ] Ensure request/response shapes are integration-agnostic where possible (e.g. provider_id + params, not provider-specific fields)
3. [ ] Verify resolution of provider/integration is by ID via registry, not hardcoded branching in routes
4. [ ] Document any endpoint that still exposes provider-hardcoded contracts for refactor

**Acceptance Criteria**:
- Backend endpoint contracts are MCP-oriented (provider-agnostic where possible)
- No provider-hardcoded request/response structures in public API

---

### 🟡 Task 2.3.3: Confirm Enable/Disable Connector Requires No Frontend Code Changes
**Priority**: Moderate  
**Estimated Time**: 30 minutes  
**Assignee**: TBD  
**Depends on**: Task 2.3.1, Task 2.3.2

**Steps**:
1. [ ] Verify that enabling a new connector (register + config) makes it appear in provider list without frontend deploy
2. [ ] Verify that disabling/removing a connector removes it from provider list without frontend deploy
3. [ ] Document any edge cases (e.g. feature flags) and ensure they are config-driven

**Acceptance Criteria**:
- Enabling/disabling a connector does not require frontend code changes
- Behavior is stable when connectors are added/removed via config

---

## Phase 3: Database & Infrastructure (Week 3)

### 🟡 Task 3.1.1: Review MongoDB Index Definitions
**Priority**: Moderate  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] Open `app/db/mongodb.py`
2. [ ] Find `create_indexes()` method (or similar)
3. [ ] Review existing indexes:
   - `materials` collection indexes
   - `ai_providers` collection indexes
   - `companies` collection indexes
   - `users` collection indexes
4. [ ] Document current indexes

**Acceptance Criteria**:
- All indexes documented
- Index creation method identified

---

### 🟡 Task 3.1.2: Verify Index Coverage
**Priority**: Moderate  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] Review query patterns in codebase:
   - Search for MongoDB queries (`find`, `find_one`)
   - Identify frequently queried fields
2. [ ] Compare with existing indexes:
   - `materials`: `user_id`, `company_id`, `stage`, `status`
   - `ai_providers`: `user_id`, `id`
   - `companies`: `user_id`
   - `users`: `email` (unique)
3. [ ] Identify missing indexes
4. [ ] Document missing indexes

**Acceptance Criteria**:
- Query patterns analyzed
- Missing indexes identified

---

### 🟡 Task 3.1.3: Add Missing Indexes
**Priority**: Moderate  
**Estimated Time**: 1 hour  
**Assignee**: TBD  
**Depends on**: Task 3.1.2

**Steps**:
1. [ ] Update `app/db/mongodb.py`:
   - Add missing index definitions
   - Ensure indexes are created on startup
2. [ ] Test index creation:
   - Restart application
   - Verify indexes created in MongoDB
3. [ ] Document new indexes

**Acceptance Criteria**:
- Missing indexes added
- Indexes created on startup
- Documented

---

### 🟡 Task 3.1.4: Document Index Strategy
**Priority**: Low  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] Update `docs/MONGODB_ARCHITECTURE.md`:
   - Add "Index Strategy" section
   - Document all indexes per collection
   - Explain why each index exists (query pattern)
   - Document index creation process
2. [ ] Add index maintenance guidelines

**Acceptance Criteria**:
- Index strategy documented
- Maintenance guidelines added

---

### 🟡 Task 3.2.1: Verify AI Provider Database Integration
**Priority**: Moderate  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] Review `app/services/ai_provider_service.py`:
   - Verify all provider loading goes through `mongodb.ai_providers`
   - Check for any hardcoded provider lists
2. [ ] Review `app/api/v1/ai_providers.py`:
   - Verify uses service layer
   - No hardcoded providers
3. [ ] Review frontend:
   - Verify `getUserAIProviders()` fetches from API
   - Check for localStorage fallbacks (should fail gracefully)
4. [ ] Verify all provider execution paths use MCP connectors (no direct SDK calls from route layer); document any direct SDK usage
5. [ ] Document findings

**Acceptance Criteria**:
- Database integration verified
- Hardcoded providers identified (if any)
- Provider execution paths are MCP-mediated (or violations documented)

---

### 🟡 Task 3.2.2: Remove Hardcoded Provider Lists
**Priority**: Moderate (if found)  
**Estimated Time**: 1-2 hours  
**Assignee**: TBD  
**Depends on**: Task 3.2.1

**Steps**:
1. [ ] For each hardcoded provider list found:
   - Remove hardcoded array
   - Replace with database fetch
   - Update tests
2. [ ] Verify no regressions
3. [ ] Test provider loading

**Acceptance Criteria**:
- All hardcoded providers removed
- Database-driven verified
- Tests pass

---

### 🟡 Task 3.2.3: Verify Frontend Fallback Behavior
**Priority**: Moderate  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] Review `frontend/src/services/ai-providers.ts`:
   - Check `getUserAIProviders()` function
   - Verify fallback behavior (should fail gracefully, not use localStorage)
2. [ ] Test fallback:
   - Simulate API failure
   - Verify error handling
   - Verify no localStorage fallback
3. [ ] Update if needed to fail gracefully

**Acceptance Criteria**:
- Fallback behavior verified
- Graceful failure confirmed

---

### 🟡 Task 3.2.4: Verify All Provider Execution Paths Use MCP Connectors
**Priority**: Moderate  
**Estimated Time**: 1.5 hours  
**Assignee**: TBD  
**Depends on**: Task 1.0.3, Task 3.2.1

**Steps**:
1. [ ] Using MCP compliance matrix from Task 1.0.3, list all execution paths (e.g. image generation, validation)
2. [ ] For each path, trace from route → service → connector:
   - Confirm no direct provider SDK calls in route or service (only via MCP connector interface)
   - Confirm connector is resolved via registry by provider/integration ID
3. [ ] Document any path that still uses direct SDK; create follow-up refactor task
4. [ ] Update compliance matrix with “execution path MCP-mediated” status

**Acceptance Criteria**:
- All provider execution paths verified
- Provider execution is fully MCP-mediated, or refactor tasks created for exceptions

---

## Phase 4: Documentation & Validation (Week 4)

### 🟢 Task 4.1.1: Update MongoDB Architecture Docs
**Priority**: Low  
**Estimated Time**: 2 hours  
**Assignee**: TBD

**Steps**:
1. [ ] Review `docs/MONGODB_ARCHITECTURE.md`
2. [ ] Update with current architecture:
   - Connection patterns
   - Collection schemas
   - Index strategy (from Task 3.1.4)
   - Query patterns
3. [ ] Add architecture diagram (text or image)
4. [ ] Document AI provider integration flow

**Acceptance Criteria**:
- Docs updated
- Architecture diagram added
- Integration flow documented

---

### 🟢 Task 4.1.2: Create Architecture Diagram
**Priority**: Low  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] Create diagram showing:
   - Frontend layer (`frontend/src/app/[locale]/`)
   - API layer (`app/api/v1/endpoints/`)
   - Service layer (`app/services/`)
   - Data access layer (`app/db/`)
   - Database (MongoDB)
2. [ ] Add to `docs/MONGODB_ARCHITECTURE.md` or create `docs/ARCHITECTURE.md`
3. [ ] Include data flow arrows

**Acceptance Criteria**:
- Diagram created
- Added to documentation

---

### 🟢 Task 4.1.3: Document AI Provider Integration Flow
**Priority**: Low  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] Create flow diagram:
   - Frontend requests providers
   - API calls service
   - Service queries MongoDB
   - Response flows back
2. [ ] Document in `docs/MONGODB_ARCHITECTURE.md`
3. [ ] Include error handling flow

**Acceptance Criteria**:
- Integration flow documented
- Error handling included

---

### 🟢 Task 4.2.1: Create Architecture Validation Test - Route Handlers
**Priority**: Low  
**Estimated Time**: 2 hours  
**Assignee**: TBD

**Steps**:
1. [ ] Create `tests/unit/test_architecture_routes.py`:
   - Test that route handlers don't contain business logic
   - Test that routes delegate to services
   - Test route handler length (< 50 lines)
2. [ ] Add test fixtures
3. [ ] Run tests
4. [ ] Document test results

**Acceptance Criteria**:
- Tests created
- Tests pass for compliant routes
- Tests fail for non-compliant routes

---

### 🟢 Task 4.2.2: Create Architecture Validation Test - Services
**Priority**: Low  
**Estimated Time**: 2 hours  
**Assignee**: TBD

**Steps**:
1. [ ] Create `tests/unit/test_architecture_services.py`:
   - Test that services don't have HTTP dependencies
   - Test that services are testable without HTTP context
   - Test service layer isolation
2. [ ] Run tests
3. [ ] Document results

**Acceptance Criteria**:
- Tests created
- Services validated

---

### 🟢 Task 4.2.3: Create Architecture Validation Test - Database-Driven Providers
**Priority**: Low  
**Estimated Time**: 1 hour  
**Assignee**: TBD

**Steps**:
1. [ ] Create `tests/unit/test_architecture_providers.py`:
   - Test that no hardcoded provider lists exist
   - Test that providers are loaded from database
   - Test frontend doesn't use localStorage fallback
2. [ ] Run tests
3. [ ] Document results

**Acceptance Criteria**:
- Tests created
- Database-driven providers validated

---

### 🟢 Task 4.2.5: Create Architecture Validation Test - MCP-Mediated Execution
**Priority**: Low  
**Estimated Time**: 1.5 hours  
**Assignee**: TBD  
**Depends on**: Task 1.0.1, Task 3.2.4

**Steps**:
1. [ ] Create `tests/unit/test_architecture_mcp.py` (or add to existing architecture tests):
   - Test that no route or service calls provider SDKs directly (only via connector interface)
   - Test that connector resolution is via registry by ID
   - Test that adding/removing a connector (mock) does not require route changes
2. [ ] Run tests
3. [ ] Document results

**Acceptance Criteria**:
- Tests created for MCP-mediated execution
- Violations fail tests

---

### 🟢 Task 4.2.4: Add Architecture Tests to CI/CD
**Priority**: Low  
**Estimated Time**: 30 minutes  
**Assignee**: TBD  
**Depends on**: Tasks 4.2.1, 4.2.2, 4.2.3, 4.2.5

**Steps**:
1. [ ] Review CI/CD configuration (`.github/workflows/` or similar)
2. [ ] Add architecture validation tests to test suite
3. [ ] Ensure tests run on every PR
4. [ ] Verify tests fail on architecture violations

**Acceptance Criteria**:
- Tests in CI/CD
- Violations caught automatically

---

## Summary Checklist

### Phase 1: Compliance Verification
- [ ] Task 1.0.1: Create MCP connector contract
- [ ] Task 1.0.2: Document MCP registry responsibilities
- [ ] Task 1.0.3: Map integrations to MCP / compliance matrix
- [ ] Task 1.0.4: Define add/remove runbook for connections
- [ ] Task 1.1.1: Audit materials.py
- [ ] Task 1.1.2: Audit ai_generation.py
- [ ] Task 1.1.3: Audit companies.py
- [ ] Task 1.1.4: Audit users.py
- [ ] Task 1.1.5: Audit auth.py
- [ ] Task 1.1.6: Audit ai_providers.py
- [ ] Task 1.1.7: Create audit report
- [ ] Task 1.1.8: Refactor materials.py (if needed)
- [ ] Task 1.1.9: Refactor ai_generation.py (if needed)
- [ ] Task 1.1.10: Refactor other routes (if needed)
- [ ] Task 1.2.1: Verify service coverage
- [ ] Task 1.2.2: Create missing services
- [ ] Task 1.2.3: Verify service testability

### Phase 2: Frontend Alignment
- [ ] Task 2.1.1: Search fetch() calls
- [ ] Task 2.1.2: Search axios imports
- [ ] Task 2.1.3: Audit material pages
- [ ] Task 2.1.4: Audit settings pages
- [ ] Task 2.1.5: Audit components
- [ ] Task 2.1.6: Create frontend audit report
- [ ] Task 2.1.7: Refactor fetch() calls
- [ ] Task 2.1.8: Refactor axios usage
- [ ] Task 2.2.1: Verify apiRequest() usage
- [ ] Task 2.2.2: Verify correlation IDs
- [ ] Task 2.2.3: Verify timeout config
- [ ] Task 2.2.4: Verify error enrichment
- [ ] Task 2.3.1: Verify frontend not coupled to provider-specific behavior
- [ ] Task 2.3.2: Ensure backend endpoints MCP-oriented
- [ ] Task 2.3.3: Confirm enable/disable connector needs no frontend changes

### Phase 3: Database & Infrastructure
- [ ] Task 3.1.1: Review index definitions
- [ ] Task 3.1.2: Verify index coverage
- [ ] Task 3.1.3: Add missing indexes
- [ ] Task 3.1.4: Document index strategy
- [ ] Task 3.2.1: Verify provider DB integration
- [ ] Task 3.2.2: Remove hardcoded providers
- [ ] Task 3.2.3: Verify frontend fallback
- [ ] Task 3.2.4: Verify all provider execution paths use MCP connectors

### Phase 4: Documentation & Validation
- [ ] Task 4.1.1: Update MongoDB docs
- [ ] Task 4.1.2: Create architecture diagram
- [ ] Task 4.1.3: Document provider integration flow
- [ ] Task 4.2.1: Create route validation tests
- [ ] Task 4.2.2: Create service validation tests
- [ ] Task 4.2.3: Create provider validation tests
- [ ] Task 4.2.5: Create MCP-mediated execution validation tests
- [ ] Task 4.2.4: Add tests to CI/CD

---

## Next Steps

1. **Start with Phase 1, Task 1.0.1**: Define MCP connector contract and registry baseline (per `spec/process/architecture-guidelines-implementation-plan.md`)
2. **Then**: Task 1.0.2–1.0.4, then Task 1.1.1 (audit API routes)
3. **Track progress**: Check off tasks as completed
4. **Update audit reports**: Document findings (including MCP compliance matrix)
5. **Refactor incrementally**: One file at a time to minimize risk

---

**Total Estimated Time**: ~80-120 hours (depending on violations found)  
**Recommended Timeline**: 4 weeks (1 phase per week)
