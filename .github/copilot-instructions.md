# AI Marketing Agent - Copilot Instructions

> **⚠️ IMPORTANT:** Before making any changes, always read the relevant instruction files from `.github/instructions/` based on your task:
> - **All tasks:** Read `.github/instructions/ai-marketing-agent.architecture-and-development-guidelines.instructions.md`
> - **All tasks:** Read `.github/instructions/ai-marketing-agent.development-best-practices.instructions.md`
> - **Bug fixes:** Read `.github/instructions/ai-marketing-agent-fix-bug.instructions.md`
> - **UI/UX changes:** Read `.github/instructions/ai-marketing-agent-ux-guidelines.instructions.md`

---

## Architecture Overview

**Full Stack Marketing Content Generation Platform**
- **Frontend:** Next.js 14 (React + TypeScript) on port **3001**
- **Backend:** FastAPI (Python) on port **8088** - Critical: always use 8088, not 8089
- **Database:** MongoDB (Docker) on port 27017 - migrated from mock DB in Jan 2025
- **AI Integration:** Multi-provider system (OpenAI DALL-E, HuggingFace, Replicate, Stability)

### Key Principle: Database-Driven AI Providers
AI providers are **never hardcoded**. All provider configurations (name, API keys, models, capabilities) are stored in MongoDB's `ai_providers` collection and dynamically loaded. The frontend reads these via `/api/v1/ai-providers` endpoints.

---

## Critical Workflows

### Starting Development Environment
Use VS Code tasks (defined in `.vscode/tasks.json`):
1. **🚀 Start Full Development Environment** - Starts MongoDB → Backend → Frontend sequentially
2. **📊 Check Services Status** - Verify all three services are running
3. **🛑 Stop All Services** - Clean shutdown of all services

Or manually:
```bash
# Start MongoDB container
docker start ai-marketing-agent-mongo-1

# Start backend (from project root)
uvicorn app.main:api_app --host 127.0.0.1 --port 8088 --reload

# Start frontend (from frontend/)
npm run dev
```

**Access points:**
- Frontend: `http://localhost:3001`
- Backend API docs: `http://127.0.0.1:8088/docs`
- MongoDB: `mongodb://localhost:27017/ai_marketing_agent`

### Material Creation Workflow (3 Stages)
The app follows a strict 3-stage material creation pipeline:

1. **Idea Stage** (`/materials/create`)
   - User defines title, description, target audience, campaign objective, keywords
   - Creates material record with stage=`idea`, status=`draft`

2. **Refinement Stage** (`/materials/[id]/edit`)
   - User generates AI images using configured providers
   - Uses `enhanced-refinement-form.tsx` component
   - Backend calls `/api/v1/ai/generate-image` (coordinates with AI providers)
   - Images stored in `material.generated_images[]` with metadata

3. **Finalization Stage**
   - User selects final image
   - Material moves to stage=`finalization`, status=`completed`

---

## Error Handling Pattern: Correlation IDs + Enriched Errors

### Backend Error Structure
All backend errors return enriched `error_details`:
```python
{
    "success": False,
    "error": "Brief error message",
    "error_details": {
        "error_type": "timeout|rate_limit|billing|invalid_key|content_policy|...",
        "message": "Technical details",
        "user_message": "errors.ai.timeout",  # i18n key
        "provider": "openai",
        "correlation_id": "req_abc123_xyz",  # For debugging
        "timestamp": "2025-01-28T10:27:46Z",
        "http_status": 408,
        "suggested_actions": ["actions.try_again", "actions.switch_provider"],
        "details": { "timeout_seconds": 60, "url": "/api/v1/ai/generate-image" }
    }
}
```

### Frontend Error Handling
- **Never use `alert()`** - Use `AIErrorDisplay` component instead
- Axios interceptor (`frontend/src/services/api.ts`) enriches errors:
  - Timeout detection: `error.code === 'ECONNABORTED'` → adds `error.isTimeout = true`
  - Correlation IDs: auto-generated per request via `X-Correlation-ID` header
- Pages set `setAiError(error_details)` to display rich error UI
- Component: `frontend/src/components/ui/ai-error-display.tsx`

**Example (materials/create/page.tsx):**
```typescript
catch (error: any) {
  if (error.error_details) {
    setAiError(error.error_details);  // Rich error display
  } else if (error.isTimeout) {
    setAiError({
      error_type: 'timeout',
      message: error.userMessage,
      correlation_id: error.config?.headers?.['X-Correlation-ID'],
      // ...
    });
  }
}
```

---

## File Organization Rules

**Backend (Python):**
- `app/api/v1/endpoints/` - API route handlers
- `app/services/` - Business logic (never in routes)
- `app/models/` - Pydantic schemas
- `app/db/` - Database operations (MongoDB queries)
- `app/ai_providers/` - AI provider integrations

**Frontend (TypeScript):**
- `frontend/src/app/[locale]/` - Next.js App Router pages (i18n-enabled)
- `frontend/src/components/` - Reusable React components
- `frontend/src/services/` - API client logic (axios wrappers)
- `frontend/src/i18n/locales/` - Translation files (en.json, pt.json)

**Testing & Docs:**
- `tests/unit/` - Backend unit tests (pytest)
- `tests/frontend/` - Frontend debugging HTML tools
- `docs/` - Architecture docs, troubleshooting guides
- `debug/` - One-off debug scripts

**Never create files at project root** - Always place in appropriate subdirectory.

---

## Project-Specific Conventions

### 1. Internationalization (i18n)
All user-facing text uses i18n keys:
```typescript
// Frontend
const { t } = useTranslations();
<p>{t('errors.ai.timeout')}</p>

// Backend returns i18n keys
"user_message": "errors.ai.rate_limit_exceeded"
```
Translations: `frontend/src/i18n/locales/{en,pt}.json`

### 2. AI Image Generation Timeouts
- **Axios timeout: 60 seconds** (DALL-E takes 15-30s per image)
- Default image count: **3 images** (reduced from 5 for performance)
- Progress indicator: Show animated "Generating 3 AI images... 20-30 seconds" while `isGenerating=true`

### 3. MongoDB Patterns
- Use Motor (async MongoDB driver)
- Global instance: `from app.db.mongodb import mongodb`
- Collections: `mongodb.users`, `mongodb.companies`, `mongodb.materials`, `mongodb.ai_providers`
- Always use indexes: Created via `mongodb.create_indexes()` on startup

### 4. Port Configuration (CRITICAL)
- **Frontend must proxy to port 8088** (defined in `next.config.js`)
- Backend API name: `api_app` (not `app`) - see `app/main.py:19`
- CORS: Explicitly allows `localhost:3000`, `localhost:3001`, `127.0.0.1:3000`, `127.0.0.1:3001`

---

## Debugging Tools

### Frontend HTML Test Suites
Located in `tests/frontend/`:
- `complete_provider_test.html` - Test AI provider detection logic
- `auth-debug-suite.html` - Test authentication flow
- `settings-debug.html` - Debug UI components

### Backend Diagnostic Scripts
Located in `debug/`:
- `debug_api.py` - Test API endpoints directly
- `debug_company_db.py` - Verify MongoDB connections
- Use VS Code debugger config (`.vscode/launch.json`)

### VS Code Tasks Quick Reference
- `📊 Check Services Status` - See what's running
- `🔍 View Backend Logs` - Tail `api_server.log`
- `🧹 Clean Logs` - Remove old log files
- `🔄 Restart All Services` - Full restart

---

## Common Pitfalls

1. **Don't hardcode AI providers** - They're database-driven, never in code
2. **Don't use `alert()`** - Use `AIErrorDisplay` component
3. **Don't forget correlation IDs** - Needed for debugging production issues
4. **Don't ignore timeout errors** - DALL-E needs 60s, handle gracefully
5. **Don't create masked API keys** - Check `isMaskedApiKey()` before storing (`sk-****` is masked)
6. **Port 8088 is non-negotiable** - Frontend proxy expects this exact port

---

## Testing Credentials
- Email: `test@example.com`
- Password: `password`
- Test company ID: `test_company`

---

## Instruction Files Reference

This project uses specialized instruction files for different development scenarios. **Always consult the appropriate instruction file before making changes:**

### Core Architecture & Guidelines
- **📋 `.github/instructions/ai-marketing-agent.architecture-and-development-guidelines.instructions.md`**
  - Stack overview and environment rules
  - Directory structure and code organization
  - AI provider integration patterns
  - Database-driven configuration principles
  - Clean architecture guidelines
  - **Read this for:** Any structural changes, new features, or architectural decisions

### Development Best Practices
- **✨ `.github/instructions/ai-marketing-agent.development-best-practices.instructions.md`**
  - Backend coding standards (PEP 8, type hints, docstrings)
  - Frontend patterns (TypeScript, component organization, TailwindCSS)
  - File creation policies and directory placement rules
  - Version control and collaboration guidelines
  - Testing requirements and quality assurance
  - **Read this for:** Code quality, conventions, file placement decisions

### Bug Fixing Workflow
- **🐛 `.github/instructions/ai-marketing-agent-fix-bug.instructions.md`**
  - Bug diagnosis and debugging procedures
  - Root cause analysis approach
  - Testing and validation requirements
  - Documentation update requirements
  - Commit message standards for fixes
  - **Read this for:** Any bug fix, error resolution, or debugging task

### UI/UX Guidelines
- **🎨 `.github/instructions/ai-marketing-agent-ux-guidelines.instructions.md`**
  - Design system and visual consistency
  - Component usage patterns
  - Accessibility requirements
  - User feedback and error handling
  - Animation and interaction guidelines
  - **Read this for:** Frontend components, UI changes, user experience improvements

---

## Reference Documents
- `.github/instructions/ai-marketing-agent.architecture-and-development-guidelines.instruction.md` - Full architecture
- `.github/instructions/ai-marketing-agent-fix-bug.instructions.md` - Bug fixing workflow
- `docs/MONGODB_ARCHITECTURE.md` - Database schema details
- `docs/authentication-guide.md` - Auth system documentation
- `CONTRIBUTING.md` - Development workflow and standards
