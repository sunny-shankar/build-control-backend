from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.projects.models import Project
from app.projects.repository import ProjectRepository
from app.projects.schemas import ProjectCreateSchema
from app.users.models import User


class ProjectService:
    """
    Service layer for all Project-related operations.
    - Handles validation/business rules
    - Manages transactions (commit/rollback)
    - Uses repository for persistence
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ProjectRepository(session, Project)

    async def create_project(self, payload: ProjectCreateSchema, user: User) -> Project:
        """
        Create a new project with business validations.
        Associates the project with the current user.
        """
        # Prepare project data
        project_data_dict = payload.model_dump()
        project_data_dict["user_id"] = user.uuid

        # Create project instance
        project_data = Project(**project_data_dict)
        project = await self.repo.create(project_data)

        # Transaction boundary
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def get_project(self, project_uuid: str, user: User) -> Project:
        """
        Retrieve project by UUID.
        Only returns the project if it belongs to the current user.
        """
        try:
            uuid_obj = UUID(project_uuid)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid project UUID format",
            )

        project = await self.repo.get(uuid_obj)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        # Verify ownership
        if project.user_id != user.uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this project",
            )

        return project

    async def get_all_projects(
        self, user: User, skip: int = 0, limit: int = 100
    ) -> list[Project]:
        """
        Retrieve all projects for the current user with pagination.
        """
        return await self.repo.get_by_filters(user_id=user.uuid, skip=skip, limit=limit)
