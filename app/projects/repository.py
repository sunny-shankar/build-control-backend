from typing import Optional
from app.common.repository import BaseRepository
from app.projects.models import Project


class ProjectRepository(BaseRepository[Project]):
    """
    Repository class for Project model.
    Inherits common CRUD operations from BaseRepository.
    """

    async def get_by_name(self, project_name: str) -> Optional["Project"]:
        """Get project by name."""
        results = await self.get_by_filters(project_name=project_name)
        return results[0] if results else None
