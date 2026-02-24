"""
MCP Connector contract — Protocol and error types.

Contract reference: docs/mcp-connector-contract.md §2–3
Spec reference:     spec/process/architecture-guidelines.speckit.md ARCH-MCP-001
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class MCPConnector(Protocol):
    """
    Contract for every external connection in the AI Marketing Agent.

    Implementors: one class per provider (e.g. OpenAIConnector, StabilityConnector).
    Registration: each implementor is registered in MCPRegistry at application startup.
    Configuration: all credentials and settings come from the `ai_providers` MongoDB
                   collection (ARCH-MCP-003). Never hardcode API keys or base URLs.

    Contract invariants (docs/mcp-connector-contract.md §2.2):
      I-1  health_check() and validate() MUST NOT raise; they return bool.
      I-2  execute() MUST raise MCPConnectorError on any failure.
      I-3  disconnect() MUST be idempotent.
      I-4  Connector instances MUST be stateless w.r.t. request data.
      I-5  All configuration is read from MongoDB at connect() time.
    """

    async def connect(self) -> None:
        """Establish and validate the connection to the external service."""

    async def disconnect(self) -> None:
        """Tear down the connection cleanly. MUST be idempotent."""

    async def validate(self) -> bool:
        """
        Validate credentials and configuration.

        Returns True if properly configured and credentials are valid.
        MUST NOT raise.
        """

    async def execute(self, action: str, params: dict) -> dict:
        """
        Execute a domain action against the external service.

        Raises:
            MCPConnectorError: wraps all provider SDK exceptions.
        """

    async def health_check(self) -> bool:
        """
        Return True if the connector is available and responsive.

        MUST NOT raise.
        """


@dataclass
class MCPConnectorError(Exception):
    """
    Raised by MCPConnector.execute() on any failure.

    The `error_details` property is the canonical representation used in HTTP
    responses (docs/mcp-connector-contract.md §3).
    """

    error_type: str          # snake_case key — see canonical values in contract §3.3
    user_message: str        # i18n key, e.g. "errors.provider.unavailable"
    provider: str            # provider_id from ai_providers collection
    http_status: int         # intended HTTP status code for the response
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    details: dict = field(default_factory=dict)

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
