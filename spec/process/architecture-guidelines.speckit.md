# Architecture & System Design Guidelines – Process Spec

## Purpose

Capture the system‑level architecture rules and constraints for the AI Marketing Agent.

## Scope

Applies to any structural change, new feature, or infrastructure‑level work.

## System Overview

- **Backend**: FastAPI (Python) on port 8088.
- **Frontend**: Next.js 14 (React + TypeScript) on port 3001.
- **Database**: MongoDB (Docker) on port 27017.
- **AI Providers**: Database‑driven via the `ai_providers` collection.

## Layered Architecture

- **API Layer**
  - Located in `app/api/v1/endpoints/`.
  - Thin controllers: validate input, call services, map results to HTTP responses.

- **Service Layer**
  - Located in `app/services/`.
  - Contains business logic and workflows (e.g., material creation stages, provider selection).

- **Data Access Layer**
  - Located in `app/db/`.
  - Uses the global Motor `mongodb` instance to access collections.
  - Responsible for indexes and persistence rules.

- **Frontend**
  - Pages: `frontend/src/app/[locale]/`.
  - Components: `frontend/src/components/`.
  - Services/API clients: `frontend/src/services/`.

## AI Provider Architecture

- Provider configurations (name, keys, models, capabilities) live in `mongodb.ai_providers`.
- Frontend loads provider lists from API endpoints, never from hardcoded arrays.
- All provider and external service integrations must be implemented via the MCP framework (no direct provider SDK calls from routes/components).
- Connection lifecycle (register, configure, enable, disable, remove) must be managed through a centralized MCP connection registry/service.
- Adding a new provider is done by:
  - Creating a new MCP connector that implements the shared connection contract,
  - Registering the connector in the MCP connection registry,
  - Updating DB configuration,
  - Surfacing provider metadata to the frontend.
- Removing a provider is done by:
  - Unregistering/disabling the MCP connector,
  - Cleaning connection configuration in storage,
  - Keeping API contracts stable for unaffected providers.

## MCP Connection Architecture

- All external connections (AI providers and future third-party integrations) must go through MCP abstractions.
- Define a shared connector contract so every connection follows the same methods (e.g., connect, validate, execute, health-check, disconnect).
- Use a registry/factory pattern to resolve connectors by ID, preventing hardcoded branching logic.
- Keep connection configuration data-driven so adding/removing connectors does not require route-layer changes.
- Route handlers and frontend clients must call application services only; services delegate integration work to MCP connectors.
- Feature flags or status fields should support safe rollout and quick disable/removal of a connector.

## Material Creation Workflow (Integration View)

- Stage 1 (Idea):
  - API creates a material with `stage="idea"`, `status="draft"`.
- Stage 2 (Refinement):
  - API coordinates AI image generation across providers.
  - Generated images and metadata are stored in `material.generated_images`.
- Stage 3 (Finalization):
  - API updates the material to `stage="finalization"`, `status="completed"` when user selects final image.

## Environment & Ports

- Backend must run on port 8088; frontend proxies to it.
- Do not change ports to fix issues; debug the root cause instead.
- CORS is configured to allow local development origins (e.g. `localhost:3001`).

## Architectural Acceptance Criteria

- New features respect the service / API / DB separation.
- AI providers remain database‑driven.
- All external integrations use MCP connectors behind a shared contract.
- Adding/removing a connection requires only connector registration/config updates, not route rewrites.
- The material 3‑stage workflow is preserved.
- Environment expectations (ports, DB, AI providers) stay consistent with the constitution.