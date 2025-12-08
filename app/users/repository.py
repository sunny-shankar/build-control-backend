from typing import Optional
from app.common.repository import BaseRepository
from app.users.models import User


class UserRepository(BaseRepository[User]):
    """
    Repository class for User model.
    Inherits common CRUD operations from BaseRepository.
    """

    async def get_by_email(self, email: str) -> Optional["User"]:
        """Get user by email address."""
        results = await self.get_by_filters(email=email)
        return results[0] if results else None

    async def get_by_mobile(self, mobile: str) -> Optional["User"]:
        """Get user by mobile number."""
        results = await self.get_by_filters(mobile_number=mobile)
        return results[0] if results else None
