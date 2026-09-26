from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class HealthOut(BaseModel):
    status: str


@router.get("/", response_model=HealthOut, status_code=status.HTTP_200_OK)
async def health() -> HealthOut:
    return HealthOut(status="ok")
