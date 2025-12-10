from typing import Optional
from sqlalchemy import select, and_

from app.common.repository import BaseRepository
from app.otp.models import OTP
from app.utils.datetime import now_utc_naive


class OTPRepository(BaseRepository[OTP]):
    """
    Repository class for OTP model.
    Inherits common CRUD operations from BaseRepository.
    """

    async def get_active_by_mobile(self, mobile_number: str) -> Optional[OTP]:
        """
        Get the most recent active (non-expired, non-verified) OTP for a mobile number.
        Returns None if no active OTP exists.
        """
        now = now_utc_naive()
        query = (
            select(OTP)
            .where(
                and_(
                    OTP.mobile_number == mobile_number,
                    OTP.expires_at > now,
                    OTP.is_verified == False,  # noqa: E712
                    OTP.deleted_at.is_(None),
                )
            )
            .order_by(OTP.created_at.desc())
            .limit(1)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_latest_by_mobile(
        self, mobile_number: str, include_deleted: bool = False
    ) -> Optional[OTP]:
        """
        Get the most recent OTP for a mobile number (regardless of status).
        """
        query = select(OTP).where(OTP.mobile_number == mobile_number)

        if not include_deleted:
            query = query.where(OTP.deleted_at.is_(None))

        query = query.order_by(OTP.created_at.desc()).limit(1)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def soft_delete_expired(self) -> int:
        """
        Soft delete all expired OTPs that haven't been verified.
        Returns the number of OTPs soft-deleted.
        """
        now = now_utc_naive()
        query = select(OTP).where(
            and_(
                OTP.expires_at <= now,
                OTP.is_verified == False,  # noqa: E712
                OTP.deleted_at.is_(None),
            )
        )

        result = await self.session.execute(query)
        otps = result.scalars().all()

        for otp in otps:
            otp.soft_delete()

        await self.session.commit()
        return len(otps)
