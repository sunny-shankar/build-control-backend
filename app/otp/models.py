from datetime import datetime
from typing import Optional

from sqlmodel import Field

from app.common.models import BaseSQLModel


class OTP(BaseSQLModel, table=True):
    """
    OTP (One-Time Password) model for storing OTPs with soft delete support.
    """

    __tablename__ = "otps"

    # Required fields
    mobile_number: str = Field(
        nullable=False,
        index=True,
        description="Mobile number for which OTP was generated",
        max_length=15,
    )

    otp: str = Field(
        nullable=False,
        description="The OTP code",
        max_length=10,
    )

    expires_at: datetime = Field(
        description="Expiration timestamp for the OTP",
    )

    # Verification tracking
    attempts: int = Field(
        default=0,
        nullable=False,
        description="Number of verification attempts made",
    )

    is_verified: bool = Field(
        default=False,
        nullable=False,
        description="Whether the OTP has been successfully verified",
    )

    verified_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when OTP was verified",
    )
