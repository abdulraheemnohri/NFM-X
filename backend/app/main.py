"""
NFM-X Main Application
FastAPI Server for Non-Forgettable Evolutionary AI Memory
"""

from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

# Import local modules
from .config import settings
from .storage.database import init_database, get_db_session
from .memory.models import Base
from .api import memory, search, context, evolution, graph, agents

# Configure logging
logging.basicConfig(
    level=settings.NFM_LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("nfm-x.log")
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting NFM-X server...")
    
    # Initialize storage directory
    storage_path = settings.NFM_STORAGE_PATH
    storage_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize database
    db_path = storage_path / "nfm.db"
    logger.info(f"Initializing database at {db_path}")
    await init_database(str(db_path))
    
    # Initialize vector store
    from .embeddings.vector_store import init_vector_store
    await init_vector_store()
    
    # Initialize knowledge graph
    from .graph.knowledge_graph import init_knowledge_graph
    await init_knowledge_graph()
    
    # Start background workers
    from .workers.background import start_background_workers
    start_background_workers()
    
    logger.info("NFM-X server started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down NFM-X server...")
    from .embeddings.vector_store import shutdown_vector_store
    await shutdown_vector_store()
    logger.info("NFM-X server stopped")


# Create FastAPI app
app = FastAPI(
    title="NFM-X API",
    description="Non-Forgettable Evolutionary AI Memory Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create API router
api_router = APIRouter(prefix="/v1")

# Include all API endpoints
api_router.include_router(memory.router, prefix="/memory", tags=["Memory"])
api_router.include_router(search.router, prefix="/memory", tags=["Search"])
api_router.include_router(context.router, prefix="/memory", tags=["Context"])
api_router.include_router(evolution.router, prefix="/memory", tags=["Evolution"])
api_router.include_router(graph.router, prefix="/graph", tags=["Graph"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])

# Mount API router
app.include_router(api_router)


# Root endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with basic info"""
    return {
        "name": "NFM-X",
        "version": "1.0.0",
        "description": "Non-Forgettable Evolutionary AI Memory Platform",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2026-08-01T00:00:00Z"
    }


@app.get("/stats", tags=["Stats"])
async def get_stats(db_session=Depends(get_db_session)):
    """Get system statistics"""
    from .memory.models import Memory
    from sqlalchemy import select, func
    from sqlalchemy.orm import selectinload
    
    # Count memories by type
    result = await db_session.execute(
        select(
            Memory.type,
            func.count(Memory.id).label("count")
        ).group_by(Memory.type)
    )
    type_counts = {row.type: row.count for row in result}
    
    # Total memories
    total_result = await db_session.execute(select(func.count(Memory.id)))
    total_memories = total_result.scalar() or 0
    
    return {
        "total_memories": total_memories,
        "memories_by_type": type_counts,
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.NFM_HOST,
        port=settings.NFM_PORT,
        reload=settings.NFM_DEBUG,
        log_level=settings.NFM_LOG_LEVEL.lower()
    )