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
from .storage.database import init_db, close_db, get_db
from .memory.models import Base
from .workers.scheduler import scheduler, add_scheduled_job
from .workers.jobs import run_all_consolidation_jobs
from .api import memory_router, search_router, context_router, conflicts_router, graph_router, stats_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    yield
    await close_db()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="NFM-X: Non-Forgettable Memory Layer API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(memory_router, prefix="/v1/memory")
app.include_router(search_router, prefix="/v1/memory")
app.include_router(context_router, prefix="/v1/memory")
app.include_router(conflicts_router, prefix="/v1")
app.include_router(graph_router, prefix="/v1")
app.include_router(stats_router, prefix="/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.app_name, "version": settings.app_version}

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)