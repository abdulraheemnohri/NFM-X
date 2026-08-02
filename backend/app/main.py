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


logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    try:
        await init_db()
        from .embeddings.vector_store import vector_store
        try:
            vector_store.load()
        except Exception as e:
            logger.warning(f"Could not load FAISS index: {e}")
        logger.info(f"{settings.app_name} started successfully")
        yield
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    finally:
        try:
            vector_store.save()
            await close_db()
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
        logger.info("Shutdown complete")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="NFM-X: Non-Forgettable Memory Layer API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc) if settings.debug else None},
    )


from .api import memory, search, context
app.include_router(memory.router, prefix="/v1")
app.include_router(search.router, prefix="/v1")
app.include_router(context.router, prefix="/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.app_name, "version": settings.app_version, "timestamp": datetime.now(timezone.utc).isoformat()}


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)
