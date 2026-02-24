"""
Custom exceptions for FastAPI application.
"""
from typing import Any
from fastapi import HTTPException, status


class StreamHubException(Exception):
    """Base exception for StreamHub API."""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(StreamHubException):
    """Resource not found exception."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class BadRequestException(StreamHubException):
    """Bad request exception."""
    
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class UnauthorizedException(StreamHubException):
    """Unauthorized exception."""
    
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(StreamHubException):
    """Forbidden exception."""
    
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class ConflictException(StreamHubException):
    """Conflict exception."""
    
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class ValidationException(StreamHubException):
    """Validation exception."""
    
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class InternalServerException(StreamHubException):
    """Internal server error exception."""
    
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)
