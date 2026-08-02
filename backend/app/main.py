"""
NFM-X Main Application
FastAPI backend for Non-Forgettable Memory Layer
Supports V1.5, V2, V3, and V4 endpoints
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import configuration and logging first
from backend.app.config import get_config
from backend.app.logging_config import setup_logging

# Setup logging before any other imports
setup_logging()

# Import middleware
from backend.app.middleware.rate_limit import rate_limit_middleware

# Import V1.5 API routers
from backend.app.api.memory import router as memory_router
from backend.app.api.search import router as search_router
from backend.app.api.context import router as context_router
from backend.app.api.conflicts import router as conflicts_router
from backend.app.api.graph import router as graph_router
from backend.app.api.stats import router as stats_router

# Import V2 API routers
from backend.app.api.v2.memory_v2 import router as memory_v2_router
from backend.app.api.v2.search_v2 import router as search_v2_router
from backend.app.api.v2.graph_v2 import router as graph_v2_router
from backend.app.api.v2.conflicts_v2 import router as conflicts_v2_router
from backend.app.api.v2.stats_v2 import router as stats_v2_router

# Import V3 API routers
from backend.app.api.world_model import router as world_model_router
from backend.app.api.predictions import router as predictions_router
from backend.app.api.causal_advanced import router as causal_advanced_router
from backend.app.api.sharing import router as sharing_router
from backend.app.api.sync import router as sync_router
from backend.app.api.simulation import router as simulation_router
from backend.app.api.compression import router as compression_router

# Import V4 API routers
from backend.app.api.health import router as health_router

# Get configuration
config = get_config()
import logging
logger = logging.getLogger(__name__)

logger.info(f"Starting {config.app_name} v{config.version} in {config.environment} mode")

# Create FastAPI app
app = FastAPI(
    title=config.app_name,
    description="Non-Forgettable Memory Layer API - V1.5, V2, V3, V4",
    version=config.version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware with configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors.allow_origins,
    allow_credentials=config.cors.allow_credentials,
    allow_methods=config.cors.allow_methods,
    allow_headers=config.cors.allow_headers,
    expose_headers=config.cors.expose_headers,
)

# Rate limiting middleware (optional)
if config.rate_limit.enabled:
    app.middleware("http")(rate_limit_middleware)
    logger.info(f"Rate limiting enabled: {config.rate_limit.requests_per_minute} req/min")
else:
    logger.info("Rate limiting is disabled")


# Include V1.5 routers
app.include_router(memory_router, prefix="/api", tags=["Memory"])
app.include_router(search_router, prefix="/api", tags=["Search"])
app.include_router(context_router, prefix="/api", tags=["Context"])
app.include_router(conflicts_router, prefix="/api", tags=["Conflicts"])
app.include_router(graph_router, prefix="/api", tags=["Graph"])
app.include_router(stats_router, prefix="/api", tags=["Stats"])

# Include V2 routers
app.include_router(memory_v2_router, prefix="/api/v2", tags=["V2 Memory"])
app.include_router(search_v2_router, prefix="/api/v2", tags=["V2 Search"])
app.include_router(graph_v2_router, prefix="/api/v2", tags=["V2 Graph"])
app.include_router(conflicts_v2_router, prefix="/api/v2", tags=["V2 Conflicts"])
app.include_router(stats_v2_router, prefix="/api/v2", tags=["V2 Stats"])

# Include V3 routers
app.include_router(world_model_router, prefix="/api/v1", tags=["World Model"])
app.include_router(predictions_router, prefix="/api/v1", tags=["Predictions"])
app.include_router(causal_advanced_router, prefix="/api/v1", tags=["Causal Advanced"])
app.include_router(sharing_router, prefix="/api/v1", tags=["Sharing"])
app.include_router(sync_router, prefix="/api/v1", tags=["Sync"])
app.include_router(simulation_router, prefix="/api/v1", tags=["Simulation"])
app.include_router(compression_router, prefix="/api/v1", tags=["Compression"])

# Include V4 routers
app.include_router(health_router, prefix="/health", tags=["Health Check"])


# Root endpoint
@app.get("/")
async def root():
    return {
        "name": config.app_name,
        "version": config.version,
        "description": "Non-Forgettable Memory Layer",
        "docs": "/docs",
        "health": "/health/detailed",
        "versions": {
            "v1.5": "/api/docs",
            "v2": "/api/v2/docs",
            "v3": "/api/v1/docs",
            "v4": "/health/detailed"
        },
        "environment": config.environment,
        "features": {
            "ocr_enabled": config.ocr.enabled,
            "compression_enabled": config.compression.enabled,
            "sync_enabled": config.sync.enabled,
            "rate_limiting_enabled": config.rate_limit.enabled
        }
    }


# Health check endpoint (kept for backward compatibility)
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": config.version, "environment": config.environment}