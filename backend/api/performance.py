from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from backend.services.performance_engine import calculate_performance

router = APIRouter(
    prefix="/performance",
    tags=["Performance"]
)

class PerformanceResponse(BaseModel):
    score: float = Field(..., example=35.67)

@router.get("/", response_model=PerformanceResponse)
def calculate(
    correct: int = Query(...),
    total: int = Query(...),
    time: int = Query(...)
):
    score = calculate_performance(correct, total, time)
    return PerformanceResponse(score=round(score, 2))
