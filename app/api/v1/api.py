from fastapi import APIRouter

from app.api.v1 import auth, companies, users, materials, diagnostic, ai_providers, ai_generation, notifications

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(materials.router, prefix="/materials", tags=["materials"])
api_router.include_router(diagnostic.router, prefix="/diagnostic", tags=["diagnostic"])
api_router.include_router(ai_providers.router, prefix="/ai-providers", tags=["ai-providers"])
api_router.include_router(ai_generation.router, prefix="/ai", tags=["ai-generation"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
