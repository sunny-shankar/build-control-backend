import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core import settings


class OTPService:
    """
    Service for managing OTP generation, storage, and verification.
    Uses in-memory storage (can be replaced with Redis in production).
    """

    def __init__(self):
        # In-memory storage: {mobile_number: {"otp": str, "expires_at": datetime}}
        self._otp_store: dict[str, dict] = {}

    def generate_otp(self, length: int = 6) -> str:
        """Generate a cryptographically secure random OTP of specified length."""
        return "".join([str(secrets.randbelow(10)) for _ in range(length)])

    def store_otp(
        self, mobile_number: str, otp: str, expiry_minutes: int = None
    ) -> None:
        """Store OTP with expiration time."""
        expiry_minutes = expiry_minutes or settings.OTP_EXPIRE_MINUTES
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
        self._otp_store[mobile_number] = {
            "otp": otp,
            "expires_at": expires_at,
            "attempts": 0,
        }

    def verify_otp(self, mobile_number: str, otp: str) -> bool:
        """
        Verify OTP for a mobile number.
        Returns True if valid, False otherwise.
        """
        if mobile_number not in self._otp_store:
            return False

        otp_data = self._otp_store[mobile_number]

        # Check expiration
        if datetime.now(timezone.utc) > otp_data["expires_at"]:
            # Remove expired OTP
            del self._otp_store[mobile_number]
            return False

        # Check max attempts
        if otp_data["attempts"] >= settings.OTP_MAX_ATTEMPTS:
            del self._otp_store[mobile_number]
            return False

        # Increment attempts
        otp_data["attempts"] += 1

        # Verify OTP
        if otp_data["otp"] == otp:
            # Remove OTP after successful verification
            del self._otp_store[mobile_number]
            return True

        return False

    def get_otp(self, mobile_number: str) -> Optional[str]:
        """Get stored OTP for a mobile number (for testing/debugging)."""
        if mobile_number not in self._otp_store:
            return None

        otp_data = self._otp_store[mobile_number]

        # Check expiration
        if datetime.now(timezone.utc) > otp_data["expires_at"]:
            del self._otp_store[mobile_number]
            return None

        return otp_data["otp"]

    def clear_otp(self, mobile_number: str) -> None:
        """Clear OTP for a mobile number."""
        self._otp_store.pop(mobile_number, None)


# Global OTP service instance
otp_service = OTPService()
