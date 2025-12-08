from fastapi import HTTPException, status
from app.users.models import User
from app.users.repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.schemas import UserCreateSchema


class UserService:
    """
    Service layer for all User-related operations.
    - Handles validation/business rules
    - Manages transactions (commit/rollback)
    - Uses repository for persistence
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session, User)

    async def create_user(self, payload: UserCreateSchema) -> User:
        """
        Create a new user with business validations:
        - Ensure unique email
        - Ensure unique mobile number
        """

        # Check mobile exists
        existing = await self.repo.get_by_mobile(payload.mobile_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this mobile number already exists",
            )

        # Check email exists
        existing = await self.repo.get_by_email(payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        # Persist user
        user_data = User(**payload.model_dump())
        user = await self.repo.create(user_data)

        # Transaction boundary
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_email(self, email: str) -> User:
        """Retrieve user by email."""
        user = await self.repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user
