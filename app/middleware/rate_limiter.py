"""Rate limiting middleware for API protection."""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

from app.config import get_settings

settings = get_settings()


def get_user_identifier(request: Request) -> str:
    """Get rate limit key - use auth token user or IP address."""
    # Try to get user from authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        # Use token as identifier (unique per user)
        return auth_header[7:20]  # First 13 chars of token as key
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(key_func=get_user_identifier)
