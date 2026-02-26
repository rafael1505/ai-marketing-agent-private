import logging

from fastapi import APIRouter

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/unread-count")
async def get_unread_count():
    """
    Return unread notification count for the current user.
    Stub implementation returns 0 until a real notifications feature exists.
    """
    # Temporary debug log to verify backend receives the request
    logger.info("[notifications] GET /unread-count called")
    return {"count": 0}
