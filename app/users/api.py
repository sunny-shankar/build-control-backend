from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.schemas import ApiResponse
from app.db.session import get_async_session
from app.users.models import User
from app.users.schemas import UserCreateSchema
from app.users.services import UserService


router = APIRouter()


def get_user_service(
    session: AsyncSession = Depends(get_async_session),
) -> UserService:
    return UserService(session=session)


@router.post("")
async def create_user(
    payload: UserCreateSchema,
    service: UserService = Depends(get_user_service),
) -> ApiResponse[User]:
    """Create a new user."""
    user = await service.create_user(payload)
    return ApiResponse(data=user.model_dump())
