"""
NFM-X Main Application
FastAPI backend for Non-Forgettable Memory Layer
Supports V1.5 and V2 endpoints
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

# Create FastAPI app
app = FastAPI(
    title="NFM-X",
    description="Non-Forgettable Memory Layer API",
    version="2.0.0",
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


# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "NFM-X",
        "version": "2.0.0",
        "description": "Non-Forgettable Memory Layer",
        "docs": "/docs",
        "v1.5": "/api/docs",
        "v2": "/api/v2/docs"
    }


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}