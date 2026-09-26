from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.database import get_db
from app.pipeline import run_ingestion

router = APIRouter()


@router.post("/{document_id}", response_model=schemas.ReplayOut)
async def replay_document(
    document_id: int, session: AsyncSession = Depends(get_db)
) -> schemas.ReplayOut:
    document = await session.get(models.Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    previous = schemas.Stage(document.stage.value)
    if previous == schemas.Stage.completed:
        raise HTTPException(status_code=400, detail="Document already completed")

    document.error_message = None
    document.stage = models.Stage.pending
    await session.commit()

    document = await run_ingestion(document.id, session)
    return schemas.ReplayOut(
        document_id=document.id,
        previous_stage=previous,
        new_stage=schemas.Stage(document.stage.value),
    )
