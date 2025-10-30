# AI Marketing Agent - Copilot Instructions

**Version**: 1.1.0  
**Last Updated**: January 29, 2025  
**Maintainer**: Rafael Amorim

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

## 📋 Instruction File Hierarchy

When conflicts arise between instruction files, follow this precedence order:

1. **Copilot Instructions** (`.github/copilot-instructions.md`) - Quick reference and critical overrides
2. **Specialized Instructions** (`.github/instructions/*.instructions.md`) - Context-specific rules:
   - `architecture-and-development-guidelines.instructions.md` - System design decisions
   - `development-best-practices.instructions.md` - Code quality standards  
   - `fix-bug.instructions.md` - Debugging workflow
   - `ux-guidelines.instructions.md` - Frontend design rules
3. **Main Prompt** (`.github/prompts/ai-marketing-agent.prompt.md`) - Original project vision and general guidelines

**Golden Rule**: More specific instructions override general ones. When in doubt, consult this file first.

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

## Common Pitfalls

1. **Don't hardcode AI providers** - They're database-driven, never in code
2. **Don't use `alert()`** - Use `AIErrorDisplay` component
3. **Don't forget correlation IDs** - Needed for debugging production issues
4. **Don't ignore timeout errors** - DALL-E needs 60s, handle gracefully
5. **Don't create masked API keys** - Check `isMaskedApiKey()` before storing (`sk-****` is masked)
6. **Port 8088 is non-negotiable** - Frontend proxy expects this exact port

---

## 🌳 Quick Decision Tree

### Creating a New File?
```
→ Test file? → `/tests/`
→ Documentation? → `/docs/`
→ Backend code? → `/app/`
→ Frontend component? → `/frontend/src/components/`
→ Frontend page? → `/frontend/src/app/[locale]/`
→ Debug script? → `/debug/`
→ System prompt? → `.github/prompts/`
→ Not sure? → **ASK FIRST** (never create at project root)
```

### Fixing a Bug?
```
1. Read `.github/instructions/ai-marketing-agent-fix-bug.instructions.md`
2. Investigate → Identify root cause
3. Check Pre-Fix Checklist
4. Apply fix in correct file
5. Add/update tests in `/tests/`
6. Update docs if behavior changed
7. Commit with `fix:` prefix
```

### Adding UI Feature?
```
1. Read `.github/instructions/ai-marketing-agent-ux-guidelines.instructions.md`
2. Use shadcn/ui components
3. Follow Apple-inspired design principles
4. Add i18n support (English + Portuguese)
5. Use `AIErrorDisplay` for errors (never `alert()`)
6. Test on mobile viewports
7. Ensure accessibility (WCAG AA)
```

### Encountering an Error?
```
→ Backend error? → Check correlation ID in logs
→ Frontend error? → Check browser console
→ AI generation error? → Display via `AIErrorDisplay` component
→ Database error? → Check MongoDB connection
→ Port conflict? → Don't change ports - debug the conflict
```

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
  - **React Hooks best practices and violations** ⚠️
  - **Translation pattern (custom i18n, not next-intl)** ⚠️
  - Accessibility requirements
  - User feedback and error handling
  - Animation and interaction guidelines
  - **Read this for:** Frontend components, UI changes, user experience improvements

---

## ⚠️ Common Mistakes Appendix

This section catalogs the most frequent errors made during development. **Always consult this before making changes.**

### 🔴 Critical: React Hooks Violations

**Symptom**: Runtime error "Rendered more hooks than during the previous render" or "Invalid hook call"

**Root Cause**: Hooks called conditionally, in loops, or in non-component functions

**Fix Pattern**:
```tsx
// ❌ WRONG - Hook inside conditional
function Component() {
  if (error) return <Error />;
  const [state, setState] = useState(false); // ERROR: Hook after early return
}

// ✅ CORRECT - All hooks at top level
function Component() {
  const [state, setState] = useState(false); // Hook FIRST
  if (error) return <Error />;
}
```

**Prevention**:
- [ ] Move ALL hooks to the very top of the component
- [ ] Never put hooks inside `if`, `for`, `while`, `switch`, `map`
- [ ] Extract logic without hooks to helper functions
- [ ] Read: `.github/instructions/ai-marketing-agent-ux-guidelines.instructions.md` → "React Hooks Best Practices"

---

### 🔴 Critical: Wrong i18n Pattern

**Symptom**: Error "Failed to call `useTranslations` because the context from `NextIntlClientProvider` was not found"

**Root Cause**: Using `next-intl` package instead of project's custom `@/i18n` pattern

**Fix Pattern**:
```tsx
// ❌ WRONG - Project doesn't use next-intl
import { useTranslations } from "next-intl";
const t = useTranslations();

// ✅ CORRECT - Use custom i18n
import { getTranslations } from "@/i18n";
const [t, setT] = useState<Record<string, any>>({});

useEffect(() => {
  const loadTranslations = async () => {
    const translations = await getTranslations(locale === "pt" ? "pt" : "en");
    setT(translations);
  };
  loadTranslations();
}, [locale]);

// Helper to safely access nested keys
const getT = (key: string) => {
  const keys = key.split('.');
  let value: any = t;
  for (const k of keys) {
    value = value?.[k];
  }
  return typeof value === 'string' ? value : key;
};

// Add loading guard
if (loading || !t.pages) return <LoadingState />;
```

**Prevention**:
- [ ] Never import from `next-intl`
- [ ] Always use `getTranslations()` from `@/i18n`
- [ ] Always add loading guard: `if (loading || !t.pages)`
- [ ] Read: `.github/instructions/ai-marketing-agent-ux-guidelines.instructions.md` → "Translation Pattern"

---

### 🔴 Critical: Hardcoded AI Providers

**Symptom**: Providers don't reflect user configurations, or new providers don't appear

**Root Cause**: Providers hardcoded in frontend instead of loaded from database

**Fix Pattern**:
```tsx
// ❌ WRONG - Hardcoded providers
const providers = [
  { id: 'openai', name: 'OpenAI' },
  { id: 'stability', name: 'Stability AI' }
];

// ✅ CORRECT - Database-driven
const [providers, setProviders] = useState<AIProviderConfig[]>([]);
useEffect(() => {
  const loadProviders = async () => {
    const data = await getUserAIProviders(); // From API
    setProviders(data);
  };
  loadProviders();
}, []);
```

**Prevention**:
- [ ] Never hardcode provider lists in code
- [ ] Always fetch via `getUserAIProviders()` API call
- [ ] Providers configured in MongoDB `ai_providers` collection
- [ ] Read: `.github/copilot-instructions.md` → "Key Principle: Database-Driven AI Providers"

---

### 🟠 Important: Port Configuration

**Symptom**: Frontend can't connect to backend API, CORS errors

**Root Cause**: Backend running on wrong port (not 8088)

**Fix Pattern**:
```bash
# ❌ WRONG - Any port other than 8088
uvicorn app.main:api_app --port 8000
uvicorn app.main:api_app --port 8089

# ✅ CORRECT - Must be 8088
uvicorn app.main:api_app --host 127.0.0.1 --port 8088 --reload
```

**Prevention**:
- [ ] Backend MUST run on port 8088 (non-negotiable)
- [ ] Frontend configured in `next.config.js` to proxy to 8088
- [ ] CORS explicitly allows `localhost:3001` and `localhost:3000`
- [ ] Read: `.github/copilot-instructions.md` → "Port Configuration (CRITICAL)"

---

### 🟠 Important: Error Handling Pattern

**Symptom**: Alerts instead of rich error UI, no correlation IDs, poor UX

**Root Cause**: Using `alert()` or `console.error()` instead of `AIErrorDisplay`

**Fix Pattern**:
```tsx
// ❌ WRONG - Using alert
catch (error) {
  alert("An error occurred!");
}

// ✅ CORRECT - Using AIErrorDisplay
import { AIErrorDisplay } from "@/components/ui/ai-error-display";
const [aiError, setAiError] = useState<any>(null);

catch (error: any) {
  if (error.error_details) {
    setAiError(error.error_details); // Rich error with correlation ID
  }
}

// In JSX
{aiError && <AIErrorDisplay error={aiError} onRetry={() => setAiError(null)} />}
```

**Prevention**:
- [ ] Never use `alert()` for error messages
- [ ] Always use `<AIErrorDisplay>` component
- [ ] Backend returns enriched errors with correlation IDs
- [ ] Axios interceptor adds correlation IDs to requests
- [ ] Read: `.github/copilot-instructions.md` → "Error Handling Pattern"

---

### 🟡 Moderate: File Organization

**Symptom**: Files at project root, clutter, hard to find code

**Root Cause**: Creating files in wrong directories

**Fix Pattern**:
```bash
# ❌ WRONG - At project root
touch test_script.py
touch debug.js

# ✅ CORRECT - In appropriate directories
touch debug/test_script.py
touch tests/frontend/debug.html
```

**Prevention**:
- [ ] Backend code → `/app/`
- [ ] Frontend code → `/frontend/src/`
- [ ] Tests → `/tests/`
- [ ] Debug scripts → `/debug/`
- [ ] Documentation → `/docs/`
- [ ] **NEVER create files at project root**
- [ ] Read: `.github/instructions/ai-marketing-agent.development-best-practices.instructions.md` → "File Organization"

---

### 🟡 Moderate: Missing Type Safety

**Symptom**: TypeScript errors, runtime type errors, hard to debug

**Root Cause**: Using `any` type or missing type annotations

**Fix Pattern**:
```tsx
// ❌ WRONG - Using any
const handleClick = (data: any) => { ... }

// ✅ CORRECT - Proper types
import { AIProviderConfig } from "@/types";
const handleClick = (data: AIProviderConfig) => { ... }
```

**Prevention**:
- [ ] Never use `any` type
- [ ] Import types from `@/types`
- [ ] Use optional chaining: `provider?.apiKey`
- [ ] Use nullish coalescing: `provider.name ?? 'Unknown'`
- [ ] Read: `.github/instructions/ai-marketing-agent-fix-bug.instructions.md` → "TypeScript Type Safety"

---

## 📋 Pre-Task Checklist (AI Assistants)

Before starting ANY task, verify:

**For UI/UX Changes:**
- [ ] Read `.github/instructions/ai-marketing-agent-ux-guidelines.instructions.md`
- [ ] Understand React Hooks rules (section "React Hooks Best Practices")
- [ ] Understand translation pattern (section "Translation Pattern")
- [ ] Check "Common Mistakes" above for hooks and i18n violations

**For Bug Fixes:**
- [ ] Read `.github/instructions/ai-marketing-agent-fix-bug.instructions.md`
- [ ] Check "Common Bug Patterns" section
- [ ] Identify root cause before applying fix
- [ ] Check "Common Mistakes" above for similar patterns

**For Any Code Change:**
- [ ] Read `.github/copilot-instructions.md` (this file)
- [ ] Understand file organization rules
- [ ] Understand error handling pattern
- [ ] Never hardcode AI providers
- [ ] Use port 8088 for backend
- [ ] Check "Common Mistakes" above

---

## Reference Documents
- `.github/instructions/README.md` - **Instruction files index and decision trees**
- `.github/instructions/ai-marketing-agent.architecture-and-development-guidelines.instructions.md` - Full architecture
- `.github/instructions/ai-marketing-agent-fix-bug.instructions.md` - Bug fixing workflow
- `.github/instructions/ai-marketing-agent-ux-guidelines.instructions.md` - UX and React patterns
- `docs/MONGODB_ARCHITECTURE.md` - Database schema details
- `docs/authentication-guide.md` - Auth system documentation
- `CONTRIBUTING.md` - Development workflow and standards
