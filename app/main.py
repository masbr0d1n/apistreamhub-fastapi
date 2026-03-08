"""
Main FastAPI application.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

from app.config import settings
from app.db.base import init_db
from app.core.exceptions import StreamHubException
from app.core.rate_limiter import limiter, rate_limit_exceeded_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    
    Handles startup and shutdown events.
    """
    # Startup
    print("🚀 Starting StreamHub API...")
    await init_db()
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down StreamHub API...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="StreamHub API - YouTube to RTMP/UDP streaming relay",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Register rate limiter
app.state.limiter = limiter
app.add_exception_handler(429, rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
import os
UPLOAD_DIR = Path(os.getcwd()) / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


# Exception handlers
@app.exception_handler(StreamHubException)
async def streamhub_exception_handler(request, exc: StreamHubException):
    """Handle StreamHub custom exceptions."""
    from fastapi.responses import JSONResponse
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": False,
            "statusCode": exc.status_code,
            "error": exc.__class__.__name__,
            "message": exc.message
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions."""
    from fastapi.responses import JSONResponse
    import traceback
    
    return JSONResponse(
        status_code=500,
        content={
            "status": False,
            "statusCode": 500,
            "error": "InternalServerError",
            "message": str(exc) if settings.DEBUG else "Internal server error",
            "detail": traceback.format_exc() if settings.DEBUG else None
        }
    )


@app.get("/", tags=["root"])
async def root():
    """Root endpoint - API information."""
    return {
        "status": True,
        "statusCode": 200,
        "message": "StreamHub API is running",
        "data": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected"
    }


# Include API v1 routers
from app.api.v1 import auth, channels, videos, api_router, screens, layouts, campaigns, templates
from app.api.playlists import router as playlists_router

app.include_router(auth.router, prefix="/api/v1")
app.include_router(channels.router, prefix="/api/v1")
app.include_router(videos.router, prefix="/api/v1")
app.include_router(api_router, prefix="/api/v1")
app.include_router(playlists_router)
app.include_router(screens.router, prefix="/api/v1")
app.include_router(layouts.router, prefix="/api/v1")
app.include_router(campaigns.router, prefix="/api/v1")
app.include_router(templates.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
