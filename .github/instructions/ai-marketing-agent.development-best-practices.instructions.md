# AI Marketing Agent – Development Best Practices Instruction

**Version**: 1.0.0  
**Last Updated**: January 28, 2025  
**Applies To**: All development work (frontend and backend)

## 🎯 Objective
This instruction defines the **development best practices** for the AI Marketing Agent project.  
Its goal is to ensure consistent, scalable, and maintainable code across all frontend and backend components.

---

## 🧠 General Guidelines

1. Always follow the structure and coding standards defined in `.github/prompts/ai-marketing-agent.system.prompt.md`.
2. Maintain a **clean, readable, and modular** codebase.
3. Never hardcode values that should come from:
   - The database
   - Environment variables
   - Config files
4. Avoid creating placeholder pages or dummy components unless explicitly requested.
5. Always preserve port configurations (see `.github/copilot-instructions.md` for details).

---

## ⚙️ Stack-Specific Best Practices

### 🐍 Backend (Python + FastAPI or Django)

- Respect **PEP 8** and **Clean Architecture**.
- Use **type hints** and **docstrings** for all functions and classes.
- Separate responsibilities:
  - `app/routes/` → endpoints
  - `app/services/` → business logic
  - `app/models/` → database models
  - `app/utils/` → helpers or shared tools
- Validate requests using **Pydantic models**.
- Add meaningful logging for all API errors.
- Implement exception handling that clearly reports the root cause.

### ⚛️ Frontend (Next.js + React + TypeScript)

- Use **TypeScript strictly** (avoid `any`).
- Follow component organization under:
  - `frontend/src/components/`
  - `frontend/src/pages/`
  - `frontend/src/hooks/`
  - `frontend/src/services/`
- Use **TailwindCSS** and **shadcn/ui** for visual consistency.
- Apply **UX guidelines inspired by Apple’s design language**, focusing on:
  - Simplicity
  - Accessibility
  - Smooth animations and feedback
  - Balanced spacing and alignment
- Keep AI providers **database-driven** — never hardcode them in the frontend.

---

## 🧩 File Creation Policy

| File Type | Destination Directory |
|------------|-----------------------|
| Documentation (`.md`) | `docs/` |
| Backend or API code | `app/` |
| Frontend components | `frontend/src/` |
| Tests | `tests/` |
| Debug or diagnostics | `debug/` |
| Experimental or temporary | `archive/` |

> ⚠️ Files must **never** be created at the project root.  
> If the location is unclear, ask before creating.

---

## 🔄 Version Control & Collaboration

- Write **clear, concise commit messages** (use imperative mood).
- Each feature or fix should be developed in a **dedicated branch**.
- Always request **code review** before merging to `main`.
- Tag and document every release under `docs/release-notes.md`.

---

## 🧪 Testing & Quality Assurance

- Use **pytest** for Python and **vitest/jest** for TypeScript.
- Each major module must have **unit and integration tests**.
- Include error simulation tests for AI provider connectivity.
- Document the test coverage summary in `docs/test-report.md`.

---

## 🧭 Expected Behavior in AI-Assisted Development

When AI assistants (Copilot, ChatGPT, Claude, etc.) are used within this project:

1. Always operate under the **AI Marketing Agent context**.
2. When generating files, place them in the proper directories listed above.
3. Respect the stack, coding standards, and architecture defined in this instruction.
4. Avoid unnecessary regeneration of existing components — debug first, replace only if confirmed broken.

---

## 🏁 Conclusion

This instruction ensures that all contributors — human or AI — follow the same development principles.  
By enforcing these practices, the AI Marketing Agent project will remain **stable, elegant, and scalable**, aligning technical excellence with Apple-inspired user experience.
