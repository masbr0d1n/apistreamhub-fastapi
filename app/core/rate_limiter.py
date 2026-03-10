"""
Rate limiting configuration using SlowAPI.

This module sets up rate limiting to protect against brute force attacks and API abuse.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

# Create limiter instance
limiter = Limiter(key_func=get_remote_address)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Handle rate limit exceeded errors.
    
    Returns a 429 Too Many Requests response with retry information.
    """
    return JSONResponse(
        status_code=429,
        content={
            "status": False,
            "statusCode": 429,
            "error": "RateLimitExceeded",
            "message": "Too many requests. Please slow down.",
            "detail": str(exc.detail),
            "retry_after": exc.headers.get("Retry-After", "60") if exc.headers else "60"
        }
    )


# Rate limit presets for different endpoint types
RATE_LIMITS = {
    # Authentication endpoints (strict limits for brute force protection)
    "auth_login": "5/minute",      # 5 requests per minute
    "auth_register": "3/minute",    # 3 requests per minute
    
    # File upload endpoints (moderate limits)
    "video_upload": "10/minute",    # 10 requests per minute
    
    # General API endpoints (relaxed limits)
    "default": "60/minute",         # 60 requests per minute
    "read_heavy": "30/minute",      # 30 requests per minute for expensive queries
}
