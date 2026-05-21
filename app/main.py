"""GaanaPaglu - AI-Powered Music Recommendation System."""

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
    """Application lifespan."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Initialize database (sync - fast)
    init_db()
    logger.info("Database initialized")

    # Initialize recommendation engine
    try:
        await recommendation_engine.initialize()
        logger.info("Recommendation engine ready")
    except Exception as e:
        logger.warning(f"Engine init warning: {e}")

    yield
    logger.info("Shutting down")


# Create app
app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Music Recommendation System",
    version=settings.app_version,
    lifespan=lifespan,
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(recommendations_router)


@app.get("/", tags=["Health"])
async def root():
    return {"app": settings.app_name, "version": settings.app_version, "status": "running"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "engine_ready": recommendation_engine._initialized}


@app.exception_handler(Exception)
async def error_handler(request: Request, exc: Exception):
    logger.error(f"Error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
