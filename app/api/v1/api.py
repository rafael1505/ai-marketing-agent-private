from fastapi import APIRouter

from app.api.v1 import auth, companies, users, materials, diagnostic, auth_test, ai_providers

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(materials.router, prefix="/materials", tags=["materials"])
api_router.include_router(diagnostic.router, prefix="/diagnostic", tags=["diagnostic"])
api_router.include_router(auth_test.router, prefix="/auth-test", tags=["testing"])
api_router.include_router(ai_providers.router, prefix="/ai-providers", tags=["ai-providers"])
