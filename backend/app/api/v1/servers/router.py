from fastapi import APIRouter
from .endpoints import router as servers_router

router = APIRouter()
router.include_router(servers_router, prefix="/servers", tags=["servers"])