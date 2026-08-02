"""
NFM-X FastAPI Application
Main entry point for the NFM-X memory layer API
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .config import settings
from .storage.database import init_db, close_db
from .memory.models import Base
from .workers.scheduler import scheduler, add_scheduled_job
from .workers.jobs import run_all_consolidation_jobs


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# LIFESPAN MANAGEMENT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager"""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Database URL: {settings.database_url}")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully")
        
        # Load FAISS index if exists
        from .embeddings.vector_store import vector_store
        try:
            vector_store.load()
            logger.info(f"Loaded FAISS index with {vector_store.count} vectors")
        except Exception as e:
            logger.warning(f"Could not load FAISS index: {e}")
        
        # Load embedding model
        from .embeddings.models import embedding_model
        try:
            _ = embedding_model.dimension
            logger.info(f"Embedding model loaded (dimension: {embedding_model.dimension})")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
        
        # Start background scheduler
        logger.info("Starting background scheduler...")
        await scheduler.start()
        
        # Add consolidation job (runs hourly)
        add_scheduled_job(
            run_all_consolidation_jobs,
            name="consolidation",
            hours=1
        )
        logger.info("Added consolidation job (runs every hour)")
        
        logger.info(f"{settings.app_name} started successfully")
        logger.info(f"API available at http://{settings.host}:{settings.port}")
        
        yield
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    
    # Shutdown
    logger.info("Shutting down...")
    
    try:
        # Stop scheduler
        await scheduler.stop()
        logger.info("Scheduler stopped")
        
        # Save FAISS index
        from .embeddings.vector_store import vector_store
        try:
            vector_store.save()
            logger.info(f"Saved FAISS index with {vector_store.count} vectors")
        except Exception as e:
            logger.warning(f"Could not save FAISS index: {e}")
        
        # Close database
        await close_db()
        logger.info("Database closed")
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}")
    
    logger.info("Shutdown complete")


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    NFM-X: Non-Forgettable Memory Layer API
    
    A production-grade, model-independent, local-first long-term memory layer for AI systems.
    
    ## Core Principles
    
    - **Never Forget**: Once memory is committed, it is never silently overwritten or lost
    - **Versioning**: New information creates a new version, history is preserved
    - **Provenance**: Every memory has a source and lineage
    - **Portability**: Memory remains portable between models and applications
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ============================================================================
# MIDDLEWARE
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else None,
        },
    )


# ============================================================================
# ROUTERS
# ============================================================================

from .api import memory, search, context, conflicts, graph, stats

app.include_router(memory.router, prefix="/v1/memory", tags=["Memory"])
app.include_router(search.router, prefix="/v1/memory", tags=["Search"])
app.include_router(context.router, prefix="/v1/memory", tags=["Context"])
app.include_router(conflicts.router, prefix="/v1", tags=["Conflicts"])
app.include_router(graph.router, prefix="/v1", tags=["Graph"])
app.include_router(stats.router, prefix="/v1", tags=["Stats"])


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/v1/health")
async def health_check_v1():
    return {
        "status": "healthy",
        "version": "v1",
        "app": settings.app_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )