import hashlib
import json
import random

from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.config import settings


async def run_ingestion(document_id: int, session: AsyncSession) -> models.Document:
    document = await session.get(models.Document, document_id)
    if not document:
        raise ValueError(f"Document {document_id} not found")

    stages = [
        (schemas.Stage.parsing, _parse),
        (schemas.Stage.chunking, _chunk),
        (schemas.Stage.embedding, _embed),
        (schemas.Stage.indexing, _index),
        (schemas.Stage.completed, _complete),
    ]

    for stage, handler in stages:
        if _should_fail(document, stage):
            document.stage = models.Stage.failed
            document.error_message = f"Simulated failure at {stage.value}"
            await _save_checkpoint(session, document)
            break

        await _save_checkpoint(session, document, stage=stage)
        result = handler(document)
        if result:
            for key, value in result.items():
                setattr(document, key, value)
        document.stage = models.Stage(stage.value)

    await session.commit()
    await session.refresh(document)
    return document


def _should_fail(document: models.Document, stage: schemas.Stage) -> bool:
    seed = hashlib.md5(f"{document.id}{document.name}{stage.value}".encode()).hexdigest()
    return int(seed, 16) % 7 == 0


def _parse(document: models.Document) -> dict:
    return {"content": document.content.strip()}


def _chunk(document: models.Document) -> dict:
    words = document.content.split()
    chunks = [
        " ".join(words[i : i + settings.chunk_size])
        for i in range(0, len(words), settings.chunk_size)
    ]
    return {"chunks_count": len(chunks)}


def _embed(document: models.Document) -> dict:
    return {"vectors_count": document.chunks_count}


def _index(document: models.Document) -> dict:
    return {}


def _complete(document: models.Document) -> dict:
    return {}


async def _save_checkpoint(
    session: AsyncSession,
    document: models.Document,
    stage: schemas.Stage | None = None,
) -> None:
    checkpoint = models.Checkpoint(
        document_id=document.id,
        stage=models.Stage((stage or schemas.Stage(document.stage.value)).value),
        payload=json.dumps(
            {
                "chunks_count": document.chunks_count,
                "vectors_count": document.vectors_count,
            }
        ),
    )
    session.add(checkpoint)
    await session.commit()
