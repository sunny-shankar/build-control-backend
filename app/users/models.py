from typing import Optional

from sqlmodel import Field

from app.core.models import BaseSQLModel


class User(BaseSQLModel, table=True):
    __tablename__ = "users"

    # Required fields
    mobile_number: str = Field(
        nullable=False,
        index=True,
        unique=True,
        description="10-digit mobile number; validated at the service layer",
        max_length=15,
    )

    email: str = Field(
        nullable=False,
        index=True,
        unique=True,
        max_length=255,
    )

    company_name: str = Field(
        nullable=False,
        max_length=255,
    )

    state: str = Field(
        nullable=False,
        max_length=100,
    )

    # Optional business details
    company_address: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    gstin: Optional[str] = Field(
        default=None,
        max_length=15,  # standard GSTIN length
        index=True,
    )

    pan: Optional[str] = Field(
        default=None,
        max_length=10,  # standard PAN length
        index=True,
    )

    # Flags
    is_active: bool = Field(default=True, nullable=False)
    is_verified: bool = Field(default=False, nullable=False)
