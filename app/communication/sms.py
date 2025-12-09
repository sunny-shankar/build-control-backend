from abc import ABC, abstractmethod

from app.core import settings


class SMSProvider(ABC):
    """Abstract base class for SMS providers."""

    @abstractmethod
    async def send_otp(self, mobile_number: str, otp: str) -> bool:
        """Send OTP to mobile number. Returns True if successful."""
        pass


class MockSMSProvider(SMSProvider):
    """
    Mock SMS provider for development/testing.
    In production, replace with actual SMS provider (Twilio, AWS SNS, etc.)
    """

    async def send_otp(self, mobile_number: str, otp: str) -> bool:
        """
        Mock SMS sending. In development, just log the OTP.
        In production, integrate with actual SMS service.
        """
        if settings.ENVIRONMENT.value == "development":
            print(f"[MOCK SMS] OTP for {mobile_number}: {otp}")
            # In production, replace with actual SMS API call:
            # return await self._send_via_twilio(mobile_number, otp)
            return True
        else:
            # Production implementation would go here
            # Example: return await self._send_via_twilio(mobile_number, otp)
            raise NotImplementedError("SMS provider not configured for production")


# Global SMS provider instance
sms_provider = MockSMSProvider()
