from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.schemas import ApiResponse
from app.db.session import get_async_session
from app.users.models import User
from app.users.schemas import (
    LoginResponseSchema,
    LoginSchema,
    SendOTPResponseSchema,
    SendOTPSchema,
    UserCreateSchema,
    VerifyOTPSchema,
)
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


@router.post("/login")
async def login(
    payload: LoginSchema,
    service: UserService = Depends(get_user_service),
) -> ApiResponse[LoginResponseSchema]:
    """Login with email and password, returns JWT token."""
    login_response = await service.login(payload.email, payload.password)
    return ApiResponse(data=login_response.model_dump())


@router.post("/send-otp")
async def send_otp(
    payload: SendOTPSchema,
    service: UserService = Depends(get_user_service),
) -> ApiResponse[SendOTPResponseSchema]:
    """Send OTP to user's mobile number for login."""
    otp_response = await service.send_otp(payload.mobile_number)
    return ApiResponse(data=otp_response.model_dump())


@router.post("/verify-otp")
async def verify_otp(
    payload: VerifyOTPSchema,
    service: UserService = Depends(get_user_service),
) -> ApiResponse[LoginResponseSchema]:
    """Verify OTP and login, returns JWT token."""
    login_response = await service.verify_otp_and_login(
        payload.mobile_number, payload.otp
    )
    return ApiResponse(data=login_response.model_dump())
