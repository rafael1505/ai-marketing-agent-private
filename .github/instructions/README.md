# AI Marketing Agent - Instruction Files Index

## 📚 Quick Navigation

This directory contains specialized instruction files that guide AI-assisted development for the AI Marketing Agent project.

| File | Purpose | When to Use |
|------|---------|-------------|
| [copilot-instructions.md](../copilot-instructions.md) | Main reference and quick guide | **Always** - start here for any task |
| [ai-marketing-agent.prompt.md](../prompts/ai-marketing-agent.prompt.md) | Original project vision | Understanding project goals and context |
| [architecture-and-development-guidelines](./ai-marketing-agent.architecture-and-development-guidelines.instructions.md) | System design and structure | Making structural decisions, new features |
| [development-best-practices](./ai-marketing-agent.development-best-practices.instructions.md) | Code quality standards | Writing any code (backend or frontend) |
| [fix-bug](./ai-marketing-agent-fix-bug.instructions.md) | Debugging and QA workflow | Fixing issues, debugging problems |
| [ux-guidelines](./ai-marketing-agent-ux-guidelines.instructions.md) | UI/UX design principles | Frontend work, UI components |

---

## 🎯 How to Use These Instructions

### For AI Assistants (GitHub Copilot, ChatGPT, Claude, etc.)

1. **Always read** `.github/copilot-instructions.md` first
2. **Check the hierarchy** - more specific instructions override general ones
3. **Follow the decision tree** for file placement and task workflow
4. **Cross-reference** related files when working on complex tasks

### For Developers

1. Review these instructions when onboarding
2. Reference when unsure about project conventions
3. Update when making architectural changes
4. Follow the same standards as AI assistants

---

## 📋 Instruction Hierarchy

When conflicts arise, follow this precedence order:

1. **Copilot Instructions** - Quick reference and critical overrides
2. **Specialized Instructions** - Context-specific rules (this folder)
3. **Main Prompt** - Original project vision and general guidelines

**Golden Rule**: More specific instructions override general ones.

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
