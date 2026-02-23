# MCP Connector Contract

**Document ID**: `ARCH-MCP-CONTRACT-001`
**Spec reference**: `spec/process/architecture-guidelines.speckit.md` — ARCH-MCP-001 through ARCH-MCP-005
**Branch**: `003-architecture-core-and-compliance`
**Created**: 2026-02-23
**Status**: Authoritative

---

## 1. Purpose

This document is the single authoritative reference for every external connection
made by the AI Marketing Agent backend. It defines:

- The `MCPConnector` Protocol that all connectors MUST implement.
- The standard `error_details` schema that all error paths MUST return.
- The Registry/Factory pattern used to resolve connectors at runtime.
- The add/remove runbook for introducing or retiring a connector.

No route handler or service may call an external provider SDK directly.
All external calls MUST go through a connector that satisfies this contract.

---

## 2. MCPConnector Protocol

Every connector MUST implement the following `typing.Protocol`. The interface lives
in `app/services/mcp_connector.py`.

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class MCPConnector(Protocol):
    """
    Contract for every external connection in the AI Marketing Agent.

    Implementors: one class per provider (e.g. OpenAIConnector, StabilityConnector).
    Registration: each implementor is registered in MCPRegistry at application startup.
    Configuration: all credentials and settings come from the `ai_providers` MongoDB
                   collection (ARCH-MCP-003). Never hardcode API keys or base URLs.
    """

    async def connect(self) -> None:
        """
        Establish and validate the connection to the external service.

        Called once at startup (or on demand after a disconnect). MUST NOT raise
        on temporary network failures — log and set internal state instead.
        A successful call transitions the connector to READY state.
        """

    async def disconnect(self) -> None:
        """
        Tear down the connection cleanly.

        Release any persistent sessions, tokens, or pooled resources.
        MUST be idempotent — calling on an already-disconnected connector is safe.
        """

    async def validate(self) -> bool:
        """
        Validate credentials and configuration.

        Performs a lightweight probe (e.g. list models, auth ping) without
        consuming billable quota.

        Returns:
            True  — connector is properly configured and credentials are valid.
            False — credentials absent, invalid, or insufficient permissions.

        MUST NOT raise. Exceptions are caught and return False with logging.
        """

    async def execute(self, action: str, params: dict) -> dict:
        """
        Execute a domain action against the external service.

        Args:
            action: Provider-specific action name (e.g. "generate_image",
                    "list_models"). Connectors document their supported actions.
            params: Action parameters. Shape is action-specific and documented
                    per connector.

        Returns:
            Result dict. Shape is action-specific and documented per connector.
            On failure, raises MCPConnectorError (never returns a partial dict
            with an implicit failure flag).

        Raises:
            MCPConnectorError: Wraps all provider SDK exceptions. The error MUST
                               include a populated error_details dict conforming
                               to Section 3 of this document.
        """

    async def health_check(self) -> bool:
        """
        Return True if the connector is available and responsive right now.

        Intended for periodic liveness probes and the /health endpoint.
        A faster, cheaper check than validate() — may only ping connectivity.

        Returns:
            True  — connector is reachable and operational.
            False — connector is unreachable, misconfigured, or rate-limited.

        MUST NOT raise.
        """
```

### 2.1 Connector State Machine

```
         connect()
  INIT ──────────────► READY ──── execute()/health_check() ──► READY
                         │
                         │  disconnect()
                         ▼
                     DISCONNECTED
                         │
                         │  connect()
                         ▼
                       READY

  Any state + unrecoverable error ──► ERROR
  ERROR + connect() ──► READY (if resolved) or ERROR (if not)
```

### 2.2 Contract Invariants

| # | Invariant |
|---|-----------|
| I-1 | `health_check()` and `validate()` MUST NOT raise; they return `bool`. |
| I-2 | `execute()` MUST raise `MCPConnectorError` on any failure; never return a dict with a success flag. |
| I-3 | `disconnect()` MUST be idempotent. |
| I-4 | Connector instances MUST be stateless with respect to request data. Request parameters are passed through `execute(action, params)`, never stored on `self`. |
| I-5 | All configuration is read from MongoDB `ai_providers` collection at `connect()` time (and on `refresh_provider_configs()`). Never read from environment variables directly inside a connector — use the config dict supplied by the registry. |

---

## 3. Standard Error Model

All connector errors MUST be wrapped in `MCPConnectorError` and serialised as an
`error_details` dict. Routes and services MUST use this structure when building
HTTP error responses. Raw SDK exceptions or stack traces MUST NOT reach the HTTP
response layer.

### 3.1 `MCPConnectorError`

```python
from dataclasses import dataclass, field
from typing import Any
import uuid


@dataclass
class MCPConnectorError(Exception):
    """
    Raised by MCPConnector.execute() on any failure.

    The `error_details` attribute is the canonical representation used in HTTP
    responses (see Section 3.2).
    """
    error_type: str          # snake_case classification key (see Section 3.3)
    user_message: str        # i18n key — e.g. "errors.provider.unavailable"
    provider: str            # provider_id from ai_providers collection
    http_status: int         # intended HTTP status code for the response
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    details: dict = field(default_factory=dict)  # provider diagnostic data

    @property
    def error_details(self) -> dict[str, Any]:
        return {
            "error_type":     self.error_type,
            "user_message":   self.user_message,
            "provider":       self.provider,
            "correlation_id": self.correlation_id,
            "http_status":    self.http_status,
            "details":        self.details,
        }
```

### 3.2 `error_details` Schema

Every error response returned from a route handler MUST include this top-level
object.

```python
{
    "error_type":     str,   # snake_case — see canonical values in Section 3.3
    "user_message":   str,   # i18n key, e.g. "errors.provider.unavailable"
    "provider":       str,   # provider_id, e.g. "openai"
    "correlation_id": str,   # UUID — generated at route entry if absent
    "http_status":    int,   # HTTP status code, e.g. 503
    "details":        dict,  # optional provider-specific diagnostic data
}
```

Field rules:

| Field | Required | Rule |
|-------|----------|------|
| `error_type` | Yes | One of the canonical values in Section 3.3 or a namespaced extension `"<provider>.<reason>"`. |
| `user_message` | Yes | An i18n key from `frontend/src/i18n/locales/`. Never a raw English string. |
| `provider` | Yes | The `provider_id` as stored in `ai_providers` collection. |
| `correlation_id` | Yes | UUID. Generated at the route boundary; propagated through all layers. Never generated inside a connector. |
| `http_status` | Yes | The HTTP status code the route MUST return. |
| `details` | No | Provider-specific diagnostic dict. MUST NOT contain API keys, tokens, or PII. |

### 3.3 Canonical `error_type` Values

| `error_type` | Meaning | Typical `http_status` |
|---|---|---|
| `provider_unavailable` | Service unreachable or health_check failed | 503 |
| `provider_not_configured` | API key absent or `validate()` returned False | 503 |
| `provider_not_found` | `provider_id` not in registry | 400 |
| `invalid_api_key` | Authentication rejected by provider | 401 |
| `quota_exceeded` | Billing quota exhausted | 402 |
| `rate_limit_exceeded` | Too many requests; retry after `details.retry_after_seconds` | 429 |
| `content_policy_violation` | Prompt rejected by provider safety filter | 422 |
| `invalid_request` | Malformed action parameters | 400 |
| `timeout` | Provider did not respond within configured deadline | 504 |
| `service_error` | Provider returned 5xx | 502 |
| `unknown_error` | Unclassified failure | 500 |

---

## 4. Registry / Factory Pattern

Route handlers and services resolve connectors exclusively via `MCPRegistry`.
They MUST NOT branch on `provider_id` (no `if provider == "openai"` blocks).

### 4.1 `MCPRegistry` Interface

```python
class MCPRegistry:
    """
    Central registry that maps provider_id → MCPConnector instance.

    Populated at application startup from the `ai_providers` MongoDB collection.
    Refreshed on-demand by calling refresh() (e.g. after an admin saves new
    provider settings in the UI).
    """

    def get(self, provider_id: str) -> MCPConnector:
        """
        Return the live connector for provider_id.

        Raises:
            MCPConnectorError(error_type="provider_not_found", ...)
                if provider_id is not registered.
            MCPConnectorError(error_type="provider_not_configured", ...)
                if provider_id is registered but validate() is False.
        """

    def list_available(self) -> list[str]:
        """Return provider_ids of all connectors currently passing health_check()."""

    async def refresh(self, db, user_id: str) -> None:
        """
        Reload all provider configurations from `ai_providers` collection and
        reinitialise connectors. Existing in-flight requests are not interrupted.
        """
```

### 4.2 Canonical Resolution Pattern

```python
# In a service (app/services/):
connector = registry.get(provider_id)          # only valid resolution pattern
result = await connector.execute("generate_image", params)
```

Never:

```python
# FORBIDDEN in routes or services:
if provider_id == "openai":
    result = openai_client.images.generate(...)
elif provider_id == "stability":
    result = stability_sdk.generate(...)
```

### 4.3 Registry Lifecycle

```
Application startup
  └─► MCPRegistry.__init__()
        └─► loads ai_providers from MongoDB
              └─► instantiates one MCPConnector per enabled provider
                    └─► calls connector.connect() for each

Admin saves provider settings (UI)
  └─► POST /api/v1/ai-providers/:id  (route)
        └─► ai_generation_service.refresh_providers(db, user_id)
              └─► registry.refresh(db, user_id)

Request arrives
  └─► route handler (app/api/v1/)
        └─► ai_generation_service.generate(provider_id, params, db, correlation_id)
              └─► registry.get(provider_id)
                    └─► connector.execute("generate_image", params)
```

---

## 5. Add / Remove Runbook

### 5.1 Adding a New Connector

Follow these steps in order. **Zero route or frontend code changes are required.**

1. **Implement the interface**

   Create `app/services/connectors/<provider_id>_connector.py`.
   The class MUST implement all five methods of `MCPConnector` (Section 2).

   ```python
   # app/services/connectors/acme_connector.py
   from app.services.mcp_connector import MCPConnector, MCPConnectorError

   class AcmeConnector:
       def __init__(self, config: dict) -> None:
           self._config = config
           self._session = None

       async def connect(self) -> None: ...
       async def disconnect(self) -> None: ...
       async def validate(self) -> bool: ...
       async def execute(self, action: str, params: dict) -> dict: ...
       async def health_check(self) -> bool: ...
   ```

2. **Register in the registry**

   Add the provider class to `CONNECTOR_REGISTRY` in
   `app/services/connectors/__init__.py`:

   ```python
   from .acme_connector import AcmeConnector

   CONNECTOR_REGISTRY: dict[str, type] = {
       "openai":    OpenAIConnector,
       "stability": StabilityConnector,
       "acme":      AcmeConnector,     # ← add here
   }
   ```

3. **Add the DB configuration record**

   Insert a document into the `ai_providers` MongoDB collection (via the admin
   UI or a migration script):

   ```json
   {
     "id":            "acme",
     "name":          "Acme AI",
     "enabled":       true,
     "apiKey":        "<set by admin>",
     "baseUrl":       "https://api.acme.example/v1",
     "selectedModel": "acme-image-v1",
     "capabilities":  ["image_generation"],
     "user_id":       "1"
   }
   ```

4. **Write unit tests**

   Add `tests/unit/connectors/test_acme_connector.py`.
   Cover: `validate()` returns False when API key is absent; `execute()` raises
   `MCPConnectorError` on provider 5xx; `health_check()` does not raise.

5. **Verify**

   ```bash
   pytest tests/unit/connectors/test_acme_connector.py
   ruff check app/services/connectors/acme_connector.py
   ```

### 5.2 Removing a Connector

1. **Mark disabled in DB**

   ```json
   { "id": "acme", "enabled": false }
   ```

   The registry will exclude disabled providers on the next `refresh()`.
   In-flight requests complete normally.

2. **Unregister from the registry**

   Remove the entry from `CONNECTOR_REGISTRY` in
   `app/services/connectors/__init__.py`.

3. **Delete the connector file**

   Remove `app/services/connectors/<provider_id>_connector.py`.

4. **Remove tests**

   Delete `tests/unit/connectors/test_<provider_id>_connector.py`.

5. **Verify remaining providers are unaffected**

   ```bash
   pytest
   ruff check .
   ```

**Contract guarantee**: all other providers continue to work without modification.
The API surface (`/api/v1/ai-generation/`) is unchanged.

---

## 6. Correlation ID Propagation

A `correlation_id` (UUID) MUST be created at the route boundary on every request
and threaded through all layers:

```python
# In the route handler:
import uuid
correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())

# Passed to the service:
result = await ai_generation_service.generate(
    provider_id=provider_id,
    params=params,
    db=request.app.mongodb,
    correlation_id=correlation_id,
)

# Returned in the response header:
response.headers["X-Correlation-ID"] = correlation_id
```

Services pass `correlation_id` to `MCPConnectorError` when re-raising; they
MUST NOT generate a new UUID. The same ID appears in logs and the error response,
enabling end-to-end tracing from frontend to provider call.

---

## 7. Compliance Checklist

Use this checklist before merging any change that touches connectors, routes, or
services:

- [ ] Connector class implements all five `MCPConnector` methods.
- [ ] `execute()` raises `MCPConnectorError` (never returns an error dict).
- [ ] `health_check()` and `validate()` do not raise.
- [ ] `error_details` contains all six required fields (Section 3.2).
- [ ] `user_message` is an i18n key, not a raw string.
- [ ] `correlation_id` originates at the route boundary and is not regenerated.
- [ ] No `if provider == "<name>"` branching in routes or services.
- [ ] New connector registered in `CONNECTOR_REGISTRY`.
- [ ] DB configuration record present in `ai_providers` collection.
- [ ] Unit tests added; `pytest` green; `ruff check .` clean.

---

## 8. Changelog

| Date | Change |
|------|--------|
| 2026-02-23 | Initial contract created for ARCH-T001 (branch 003-architecture-core-and-compliance). Defines MCPConnector Protocol (5 methods), error_details schema (6 fields, 11 canonical error_type values), MCPRegistry interface, add/remove runbook, and correlation_id propagation rules. |
