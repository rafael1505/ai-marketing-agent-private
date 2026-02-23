# AI Marketing Agent - Instruction Files Index

**Version**: 2.0.0  
**Last Updated**: January 29, 2025  
**Maintainer**: Rafael Amorim

> **🔄 SDD MIGRATION (2026):** These instruction files are now **secondary references**. The authoritative source is **Spec Kit SDD** in `spec/`:
> - Constitution: `spec/constitution/project-constitution.speckit.md`
> - Process specs: `spec/process/*.speckit.md`
> 
> **When in doubt, follow Spec Kit specs.** These files remain for historical reference.

---

## 📚 Quick Navigation

This directory contains specialized instruction files that guide AI-assisted development for the AI Marketing Agent project.

| File | Purpose | When to Consult |
|------|---------|-----------------|
| [copilot-instructions.md](../copilot-instructions.md) | Main coordination file | **ALWAYS** - Start here for all tasks |
| [ai-marketing-agent.prompt.md](../prompts/ai-marketing-agent.prompt.md) | Original project vision | Understanding overall goals |
| [architecture-and-development-guidelines](./ai-marketing-agent.architecture-and-development-guidelines.instructions.md) | System design rules | Structural changes, new features |
| [development-best-practices](./ai-marketing-agent.development-best-practices.instructions.md) | Code quality standards | Writing any code |
| [fix-bug](./ai-marketing-agent-fix-bug.instructions.md) | Debugging workflow | **Required** before fixing bugs |
| [ux-guidelines](./ai-marketing-agent-ux-guidelines.instructions.md) | UI/UX design rules | **Required** for frontend changes |

---

## � Decision Tree for AI Assistants

### Making a UI Change?
```
1. Read `.github/copilot-instructions.md` (Material creation workflow, error handling)
2. Read `.github/instructions/ai-marketing-agent-ux-guidelines.instructions.md` (React Hooks, design patterns)
3. Read `.github/instructions/ai-marketing-agent.development-best-practices.instructions.md` (Component organization)
4. Apply changes
5. Run Pre-Commit Checklist from UX guidelines (React Hooks verification)
6. Test in development mode (React Hook warnings enabled)
```

### Fixing a Bug?
```
1. Read `.github/copilot-instructions.md` (Error handling pattern)
2. Read `.github/instructions/ai-marketing-agent-fix-bug.instructions.md` (Bug diagnosis workflow)
3. Check "Common Bug Patterns" section (React Hooks, TypeScript, Performance, API)
4. Apply fix
5. Update tests in `/tests/`
6. Update docs if behavior changed
```

### Adding a Feature?
```
1. Read `.github/copilot-instructions.md` (Architecture overview, database patterns)
2. Read `.github/instructions/ai-marketing-agent.architecture-and-development-guidelines.instructions.md` (Clean architecture)
3. Read `.github/instructions/ai-marketing-agent.development-best-practices.instructions.md` (File placement)
4. Implement feature
5. Add tests
6. Update documentation
```

---

## ⚠️ Critical Rules (Most Violated)

### 1. React Hooks Must Be at Top Level
**Location**: `ai-marketing-agent-ux-guidelines.instructions.md` → "React Hooks Best Practices"

**Violation Example:**
```tsx
// ❌ WRONG
function MyComponent({ providers }) {
  if (providers.length > 0) {
    const [selected, setSelected] = useState(null); // ERROR!
  }
}

// ✅ CORRECT
function MyComponent({ providers }) {
  const [selected, setSelected] = useState(null);
  if (providers.length > 0) {
    // Use selected state here
  }
}
```

**Why it's critical**: Causes "Rendered more hooks than during the previous render" error.

---

### 2. Use Custom i18n, Not next-intl
**Location**: `ai-marketing-agent-ux-guidelines.instructions.md` → "Translation Pattern"

**Violation Example:**
```tsx
// ❌ WRONG - Causes context error
import { useTranslations } from "next-intl";
const t = useTranslations();

// ✅ CORRECT - Project pattern
import { getTranslations } from "@/i18n";
const [t, setT] = useState<Record<string, any>>({});
useEffect(() => {
  const translations = await getTranslations(locale === "pt" ? "pt" : "en");
  setT(translations);
}, [locale]);
```

**Why it's critical**: Project doesn't use `next-intl` package; causes "context not found" runtime error.

---

### 3. Always Use AIErrorDisplay Component
**Location**: `.github/copilot-instructions.md` → "Error Handling Pattern"

**Violation Example:**
```tsx
// ❌ WRONG
alert("Error occurred!");

// ✅ CORRECT
<AIErrorDisplay error={error} onRetry={handleRetry} />
```

**Why it's critical**: Breaks error handling consistency, correlation IDs, and i18n support.

---

### 4. Never Hardcode AI Providers
**Location**: `.github/copilot-instructions.md` → "Key Principle: Database-Driven AI Providers"

**Violation Example:**
```tsx
// ❌ WRONG
const providers = ['openai', 'stability'];

// ✅ CORRECT
const providers = await getUserAIProviders();
```

**Why it's critical**: Providers are database-driven, not hardcoded. User configurations stored in MongoDB.

---

### 5. Port 8088 is Non-Negotiable
**Location**: `.github/copilot-instructions.md` → "Port Configuration (CRITICAL)"

**Violation Example:**
```bash
# ❌ WRONG
uvicorn app.main:api_app --port 8089

# ✅ CORRECT
uvicorn app.main:api_app --port 8088
```

**Why it's critical**: Frontend proxy (`next.config.js`) expects port 8088 exactly. Changing breaks API connectivity.

---

### 6. Never Create Files at Project Root
**Location**: `ai-marketing-agent.development-best-practices.instructions.md` → "File Organization"

**Violation Example:**
```bash
# ❌ WRONG
touch test_script.py  # At project root

# ✅ CORRECT
touch debug/test_script.py  # In appropriate directory
```

**Why it's critical**: Maintains clean project structure and separation of concerns.

---

## 📊 Instruction File Versions

| File | Version | Last Updated | Status |
|------|---------|--------------|--------|
| copilot-instructions.md | 1.1.0 | 2025-01-29 | **Updated** |
| ai-marketing-agent.prompt.md | 1.0.0 | Original | Reference |
| architecture-and-development-guidelines | 1.0.0 | 2025-01-28 | Active |
| development-best-practices | 1.0.0 | 2025-01-28 | Active |
| fix-bug | 2.0.0 | 2025-01-29 | **Updated** |
| ux-guidelines | 2.0.0 | 2025-01-29 | **Updated** |

---

## 📋 Quick Checklists

### Before Committing ANY Code
- [ ] Read relevant instruction files (see Decision Tree above)
- [ ] No TypeScript errors (`npm run type-check` if available)
- [ ] No console errors in development mode
- [ ] Follows file organization rules (no root files)
- [ ] Uses project patterns (custom i18n, AIErrorDisplay, etc.)

### Before Committing Frontend Code
- [ ] All hooks at top level of components
- [ ] No `next-intl` imports (use `@/i18n`)
- [ ] Translation loading includes guard: `if (loading || !t.pages)`
- [ ] Uses shadcn/ui components
- [ ] Follows Apple-inspired UX guidelines
- [ ] Responsive design tested

### Before Committing Backend Code
- [ ] No hardcoded providers (database-driven)
- [ ] Port 8088 used for API server
- [ ] Error responses include correlation IDs
- [ ] Business logic in `app/services/`, not routes
- [ ] Database operations in `app/db/`
- [ ] Type hints and docstrings present

---

## ❓ Questions?

If instructions conflict or are unclear:
1. Follow precedence order (Copilot Instructions > Specialized > Main Prompt)
2. Consult this README for common patterns
3. Check "Common Mistakes" in Copilot Instructions
4. When in doubt, **ask before implementing**

---

**Remember**: These instructions exist to **prevent bugs**, not slow you down. Taking 2 minutes to read the right file saves 2 hours of debugging. 🚀

---

## 🔄 Update Process

---

## 📋 Instruction Hierarchy

When conflicts arise, follow this precedence order:

1. **Copilot Instructions** (`.github/copilot-instructions.md`) - Quick reference and critical overrides
2. **Specialized Instructions** (`.github/instructions/*.instructions.md`) - Context-specific rules
3. **Main Prompt** (`.github/prompts/ai-marketing-agent.prompt.md`) - Original project vision

**Golden Rule**: More specific instructions override general ones. When in doubt, consult this README first.

---

## 🔄 Update Process

When modifying instruction files:

1. **Review impact** - Check if changes affect other files
2. **Update cross-references** - Ensure links remain valid
3. **Test with AI** - Verify AI assistants interpret correctly
4. **Version control** - Commit with descriptive message
5. **Document changes** - Note in commit message and/or docs

---

## 📁 File Descriptions

### copilot-instructions.md
**Purpose**: Main coordination file for GitHub Copilot  
**Contains**:
- Architecture overview
- Critical workflows (Material Creation, Error Handling)
- File organization rules
- Common pitfalls
- Quick decision tree

### ai-marketing-agent.prompt.md
**Purpose**: Original system prompt defining project vision  
**Contains**:
- Project context and objectives
- Repository structure
- File generation rules
- Coding standards
- i18n behavior

### architecture-and-development-guidelines.instructions.md
**Purpose**: Technical architecture and design decisions  
**Contains**:
- Stack overview (FastAPI, Next.js, MongoDB)
- Environment rules (ports, Docker)
- Clean architecture principles
- AI provider integration patterns
- Directory structure

### development-best-practices.instructions.md
**Purpose**: Code quality and conventions  
**Contains**:
- Backend best practices (PEP 8, type hints)
- Frontend best practices (TypeScript, React)
- File creation policy
- Version control guidelines
- Testing requirements

### fix-bug.instructions.md
**Purpose**: Bug fixing and QA workflow  
**Contains**:
- Debugging procedures
- Root cause analysis approach
- Pre-fix checklist
- Testing requirements
- Documentation update requirements

### ux-guidelines.instructions.md
**Purpose**: UI/UX design principles  
**Contains**:
- Apple-inspired design philosophy
- Layout and typography guidelines
- Color palette
- Component patterns (shadcn/ui)
- Accessibility requirements (WCAG AA)

---

## 🎓 Best Practices

### DO:
✅ Read relevant instruction files before starting work  
✅ Follow the decision tree for file placement  
✅ Use cross-references to understand context  
✅ Check pre-fix checklists before committing  
✅ Maintain consistency with existing patterns  

### DON'T:
❌ Ignore instruction hierarchy  
❌ Create files at project root  
❌ Use `alert()` for errors (use `AIErrorDisplay`)  
❌ Hardcode AI providers (database-driven)  
❌ Change ports to fix issues (debug instead)  
❌ Skip tests when fixing bugs  

---

## 📊 Metrics

**Current Status**:
- **Clarity**: 9/10 - Clear hierarchy and references
- **Consistency**: 9/10 - All conflicts resolved
- **Completeness**: 9/10 - Comprehensive coverage
- **Maintainability**: 9/10 - Single source of truth

**Last Updated**: October 29, 2025  
**Version**: 1.0.0 (Phase 2 Complete)

---

## 📞 Support

For questions or suggestions about these instructions:
1. Review existing instruction files
2. Check cross-references
3. Consult project maintainer (Rafael Amorim)
4. Update documentation if pattern is unclear

---

## 🔗 Related Documentation

- [INSTRUCTION_FILES_ANALYSIS.md](../../docs/INSTRUCTION_FILES_ANALYSIS.md) - Comprehensive analysis and harmonization report
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - General contribution guidelines
- [docs/](../../docs/) - Project documentation

---

**Maintained by**: AI Marketing Agent Project Team  
**Last Review**: October 29, 2025
