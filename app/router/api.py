from fastapi import APIRouter

from app.users.api import router as user_router

router = APIRouter(prefix="/api")


router.include_router(user_router, prefix="/users", tags=["Users"])
