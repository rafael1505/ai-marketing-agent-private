"""
Unit tests for app/services/ai_generation_service.py

Coverage:
  - generate_image: success (single), success (parallel), provider failure,
    unexpected exception, error_details normalisation
  - get_available_providers: success, exception path
  - get_recommended_provider: known provider, fallback provider, exception path
  - refresh_configs: success, exception path
  - _normalise_error_details: complete and partial error_details
  - _error_details: field contract

Mocking strategy (BFIX-001):
  - `app.services.ai_generation_service.get_provider_manager` is patched to
    return a fake manager — no real DB or HTTP calls are made.
  - ImageGenerationResult is constructed directly from the dataclass.
"""
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.ai_providers.provider_manager import ImageGenerationResult
import app.services.ai_generation_service as svc

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

FAKE_DB = object()
FAKE_CID = "aaaaaaaa-0000-0000-0000-000000000000"

SUCCESS_RESULT = ImageGenerationResult(
    success=True,
    images=["https://example.com/img1.png"],
    provider="openai",
    model="dall-e-3",
    metadata={"size": "1024x1024", "total_images": 1},
    cost=0.04,
)

PARALLEL_RESULT = ImageGenerationResult(
    success=True,
    images=["https://example.com/img1.png", "https://example.com/img2.png"],
    provider="openai",
    model="dall-e-3",
    metadata={"total_requested": 2, "total_generated": 2, "parallel_execution": True},
    cost=0.08,
)

FAILURE_RESULT = ImageGenerationResult(
    success=False,
    images=[],
    provider="openai",
    model="dall-e-3",
    metadata={},
    error="quota exceeded",
    error_details={
        "error_type": "quota_exceeded",
        "user_message": "errors.ai.quota_exceeded",
        "provider": "openai",
        "http_status": 429,
        "correlation_id": FAKE_CID,
    },
)

FAILURE_NO_DETAILS = ImageGenerationResult(
    success=False,
    images=[],
    provider="stability",
    model="sdxl",
    metadata={},
    error="something broke",
    error_details=None,
)


def _make_manager(
    generate_result=SUCCESS_RESULT,
    parallel_result=PARALLEL_RESULT,
    provider_status=None,
    recommended="openai",
):
    """Return a mock AIProviderManager with sensible defaults."""
    m = MagicMock()
    m.refresh_provider_configs = AsyncMock()
    m.generate_image = AsyncMock(return_value=generate_result)
    m.generate_images_parallel = AsyncMock(return_value=parallel_result)
    m.get_provider_status = MagicMock(
        return_value=provider_status
        or {
            "openai": {
                "name": "OpenAI DALL-E",
                "configured": True,
                "available": True,
                "model": "dall-e-3",
                "max_variations": 4,
                "supported_sizes": ["1024x1024"],
                "features": ["image_generation"],
                "pricing": {"standard": 0.04},
                "status": "configured",
            }
        }
    )
    m.get_recommended_provider = MagicMock(return_value=recommended)
    m.providers = {"openai": MagicMock(is_configured=MagicMock(return_value=True))}
    return m


def _patch_manager(manager):
    """Context-manager helper that patches get_provider_manager."""
    return patch(
        "app.services.ai_generation_service.get_provider_manager",
        return_value=manager,
    )


# ---------------------------------------------------------------------------
# _error_details helper
# ---------------------------------------------------------------------------

class TestErrorDetails:
    def test_all_fields_present(self):
        ed = svc._error_details(
            error_type="invalid_api_key",
            user_message="errors.ai.invalid_api_key",
            provider="openai",
            http_status=401,
            correlation_id=FAKE_CID,
            details={"hint": "check settings"},
        )
        assert ed["error_type"] == "invalid_api_key"
        assert ed["user_message"] == "errors.ai.invalid_api_key"
        assert ed["provider"] == "openai"
        assert ed["http_status"] == 401
        assert ed["correlation_id"] == FAKE_CID
        assert ed["details"] == {"hint": "check settings"}

    def test_details_defaults_to_empty_dict(self):
        ed = svc._error_details("t", "u", "p", 500, FAKE_CID)
        assert ed["details"] == {}


# ---------------------------------------------------------------------------
# _normalise_error_details helper
# ---------------------------------------------------------------------------

class TestNormaliseErrorDetails:
    def test_passes_through_complete_details(self):
        raw = {
            "error_type": "rate_limit_exceeded",
            "user_message": "errors.ai.rate_limit_exceeded",
            "provider": "openai",
            "http_status": 429,
            "correlation_id": FAKE_CID,
            "retry_after": 60,
        }
        result = svc._normalise_error_details(raw, "openai", "fallback-cid")
        assert result["error_type"] == "rate_limit_exceeded"
        assert result["correlation_id"] == FAKE_CID
        assert result["details"]["retry_after"] == 60

    def test_fills_missing_fields(self):
        result = svc._normalise_error_details(None, "stability", "fallback-cid")
        assert result["error_type"] == "generation_failed"
        assert result["user_message"] == "errors.ai.generation_failed"
        assert result["provider"] == "stability"
        assert result["http_status"] == 500
        assert result["correlation_id"] == "fallback-cid"

    def test_uses_fallback_cid_when_absent(self):
        raw = {"error_type": "timeout", "user_message": "errors.ai.timeout"}
        result = svc._normalise_error_details(raw, "replicate", "my-cid")
        assert result["correlation_id"] == "my-cid"


# ---------------------------------------------------------------------------
# generate_image
# ---------------------------------------------------------------------------

class TestGenerateImage:
    @pytest.mark.asyncio
    async def test_single_image_success(self):
        manager = _make_manager(generate_result=SUCCESS_RESULT)
        with _patch_manager(manager):
            result = await svc.generate_image(
                FAKE_DB, "openai", "a red sunset", correlation_id=FAKE_CID
            )

        assert result["success"] is True
        assert result["images"] == ["https://example.com/img1.png"]
        assert result["provider"] == "openai"
        assert result["correlation_id"] == FAKE_CID
        manager.generate_image.assert_awaited_once()
        manager.generate_images_parallel.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_parallel_generation_used_for_multiple_variations(self):
        manager = _make_manager(parallel_result=PARALLEL_RESULT)
        with _patch_manager(manager):
            result = await svc.generate_image(
                FAKE_DB, "openai", "mountains", variations=2, correlation_id=FAKE_CID
            )

        assert result["success"] is True
        assert len(result["images"]) == 2
        manager.generate_images_parallel.assert_awaited_once()
        manager.generate_image.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_single_path_for_variations_eq_1(self):
        manager = _make_manager()
        with _patch_manager(manager):
            await svc.generate_image(FAKE_DB, "openai", "test", variations=1)
        manager.generate_image.assert_awaited_once()
        manager.generate_images_parallel.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_provider_failure_returns_error_details(self):
        manager = _make_manager(generate_result=FAILURE_RESULT)
        with _patch_manager(manager):
            result = await svc.generate_image(
                FAKE_DB, "openai", "test", correlation_id=FAKE_CID
            )

        assert result["success"] is False
        ed = result["error_details"]
        assert ed["error_type"] == "quota_exceeded"
        assert ed["user_message"] == "errors.ai.quota_exceeded"
        assert ed["http_status"] == 429
        assert "correlation_id" in ed

    @pytest.mark.asyncio
    async def test_null_error_details_are_normalised(self):
        manager = _make_manager(generate_result=FAILURE_NO_DETAILS)
        with _patch_manager(manager):
            result = await svc.generate_image(FAKE_DB, "stability", "test")

        assert result["success"] is False
        ed = result["error_details"]
        assert ed["error_type"] == "generation_failed"
        assert ed["user_message"] == "errors.ai.generation_failed"
        assert ed["http_status"] == 500
        assert isinstance(ed["correlation_id"], str)

    @pytest.mark.asyncio
    async def test_unexpected_exception_returns_internal_error(self):
        manager = _make_manager()
        manager.generate_image = AsyncMock(side_effect=RuntimeError("boom"))
        with _patch_manager(manager):
            result = await svc.generate_image(
                FAKE_DB, "openai", "test", correlation_id=FAKE_CID
            )

        assert result["success"] is False
        ed = result["error_details"]
        assert ed["error_type"] == "internal_error"
        assert ed["user_message"] == "errors.ai.internal_error"
        assert ed["http_status"] == 500
        assert ed["correlation_id"] == FAKE_CID
        assert "boom" in ed["details"]["exception"]

    @pytest.mark.asyncio
    async def test_correlation_id_is_generated_when_absent(self):
        manager = _make_manager()
        with _patch_manager(manager):
            result = await svc.generate_image(FAKE_DB, "openai", "test")

        assert "correlation_id" in result
        assert len(result["correlation_id"]) == 36  # UUID4 format

    @pytest.mark.asyncio
    async def test_refresh_is_always_called(self):
        manager = _make_manager()
        with _patch_manager(manager):
            await svc.generate_image(FAKE_DB, "openai", "test")
        manager.refresh_provider_configs.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_response_contains_cost_and_model(self):
        manager = _make_manager()
        with _patch_manager(manager):
            result = await svc.generate_image(FAKE_DB, "openai", "test")
        assert result["cost"] == 0.04
        assert result["model"] == "dall-e-3"


# ---------------------------------------------------------------------------
# get_available_providers
# ---------------------------------------------------------------------------

class TestGetAvailableProviders:
    @pytest.mark.asyncio
    async def test_returns_provider_list(self):
        manager = _make_manager()
        with _patch_manager(manager):
            result = await svc.get_available_providers(FAKE_DB)

        assert "providers" in result
        assert len(result["providers"]) == 1
        p = result["providers"][0]
        assert p["id"] == "openai"
        assert p["name"] == "OpenAI DALL-E"
        assert p["available"] is True

    @pytest.mark.asyncio
    async def test_all_provider_fields_present(self):
        manager = _make_manager()
        with _patch_manager(manager):
            result = await svc.get_available_providers(FAKE_DB)

        p = result["providers"][0]
        for field in ("id", "name", "configured", "available", "model",
                      "max_variations", "supported_sizes", "features",
                      "pricing", "status"):
            assert field in p, f"missing field: {field}"

    @pytest.mark.asyncio
    async def test_exception_returns_error_details(self):
        manager = _make_manager()
        manager.get_provider_status = MagicMock(side_effect=Exception("db down"))
        with _patch_manager(manager):
            result = await svc.get_available_providers(FAKE_DB)

        assert result["success"] is False
        ed = result["error_details"]
        assert ed["error_type"] == "registry_error"
        assert ed["user_message"] == "errors.ai.registry_unavailable"
        assert ed["http_status"] == 503

    @pytest.mark.asyncio
    async def test_refresh_is_always_called(self):
        manager = _make_manager()
        with _patch_manager(manager):
            await svc.get_available_providers(FAKE_DB)
        manager.refresh_provider_configs.assert_awaited_once()


# ---------------------------------------------------------------------------
# get_recommended_provider
# ---------------------------------------------------------------------------

class TestGetRecommendedProvider:
    @pytest.mark.asyncio
    async def test_returns_known_provider(self):
        manager = _make_manager(recommended="openai")
        with _patch_manager(manager):
            result = await svc.get_recommended_provider(
                FAKE_DB, correlation_id=FAKE_CID
            )

        assert result["provider_id"] == "openai"
        assert result["name"] == "OpenAI DALL-E"
        assert result["reason"] == "best_available_provider"
        assert result["correlation_id"] == FAKE_CID

    @pytest.mark.asyncio
    async def test_falls_back_to_test_provider_when_unknown(self):
        manager = _make_manager(recommended="unknown-provider")
        with _patch_manager(manager):
            result = await svc.get_recommended_provider(FAKE_DB)

        assert result["provider_id"] == "free-test-provider"
        assert result["reason"] == "fallback_provider"

    @pytest.mark.asyncio
    async def test_exception_returns_error_details(self):
        manager = _make_manager()
        manager.get_recommended_provider = MagicMock(side_effect=Exception("oops"))
        with _patch_manager(manager):
            result = await svc.get_recommended_provider(
                FAKE_DB, correlation_id=FAKE_CID
            )

        assert result["success"] is False
        ed = result["error_details"]
        assert ed["error_type"] == "registry_error"
        assert ed["correlation_id"] == FAKE_CID

    @pytest.mark.asyncio
    async def test_correlation_id_auto_generated(self):
        manager = _make_manager()
        with _patch_manager(manager):
            result = await svc.get_recommended_provider(FAKE_DB)
        assert "correlation_id" in result


# ---------------------------------------------------------------------------
# refresh_configs
# ---------------------------------------------------------------------------

class TestRefreshConfigs:
    @pytest.mark.asyncio
    async def test_returns_provider_counts(self):
        manager = _make_manager()
        with _patch_manager(manager):
            result = await svc.refresh_configs(FAKE_DB)

        assert result["success"] is True
        assert "total_providers" in result
        assert "configured_providers" in result

    @pytest.mark.asyncio
    async def test_exception_returns_error_details(self):
        manager = _make_manager()
        manager.refresh_provider_configs = AsyncMock(side_effect=Exception("timeout"))
        with _patch_manager(manager):
            result = await svc.refresh_configs(FAKE_DB)

        assert result["success"] is False
        ed = result["error_details"]
        assert ed["error_type"] == "registry_error"
        assert ed["user_message"] == "errors.ai.registry_refresh_failed"
        assert ed["http_status"] == 503
        assert "timeout" in ed["details"]["exception"]
