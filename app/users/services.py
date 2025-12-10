from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from app.core import settings
from app.users.models import User
from app.otp.services import OTPService
from app.users.repository import UserRepository
from app.communication.sms import sms_provider
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.schemas import (
    LoginResponseSchema,
    SendOTPResponseSchema,
    UserCreateSchema,
)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
        self.otp_service = OTPService(session)

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

        # Prepare user data
        user_data_dict = payload.model_dump()

        # Hash password if provided
        user_data_dict["password"] = pwd_context.hash(user_data_dict["password"])

        # Persist user
        user_data = User(**user_data_dict)
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

    def _create_access_token(self, user: User) -> str:
        """Create JWT access token for user."""
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {
            "sub": str(user.uuid),
            "email": user.email,
            "exp": expire,
        }
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    async def login(self, email: str, password: str) -> LoginResponseSchema:
        """
        Verify user credentials and generate JWT token.
        - Verify email exists
        - Verify password matches
        - Generate and return JWT token
        """
        # Get user by email
        user = await self.repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Verify password
        if not pwd_context.verify(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        # Generate JWT token
        access_token = self._create_access_token(user)

        # Prepare user data (exclude password)
        user_data = user.model_dump(exclude={"password"})

        return LoginResponseSchema(
            access_token=access_token,
            user=user_data,
        )

    async def send_otp(self, mobile_number: str) -> SendOTPResponseSchema:
        """
        Send OTP to user's mobile number.
        - Verify user exists with this mobile number
        - Generate OTP
        - Send OTP via SMS
        - Store OTP for verification
        """
        # Get user by mobile number
        user = await self.repo.get_by_mobile(mobile_number)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this mobile number not found",
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        # Generate OTP
        otp = self.otp_service.generate_otp(length=settings.OTP_LENGTH)

        # Store OTP
        await self.otp_service.store_otp(
            mobile_number=mobile_number,
            otp=otp,
            expiry_minutes=settings.OTP_EXPIRE_MINUTES,
        )

        # Send OTP via SMS
        sms_sent = await sms_provider.send_otp(mobile_number, otp)
        if not sms_sent:
            # Clear stored OTP if SMS failed
            await self.otp_service.clear_otp(mobile_number)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP. Please try again later.",
            )

        return SendOTPResponseSchema(
            message="OTP sent successfully to your mobile number",
            mobile_number=mobile_number,
        )

    async def verify_otp_and_login(
        self, mobile_number: str, otp: str
    ) -> LoginResponseSchema:
        """
        Verify OTP and generate JWT token.
        - Verify OTP is correct
        - Get user by mobile number
        - Generate and return JWT token
        """
        # Verify OTP
        if not await self.otp_service.verify_otp(mobile_number, otp):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP",
            )

        # Get user by mobile number
        user = await self.repo.get_by_mobile(mobile_number)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        # Generate JWT token
        access_token = self._create_access_token(user)

        # Prepare user data (exclude password)
        user_data = user.model_dump(exclude={"password"})

        return LoginResponseSchema(
            access_token=access_token,
            user=user_data,
        )
