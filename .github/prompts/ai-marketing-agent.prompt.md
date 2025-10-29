# AI Marketing Agent – Developer Prompt

## 🧠 Project Context

This repository contains the **AI Marketing Agent**, a full-stack system designed to create visual marketing campaign materials using **Artificial Intelligence**.  

The system must provide a **modern, fluid, and clean interface** with:

- Secure login and authentication  
- Company and user registration  
- CRUD for marketing material types  
- Integration with AI image/text generation APIs: **OpenAI DALL-E**, **Stability AI**, **Replicate**, **HuggingFace** (with planned support for Anthropic Claude, Midjourney, LM Studio, Ollama)  
- Multilingual support (🇺🇸 English / 🇧🇷 Portuguese)  
- Backend using **FastAPI (Python)** and **MongoDB (containerized)**  
- Based on **Clean Code**, modular architecture, automated tests, and complete documentation in Markdown  

---

## 🧩 Repository Structure (Standard)

AI-MARKETING-AGENT/  
├── .github/  
│ └── instructions/
│ └── prompts/  
│ └── ai-marketing-agent.system.prompt.md  
├── .vscode/  
│ ├── launch.json  
│ ├── settings.json  
│ └── tasks.json  
├── app/  
├── archive/  
├── database/  
├── debug/  
├── docs/  
├── frontend/  
│ ├── .next/  
│ ├── certificates/  
│ ├── node_modules/  
│ ├── pages/  
│ ├── public/  
│ ├── src/  
│ └── tmp/  
├── logs/  
├── scripts/  
├── tests/  
├── venv/  
└── volumes/  

---

## ⚙️ File Generation Rules

All automatically created files **must follow this structure**.

| File Type | Target Folder | Notes |
|------------|----------------|-------|
| Test scripts (`*.py`, `*.js`, `*.ts`, `*.test.js`) | `tests/` | Use descriptive names, e.g. `api-connection-test.py` |
| Documentation (`*.md`) | `docs/` | Never generate docs at the root |
| System Prompts / AI Templates | `.github/prompts/` | AI system prompts only (NOT for general docs) |
| Assets (images, icons, logos) | `frontend/public/` | Group AI provider SVGs under `ai-providers/` |
| API and backend code | `app/` | Core backend logic (FastAPI / Django) |
| Database scripts / seeds / schemas | `database/` | Structure definitions and initialization scripts |
| Experimental or prototype code | `archive/` | Anything outside production scope |

⚠️ Never create files at the repository root.  
If the file type is not listed, ask for confirmation before creating it.

If the assistant cannot determine the correct folder, the default target must be `archive/` and a clarification should be requested.

---

## 🧱 Coding Standards

### Backend (Python / FastAPI)
- Follow **PEP 8** and **Clean Code** principles  
- Always include **type hints**  
- Separate business logic into a `services/` folder  
- Validate input using **Pydantic**  
- Use docstrings and Swagger for route documentation  

### Frontend (Next.js / React / TypeScript)
- Use **TypeScript** only  
- Recommended folder structure:  
  src/components/  
  src/pages/  
  src/hooks/  
  src/services/  
- Use **TailwindCSS** and **shadcn/ui** for UI components  
- Avoid `any`; ensure strong typing  
- Keep components small, clean, and commented  
- Use **ESLint** and **Prettier** consistently  

---

## 🌍 i18n Behavior

- The system and all user-facing messages must support both **English and Portuguese**.  
- When generating UI text, validation messages, or errors, wrap them in i18n functions (e.g., `t('error.limitExceeded')`).  
- Documentation and comments should remain in **English**.  

---

## 🧾 Documentation Rules (`.md`)

All documentation files must:

- Be placed under `docs/`
- Be named according to purpose (e.g., `api-endpoints.md`, `architecture-overview.md`, `deployment-guide.md`, etc.)
- Contain the following sections:
  - Context  
  - Objective  
  - Instructions  
  - Usage examples  
- Be written in **English**

---

## 🧪 Automated Testing Rules

- All test files go inside the **`tests/`** directory  
- Use consistent naming: `test_<feature>.py`  
- Each test should include:
  - A clear header describing its purpose  
  - Well-commented sections  
  - Clean and readable logging  
- Preferred frameworks:
  - Python → `pytest`
  - JS/TS → `vitest` or `jest`

---

## 🌐 Assistant Behavior (Chat Integration)

When interacting within this project, the assistant must:

1. Automatically assume the **AI Marketing Agent** context — no need to redefine it in every chat.  
2. Follow the project’s objectives: assist in architecture, design, coding, testing, and documentation.  
3. Before generating a file, confirm:
   - File type and suggested name  
   - Correct target directory based on the structure above  
   - Avoid overwriting existing files without confirmation  
4. Always maintain consistency with the defined tech stack, naming conventions, and architecture.  
5. If uncertain about file placement, ask:  
   “Where should this file be created — `docs/`, `tests/`, or another folder?”  

---

## 📦 Documentation and Test File Generation

When the assistant is instructed to generate a:  
- Documentation file (`.md`): create under `docs/`  
- Test script: create under `tests/`  
- API or backend file: create under `app/`  
- UI or frontend file: create under `frontend/src/`  
- Prototype or experiment: create under `archive/`

If unclear, the assistant must always ask for clarification before file creation.

---

## 🧭 Project Purpose Summary

This prompt defines the **development context, structure, and behavioral rules** for the **AI Marketing Agent** project.

Its purpose is to ensure that every chat, code generation, test, or documentation file is:
- Consistent with the system’s technical and business goals  
- Structured according to repository conventions  
- Clean, maintainable, and easily traceable  

By maintaining a shared prompt like this, any AI assistant (ChatGPT, GitHub Copilot, Claude, etc.) will behave as a **unified, context-aware development partner** across all interactions.  

---

# AI Marketing Agent — Copilot Project Guidelines

The following instructions are *strict rules* for this project.  
Always follow them unless explicitly told otherwise by Rafael Amorim.

---

## Architecture & Data Flow
- All AI providers (DALL-E, Replicate, Hugging Face, etc.) must be **database-driven**.
  - Do not hardcode provider logic or configurations in the frontend.
  - All provider parameters, configurations, and credentials must be retrieved from the backend via API.
- Never create dummy, placeholder, or duplicate pages unless explicitly requested.
  - When a page fails or throws an error, focus on **debugging and fixing the existing implementation**.
- The frontend must always run on port **3001**.
- The backend must always run on port **8088**.
  - Never change these ports to “fix” an error.
- Always follow clean code and separation of concerns principles.
- Never bypass or mock API calls unless Rafael explicitly asks.

---

## Testing Standards
- **Backend Testing**: Use Python's built-in `unittest` or manual test scripts (no pytest dependency currently).
  - Unit tests: `/tests/unit/`
  - Integration tests: `/tests/integration/`
  - Follow PEP 8 naming conventions (`test_*.py`)
- **Frontend Testing**: No testing framework currently configured.
  - HTML test suites available in `/tests/frontend/` for manual debugging
  - Component testing to be implemented with Vitest (recommended for Next.js 14)
- Always add/update tests when fixing bugs or adding features.

---

## General behavior
- When debugging, prefer to *analyze and fix* rather than *replace or recreate*.
- Ask for clarification before assuming large changes.
