from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
from datetime import datetime, timezone

from .config import settings
from .storage.database import init_database
from .api import (
    memory, search, context, conflicts, graph, stats, evolution,
    multimodal, ocr, replay, debugger, checkpoints, world_model,
    predictions, strategy, causal_advanced, sharing, sync, simulation, compression
)

logging.basicConfig(
    level=settings.NFM_LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting NFM-X V2...")
    settings.NFM_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    await init_database(str(settings.NFM_DB_PATH))

    # Start background scheduler
    from .workers.scheduler import start_scheduler, get_scheduler
    from .workers.jobs import run_consolidation_job
    from apscheduler.triggers.interval import IntervalTrigger

    start_scheduler()
    scheduler = get_scheduler()
    scheduler.add_job(run_consolidation_job, IntervalTrigger(hours=1), id="consolidation", replace_existing=True)

    logger.info("NFM-X V2 ready")
    yield

    from .workers.scheduler import stop_scheduler
    stop_scheduler()
    logger.info("Shutting down NFM-X V2...")

app = FastAPI(
    title="NFM-X API",
    description="Non-Forgettable Evolutionary AI Memory",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8765", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(memory.router, prefix="/v1/memory", tags=["Memory"])
app.include_router(search.router, prefix="/v1/memory", tags=["Search"])
app.include_router(context.router, prefix="/v1/memory", tags=["Context"])
app.include_router(conflicts.router, prefix="/v1", tags=["Conflicts"])
app.include_router(graph.router, prefix="/v1", tags=["Graph"])
app.include_router(stats.router, prefix="/v1", tags=["Stats"])
app.include_router(evolution.router, prefix="/v1", tags=["Evolution"])
app.include_router(multimodal.router, prefix="/v1", tags=["Multimodal"])
app.include_router(ocr.router, prefix="/v1", tags=["OCR"])
app.include_router(replay.router, prefix="/v1", tags=["Replay"])
app.include_router(debugger.router, prefix="/v1", tags=["Debugger"])

# V3 routers
app.include_router(checkpoints.router, prefix="/v1", tags=["Checkpoints"])
app.include_router(world_model.router, prefix="/v1", tags=["World Model"])
app.include_router(predictions.router, prefix="/v1", tags=["Predictions"])
app.include_router(strategy.router, prefix="/v1", tags=["Strategy"])
app.include_router(causal_advanced.router, prefix="/v1", tags=["Causal"])
app.include_router(sharing.router, prefix="/v1", tags=["Sharing"])
app.include_router(sync.router, prefix="/v1", tags=["Sync"])
app.include_router(simulation.router, prefix="/v1", tags=["Simulation"])
app.include_router(compression.router, prefix="/v1", tags=["Compression"])

@app.get("/", tags=["Health"])
async def root():
    return {"name": "NFM-X", "version": "1.0.0", "docs": "/docs"}

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.NFM_HOST,
        port=settings.NFM_PORT,
        reload=settings.NFM_DEBUG
    )
