from pydantic import BaseModel, EmailStr, Field


class LoginSchema(BaseModel):
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=6, description="User password")


class SendOTPSchema(BaseModel):
    mobile_number: str = Field(
        description="10-digit mobile number",
        min_length=10,
        max_length=15,
    )


class VerifyOTPSchema(BaseModel):
    mobile_number: str = Field(
        description="10-digit mobile number",
        min_length=10,
        max_length=15,
    )
    otp: str = Field(
        description="6-digit OTP code",
        min_length=6,
        max_length=6,
    )


class LoginResponseSchema(BaseModel):
    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: dict = Field(description="User information")


class SendOTPResponseSchema(BaseModel):
    message: str = Field(description="Response message")
    mobile_number: str = Field(description="Mobile number OTP was sent to")


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
