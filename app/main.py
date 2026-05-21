"""GaanaPaglu - AI-Powered Music Recommendation System.

Main FastAPI application entry point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from loguru import logger

from app.config import get_settings
from app.database.connection import init_db
from app.middleware.rate_limiter import limiter
from app.auth.router import router as auth_router
from app.user.router import router as user_router
from app.recommendations.router import router as recommendations_router
from app.recommendations.engine import recommendation_engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Initialize recommendation engine
    try:
        await recommendation_engine.initialize()
        logger.info("Recommendation engine initialized")
    except Exception as e:
        logger.warning(f"Recommendation engine initialization failed: {e}")
        logger.warning("API will work but recommendations may use fallback mode")

    yield

    # Shutdown
    logger.info("Shutting down GaanaPaglu")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description=(
        "🎵 GaanaPaglu - AI-Powered Music Recommendation System\n\n"
        "Get personalized music recommendations using AI. "
        "Supports natural language queries, mood-based playlists, "
        "similar song discovery, and history-aware personalization."
    ),
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - restrict for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Include routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(recommendations_router)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "message": "🎵 Welcome to GaanaPaglu! Visit /docs for API documentation.",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "components": {
            "database": "connected",
            "embedding_engine": "ready" if recommendation_engine._initialized else "not_loaded",
            "llm_generator": "ready" if recommendation_engine._initialized else "not_loaded",
        },
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred. Please try again later.",
            "error_type": type(exc).__name__,
        },
    )
