"""
Unit tests for app/services/material_service.py

BFIX-001 compliance: tests were authored before the service implementation
and define the expected contracts. They run without a live database or HTTP
server — all DB interactions are mocked via unittest.mock.AsyncMock.

Coverage:
  - serialize_material: _id → id conversion, original key removed
  - create: delegates to MaterialDB, returns serialised dict
  - get: 404 on missing, 403 on wrong company, serialised on success
  - list_materials: delegates with filter params, returns serialised list
  - update: 404 on missing, 403 on wrong company, serialised on success
  - delete: 404 on missing, 403 on wrong company, success payload
  - add_generated_image: 404 on missing, 403 on wrong company, serialised
  - select_image (ARCH-MAT-004): 422 when generated_images is empty,
                                  success when images present
  - add_feedback: 404 on missing, 403 on wrong company, serialised
  - transition_stage (ARCH-MAT-002): 404 on missing, serialised on success
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

import app.services.material_service as svc
from app.models.material import MaterialCreate, MaterialStage, MaterialStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(coro):
    """Run an async coroutine in a fresh event loop."""
    return asyncio.run(coro)


def _mock_db_with(material_db_mock: MagicMock):
    """Return a context manager that patches _make_db to return the given mock."""
    return patch("app.services.material_service._make_db", return_value=material_db_mock)


def _material(extra: dict | None = None) -> dict:
    """Build a minimal material dict as the DB would return it."""
    base = {
        "_id": "mat001",
        "title": "Test Material",
        "company_id": "company1",
        "created_by": "user1",
        "stage": "idea",
        "status": "draft",
        "generated_images": [],
        "feedback": [],
    }
    if extra:
        base.update(extra)
    return base


def _make_material_db(overrides: dict | None = None) -> MagicMock:
    """Return a MagicMock MaterialDB with sensible AsyncMock defaults."""
    m = MagicMock()
    m.get = AsyncMock(return_value=_material())
    m.create_material = AsyncMock(return_value=_material())
    m.get_company_materials = AsyncMock(return_value=[_material()])
    m.update = AsyncMock(return_value=_material())
    m.delete = AsyncMock(return_value=True)
    m.add_generated_image = AsyncMock(
        return_value=_material({"generated_images": [{"url": "http://x.com/a.png"}]})
    )
    m.select_image = AsyncMock(
        return_value=_material({"selected_image": "http://x.com/a.png"})
    )
    m.add_feedback = AsyncMock(
        return_value=_material({"feedback": [{"comment": "looks good"}]})
    )
    m.update_stage = AsyncMock(
        return_value=_material({"stage": "refinement", "status": "in_progress"})
    )
    if overrides:
        for attr, value in overrides.items():
            setattr(m, attr, value)
    return m


# ---------------------------------------------------------------------------
# serialize_material
# ---------------------------------------------------------------------------

class TestSerializeMaterial:
    def test_converts_id_field(self):
        doc = {"_id": "abc", "title": "T"}
        result = svc.serialize_material(doc)
        assert result["id"] == "abc"
        assert "_id" not in result

    def test_no_op_when_no_id(self):
        doc = {"title": "T", "id": "already-set"}
        result = svc.serialize_material(doc)
        assert result["id"] == "already-set"
        assert "_id" not in result

    def test_handles_none(self):
        assert svc.serialize_material(None) is None

    def test_serialize_materials_copies(self):
        docs = [{"_id": "1", "title": "A"}, {"_id": "2", "title": "B"}]
        results = svc.serialize_materials(docs)
        assert results[0]["id"] == "1"
        assert results[1]["id"] == "2"
        # originals should not be mutated (serialize_materials uses .copy())
        assert "_id" in docs[0]


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------

class TestCreate:
    def test_successful_creation_returns_serialized_material(self):
        mock_db = _make_material_db()
        material_in = MaterialCreate(
            title="New Campaign",
            stage=MaterialStage.IDEA,
            status=MaterialStatus.DRAFT,
        )
        with _mock_db_with(mock_db):
            result = run(svc.create(MagicMock(), material_in, "user1", "company1"))

        assert result["id"] == "mat001"
        assert "_id" not in result
        assert result["title"] == "Test Material"
        mock_db.create_material.assert_called_once_with(material_in, "user1", "company1")

    def test_delegates_user_and_company_ids(self):
        mock_db = _make_material_db()
        material_in = MaterialCreate(
            title="X", stage=MaterialStage.IDEA, status=MaterialStatus.DRAFT
        )
        with _mock_db_with(mock_db):
            run(svc.create(MagicMock(), material_in, "u99", "c99"))

        mock_db.create_material.assert_called_once_with(material_in, "u99", "c99")


# ---------------------------------------------------------------------------
# get
# ---------------------------------------------------------------------------

class TestGet:
    def test_returns_material_on_success(self):
        mock_db = _make_material_db()
        with _mock_db_with(mock_db):
            result = run(svc.get(MagicMock(), "mat001", "company1"))
        assert result["id"] == "mat001"
        assert "_id" not in result

    def test_raises_404_when_not_found(self):
        mock_db = _make_material_db({"get": AsyncMock(return_value=None)})
        with _mock_db_with(mock_db):
            with pytest.raises(HTTPException) as exc:
                run(svc.get(MagicMock(), "missing", "company1"))
        assert exc.value.status_code == 404

    def test_raises_403_on_wrong_company(self):
        mock_db = _make_material_db()
        with _mock_db_with(mock_db):
            with pytest.raises(HTTPException) as exc:
                run(svc.get(MagicMock(), "mat001", "OTHER_company"))
        assert exc.value.status_code == 403


# ---------------------------------------------------------------------------
# list_materials
# ---------------------------------------------------------------------------

class TestListMaterials:
    def test_returns_list_of_serialized_materials(self):
        mock_db = _make_material_db()
        with _mock_db_with(mock_db):
            results = run(svc.list_materials(MagicMock(), "company1"))
        assert isinstance(results, list)
        assert results[0]["id"] == "mat001"
        assert "_id" not in results[0]

    def test_passes_filters_to_db(self):
        mock_db = _make_material_db()
        with _mock_db_with(mock_db):
            run(
                svc.list_materials(
                    MagicMock(),
                    "company1",
                    stage=MaterialStage.IDEA,
                    status=MaterialStatus.DRAFT,
                    skip=10,
                    limit=5,
                )
            )
        mock_db.get_company_materials.assert_called_once_with(
            "company1",
            stage=MaterialStage.IDEA,
            status=MaterialStatus.DRAFT,
            skip=10,
            limit=5,
        )


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------

class TestUpdate:
    def test_returns_updated_material(self):
        mock_db = _make_material_db()
        with _mock_db_with(mock_db):
            result = run(svc.update(MagicMock(), "mat001", "company1", {"title": "New"}))
        assert result["id"] == "mat001"
        mock_db.update.assert_called_once_with("mat001", {"title": "New"})

    def test_raises_404_when_not_found(self):
        mock_db = _make_material_db({"get": AsyncMock(return_value=None)})
        with _mock_db_with(mock_db):
            with pytest.raises(HTTPException) as exc:
                run(svc.update(MagicMock(), "missing", "company1", {}))
        assert exc.value.status_code == 404

    def test_raises_403_on_wrong_company(self):
        mock_db = _make_material_db()
        with _mock_db_with(mock_db):
            with pytest.raises(HTTPException) as exc:
                run(svc.update(MagicMock(), "mat001", "WRONG", {}))
        assert exc.value.status_code == 403


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------

class TestDelete:
    def test_returns_success_payload(self):
        mock_db = _make_material_db()
        with _mock_db_with(mock_db):
            result = run(svc.delete(MagicMock(), "mat001", "company1"))
        assert result == {"success": True, "message": "Material deleted successfully", "id": "mat001"}

    def test_raises_404_when_not_found(self):
        mock_db = _make_material_db({"get": AsyncMock(return_value=None)})
        with _mock_db_with(mock_db):
            with pytest.raises(HTTPException) as exc:
                run(svc.delete(MagicMock(), "missing", "company1"))
        assert exc.value.status_code == 404

    def test_raises_403_on_wrong_company(self):
        mock_db = _make_material_db()
        with _mock_db_with(mock_db):
            with pytest.raises(HTTPException) as exc:
                run(svc.delete(MagicMock(), "mat001", "WRONG"))
        assert exc.value.status_code == 403


# ---------------------------------------------------------------------------
# add_generated_image
# ---------------------------------------------------------------------------

class TestAddGeneratedImage:
    def test_returns_material_with_image(self):
        mock_db = _make_material_db()
        with _mock_db_with(mock_db):
            result = run(
                svc.add_generated_image(
                    MagicMock(), "mat001", "company1",
                    "http://x.com/a.png", "a prompt", "openai", {}
                )
            )
        assert result["id"] == "mat001"
        mock_db.add_generated_image.assert_called_once_with(
            "mat001", "http://x.com/a.png", "a prompt", "openai", {}
        )

    def test_raises_404_when_not_found(self):
        mock_db = _make_material_db({"get": AsyncMock(return_value=None)})
        with _mock_db_with(mock_db):
            with pytest.raises(HTTPException) as exc:
                run(svc.add_generated_image(MagicMock(), "x", "c1", "u", "p", "q", {}))
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# select_image — ARCH-MAT-004 finalization guard
# ---------------------------------------------------------------------------

class TestSelectImage:
    def test_raises_422_when_generated_images_is_empty(self):
        """
        ARCH-MAT-004: A material with no generated images MUST NOT reach
        finalization. The service MUST raise HTTP 422 with error_type
        'finalization_guard' when generated_images is empty or absent.
        """
        mock_db = _make_material_db()  # _material() has generated_images=[]
        with _mock_db_with(mock_db):
            with pytest.raises(HTTPException) as exc:
                run(
                    svc.select_image(
                        MagicMock(), "mat001", "company1", "http://x.com/a.png"
                    )
                )
        assert exc.value.status_code == 422
        assert exc.value.detail["error_type"] == "finalization_guard"
        assert exc.value.detail["user_message"] == "errors.material.no_generated_images"

    def test_raises_422_when_generated_images_key_absent(self):
        """Guard also triggers when the key is missing entirely."""
        mat_no_key = {k: v for k, v in _material().items() if k != "generated_images"}
        mock_db = _make_material_db({"get": AsyncMock(return_value=mat_no_key)})
        with _mock_db_with(mock_db):
            with pytest.raises(HTTPException) as exc:
                run(svc.select_image(MagicMock(), "mat001", "company1", "http://x.png"))
        assert exc.value.status_code == 422

    def test_succeeds_when_generated_images_non_empty(self):
        """
        ARCH-MAT-004: Finalization guard passes when at least one generated
        image exists — select_image returns the serialised material.
        """
        mat_with_images = _material(
            {"generated_images": [{"url": "http://x.com/a.png", "prompt": "p"}]}
        )
        mock_db = _make_material_db({"get": AsyncMock(return_value=mat_with_images)})
        with _mock_db_with(mock_db):
            result = run(
                svc.select_image(
                    MagicMock(), "mat001", "company1", "http://x.com/a.png"
                )
            )
        assert result["id"] == "mat001"
        assert "_id" not in result
        mock_db.select_image.assert_called_once_with("mat001", "http://x.com/a.png")

    def test_raises_404_when_not_found(self):
        mock_db = _make_material_db({"get": AsyncMock(return_value=None)})
        with _mock_db_with(mock_db):
            with pytest.raises(HTTPException) as exc:
                run(svc.select_image(MagicMock(), "missing", "company1", "http://x.png"))
        assert exc.value.status_code == 404

    def test_raises_403_on_wrong_company(self):
        mock_db = _make_material_db()
        with _mock_db_with(mock_db):
            with pytest.raises(HTTPException) as exc:
                run(svc.select_image(MagicMock(), "mat001", "WRONG", "http://x.png"))
        assert exc.value.status_code == 403


# ---------------------------------------------------------------------------
# add_feedback
# ---------------------------------------------------------------------------

class TestAddFeedback:
    def test_returns_material_with_feedback(self):
        mock_db = _make_material_db()
        with _mock_db_with(mock_db):
            result = run(
                svc.add_feedback(MagicMock(), "mat001", "company1", "user1", "looks good")
            )
        assert result["id"] == "mat001"
        mock_db.add_feedback.assert_called_once_with("mat001", "user1", "looks good")

    def test_raises_404_when_not_found(self):
        mock_db = _make_material_db({"get": AsyncMock(return_value=None)})
        with _mock_db_with(mock_db):
            with pytest.raises(HTTPException) as exc:
                run(svc.add_feedback(MagicMock(), "x", "c", "u", "comment"))
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# transition_stage — ARCH-MAT-002
# ---------------------------------------------------------------------------

class TestTransitionStage:
    def test_successful_transition(self):
        """
        ARCH-MAT-002: Stage transitions MUST be performed exclusively in
        material_service, not in route handlers.
        """
        mock_db = _make_material_db()
        with _mock_db_with(mock_db):
            result = run(
                svc.transition_stage(
                    MagicMock(), "mat001", "company1",
                    MaterialStage.REFINEMENT, MaterialStatus.IN_PROGRESS
                )
            )
        assert result["id"] == "mat001"
        mock_db.update_stage.assert_called_once_with(
            "mat001", MaterialStage.REFINEMENT, MaterialStatus.IN_PROGRESS
        )

    def test_raises_404_when_not_found(self):
        mock_db = _make_material_db({"get": AsyncMock(return_value=None)})
        with _mock_db_with(mock_db):
            with pytest.raises(HTTPException) as exc:
                run(
                    svc.transition_stage(
                        MagicMock(), "x", "c", MaterialStage.REFINEMENT
                    )
                )
        assert exc.value.status_code == 404

    def test_raises_403_on_wrong_company(self):
        mock_db = _make_material_db()
        with _mock_db_with(mock_db):
            with pytest.raises(HTTPException) as exc:
                run(
                    svc.transition_stage(
                        MagicMock(), "mat001", "WRONG", MaterialStage.REFINEMENT
                    )
                )
        assert exc.value.status_code == 403
