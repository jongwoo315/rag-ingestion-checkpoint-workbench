from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.database import get_db

router = APIRouter()


@router.get("/{document_id}", response_model=list[schemas.CheckpointOut])
async def get_checkpoints(
    document_id: int, session: AsyncSession = Depends(get_db)
) -> list[models.Checkpoint]:
    result = await session.execute(
        select(models.Checkpoint)
        .where(models.Checkpoint.document_id == document_id)
        .order_by(models.Checkpoint.id.asc())
    )
    return list(result.scalars().all())
