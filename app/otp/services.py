import secrets
from datetime import timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import settings
from app.otp.models import OTP
from app.otp.repository import OTPRepository
from app.utils.datetime import now_utc_naive


class OTPService:
    """
    Service for managing OTP generation, storage, and verification.
    Uses database storage with soft delete support.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize OTP service with database session.

        Args:
            session: AsyncSession instance for database operations
        """
        self.session = session
        self.repo = OTPRepository(session, OTP)

    def generate_otp(self, length: int = 6) -> str:
        """Generate a cryptographically secure random OTP of specified length."""
        return "".join([str(secrets.randbelow(10)) for _ in range(length)])

    async def store_otp(
        self, mobile_number: str, otp: str, expiry_minutes: int = None
    ) -> OTP:
        """
        Store OTP with expiration time in the database.
        Soft deletes any existing active OTPs for the mobile number first.

        Args:
            mobile_number: Mobile number for which OTP is generated
            otp: The OTP code to store
            expiry_minutes: Expiration time in minutes (defaults to settings value)

        Returns:
            Created OTP model instance
        """
        expiry_minutes = expiry_minutes or settings.OTP_EXPIRE_MINUTES
        expires_at = now_utc_naive() + timedelta(minutes=expiry_minutes)

        # Soft delete any existing active OTPs for this mobile number
        existing_otp = await self.repo.get_active_by_mobile(mobile_number)
        if existing_otp:
            existing_otp.soft_delete()
            await self.session.commit()

        # Create new OTP
        otp_obj = OTP(
            mobile_number=mobile_number,
            otp=otp,
            expires_at=expires_at,
            attempts=0,
            is_verified=False,
        )

        return await self.repo.create(otp_obj)

    async def verify_otp(self, mobile_number: str, otp: str) -> bool:
        """
        Verify OTP for a mobile number.
        Returns True if valid, False otherwise.
        Soft deletes the OTP after verification or max attempts reached.

        Args:
            mobile_number: Mobile number to verify OTP for
            otp: OTP code to verify

        Returns:
            True if OTP is valid and verified, False otherwise
        """
        # Get active OTP for mobile number
        otp_obj = await self.repo.get_active_by_mobile(mobile_number)
        if not otp_obj:
            return False

        # Check expiration
        if now_utc_naive() > otp_obj.expires_at:
            otp_obj.soft_delete()
            await self.session.commit()
            return False

        # Check max attempts
        if otp_obj.attempts >= settings.OTP_MAX_ATTEMPTS:
            otp_obj.soft_delete()
            await self.session.commit()
            return False

        # Increment attempts
        otp_obj.attempts += 1

        # Verify OTP
        if otp_obj.otp == otp:
            # Mark as verified and soft delete
            otp_obj.is_verified = True
            otp_obj.verified_at = now_utc_naive()
            otp_obj.soft_delete()
            await self.session.commit()
            return True

        # Save updated attempts count
        await self.session.commit()
        await self.session.refresh(otp_obj)
        return False

    async def get_otp(self, mobile_number: str) -> Optional[str]:
        """
        Get stored OTP for a mobile number (for testing/debugging).
        Returns None if no active OTP exists.

        Args:
            mobile_number: Mobile number to get OTP for

        Returns:
            OTP code string or None if not found/expired
        """
        otp_obj = await self.repo.get_active_by_mobile(mobile_number)
        if not otp_obj:
            return None

        # Check expiration
        if now_utc_naive() > otp_obj.expires_at:
            otp_obj.soft_delete()
            await self.session.commit()
            return None

        return otp_obj.otp

    async def clear_otp(self, mobile_number: str) -> None:
        """
        Soft delete OTP for a mobile number.

        Args:
            mobile_number: Mobile number to clear OTP for
        """
        otp_obj = await self.repo.get_active_by_mobile(mobile_number)
        if otp_obj:
            otp_obj.soft_delete()
            await self.session.commit()
