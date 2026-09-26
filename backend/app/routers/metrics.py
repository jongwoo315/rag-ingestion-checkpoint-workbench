from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.database import get_db

router = APIRouter()


@router.get("/", response_model=schemas.MetricsOut)
async def get_metrics(session: AsyncSession = Depends(get_db)) -> schemas.MetricsOut:
    total_result = await session.execute(select(func.count(models.Document.id)))
    total = total_result.scalar() or 0

    stage_counts = await session.execute(
        select(models.Document.stage, func.count(models.Document.id)).group_by(
            models.Document.stage
        )
    )
    by_stage = {stage.value: count for stage, count in stage_counts.all()}

    dead_letter_count = by_stage.get(models.Stage.dead_letter.value, 0)

    avg_chunks = await session.execute(
        select(func.avg(models.Document.chunks_count))
    )
    avg_vectors = await session.execute(
        select(func.avg(models.Document.vectors_count))
    )

    return schemas.MetricsOut(
        total=total,
        by_stage=by_stage,
        dead_letter_count=dead_letter_count,
        average_chunks=avg_chunks.scalar() or 0.0,
        average_vectors=avg_vectors.scalar() or 0.0,
    )
