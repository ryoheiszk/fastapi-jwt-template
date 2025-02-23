from fastapi import APIRouter
from app.api import v1_auth

router = APIRouter()
router.include_router(v1_auth.router, prefix="/auth", tags=["v1 Auth"])
