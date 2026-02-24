"""
AI Generation Service — all business logic for AI image generation.

Layer contract (ARCH-LAYER-001):
  Route → ai_generation_service (this file) → AIProviderManager → providers

Registry resolution (ARCH-MCP-002):
  All provider resolution is delegated to AIProviderManager.  Services and
  routes MUST NOT branch on provider_id (e.g. if provider == "openai").

Error schema (ARCH-MCP-005):
  Every error path returns a compliant error_details dict:
    { error_type, user_message (i18n key), provider, http_status,
      correlation_id, details }
  Raw provider exceptions and stack traces are never surfaced to HTTP responses.

Correlation IDs (ARCH-MCP-005 / PR-BE-005):
  The route generates the correlation_id at request entry and passes it in.
  The service propagates it in every success and error response so end-to-end
  tracing is always possible.
"""
import uuid
import logging
from typing import Any, Dict, List, Optional

from app.ai_providers.provider_manager import (
    ImageGenerationRequest,
    get_provider_manager,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _error_details(
    error_type: str,
    user_message: str,
    provider: str,
    http_status: int,
    correlation_id: str,
    details: Optional[dict] = None,
) -> Dict[str, Any]:
    """Build a compliant ARCH-MCP-005 error_details dict."""
    return {
        "error_type": error_type,
        "user_message": user_message,
        "provider": provider,
        "http_status": http_status,
        "correlation_id": correlation_id,
        "details": details or {},
    }


def _normalise_error_details(
    raw: Optional[Dict[str, Any]],
    provider: str,
    fallback_cid: str,
) -> Dict[str, Any]:
    """
    Ensure a result's error_details conform to ARCH-MCP-005.

    AIProviderManager already populates error_details on most failure paths,
    but some older code paths omit fields.  This function fills any gaps so
    the service always returns a consistent shape.
    """
    if not raw:
        raw = {}
    return {
        "error_type": raw.get("error_type", "generation_failed"),
        "user_message": raw.get("user_message", "errors.ai.generation_failed"),
        "provider": raw.get("provider", provider),
        "http_status": raw.get("http_status", 500),
        "correlation_id": raw.get("correlation_id", fallback_cid),
        "details": {
            k: v for k, v in raw.items()
            if k not in {"error_type", "user_message", "provider",
                         "http_status", "correlation_id"}
        },
    }


async def _refreshed_manager(db: Any):
    """
    Return the AIProviderManager singleton with up-to-date DB config.

    The manager is the MCP registry: provider_id → connector implementation.
    Calling refresh_provider_configs() here ensures routes never need to
    know about this lifecycle step (GEN-V002 fix).
    """
    manager = get_provider_manager(database_client=db)
    await manager.refresh_provider_configs()
    return manager


# ---------------------------------------------------------------------------
# Public service API
# ---------------------------------------------------------------------------

async def generate_image(
    db: Any,
    provider_id: str,
    prompt: str,
    size: str = "1024x1024",
    style: str = "photorealistic",
    quality: str = "standard",
    variations: int = 1,
    negative_prompt: Optional[str] = None,
    seed: Optional[int] = None,
    people_preference: str = "auto",
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate one or more images via the MCP registry.

    ARCH-MCP-002 — Registry resolution:
      Provider lookup is fully delegated to AIProviderManager; this service
      never branches on provider_id.

    ARCH-MCP-005 — Error schema:
      All failure paths return { success: False, error_details: {...} }.

    Parallel vs. single decision (GEN-V003):
      Centralised here — route only passes `variations`.
    """
    cid = correlation_id or str(uuid.uuid4())
    logger.info(
        "generate_image: provider=%s variations=%d correlation_id=%s",
        provider_id, variations, cid,
    )

    try:
        manager = await _refreshed_manager(db)

        gen_request = ImageGenerationRequest(
            prompt=prompt,
            size=size,
            style=style,
            quality=quality,
            variations=variations,
            negative_prompt=negative_prompt,
            seed=seed,
            people_preference=people_preference,
        )

        if variations > 1:
            logger.debug(
                "Using parallel generation for %d variations (correlation_id=%s)",
                variations, cid,
            )
            result = await manager.generate_images_parallel(provider_id, gen_request)
        else:
            result = await manager.generate_image(provider_id, gen_request)

    except Exception as exc:
        logger.error(
            "Unexpected error in generate_image (correlation_id=%s): %s",
            cid, exc, exc_info=True,
        )
        return {
            "success": False,
            "error_details": _error_details(
                error_type="internal_error",
                user_message="errors.ai.internal_error",
                provider=provider_id,
                http_status=500,
                correlation_id=cid,
                details={"exception": str(exc)},
            ),
        }

    if result.success:
        logger.info(
            "generate_image success: %d image(s), provider=%s correlation_id=%s",
            len(result.images), result.provider, cid,
        )
        return {
            "success": True,
            "images": result.images,
            "prompt": prompt,
            "provider": result.provider,
            "model": result.model,
            "metadata": result.metadata,
            "cost": result.cost,
            "correlation_id": cid,
        }

    error_details = _normalise_error_details(result.error_details, provider_id, cid)
    logger.warning(
        "generate_image failed: provider=%s error_type=%s correlation_id=%s",
        result.provider,
        error_details["error_type"],
        error_details["correlation_id"],
    )
    return {
        "success": False,
        "error_details": error_details,
    }


async def get_available_providers(db: Any) -> Dict[str, Any]:
    """
    Return capability and status of every registered provider.

    ARCH-MCP-002: provider list comes from the AIProviderManager registry;
    no static lists or provider branching.
    """
    try:
        manager = await _refreshed_manager(db)
        provider_status = manager.get_provider_status()
        return {
            "providers": [
                {
                    "id": pid,
                    "name": info["name"],
                    "configured": info["configured"],
                    "available": info["available"],
                    "model": info["model"],
                    "max_variations": info["max_variations"],
                    "supported_sizes": info["supported_sizes"],
                    "features": info["features"],
                    "pricing": info["pricing"],
                    "status": info["status"],
                }
                for pid, info in provider_status.items()
            ]
        }
    except Exception as exc:
        cid = str(uuid.uuid4())
        logger.error(
            "get_available_providers failed (correlation_id=%s): %s",
            cid, exc, exc_info=True,
        )
        return {
            "success": False,
            "error_details": _error_details(
                error_type="registry_error",
                user_message="errors.ai.registry_unavailable",
                provider="registry",
                http_status=503,
                correlation_id=cid,
                details={"exception": str(exc)},
            ),
        }


async def get_recommended_provider(
    db: Any,
    features: Optional[List[str]] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Return the recommended provider for the given feature requirements.

    ARCH-MCP-002: resolution via registry only.
    """
    cid = correlation_id or str(uuid.uuid4())
    try:
        manager = await _refreshed_manager(db)
        recommended = manager.get_recommended_provider(features)
        provider_status = manager.get_provider_status()
        if recommended in provider_status:
            return {
                "provider_id": recommended,
                "name": provider_status[recommended]["name"],
                "reason": "best_available_provider",
                "status": provider_status[recommended],
                "correlation_id": cid,
            }
        return {
            "provider_id": "free-test-provider",
            "name": "Test Provider",
            "reason": "fallback_provider",
            "status": {},
            "correlation_id": cid,
        }
    except Exception as exc:
        logger.error(
            "get_recommended_provider failed (correlation_id=%s): %s",
            cid, exc, exc_info=True,
        )
        return {
            "success": False,
            "error_details": _error_details(
                error_type="registry_error",
                user_message="errors.ai.registry_unavailable",
                provider="registry",
                http_status=503,
                correlation_id=cid,
                details={"exception": str(exc)},
            ),
        }


async def refresh_configs(db: Any) -> Dict[str, Any]:
    """
    Explicitly refresh all provider configurations from the database.

    Called after a user updates provider settings (e.g. saves a new API key)
    to ensure the in-memory registry reflects the latest DB state without
    restarting the process.
    """
    try:
        manager = get_provider_manager(database_client=db)
        await manager.refresh_provider_configs()
        configured = sum(
            1 for p in manager.providers.values() if p.is_configured()
        )
        return {
            "success": True,
            "total_providers": len(manager.providers),
            "configured_providers": configured,
        }
    except Exception as exc:
        cid = str(uuid.uuid4())
        logger.error(
            "refresh_configs failed (correlation_id=%s): %s",
            cid, exc, exc_info=True,
        )
        return {
            "success": False,
            "error_details": _error_details(
                error_type="registry_error",
                user_message="errors.ai.registry_refresh_failed",
                provider="registry",
                http_status=503,
                correlation_id=cid,
                details={"exception": str(exc)},
            ),
        }
