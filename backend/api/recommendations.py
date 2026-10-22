
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.recommendation_engine import generate_recommendations


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


class WorkoutHistoryItem(BaseModel):
    exercise: str
    date: str | None = None
    reps: int | None = Field(default=None, ge=0)


class RecommendationRequest(BaseModel):
    goal: Literal[
        "muscle_gain",
        "strength",
        "general_fitness",
        "weight_loss",
    ] = "general_fitness"

    experience: Literal[
        "beginner",
        "intermediate",
        "advanced",
    ] = "beginner"

    equipment: list[str] = Field(default_factory=lambda: ["none"])
    preferences: list[str] = Field(default_factory=list)
    target_muscles: list[str] = Field(default_factory=list)

    performance_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    workout_history: list[WorkoutHistoryItem] = Field(
        default_factory=list,
        max_length=100,
    )


@router.get("/health")
def recommendations_health():
    return {"status": "ok", "service": "recommendations"}


@router.post("/generate")
def generate_recommendations_endpoint(
    request: RecommendationRequest,
):
    try:
        profile = request.model_dump()
        return generate_recommendations(profile)

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        # Keep internal errors and credentials out of API responses.
        print(f"Recommendation generation failed: {type(exc).__name__}")
        raise HTTPException(
            status_code=502,
            detail="Recommendation service failed. Check backend logs.",
        ) from exc
