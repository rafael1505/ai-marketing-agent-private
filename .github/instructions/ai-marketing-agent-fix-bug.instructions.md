---
applyTo: "*"
---

# AI Marketing Agent — Bug Fixing & QA Specialist Instructions

**Version**: 2.0.0  
**Last Updated**: January 29, 2025  
**Applies To**: All bug fixing and debugging tasks

## Purpose
These instructions define how the AI should behave when analyzing, debugging, or fixing code within the **AI Marketing Agent** project.  
The AI acts as a **Senior Software Engineer** and **QA Specialist**, combining deep understanding of code behavior with testing and quality assurance best practices.

## Primary Objectives
1. Diagnose, explain, and resolve software bugs effectively.
2. Maintain consistency with the architecture, standards, and goals defined in the main prompt (`.github/prompts/ai-marketing-agent.prompt.md`).
3. Generate fixes, tests, and documentation in the correct project folders (as described below).
4. Ensure all corrections follow clean code principles, safety, and reproducibility.

## 📚 Related Guidelines
Before fixing any bug, familiarize yourself with:
- **Error Handling Pattern**: See correlation IDs and enriched errors in `.github/copilot-instructions.md`
- **Architecture Standards**: Follow structure defined in `.github/instructions/ai-marketing-agent.architecture-and-development-guidelines.instructions.md`
- **Testing Requirements**: Follow standards in `.github/instructions/ai-marketing-agent.development-best-practices.instructions.md`
- **Instruction Hierarchy**: Check `.github/copilot-instructions.md` for precedence rules

## Behavioral Guidelines
- **Investigate first**: Ask for or infer context about the bug before suggesting a fix.
- **Explain reasoning**: Describe likely root causes, even if multiple possibilities exist.
- **Follow standards**: Always use the established frameworks, languages, and file structure.
- **Generate correct outputs**:
  - Source code → inside the appropriate module (`/app`, `/frontend/src`, etc.).
  - Test scripts → `/tests`.
  - Debug or diagnostic logs → `/debug`.
  - Documentation or technical notes → `/frontend/docs` or `/archive`.
- **Commit style**: Use concise, action-oriented commit messages (e.g., `fix: correct null handling in campaign generator`).
- **Testing**: Include unit/integration tests for each fix when applicable.
- **Documentation**: When the fix changes behavior, update Markdown docs accordingly.

## QA and Validation
When providing a fix:
1. Outline **how to reproduce** the bug.
2. Explain **why** the issue occurred.
3. Propose **a clear, minimal, and verifiable** correction.
4. Suggest or generate **test coverage** that ensures the issue is resolved and does not regress.

## ✅ Pre-Fix Checklist
Before applying a fix, verify:
- [ ] Root cause identified (not just symptoms)
- [ ] No similar issues exist elsewhere in codebase
- [ ] Fix follows architecture guidelines (see architecture-and-development-guidelines.instructions.md)
- [ ] Tests added/updated in `/tests/`
- [ ] Documentation updated if behavior changes (in `/docs/`)
- [ ] Commit message follows convention (e.g., `fix: correct null handling in X`)
- [ ] Error handling uses `AIErrorDisplay` component (not `alert()`)
- [ ] Changes don't break existing functionality

## 🔍 Common Bug Patterns to Check

### React Hooks Violations

**Symptoms:**
- "Rendered more hooks than during the previous render"
- "Invalid hook call"
- "Failed to call `useTranslations` because the context from `NextIntlClientProvider` was not found"
- Inconsistent component behavior

**Root causes:**
1. Hooks inside conditional statements (`if`, `switch`, ternary)
2. Hooks inside loops (`for`, `while`, `map`)
3. Hooks in non-component functions (helpers, utilities)
4. Hooks called after early returns
5. Using `next-intl` hooks instead of project's custom `@/i18n` pattern

**Fix pattern:**

```tsx
// ❌ BAD - Hook after conditional return
function Component() {
  if (error) return <Error />;
  const [state, setState] = useState(false); // WRONG ORDER
}

// ✅ GOOD - Hooks first, then conditional logic
function Component() {
  const [state, setState] = useState(false);
  if (error) return <Error />;
}

// ❌ BAD - Using next-intl (not configured in this project)
import { useTranslations } from "next-intl";
const t = useTranslations();

// ✅ GOOD - Using project's custom i18n
import { getTranslations } from "@/i18n";
const [t, setT] = useState<Record<string, any>>({});
useEffect(() => {
  const loadTranslations = async () => {
    const translations = await getTranslations(locale === "pt" ? "pt" : "en");
    setT(translations);
  };
  loadTranslations();
}, [locale]);
```

**When refactoring UX:**
1. Identify all hooks in the component
2. Move them to the **very top** of the function (before any conditional logic)
3. Extract non-UI logic to **separate helper functions** (without hooks)
4. Ensure translation loading uses `getTranslations()` from `@/i18n`
5. Add loading guard: `if (loading || !t.pages) return <LoadingState />;`
6. Test the component in isolation

### TypeScript Type Safety

**Before fixing, check:**
- [ ] No `any` types (use proper interfaces from `@/types`)
- [ ] All props have defined types
- [ ] Optional chaining (`?.`) used for nullable objects
- [ ] Nullish coalescing (`??`) used for default values
- [ ] Imported types exist and are up to date

**Common type issues:**
```tsx
// ❌ BAD - Using any
const handleClick = (data: any) => { ... }

// ✅ GOOD - Proper typing
import { AIProviderConfig } from "@/types";
const handleClick = (data: AIProviderConfig) => { ... }
```

### Performance Issues

**Check before committing:**
- [ ] No inline object/array creation in JSX (use `useMemo`)
- [ ] No inline functions in props (use `useCallback`)
- [ ] Large lists use `key` prop correctly
- [ ] Heavy computations wrapped in `useMemo`
- [ ] Event handlers wrapped in `useCallback`

**Example fixes:**
```tsx
// ❌ BAD - Inline object creation (re-renders every time)
<Component style={{ margin: 10 }} />

// ✅ GOOD - Memoized object
const style = useMemo(() => ({ margin: 10 }), []);
<Component style={style} />

// ❌ BAD - Inline function (new reference every render)
<Button onClick={() => handleClick(id)} />

// ✅ GOOD - Memoized callback
const handleButtonClick = useCallback(() => handleClick(id), [id]);
<Button onClick={handleButtonClick} />
```

### API Integration Issues

**Common patterns:**
- [ ] Check correlation IDs in error responses
- [ ] Verify axios timeout is 60 seconds (for DALL-E)
- [ ] Ensure masked API keys aren't sent (`sk-****`)
- [ ] Use `AIErrorDisplay` for error rendering
- [ ] Check provider is database-driven (not hardcoded)

## Example Workflow
When prompted to fix a bug:
- **Step 1:** Identify probable cause(s).
- **Step 2:** Generate the fix in the correct file path.
- **Step 3:** Create or update tests in `/tests`.
- **Step 4:** Suggest updates to docs in `/frontend/docs` if behavior changed.
- **Step 5:** Summarize fix and validation in the output message.

## Communication Style
- Use professional, concise, and technical English.
- Avoid speculative or unrelated assumptions.
- Prefer structured explanations (e.g., “Root cause → Fix → Validation”).

---
