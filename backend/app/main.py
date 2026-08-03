"""
NFM-X Main Application
FastAPI application entry point with all API routers.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from backend.app.config import (
    NFM_APP_NAME,
    NFM_APP_VERSION,
    NFM_CORS_ORIGINS,
    NFM_CORS_METHODS,
    NFM_CORS_HEADERS,
    NFM_RATE_LIMIT_ENABLED,
    NFM_COMPRESSION_ENABLED,
    NFM_OCR_ENABLED,
    NFM_MCP_ENABLED
)
from backend.app.health import router as health_router
from backend.app.logging_config import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(f"Starting {NFM_APP_NAME} v{NFM_APP_VERSION}")
    
    # Initialize compression scheduler if enabled
    if NFM_COMPRESSION_ENABLED:
        from backend.app.compression.scheduler import initialize_compression_scheduler
        await initialize_compression_scheduler()
        logger.info("Compression scheduler initialized")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {NFM_APP_NAME}")


# Create FastAPI app
app = FastAPI(
    title=NFM_APP_NAME,
    version=NFM_APP_VERSION,
    description="NFM-X: Non-Forgettable Memory Layer API",
    lifespan=lifespan
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=NFM_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=NFM_CORS_METHODS,
    allow_headers=NFM_CORS_HEADERS
)

# Add rate limiting middleware if enabled
if NFM_RATE_LIMIT_ENABLED:
    from backend.app.middleware.rate_limit import rate_limit_middleware
    app.middleware("http")(rate_limit_middleware)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include all API routers

# V1 API Routers
try:
    from backend.app.api.memory import router as memory_router
    app.include_router(memory_router, prefix="/api/v1/memories", tags=["v1"])
    logger.info("Memory API v1 loaded")
except ImportError as e:
    logger.warning(f"Memory API v1 not available: {e}")

try:
    from backend.app.api.search import router as search_router
    app.include_router(search_router, prefix="/api/v1/search", tags=["v1"])
    logger.info("Search API v1 loaded")
except ImportError as e:
    logger.warning(f"Search API v1 not available: {e}")

try:
    from backend.app.api.graph import router as graph_router
    app.include_router(graph_router, prefix="/api/v1/graph", tags=["v1"])
    logger.info("Graph API v1 loaded")
except ImportError as e:
    logger.warning(f"Graph API v1 not available: {e}")

try:
    from backend.app.api.stats import router as stats_router
    app.include_router(stats_router, prefix="/api/v1/stats", tags=["v1"])
    logger.info("Stats API v1 loaded")
except ImportError as e:
    logger.warning(f"Stats API v1 not available: {e}")

try:
    from backend.app.api.conflicts import router as conflicts_v1_router
    app.include_router(conflicts_v1_router, prefix="/api/v1/conflicts", tags=["v1"])
    logger.info("Conflicts API v1 loaded")
except ImportError as e:
    logger.warning(f"Conflicts API v1 not available: {e}")

# V2 API Routers
try:
    from backend.app.api.v2.memory_v2 import router as memory_v2_router
    app.include_router(memory_v2_router, prefix="/api/v2/memories", tags=["v2"])
    logger.info("Memory API v2 loaded")
except ImportError as e:
    logger.warning(f"Memory API v2 not available: {e}")

try:
    from backend.app.api.v2.search_v2 import router as search_v2_router
    app.include_router(search_v2_router, prefix="/api/v2/search", tags=["v2"])
    logger.info("Search API v2 loaded")
except ImportError as e:
    logger.warning(f"Search API v2 not available: {e}")

try:
    from backend.app.api.v2.graph_v2 import router as graph_v2_router
    app.include_router(graph_v2_router, prefix="/api/v2/graph", tags=["v2"])
    logger.info("Graph API v2 loaded")
except ImportError as e:
    logger.warning(f"Graph API v2 not available: {e}")

try:
    from backend.app.api.v2.stats_v2 import router as stats_v2_router
    app.include_router(stats_v2_router, prefix="/api/v2/stats", tags=["v2"])
    logger.info("Stats API v2 loaded")
except ImportError as e:
    logger.warning(f"Stats API v2 not available: {e}")

try:
    from backend.app.api.v2.conflicts_v2 import router as conflicts_v2_router
    app.include_router(conflicts_v2_router, prefix="/api/v2/conflicts", tags=["v2"])
    logger.info("Conflicts API v2 loaded")
except ImportError as e:
    logger.warning(f"Conflicts API v2 not available: {e}")

# V3 API Routers
try:
    from backend.app.api.world_model import router as world_model_router
    app.include_router(world_model_router, prefix="/api/v3/world-model", tags=["v3"])
    logger.info("World Model API v3 loaded")
except ImportError as e:
    logger.warning(f"World Model API v3 not available: {e}")

try:
    from backend.app.api.predictions import router as predictions_router
    app.include_router(predictions_router, prefix="/api/v3/predictions", tags=["v3"])
    logger.info("Predictions API v3 loaded")
except ImportError as e:
    logger.warning(f"Predictions API v3 not available: {e}")

try:
    from backend.app.api.causal_advanced import router as causal_router
    app.include_router(causal_router, prefix="/api/v3/causal", tags=["v3"])
    logger.info("Causal API v3 loaded")
except ImportError as e:
    logger.warning(f"Causal API v3 not available: {e}")

try:
    from backend.app.api.sharing import router as sharing_router
    app.include_router(sharing_router, prefix="/api/v3/sharing", tags=["v3"])
    logger.info("Sharing API v3 loaded")
except ImportError as e:
    logger.warning(f"Sharing API v3 not available: {e}")

try:
    from backend.app.api.sync import router as sync_router
    app.include_router(sync_router, prefix="/api/v3/sync", tags=["v3"])
    logger.info("Sync API v3 loaded")
except ImportError as e:
    logger.warning(f"Sync API v3 not available: {e}")

try:
    from backend.app.api.simulation import router as simulation_router
    app.include_router(simulation_router, prefix="/api/v3/simulation", tags=["v3"])
    logger.info("Simulation API v3 loaded")
except ImportError as e:
    logger.warning(f"Simulation API v3 not available: {e}")

try:
    from backend.app.api.compression import router as compression_router
    app.include_router(compression_router, prefix="/api/v3/compression", tags=["v3"])
    logger.info("Compression API v3 loaded")
except ImportError as e:
    logger.warning(f"Compression API v3 not available: {e}")

# V4 API Routers
try:
    from backend.app.api.health import router as health_router
    app.include_router(health_router, prefix="/api/health", tags=["v4"])
    logger.info("Health API v4 loaded")
except ImportError as e:
    logger.warning(f"Health API v4 not available: {e}")

try:
    from backend.app.api.ocr import router as ocr_router
    app.include_router(ocr_router, prefix="/api/ocr", tags=["v4"])
    logger.info("OCR API v4 loaded")
except ImportError as e:
    logger.warning(f"OCR API v4 not available: {e}")

try:
    from backend.app.api.documents import router as documents_router
    app.include_router(documents_router, prefix="/api/documents", tags=["v4"])
    logger.info("Documents API v4 loaded")
except ImportError as e:
    logger.warning(f"Documents API v4 not available: {e}")

try:
    from backend.app.api.batch import router as batch_router
    app.include_router(batch_router, prefix="/api/batch", tags=["v4"])
    logger.info("Batch API v4 loaded")
except ImportError as e:
    logger.warning(f"Batch API v4 not available: {e}")

try:
    from backend.app.api.conflicts import router as conflicts_v4_router
    app.include_router(conflicts_v4_router, prefix="/api/conflicts", tags=["v4"])
    logger.info("Conflicts API v4 loaded")
except ImportError as e:
    logger.warning(f"Conflicts API v4 not available: {e}")

try:
    from backend.app.api.patterns import router as patterns_router
    app.include_router(patterns_router, prefix="/api/patterns", tags=["v4"])
    logger.info("Patterns API v4 loaded")
except ImportError as e:
    logger.warning(f"Patterns API v4 not available: {e}")

try:
    from backend.app.api.skills import router as skills_router
    app.include_router(skills_router, prefix="/api/skills", tags=["v4"])
    logger.info("Skills API v4 loaded")
except ImportError as e:
    logger.warning(f"Skills API v4 not available: {e}")

try:
    from backend.app.api.mcp import router as mcp_router
    app.include_router(mcp_router, prefix="/api/mcp", tags=["v4"])
    logger.info("MCP API v4 loaded")
except ImportError as e:
    logger.warning(f"MCP API v4 not available: {e}")


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": NFM_APP_NAME,
        "version": NFM_APP_VERSION,
        "status": "running",
        "features": {
            "ocr_enabled": NFM_OCR_ENABLED,
            "compression_enabled": NFM_COMPRESSION_ENABLED,
            "mcp_enabled": NFM_MCP_ENABLED,
            "rate_limiting_enabled": NFM_RATE_LIMIT_ENABLED
        },
        "api_versions": ["v1", "v2", "v3", "v4"],
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
