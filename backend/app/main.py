from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
from datetime import datetime, timezone

from .config import settings
from .storage.database import init_database
from .api import memory, search, context

logging.basicConfig(
    level=settings.NFM_LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting NFM-X...")
    settings.NFM_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    await init_database(str(settings.NFM_DB_PATH))
    logger.info("NFM-X ready")
    yield
    logger.info("Shutting down NFM-X...")

app = FastAPI(
    title="NFM-X API",
    description="Non-Forgettable Evolutionary AI Memory",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8765"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(memory.router, prefix="/v1/memory", tags=["Memory"])
app.include_router(search.router, prefix="/v1/memory", tags=["Search"])
app.include_router(context.router, prefix="/v1/memory", tags=["Context"])

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
