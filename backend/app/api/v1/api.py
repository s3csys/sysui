from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.v1.admin import router as admin_router
from app.api.v1.permissions import router as permissions_router
from app.api.v1.profile import router as profile_router
from app.api.v1.servers import router as servers_router

api_router = APIRouter()

# Include routers
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(permissions_router, prefix="/permissions", tags=["permissions"])
api_router.include_router(profile_router, prefix="/profile", tags=["profile"])

# Add more routers here as needed
# api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(servers_router, prefix="/servers", tags=["servers"])