from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.database import init_db
from app.routers import checkpoint, documents, health, metrics, replay


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    yield


app = FastAPI(
    title="RAG Ingestion Checkpoint Workbench",
    description="Durable, observable RAG document ingestion with checkpoints, dead-letter queue, and replay.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router, tags=["health"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(checkpoint.router, prefix="/checkpoint", tags=["checkpoint"])
app.include_router(replay.router, prefix="/replay", tags=["replay"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
