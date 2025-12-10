from fastapi import APIRouter

from app.users.api import router as user_router
from app.projects.api import router as project_router

router = APIRouter(prefix="/api")


router.include_router(user_router, prefix="/users", tags=["Users"])
router.include_router(project_router, prefix="/projects", tags=["Projects"])
