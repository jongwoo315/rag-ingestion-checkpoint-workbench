from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.database import get_db
from app.pipeline import run_ingestion

router = APIRouter()


@router.post("/", response_model=schemas.DocumentOut, status_code=201)
async def create_document(
    payload: schemas.DocumentCreate, session: AsyncSession = Depends(get_db)
) -> models.Document:
    document = models.Document(name=payload.name, content=payload.content)
    session.add(document)
    await session.commit()
    await session.refresh(document)
    document = await run_ingestion(document.id, session)
    return document


@router.get("/", response_model=list[schemas.DocumentOut])
async def list_documents(session: AsyncSession = Depends(get_db)) -> list[models.Document]:
    result = await session.execute(select(models.Document).order_by(models.Document.id.desc()))
    return list(result.scalars().all())


@router.get("/{document_id}", response_model=schemas.DocumentOut)
async def get_document(
    document_id: int, session: AsyncSession = Depends(get_db)
) -> models.Document:
    document = await session.get(models.Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document
