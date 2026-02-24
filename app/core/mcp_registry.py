"""
MCP Registry — central registry mapping provider_id → connector.

Contract reference: docs/mcp-connector-contract.md §4
Spec reference:     spec/process/architecture-guidelines.speckit.md ARCH-MCP-002

Design notes
------------
The factory callable (``manager_factory``) is injected at construction time
rather than imported directly.  This keeps the registry itself free of any
hard dependency on ``get_provider_manager``, and—critically—allows unit tests
to patch the name inside ``app.services.ai_generation_service`` without also
having to patch this module.  The service passes whichever callable it has in
scope, so the mock flows through unchanged.

During the current transition period the registry wraps ``AIProviderManager``
(the legacy runtime) via ``get_underlying_manager()``.  Once all providers
implement the full ``MCPConnector`` protocol, services will call
``registry.get(provider_id).execute(action, params)`` directly.
"""
from __future__ import annotations

import logging
from typing import Any, Callable

from app.services.mcp_connector import MCPConnectorError

logger = logging.getLogger(__name__)


class MCPRegistry:
    """
    Central registry that maps provider_id → MCPConnector instance.

    Populated on ``refresh()`` from the ``ai_providers`` MongoDB collection
    (via the injected manager factory).  Refreshed on-demand by calling
    ``refresh()`` after an admin saves new provider settings.

    Usage in services (canonical pattern — contract §4.2)::

        registry = MCPRegistry(get_provider_manager)
        await registry.refresh(db)
        connector = registry.get(provider_id)   # raises MCPConnectorError if absent
    """

    def __init__(self, manager_factory: Callable) -> None:
        """
        Args:
            manager_factory: callable(*, database_client) → AIProviderManager.
                Typically ``get_provider_manager`` imported in the *calling* module
                so that test patches on that module's name are respected here.
        """
        self._factory = manager_factory
        self._manager: Any = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def refresh(self, db: Any, user_id: str = "1") -> None:
        """
        Reload all provider configurations from ``ai_providers`` collection
        and reinitialise connectors.  Existing in-flight requests are not
        interrupted.

        Args:
            db:      MongoDB database client.
            user_id: Tenant identifier used to scope the ``ai_providers`` query.
        """
        self._manager = self._factory(database_client=db)
        await self._manager.refresh_provider_configs(user_id)
        logger.debug(
            "MCPRegistry refreshed: %d provider(s) available",
            len(self._manager.providers),
        )

    # ------------------------------------------------------------------
    # Resolution  (contract §4.1)
    # ------------------------------------------------------------------

    def get(self, provider_id: str):
        """
        Return the live connector for *provider_id*.

        Raises:
            MCPConnectorError(error_type="provider_not_found", http_status=400)
                if ``provider_id`` is not registered.
            MCPConnectorError(error_type="provider_not_configured", http_status=503)
                if ``provider_id`` is registered but ``is_available()`` is False.

        Note: the returned object is a legacy ``BaseProvider`` during the
        current transition.  Once providers implement the full ``MCPConnector``
        protocol, callers will be able to use ``connector.execute(action, params)``.
        """
        if self._manager is None:
            raise MCPConnectorError(
                error_type="provider_not_found",
                user_message="errors.ai.provider_not_found",
                provider=provider_id,
                http_status=400,
            )

        if provider_id not in self._manager.providers:
            raise MCPConnectorError(
                error_type="provider_not_found",
                user_message="errors.ai.provider_not_found",
                provider=provider_id,
                http_status=400,
            )

        provider = self._manager.providers[provider_id]
        if not provider.is_available():
            raise MCPConnectorError(
                error_type="provider_not_configured",
                user_message="errors.ai.provider_not_configured",
                provider=provider_id,
                http_status=503,
            )

        return provider

    def list_available(self) -> list[str]:
        """
        Return ``provider_id``s of all connectors currently passing
        ``is_available()``.

        Analogous to the contract's ``list_available()`` which checks
        ``health_check()``; mapped to ``is_available()`` on legacy providers.
        """
        if self._manager is None:
            return []
        return [
            pid
            for pid, provider in self._manager.providers.items()
            if provider.is_available()
        ]

    # ------------------------------------------------------------------
    # Transition helper
    # ------------------------------------------------------------------

    def get_underlying_manager(self) -> Any:
        """
        Return the wrapped ``AIProviderManager``.

        Used by the service layer for operations (``generate_image``,
        ``get_provider_status``, etc.) that are delegated to the manager
        until all providers implement ``MCPConnector.execute()``.
        """
        return self._manager
