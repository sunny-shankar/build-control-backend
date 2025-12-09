from pydantic import BaseModel, EmailStr, Field


class UserCreateSchema(BaseModel):
    mobile_number: str = Field(
        description="10-digit mobile number; validated at the service layer",
        max_length=15,
    )

    email: EmailStr = Field(
        max_length=255,
    )

    company_name: str | None = Field(default=None, max_length=255)

    state: str | None = Field(default=None, max_length=100)

    # Optional business details
    company_address: str | None = Field(
        default=None,
        max_length=500,
    )

    gstin: str | None = Field(
        default=None,
        max_length=15,  # standard GSTIN length
    )

    pan: str | None = Field(
        default=None,
        max_length=10,  # standard PAN length
    )

    password: str = Field(
        min_length=6,
        max_length=255,
        description="User password",
    )
