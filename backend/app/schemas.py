from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class Stage(str, Enum):
    pending = "pending"
    parsing = "parsing"
    chunking = "chunking"
    embedding = "embedding"
    indexing = "indexing"
    completed = "completed"
    failed = "failed"
    dead_letter = "dead_letter"


class DocumentCreate(BaseModel):
    name: str
    content: str


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    stage: Stage
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    chunks_count: int
    vectors_count: int


class CheckpointOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    stage: Stage
    payload: str | None
    created_at: datetime


class ReplayOut(BaseModel):
    document_id: int
    previous_stage: Stage
    new_stage: Stage


class MetricsOut(BaseModel):
    total: int
    by_stage: dict[str, int]
    dead_letter_count: int
    average_chunks: float
    average_vectors: float
