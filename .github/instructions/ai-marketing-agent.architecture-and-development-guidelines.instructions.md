---
applyTo: "*"
description: "System architecture and design guidelines covering FastAPI backend structure, MongoDB patterns, clean architecture principles, AI provider integration, Material Creation Workflow, port configuration, and directory organization"
---

# 🧠 Instruction: Architecture & Development Guidelines

**Version**: 2.0.0  
**Last Updated**: November 6, 2025  
**Applies To**: All development work (backend architecture, database design, API structure, system design)

## 🎯 Goal
Ensure technical consistency, maintainability, and compliance with the architectural principles of the **AI Marketing Agent** project.  
This instruction defines how to structure the code, where business logic should reside, and how frontend, backend, and AI providers interact harmoniously.

---

## 🏗️ Stack Overview

- **Frontend:** Next.js (React + TypeScript)
- **Backend:** FastAPI (Python)
- **Database:** MongoDB (Docker container)
- **Infra:** Docker Compose
- **AI Providers:** DALL·E, Hugging Face, Replicate (and similar APIs)
- **i18n:** English and Portuguese (automatic detection)

---

## ⚙️ Environment Rules

> **Port Configuration**: See `.github/copilot-instructions.md` for detailed port assignments
- **Frontend port:** `3001`  
- **Backend port:** `8088`  
- **Database port:** `27017` (managed by Docker, internal)
- **No automatic port switching is allowed.**
- **Never create new placeholders or pages unless explicitly requested.**
- Always debug and fix the existing component first.

---

## 🧩 Architectural Guidelines

### 1. Clean Architecture & Responsibility Separation
- **Frontend:** UI rendering, input validation, and i18n messages only.  
  ❌ No business logic or AI API integration logic.  
  ✅ Uses centralized service layer for data access (API clients).
- **Backend:** Core business rules, API endpoints, AI provider orchestration, authentication, and persistence logic.  
- **Database:** Stores normalized entities (Users, Companies, Materials, etc.) with clear schema definitions.
- **AI Providers:** Modularized and database-driven configuration.  
  Never hardcode provider settings in the frontend or backend code.

---

### 2. Directory and Code Structure
Maintain the following logical boundaries:

AI-MARKETING-AGENT/  
├── .github/  
│ └── instructions/
│ └── prompts/  
├── .vscode/  
│ ├── launch.json  
│ ├── settings.json  
│ └── tasks.json  
├── app/ # FastAPI backend core
├── archive/  
├── database/ # MongoDB data scripts and schemas
├── debug/  
├── docs/  
├── frontend/ # Next.js app
│ ├── .next/  
│ ├── certificates/  
│ ├── node_modules/  
│ ├── pages/  
│ ├── public/  
│ ├── src/  
│ └── tmp/  
├── logs/  
├── scripts/ # Maintenance or build scripts
├── tests/ # Automated tests for backend and frontend
├── venv/  
└── volumes/  

---

### 3. Material Creation Workflow (3-Stage Pipeline)

The application follows a strict 3-stage material creation process:

**Stage 1: Idea** (`/materials/create`)
- User defines title, description, target audience, campaign objective, keywords
- Creates material record with `stage="idea"` and `status="draft"`
- Frontend form: Standard Next.js form with shadcn/ui components
- Backend endpoint: `POST /api/v1/materials` → inserts into `materials` collection

**Stage 2: Refinement** (`/materials/[id]/edit`)
- User generates AI images using configured providers
- Uses `enhanced-refinement-form.tsx` component for provider selection
- Backend workflow:
  1. `POST /api/v1/ai/generate-image` receives request
  2. Validates API keys via `isMaskedApiKey()` check
  3. Coordinates with provider-specific service (e.g., `OpenAIService`, `StabilityService`)
  4. Returns image URLs with metadata (provider, model, parameters)
- Images stored in `material.generated_images[]` array with:
  ```json
  {
    "id": "gen_123",
    "url": "https://...",
    "provider": "openai",
    "model": "dall-e-3",
    "prompt": "enhanced prompt",
    "created_at": "2025-01-28T10:00:00Z"
  }
  ```
- Frontend displays images with provider badges and selection interface

**Stage 3: Finalization**
- User selects final image from generated options
- Material moves to `stage="finalization"` and `status="completed"`
- Backend endpoint: `PATCH /api/v1/materials/{id}/finalize`
- Selected image becomes `material.final_image`

**Critical Rules**:
- Never skip stages (idea → refinement → finalization)
- Always validate `stage` before allowing operations
- Image generation must use database-configured providers (never hardcoded)
- Timeout handling: 60 seconds for DALL-E (show progress indicator)

---

### 4. AI Provider Integration

- All AI providers (e.g., DALL·E, Hugging Face, Replicate) must be **defined in the database** with:
  - Name, API key reference, endpoint, and capability metadata.
  - Dynamically loaded into the system (no hardcoded providers).
- Use a centralized **AI Provider Service** class to handle requests, caching, and fallback logic.
- When generating tests or docs, store outputs in:
  - `/tests/` → for test files  
  - `/docs/` → for all project documentation (architecture, guides, reports)

---

### 5. i18n and Localization

- Always wrap user-facing text with i18n functions.  
- Support both English and Portuguese translations.  
- Use language auto-detection from the browser or user profile.  
- Backend messages returned to the frontend should also be i18n-aware.

---

### 6. Quality and Test Rules

- All new features must include at least **unit tests** or **integration tests**.
- Always prefer **test-driven development (TDD)** when possible.
- Test scripts must be placed under `/tests/` and named following the convention:
  - `test_[module]_[feature].py` (backend)
  - `[feature].spec.tsx` (frontend)
- No test or documentation file should ever be created in the project root.

---

### 6. Code Style and Consistency

- **Frontend:**  
  - TypeScript strict mode enabled.  
  - Use React Hooks, functional components, and Next.js routing.  
  - Keep components small and reusable.  
  - Centralize API calls under `/frontend/src/services/`.

- **Backend:**  
  - Use Pydantic models for validation.  
  - Separate routers, models, and services by domain.  
  - Keep routes thin and business logic inside services.  
  - Follow clean and modular architecture principles.

---

### 7. Collaboration & Documentation

- Use Markdown (`.md`) for all internal docs under `/frontend/docs/`.  
- Automatically include code snippets or API references when describing features.  
- When generating or editing documentation, always save in the correct subfolder (never at project root).

---

### 8. Copilot Behavior Overrides

To guide AI-generated outputs consistently:
- Never move or rename core folders.
- Never change ports (keep `3001` / `8088`).
- Never create temporary files outside their intended directories.
- Always debug existing code instead of recreating it.
- Always respect i18n, architecture, and folder conventions.

---

## ✅ Summary

This instruction ensures:
- Technical discipline and clean separation of concerns.  
- Predictable and stable system behavior.  
- Database-driven AI provider configuration.  
- Strong adherence to clean code and maintainability principles.

---

**File name:**  
`.github/instructions/architecture-and-development-guidelines.instruction.md`

**Applies to:**  
All chats and code generation within the AI Marketing Agent project.

