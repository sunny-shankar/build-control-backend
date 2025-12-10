from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.auth import get_current_user
from app.common.schemas import ApiResponse
from app.db.session import get_async_session
from app.projects.schemas import (
    ProjectCreateSchema,
    ProjectResponseSchema,
)
from app.projects.services import ProjectService
from app.users.models import User


router = APIRouter()


def get_project_service(
    session: AsyncSession = Depends(get_async_session),
) -> ProjectService:
    return ProjectService(session=session)


@router.post("", response_model=ApiResponse[ProjectResponseSchema])
async def create_project(
    payload: ProjectCreateSchema,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
) -> ApiResponse[ProjectResponseSchema]:
    """Create a new project. The project will be associated with the current user."""
    project = await service.create_project(payload, current_user)
    project_dict = project.model_dump(mode="json")
    return ApiResponse(data=ProjectResponseSchema(**project_dict))


@router.get("/{project_uuid}", response_model=ApiResponse[ProjectResponseSchema])
async def get_project(
    project_uuid: str,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
) -> ApiResponse[ProjectResponseSchema]:
    """Get a project by UUID. Only returns projects owned by the current user."""
    project = await service.get_project(project_uuid, current_user)
    project_dict = project.model_dump(mode="json")
    return ApiResponse(data=ProjectResponseSchema(**project_dict))


@router.get("", response_model=ApiResponse[list[ProjectResponseSchema]])
async def get_all_projects(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
) -> ApiResponse[list[ProjectResponseSchema]]:
    """Get all projects for the current user with pagination."""
    projects = await service.get_all_projects(current_user, skip=skip, limit=limit)
    projects_list = [
        ProjectResponseSchema(**project.model_dump(mode="json")) for project in projects
    ]
    return ApiResponse(data=projects_list)
