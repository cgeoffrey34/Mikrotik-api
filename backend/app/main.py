from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .config import get_settings
from .database import init_db
from .api import routers_router, mikrotik_router
from .scheduler import start_scheduler, stop_scheduler

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Mikrotik Management API...")
    await init_db()
    logger.info("Database initialized")
    start_scheduler()
    logger.info("Background scheduler started")
    yield
    # Shutdown
    logger.info("Shutting down...")
    stop_scheduler()


app = FastAPI(
    title=settings.app_name,
    description="API for centralized Mikrotik router management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routers_router, prefix=settings.api_prefix)
app.include_router(mikrotik_router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
