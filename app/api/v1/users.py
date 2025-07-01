from typing import Any, List, Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.api.v1.deps import get_current_admin_user, get_current_active_user
from app.models.user import UserCreate, UserUpdate, User
from app.db.user import UserDB

router = APIRouter()

@router.post("", response_model=User)
async def create_user(
    user: UserCreate,
    current_user: Annotated[dict, Depends(get_current_admin_user)],
    request: Request
) -> Any:
    mongodb = request.app.mongodb
    user_db = UserDB(mongodb[settings.MONGODB_DB].users)
    try:
        return await user_db.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=User)
async def read_current_user(
    current_user: Annotated[dict, Depends(get_current_active_user)]
) -> Any:
    return current_user

@router.put("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: Annotated[dict, Depends(get_current_active_user)],
    request: Request
) -> Any:
    mongodb = request.app.mongodb
    user_db = UserDB(mongodb[settings.MONGODB_DB].users)
    updated_user = await user_db.update_user(str(current_user["_id"]), user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.get("/company/{company_id}", response_model=List[User])
async def read_company_users(
    company_id: str,
    current_user: Annotated[dict, Depends(get_current_admin_user)],
    request: Request,
    skip: int = 0,
    limit: int = 100
) -> Any:
    mongodb = request.app.mongodb
    user_db = UserDB(mongodb[settings.MONGODB_DB].users)
    return await user_db.get_company_users(company_id, skip=skip, limit=limit)
