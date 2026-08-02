"""
NFM-X Main Application
FastAPI backend for Non-Forgettable Memory Layer
Supports V1.5, V2, and V3 endpoints
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# Create FastAPI app
app = FastAPI(
    title="NFM-X",
    description="Non-Forgettable Memory Layer API - V1.5, V2, V3",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "NFM-X",
        "version": "3.0.0",
        "description": "Non-Forgettable Memory Layer",
        "docs": "/docs",
        "versions": {
            "v1.5": "/api/docs",
            "v2": "/api/v2/docs",
            "v3": "/api/v1/docs"
        }
    }


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "3.0.0"}