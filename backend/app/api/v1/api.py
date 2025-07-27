from fastapi import APIRouter

from app.api.auth import router as auth_router

api_router = APIRouter()

# Include routers
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

# Add more routers here as needed
# api_router.include_router(users_router, prefix="/users", tags=["users"])
# api_router.include_router(servers_router, prefix="/servers", tags=["servers"])